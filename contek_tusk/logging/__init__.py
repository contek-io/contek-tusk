import logging
from logging import INFO
from typing import Union, Dict, Optional

import contek_tusk
from contek_tusk.app_name_resolver import get_app_name
from contek_tusk.logging.tusk_handler import TuskHandler, ORIGINAL_EXTRA_KEY
from contek_tusk.logging.tusk_logging_config import TuskLoggingConfig
from contek_tusk.metric_client import DEFAULT_CLIENT
from contek_tusk.table import Table

_handlers: Dict[str, TuskHandler] = {}


def init(
    table: Union[Table, str],
    app_name: Optional[str] = None,
    client_name: str = DEFAULT_CLIENT,
    level: int = INFO,
) -> None:
    if type(table) is str:
        table = Table.from_str(table)
    if app_name is None:
        app_name = get_app_name()
    init_for_config(
        TuskLoggingConfig(
            app_name=app_name,
            table=table,
        ),
        client_name,
        level,
    )


def init_for_config(
    config: TuskLoggingConfig,
    client_name: str = DEFAULT_CLIENT,
    level: int = INFO,
) -> None:
    metric = contek_tusk.metric(
        config.get_table(),
        config.get_batching_config(),
        client_name,
    )
    _patch_make_record_extra()
    handler = TuskHandler(metric, config, level)
    logger = logging.getLogger()
    logger.addHandler(handler)
    global _handlers
    _handlers[client_name] = handler


def _patch_make_record_extra():
    make_record = logging.Logger.makeRecord
    var_names = make_record.__code__.co_varnames

    def make_record_with_extra(*args, **kwargs):
        kwargs.update(zip(var_names, args))
        record = make_record(**kwargs)
        extra = kwargs.get('extra')
        if extra is not None:
            setattr(record, ORIGINAL_EXTRA_KEY, extra)
        return record

    logging.Logger.makeRecord = make_record_with_extra
