# JSON仕様

`動画ファイル名.json` は以下のトップレベル構造を持ちます。

```json
{
  "meta": {},
  "slides": []
}
```

## meta

- `source_video`: 入力動画パス
- `duration`: 動画秒数
- `fps`: 動画FPS
- `frame_count`: フレーム数
- `created_at`: 生成日時
- `transcription`: 文字起こし設定
- `ocr`: OCR設定
- `slide_detection`: スライド検出設定

## slides

- `index`: 1始まりのスライド番号
- `start`: スライド開始秒
- `end`: スライド終了秒
- `image_filename`: `動画ファイル名_ページ番号.png` 形式の画像ファイル名
- `image_path`: 出力ディレクトリからの相対パス
- `transcript`: スライドに割り当てられた文字起こし
- `ocr`: OCRテキスト
- `transcript_segments`: 元の文字起こしセグメント配列
- `detection_score`: スライド検出時のSSIM値
