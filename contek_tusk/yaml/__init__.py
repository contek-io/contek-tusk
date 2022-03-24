import os
from typing import Dict

import yaml

import contek_tusk as tusk
import contek_tusk.heartbeat as tusk_heartbeat
import contek_tusk.logging as tusk_logging
from contek_tusk.app_name_resolver import set_app_name
from contek_tusk.table import Table

APP = 'app'
HEARTBEAT = 'heartbeat'
LOGGING = 'logging'


def for_yaml_file(file: str) -> None:
    with open(os.path.expanduser(file), 'r') as file:
        key_values = yaml.load(file, Loader=yaml.FullLoader)
    for_dict(key_values)


def for_dict(key_values: Dict[str, any]) -> None:
    app = key_values.get(APP)
    if type(app) is str:
        set_app_name(app)

    tusk.init(**key_values)

    heartbeat = key_values.get(HEARTBEAT)
    if type(heartbeat) is Dict:
        tusk_heartbeat.init(Table.from_dict(heartbeat))

    logging = key_values.get(LOGGING)
    if type(logging) is Dict:
        tusk_logging.init(Table.from_dict(logging))
