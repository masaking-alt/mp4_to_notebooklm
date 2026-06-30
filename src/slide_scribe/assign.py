from __future__ import annotations

from slide_scribe.models import Slide, TranscriptSegment
from slide_scribe.utils import clean_join


def assign_transcript_to_slides(
    slides: list[Slide],
    segments: list[TranscriptSegment],
    video_duration: float,
) -> list[Slide]:
    if not slides:
        return []

    ordered_slides = sorted(slides, key=lambda slide: slide.start)

    for index, slide in enumerate(ordered_slides):
        if index + 1 < len(ordered_slides):
            slide.end = ordered_slides[index + 1].start
        else:
            slide.end = video_duration
        slide.transcript_segments = []
        slide.transcript = ""

    for segment in segments:
        slide = _find_slide_for_segment(ordered_slides, segment)
        if slide is None:
            continue
        slide.transcript_segments.append(segment)

    for slide in ordered_slides:
        slide.transcript = clean_join([segment.text for segment in slide.transcript_segments])

    return ordered_slides


def _find_slide_for_segment(slides: list[Slide], segment: TranscriptSegment) -> Slide | None:
    for slide in slides:
        if slide.end is None:
            continue
        if slide.start <= segment.start < slide.end:
            return slide
    return None
