import json
from channels.generic.websocket import AsyncWebsocketConsumer
import time
import asyncio
from django.core.cache import cache
import threading 
from sumo_environment.index import location_dict 
# for updating location of vehicles

class LocationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()
        veh_id = self.scope["url_route"]["kwargs"]["vehicle_id"]
        if veh_id == "all":
            threading.Thread(target=self.fetch_and_send_data, args=(None,), daemon=True).start()
        else:
            threading.Thread(target=self.fetch_and_send_data, args=(veh_id,), daemon=True).start()
    

    def fetch_and_send_data(self, veh_id):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def async_function():
            while True:
                if veh_id is None:
                    await self.send(text_data=json.dumps(location_dict))
                else:
                    import traci
                    x, y = traci.vehicle.getPosition(veh_id)
                    x, y = traci.simulation.convertGeo(x, y)
                    print(x, y)
                    await self.send(text_data=json.dumps({"location": [x, y]}))
                await asyncio.sleep(1)  # Adjust the sleep duration as needed
        print("hi")
        loop.run_until_complete(async_function())
        loop.close()

# for updating parameters of vehicles based on frequency
class ParameterConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()
        veh_id = self.scope["url_route"]["kwargs"]["vehicle_id"]
        asyncio.create_task(self.fetch_and_send_data())


    async def fetch_and_send_data(self):
        while True:
            print("Started")
            #get all paramter from  
            await asyncio.sleep(2)

    async def send_data(self, event):
        data = event["data"]
        await self.send(text_data=json.dumps(data))

    async def start_sending(self):
        try:
            while True:
                print("baby")
                await self.send(text_data="hi")
                # traci.simulationStep()

                # vehicle_position = traci.vehicle.getPosition("veh0")
                # latitude, longitude = traci.simulation.convertGeo(*vehicle_position)

                # print(latitude, longitude)

                # Use channels.layers to send data to the WebSocket consumer
                # channel_layer = get_channel_layer()
                # message = {
                #     "type": "websocket.send",
                #     "text": json.dumps({'message': (latitude, longitude)})
                # }
                # async_to_sync(channel_layer.send)('hi', message)

                time.sleep(4)

        except Exception as e:
            print(e)
