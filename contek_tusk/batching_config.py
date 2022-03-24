from __future__ import annotations

from datetime import timedelta


class BatchingConfig:

    def __init__(self, duration: timedelta, max_size: int) -> None:
        self._duration = duration
        self._max_size = max_size

    @classmethod
    def disabled(cls) -> BatchingConfig:
        return cls(timedelta(seconds=0), 0)

    @classmethod
    def default(cls) -> BatchingConfig:
        return cls(timedelta(seconds=60), 10000)

    @classmethod
    def unlimited(cls, duration: timedelta) -> BatchingConfig:
        return cls(duration, 0)

    def is_immediate(self) -> bool:
        return self.get_period() == 0

    def get_period(self) -> timedelta:
        return self._duration

    def get_max_size(self) -> int:
        return self._max_size
