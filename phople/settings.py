import configparser
import os
from urllib.error import URLError
from urllib.request import urlopen

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$!21i-kg*8o%z6%2s9-0t9z2e_cfv^h8ql8(jf&+!jr#$l3w-*'
AUTH_USER_MODEL = 'apiserver.User'
CREDENTIAL = configparser.ConfigParser()
CREDENTIAL.read(os.path.join(BASE_DIR, 'credentials', 'phople.cfg'))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
PRODUCTION = False
try:
    urlopen('http://169.254.169.254/latest/meta-data/', timeout=1).read()
    # DEBUG = False # TODO uncomment this when development reached at stable version
    PRODUCTION = True
    print('Running in Production Environment')
except URLError:
    print('Running in Development Environment')

# django CORS. see https://github.com/ottoyiu/django-cors-headers
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = (
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'apiserver',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'phople.middleware.CsrfCookieToHeader',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
)

ROOT_URLCONF = 'phople.urls'
WSGI_APPLICATION = 'phople.wsgi.application'
APPEND_SLASH = False

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

REST_FRAMEWORK = {
    # Paginator must be specified explicitly
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',
                                'rest_framework.filters.OrderingFilter')
}

p = CREDENTIAL['Postgres'] if PRODUCTION else CREDENTIAL['PostgresTest']
DATABASES = {
    'default': {
        'ENGINE': p['ENGINE'],
        'NAME': p['NAME'],
        'USER': p['USER'],
        'PASSWORD': p['PASSWORD'],
        'HOST': p['HOST'],
        'PORT': p['PORT'],
    }
}

# AWS util settings. see 'apiserver.util.aws'
S3_FILE_BUCKET_NAME = 'file-phople-us'

LANGUAGE_CODE, TIME_ZONE, USE_I18N, USE_L10N, USE_TZ = 'en-us', 'Asia/Seoul', True, True, True
STATIC_URL = '/static/'  # Not used. remained for support django bootstrapping
