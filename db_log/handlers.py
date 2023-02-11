import logging

from django.views.debug import ExceptionReporter

from django_utils.db_log.models import DBLog


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
                'handlers': [
                    'db_log',
                ],
                'level': 'INFO',
                'propagate': True,
            },
        }
    }
    ...
    """

    def __init__(self, include_traceback=True):
        super().__init__()
        self.include_traceback = include_traceback

    def emit(self, record):
        """
        例:
        logger.info('.....', extra={
          'request': request, 'category': 'hoge'})
        """

        request = None
        request_repr = "unavailable"

        if hasattr(record, "request"):
            try:
                request = record.request
                data = {
                    "META": request.META,
                    "POST": request.POST,
                    "GET": request.GET,
                }
                request_repr = str(data)
            except Exception:  # NOQA
                pass

        traceback = None
        if self.include_traceback and record.exc_info:
            exc_info = record.exc_info
            reporter = ExceptionReporter(request, is_email=False, *exc_info)
            traceback = reporter.get_traceback_text()

        DBLog.objects.create(
            levelname=record.levelname,
            category=getattr(record, "category", record.name),
            message=record.getMessage(),
            request=request_repr,
            traceback=traceback,
        )
