# Codex Prompt: プレゼン動画からスライド画像・文字起こし・OCR・NotebookLM用PDFを生成するPythonリポジトリを構成する

## 目的

静止画スライドが切り替わっていくプレゼン動画から、以下を自動生成するPythonツールを作りたい。

入力は `.mp4` などのプレゼン動画。
出力は以下。

* スライドごとの画像ファイル
* スライドごとの音声文字起こし
* スライド画像に対するOCRテキスト
* それらを統合した `transcript.json`
* NotebookLMに投入しやすい `notebooklm_source.pdf`
* 任意で人間確認用の `transcript.md`

このツールの主な用途は、大学講義・研究発表・プレゼン動画を、NotebookLMやLLMに読み込ませやすい資料形式に変換すること。

---

## 基本方針

最終成果物はPDFでもMarkdownでもよいが、正本は必ず `transcript.json` とする。

理由：

* PDFはNotebookLM投入用
* Markdownは人間確認用
* JSONは後からPDF/Markdown/HTML/要約/検索などに再利用できる

処理全体は以下のパイプラインにする。

```txt
動画 input.mp4
  ↓
音声文字起こし
  ↓
スライド切替検出
  ↓
スライド画像保存
  ↓
スライド画像OCR
  ↓
スライド時間範囲にtranscriptを割り当て
  ↓
transcript.json生成
  ↓
notebooklm_source.pdf生成
  ↓
任意でtranscript.md生成
```

---

## リポジトリ名

仮に以下で作る。

```txt
slide-scribe
```

Pythonパッケージ名は以下。

```txt
slide_scribe
```

CLIコマンド名は以下。

```txt
slide-scribe
```

---

## 技術スタック

### 言語

* Python 3.11以上
* 型ヒントを使う
* `pathlib.Path` を使う
* 過剰にクラス化しすぎず、責務ごとの関数・小さなモジュールに分ける

### パッケージ管理

`pyproject.toml` を使う。

可能なら `uv` でも `pip` でも使える構成にする。

### 主要ライブラリ

| 用途      | ライブラリ            | 備考                        |
| ------- | ---------------- | ------------------------- |
| CLI     | `typer`          | コマンドライン実行用                |
| ログ表示    | `rich`           | 進捗・ログを見やすくする              |
| 動画読み込み  | `opencv-python`  | フレーム抽出、スライド検出             |
| 画像類似度   | `scikit-image`   | SSIMでスライド切替検出             |
| 画像処理    | `Pillow`         | imagehashやPDF生成補助         |
| 重複除去    | `imagehash`      | pHashで似すぎたスライドを除外         |
| 音声文字起こし | `faster-whisper` | Whisper系の高速実装             |
| PDF生成   | `PyMuPDF`        | 画像とテキストをPDF化              |
| OCR     | `PaddleOCR`      | 日本語OCR用。ただし重いのでoptional扱い |

### OCRについて

`PaddleOCR` は重いので、初期実装では以下の方針にする。

* OCR機能は `--enable-ocr` を付けたときだけ動かす
* `paddleocr` が未インストールなら、わかりやすいエラーを出す
* `--skip-ocr` またはデフォルトではOCR欄を空文字にして処理継続できるようにする
* 将来的に別OCRエンジンに差し替えられるよう、`ocr.py` に責務を閉じ込める

---

## 推奨ディレクトリ構成

以下のように構成してほしい。

```txt
slide-scribe/
  README.md
  pyproject.toml
  .gitignore
  .python-version
  LICENSE

  src/
    slide_scribe/
      __init__.py
      cli.py
      config.py
      models.py
      pipeline.py

      media.py
      transcribe.py
      slide_detect.py
      ocr.py
      assign.py

      export_json.py
      export_pdf.py
      export_markdown.py

      utils.py
      logging.py

  tests/
    test_models.py
    test_assign.py
    test_utils.py
    test_export_markdown.py

  examples/
    config.example.yaml
    sample_output/
      transcript.example.json
      transcript.example.md

  docs/
    architecture.md
    json_schema.md
    notebooklm_pdf_format.md
```

---

## 各ファイルの責務

### `cli.py`

CLIの入口。

Typerで以下のコマンドを実装する。

```bash
slide-scribe process input/presentation.mp4 --output output/
```

