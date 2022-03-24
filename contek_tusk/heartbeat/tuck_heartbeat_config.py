from datetime import timedelta

from contek_tusk.app_name_resolver import APP_NAME_KEY
from contek_tusk.batching_config import BatchingConfig
from contek_tusk.table import Table


class TuskHeartbeatConfig:
    DEFAULT_BATCHING_CONFIG = BatchingConfig.unlimited(timedelta(seconds=5))
    DEFAULT_APP_COLUMN = APP_NAME_KEY
    DEFAULT_TASK_COLUMN = 'task'
    DEFAULT_SEQUENCE_COLUMN = 'sequence'
    DEFAULT_EXPIRY_COLUMN = 'expiry'

    def __init__(
        self,
        app_name: str,
        table: Table,
        heartbeat_period: timedelta,
        timeout: timedelta,
        batching_config: BatchingConfig = DEFAULT_BATCHING_CONFIG,
        app_column: str = DEFAULT_APP_COLUMN,
        task_column: str = DEFAULT_TASK_COLUMN,
        sequence_column: str = DEFAULT_SEQUENCE_COLUMN,
        expiry_column: str = DEFAULT_EXPIRY_COLUMN,
    ) -> None:
        self._app_name = app_name
        self._table = table
        self._heartbeat_period = heartbeat_period
        self._timeout = timeout
        self._batching_config = batching_config
        self._app_column = app_column
        self._task_column = task_column
        self._sequence_column = sequence_column
        self._expiry_column = expiry_column

    def get_app_name(self) -> str:
        return self._app_name

    def get_table(self) -> Table:
        return self._table

    def get_heartbeat_period(self) -> timedelta:
        return self._heartbeat_period

    def get_timeout(self) -> timedelta:
        return self._timeout

    def get_batching_config(self) -> BatchingConfig:
        return self._batching_config

    def get_app_column(self) -> str:
        return self._app_column

    def get_task_column(self) -> str:
        return self._task_column

    def get_sequence_column(self) -> str:
        return self._sequence_column

    def get_expiry_column(self) -> str:
        return self._expiry_column
