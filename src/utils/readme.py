def load_readme(title=False) -> str:
    with open("README.md") as file:
        lines = file.readlines()
        if not title:
            lines.pop(0)
        return "\n".join(lines)
