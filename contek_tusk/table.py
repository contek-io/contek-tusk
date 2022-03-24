from __future__ import annotations

from typing import Optional, Dict

DATABASE = 'database'
TABLE = 'table'


class Table:

    def __init__(
        self,
        database: Optional[str],
        table_name: str,
        time_column: Optional[str] = None,
    ) -> None:
        self._database = database
        self._table_name = table_name
        self._time_column = time_column

    @classmethod
    def from_str(cls, str_value: str) -> Table:
        split = str_value.split('.')
        if len(split) == 2:
            return cls(split[0], split[1])
        if len(split) == 1:
            return cls(None, split[0])
        raise ValueError(str_value)

    @classmethod
    def from_dict(cls, key_values: Dict[str, str]) -> Table:
        database = key_values.get(DATABASE)
        table = key_values.get(TABLE)
        if table is None:
            raise ValueError('Table not specified')
        return cls(database, table)

    def get_full_name(self) -> str:
        if self._database is None:
            return self._table_name

        return f"{self._database}.{self._table_name}"

    def get_time_column(self) -> Optional[str]:
        return self._time_column
