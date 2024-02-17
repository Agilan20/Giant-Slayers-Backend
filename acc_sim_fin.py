import traci
import time
import traci.constants as tc
import pytz
import datetime
from random import randrange
import pandas as pd
import random


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


## params needed: probs_reasons, acc_prob, fail_prob

reasons=["punc_front_left","punc_front_right","punc_rear_left","punc_rear_right","fuel_leak","engine_failure"]
prob_reasons=[0.1,0.1,0.1,0.1,0.1,0.5]
naive_prob=0.01
acc_prob=naive_prob/simulation_duration_limit





# Record the start time
start_time = time.time()
break_down_veh=list()

counter=0

while traci.simulation.getMinExpectedNumber() > 0 and (time.time() - start_time) < simulation_duration_limit:
        counter=counter+1
       
        traci.simulationStep();

        vehicles=traci.vehicle.getIDList();
        trafficlights=traci.trafficlight.getIDList();

        for i in range(0,len(vehicles)):

                #Function descriptions
                #https://sumo.dlr.de/docs/TraCI/Vehicle_Value_Retrieval.html
                #https://sumo.dlr.de/pydoc/traci._vehicle.html#VehicleDomain-getSpeed

                vehid = vehicles[i]
                x, y = traci.vehicle.getPosition(vehicles[i])
                coord = [x, y]
                lon, lat = traci.simulation.convertGeo(x, y)
                gpscoord = [lon, lat]
                spd = round(traci.vehicle.getSpeed(vehicles[i])*3.6,2)
                edge = traci.vehicle.getRoadID(vehicles[i])
                lane = traci.vehicle.getLaneID(vehicles[i])
                displacement = round(traci.vehicle.getDistance(vehicles[i]),2)
                turnAngle = round(traci.vehicle.getAngle(vehicles[i]),2)
                nextTLS = traci.vehicle.getNextTLS(vehicles[i])
                acc=traci.vehicle.getAcceleration(vehicles[i])
                odomDist=traci.vehicle.getDistance(vehicles[i])
                fuelCons=traci.vehicle.getFuelConsumption(vehicles[i])
                eleCons=traci.vehicle.getElectricityConsumption(vehicles[i])
                sigma=traci.vehicle.getImperfection(vehicles[i])
                impatience=traci.vehicle.getImpatience(vehicles[i])

                random_number = random.random()
                if random_number<=acc_prob and vehicles[i] not in break_down_veh:
                    print("Accident has occurred for vehicle ",vehicles[i])

                      ## accident has occured. Determining reason for the crash
                    chosen_reason = random.choices(reasons, prob_reasons)[0]
                    print("Cause of accident is: ",chosen_reason)
                    traci.vehicle.setSpeed(vehicles[i],0)
                    traci.vehicle.setAcceleration(vehicles[i],0,5)
                    break_down_veh.append(vehicles[i])

                if vehicles[i] in break_down_veh:
                    print("Broken Down: ",vehicles[i])
                    print("Break Down Vehicles List: ",break_down_veh)
                    print("Total Cars Present is ",len(vehicles))
                    traci.vehicle.setSpeed(vehicles[i],0)

                          

                    


                      




                #Packing of all the data for export to CSV/XLSX
                vehList = [getdatetime(), vehid, coord, gpscoord, spd, edge, lane, displacement, turnAngle, nextTLS]
                
                
                

                print("Vehicle: ", vehid, " at datetime: ", getdatetime())
                print("ID:", vehid, " | Position: ", coord, " | GPS Position: ", gpscoord, " | Speed: ", spd, "km/h |",
      " EdgeID of veh: ", edge, " | LaneID of veh: ", lane, " | Distance: ", displacement, "m |",
      " Vehicle orientation: ", turnAngle, "deg | Upcoming traffic lights: ", nextTLS, " |",
      " Acceleration: ", acc, " | Odometer Distance: ", odomDist, " | Fuel Consumption: ", fuelCons, " |",
      " Electricity Consumption: ", eleCons, " | Imperfection: ", sigma, " | Impatience: ", impatience)


                idd = traci.vehicle.getLaneID(vehicles[i])

                tlsList = []
        
                for k in range(0,len(trafficlights)):

                        #Function descriptions
                        #https://sumo.dlr.de/docs/TraCI/Traffic_Lights_Value_Retrieval.html#structure_of_compound_object_controlled_links
                        #https://sumo.dlr.de/pydoc/traci._trafficlight.html#TrafficLightDomain-setRedYellowGreenState
                        
                        if idd in traci.trafficlight.getControlledLanes(trafficlights[k]):

                                tflight = trafficlights[k]
                                tl_state = traci.trafficlight.getRedYellowGreenState(trafficlights[k])
                                tl_phase_duration = traci.trafficlight.getPhaseDuration(trafficlights[k])
                                tl_lanes_controlled = traci.trafficlight.getControlledLanes(trafficlights[k])
                                tl_program = traci.trafficlight.getCompleteRedYellowGreenDefinition(trafficlights[k])
                                tl_next_switch = traci.trafficlight.getNextSwitch(trafficlights[k])

                                #Packing of all the data for export to CSV/XLSX
                                tlsList = [tflight, tl_state, tl_phase_duration, tl_lanes_controlled, tl_program, tl_next_switch]
                                
                                print(trafficlights[k], " --->", \
                                      #Returns the named tl's state as a tuple of light definitions from rRgGyYoO, for red,
                                      #green, yellow, off, where lower case letters mean that the stream has to decelerate
                                        " TL state: ", traci.trafficlight.getRedYellowGreenState(trafficlights[k]), " |" \
                                      #Returns the default total duration of the currently active phase in seconds; To obtain the
                                      #remaining duration use (getNextSwitch() - simulation.getTime()); to obtain the spent duration
                                      #subtract the remaining from the total duration
                                        " TLS phase duration: ", traci.trafficlight.getPhaseDuration(trafficlights[k]), " |" \
                                      #Returns the list of lanes which are controlled by the named traffic light. Returns at least
                                      #one entry for every element of the phase state (signal index)                                
                                        " Lanes controlled: ", traci.trafficlight.getControlledLanes(trafficlights[k]), " |", \
                                      #Returns the complete traffic light program, structure described under data types                                      
                                        " TLS Program: ", traci.trafficlight.getCompleteRedYellowGreenDefinition(trafficlights[k]), " |"
                                      #Returns the assumed time (in seconds) at which the tls changes the phase. Please note that
                                      #the time to switch is not relative to current simulation step (the result returned by the query
                                      #will be absolute time, counting from simulation start);
                                      #to obtain relative time, one needs to subtract current simulation time from the
                                      #result returned by this query. Please also note that the time may vary in the case of
                                      #actuated/adaptive traffic lights
                                        " Next TLS switch: ", traci.trafficlight.getNextSwitch(trafficlights[k]))

                #Pack Simulated Data
                packBigDataLine = flatten_list([vehList, tlsList])
                packBigData.append(packBigDataLine)

                NEWSPEED = 15 
                


traci.close()

print("Counter Value is ",counter)
#Generate Excel file
columnnames = ['dateandtime', 'vehid', 'coord', 'gpscoord', 'spd', 'edge', 'lane', 'displacement', 'turnAngle', 'nextTLS', \
                       'tflight', 'tl_state', 'tl_phase_duration', 'tl_lanes_controlled', 'tl_program', 'tl_next_switch']
dataset = pd.DataFrame(packBigData, index=None, columns=columnnames)
dataset.to_excel("output_acc.xlsx", index=False)
time.sleep(5)