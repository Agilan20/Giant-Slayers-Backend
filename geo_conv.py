import traci
import time
import traci.constants as tc
import pytz
import datetime
from random import randrange
import pandas as pd



sumoCmd = ["sumo", "-c", "osm.sumocfg"]
traci.start(sumoCmd)
# x,y=12008.96542033627, 3716.079607686149
x,y=1.322390, 103.739745
# x,y=11983.80,3722.52
# lon, lat = traci.simulation.convertGeo(x, y)
# print("\n")
# print(lon,lat)
print("Value 1 ")
lon1, lat1 = traci.simulation.convertGeo(x, y,fromGeo=False)
print(lon1,lat1)
print("\n")


print("Value 2 ")
lon1, lat1 = traci.simulation.convertGeo(y, x,fromGeo=False)
print(lon1,lat1)
print("\n")

print("Value 3 ")
ans=traci.simulation.convertRoad(x,y,isGeo=True)
print(ans)

print("Value 4")
ans1=traci.simulation.convertRoad(x,y)
print(ans1)

print("Value 5 Workings ")
ans=traci.simulation.convertRoad(y,x,isGeo=True)
print(ans)

print("Value 6")
ans1=traci.simulation.convertRoad(y,x)
print(ans1)
