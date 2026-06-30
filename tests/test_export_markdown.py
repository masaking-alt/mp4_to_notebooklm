from slide_scribe.export_markdown import export_markdown
from slide_scribe.models import Slide, TranscriptDocument


def test_export_markdown(tmp_path) -> None:
    output_path = tmp_path / "transcript.md"
    document = TranscriptDocument(
        meta={"source_video": "input/presentation.mp4"},
        slides=[
            Slide(
                index=1,
                start=0.0,
                end=42.0,
                image_filename="slide_001.png",
                image_path="slides/slide_001.png",
                transcript="説明本文",
                ocr="見出し",
            )
        ],
    )

    export_markdown(document, output_path)

    text = output_path.read_text(encoding="utf-8")
    assert "## Slide 001" in text
    assert "Time: 00:00 - 00:42" in text
    assert "説明本文" in text
    assert "見出し" in text
