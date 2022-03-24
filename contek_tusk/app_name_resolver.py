from typing import Optional

from contek_tusk.env_utils import get_env_tag

APP_NAME_KEY = 'app'

_app_name: Optional[str] = None


def set_app_name(app_name: str) -> None:
    global _app_name
    _app_name = app_name


def get_app_name() -> str:
    global _app_name
    if _app_name is None:
        _app_name = get_env_tag(APP_NAME_KEY)
        if _app_name is None:
            raise ValueError('Could not read app name from env')
    return _app_name
