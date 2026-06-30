# slide-scribe

プレゼン動画からスライド画像、文字起こし、OCR、NotebookLM用PDFを生成するPython CLIツールです。

## 機能

- プレゼン動画からスライド画像を抽出
- `faster-whisper` による音声文字起こし
- スライド時間範囲への文字起こし割り当て
- 任意のOCR実行
- 正本としての `動画ファイル名.json` 出力
- NotebookLMに投入しやすい `動画ファイル名.pdf` 出力
- 任意の `動画ファイル名.md` 出力

## インストール

```bash
pip install -e .
```

開発用依存関係も入れる場合:

```bash
pip install -e ".[dev]"
```

OCRも使う場合:

```bash
pip install -e ".[ocr,dev]"
```

OCRはPython 3.11または3.12の仮想環境を推奨します。

Apple Silicon向けに `mlx-whisper` も使う場合:

```bash
pip install -e ".[mlx,dev]"
brew install ffmpeg
```

## 使い方

```bash
slide-scribe process input/presentation.mp4 --output output --export-md
```

OCRを使う場合:

```bash
slide-scribe process input/presentation.mp4 \
  --output output \
  --enable-ocr \
  --ocr-lang japan \
  --ocr-version PP-OCRv6 \
  --ocr-device cpu
```

`mlx-whisper` を使う場合:

```bash
slide-scribe process input/presentation.mp4 \
  --output output \
  --transcriber mlx \
  --model large-v3 \
  --export-md
```

主なオプション:

```bash
slide-scribe process VIDEO_PATH \
  --output output \
  --transcriber faster-whisper \
  --model large-v3 \
  --language ja \
  --sample-fps 2 \
  --ssim-threshold 0.82 \
  --min-gap-sec 1.0 \
  --capture-delay-sec 0.5 \
  --enable-ocr \
  --ocr-lang japan \
  --ocr-version PP-OCRv6 \
  --ocr-device cpu \
  --device cpu \
  --compute-type int8 \
  --export-md
```

## 出力

```txt
output/
  presentation.json
  presentation.pdf
  presentation.md
  slides/
    presentation_001.png
    presentation_002.png
```

## 注意

OCRは任意機能です。`paddleocr` が未インストールでも、`--enable-ocr` を付けなければ処理できます。
PaddleOCRは初回実行時にモデルをダウンロードします。

`mlx-whisper` は任意機能です。Apple Silicon Macでは有効な選択肢ですが、FFmpegが必要です。

PDFにはスライド画像だけでなく、画像ファイル名、文字起こし、OCRテキストを埋め込みます。