必要なオプション：

```bash
slide-scribe process VIDEO_PATH \
  --output output \
  --model large-v3 \
  --language ja \
  --sample-fps 2 \
  --ssim-threshold 0.82 \
  --min-gap-sec 1.0 \
  --capture-delay-sec 0.5 \
  --enable-ocr \
  --export-md
```

最低限ほしいオプション：

| オプション                 | 意味                 | デフォルト      |
| --------------------- | ------------------ | ---------- |
| `video_path`          | 入力動画               | 必須         |
| `--output`            | 出力先ディレクトリ          | `output`   |
| `--model`             | faster-whisperモデル  | `large-v3` |
| `--language`          | 文字起こし言語            | `ja`       |
| `--sample-fps`        | スライド検出のサンプリングFPS   | `2`        |
| `--ssim-threshold`    | SSIMしきい値           | `0.82`     |
| `--min-gap-sec`       | 連続検出抑制秒数           | `1.0`      |
| `--capture-delay-sec` | 切替検出後に何秒後の画像を保存するか | `0.5`      |
| `--enable-ocr`        | OCRを有効にする          | false      |
| `--export-md`         | Markdownも出力する      | false      |
| `--device`            | Whisper実行デバイス      | `cpu`      |
| `--compute-type`      | Whisper計算タイプ       | `int8`     |

---

### `config.py`

設定値をまとめる。

`dataclass` を使ってよい。

例：

```python
@dataclass
class SlideDetectionConfig:
    sample_fps: float = 2.0
    ssim_threshold: float = 0.82
    min_gap_sec: float = 1.0
    capture_delay_sec: float = 0.5
    phash_threshold: int = 6
```

```python
@dataclass
class TranscriptionConfig:
    model_name: str = "large-v3"
    language: str = "ja"
    device: str = "cpu"
    compute_type: str = "int8"
    vad_filter: bool = True
```

```python
@dataclass
class AppConfig:
    output_dir: Path
    enable_ocr: bool = False
    export_md: bool = False
```

---

### `models.py`

中間データ構造を定義する。

最低限以下のモデルが必要。

```python
@dataclass
class TranscriptSegment:
    start: float
    end: float
    text: str
```

```python
@dataclass
class Slide:
    index: int
    start: float
    end: float | None
    image_filename: str
    image_path: str
    transcript: str = ""
    ocr: str = ""
    transcript_segments: list[TranscriptSegment] = field(default_factory=list)
    detection_score: float | None = None
```

```python
@dataclass
class TranscriptDocument:
    meta: dict[str, Any]
    slides: list[Slide]
```

JSONに出すときは `dataclasses.asdict()` などを使ってよい。

---

### `media.py`

動画情報取得を担当する。

責務：

* 動画の存在確認
* duration取得
* fps取得
* frame_count取得
* 任意時刻のフレーム取得
* 秒数とフレーム番号の変換

想定関数：

```python
def get_video_info(video_path: Path) -> VideoInfo:
    ...
```

```python
def read_frame_at(video_path: Path, timestamp_sec: float) -> np.ndarray:
    ...
```

---

### `transcribe.py`

音声文字起こしを担当する。

`faster-whisper` を使う。

想定関数：

```python
def transcribe_video(
    video_path: Path,
    config: TranscriptionConfig,
) -> list[TranscriptSegment]:
    ...
```

実装方針：

* `WhisperModel` を使う
* `language="ja"`
* `vad_filter=True`
* セグメントごとに `start`, `end`, `text` を保存
* textはstripする
* 空文字は除外する
* 例外時はわかりやすくエラーを出す

---

### `slide_detect.py`

スライド切替検出と画像保存を担当する。

基本方針：

* OpenCVで動画を読む
* 1秒に `sample_fps` 回だけフレームを比較する
* 比較にはSSIMを使う
* SSIMがしきい値未満になったらスライド切替候補
* 連続検出を避けるため `min_gap_sec` を設ける
* 切替直後はフェード途中の可能性があるため、検出時刻そのものではなく `capture_delay_sec` 秒後のフレームを保存する
* 直前スライドとpHashが近すぎる場合は重複としてスキップする
* 最初のフレームは必ず `slide_001.png` として保存する

想定関数：

