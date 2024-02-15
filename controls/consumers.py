import json
from channels.generic.websocket import AsyncWebsocketConsumer
import traci
import time
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import asyncio
import threading


class MyConsumer(AsyncWebsocketConsumer):
    connected_clients = set()
    continuous_data_task = None

    async def connect(self):
        await self.accept()
        self.connected_clients.add(self.channel_name)

        # Start sending data continuously if the task hasn't been started yet
        if not self.continuous_data_task:
            self.continuous_data_task = asyncio.create_task(
                self.send_continuous_data())
            vehicle_id = "vehicle1"
            traci.vehicle.add(vehicle_id,  typeID="veh_passenger", depart=0, departLane="best")

    async def disconnect(self, close_code):
        self.connected_clients.remove(self.channel_name)

    async def send_continuous_data(self):
        while True:
            # Generate or customize data for all connected clients
            data = {"message": "Hello, this is continuous data!"}

            for client_channel_name in self.connected_clients:
                traci.simulationStep()

                vehicle_position = traci.vehicle.getPosition("veh0")
                latitude, longitude = traci.simulation.convertGeo(*vehicle_position)

                print(latitude, longitude)

                data = (latitude,longitude,)

                await self.channel_layer.send(
                    client_channel_name,
                    {
                        "type": "send.data",
                        "data": data,
                    },
                )

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
