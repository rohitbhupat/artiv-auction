import json
from channels.generic.websocket import AsyncWebsocketConsumer

class BidConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.artwork_id = self.scope['url_route']['kwargs']['artwork_id']
        self.room_group_name = f'artwork_{self.artwork_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        bid = text_data_json['bid']

        # Notify via WebSocket
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'new_bid',
                'bid': bid
            }
        )

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'notifications'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        notification = text_data_json['notification']

        # Notify via WebSocket
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_notification',
                'notification': notification
            }
        )

class BidUpdateConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.product_id = self.scope['url_route']['kwargs']['product_id']
        self.group_name = f"bid_updates_{self.product_id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def bid_update(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))
