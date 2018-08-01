"""
Django settings for kiramama project.

Generated by 'django-admin startproject' using Django 1.9.8.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""
# from __future__ import absolute_import
import os
from datetime import timedelta
from django.utils.translation import ugettext_lazy as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/
PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
PROJECT_ROOT = os.path.abspath(os.path.join(PROJECT_PATH, os.pardir))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'redis',
    #'django_extensions',
    'import_export',
    'kiramama_app',
    'health_administration_structure_app',
    'public_administration_structure_app',
    'rest_framework',
    'djcelery'
]


MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

ROOT_URLCONF = 'kiramama.urls'

SECRET_KEY = 'ch25angeth23i@ssecr1!!$)(etke@%/32y'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
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

WSGI_APPLICATION = 'kiramama.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/
# Provide a lists of languages which your site supports.
LANGUAGES = (
    ('en', _('English')),
    ('fr', _('French')),
)

LANGUAGE_CODE = 'en-US'

TIME_ZONE = 'Africa/Bujumbura'

USE_THOUSAND_SEPARATOR = True

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(PROJECT_PATH,  'media')

MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(PROJECT_PATH,  'static')

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'staticfiles'),
)

# Tell Django where the project's translation files should be.
LOCALE_PATHS = (
    os.path.join(PROJECT_PATH, 'locale'),
)

#The below setting is to define the setting_code of the setting about active/not active for community health workers
#It's value will be the setting_code of the corresponding setting in Settings model.
KEY_WORD_FOR_CHW_ACTIVE_SETTING = 'CHWAI'

KNOWN_PREFIXES = {
    'REG': 'SELF_REGISTRATION',
    'GRO': 'PREGNANT_CASE_REGISTRATION',
    'CPN': 'PRENATAL_CONSULTATION_REGISTRATION',
    'NSC': 'BIRTH_REGISTRATION',
    'CON': 'POSTNATAL_CARE_REPORT',
    'VAC': 'CHILD_FOLLOW_UP_REPORT',
    'RIS': 'RISK_REPORT',
    'ARR': 'REPORT_MOTHER_ARRIVED_AT_HF',
    'RER': 'RESPONSE_TO_RISK_REPORT',
    'DEC': 'DEATH_REPORT',
    'DEP': 'LEAVE_REPORT',
    'REC': 'RECEPTION_REPORT',
    'REGM': 'SELF_REGISTRATION_M',
    'GROM': 'PREGNANT_CASE_REGISTRATION_M',
    'CPNM': 'PRENATAL_CONSULTATION_REGISTRATION_M',
    'NSCM': 'BIRTH_REGISTRATION_M',
    'CONM': 'POSTNATAL_CARE_REPORT_M',
    'VACM': 'CHILD_FOLLOW_UP_REPORT_M',
    'RISM': 'RISK_REPORT_M',
    'RERM': 'RESPONSE_TO_RISK_REPORT_M',
    'DECM': 'DEATH_REPORT_M',
    'DEPM': 'LEAVE_REPORT_M',
    'RECM': 'RECEPTION_REPORT_M',
}

EXPECTED_NUMBER_OF_VALUES = {
    'SELF_REGISTRATION': 5,
    'PREGNANT_CASE_REGISTRATION': 6,
    'PRENATAL_CONSULTATION_REGISTRATION': 7,
    'BIRTH_REGISTRATION': 9,
    'POSTNATAL_CARE_REPORT': 8,
    'CHILD_FOLLOW_UP_REPORT': 5,
    'RISK_REPORT': 4,
    'REPORT_MOTHER_ARRIVED_AT_HF': 2,
    'RESPONSE_TO_RISK_REPORT': 4,
    'DEATH_REPORT': 5,
    'LEAVE_REPORT': 2,
    'RECEPTION_REPORT': 2,
    'SELF_REGISTRATION_M': 5,
    'PREGNANT_CASE_REGISTRATION_M': 7,
    'PRENATAL_CONSULTATION_REGISTRATION_M': 7,
    'BIRTH_REGISTRATION_M': 9,
    'POSTNATAL_CARE_REPORT_M': 8,
    'CHILD_FOLLOW_UP_REPORT_M': 5,
    'RISK_REPORT_M': 4,
    'RESPONSE_TO_RISK_REPORT_M': 4,
    'DEATH_REPORT_M': 5,
    'LEAVE_REPORT_M': 2,
    'RECEPTION_REPORT_M': 2,
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

# Django REST FRAMEWORK
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend', 'rest_framework.filters.SearchFilter',)
}

# CELERY STUFF
BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Africa/Bujumbura'
# CELERY_ALWAYS_EAGER = True
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'

RAPIDPRO_BROADCAST_URL = 'https://api.rapidpro.io/api/v2/broadcasts.json'

LOGIN_REDIRECT_URL = 'home'
LOGIN_URL = '/login/'

try:
    from localsettings import *
except ImportError:
    pass

import djcelery
djcelery.setup_loader()