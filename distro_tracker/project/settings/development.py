"""
Appropriate settings to run during development.

When running in development mode, selected.py should point to this file.
"""

from .defaults import INSTALLED_APPS, MIDDLEWARE_CLASSES

DEBUG = True
TEMPLATE_DEBUG = True

ADMINS = ()

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SITE_URL = 'http://127.0.0.1:8000'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

XHR_SIMULATED_DELAY = 0.5

INSTALLED_APPS += (
    'debug_toolbar',
)
