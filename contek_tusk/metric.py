from __future__ import annotations

import atexit
from datetime import datetime
from threading import Timer, RLock
from typing import Optional, Union, Dict

import contek_tusk as tusk
from contek_tusk.batching_config import BatchingConfig
from contek_tusk.entry_input_normalizer import EntryInputNormalizer
from contek_tusk.entry_row import EntryRow
from contek_tusk.env_tags_cache import EnvTagsCache
from contek_tusk.metric_batch import MetricBatch
from contek_tusk.metric_client import DEFAULT_CLIENT
from contek_tusk.metric_formatter import MetricFormatter
from contek_tusk.schema_provider import SchemaProvider
from contek_tusk.table import Table
from contek_tusk.time_column_cache import TimeColumnCache


class Metric:
    DEFAULT_BATCHING_CONFIG = BatchingConfig.default()

    def __init__(
        self,
        table: Table,
        time_column_cache: TimeColumnCache,
        env_tags_cache: EnvTagsCache,
        entry_input_normalizer: EntryInputNormalizer,
        metric_formatter: MetricFormatter,
        schema_provider: SchemaProvider,
        batching_config: BatchingConfig,
        client_name: str,
    ) -> None:
        self._table = table
        self._time_column_cache = time_column_cache
        self._env_tags_cache = env_tags_cache
        self._entry_input_normalizer = entry_input_normalizer
        self._metric_formatter = metric_formatter
        self._schema_provider = schema_provider
        self._batch = MetricBatch(table, batching_config)
        self._client_name = client_name
        self._lock: RLock = RLock()
        self._timer: Optional[Timer] = None
        atexit.register(self._flush)

    @classmethod
    def metric(
        cls,
        table: Union[Table, str],
        batching_config: BatchingConfig = DEFAULT_BATCHING_CONFIG,
        client_name: str = DEFAULT_CLIENT,
    ) -> Metric:
        if type(table) is str:
            table = Table.from_str(table)
        schema_provider = SchemaProvider(table, client_name)
        return cls(
            table,
            TimeColumnCache(schema_provider, table.get_time_column()),
            EnvTagsCache(schema_provider),
            EntryInputNormalizer(schema_provider),
            MetricFormatter(table, schema_provider),
            schema_provider,
            batching_config,
            client_name,
        )

    def write(self, key_values: Dict[str, any]) -> None:
        key_values = key_values.copy() # Don't modify input inplace
        time_column = self._time_column_cache.get()
        if time_column is not None:
            now = datetime.utcnow()
            key_values[time_column] = now

        env_tags = self._env_tags_cache.get()
        if env_tags is not None:
            for (key, value) in env_tags.items():
                env_tags.setdefault(key, value)

        entry_row = self._entry_input_normalizer.normalize(key_values)
        if entry_row is None:
            return

        self._accept(entry_row)

    def get_schema_provider(self) -> SchemaProvider:
        return self._schema_provider

    def _accept(self, entry_row: EntryRow) -> None:
        self._batch.add(entry_row)
        self._schedule_if_idle()

    def _schedule_if_idle(self) -> None:
        if self._batch.is_immediate():
            self._flush()
            return
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
                self._batch.get_period().total_seconds(),
                self._flush_and_schedule,
            )
            timer.daemon = True
            timer.start()
            self._timer = timer
        finally:
            self._lock.release()

    def _flush(self) -> bool:
        client = tusk.get_client(self._client_name)
        if client is None:
            return False

        data = self._batch.export(self._metric_formatter)
        if data is None:
            return False

        client.write(data)
        return True
