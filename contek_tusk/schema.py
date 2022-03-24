from typing import Dict, Optional


class Schema:

    def __init__(self, columns: Dict[str, str]) -> None:
        self._columns = columns

    def get_column_type(self, column_name: str) -> Optional[str]:
        return self._columns.get(column_name)

    def get_columns(self) -> Dict[str, str]:
        return self._columns
