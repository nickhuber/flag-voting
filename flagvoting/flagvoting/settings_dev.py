from .settings import *

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    *MIDDLEWARE,
]

INTERNAL_IPS = [
    "192.168.1.50",
]

INSTALLED_APPS.append("debug_toolbar")
