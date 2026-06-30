from __future__ import annotations

from pathlib import Path

from slide_scribe.models import Slide, TranscriptDocument
from slide_scribe.utils import ensure_parent_dir, format_timestamp


def export_notebooklm_pdf(
    document: TranscriptDocument,
    output_path: Path,
    base_dir: Path,
) -> None:
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError(
            "PyMuPDFがインストールされていません。"
            ' `pip install -e ".[dev]"` または `pip install pymupdf` を実行してください。'
        ) from exc

    ensure_parent_dir(output_path)
    pdf = fitz.open()
    try:
        for slide in document.slides:
            _append_slide_pages(pdf, slide, base_dir, fitz)
        pdf.save(str(output_path))
    finally:
        pdf.close()


def _append_slide_pages(pdf, slide: Slide, base_dir: Path, fitz) -> None:
    width = 842
    height = 595
    margin = 36
    header_rect = fitz.Rect(margin, 24, width - margin, 70)
    image_rect = fitz.Rect(margin, 76, width - margin, 356)
    text_rect = fitz.Rect(margin, 370, width - margin, height - margin)

    body_lines = _slide_text_lines(slide)
    first_chunk, remaining = _split_lines(body_lines, max_lines=15)

    page = pdf.new_page(width=width, height=height)
    _insert_textbox(page, header_rect, _slide_header(slide), fitz, fontsize=10)
    _insert_slide_image(page, image_rect, base_dir / slide.image_path)
    _insert_textbox(page, text_rect, "\n".join(first_chunk), fitz, fontsize=9)

    while remaining:
        chunk, remaining = _split_lines(remaining, max_lines=34)
        page = pdf.new_page(width=width, height=height)
        _insert_textbox(
            page,
            header_rect,
            f"Slide {slide.index:03d} continued",
            fitz,
            fontsize=10,
        )
        full_rect = fitz.Rect(margin, 78, width - margin, height - margin)
        _insert_textbox(page, full_rect, "\n".join(chunk), fitz, fontsize=9)


def _slide_header(slide: Slide) -> str:
    start = format_timestamp(slide.start)
    end = format_timestamp(slide.end or slide.start)
    return (
        f"Slide {slide.index:03d}\n"
        f"Time: {start} - {end}\n"
        f"Image filename: {slide.image_filename}"
    )


def _slide_text_lines(slide: Slide) -> list[str]:
    text = f"Transcript:\n{slide.transcript}\n\nOCR:\n{slide.ocr}"
    return _wrap_text(text, line_width=92)


def _wrap_text(text: str, line_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.splitlines():
        if not paragraph:
            lines.append("")
            continue

        current = paragraph
        while len(current) > line_width:
            lines.append(current[:line_width])
            current = current[line_width:]
        lines.append(current)
    return lines


def _split_lines(lines: list[str], max_lines: int) -> tuple[list[str], list[str]]:
    return lines[:max_lines], lines[max_lines:]


def _insert_slide_image(page, rect, image_path: Path) -> None:
    if image_path.exists():
        page.insert_image(rect, filename=str(image_path), keep_proportion=True)


def _insert_textbox(page, rect, text: str, fitz, fontsize: float) -> None:
    for fontname in ("japan", "helv"):
        try:
            page.insert_textbox(
                rect,
                text,
                fontsize=fontsize,
                fontname=fontname,
                color=(0, 0, 0),
                align=fitz.TEXT_ALIGN_LEFT,
            )
            return
        except Exception:
            continue
    page.insert_textbox(rect, text, fontsize=fontsize)
