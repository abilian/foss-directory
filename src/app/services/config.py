from typing import Any

from flask import current_app


class Config:
    _config: dict[str, Any]

    def __init__(self):
        self._config = current_app.config

    def __getitem__(self, key):
        return self._config[key]
