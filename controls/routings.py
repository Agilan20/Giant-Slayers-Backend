
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'parameters/$', consumers.MyConsumer.as_asgi()),
    re_path(r'location/(?P<vehicle_id>[\w\.-]+)/$', consumers.LocationConsumer.as_asgi())
]
