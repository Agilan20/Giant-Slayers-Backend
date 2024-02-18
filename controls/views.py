from django.shortcuts import render
from django.http import JsonResponse
from sumo_environment.index import manager
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.cache import cache
from sumo_environment.index import collection
import json 
from sumo_environment.index import manager 
import datetime 

@csrf_exempt
@require_POST
# get vehicle start point , end point , vehicle_id 
def create_vehicle(request):
    temp = request.POST
    data = dict()
    for i in temp :
        data[i] = temp[i]
    print(data)
    manager.event_queue.put(
        {"type": "add_vehicle", "data": data})
    return JsonResponse({"message": "Successfully created"})


@csrf_exempt
@require_POST
#get vehicle id , parameter , new_frequency 
def update_vehicle_parameter(request):
    temp = request.POST
    data = dict()
    for i in temp :
        data[i] = temp[i]

    manager.event_queue.put({"type": "update_parameter", "data": data})
    return JsonResponse({"message": "Frequency has been updated successfully"})

# @csrf_exempt
# @require_POST
# #get vehicle_id , start/end location tracking 
# def publish_location(request):
#     data = request.POST
#     manager.event_queue.put({"type": "publish_location", "data": {"mode":data["mode"]}})
#     return JsonResponse({"message": "Location publishing updates changed"})

@csrf_exempt
@require_POST
def get_data(request):
    data = request.POST 
    vehicle_id = data.get("vehicle_id")
    parameter = data.get("parameter")
    print(vehicle_id,parameter)
    query = {"vehicle_id": vehicle_id ,"parameter" :parameter}
    print(query)
    data = list(collection.find(query).sort("time",1).limit(20))

    for item in data:
        item["_id"] = str(item["_id"])
        item["time"] = item["time"].strftime("%Y-%m-%d %H:%M:%S")

    return JsonResponse({"message":"Done","data":data})

@csrf_exempt
@require_POST
def get_vehicle_parameter(request):
    data = request.POST
    vehicle_id = data.get("vehicle_id")
    print(vehicle_id)
    data = manager.cars[vehicle_id].frequency
    item = dict()
    for i in data:
        item[i] = dict()
        item[i]["frequency"] = data[i]["frequency"]
        item[i]["updated_at"] = data[i]["last_log_time"].strftime("%Y-%m-%d %H:%M:%S")

    return JsonResponse({"message": "Fetched" , "data" : json.dumps(item)})

@require_POST
@csrf_exempt
def lane_to_block(request):
    manager.event_queue.put({
         "type" : "lane_to_block"
    })
    
    return JsonResponse({"message":"Success"})
