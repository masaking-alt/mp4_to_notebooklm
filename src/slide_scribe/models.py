from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class VideoInfo:
    path: str
    duration: float
    fps: float
    frame_count: int


@dataclass
class TranscriptSegment:
    start: float
    end: float
    text: str


@dataclass
class Slide:
    index: int
    start: float
    end: float | None
    image_filename: str
    image_path: str
    transcript: str = ""
    ocr: str = ""
    transcript_segments: list[TranscriptSegment] = field(default_factory=list)
    detection_score: float | None = None


@dataclass
class TranscriptDocument:
    meta: dict[str, Any]
    slides: list[Slide]
