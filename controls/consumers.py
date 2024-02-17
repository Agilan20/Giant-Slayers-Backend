import json
from channels.generic.websocket import AsyncWebsocketConsumer
import time
import asyncio

# for updating location of vehicles

class LocationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()
        veh_id = self.scope["url_route"]["kwargs"]["vehicle_id"]
        asyncio.create_task(self.fetch_and_send_data(veh_id))

    async def fetch_and_send_data(self,veh_id):
        while True:
            data = {'message': 'Hello from the server!'}

            await self.send(text_data=json.dumps(data))

            await asyncio.sleep(5)

# for updating parameters of vehicles based on frequency
class ParameterConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()
        veh_id = self.scope["url_route"]["kwargs"]["vehicle_id"]
        asyncio.create_task(self.fetch_and_send_data(veh_id))


    async def fetch_and_send_data(self,veh_id):
        while True:
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
