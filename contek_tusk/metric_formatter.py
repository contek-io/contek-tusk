from typing import List, Optional

from pandas import DataFrame

from contek_tusk.entry_row import EntryRow
from contek_tusk.metric_data import MetricData
from contek_tusk.schema_provider import SchemaProvider
from contek_tusk.table import Table


class MetricFormatter:

    def __init__(
        self,
        table: Table,
        schema_provider: SchemaProvider,
    ) -> None:
        self._table = table
        self._schema_provider = schema_provider

    def format(self, rows: List[EntryRow]) -> Optional[MetricData]:
        schema = self._schema_provider.get_schema()
        if schema is None:
            return None

        if len(rows) == 0:
            return None

        records = list(map(lambda r: r.get_key_values(), rows))
        df = DataFrame(records, dtype=object)
        return MetricData(self._table, df)