```python
def detect_and_save_slides(
    video_path: Path,
    slides_dir: Path,
    config: SlideDetectionConfig,
) -> list[Slide]:
    ...
```

比較用の前処理：

```python
def preprocess_for_comparison(frame: np.ndarray) -> np.ndarray:
    ...
```

前処理方針：

* 比較用に `640x360` 程度にリサイズ
* グレースケール化
* 必要なら上下左右を少しクロップできるようにする
* マウスカーソルや再生バーの影響を減らすため、将来的にcrop設定を追加できる設計にする

SSIM判定の目安：

```txt
SSIM >= 0.95: ほぼ同じ
SSIM 0.85 - 0.95: 軽微な変化
SSIM < 0.82: スライド切替候補
```

ただししきい値はCLIオプションで変更可能にする。

---

### `ocr.py`

スライド画像OCRを担当する。

想定関数：

```python
def run_ocr_on_image(image_path: Path) -> str:
    ...
```

```python
def attach_ocr_to_slides(slides: list[Slide], enable_ocr: bool) -> list[Slide]:
    ...
```

方針：

* `enable_ocr=False` の場合は何もせず、`ocr=""` のまま返す
* `enable_ocr=True` の場合だけPaddleOCRをimportする
* importできなければ、インストール方法を含めてエラーを出す
* OCR結果は改行区切りのテキストにする
* OCRエンジンは将来的に差し替え可能にする

---

### `assign.py`

文字起こしセグメントを各スライドに割り当てる。

想定関数：

```python
def assign_transcript_to_slides(
    slides: list[Slide],
    segments: list[TranscriptSegment],
    video_duration: float,
) -> list[Slide]:
    ...
```

仕様：

* 各スライドに `end` を設定する

  * 次のスライドの `start` が現在スライドの `end`
  * 最後のスライドの `end` は動画duration
* 各TranscriptSegmentについて、`segment.start` が含まれるスライドに割り当てる
* スライドの `transcript_segments` に格納する
* スライドの `transcript` には該当セグメントのtextを改行結合する

割り当てルール：

```python
slide.start <= segment.start < slide.end
```

境界の発話がズレることは許容する。将来的にセグメントの中央時刻で割り当てるオプションを追加してもよい。

---

### `export_json.py`

`transcript.json` を出力する。

想定関数：

```python
def export_json(document: TranscriptDocument, output_path: Path) -> None:
    ...
```

仕様：

* UTF-8
* `ensure_ascii=False`
* `indent=2`
* パスはPOSIX風の相対パスにする

---

### `export_pdf.py`

NotebookLM投入用PDFを生成する。

想定関数：

```python
def export_notebooklm_pdf(
    document: TranscriptDocument,
    output_path: Path,
    base_dir: Path,
) -> None:
    ...
```

PDFのページ構成：

```txt
Slide 001
Time: 00:00 - 00:42
Image filename: slide_001.png

[スライド画像]

Transcript:
ここでは今回の研究背景について説明します...

OCR:
研究背景
既存研究
課題
```

仕様：

* 1スライド1ページ
* A4縦または16:9スライドに合う横向きページ
* 画像をなるべく大きく配置
* 下部または次の領域にTranscriptとOCRを配置
* テキストが長すぎる場合は複数ページに分けてもよい
* 最初は単純実装でよい
* 日本語フォント問題が出ても、まずは標準フォントで動くことを優先する

注意：

* PDF内には画像だけでなく、transcriptとOCRのテキストを必ず埋め込む
* NotebookLMに読ませる前提なので、画像だけのPDFにはしない

---

### `export_markdown.py`

人間確認用のMarkdownを生成する。

想定関数：

```python
def export_markdown(
    document: TranscriptDocument,
    output_path: Path,
) -> None:
    ...
```

出力形式：

```md
# Presentation Transcript

## Slide 001

Time: 00:00 - 00:42  
Image filename: `slide_001.png`

![Slide 001](slides/slide_001.png)

### Transcript

ここでは今回の研究背景について説明します。

### OCR

研究背景  
既存研究  
課題
```

---

### `pipeline.py`

全体処理をまとめる。

想定関数：

```python
def process_video(
    video_path: Path,
    output_dir: Path,
    app_config: AppConfig,
    transcription_config: TranscriptionConfig,
    slide_config: SlideDetectionConfig,
) -> TranscriptDocument:
    ...
```

