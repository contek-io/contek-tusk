from typing import Optional, Dict

from contek_tusk import app_name_resolver
from contek_tusk.metric import Metric
from contek_tusk.metric_client import MetricClient, DEFAULT_CLIENT

_clients: Dict[str, MetricClient] = {}


def init(
    host: str,
    user: str,
    password: str,
    client_name: str = DEFAULT_CLIENT,
    **kwargs: object,
) -> None:
    client = MetricClient.create(host, user, password, **kwargs)
    set_client(client, client_name)


def get_client(client_name: str = DEFAULT_CLIENT) -> Optional[MetricClient]:
    global _clients
    return _clients.get(client_name)


def set_client(
    client: MetricClient,
    client_name: str = DEFAULT_CLIENT,
) -> None:
    global _clients
    _clients[client_name] = client


metric = Metric.metric
set_app_name = app_name_resolver.set_app_name
