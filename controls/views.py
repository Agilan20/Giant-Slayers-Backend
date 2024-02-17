from django.shortcuts import render
from django.http import JsonResponse
from sumo_environment.index import manager
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.cache import cache
from sumo_environment.index import collection
import json 

@csrf_exempt
@require_POST
# get vehicle start point , end point , vehicle_id 
def create_vehicle(request):
    temp = request.POST
    data = dict()
    for i in temp :
        data[i] = temp[i]
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

@csrf_exempt
@require_POST
#get vehicle_id , start/end location tracking 
def publish_location(request):
    data = request.POST
    manager.event_queue.put({"type": "publish_location", "data": {"mode":data["mode"]}})
    return JsonResponse({"message": "Location publishing updates changed"})

@csrf_exempt
@require_POST
def get_vehicle_parameter(request):
    data = request.POST
    parameter = data.get("parameter")
    vehicle_id = data.get("vehicle_id")
    print(parameter, vehicle_id)

    query = {
        "parameter": parameter,
        "vehicle_id": vehicle_id,
    }
    
    # Correct the field name to "vehicle_id"
    data = collection.find(query, {'_id': 0, 'time': 0})

    data = list(data)

    print(data)
    
    return JsonResponse({"message": "Fetched" , "data" : json.dumps(data)})
