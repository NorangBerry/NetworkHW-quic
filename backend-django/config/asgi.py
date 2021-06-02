"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django.setup()

application = get_asgi_application()


#hypercorn config.asgi:application
#python3 manage.py runsslserver --certificate public.pem --key private.pem
#hypercorn --certfile public.pem --keyfile private.pem --bind 0.0.0.0:8000 config.asgi:application --quic-bind 0.0.0.0:8001