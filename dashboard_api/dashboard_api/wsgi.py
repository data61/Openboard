"""
WSGI config for dashboard_api project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import sys
import os

base_path = '{0}/../..'.format(os.path.dirname(os.path.abspath(__file__)))
sys.path.append('{0}/dashboard_api'.format(base_path))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dashboard_api.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
