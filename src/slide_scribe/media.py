from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from slide_scribe.models import VideoInfo


def get_video_info(video_path: Path) -> VideoInfo:
    if not video_path.exists():
        raise FileNotFoundError(f"動画ファイルが見つかりません: {video_path}")

    capture = cv2.VideoCapture(str(video_path))
    try:
        if not capture.isOpened():
            raise RuntimeError(f"動画を開けません: {video_path}")

        fps = float(capture.get(cv2.CAP_PROP_FPS) or 0.0)
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        if fps <= 0:
            raise RuntimeError(f"FPSを取得できません: {video_path}")

        duration = frame_count / fps if frame_count else 0.0
        return VideoInfo(
            path=str(video_path),
            duration=duration,
            fps=fps,
            frame_count=frame_count,
        )
    finally:
        capture.release()


def timestamp_to_frame_index(timestamp_sec: float, fps: float) -> int:
    return max(0, int(round(timestamp_sec * fps)))


def frame_index_to_timestamp(frame_index: int, fps: float) -> float:
    if fps <= 0:
        raise ValueError("fpsは0より大きい必要があります")
    return frame_index / fps


def read_frame_at(video_path: Path, timestamp_sec: float) -> np.ndarray:
    info = get_video_info(video_path)
    frame_index = min(
        max(0, timestamp_to_frame_index(timestamp_sec, info.fps)),
        max(0, info.frame_count - 1),
    )

    capture = cv2.VideoCapture(str(video_path))
    try:
        if not capture.isOpened():
            raise RuntimeError(f"動画を開けません: {video_path}")

        capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = capture.read()
        if not ok or frame is None:
            raise RuntimeError(f"フレームを読み取れません: {video_path} at {timestamp_sec:.2f}s")
        return frame
    finally:
        capture.release()
