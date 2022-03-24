from datetime import timedelta
from typing import Dict, Optional, Callable

from contek_tusk.app_name_resolver import APP_NAME_KEY
from contek_tusk.batching_config import BatchingConfig
from contek_tusk.logging.level_mapper import LevelMapper
from contek_tusk.table import Table


class TuskLoggingConfig:
    DEFAULT_BATCHING_CONFIG = BatchingConfig(timedelta(seconds=10), 50000)
    DEFAULT_APP_COLUMN = APP_NAME_KEY
    DEFAULT_LEVEL_COLUMN = 'level'
    DEFAULT_LOGGER_COLUMN = 'logger'
    DEFAULT_LINE_COLUMN = 'line'
    DEFAULT_ERROR_COLUMN = 'error'
    DEFAULT_MESSAGE_COLUMN = 'message'
    DEFAULT_STACKTRACE_COLUMN = 'stacktrace'

    def __init__(
        self,
        app_name: str,
        table: Table,
        batching_config: BatchingConfig = DEFAULT_BATCHING_CONFIG,
        app_column: str = DEFAULT_APP_COLUMN,
        level_column: str = DEFAULT_LEVEL_COLUMN,
        logger_column: Optional[str] = DEFAULT_LOGGER_COLUMN,
        line_column: Optional[str] = DEFAULT_LINE_COLUMN,
        error_column: Optional[str] = DEFAULT_ERROR_COLUMN,
        message_column: Optional[str] = DEFAULT_MESSAGE_COLUMN,
        stacktrace_column: Optional[str] = DEFAULT_STACKTRACE_COLUMN,
        context_columns: Optional[Dict[str, str]] = None,
        mapper: Optional[Callable[[int], int]] = None,
    ) -> None:
        self._app_name = app_name
        self._table = table
        self._batching_config = batching_config
        self._app_column = app_column
        self._level_column = level_column
        self._logger_column = logger_column
        self._line_column = line_column
        self._error_column = error_column
        self._message_column = message_column
        self._stacktrace_column = stacktrace_column
        self._context_columns = {} if context_columns is None else context_columns
        self._mapper = LevelMapper() if mapper is None else mapper

    def get_app_name(self) -> str:
        return self._app_name

    def get_table(self) -> Table:
        return self._table

    def get_batching_config(self) -> BatchingConfig:
        return self._batching_config

    def get_app_column(self) -> str:
        return self._app_column

    def get_level_column(self) -> str:
        return self._level_column

    def get_logger_column(self) -> Optional[str]:
        return self._logger_column

    def get_line_column(self) -> Optional[str]:
        return self._line_column

    def get_error_column(self) -> Optional[str]:
        return self._error_column

    def get_message_column(self) -> Optional[str]:
        return self._message_column

    def get_stacktrace_column(self) -> Optional[str]:
        return self._stacktrace_column

    def get_context_columns(self) -> Dict[str, str]:
        return self._context_columns

    def get_mapper(self) -> Callable[[int], int]:
        return self._mapper
