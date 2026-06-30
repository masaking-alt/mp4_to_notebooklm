from slide_scribe.assign import assign_transcript_to_slides
from slide_scribe.models import Slide, TranscriptSegment


def test_assign_transcript_to_slides() -> None:
    slides = [
        Slide(
            index=1,
            start=0.0,
            end=None,
            image_filename="slide_001.png",
            image_path="slides/slide_001.png",
        ),
        Slide(
            index=2,
            start=10.0,
            end=None,
            image_filename="slide_002.png",
            image_path="slides/slide_002.png",
        ),
    ]
    segments = [
        TranscriptSegment(start=1.0, end=2.0, text="first"),
        TranscriptSegment(start=12.0, end=13.0, text="second"),
    ]

    result = assign_transcript_to_slides(slides, segments, video_duration=20.0)

    assert result[0].end == 10.0
    assert result[1].end == 20.0
    assert result[0].transcript == "first"
    assert result[1].transcript == "second"


def test_assign_boundary_segment_to_next_slide() -> None:
    slides = [
        Slide(1, 0.0, None, "slide_001.png", "slides/slide_001.png"),
        Slide(2, 10.0, None, "slide_002.png", "slides/slide_002.png"),
    ]
    segments = [
        TranscriptSegment(start=10.0, end=11.0, text="boundary"),
    ]

    result = assign_transcript_to_slides(slides, segments, video_duration=20.0)

    assert result[0].transcript == ""
    assert result[1].transcript == "boundary"
