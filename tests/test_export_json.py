import json

from slide_scribe.export_json import document_to_dict, export_json
from slide_scribe.models import Slide, TranscriptDocument, TranscriptSegment


def test_document_to_dict() -> None:
    document = TranscriptDocument(
        meta={"source_video": "input/presentation.mp4"},
        slides=[
            Slide(
                index=1,
                start=0.0,
                end=5.0,
                image_filename="slide_001.png",
                image_path="slides/slide_001.png",
                transcript_segments=[TranscriptSegment(0.0, 1.0, "本文")],
            )
        ],
    )

    payload = document_to_dict(document)

    assert payload["slides"][0]["transcript_segments"][0]["text"] == "本文"


def test_export_json_writes_utf8(tmp_path) -> None:
    output_path = tmp_path / "transcript.json"
    document = TranscriptDocument(
        meta={"source_video": "input/presentation.mp4"},
        slides=[
            Slide(
                index=1,
                start=0.0,
                end=5.0,
                image_filename="slide_001.png",
                image_path="slides/slide_001.png",
                transcript="日本語",
            )
        ],
    )

    export_json(document, output_path)

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["slides"][0]["transcript"] == "日本語"
