from django.shortcuts import render
from django.http import JsonResponse
from sumo_environment.index import manager

def create_vehicle(request):
    manager.event_queue.put({"type":"add_vehicle","data":{"car_id":"veh0"}})
    return JsonResponse({"message":"Successfully created"})

def update_vehicle_parameter(request):
    manager.event_queue.put({"type":"update_parameter","data":{"car_id":"veh0"}})
    return JsonResponse({"message":"Successfully updated"})



