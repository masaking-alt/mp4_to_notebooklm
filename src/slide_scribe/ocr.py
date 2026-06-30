from __future__ import annotations

from pathlib import Path
from typing import Any

from slide_scribe.models import Slide
from slide_scribe.utils import clean_join


def run_ocr_on_image(
    image_path: Path,
    lang: str = "japan",
    device: str = "cpu",
    ocr_version: str = "PP-OCRv6",
) -> str:
    reader = _create_paddleocr_reader(
        lang=lang,
        device=device,
        ocr_version=ocr_version,
    )
    return _run_reader(reader, image_path)


def attach_ocr_to_slides(
    slides: list[Slide],
    enable_ocr: bool,
    lang: str = "japan",
    device: str = "cpu",
    ocr_version: str = "PP-OCRv6",
) -> list[Slide]:
    if not enable_ocr:
        return slides

    reader = _create_paddleocr_reader(
        lang=lang,
        device=device,
        ocr_version=ocr_version,
    )
    for slide in slides:
        slide.ocr = _run_reader(reader, Path(slide.image_path))
    return slides


def attach_ocr_to_slides_with_base_dir(
    slides: list[Slide],
    enable_ocr: bool,
    base_dir: Path,
    lang: str = "japan",
    device: str = "cpu",
    ocr_version: str = "PP-OCRv6",
) -> list[Slide]:
    if not enable_ocr:
        return slides

    reader = _create_paddleocr_reader(
        lang=lang,
        device=device,
        ocr_version=ocr_version,
    )
    for slide in slides:
        slide.ocr = _run_reader(reader, base_dir / slide.image_path)
    return slides


def _create_paddleocr_reader(lang: str, device: str, ocr_version: str) -> Any:
    try:
        from paddleocr import PaddleOCR
    except ImportError as exc:
        raise RuntimeError(
            "PaddleOCRがインストールされていません。OCRを使う場合は"
            ' `pip install -e ".[ocr]"` を実行してください。'
        ) from exc

    try:
        return PaddleOCR(
            lang=lang,
            ocr_version=ocr_version,
            device=device,
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
        )
    except TypeError as exc:
        raise RuntimeError(
            "PaddleOCRの初期化に失敗しました。PaddleOCR 3.xを前提にしています。"
            ' `pip install -e ".[ocr]"` で依存関係を入れ直してください。'
        ) from exc


def _run_reader(reader: Any, image_path: Path) -> str:
    if not image_path.exists():
        raise FileNotFoundError(f"OCR対象画像が見つかりません: {image_path}")

    if hasattr(reader, "predict"):
        result = reader.predict(str(image_path))
    elif hasattr(reader, "ocr"):
        result = reader.ocr(str(image_path))
    else:
        raise RuntimeError("PaddleOCR readerにpredict/ocrメソッドがありません")

    lines: list[str] = []
    _collect_ocr_lines(result, lines)
    return clean_join(lines)


def _collect_ocr_lines(value: Any, lines: list[str]) -> None:
    if value is None:
        return

    if isinstance(value, dict):
        for key in ("rec_texts", "texts", "text"):
            if key in value:
                _append_text_value(value[key], lines)

        for key in ("res", "result", "ocrResults", "prunedResult"):
            if key in value:
                _collect_ocr_lines(value[key], lines)
        return

    if isinstance(value, (list, tuple)):
        if (
            len(value) == 2
            and isinstance(value[1], (list, tuple))
            and value[1]
            and isinstance(value[1][0], str)
        ):
            lines.append(value[1][0])
            return

        for item in value:
            _collect_ocr_lines(item, lines)

    for attribute_name in ("res", "rec_texts", "texts", "text"):
        if hasattr(value, attribute_name):
            _collect_ocr_lines(getattr(value, attribute_name), lines)


def _append_text_value(value: Any, lines: list[str]) -> None:
    if isinstance(value, str):
        lines.append(value)
        return

    if isinstance(value, (list, tuple)):
        for item in value:
            _append_text_value(item, lines)
