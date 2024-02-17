import traci
import time
import threading
from queue import Queue
from datetime import datetime, timedelta
from django.core.cache import cache
import asyncio 

class Car():
    def __init__(self, id , speed=0, turn_angle=0) -> None:
        self.id = id 
        self.frequency = dict({
            "speed" : {"frequency":10 ,"last_log_time": datetime.now() , "function":traci.vehicle.getSpeed } ,
            "turn_angle" : {"frequency":10 , "last_log_time" : datetime.now(),  "function":traci.vehicle.getAngle },
        })
        self.start_time = datetime.now()
        self.location_publish_mode = False 
        #create car 

    def set_publish_location_mode(self,mode="OFF"):
        if(mode=="OFF"):
            self.location_publish_mode = False 
        else :
            self.location_publish_mode = True 
            print("Starting location updates")
            asyncio.create_task(self.start_publishing_location())

    def update_frequency(self, parameter, new_frequency):
        print("Updating Frequency of",parameter,"to",new_frequency)
        self.frequency[parameter]["frequency"] = int(new_frequency) 
        self.frequency[parameter]["last_log_time"] = datetime.now() 

    def log_data(self):
        while True :
            # current_time = datetime.now()
            # elapsed_time = current_time - self.start_time
            for i in self.frequency.keys():
                current_time = datetime.now()
                last_log_time = self.frequency[i]["last_log_time"]
                delta = current_time - last_log_time 
                if(delta.seconds >=  self.frequency[i]["frequency"]):
                    print(self.id, i , self.frequency[i]["function"](self.id))
                    # cache.set(self.id+"_"+i ,self.frequency[i]["function"](self.id) , self.frequency[i]["frequency"]+20)
                    #write to mongodb 
                    
                    self.frequency[i]["last_log_time"] = current_time

            time.sleep(1)
            

    def start_publishing_location(self):
        while True and self.location_publish_mode : 
            vehicle_position = traci.vehicle.getPosition(self.id)
            latitude, longitude = traci.simulation.convertGeo(*vehicle_position)
            cache.set(self.id+"_location" , (latitude,longitude))
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
                    self.add_car(item["data"]["car_id"])

                elif item["type"] == "delete_vehicle":
                    self.delete_car(item)
                
                elif item["type"]=="update_parameter":
                    self.update_parameter(item["data"])
                
                elif item["type"]=="publish_location":
                    self.cars[item[""]].set_publish_location_mode(item["data"]["mode"])

manager = CarManager()


def start_sumo():
    # new_route_id = "new_route"
    # edges_of_new_route = [':cluster_392853442_9189925470_19', ':cluster_392853442_9189925470_2', ':cluster_392853442_9189925470_3']  # Replace with the actual edge IDs of your new route
    # traci.route.add(new_route_id, edges_of_new_route)
    # traci.vehicle.add("new_vehicle", "new_route", typeID="veh_passenger")
    # traci.vehicle.subscribe("new_vehicle",  [traci.constants.VAR_POSITION, traci.constants.VAR_SPEED])
    
    print("Starting Sumo...")
    traci.start(["sumo", "-c", "sumo_files/osm.sumocfg"])

    try:
        while True:
            traci.simulationStep()

            start_lat_long = (13.0524722222 , 80.2201666667 )
            end_lat_long = (13.0343055556,80.1598333333)

            # start = traci.simulation.convertGeo(start_lat_long[0], start_lat_long[1])
            
            # end = traci.simulation.convertGeo(end_lat_long[0], end_lat_long[1])

            start_lane_id = traci.simulation.convertRoad(start_lat_long[0],start_lat_long[1])

            startlane_id_str = start_lane_id[0]+'_0'

            end_lane_id = traci.simulation.convertRoad(end_lat_long[0],end_lat_long[1])

            endlane_id_str = end_lane_id[0]+'_0'

            if startlane_id_str in traci.lane.getIDList() and endlane_id_str in traci.lane.getIDList():
                start_edge_id = traci.lane.getEdgeID(startlane_id_str)
                end_edge_id = traci.lane.getEdgeID(endlane_id_str)
        
            #     routes = traci.simulation.findRoute(start_edge_id, end_edge_id)
            # # Print the route
            #     print("Found route:", routes.edges)

            time.sleep(3)

    finally:
        traci.close()
