from __future__ import annotations

from pathlib import Path


def build_slide_image_filename(video_path: Path, index: int, extension: str = ".png") -> str:
    if index < 1:
        raise ValueError("indexは1以上である必要があります")

    suffix = extension if extension.startswith(".") else f".{extension}"
    return f"{video_path.stem}_{index:03d}{suffix}"


def build_output_filename(video_path: Path, extension: str) -> str:
    suffix = extension if extension.startswith(".") else f".{extension}"
    return f"{video_path.stem}{suffix}"


def format_timestamp(seconds: float) -> str:
    total_seconds = max(0, int(seconds))
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    remaining_seconds = total_seconds % 60

    if hours:
        return f"{hours:02d}:{minutes:02d}:{remaining_seconds:02d}"
    return f"{minutes:02d}:{remaining_seconds:02d}"


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def to_posix_relative(path: Path, base_dir: Path) -> str:
    try:
        return path.relative_to(base_dir).as_posix()
    except ValueError:
        return path.as_posix()


def clean_join(lines: list[str]) -> str:
    return "\n".join(line.strip() for line in lines if line.strip())
