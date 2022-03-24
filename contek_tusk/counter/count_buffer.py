from threading import Lock
from typing import Dict

from contek_tusk.counter.count_column_cache import CountColumnCache
from contek_tusk.counter.count_details import CountDetails
from contek_tusk.metric import Metric


class CountBuffer:

    def __init__(
        self,
        metric: Metric,
        count_column_cache: CountColumnCache,
    ) -> None:
        self._metric = metric
        self._count_column_cache = count_column_cache
        self._counts: Dict[str, CountDetails] = {}
        self._lock = Lock()

    def count(self, tags: Dict[str, str], n: int = 1) -> None:
        key = CountBuffer._to_tags_key(tags)
        self._lock.acquire()
        try:
            count = self._counts.get(key)
            if count is None:
                count = CountDetails(tags)
                self._counts[key] = count
            count.increment_unsafe(n)
        finally:
            self._lock.release()

    def flush(self) -> bool:
        count_column = self._count_column_cache.get()
        if count_column is None:
            return False

        self._lock.acquire()
        try:
            while len(self._counts) > 0:
                (_, count) = self._counts.popitem()
                key_values: Dict[str, any] = count.get_tags()
                key_values[count_column] = count.get_count_unsafe()
                self._metric.write(key_values)
        finally:
            self._lock.release()

    @staticmethod
    def _to_tags_key(tags: Dict[str, str]) -> str:
        return '&'.join(["{}={}".format(k, v) for (k, v) in tags.items()])
