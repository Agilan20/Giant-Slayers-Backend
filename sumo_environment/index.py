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
naive_prob=0.05 
acc_prob=naive_prob/simulation_duration_limit
client = MongoClient("localhost", 27017)
db = client["k_hacks"]
collection = db["parameters"]
location_dict = {}
result = collection.delete_many({})
wear_and_tear_threshold = 100000

print(f"Deleted {result.deleted_count} documents from the collection.")

class Car():
    def __init__(self, id ,odometer=0 , fuel_consumption = 0 ,color ="red"  ) -> None:
        self.id = id 
        self.color = color 
        self.initial = {
            "Odometer" : odometer ,
            "Fuel_Consumption": fuel_consumption 
        }
        self.accident = None 
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
            "Pressure" : {
                "frequency" : 10 , "last_log_time" : datetime.now() , "function" : self.calculate_tire_pressure_rise } , 

            "Oil_life": {
                "frequency" : 10 , "last_log_time" : datetime.now() , "function" : self.estimate_oil_life },
             
        })
        self.start_time = datetime.now()
        self.location_publish_mode = False

    def calculate_tire_pressure_rise(self,id,initial_pressure_psi=32,  variance_factor=0.000005,pressure_change_per_meter=0.00000000000000001):

        distance_travelled = self.get_odometer(id)

        psi_to_pa_conversion = 6894.76

        initial_pressure_pa = initial_pressure_psi * psi_to_pa_conversion
        
        final_pressure_pa = initial_pressure_pa

        for _ in range(round(distance_travelled)):
            delta_pressure_pa = pressure_change_per_meter

            variance = random.uniform(0, variance_factor * initial_pressure_pa)
            delta_pressure_pa += variance

            final_pressure_pa += delta_pressure_pa

            final_pressure_psi = final_pressure_pa / psi_to_pa_conversion

        return final_pressure_psi

    def estimate_oil_life(self,id ):
        speed  = traci.vehicle.getSpeed(id)
        rpm = self.calculate_rpm(speed)
        speed_threshold = 60  # Speed threshold in km/h
        rpm_threshold = 3000  # RPM threshold
        speed_factor = 0.1  # Factor to increase stress for each km/h above threshold
        rpm_factor = 0.2  # Factor to increase stress for each RPM above threshold

        stress_factor = 0

        if speed > speed_threshold:
            stress_factor += (speed - speed_threshold) * speed_factor

        if rpm > rpm_threshold:
            stress_factor += (rpm - rpm_threshold) * rpm_factor

        estimated_oil_life = 100 - stress_factor
        return max(0, estimated_oil_life)

    def calculate_rpm(self,speed, diameter=0.5):
        import math 

        circumference = math.pi * diameter
    
        speed_m_per_min = speed * 60

        rpm = speed_m_per_min / circumference
    
        return rpm
    
    def get_odometer(self,id):
        return int(self.initial["Odometer"]) + traci.vehicle.getDistance(id)

    def get_fuel(self,id):
        return int(self.initial["Fuel_Consumption"]) + traci.vehicle.getFuelConsumption(id)

    def get_geo(self,id):
        x, y = traci.vehicle.getPosition(id)
        return traci.simulation.convertGeo(x, y)


    def update_frequency(self, parameter, new_frequency):
        print("Updating Frequency of",parameter,"to",new_frequency)
        self.frequency[parameter]["frequency"] = int(new_frequency) 
        self.frequency[parameter]["last_log_time"] = datetime.now() 

    def log_data(self):
         
        while True :
            if self.accident!=None or (self.id not in traci.vehicle.getIDList()):
                continue 
            for i in self.frequency.keys():
                current_time = datetime.now()
                last_log_time = self.frequency[i]["last_log_time"]
                delta = current_time - last_log_time 
                if(delta.seconds >=  self.frequency[i]["frequency"]):
                    collection.insert_one({
                        "vehicle_id" : self.id ,
                        "parameter" :  i , 
                        "value" :  self.frequency[i]["function"](self.id),
                        "time" : datetime.now() , 
                    })

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
        print("----------")
        thread = threading.Thread(target=self.look_for_triggers)
        thread.start()

    def get_edge(self,y,x,name):
        lane_id=traci.simulation.convertRoad(y,x,isGeo=True)
        if lane_id[0]+'_0' in traci.lane.getIDList():
            lane_id_str = lane_id[0]+'_0'
            print(lane_id_str)
            print(f"Coordinates {name} is on Lane {lane_id_str}")
            edge_id = traci.lane.getEdgeID(lane_id_str)
            print(f"Edge ID for Coordinate {name}: {edge_id}")
            return edge_id
        else:
            print(f"Error: Lane {lane_id[0]} is not known for name")
            return -1

    def add_car(self, item ):
       
        odometer =0 
        fuel_consumption = 0

        if "odometer" in item:
            odometer = int(item["odometer"])
        if "fuel_consumption" in  item : 
            fuel_consumption = int(item["fuel_consumption"])

        if "start_point_lng" in item: 
            start_point = [item["start_point_lng"] , item["start_point_lat"]]
            end_point = [item["end_point_lng"] , item["end_point_lat"]]

            edge_id_1 =self.get_edge(float(start_point[0]),float(start_point[1]),item["vehicle_id"])
            edge_id_2 =self.get_edge(float(end_point[0]),float(end_point[1]),item["vehicle_id"])
            vehicle_id=  item["vehicle_id"]
            trip_id="trip"+ item["vehicle_id"]
            traci.edge.setAllowed(edge_id_1,"all")
            traci.edge.setAllowed(edge_id_2,"all")
            print(traci.simulation.findRoute(edge_id_1,edge_id_2,depart=traci.simulation.getCurrentTime()))
            if(len(traci.simulation.findRoute(edge_id_1,edge_id_2,depart=traci.simulation.getCurrentTime()).edges)==0):
                print("No Routes Found")
                return False 
            traci.route.add(trip_id, traci.simulation.findRoute(edge_id_1,edge_id_2).edges)
            traci.vehicle.add(vehicle_id,trip_id)

        print("Adding New Car")
        print(item)
        temp = Car( item["vehicle_id"] ,odometer,fuel_consumption)
        self.cars[ item["vehicle_id"]] = temp 
        my_thread = threading.Thread(target=temp.log_data)
        my_thread.start()
        return True 

    def delete_car(self,item):
        print("Delete car",item)

    def update_parameter(self,item):
        self.cars[item["vehicle_id"]].update_frequency(item["parameter"],item["frequency"])

    def lane_to_block(self):
        block_prob= 0.5  
        min_speed_req=8
        min_width_req=2
        lane_list=traci.lane.getIDList()
        print("-------", len(lane_list))
        speed_filtered_value=[lane for lane in lane_list if traci.lane.getMaxSpeed(lane)>min_speed_req]
        width_filtered_value=[lane for lane in speed_filtered_value if traci.lane.getWidth(lane)>min_width_req]
        road_purpose_filter=['army','vip','emergency','truck']
        purpose_filtered_road=[lane for lane in width_filtered_value if len(set(traci.lane.getAllowed(lane)).intersection(road_purpose_filter))!=0]
        
        temp = random.random()

        print(temp)

        if temp <=block_prob:
            print("Proceeding to block a lane")
            while True:
                lane_to_block=random.choice(purpose_filtered_road)
                if lane_to_block in traci.lane.getIDList():
                    print("found a proper lane")
                    break
                else:
                  # print("failed to find a proper lane")
                  pass

            route_id = "blocker_route_" + str(len(traci.route.getIDList()) + 1)
            connected_edges = traci.lane.getEdgeID(lane_to_block)

            traci.route.add(route_id, [connected_edges] + [connected_edges])

            # n_veh=int(random.uniform(20,30))
            j = 0 
            while True:
                new_veh_add = "blocker_vehicle_" + str(j + random.randint(1000, 900000000))
                if new_veh_add not in traci.vehicle.getIDList():
                    traci.vehicle.add(new_veh_add, routeID=route_id)
                    temp = Car( new_veh_add , color = "blue" )
                    self.cars[ new_veh_add] = temp 
                    my_thread = threading.Thread(target=temp.log_data)
                    my_thread.start()  
                    # print("Vehicle has been added")
                    break
                else :
                    j+=1 
                

    def look_for_triggers(self):
        # print("----------------", item["type"])
        while True:
            while self.event_queue.qsize() != 0:
                item = self.event_queue.get()

                
                if item["type"] == "add_vehicle":
                    self.add_car(item["data"])

                elif item["type"] == "delete_vehicle":
                    self.delete_car(item)
                
                elif item["type"]=="update_parameter":
                    self.update_parameter(item["data"])
                
                elif item["type"]=="publish_location":
                    self.cars[item[""]].set_publish_location_mode(item["data"]["mode"])

                # elif item["type"]=="lane_to_block":
                #     self.lane_to_block()

manager = CarManager()

def simulate_first_100vehicle():
    print("Starting simulation for first 100 vehicles randomly")

    vehicles=traci.vehicle.getIDList()

    for i in range(34,50):
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
                    location_dict[i]["accident"] = chosen_reason
                    break_down_veh.add(id)
                    manager.cars[i].accident = True 

                    if id in break_down_veh:
                        print("Broken Down: ",id)
                        print("Break Down Vehicles List: ",break_down_veh)
                        print("Total Cars Present is ",len(vehicles),traci.vehicle.getIDList())
                        traci.vehicle.setSpeed(id,0)
                    
    finally : 
        pass 

