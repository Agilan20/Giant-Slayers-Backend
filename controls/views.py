from django.shortcuts import render
from django.http import JsonResponse
from sumo_environment.index import manager
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.cache import cache


def create_vehicle(request):
    manager.event_queue.put(
        {"type": "add_vehicle", "data": {"car_id": "veh0"}})
    return JsonResponse({"message": "Successfully created"})


@csrf_exempt
@require_POST
def update_vehicle_parameter(request):
    data = request.POST
    input_data = dict()
    for i in data:
        input_data[i] = data[i]
    print(input_data)

    manager.event_queue.put({"type": "update_parameter", "data": input_data})
    return JsonResponse({"message": "Frequency has been updated successfully"})

@csrf_exempt
@require_POST
def publish_location(request):
    data = request.POST
    manager.event_queue.put({"type": "publish_location", "data": {"mode":data["mode"]}})
    return JsonResponse({"message": "Location publishing updates changed"})


def get_vehicle_parameter(request):
    print(cache.get("veh0_speed"))
    return JsonResponse({"message": cache.get("veh0_speed")})
