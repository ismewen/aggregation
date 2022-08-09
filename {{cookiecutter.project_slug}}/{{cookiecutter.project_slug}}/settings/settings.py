import os

SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'postgres://postgres:@127.0.0.1:5432/aggregation')
# SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI',
#                                     'mysql+pymysql://root:ismewen@localhost/cluster-aggregation')

SECCRET_KEY = "HELLO"
DEBUG = True
REQUEST_DEBUG = False
DEBUG_RANDOM_LATENCY = 1
SQLALCHEMY_TRACK_MODIFICATIONS=False

APP_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # refers to application_topS

import logging.config

LOGGING = {
    'version': 1,
    'formatters': {
        'simple': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
        # 其他的 formatter
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'simple',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'logging.log',
            'level': 'DEBUG',
            'formatter': 'simple'
        },
        # 其他的 handler
    },
    'loggers': {
        'StreamLogger': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'FileLogger': {
            # 既有 console Handler，还有 file Handler
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
        # 其他的 Logger
    }
}

CELERY_BROKER_URL = "redis://localhost:6379"
CELERY_RESULT_BACKEND = "redis://localhost:6379"

AGENT_SERVER_USER = "tripanels"
AGENT_SERVER_PASSWORD = "jJ$kifvz17g735p7"

# email

# email Settings
SMTP_ENABLED = True
SMTP_HOST = 'smtp.163.com'
SMTP_PORT = 25
SMTP_USER = 'ismewen@163.com'
SMTP_PASS = 'ismewen95'
SMTP_STARTTLS = False
SMTP_TLS = False
TESTING = True

CLUSTER_NOTICE_ADMIN__EMAIL = ["ismewen@163.com"]

##
ELASTIC_APM = dict(SERVICE_NAME='aide_api', SECRET_TOKEN=None, SERVER_URL='http://localhost:8200')

ENVIRONMENT = os.getenv("AGGREGATION", "LOCAL")

# sentry
# SENTRY_DSN = "https://290b234cf226411d8768364b318f65c6@sentry.io/1501311"
SENTRY_DSN = "http://7c0bcbec32e14236b151c3f625142065@sentry.ismewen.com/2"

PRODUCTION = False

if ENVIRONMENT == "TESTING":
    try:
        from .test_settings import *
    except ImportError as e:
        pass

elif ENVIRONMENT == "LOCAL":
    try:
        from .local_settings import *
    except ImportError as e:
        pass

elif ENVIRONMENT == "PRODUCTION":
    try:
        from .production_settings import *
    except ImportError as e:
        pass
