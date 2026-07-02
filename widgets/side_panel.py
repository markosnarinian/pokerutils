"""A bordered panel beside the table, reserved for auxiliary info."""

from __future__ import annotations

from textual.containers import Vertical


class SidePanel(Vertical):
    """A panel next to the table for future info such as stats or actions."""
