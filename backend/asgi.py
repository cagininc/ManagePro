import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import  notifications.routing 

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # HTTP protocol works like django apps
    "websocket": AuthMiddlewareStack(
        URLRouter(
            # WebSocket 
            notifications.routing.websocket_urlpatterns
        )
    ),
})
