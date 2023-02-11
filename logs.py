import inspect
import logging
from typing import Callable, Optional, Self


class Log:
    def __init__(
        self,
        logger: logging.Logger,
        name: str = "",
        variables: list[str] | None = None,
        log_format: str | None = None,
        when_success: bool = True,
        when_fail: bool = True,
        _wrapped: Optional[Callable] = None,
    ):
        self.logger = logger
        self.variables = variables
        self._log_format = log_format
        self.name = name
        self.when_success = when_success
        self.when_fail = when_fail
        self._default_func = None
        self._wrapped = _wrapped

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        previous = inspect.stack()[1]
        local_vars = previous[0].f_locals
        pathname = previous[1]

        if self.variables:
            log_vars = {var: local_vars.get(var) for var in self.variables}
        else:
            log_vars = local_vars.copy()

        self.setup_makeLogRecord(pathname=pathname)
        if exc_type is None:
            if self.when_success:
                self.logger.info(self.get_log_message(log_vars))
        else:
            if self.when_fail:
                # エラーが起きた場合
                self.logger.error(self.get_log_message(log_vars))
        self.reset_makeLogRecord()

    def get_log_message(self, log_vars: dict):
        header = f"[{self.name}] " if self.name else ""
        if self._log_format:
            return header + self._log_format.format(**log_vars)

        return header + ", ".join([f"{k}={v}" for k, v in log_vars.items()])

    def setup_makeLogRecord(self, pathname: str):
        """
        LogRecord の pathname がこのファイルになってしまうため書き換える
        """
        self._default_func = self.logger.makeRecord

        def _makeRecord(*args, **kwargs):
            rv = self._default_func(*args, **kwargs)
            rv.pathname = pathname
            return rv

        self.logger.makeRecord = _makeRecord

    def reset_makeLogRecord(self):
        self.logger.makeRecord = self._default_func
