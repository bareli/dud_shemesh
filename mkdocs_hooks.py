"""Build hooks for the docs site."""

from pathlib import Path

SRC = Path("CHANGELOG.md")
OUT = Path(".docs_build/CHANGELOG.md")


def on_pre_build(config):
    # The docs style has no em-dashes; the repo changelog does.
    text = SRC.read_text(encoding="utf-8")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(text.replace(" — ", " - ").replace("—", "-"), encoding="utf-8")
