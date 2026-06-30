from dataclasses import asdict

from slide_scribe.models import Slide, TranscriptDocument, TranscriptSegment


def test_slide_can_be_converted_to_dict() -> None:
    segment = TranscriptSegment(start=0.2, end=7.6, text="本文")
    slide = Slide(
        index=1,
        start=0.0,
        end=42.3,
        image_filename="slide_001.png",
        image_path="slides/slide_001.png",
        transcript="本文",
        ocr="OCR",
        transcript_segments=[segment],
    )

    payload = asdict(slide)

    assert payload["index"] == 1
    assert payload["transcript_segments"][0]["text"] == "本文"


def test_transcript_document_holds_meta_and_slides() -> None:
    document = TranscriptDocument(meta={"duration": 10.0}, slides=[])

    assert document.meta["duration"] == 10.0
    assert document.slides == []
