import traci
import time
import traci.constants as tc
import pytz
import datetime
from random import randrange
import pandas as pd


def getdatetime():
        utc_now = pytz.utc.localize(datetime.datetime.utcnow())
        currentDT = utc_now.astimezone(pytz.timezone("Asia/Singapore"))
        DATIME = currentDT.strftime("%Y-%m-%d %H:%M:%S")
        return DATIME

def flatten_list(_2d_list):
    flat_list = []
    for element in _2d_list:
        if type(element) is list:
            for item in element:
                flat_list.append(item)
        else:
            flat_list.append(element)
    return flat_list


sumoCmd = ["sumo", "-c", "osm.sumocfg"]
traci.start(sumoCmd)

packVehicleData = []
packTLSData = []
packBigData = []

simulation_duration_limit = 15


# Record the start time
start_time = time.time()

gps_coords=[(80.19886995097721, 13.019324991705446),(80.19801164409267,  13.017067124332101),(80.19528704259318, 13.011620522547872),(80.20370966343273,  13.008228307124497),(80.20864332553697, 13.00422270707746)]
for i in range(len(gps_coords)):
    gps_position=gps_coords[i]
    lane_id = traci.simulation.convertRoad(gps_position[0], gps_position[1])

    # Check if the lane is known before trying to get the edge ID
    if lane_id[0]+'_0' in traci.lane.getIDList():
        lane_id_str = lane_id[0]+'_0'
        print(lane_id_str)
        print(f"Coordinates {i} is on Lane {lane_id_str}")

        # Now you can use lane_id_str to get the edge_id
        edge_id = traci.lane.getEdgeID(lane_id_str)
        print(f"Edge ID for Coordinate {i}: {edge_id}")
    else:
        print(f"Error: Lane {lane_id[0]} is not known for Coordinate {i}")
        # pass



traci.close()

#Generate Excel file

time.sleep(5)