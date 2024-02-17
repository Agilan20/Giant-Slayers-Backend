
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'parameters/(?P<vehicle_id>[\w\.-]+)$', consumers.ParameterConsumer.as_asgi()),
    re_path(r'location/(?P<vehicle_id>[\w\.-]+)/$', consumers.LocationConsumer.as_asgi())
]
