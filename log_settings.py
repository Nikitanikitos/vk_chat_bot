# -*- coding: utf-8 -*-
import logging
from logging.config import dictConfigClass

log_config = {
    "version": 1,
    "formatters": {
        "file_formatter": {
            "format": "{asctime} - {levelname}:\n\t{message}",
            "datefmt": "%d-%m-%Y %H:%M:%S",
            "style": "{"
        },
    },
    "handlers": {
        "file_handler": {
            "class": "logging.FileHandler",
            "formatter": "file_formatter",
            "filename": "log_bot.log",
            "encoding": "UTF-8",
            "delay": "True"
        },
        "stream_handler": {
            "class": "logging.StreamHandler"
        }
    },
    "loggers": {
        "file_stream_handler": {
            "handlers": ["file_handler", "stream_handler"],
            "level": "INFO"
        },
        "file_handler": {
            "handlers": ["file_handler"],
            "level": "INFO"
        },
        "stream_handler": {
            "handlers": ["stream_handler"],
            "level": "INFO"
        }
    }
}


def dictConfig(config):
    dictConfigClass(config).configure()

dictConfig(log_config)

file_stream_handler = logging.getLogger("file_stream_handler")
file_handler = logging.getLogger("file_handler")
stream_handler = logging.getLogger("stream_handler")