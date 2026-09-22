"""Чтение UTF-8 JSON и атомарная запись через временный файл."""

import json
import os
import tempfile
from pathlib import Path

from sportpartner.validation import validate_data


def load_data(path: str | Path) -> dict:
    """Загрузить проверенные данные; ошибки передать интерфейсу."""
    with Path(path).open(encoding="utf-8") as stream:
        return validate_data(json.load(stream))


def save_data(path: str | Path, data: dict) -> None:
    """Сохранить весь набор, не оставляя частично записанный JSON."""
    validate_data(data)
    target = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=target.parent,
            prefix=target.name + ".", suffix=".tmp", delete=False,
        ) as stream:
            temporary = Path(stream.name)
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
