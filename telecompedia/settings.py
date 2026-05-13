import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-your-secret-key-change-in-production'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',  # Add this line

    # Third party apps
    'crispy_forms',
    'crispy_bootstrap5',
    'django_countries',
    
    # Local apps
    'telecom',
    'users',
    'plans',
    'payments',
    'notifications',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'telecompedia.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'telecom.context_processors.global_data',
            ],
        },
    },
]

WSGI_APPLICATION = 'telecompedia.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTH_USER_MODEL = 'users.CustomUser'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'

# Payment Gateway Settings
RAZORPAY_KEY_ID = 'rzp_test_S9Nry6FbsLPWnJ'
RAZORPAY_KEY_SECRET = 'BG838K1LuxxJ2SD7Q8Yy4VcY'

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-email-password'
DEFAULT_FROM_EMAIL = 'TelecomPedia <noreply@telecompedia.com>'



# # Add these to your settings.py
# RAZORPAY_KEY_ID = 'your_razorpay_key_id'
# RAZORPAY_KEY_SECRET = 'your_razorpay_key_secret'
# RAZORPAY_WEBHOOK_SECRET = 'your_webhook_secret'


# settings.py
import os
INFOBIP_SIMULATION_MODE = False  # Set to False for production
# settings.py - Add these lines at the bottom

# Infobip Configuration
INFOBIP_API_KEY = '456e48165c4e0630d3387fa358b5e376-5f3b404b-0218-4d3b-b814-f7ba472ac545'

INFOBIP_BASE_URL = 'x19rj4.api.infobip.com'
INFOBIP_BASE_URL_FULL = f"https://{INFOBIP_BASE_URL}"

# These are the IDs you just generated from the setup script
INFOBIP_2FA_APPLICATION_ID = '573AA8224B135491F6921E09D590C831'
INFOBIP_2FA_MESSAGE_TEMPLATE_ID = '5E4DEB0796B9BE301DA94B6918E93ADF'