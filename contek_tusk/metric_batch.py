import logging
from datetime import timedelta
from threading import Lock
from typing import Optional, List

from contek_tusk.batching_config import BatchingConfig
from contek_tusk.entry_row import EntryRow
from contek_tusk.metric_data import MetricData
from contek_tusk.metric_formatter import MetricFormatter
from contek_tusk.table import Table

logger = logging.getLogger(__name__)


class MetricBatch:

    def __init__(
        self,
        table: Table,
        batching_config: BatchingConfig,
    ) -> None:
        self._table = table
        self._batching_config = batching_config
        self._rows: List[EntryRow] = []
        self._drop_count = 0
        self._lock = Lock()

    def is_immediate(self) -> bool:
        return self._batching_config.is_immediate()

    def get_period(self) -> timedelta:
        return self._batching_config.get_period()

    def add(self, entry_row: EntryRow) -> None:
        max_size = self._batching_config.get_max_size()
        self._lock.acquire()
        try:
            if 0 < max_size <= len(self._rows):
                self._drop_count = self._drop_count + 1
            else:
                self._rows.append(entry_row)
        finally:
            self._lock.release()

    def export(self, formatter: MetricFormatter) -> Optional[MetricData]:
        self._lock.acquire()
        try:
            data = formatter.format(self._rows)
            self._rows.clear()
            if self._drop_count > 0:
                logger.error(
                    f"Dropped {self._drop_count} rows inserting to table \"{self._table.get_full_name()}\"",
                )
                self._drop_count = 0
            return data
        finally:
            self._lock.release()
