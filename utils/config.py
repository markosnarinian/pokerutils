"""Persisting user preferences, like the selected theme, to a JSON config file."""

from __future__ import annotations

import json

from platformdirs import user_config_path

CONFIG_PATH = user_config_path("pokertools", appauthor=False) / "config.json"


def load_theme() -> str | None:
    """Return the previously saved theme name, or None if there isn't one."""
    try:
        data = json.loads(CONFIG_PATH.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    theme = data.get("theme")
    return theme if isinstance(theme, str) else None


def save_theme(theme: str) -> None:
    """Persist the given theme name to the config file."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps({"theme": theme}))
