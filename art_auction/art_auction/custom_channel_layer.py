# # custom_channel_layer.py

# import json
# from channels.layers import BaseChannelLayer
# from channels.db import database_sync_to_async
# from dashboard.models import Notification  # Example model where notifications are stored

# class CustomChannelLayer(BaseChannelLayer):
#     async def send(self, channel_name, message):
#         # Send message to a specific channel (not implemented in this example)
#         pass

#     async def group_add(self, group, channel):
#         # Add a channel to a group (not implemented in this example)
#         pass

#     async def group_discard(self, group, channel):
#         # Remove a channel from a group (not implemented in this example)
#         pass

#     async def group_send(self, group, message):
#         # Send a message to all channels in a group
#         message_type = message.get('type')
#         if message_type == 'send_notification':
#             notification = message.get('notification')
#             await self.send_notification(group, notification)
#         elif message_type == 'new_bid':
#             bid = message.get('bid')
#             await self.send_bid_notification(group, bid)

#     async def receive(self, channels):
#         # Receive messages from specified channels (not implemented in this example)
#         pass

#     async def flush(self):
#         # Clear all channels and groups (not implemented in this example)
#         pass

#     @database_sync_to_async
#     def send_notification(self, group, notification):
#         # Save notification to the database (if needed) and send to the group
#         Notification.objects.create(content=notification)
#         return True

#     @database_sync_to_async
#     def send_bid_notification(self, group, bid):
#         # Process bid notification logic (example: saving to database)
#         # Here you can also add logic to fetch specific users and their WebSocket channels
#         Notification.objects.create(content=f"New bid placed: {bid['bid_amt']} by {bid['user']}")
#         return True
