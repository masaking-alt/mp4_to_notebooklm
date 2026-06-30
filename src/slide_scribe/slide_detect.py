from __future__ import annotations

from pathlib import Path

import cv2
import imagehash
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity

from slide_scribe.config import SlideDetectionConfig
from slide_scribe.media import frame_index_to_timestamp, get_video_info, read_frame_at
from slide_scribe.models import Slide
from slide_scribe.utils import build_slide_image_filename


def preprocess_for_comparison(frame: np.ndarray) -> np.ndarray:
    resized = cv2.resize(frame, (640, 360), interpolation=cv2.INTER_AREA)
    return cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)


def detect_and_save_slides(
    video_path: Path,
    slides_dir: Path,
    config: SlideDetectionConfig,
) -> list[Slide]:
    if config.sample_fps <= 0:
        raise ValueError("sample_fpsは0より大きい必要があります")

    info = get_video_info(video_path)
    slides_dir.mkdir(parents=True, exist_ok=True)

    first_frame = read_frame_at(video_path, 0.0)
    slides: list[Slide] = []
    first_hash = _phash_from_frame(first_frame)
    _append_slide(
        video_path=video_path,
        slides=slides,
        slides_dir=slides_dir,
        frame=first_frame,
        start=0.0,
        detection_score=None,
    )

    capture = cv2.VideoCapture(str(video_path))
    try:
        if not capture.isOpened():
            raise RuntimeError(f"動画を開けません: {video_path}")

        sample_step = max(1, int(round(info.fps / config.sample_fps)))
        previous = preprocess_for_comparison(first_frame)
        last_change_time = 0.0
        last_hash = first_hash
        frame_index = sample_step

        while frame_index < info.frame_count:
            capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            ok, frame = capture.read()
            if not ok or frame is None:
                break

            current = preprocess_for_comparison(frame)
            score = float(structural_similarity(previous, current))
            timestamp = frame_index_to_timestamp(frame_index, info.fps)

            if (
                score < config.ssim_threshold
                and timestamp - last_change_time >= config.min_gap_sec
            ):
                capture_time = min(info.duration, timestamp + config.capture_delay_sec)
                stable_frame = read_frame_at(video_path, capture_time)
                current_hash = _phash_from_frame(stable_frame)

                if last_hash - current_hash > config.phash_threshold:
                    _append_slide(
                        video_path=video_path,
                        slides=slides,
                        slides_dir=slides_dir,
                        frame=stable_frame,
                        start=timestamp,
                        detection_score=score,
                    )
                    last_hash = current_hash

                last_change_time = timestamp

            previous = current
            frame_index += sample_step
    finally:
        capture.release()

    return slides


def _append_slide(
    video_path: Path,
    slides: list[Slide],
    slides_dir: Path,
    frame: np.ndarray,
    start: float,
    detection_score: float | None,
) -> None:
    index = len(slides) + 1
    image_filename = build_slide_image_filename(video_path, index)
    image_path = slides_dir / image_filename
    if not cv2.imwrite(str(image_path), frame):
        raise RuntimeError(f"スライド画像を保存できません: {image_path}")

    slides.append(
        Slide(
            index=index,
            start=float(start),
            end=None,
            image_filename=image_filename,
            image_path=f"slides/{image_filename}",
            detection_score=detection_score,
        )
    )


def _phash_from_frame(frame: np.ndarray) -> imagehash.ImageHash:
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return imagehash.phash(Image.fromarray(rgb))
