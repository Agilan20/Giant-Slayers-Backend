import traci
import time
import traci.constants as tc
import pytz
import datetime
from random import randrange
import pandas as pd
import random
import math

def getdatetime(startTime, addOn):
        
        currentDT = startTime.astimezone(pytz.timezone("Asia/Calcutta"))+ datetime.timedelta(seconds=addOn)
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

def calculate_rpm(speed, diameter):
    # Calculate circumference
    circumference = math.pi * diameter
    
    # Convert speed from m/s to m/min
    speed_m_per_min = speed * 60
    
    # Calculate RPM
    rpm = speed_m_per_min / circumference
    
    return rpm
  

def calculate_tire_pressure_rise(initial_pressure_psi, distance_traveled, variance_factor=0.000005,pressure_change_per_meter=0.00000000000000001):

    psi_to_pa_conversion = 6894.76

    initial_pressure_pa = initial_pressure_psi * psi_to_pa_conversion
    final_pressure_pa = initial_pressure_pa

    for _ in range(round(distance_traveled)):
        delta_pressure_pa = pressure_change_per_meter

        variance = random.uniform(0, variance_factor * initial_pressure_pa)
        delta_pressure_pa += variance

        final_pressure_pa += delta_pressure_pa

    final_pressure_psi = final_pressure_pa / psi_to_pa_conversion

    return final_pressure_psi
  
def estimate_oil_life(speed, rpm):
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
  
sumoCmd = ["sumo", "-c", "osm.sumocfg"]
traci.start(sumoCmd)

packVehicleData = []
packTLSData = []
packBigData = []

simulation_duration_limit = 5


# lane to block
lane_probabilities = {
    'lane1': 0.5,
    'lane2': 0.3,
    'lane3': 0.2
}
min_speed_req=8
min_width_req=2


## params needed: probs_reasons, acc_prob, fail_prob

reasons=["punc_front_left","punc_front_right","punc_rear_left","punc_rear_right","fuel_leak","engine_failure"]
prob_reasons=[0.1,0.1,0.1,0.1,0.1,0.5]
naive_prob=0.1
acc_prob=naive_prob/simulation_duration_limit


# Record the start time
start_time = pytz.utc.localize(datetime.datetime.utcnow())
break_down_veh=list()

counter=0
block_prob=0.1
ls = []

tank_capacity_ml = 60000
fuel = [0 for i in range(10000)]
pressure = [32 for i in range(10000)]


while traci.simulation.getMinExpectedNumber() > 0 and counter<simulation_duration_limit:
  
        
        counter=counter+1
        current_time = getdatetime(start_time, counter)
        
        
        vehicles=traci.vehicle.getIDList()
        trafficlights=traci.trafficlight.getIDList()
        
        lane_list=traci.lane.getIDList()
        print("-------", len(lane_list), len(vehicles))
        speed_filtered_value=[lane for lane in lane_list if traci.lane.getMaxSpeed(lane)>min_speed_req]
        width_filtered_value=[lane for lane in speed_filtered_value if traci.lane.getWidth(lane)>min_width_req]
        road_purpose_filter=['army','vip','emergency','truck']
        purpose_filtered_road=[lane for lane in width_filtered_value if len(set(traci.lane.getAllowed(lane)).intersection(road_purpose_filter))!=0]
        
        if random.random()<=block_prob:
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


          n_veh=int(random.uniform(20,30))
          # print("Number of blocking vehicles is ",n_veh)
  #         for i in range(n_veh):
  #             # traci.vehicle.add("blocker" + str(len(traci.vehicle.getIDList()) + 3), routeID=route_id)
  #             connected_edges = traci.lane.getEdgeID(lane_to_block)
  #             j=i
  # # Create a route with the selected lane and its connected edges
  #             while True:
                  
  #                 new_veh_add="blocker_vehicle_"+str(j+random.randint(100,10000))
  #                 if new_veh_add not in traci.vehicle.getIDList():
  #                     traci.vehicle.add(new_veh_add, routeID=route_id)
  #                     print("Vehicle has been added")
  #                     break
  #                 else:
  #                     j=j+1
          for i in range(n_veh):
              j = i
              while True:
                  new_veh_add = "blocker_vehicle_" + str(j + random.randint(1000, 9000000))
                  if new_veh_add not in traci.vehicle.getIDList():
                      traci.vehicle.add(new_veh_add, routeID=route_id)
                      print("Vehicle has been added")
                      break
                  else:
                      j += 1

        

        traci.simulationStep()
        

        for i in range(0,len(vehicles)):

                #ignition
                ignited = False
                seat_belt = False

                #Function descriptions
                #https://sumo.dlr.de/docs/TraCI/Vehicle_Value_Retrieval.html
                #https://sumo.dlr.de/pydoc/traci._vehicle.html#VehicleDomain-getSpeed

                vehid = vehicles[i]
                x, y = traci.vehicle.getPosition(vehicles[i])
                coord = [x, y]
                lon, lat = traci.simulation.convertGeo(x, y)
                gpscoord = [lon, lat]
                spd = round(traci.vehicle.getSpeed(vehicles[i])*3.6,2)
                
                odomDist=traci.vehicle.getDistance(vehicles[i])
                displacement = round(traci.vehicle.getDistance(vehicles[i]),2)
                impatience=traci.vehicle.getImpatience(vehicles[i])
                
                
                # rpm
                wheel_diameter = 0.5
                # rpm = (traci.vehicle.getSpeed(vehicles[i]) * 60) / (3.14159 * wheel_diameter)
                rpm = calculate_rpm(traci.vehicle.getSpeed(vehicles[i]), wheel_diameter)
                
                oil_life = estimate_oil_life(traci.vehicle.getSpeed(vehicles[i]), rpm)
                
                # tire pressure
                initial_pressure_psi = pressure[i]
                
                final_pressure_psi = calculate_tire_pressure_rise(initial_pressure_psi, odomDist)
                pressure[i] = final_pressure_psi
                
                #fuel consumption
                initial_fuel_level_mg = fuel[i]
                current_fuel_level_mg = traci.vehicle.getFuelConsumption(vehicles[i])
                consumed_fuel_level = initial_fuel_level_mg + current_fuel_level_mg
                fuel[i] = consumed_fuel_level
                fuel_consumption = 100 - (consumed_fuel_level / (tank_capacity_ml * 1000)) * 100
                # fuel_consumption = traci.vehicle.getFuelConsumption(vehicles[i])
                
                # case of ignition
                if(consumed_fuel_level > 0 or (displacement != 0) or (spd != 0 and rpm!=0 and acc!=0)):
                  ignited = True
                else:
                  ignited = False
                
                # case of seat belt latched
                if(ignited or (consumed_fuel_level > 0) or (displacement != 0) or impatience==0 or (spd != 0 and rpm!=0 and acc!=0)):
                  seat_belt = True
                else:
                  seat_belt = False
                  
                
                
                edge = traci.vehicle.getRoadID(vehicles[i])
                lane = traci.vehicle.getLaneID(vehicles[i])
                turnAngle = round(traci.vehicle.getAngle(vehicles[i]),2)
                
                nextTLS = traci.vehicle.getNextTLS(vehicles[i])
                acc=traci.vehicle.getAcceleration(vehicles[i])
                fuelCons=traci.vehicle.getFuelConsumption(vehicles[i])
                eleCons=traci.vehicle.getElectricityConsumption(vehicles[i])
                sigma=traci.vehicle.getImperfection(vehicles[i])

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

                          

                    


                      


