from datetime import timedelta
from typing import Union, Dict, Optional

from contek_tusk.app_name_resolver import get_app_name
from contek_tusk.heartbeat.tuck_heartbeat_client import TuskHeartbeatClient
from contek_tusk.heartbeat.tuck_heartbeat_config import TuskHeartbeatConfig
from contek_tusk.metric_client import DEFAULT_CLIENT
from contek_tusk.table import Table

DEFAULT_HEARTBEAT_PERIOD = timedelta(seconds=30)
DEFAULT_TIMEOUT = timedelta(seconds=30)

_heartbeat_clients: Dict[str, TuskHeartbeatClient] = {}


def init(
    table: Union[Table, str],
    app_name: Optional[str] = None,
    heartbeat_period: Union[timedelta, int] = DEFAULT_HEARTBEAT_PERIOD,
    timeout: Union[timedelta, int] = DEFAULT_TIMEOUT,
    client_name: str = DEFAULT_CLIENT,
) -> None:
    if type(table) is str:
        table = Table.from_str(table)
    if type(heartbeat_period) is int:
        heartbeat_period = timedelta(seconds=heartbeat_period)
    if type(timeout) is int:
        timeout = timedelta(seconds=timeout)
    if app_name is None:
        app_name = get_app_name()
    init_for_config(
        TuskHeartbeatConfig(
            app_name=app_name,
            table=table,
            heartbeat_period=heartbeat_period,
            timeout=timeout,
        ),
        client_name,
    )


def init_for_config(
    config: TuskHeartbeatConfig,
    client_name: str = DEFAULT_CLIENT,
) -> None:
    client = TuskHeartbeatClient.create(config, client_name)
    client.start()
    global _heartbeat_clients
    _heartbeat_clients[client_name] = client


def beat(
    task: str,
    heartbeat_period: Union[timedelta, int],
    client_name: str = DEFAULT_CLIENT,
) -> None:
    client = _get_client(client_name)
    if client is not None:
        client.beat(task, heartbeat_period)


def _get_client(client_name: str) -> Optional[TuskHeartbeatClient]:
    global _heartbeat_clients
    client = _heartbeat_clients.get(client_name)
    return client
