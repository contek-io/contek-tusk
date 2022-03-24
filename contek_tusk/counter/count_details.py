from typing import Dict


class CountDetails:

    def __init__(self, tags: Dict[str, str]) -> None:
        self._tags = tags
        self._count = 0

    def get_tags(self) -> Dict[str, str]:
        return self._tags

    def increment_unsafe(self, n: int) -> None:
        self._count = self._count + n

    def get_count_unsafe(self) -> int:
        return self._count
