from pathlib import Path

from slide_scribe.ocr import _run_reader


class PredictReader:
    def predict(self, image_path: str):
        return [
            {
                "res": {
                    "input_path": image_path,
                    "rec_texts": ["見出し", "本文"],
                    "rec_scores": [0.99, 0.95],
                }
            }
        ]


class LegacyReader:
    def ocr(self, image_path: str):
        return [
            [
                [None, ("一行目", 0.99)],
                [None, ("二行目", 0.95)],
            ]
        ]


def test_run_reader_collects_paddleocr_v3_predict_result(tmp_path: Path) -> None:
    image_path = tmp_path / "slide.png"
    image_path.write_bytes(b"fake")

    assert _run_reader(PredictReader(), image_path) == "見出し\n本文"


def test_run_reader_collects_legacy_ocr_result(tmp_path: Path) -> None:
    image_path = tmp_path / "slide.png"
    image_path.write_bytes(b"fake")

    assert _run_reader(LegacyReader(), image_path) == "一行目\n二行目"
