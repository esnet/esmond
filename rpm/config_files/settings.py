import os
import os.path
from esmond.config import get_config

#
# Only Django specific things are kept in here and if they are configurable
# the value is derived from the config setting in esmond.conf.
#

TESTING = os.environ.get("ESMOND_TESTING", False)
ESMOND_CONF = os.environ.get("ESMOND_CONF")
ESMOND_ROOT = os.environ.get("ESMOND_ROOT")
ALLOWED_HOSTS = [ '*' ]

if not ESMOND_ROOT:
    raise Error("ESMOND_ROOT not defined in environment")

if not ESMOND_CONF:
    ESMOND_CONF = os.path.join(ESMOND_ROOT, "esmond.conf")

ESMOND_SETTINGS = get_config(ESMOND_CONF)

DEBUG = ESMOND_SETTINGS.debug
TEMPLATE_DEBUG = DEBUG
# Set to true to make tastypie give a full django debug page.
TASTYPIE_FULL_DEBUG = False

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': ESMOND_SETTINGS.sql_db_engine,
        'NAME': ESMOND_SETTINGS.sql_db_name,
        'HOST': ESMOND_SETTINGS.sql_db_host,
        'USER': ESMOND_SETTINGS.sql_db_user,
        'PASSWORD': ESMOND_SETTINGS.sql_db_password,
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
#TIME_ZONE = 'America/Chicago'
TIME_ZONE = 'UTC'
USE_TZ = True

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

STATIC_URL = '/esmond-static/'
STATIC_ROOT = '/usr/lib/esmond/staticfiles'

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# List of callables that know how to import templates from various sources.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'esmond.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    # We have namespaced the app oddly and it manifest when django was
    # upgraded to 1.8 - 'api' should be a discrete app in a project. Keeping
    # the 'esmond.api' entry is necessary to not break how we have historically
    # laid things out, but api.models uses app_label = 'api' in the model Meta
    # or warnings (and future incompatabilites) will occur.
    'esmond.api',
    # 'esmond.admin',
    # apps need a unique label and 'esmond.admin' clashes with the django 
    # 'admin' module, so fix it in esmond.apps by subclassing AppConfig.
    'esmond.apps.EsmondAdminConfig',
    'netfields',
    'rest_framework',
    'rest_framework.authtoken',
)

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],

    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework_filters.backends.DjangoFilterBackend',
    ),

    # Pagination parameters are being handled in custom pagination 
    # classes since pagination is only being done on a few 
    # endpoints, not globally.

    'DEFAULT_AUTHENTICATION_CLASSES': (
        # This places token based auth (analogous to old API key),
        # on ALL endpoints, but does not enforce ANY access 
        # control. That will need to be handled by a permissions
        # (or custom throttle) class.
        'rest_framework.authentication.TokenAuthentication',
    ),

    'DEFAULT_PERMISSION_CLASSES': (
        # This puts "anonymous read only" perms on all endpoints. 
        # Anything can GET, HEAD or OPTIONS. Is overridded with 
        # AllowAny in the bulk endpoints with custom auth-based
        # throttling.
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(pathname)s: %(message)s'
        },
    },
    'handlers': {
        'django_handler': {
            'level':'INFO',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/esmond/django.log',
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,
            'formatter':'standard',
        },
        'esmond_handler': {
            'level':'INFO',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/esmond/esmond.log',
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,
            'formatter':'standard',
        }
    },
    'loggers': {
        'django.request': { 
            'handlers': ['django_handler'],
            'level': 'INFO',
            'propagate': True
        },
        'esmond': { 
            'handlers': ['esmond_handler'],
            'level': 'INFO',
            'propagate': True
        },
        'espersistd.perfsonar.cass_db': { 
            'handlers': ['esmond_handler'],
            'level': 'INFO',
            'propagate': True
        },
    }
}
