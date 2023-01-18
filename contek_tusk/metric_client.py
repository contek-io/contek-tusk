from __future__ import annotations

import logging
import multiprocessing
from typing import Optional, Dict

from clickhouse_driver import Client
from clickhouse_driver.errors import Error

from contek_tusk.metric_data import MetricData
from contek_tusk.schema import Schema
from contek_tusk.table import Table

DEFAULT_CLIENT = 'default'
logger = logging.getLogger(__name__)


class MetricClient:

    def __init__(self, client: Client):
        self._client = client
        self._lock = multiprocessing.Lock()

    @classmethod
    def create(
        cls,
        host: str,
        user: str,
        password: str,
        **kwargs,
    ) -> MetricClient:
        client = Client(
            host=host,
            user=user,
            password=password,
            settings={"use_numpy": True},
            **kwargs,
        )
        return cls(client)

    def write(self, data: MetricData) -> None:
        full_table_name = data.get_table().get_full_name()
        query = f"INSERT INTO {full_table_name} VALUES"

        df = data.get_data_frame()
        rows = df.shape[0]
        if rows < 1:
            return

        self._lock.acquire()
        try:
            self._client.insert_dataframe(query, df)
        except Error:
            logger.exception(
                f"Failed to flush metric data into table \"{data.get_table().get_full_name()}\"."
            )
        finally:
            self._lock.release()

    def describe(self, table: Table) -> Optional[Schema]:
        full_table_name = table.get_full_name()
        query = f"DESCRIBE TABLE {full_table_name}"

        self._lock.acquire()
        df = None
        try:
            df = self._client.query_dataframe(query)
        except Error:
            logger.exception(
                f"Failed to describe table \"{table.get_full_name()}\".")
        finally:
            self._lock.release()

        if df is None:
            return

        result: Dict[str, str] = {}
        for (index, row) in df.iterrows():
            column_name = row.get('name')
            column_type = row.get('type')
            if column_type.endswith(')'):
                bracket_start = column_type.index('(')
                type_or_modifier = column_type[0:bracket_start]
                if type_or_modifier == 'LowCardinality' or type_or_modifier == 'Nullable':
                    column_type = column_type[bracket_start + 1:-1]
                else:
                    column_type = type_or_modifier

            result[column_name] = column_type
        return Schema(result)
