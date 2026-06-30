from __future__ import annotations

from pathlib import Path

from slide_scribe.config import TranscriptionConfig
from slide_scribe.models import TranscriptSegment


SUPPORTED_TRANSCRIBERS = {"faster-whisper", "mlx-whisper"}

MLX_MODEL_ALIASES = {
    "tiny": "mlx-community/whisper-tiny-mlx",
    "base": "mlx-community/whisper-base-mlx",
    "small": "mlx-community/whisper-small-mlx",
    "medium": "mlx-community/whisper-medium-mlx",
    "large-v2": "mlx-community/whisper-large-v2-mlx",
    "large-v3": "mlx-community/whisper-large-v3-mlx",
    "turbo": "mlx-community/whisper-turbo",
}


def transcribe_video(
    video_path: Path,
    config: TranscriptionConfig,
) -> list[TranscriptSegment]:
    if not video_path.exists():
        raise FileNotFoundError(f"動画ファイルが見つかりません: {video_path}")

    engine = normalize_transcriber_engine(config.engine)
    if engine == "mlx-whisper":
        return _transcribe_with_mlx_whisper(video_path, config)
    return _transcribe_with_faster_whisper(video_path, config)


def normalize_transcriber_engine(engine: str) -> str:
    normalized = engine.strip().lower().replace("_", "-")
    aliases = {
        "faster": "faster-whisper",
        "faster-whisper": "faster-whisper",
        "mlx": "mlx-whisper",
        "mlx-whisper": "mlx-whisper",
    }
    if normalized not in aliases:
        supported = ", ".join(sorted(SUPPORTED_TRANSCRIBERS))
        raise ValueError(f"未対応の文字起こしエンジンです: {engine}。対応: {supported}")
    return aliases[normalized]


def resolve_mlx_model_name(model_name: str) -> str:
    if "/" in model_name or Path(model_name).exists():
        return model_name
    return MLX_MODEL_ALIASES.get(model_name, model_name)


def _transcribe_with_faster_whisper(
    video_path: Path,
    config: TranscriptionConfig,
) -> list[TranscriptSegment]:
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError(
            "faster-whisperがインストールされていません。"
            ' `pip install -e ".[dev]"` または `pip install faster-whisper` を実行してください。'
        ) from exc

    model = WhisperModel(
        config.model_name,
        device=config.device,
        compute_type=config.compute_type,
    )

    try:
        segments, _ = model.transcribe(
            str(video_path),
            language=config.language,
            vad_filter=config.vad_filter,
        )
    except Exception as exc:
        raise RuntimeError(f"文字起こしに失敗しました: {exc}") from exc

    transcript_segments: list[TranscriptSegment] = []
    for segment in segments:
        text = segment.text.strip()
        if not text:
            continue
        transcript_segments.append(
            TranscriptSegment(
                start=float(segment.start),
                end=float(segment.end),
                text=text,
            )
        )
    return transcript_segments


def _transcribe_with_mlx_whisper(
    video_path: Path,
    config: TranscriptionConfig,
) -> list[TranscriptSegment]:
    try:
        import mlx_whisper
    except ImportError as exc:
        raise RuntimeError(
            "mlx-whisperがインストールされていません。"
            ' `pip install -e ".[mlx,dev]"` または `pip install mlx-whisper` を実行してください。'
        ) from exc

    model_name = resolve_mlx_model_name(config.model_name)
    try:
        result = mlx_whisper.transcribe(
            str(video_path),
            path_or_hf_repo=model_name,
            language=config.language,
        )
    except Exception as exc:
        raise RuntimeError(f"mlx-whisperでの文字起こしに失敗しました: {exc}") from exc

    transcript_segments: list[TranscriptSegment] = []
    for segment in result.get("segments", []):
        text = str(segment.get("text", "")).strip()
        if not text:
            continue
        transcript_segments.append(
            TranscriptSegment(
                start=float(segment["start"]),
                end=float(segment["end"]),
                text=text,
            )
        )
    return transcript_segments