責務：

* 出力ディレクトリ作成
* `slides/` ディレクトリ作成
* 動画情報取得
* 文字起こし
* スライド検出
* OCR
* transcript割り当て
* meta作成
* JSON出力
* PDF出力
* Markdown出力
* 進捗ログ表示

---

## 出力ディレクトリ仕様

入力：

```txt
input/presentation.mp4
```

実行：

```bash
slide-scribe process input/presentation.mp4 --output output --export-md
```

出力：

```txt
output/
  transcript.json
  notebooklm_source.pdf
  transcript.md
  slides/
    slide_001.png
    slide_002.png
    slide_003.png
```

---

## `transcript.json` の仕様

以下のようなJSONを出力する。

```json
{
  "meta": {
    "source_video": "input/presentation.mp4",
    "duration": 602.4,
    "fps": 30.0,
    "frame_count": 18072,
    "created_at": "2026-06-30T12:00:00+09:00",
    "transcription": {
      "engine": "faster-whisper",
      "model": "large-v3",
      "language": "ja",
      "device": "cpu",
      "compute_type": "int8"
    },
    "ocr": {
      "enabled": true,
      "engine": "paddleocr"
    },
    "slide_detection": {
      "method": "ssim+phash",
      "sample_fps": 2.0,
      "ssim_threshold": 0.82,
      "min_gap_sec": 1.0,
      "capture_delay_sec": 0.5
    }
  },
  "slides": [
    {
      "index": 1,
      "start": 0.0,
      "end": 42.3,
      "image_filename": "slide_001.png",
      "image_path": "slides/slide_001.png",
      "transcript": "ここでは今回の研究背景について説明します。",
      "ocr": "研究背景\n既存研究\n課題",
      "detection_score": null,
      "transcript_segments": [
        {
          "start": 0.2,
          "end": 7.6,
          "text": "ここでは今回の研究背景について説明します。"
        }
      ]
    }
  ]
}
```

---

## 時刻フォーマット

JSONでは秒数floatを使う。

Markdown/PDFでは以下の形式で表示する。

```txt
00:00
01:23
10:45
01:02:33
```

`utils.py` に以下の関数を作る。

```python
def format_timestamp(seconds: float) -> str:
    ...
```

---

## 実装優先順位

まずはMVPを完成させる。

### Phase 1: MVP

必須：

* CLIで動画を受け取る
* faster-whisperで文字起こし
* OpenCV + SSIMでスライド検出
* スライド画像保存
* transcriptをスライドに割り当て
* `transcript.json` 出力
* `notebooklm_source.pdf` 出力
* `README.md` 作成

OCRはこの段階では空文字でもよい。

### Phase 2: OCR

* `--enable-ocr` でPaddleOCRを有効化
* OCR結果をJSON/PDF/Markdownに入れる
* PaddleOCR未インストール時のエラーを丁寧にする

### Phase 3: 重複除去と調整

* pHashによる重複除去
* crop設定
* SSIMしきい値調整
* スライド内アニメーションの扱い調整

### Phase 4: 品質改善

* テスト追加
* READMEの使用例追加
* サンプルJSON追加
* PDFレイアウト改善
* ログ改善

---

## テスト方針

重い動画処理やWhisper処理はユニットテストしなくてよい。
テストしやすい純粋関数を中心にテストする。

最低限テストするもの：

* `format_timestamp`
* `assign_transcript_to_slides`
* JSON変換
* Markdown出力
* `Slide` / `TranscriptSegment` のdict化

例：

```python
def test_assign_transcript_to_slides():
    slides = [
        Slide(index=1, start=0.0, end=None, image_filename="slide_001.png", image_path="slides/slide_001.png"),
        Slide(index=2, start=10.0, end=None, image_filename="slide_002.png", image_path="slides/slide_002.png"),
    ]
    segments = [
        TranscriptSegment(start=1.0, end=2.0, text="first"),
        TranscriptSegment(start=12.0, end=13.0, text="second"),
    ]

    result = assign_transcript_to_slides(slides, segments, video_duration=20.0)

    assert result[0].transcript == "first"
    assert result[1].transcript == "second"
```

---

## コーディング規約

