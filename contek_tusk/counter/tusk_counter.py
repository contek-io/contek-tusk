from __future__ import annotations

import atexit
from datetime import timedelta
from threading import RLock, Timer
from typing import Dict, Union, Optional

from contek_tusk.batching_config import BatchingConfig
from contek_tusk.counter.count_buffer import CountBuffer
from contek_tusk.counter.count_column_cache import CountColumnCache
from contek_tusk.metric import Metric
from contek_tusk.metric_client import DEFAULT_CLIENT
from contek_tusk.table import Table


class TuskCounter:
    DEFAULT_COUNT_PERIOD = timedelta(seconds=15)
    DEFAULT_BATCHING_CONFIG = BatchingConfig.default()

    def __init__(self, buffer: CountBuffer, count_period: timedelta) -> None:
        self._buffer = buffer
        self._count_period = count_period
        self._lock = RLock()
        self._timer: Optional[Timer] = None
        atexit.register(self._flush)

    @classmethod
    def counter(
        cls,
        table: Union[Table, str],
        count_column: Optional[str] = None,
        count_period: Union[timedelta, int] = DEFAULT_COUNT_PERIOD,
        batching_config: BatchingConfig = DEFAULT_BATCHING_CONFIG,
        client_name: str = DEFAULT_CLIENT,
    ) -> TuskCounter:
        metric = Metric.metric(table, batching_config, client_name)
        schema_provider = metric.get_schema_provider()
        count_column_cache = CountColumnCache(schema_provider, count_column)
        buffer = CountBuffer(metric, count_column_cache)
        if type(count_period) is int:
            count_period = timedelta(seconds=count_period)
        return cls(buffer, count_period)

    def count(self, tags: Dict[str, str], increment: int = 1) -> None:
        self._buffer.count(tags, increment)
        self._schedule_if_idle()

    def _schedule_if_idle(self) -> None:
        self._lock.acquire()
        try:
            timer = self._timer
            if timer is not None and timer.is_alive():
                return
            self._schedule()
        finally:
            self._lock.release()

    def _flush_and_schedule(self) -> None:
        updated = self._flush()
        if not updated:
            return
        self._schedule()

    def _schedule(self) -> None:
        self._lock.acquire()
        try:
            timer = Timer(
                self._count_period.total_seconds(),
                self._flush_and_schedule,
            )
            timer.daemon = True
            timer.start()
            self._timer = timer
        finally:
            self._lock.release()

    def _flush(self) -> bool:
        return self._buffer.flush()
