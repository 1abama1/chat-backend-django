"""
ASGI config for backend project.
"""
import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

django.setup()

from backend.routing import websocket_urlpatterns
from backend.middleware import JwtAuthMiddleware

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JwtAuthMiddleware(
        URLRouter(websocket_urlpatterns)
    ),
})
