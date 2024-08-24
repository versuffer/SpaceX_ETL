"""logger settings"""

import logging
from logging.config import dictConfig

from app.settings.config import app_settings

logger_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            '()': 'uvicorn.logging.DefaultFormatter',
            'fmt': '%(levelprefix)s[%(asctime)s - %(filename)s:%(lineno)s - %(funcName)s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'for_file': {
            '()': 'uvicorn.logging.DefaultFormatter',
            'fmt': '%(levelname)s: [%(asctime)s - %(filename)s:%(lineno)s - %(funcName)s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': app_settings.LOG_LEVEL,
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
        },
        'file': {
            'level': app_settings.LOG_LEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'for_file',
            'filename': 'log_file.log',
            'maxBytes': 500000,
            'backupCount': 10,
        },
    },
    'loggers': {
        'root': {
            'level': app_settings.LOG_LEVEL,
            'handlers': ['console', 'file'],
        },
    },
}

# Initiate logger config
dictConfig(logger_config)
logger = logging.getLogger('root')
