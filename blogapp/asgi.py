import os

from chat.routing import websocket_urlpatterns
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.security.websocket import AllowedHostsOriginValidator
# Authmiddle ware stack support standatd django authentication and where the user details are stored in session
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
"""
Protocol type router will fitst inspect the type of connection that is made to channels development server
if it is a websocket connection ws or wss
It will then be given to auth middleware stack 

"""
application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
    ),
})
