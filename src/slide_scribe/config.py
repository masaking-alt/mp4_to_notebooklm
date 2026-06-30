from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class SlideDetectionConfig:
    sample_fps: float = 2.0
    ssim_threshold: float = 0.82
    min_gap_sec: float = 1.0
    capture_delay_sec: float = 0.5
    phash_threshold: int = 6


@dataclass
class TranscriptionConfig:
    engine: str = "faster-whisper"
    model_name: str = "large-v3"
    language: str = "ja"
    device: str = "cpu"
    compute_type: str = "int8"
    vad_filter: bool = True


@dataclass
class AppConfig:
    output_dir: Path
    enable_ocr: bool = False
    ocr_lang: str = "japan"
    ocr_device: str = "cpu"
    ocr_version: str = "PP-OCRv6"
    export_md: bool = False
