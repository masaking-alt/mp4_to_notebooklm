from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from slide_scribe.models import TranscriptDocument
from slide_scribe.utils import ensure_parent_dir


def export_json(document: TranscriptDocument, output_path: Path) -> None:
    ensure_parent_dir(output_path)
    payload = _to_jsonable(document)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def document_to_dict(document: TranscriptDocument) -> dict[str, Any]:
    value = _to_jsonable(document)
    if not isinstance(value, dict):
        raise TypeError("TranscriptDocumentをdictに変換できません")
    return value


def _to_jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return _to_jsonable(asdict(value))
    if isinstance(value, dict):
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, tuple):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, Path):
        return value.as_posix()
    return value
