from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from slide_scribe.config import AppConfig, SlideDetectionConfig, TranscriptionConfig
from slide_scribe.logging import console
from slide_scribe.pipeline import process_video


app = typer.Typer(help="プレゼン動画からNotebookLM用資料を生成します。")


@app.callback()
def main() -> None:
    """プレゼン動画からNotebookLM用資料を生成します。"""


@app.command("process")
def process_command(
    video_path: Annotated[Path, typer.Argument(help="入力動画ファイル")],
    output: Annotated[Path, typer.Option("--output", "-o", help="出力先ディレクトリ")] = Path(
        "output"
    ),
    transcriber: Annotated[
        str,
        typer.Option("--transcriber", help="文字起こしエンジン: faster-whisper または mlx"),
    ] = "faster-whisper",
    model_name: Annotated[str, typer.Option("--model", help="文字起こしモデル名")] = "large-v3",
    language: Annotated[str, typer.Option("--language", help="文字起こし言語")] = "ja",
    sample_fps: Annotated[float, typer.Option("--sample-fps", help="スライド検出サンプリングFPS")] = 2.0,
    ssim_threshold: Annotated[
        float,
        typer.Option("--ssim-threshold", help="SSIMしきい値"),
    ] = 0.82,
    min_gap_sec: Annotated[
        float,
        typer.Option("--min-gap-sec", help="連続検出抑制秒数"),
    ] = 1.0,
    capture_delay_sec: Annotated[
        float,
        typer.Option("--capture-delay-sec", help="切替検出後に画像を保存するまでの秒数"),
    ] = 0.5,
    enable_ocr: Annotated[
        bool,
        typer.Option("--enable-ocr/--skip-ocr", help="OCRを有効化する"),
    ] = False,
    ocr_lang: Annotated[str, typer.Option("--ocr-lang", help="PaddleOCRのOCR言語")] = "japan",
    ocr_device: Annotated[str, typer.Option("--ocr-device", help="PaddleOCR実行デバイス")] = "cpu",
    ocr_version: Annotated[
        str,
        typer.Option("--ocr-version", help="PaddleOCRモデルバージョン"),
    ] = "PP-OCRv6",
    export_md: Annotated[
        bool,
        typer.Option("--export-md/--no-export-md", help="Markdownも出力する"),
    ] = False,
    device: Annotated[str, typer.Option("--device", help="faster-whisper実行デバイス")] = "cpu",
    compute_type: Annotated[
        str,
        typer.Option("--compute-type", help="faster-whisper計算タイプ"),
    ] = "int8",
) -> None:
    app_config = AppConfig(
        output_dir=output,
        enable_ocr=enable_ocr,
        ocr_lang=ocr_lang,
        ocr_device=ocr_device,
        ocr_version=ocr_version,
        export_md=export_md,
    )
    transcription_config = TranscriptionConfig(
        engine=transcriber,
        model_name=model_name,
        language=language,
        device=device,
        compute_type=compute_type,
    )
    slide_config = SlideDetectionConfig(
        sample_fps=sample_fps,
        ssim_threshold=ssim_threshold,
        min_gap_sec=min_gap_sec,
        capture_delay_sec=capture_delay_sec,
    )

    try:
        process_video(
            video_path=video_path,
            output_dir=output,
            app_config=app_config,
            transcription_config=transcription_config,
            slide_config=slide_config,
        )
    except Exception as exc:
        console.print(f"[bold red]エラー:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(f"[bold green]完了:[/bold green] {output}")


if __name__ == "__main__":
    app()
