# アーキテクチャ

`slide-scribe` は、プレゼン動画をNotebookLMやLLMに読み込ませやすい資料へ変換するためのCLIです。

処理順序は以下です。

```txt
動画
  ↓
音声文字起こし
  ↓
スライド切替検出
  ↓
スライド画像保存
  ↓
任意OCR
  ↓
文字起こし割り当て
  ↓
JSON、PDF、任意Markdown出力
```

正本は `動画ファイル名.json` です。PDFとMarkdownはJSONから派生する確認・投入用成果物として扱います。

## モジュール

- `cli.py`: コマンドライン入口
- `config.py`: 設定値
- `models.py`: 中間データ構造
- `media.py`: 動画情報とフレーム読み取り
- `transcribe.py`: `faster-whisper` または `mlx-whisper` による文字起こし
- `slide_detect.py`: SSIMとpHashによるスライド検出
- `ocr.py`: 任意OCR
- `assign.py`: 発話セグメントのスライド割り当て
- `export_json.py`: JSON出力
- `export_pdf.py`: NotebookLM用PDF出力
- `export_markdown.py`: 人間確認用Markdown出力
- `pipeline.py`: 全体処理