* 関数には型ヒントを付ける
* ファイルパスは `Path` を使う
* print直書きより `rich.console.Console` やloggerを使う
* 例外は握りつぶさない
* 動画ファイルが存在しない場合は早めに終了
* 出力ディレクトリは自動作成
* 既存出力がある場合は上書きしてよい
* 最初から過剰な抽象化はしない
* ただし、OCR・文字起こし・スライド検出・出力処理は必ず分離する

---

## `.gitignore`

以下を含める。

```gitignore
.venv/
__pycache__/
*.pyc
.pytest_cache/
.mypy_cache/
.ruff_cache/

output/
dist/
build/
*.egg-info/

.DS_Store
```

動画ファイルや生成物は基本的にgit管理しない。

---

## READMEに書く内容

READMEには以下を含める。

````md
# slide-scribe

プレゼン動画からスライド画像、文字起こし、OCR、NotebookLM用PDFを生成するPython CLIツール。

## Features

- Extract slide images from presentation videos
- Transcribe speech using faster-whisper
- Assign transcript segments to each slide
- Optionally run OCR on slide images
- Export transcript.json
- Export NotebookLM-friendly PDF
- Optionally export Markdown

## Installation

```bash
pip install -e .
````

## Usage

```bash
slide-scribe process input/presentation.mp4 --output output --export-md
```

OCRを使う場合：

```bash
slide-scribe process input/presentation.mp4 --output output --enable-ocr
```

## Output

```txt
output/
  transcript.json
  notebooklm_source.pdf
  transcript.md
  slides/
    slide_001.png
    slide_002.png
```

## Notes

OCRはoptionalです。PaddleOCRが未インストールの場合は `--enable-ocr` を使わなければ処理できます。

````

---

## `pyproject.toml` の方針

最低限以下の依存関係を入れる。

```toml
[project]
name = "slide-scribe"
version = "0.1.0"
description = "Extract slides, transcripts, OCR text, and NotebookLM-friendly PDFs from presentation videos."
requires-python = ">=3.11"
dependencies = [
    "typer>=0.12",
    "rich>=13.0",
    "opencv-python>=4.8",
    "scikit-image>=0.22",
    "Pillow>=10.0",
    "imagehash>=4.3",
    "faster-whisper>=1.0",
    "pymupdf>=1.24"
]

[project.optional-dependencies]
ocr = [
    "paddleocr>=2.8"
]
dev = [
    "pytest>=8.0",
    "ruff>=0.5",
    "mypy>=1.10"
]

[project.scripts]
slide-scribe = "slide_scribe.cli:app"
````

---

## 重要な実装上の注意

### 1. OCRは必須にしない

PaddleOCRは環境構築で詰まりやすいので、デフォルトではOFFにする。

### 2. MarkdownよりJSONを中心にする

Markdownは派生出力。
JSONを壊さないことを最優先にする。

### 3. NotebookLM用PDFは画像だけにしない

PDFには必ず以下を含める。

* スライド画像
* 画像ファイル名
* transcript
* OCR

### 4. スライド検出は完璧を狙わない

初期実装では、以下で十分。

* SSIMで大きな変化を検出
* `min_gap_sec` で連続誤検出を抑制
* `capture_delay_sec` で切替後の安定したフレームを保存
* pHashで重複除去

### 5. 日本語前提

文字起こしは日本語を主対象にする。
ただし `--language en` などで変更できるようにする。

---

## 最終的にCodexにやってほしいこと

この仕様に従って、Pythonリポジトリを構成・実装してください。

まずはPhase 1のMVPを優先してください。

必須成果物：

* `pyproject.toml`
* `README.md`
* `src/slide_scribe/` 以下の実装
* CLI `slide-scribe process`
* `transcript.json` 出力
* `notebooklm_source.pdf` 出力
* 任意の `transcript.md` 出力
* 基本的なユニットテスト

実装後、以下のコマンドで動くようにしてください。

```bash
pip install -e ".[dev]"
slide-scribe process input/presentation.mp4 --output output --export-md
```

OCR込みの場合は以下。

```bash
pip install -e ".[ocr,dev]"
slide-scribe process input/presentation.mp4 --output output --export-md --enable-ocr
```

まずは堅実に動くMVPを作り、凝った最適化や高度な画像認識は後回しにしてください。

