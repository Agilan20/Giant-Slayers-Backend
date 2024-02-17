import traci
import random
import time

# Connect to the SUMO simulation
sumoCmd = ["sumo", "-c", "osm.sumocfg"]
traci.start(sumoCmd)

# Define the probability of adding a vehicle on a specific lane
lane_probabilities = {
    'lane1': 0.5,
    'lane2': 0.3,
    'lane3': 0.2
}

# Simulation loop
lane_list=traci.lane.getIDList()
# print(lane_list)

print("The count of lanes is ",len(lane_list))
min_speed_req=8
min_width_req=2

## speed req is in m/s
## min width is in m


# print("The shape of lane 1 is ",traci.lane.getShape(lane_list[5]))
# print("The disallowed of lane 1 is ",traci.lane.getDisallowed(lane_list[5]))
# print("The allowed of lane 1 is ",traci.lane.getAllowed(lane_list[5]))
# speed_set=set()

speed_filtered_value=[lane for lane in lane_list if traci.lane.getMaxSpeed(lane)>min_speed_req]
width_filtered_value=[lane for lane in speed_filtered_value if traci.lane.getWidth(lane)>min_width_req]
road_purpose_filter=['army','vip','emergency','truck']
purpose_filtered_road=[lane for lane in width_filtered_value if len(set(traci.lane.getAllowed(lane)).intersection(road_purpose_filter))!=0]

# print("Final Filtered Out Roads Are: ",purpose_filtered_road)
print("Lenght of filtered out roads is ",len(purpose_filtered_road))
# for i in range(len(lane_list)):
#     print("The max speed of lane 1 is ",traci.lane.getMaxSpeed(lane_list[i]))
#     speed_set.add(traci.lane.getMaxSpeed(lane_list[i]))
# # print("The width of lane 1 is ",traci.lane.getWidth(lane_list[5]))

# print("The list of unique speed values is ",speed_set)




block_prob=0.1
counter=0
while traci.simulation.getMinExpectedNumber() > 0 and counter<100000:
    counter=counter+1
    # Add vehicles based on probabilities
    if random.random()<=block_prob:
        print("Proceeding to block a lane")
        while True:
            lane_to_block=random.choice(purpose_filtered_road)
            if lane_to_block in traci.lane.getIDList():
                print("found a proper lane")
                break
            else:
                print("failed to find a proper lane")
        print("Lane to block is ",lane_to_block)
        # lane_to_block=lane_to_block[:-4]+lane_to_block[-2:len(lane_to_block)]
        # lane_to_block = lane_to_block[:-2]
        print("Lane to block is ",lane_to_block)



        route_id = "blocker_route_" + str(len(traci.route.getIDList()) + 1)
        connected_edges = traci.lane.getEdgeID(lane_to_block)

        print(connected_edges)

        traci.route.add(route_id, [connected_edges] + [connected_edges])


        n_veh=int(random.uniform(20,30))
        print("Number of blocking vehicles is ",n_veh)
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

        

    

    # Simulate one simulation step
    traci.simulationStep()

    # Add your additional logic here if needed

    # Sleep for a short duration to control the simulation speed
    time.sleep(0.1)

# Close the connection to SUMO
traci.close()