# (time.time() - start_time) < simulation_duration_limit

                #Packing of all the data for export to CSV/XLSX
                # vehList = [getdatetime(), vehid, coord, gpscoord, spd, edge, lane, displacement, turnAngle, nextTLS]
                vehList = [
                           current_time, 
                            # counter, 
                           vehid,
                           gpscoord, 
                           spd, 
                           acc, 
                           rpm, 
                           fuel_consumption, 
                           oil_life,
                          #  edge, 
                          #  lane, 
                           displacement, 
                           turnAngle, 
                          #  nextTLS, 
                           odomDist, 
                           final_pressure_psi, 
                           impatience,
                           "Yes" if seat_belt else "No",
                           "Yes" if ignited else "No"]

                
                
                

                print("Vehicle: ", vehid, " at datetime: ", current_time)
                print("Vehicle: ", vehid, " at datetime: ", counter)
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
                                
                                # print(trafficlights[k], " --->", \
                                #       #Returns the named tl's state as a tuple of light definitions from rRgGyYoO, for red,
                                #       #green, yellow, off, where lower case letters mean that the stream has to decelerate
                                #         " TL state: ", traci.trafficlight.getRedYellowGreenState(trafficlights[k]), " |" \
                                #       #Returns the default total duration of the currently active phase in seconds; To obtain the
                                #       #remaining duration use (getNextSwitch() - simulation.getTime()); to obtain the spent duration
                                #       #subtract the remaining from the total duration
                                #         " TLS phase duration: ", traci.trafficlight.getPhaseDuration(trafficlights[k]), " |" \
                                #       #Returns the list of lanes which are controlled by the named traffic light. Returns at least
                                #       #one entry for every element of the phase state (signal index)                                
                                #         " Lanes controlled: ", traci.trafficlight.getControlledLanes(trafficlights[k]), " |", \
                                #       #Returns the complete traffic light program, structure described under data types                                      
                                #         " TLS Program: ", traci.trafficlight.getCompleteRedYellowGreenDefinition(trafficlights[k]), " |"
                                #       #Returns the assumed time (in seconds) at which the tls changes the phase. Please note that
                                #       #the time to switch is not relative to current simulation step (the result returned by the query
                                #       #will be absolute time, counting from simulation start);
                                #       #to obtain relative time, one needs to subtract current simulation time from the
                                #       #result returned by this query. Please also note that the time may vary in the case of
                                #       #actuated/adaptive traffic lights
                                #         " Next TLS switch: ", traci.trafficlight.getNextSwitch(trafficlights[k]))

                #Pack Simulated Data
                packBigDataLine = flatten_list([vehList])
                packBigData.append(packBigDataLine)

                NEWSPEED = 15 
       
        # time.sleep(1)        


traci.close()

print("Counter Value is ",counter)
#Generate Excel file
columnnames = ['Date and Time', 
               'Vehicle ID', 
               'GPS', 
               'Speed', 
               'Acceleration', 
               'RPM', 
               'Fuel Percentage', 
               'Fuel Oil Percentage',
              #  'edge', 
              #  'lane', 
               'Displacement', 
               'Turn Angle', 
              #  'NextTLS', 
               'Odometer', 
               'Pressure', 
               'Impatience',
               'Seat Belt',
               'Ignited']
                # 'tflight', 'tl_state', 'tl_phase_duration', 'tl_lanes_controlled', 'tl_program', 'tl_next_switch']
dataset = pd.DataFrame(packBigData, index=None, columns=columnnames)
dataset.to_excel("output_acc21.xlsx", index=False)