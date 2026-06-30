from __future__ import annotations

from datetime import datetime
from pathlib import Path

from slide_scribe.assign import assign_transcript_to_slides
from slide_scribe.config import AppConfig, SlideDetectionConfig, TranscriptionConfig
from slide_scribe.export_json import export_json
from slide_scribe.export_markdown import export_markdown
from slide_scribe.export_pdf import export_notebooklm_pdf
from slide_scribe.logging import console
from slide_scribe.media import get_video_info
from slide_scribe.models import TranscriptDocument
from slide_scribe.ocr import attach_ocr_to_slides_with_base_dir
from slide_scribe.slide_detect import detect_and_save_slides
from slide_scribe.transcribe import normalize_transcriber_engine, resolve_mlx_model_name, transcribe_video
from slide_scribe.utils import build_output_filename


def process_video(
    video_path: Path,
    output_dir: Path,
    app_config: AppConfig,
    transcription_config: TranscriptionConfig,
    slide_config: SlideDetectionConfig,
) -> TranscriptDocument:
    output_dir.mkdir(parents=True, exist_ok=True)
    slides_dir = output_dir / "slides"
    slides_dir.mkdir(parents=True, exist_ok=True)

    console.print("[bold]動画情報を取得しています[/bold]")
    video_info = get_video_info(video_path)

    console.print("[bold]音声を文字起こししています[/bold]")
    transcription_engine = normalize_transcriber_engine(transcription_config.engine)
    segments = transcribe_video(video_path, transcription_config)
    resolved_model_name = (
        resolve_mlx_model_name(transcription_config.model_name)
        if transcription_engine == "mlx-whisper"
        else transcription_config.model_name
    )
    transcription_meta = {
        "engine": transcription_engine,
        "model": resolved_model_name,
        "language": transcription_config.language,
    }
    if transcription_engine == "faster-whisper":
        transcription_meta.update(
            {
                "device": transcription_config.device,
                "compute_type": transcription_config.compute_type,
                "vad_filter": transcription_config.vad_filter,
            }
        )
    else:
        transcription_meta["device"] = "mlx"

    console.print("[bold]スライドを検出しています[/bold]")
    slides = detect_and_save_slides(video_path, slides_dir, slide_config)

    console.print("[bold]OCRを処理しています[/bold]")
    slides = attach_ocr_to_slides_with_base_dir(
        slides=slides,
        enable_ocr=app_config.enable_ocr,
        base_dir=output_dir,
        lang=app_config.ocr_lang,
        device=app_config.ocr_device,
        ocr_version=app_config.ocr_version,
    )

    console.print("[bold]文字起こしをスライドに割り当てています[/bold]")
    slides = assign_transcript_to_slides(slides, segments, video_info.duration)

    document = TranscriptDocument(
        meta={
            "source_video": str(video_path),
            "duration": video_info.duration,
            "fps": video_info.fps,
            "frame_count": video_info.frame_count,
            "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "transcription": transcription_meta,
            "ocr": {
                "enabled": app_config.enable_ocr,
                "engine": "paddleocr" if app_config.enable_ocr else None,
                "lang": app_config.ocr_lang if app_config.enable_ocr else None,
                "device": app_config.ocr_device if app_config.enable_ocr else None,
                "version": app_config.ocr_version if app_config.enable_ocr else None,
            },
            "slide_detection": {
                "method": "ssim+phash",
                "sample_fps": slide_config.sample_fps,
                "ssim_threshold": slide_config.ssim_threshold,
                "min_gap_sec": slide_config.min_gap_sec,
                "capture_delay_sec": slide_config.capture_delay_sec,
                "phash_threshold": slide_config.phash_threshold,
            },
        },
        slides=slides,
    )

    json_filename = build_output_filename(video_path, ".json")
    pdf_filename = build_output_filename(video_path, ".pdf")
    markdown_filename = build_output_filename(video_path, ".md")

    console.print(f"[bold]{json_filename}を出力しています[/bold]")
    export_json(document, output_dir / json_filename)

    console.print(f"[bold]{pdf_filename}を出力しています[/bold]")
    export_notebooklm_pdf(document, output_dir / pdf_filename, output_dir)

    if app_config.export_md:
        console.print(f"[bold]{markdown_filename}を出力しています[/bold]")
        export_markdown(document, output_dir / markdown_filename)

    return document
