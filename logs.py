import functools
import inspect
import logging
from typing import Self


class Log:
    def __init__(
        self,
        logger: logging.Logger,
        name: str = "",
        variables: list[str] | None = None,
        log_format: str | None = None,
        when_success: bool = True,
        when_fail: bool = True,
    ):
        self.logger = logger
        self.variables = variables
        self._log_format = log_format
        self.name = name
        self.when_success = when_success
        self.when_fail = when_fail

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        local_vars = inspect.stack()[1][0].f_locals
        if self.variables:
            log_vars = {var: local_vars.get(var) for var in self.variables}
        else:
            log_vars = local_vars.copy()

        if exc_type is None:
            if self.when_success:
                self.logger.info(self.get_log_message(log_vars))
        else:
            if self.when_fail:
                # エラーが起きた場合
                self.logger.error(self.get_log_message(log_vars))

    @classmethod
    def as_deco(cls, **kwargs):
        def wrapper(function):
            @functools.wraps(function)
            def wrapped(*args, **_kwargs):
                with Log(**kwargs):
                    return function(*args, **_kwargs)

            return wrapped

        return wrapper

    def get_log_message(self, log_vars: dict):
        header = f"[{self.name}] " if self.name else ""
        if self._log_format:
            return header + self._log_format.format(**log_vars)

        return header + ", ".join([f"{k}={v}" for k, v in log_vars.items()])
