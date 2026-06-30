from pathlib import Path

import pytest

from slide_scribe.utils import build_output_filename, build_slide_image_filename, format_timestamp


def test_format_timestamp_without_hours() -> None:
    assert format_timestamp(0) == "00:00"
    assert format_timestamp(83.9) == "01:23"


def test_format_timestamp_with_hours() -> None:
    assert format_timestamp(3723) == "01:02:03"


def test_format_timestamp_clamps_negative_values() -> None:
    assert format_timestamp(-10) == "00:00"


def test_build_slide_image_filename_uses_video_stem() -> None:
    assert build_slide_image_filename(Path("HDL_C(1)-(8).mp4"), 1) == "HDL_C(1)-(8)_001.png"
    assert build_slide_image_filename(Path("lecture.final.mov"), 12) == "lecture.final_012.png"


def test_build_slide_image_filename_rejects_invalid_index() -> None:
    with pytest.raises(ValueError):
        build_slide_image_filename(Path("lecture.mp4"), 0)


def test_build_output_filename_uses_video_stem() -> None:
    assert build_output_filename(Path("HDL_C(1)-(8).mp4"), ".json") == "HDL_C(1)-(8).json"
    assert build_output_filename(Path("lecture.final.mov"), "pdf") == "lecture.final.pdf"
