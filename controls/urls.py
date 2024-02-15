
from . import views
from django.urls import path,include 

urlpatterns = [
    path('create_vehicle/',views.create_vehicle),
    path('update_parameters/',views.update_vehicle_parameter)
]
