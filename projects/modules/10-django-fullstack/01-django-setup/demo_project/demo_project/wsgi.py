"""
WSGI config for demo_project.

It exposes the WSGI callable as a module-level variable named ``application``.
For more information:
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "demo_project.settings")

# This is the WSGI application object that web servers use.
# Gunicorn, uWSGI, or Apache mod_wsgi will import this.
application = get_wsgi_application()
