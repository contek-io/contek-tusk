import os
from typing import Optional


def get_env_tag(column_name: str) -> Optional[str]:
    env_value = os.getenv(column_name)
    if env_value is None:
        env_value = os.getenv(column_name.upper())
    if env_value is None:
        env_value = os.getenv(column_name.lower())
    return env_value
