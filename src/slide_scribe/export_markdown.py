from __future__ import annotations

from pathlib import Path

from slide_scribe.models import TranscriptDocument
from slide_scribe.utils import ensure_parent_dir, format_timestamp


def export_markdown(
    document: TranscriptDocument,
    output_path: Path,
) -> None:
    ensure_parent_dir(output_path)
    lines: list[str] = ["# Presentation Transcript", ""]

    for slide in document.slides:
        start = format_timestamp(slide.start)
        end = format_timestamp(slide.end or slide.start)

        lines.extend(
            [
                f"## Slide {slide.index:03d}",
                "",
                f"Time: {start} - {end}  ",
                f"Image filename: `{slide.image_filename}`",
                "",
                f"![Slide {slide.index:03d}]({slide.image_path})",
                "",
                "### Transcript",
                "",
                slide.transcript,
                "",
                "### OCR",
                "",
                slide.ocr,
                "",
            ]
        )

    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
