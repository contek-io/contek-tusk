from __future__ import annotations

import logging
from datetime import datetime, timedelta
from threading import RLock, Timer
from typing import Dict, Union

from contek_tusk.heartbeat.tuck_heartbeat_config import TuskHeartbeatConfig
from contek_tusk.metric import Metric
from contek_tusk.metric_client import DEFAULT_CLIENT

logger = logging.getLogger(__name__)


class TuskHeartbeatClient:
    _MAIN_TASK = 'main'

    def __init__(self, metric: Metric, config: TuskHeartbeatConfig) -> None:
        self._metric = metric
        self._config = config
        self._started: bool = False
        self._counts: Dict[str, int] = {}
        self._lock = RLock()

    @classmethod
    def create(
        cls,
        config: TuskHeartbeatConfig,
        client_name: str = DEFAULT_CLIENT,
    ) -> TuskHeartbeatClient:
        metric = Metric.metric(
            config.get_table(),
            config.get_batching_config(),
            client_name,
        )
        return cls(metric, config)

    def start(self):
        self._lock.acquire()
        try:
            if self._started:
                return
            self._send_main_beat_and_reschedule()
            self._started = True
        finally:
            self._lock.release()

    def beat(self, task: str, heartbeat_period: Union[timedelta, int]):
        if task == TuskHeartbeatClient._MAIN_TASK:
            raise ValueError(task)
        if type(heartbeat_period) is int:
            heartbeat_period = timedelta(seconds=heartbeat_period)
        self._send_beat(task, heartbeat_period)

    def _send_main_beat_and_reschedule(self):
        self._send_beat(
            TuskHeartbeatClient._MAIN_TASK,
            self._config.get_heartbeat_period(),
        )
        self._reschedule()

    def _reschedule(self):
        timer = Timer(
            self._config.get_heartbeat_period().total_seconds(),
            self._send_main_beat_and_reschedule,
        )
        timer.daemon = True
        timer.start()

    def _send_beat(self, task: str, heartbeat_period: timedelta):
        config = self._config

        app_name = config.get_app_name()
        now = datetime.utcnow()
        timeout_period = config.get_timeout()
        batching_period = config.get_batching_config().get_period()
        expiry = now + heartbeat_period + timeout_period + batching_period

        key_values: Dict[str, any] = {
            config.get_app_column(): app_name,
            config.get_task_column(): task,
            config.get_sequence_column(): self._next_sequence(task),
            config.get_expiry_column(): expiry,
        }
        self._metric.write(key_values)

    def _next_sequence(self, task: str) -> int:
        self._lock.acquire()
        try:
            count = self._counts.get(task)
            if count is None:
                count = 0
            self._counts[task] = count + 1
            return count
        finally:
            self._lock.release()
