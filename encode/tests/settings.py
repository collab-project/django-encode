# Copyright Collab 2013-2015

import os

SITE_ID = 1

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.contenttypes',
    'django.contrib.admin',
    'celery',
    'queued_storage',
    'encode',
    'encode.tests'
]

ROOT_URLCONF = 'encode.tests.urls'

SECRET_KEY = 'top_secret'

LOCAL_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

STATIC_URL = '/static/'

MEDIA_ROOT = os.path.abspath("media")

# A tuple of directories where Django looks for translation files.
LOCALE_PATHS = (
    os.path.join(os.path.abspath("../locale")),
)

QUEUED_STORAGE_RETRIES = 0

ENCODE_MEDIA_PATH_NAME = "encode_test"

ENCODE_MEDIA_ROOT = MEDIA_ROOT

ENCODE_DEFAULT_ENCODER_CLASS = "encode.encoders.BasicEncoder"

#: Encoding profiles configuration.
ENCODE_AUDIO_PROFILES = ["MP3 Audio", "Ogg Audio"]
ENCODE_VIDEO_PROFILES = ["MP4", "WebM Audio/Video"]
ENCODE_IMAGE_PROFILES = ["PNG"]

#: Django file storage used for storing incoming media uploads.
ENCODE_LOCAL_FILE_STORAGE = LOCAL_FILE_STORAGE

#: Django file storage used for transferring media uploads to the encoder.
#: SFTP (using django-storages): 'storages.backends.sftpstorage.SFTPStorage'
ENCODE_REMOTE_FILE_STORAGE = LOCAL_FILE_STORAGE

#: Django file storage used for storing encoded media on a CDN network.
#: Rackspace (using django-cumulus): 'cumulus.storage.SwiftclientStorage'
ENCODE_CDN_FILE_STORAGE = LOCAL_FILE_STORAGE

ENCODE_LOCAL_STORAGE_OPTIONS = dict(
    #: Absolute path to the local directory that will hold user-uploaded files.
    location=MEDIA_ROOT
)

ENCODE_REMOTE_STORAGE_OPTIONS = dict(
    #: Absolute path to the directory on the remote machine that will hold
    #: transferred media files.
    location=os.path.join(ENCODE_MEDIA_ROOT, "remote")
)

#: The backend used to store task results (tombstones). Disabled by default.
CELERY_RESULT_BACKEND = None

#: If this is True, all tasks will be executed locally by blocking until the
#: task returns. That is, tasks will be executed locally instead of being sent
#: to the queue.
CELERY_ALWAYS_EAGER = True

#: If this is True, eagerly executed tasks (applied by task.apply(), or when
#: the CELERY_ALWAYS_EAGER setting is enabled), will propagate exceptions.
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

#: Use custom test runner.
TEST_RUNNER = 'encode.tests.runner.CustomTestSuiteRunner'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

# Logging configuration.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.

LOG_HANDLER = 'null'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)-6s %(name)-15s - %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(asctime)s %(levelname)-6s %(name)-15s - %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        }
    },
    'loggers': {
        'encode': {
            'handlers': [LOG_HANDLER],
            'level': 'DEBUG'
        },
        'celery': {
            'handlers': [LOG_HANDLER],
            'level': 'DEBUG'
        },
    }
}
