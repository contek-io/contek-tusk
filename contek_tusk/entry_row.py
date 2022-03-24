from typing import Dict, Optional


class EntryRow:

    def __init__(self, key_values: Dict[str, any]) -> None:
        self._key_values = key_values

    def get_key_values(self) -> Dict[str, any]:
        return self._key_values

    def get_value(self, key: str) -> Optional[any]:
        return self._key_values[key]
