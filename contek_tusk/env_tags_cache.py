from threading import Lock
from typing import Optional, Dict

from contek_tusk.env_utils import get_env_tag
from contek_tusk.schema import Schema
from contek_tusk.schema_provider import SchemaProvider


class EnvTagsCache:

    def __init__(self, schema_provider: SchemaProvider) -> None:
        self._schema_provider = schema_provider
        self._cache: Optional[Dict[str, str]] = None
        self._lock: Lock = Lock()

    def get(self) -> Optional[Dict[str, str]]:
        self._lock.acquire()

        try:
            if self._cache is not None:
                return self._cache

            schema = self._schema_provider.get_schema()
            if schema is None:
                return None

            self._cache = EnvTagsCache._get_tags_from_env(schema)
            return self._cache
        finally:
            self._lock.release()

    @staticmethod
    def _get_tags_from_env(schema: Schema) -> Dict[str, str]:
        result: Dict[str, str] = {}
        for (column_name, column_type) in schema.get_columns().items():
            if column_type != 'String':
                continue
            env_value = get_env_tag(column_name)
            if env_value is not None:
                result[column_name] = env_value
        return result
