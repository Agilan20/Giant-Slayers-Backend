
from . import views
from django.urls import path,include 

urlpatterns = [
    path('create_vehicle/',views.create_vehicle),
    path('update_parameters/',views.update_vehicle_parameter),
    path('get_parameters/',views.get_vehicle_parameter)  ,
    path('publish_location/',views.publish_location) 
]
