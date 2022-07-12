import traceback
from logging import Handler, LogRecord

from contek_tusk import Metric
from contek_tusk.logging.tusk_logging_config import TuskLoggingConfig

ORIGINAL_EXTRA_KEY = '_extra'


class TuskHandler(Handler):

    def __init__(
        self,
        metric: Metric,
        config: TuskLoggingConfig,
        level: int,
    ) -> None:
        super().__init__(level)
        self._metric = metric
        self._config = config

    def emit(self, record: LogRecord) -> None:
        config = self._config
        key_values = {}

        level = config.get_mapper()(record.levelno)
        key_values[config.get_level_column()] = level

        app = config.get_app_name()
        key_values[config.get_app_column()] = app

        logger_column = config.get_logger_column()
        if logger_column is not None:
            key_values[logger_column] = record.filename

        line_column = config.get_line_column()
        if line_column is not None:
            key_values[line_column] = record.lineno

        error_column = config.get_error_column()
        if error_column is not None:
            exc = record.exc_info
            error = exc[0].__name__ if exc else ''
            key_values[error_column] = error

        message_column = config.get_message_column()
        if message_column is not None:
            msg = record.msg
            key_values[message_column] = msg if msg is not None else ''

        stacktrace_column = config.get_stacktrace_column()
        if stacktrace_column is not None:
            stacktrace = ''
            if record.exc_info:
                lines = traceback.format_exception(*record.exc_info)
                stacktrace = ''.join(lines)
            key_values[stacktrace_column] = stacktrace

        context_columns = config.get_context_columns()
        if hasattr(record, ORIGINAL_EXTRA_KEY):
            extra = getattr(record, ORIGINAL_EXTRA_KEY)
            for (key, value) in extra.items():
                column = context_columns.get(key, key)
                key_values[column] = value

        self._metric.write(key_values)
