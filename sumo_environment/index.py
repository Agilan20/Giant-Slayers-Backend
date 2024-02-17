import traci
import time
import threading
from queue import Queue
from datetime import datetime, timedelta
from django.core.cache import cache
import asyncio
from pymongo import MongoClient
import random 

simulation_duration_limit = 15
reasons=["punc_front_left","punc_front_right","punc_rear_left","punc_rear_right","fuel_leak","engine_failure"]
prob_reasons=[0.1,0.1,0.1,0.1,0.1,0.5]
naive_prob=0.01
acc_prob=naive_prob

client = MongoClient("localhost", 27017)
db = client["k_hacks"]
collection = db["parameters"]

location_dict = {}

print(db)

class Car():
    def __init__(self, id ,odometer=0 , fuel_consumption = 0  ) -> None:
        self.id = id 
        self.initial = {
            "Odometer" : odometer ,
            "Fuel_Consumption": fuel_consumption 
        }
        self.frequency = dict({
            "Speed" : {"frequency":10 ,"last_log_time": datetime.now() , "function":traci.vehicle.getSpeed } ,
            "Position" : {"frequency":10 , "last_log_time" : datetime.now(),  "function":traci.vehicle.getPosition },
            "GPS_Position" : {"frequency":10 ,"last_log_time": datetime.now() , "function": self.get_geo } ,
            "Orientation" : {"frequency":10 ,"last_log_time": datetime.now() , "function":traci.vehicle.getAngle } ,
            "Acceleration" : {"frequency":10 ,"last_log_time": datetime.now() , "function":traci.vehicle.getAcceleration } ,
            "Odometer" : {"frequency":10 ,"last_log_time": datetime.now() , "function": self.get_odometer } , 
            "Fuel_Consumption" : {"frequency":10 ,"last_log_time": datetime.now() , "function": self.get_fuel } ,
            "Electricity_Consumption" : {"frequency":10 ,"last_log_time": datetime.now() , "function":traci.vehicle.getElectricityConsumption }, 
            "Impatience" : {"frequency":10 ,"last_log_time": datetime.now() , "function":traci.vehicle.getImpatience } ,
            "Imperfection" :{"frequency":10 ,"last_log_time": datetime.now() , "function":traci.vehicle.getImperfection },
        })
        self.start_time = datetime.now()
        self.location_publish_mode = False
    
    def get_odometer(self,id):
        return self.initial["Odometer"] + traci.vehicle.getDistance(id)

    def get_fuel(self,id):
        return self.initial["Fuel_Consumption"] + traci.vehicle.getFuelConsumption(id)

    def get_geo(self,id):
        x, y = traci.vehicle.getPosition(id)
        return traci.simulation.convertGeo(x, y)


    def update_frequency(self, parameter, new_frequency):
        print("Updating Frequency of",parameter,"to",new_frequency)
        self.frequency[parameter]["frequency"] = int(new_frequency) 
        self.frequency[parameter]["last_log_time"] = datetime.now() 

    def log_data(self):
         
        while True :
    
            for i in self.frequency.keys():
                current_time = datetime.now()
                last_log_time = self.frequency[i]["last_log_time"]
                delta = current_time - last_log_time 
                if(delta.seconds >=  self.frequency[i]["frequency"]):
                    # print(self.id, i , self.frequency[i]["function"](self.id))
                    # cache.set(self.id+"_"+i ,self.frequency[i]["function"](self.id) , self.frequency[i]["frequency"]+20)
                    #write to mongodb 
                    # collection.insert_one({
                    #     "vehicle_id" : self.id ,
                    #     "parameter" :  i , 
                    #     "value" :  self.frequency[i]["function"](self.id),
                    #     "time" : datetime.now() , 
                    # })

                    self.frequency[i]["last_log_time"] = current_time

                if self.id not in location_dict:
                    location_dict[self.id] = dict()

                if i== "GPS_Position":
                        location_dict[self.id]["location"]= self.frequency[i]["function"](self.id)
            

    def set_publish_location_mode(self,mode="OFF"):
        if(mode=="OFF"):
            self.location_publish_mode = False 
        else :
            self.location_publish_mode = True 
            print("Starting location updates")
            asyncio.create_task(self.start_publishing_location())

    def start_publishing_location(self):
        while True and self.location_publish_mode : 
            vehicle_position = traci.vehicle.getPosition("veh0")
            latitude, longitude = traci.simulation.convertGeo(*vehicle_position)
            cache.set( id, (latitude,longitude))
            time.sleep(3)


class CarManager():

    cars = dict()

    event_queue = Queue()

    def __init__(self) -> None:
        thread = threading.Thread(target=self.look_for_triggers)
        thread.start()

    def add_car(self, car_id):
        print("Adding New Car")
        temp = Car(car_id)
        self.cars[car_id] = temp 
        my_thread = threading.Thread(target=temp.log_data)
        my_thread.start()

    def delete_car(self,item):
        print("Delete car",item)

    def update_parameter(self,item):
        self.cars[item["vehicle_id"]].update_frequency(item["parameter"],item["frequency"])

    def look_for_triggers(self):
        while True:
            while self.event_queue.qsize() != 0:
                item = self.event_queue.get()

                if item["type"] == "add_vehicle":
                    self.add_car(item["data"]["vehicle_id"])

                elif item["type"] == "delete_vehicle":
                    self.delete_car(item)
                
                elif item["type"]=="update_parameter":
                    self.update_parameter(item["data"])
                
                elif item["type"]=="publish_location":
                    self.cars[item[""]].set_publish_location_mode(item["data"]["mode"])

manager = CarManager()

def simulate_first_100vehicle():
    print("Starting simulation for first 100 vehicles randomly")

    vehicles=traci.vehicle.getIDList()

    for i in range(0,10):
        manager.event_queue.put({"type":"add_vehicle" , "data":{"vehicle_id":vehicles[i]}})

def start_sumo():
    # new_route_id = "new_route"
    # edges_of_new_route = [':cluster_392853442_9189925470_19', ':cluster_392853442_9189925470_2', ':cluster_392853442_9189925470_3']  # Replace with the actual edge IDs of your new route
    # traci.route.add(new_route_id, edges_of_new_route)
    # traci.vehicle.add("new_vehicle", "new_route", typeID="veh_passenger")
    # traci.vehicle.subscribe("new_vehicle",  [traci.constants.VAR_POSITION, traci.constants.VAR_SPEED])
    
    print("Starting Sumo...")
    traci.start(["sumo", "-c", "sumo_files/osm.sumocfg"])
    break_down_veh = set()

    traci.simulationStep()

    simulate_first_100vehicle()

    try:
        while True:
            traci.simulationStep()

            vehicles=traci.vehicle.getIDList()

            for i in manager.cars:
               
                random_number = random.random()
                if random_number<=acc_prob and manager.cars[i].id not in break_down_veh:
                    id = manager.cars[i].id
                    print("Accident has occurred for vehicle ",id)                                      
                    chosen_reason = random.choices(reasons, prob_reasons)[0]
                    print("Cause of accident is: ",chosen_reason)
                    traci.vehicle.setSpeed(id,0)
                    traci.vehicle.setAcceleration(id,0,5)
                    location_dict[i]["accident"] = True 
                    break_down_veh.add(id)

                    if id in break_down_veh:
                        print("Broken Down: ",id)
                        print("Break Down Vehicles List: ",break_down_veh)
                        print("Total Cars Present is ",len(vehicles),traci.vehicle.getIDList())
                        traci.vehicle.setSpeed(id,0)
                        
            time.sleep(2)
    finally : 
        traci.close()

