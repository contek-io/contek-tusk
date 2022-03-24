from threading import Lock
from typing import Optional

from contek_tusk.schema import Schema
from contek_tusk.schema_provider import SchemaProvider


class TimeColumnCache:

    def __init__(
        self,
        schema_provider: SchemaProvider,
        time_column: Optional[str],
    ) -> None:
        self._schema_provider = schema_provider
        self._cache: Optional[str] = time_column
        self._lock: Lock = Lock()

    def get(self) -> Optional[str]:
        self._lock.acquire()

        try:
            if self._cache is not None:
                return self._cache

            schema = self._schema_provider.get_schema()
            if schema is None:
                return None

            self._cache = TimeColumnCache._get_first_date_time_column(schema)
            return self._cache
        finally:
            self._lock.release()

    @staticmethod
    def _get_first_date_time_column(schema: Schema) -> Optional[str]:
        for (column_name, column_type) in schema.get_columns().items():
            if column_type.startswith('DateTime'):
                return column_name
        return None
