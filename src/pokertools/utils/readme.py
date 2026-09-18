from pathlib import Path


README_PATH = Path(__file__).parents[3] / "README.md"


def load_readme(title: bool = False) -> str:
    lines = README_PATH.read_text().splitlines(keepends=True)
    if not title and lines:
        lines.pop(0)
    return "".join(lines)
