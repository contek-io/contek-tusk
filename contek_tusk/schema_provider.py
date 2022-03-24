from threading import Lock
from typing import Optional

import contek_tusk as tusk
from contek_tusk.schema import Schema
from contek_tusk.table import Table


class SchemaProvider:

    def __init__(self, table: Table, client_name: str) -> None:
        self._table = table
        self._client_name = client_name
        self._cache: Optional[Schema] = None
        self._lock: Lock = Lock()

    def get_schema(self) -> Optional[Schema]:
        self._lock.acquire()

        try:
            if self._cache is not None:
                return self._cache

            self._cache = self._fetch()
            return self._cache
        finally:
            self._lock.release()

    def _fetch(self) -> Optional[Schema]:
        client = tusk.get_client(self._client_name)
        if client is None:
            return None

        return client.describe(self._table)
