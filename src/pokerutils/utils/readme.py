"""Loading the README shown on the home screen, from source or an installed package."""

from __future__ import annotations

from pathlib import Path

PACKAGE_ROOT = Path(__file__).parents[1]

# Installed wheels bundle the README beside the package; a source checkout keeps
# it at the repository root.
README_CANDIDATES = (PACKAGE_ROOT / "README.md", PACKAGE_ROOT.parents[1] / "README.md")

FALLBACK = "README.md is unavailable in this install. See https://github.com/markosnarinian/pokerutils\n"


def readme_path() -> Path | None:
    """Return the first README that exists, or None if neither does."""
    return next((path for path in README_CANDIDATES if path.is_file()), None)


def load_readme(title: bool = False) -> str:
    path = readme_path()
    if path is None:
        return FALLBACK
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    if not title and lines:
        lines.pop(0)
    return "".join(lines)
