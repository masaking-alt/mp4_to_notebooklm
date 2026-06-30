from pathlib import Path

import pytest

from slide_scribe.transcribe import normalize_transcriber_engine, resolve_mlx_model_name


def test_normalize_transcriber_engine_accepts_aliases() -> None:
    assert normalize_transcriber_engine("faster") == "faster-whisper"
    assert normalize_transcriber_engine("faster-whisper") == "faster-whisper"
    assert normalize_transcriber_engine("mlx") == "mlx-whisper"
    assert normalize_transcriber_engine("mlx_whisper") == "mlx-whisper"


def test_normalize_transcriber_engine_rejects_unknown_value() -> None:
    with pytest.raises(ValueError):
        normalize_transcriber_engine("unknown")


def test_resolve_mlx_model_name_maps_common_names() -> None:
    assert resolve_mlx_model_name("small") == "mlx-community/whisper-small-mlx"
    assert resolve_mlx_model_name("large-v3") == "mlx-community/whisper-large-v3-mlx"
    assert resolve_mlx_model_name("turbo") == "mlx-community/whisper-turbo"


def test_resolve_mlx_model_name_keeps_hf_repo_or_local_path(tmp_path) -> None:
    local_model = tmp_path / "model"
    local_model.mkdir()

    assert resolve_mlx_model_name("custom/repo") == "custom/repo"
    assert resolve_mlx_model_name(str(local_model)) == str(local_model)
