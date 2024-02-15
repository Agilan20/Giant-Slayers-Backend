import traci
import time
import threading
from queue import Queue
from datetime import datetime

class Car():
    def __init__(self, id , speed=0, turn_angle=0) -> None:
        self.id = id 
        self.frequency = dict({
            "speed" : {"frequency":5 , "function":traci.vehicle.getSpeed } ,
            "turn_angle" : {"frequency":10 , "function":traci.vehicle.getAngle }
        })
        self.start_time = datetime.now()

    def update_frequency(self, parameter, new_frequency):
        pass

    def log_data(self):
        while True :
            # current_time = datetime.now()
            # elapsed_time = current_time - self.start_time
            for i in self.frequency.keys():
                print("Logging data every 5 seconds")
                print(i , self.frequency[i]["function"](self.id))
            time.sleep(5)
            

    def start_publishing_location(self):
        vehicle_position = traci.vehicle.getPosition("veh0")
        latitude, longitude = traci.simulation.convertGeo(*vehicle_position)
        print(latitude,longitude)


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
        print("updating parameter",item)

    def look_for_triggers(self):

        while True:
            while self.event_queue.qsize() != 0:
                item = self.event_queue.get()

                if item["type"] == "add_vehicle":
                    self.add_car(item["data"]["car_id"])

                elif item["type"] == "delete_vehicle":
                    self.delete_car(item)
                
                elif item["type"]=="update_parameter":
                    self.update_parameter(item)
                
                elif item["type"]=="subscribe_location":
                    self.cars[item["car_id"]].start_publishing_location()


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

            time.sleep(3)

    finally:
        traci.close()
