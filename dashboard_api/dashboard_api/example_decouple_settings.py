#   Copyright 2018 CSIRO
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


"""
Decoupled django settings for dashboard_api project.

See also example_decouple.env

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

from dashboard_api.base_settings import *
import dj_database_url
from decouple import config, Csv
import random
import string

# SECURITY WARNING: keep the secret key used in production secret!
# Take secret key from environment - default to a random string.
default_key = ''.join([
    random.SystemRandom().choice(
        "{}{}{}".format(string.ascii_letters, string.digits, string.punctuation))
    for i in range(50)
])
SECRET_KEY = config('SECRET_KEY', default=default_key) #'k_&ywy8shj9!_zsyvlr1+z25z_8e9_t1m1c+qi9lp3tqn^a-fo'

# Set to true if servers are behind a load-balancing proxy that sets the "X_FORWARDED_HOST" header.
USE_X_FORWARDED_HOST = config('USE_X_FORWARDED_HOST', default=False, cast=bool)

# Database
DATABASE_URL = config('DATABASE_URL', default="postgis://dashboard:passwd@127.0.0.1:5432/dashboard")
DATABASES = {'default': dj_database_url.parse(DATABASE_URL)}
DATABASES['default']['TEST'] = {'NAME': 'dashboard_test'}

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

# ALLOWED HOSTS must be set in production, eg:
# ALLOWED_HOSTS = [ 'myserver.com.au', 'myserver_alternatename.com.au' ]
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv(), default=[])

# Sample file-cache config.  Omit CACHES if using external (e.g. AWS Cloudfront) caching
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': config('FILE_CACHE_LOCATION', default='/var/www/coag2_cache'),
    }
}

# URL path used by Session Cookie and name of session cookie
SESSION_COOKIE_PATH = "/api/"
SESSION_COOKIE_NAME = 'openboard_sessionid'

# Allow Public access to API (for themes that are marked as not requiring auth)
PUBLIC_API_ACCESS = config('PUBLIC_API_ACCESS', default=False, cast=bool)

