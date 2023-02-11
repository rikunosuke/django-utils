import logging


class DBHandler(logging.Handler):
    """
    LOGGING = {
        'handlers': {
            'db_log': {
                'formatter': 'simple',
                'level': 'INFO',
                'class': 'django_utils.db_log.handlers.DBHandler',
            },
        },
        'loggers': {
            'db_log': {
                'handlers': ['db_log',],
                'level': 'INFO',
                'propagate': True,
            },
        }
    }
    ...
    """

    def emit(self, record: logging.LogRecord):
        # import DBLog inside a method to avoid raising AppRegistryNotReady Error
        from django_utils.db_log.models import DBLog

        DBLog.objects.create(
            logname=record.name,
            levelname=record.levelname,
            category=record.pathname,
            message=record.getMessage(),
        )
