"""Persisting user preferences, like the selected theme, to a JSON config file."""

from __future__ import annotations

import json

from platformdirs import user_config_path

CONFIG_PATH = user_config_path("pokertools", appauthor=False) / "config.json"

DEFAULT_ODDS_ERROR_MARGIN = 1.0


def _load_config() -> dict:
    try:
        data = json.loads(CONFIG_PATH.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _save_config(data: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(data))


def load_theme() -> str | None:
    """Return the previously saved theme name, or None if there isn't one."""
    theme = _load_config().get("theme")
    return theme if isinstance(theme, str) else None


def save_theme(theme: str) -> None:
    """Persist the given theme name to the config file."""
    data = _load_config()
    data["theme"] = theme
    _save_config(data)


def load_odds_error_margin() -> float:
    """Return the allowed error margin when grading "odds against" answers."""
    margin = _load_config().get("odds_error_margin")
    return margin if isinstance(margin, (int, float)) else DEFAULT_ODDS_ERROR_MARGIN


def save_odds_error_margin(margin: float) -> None:
    """Persist the allowed error margin when grading "odds against" answers."""
    data = _load_config()
    data["odds_error_margin"] = margin
    _save_config(data)
