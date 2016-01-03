"""
Django settings for groundup project.

Generated by 'django-admin startproject' using Django 1.8.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

import datetime
from . import local_settings

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

try:
    BASE_DIR = local_settings.BASE_DIR
except:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECRET KEY: This must be set in local_settings.py
SECRET_KEY = local_settings.SECRET_KEY

# DEBUG: This should be overriden in local_settings.py
try:
    DEBUG = local_settings.DEBUG
except:
    DEBUG = True

if DEBUG == False:
    ALLOWED_HOSTS = local_settings.ALLOWED_HOSTS
else:
    ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'grappelli.dashboard',
    'grappelli',
    'filebrowser',
    'django.contrib.admin',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'django.contrib.redirects',

    'tagulous',

    'newsroom',
    'clearcache',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
)

ROOT_URLCONF = 'groundup.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'),],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'groundup.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases
# This should be overriden in local_settings.py

try:
    DATABASES = local_settings.DATABASES
except:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Johannesburg'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SITE_ID = 1

SERIALIZATION_MODULES = {
    'xml':    'tagulous.serializers.xml_serializer',
    'json':   'tagulous.serializers.json',
    'python': 'tagulous.serializers.python',
    'yaml':   'tagulous.serializers.pyyaml',
}


# CACHES: This should be overriden in local_settings.py

try:
    CACHES = local_settings.CACHES
except:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': '/var/tmp/django_cache',
            'KEY_PREFIX': 'gu',
        }
    }


# These should be overriden in local_settings.py
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

FILEBROWSER_DIRECTORY = "uploads/"

FILEBROWSER_EXTENSIONS = {
    'Image': ['.jpg','.jpeg','.gif','.png','.tif','.tiff'],
    'Document': ['.pdf','.doc','.rtf','.txt','.xls','.csv'],
    'Video': ['.mov','.wmv','.mpeg','.mpg','.avi','.rm'],
    'Audio': ['.mp3','.mp4','.wav','.aiff','.midi','.m4p']
}

FILEBROWSER_SELECT_FORMATS =  {
    'file': ['Image','Document','Video','Audio'],
    'image': ['Image'],
    'document': ['Document'],
    'media': ['Video','Audio'],
}

FILEBROWSER_VERSIONS_BASEDIR = '_versions'

FILEBROWSER_MAX_UPLOAD_SIZE = 10485760

FILEBROWSER_NORMALIZE_FILENAME = True

FILEBROWSER_CONVERT_FILENAME = False

FILEBROWSER_OVERWRITE_EXISTING = False

GRAPPELLI_INDEX_DASHBOARD = 'groundup.dashboard.CustomIndexDashboard'

GRAPPELLI_ADMIN_TITLE = "GroundUp Administration"

NEWSROOM_ARTICLE_COPYRIGHT = '&copy; ' + str(datetime.date.today().year) + \
                             ' GroundUp. <a rel="license" href="http://creativecommons.org/licenses/by-nd/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nd/4.0/80x15.png" /></a><br />This article is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nd/4.0/">Creative Commons Attribution-NoDerivatives 4.0 International License</a>.'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
       'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': local_settings.ERROR_LOG_FILE,
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers':['file', 'mail_admins', ],
            'propagate': True,
            'level':'WARNING',
        },
    }
}


from .local_settings import *