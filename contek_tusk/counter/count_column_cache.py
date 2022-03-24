from threading import Lock
from typing import Optional

from contek_tusk.schema import Schema
from contek_tusk.schema_provider import SchemaProvider


class CountColumnCache:

    def __init__(
        self,
        schema_provider: SchemaProvider,
        count_column: Optional[str],
    ) -> None:
        self._schema_provider = schema_provider
        self._cache: Optional[str] = count_column
        self._lock: Lock = Lock()

    def get(self) -> Optional[str]:
        self._lock.acquire()

        try:
            if self._cache is not None:
                return self._cache

            schema = self._schema_provider.get_schema()
            if schema is None:
                return None

            self._cache = CountColumnCache._get_first_int_column(schema)
            return self._cache
        finally:
            self._lock.release()

    @staticmethod
    def _get_first_int_column(schema: Schema) -> Optional[str]:
        for (column_name, column_type) in schema.get_columns().items():
            if column_type.startswith('UInt') or column_type.startswith('Int'):
                return column_name
        return None
