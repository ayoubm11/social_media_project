"""
ASGI config for social_media_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_media_project.settings')

django_asgi_app = get_asgi_application()

from apps.social import routing as social_routing

application = ProtocolTypeRouter({
	"http": django_asgi_app,
	"websocket": AuthMiddlewareStack(
		URLRouter(
			social_routing.websocket_urlpatterns
		)
	),
})
