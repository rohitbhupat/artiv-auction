from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from ..art_auction.consumers import BidConsumer, NotificationConsumer, BidUpdateConsumer
from art_auction.custom_channel_layer import CustomChannelLayer

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter([
            path('ws/bid/<str:artwork_id>/', BidConsumer.as_asgi()),
            path('ws/notifications/', NotificationConsumer.as_asgi()),
            path('ws/bid_updates/<str:product_id>/', BidUpdateConsumer.as_asgi()),
        ])
    ),
    'channel': CustomChannelLayer,
})
