"""Synthetic PT-BR pixels through the unchanged detector, OCR and parser.

These generated frames are NOT Brazilian game captures. The shipped real English
capture is exercised separately with Brazilian data to retain that regression.
"""
import _bootstrap  # noqa: F401
import json
from pathlib import Path
import unittest

import chat_detector
import cv2
from message_parser import MessageParser, looks_like_chat_line
from ocr import OcrEngine
from ptbr_assets import load_assets
import self_test
from synthetic_frames import make_frame


class BrazilianOCR(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.assets, _ = load_assets()
        cls.engine = OcrEngine()
        cls.engine.load()
        cls.output = Path(__file__).resolve().parents[1] / "build/ptbr-ocr"
        cls.output.mkdir(parents=True, exist_ok=True)

    def test_synthetic_frames(self):
        lines = [
            "(12:04) Ahri usou Flash",
            f"(12:31) Darius usou {self.assets.spells['Teleport'].name}",
            f"(13:02) Viego usou {self.assets.spells['Smite'].name}",
            "Jogador (Jinx): top sem flash",
            f"(13:40) Lux usou {self.assets.spells['Exhaust'].name}",
        ]
        expected = {("Ahri", "Flash"), ("Darius", "Teleport"), ("Viego", "Smite"), ("Lux", "Exhaust")}
        for width, height, panel, opacity, clutter in (
                (1920, 1080, True, 1, True), (2560, 1440, True, 1, True),
                (3840, 2160, True, 1, True), (1920, 1080, False, .82, True),
                (1920, 1080, False, .60, False)):
            with self.subTest(resolution=(width, height), panel=panel):
                frame, _ = make_frame(width, height, lines=lines, panel=panel,
                                      text_opacity=opacity, clutter=clutter)
                explore = chat_detector.explore_region((0, 0, width, height))
                band = frame[explore.y:explore.y + explore.height, explore.x:explore.x + explore.width]
                rows, _ = self.engine.read_rows(band, max_rows=chat_detector.EXPLORE_MAX_ROWS,
                                               left_fraction=chat_detector.EXPLORE_LEFT_FRACTION)
                boxes = [box for text, box in rows if looks_like_chat_line(text)]
                region = chat_detector.region_from_chat_rows(boxes, (explore.x, explore.y), (0, 0, width, height))
                self.assertIsNotNone(region)
                crop = frame[region.y:region.y + region.height, region.x:region.x + region.width]
                read, ms = self.engine.read_lines(crop)
                events = MessageParser(self.assets).parse_lines(read)
                actual = {(e.champion_id, e.spell_key) for e in events}
                stem = f"synthetic-{width}-{panel}-{clutter}"
                cv2.imencode('.png', crop)[1].tofile(self.output / f"{stem}.png")
                (self.output / f"{stem}.json").write_text(json.dumps({"source": "synthetic",
                    "lines": read, "ms": ms, "events": sorted(actual)}, ensure_ascii=False, indent=2), "utf-8")
                if not panel and clutter:
                    # Physical overlap can erase glyphs in a single frame. The
                    # existing pipeline re-reads later. Require useful output
                    # and no wrong champion/spell rather than inventing a cast.
                    self.assertTrue(actual, read)
                    self.assertLessEqual(actual, expected, read)
                else:
                    self.assertEqual(actual, expected, read)

    def test_real_english_sample_with_brazilian_assets(self):
        self.assertEqual(self_test.load_manifest()["locale"], "en_US")
        result = self_test.run(self.engine, self.assets)
        self.assertTrue(result.ok, (result.error, result.lines, result.missing))
        self.assertTrue(result.events)
        for event in result.events:
            expected_name = (self.assets.champions[event.champion_id].ultimate.name
                             if event.is_ultimate else self.assets.spells[event.spell_key].name)
            self.assertEqual(event.spell_name, expected_name)

    def test_user_brazilian_capture_ultimate_key(self):
        # Read the supplied file only. Never connect to or capture a live game.
        path = Path(__file__).parent / "fixtures/pt_BR/client-ultimate.png"
        import numpy as np
        frame = cv2.imdecode(np.frombuffer(path.read_bytes(), dtype=np.uint8), cv2.IMREAD_COLOR)
        self.assertIsNotNone(frame)
        manifest = json.loads(path.with_suffix(".json").read_text("utf-8"))
        import hashlib
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), manifest["sha256"])
        # A human-annotated chat rectangle, matching the app's existing manual
        # framing path. Automatic framing on this screenshot chose a wrong
        # region; this test makes no claim about automatic region detection.
        x, y, width, height = manifest["manual_chat_region"]
        crop = frame[y:y + height, x:x + width]
        lines, ms = self.engine.read_lines(crop)
        events = MessageParser(self.assets).parse_lines(lines)
        (self.output / "real-client-ultimate.json").write_text(json.dumps({
            "source": "user_game_capture", "image": path.name, "lines": lines,
            "ms": ms, "events": [{"champion": e.champion_id, "spell": e.spell_key,
                                    "time": e.game_time, "certain": e.certain} for e in events],
        }, ensure_ascii=False, indent=2), "utf-8")
        ultimates = [e for e in events if e.kind == "ultimate"]
        self.assertTrue(ultimates, lines)
        self.assertTrue(all(e.champion_id == "Nasus" and e.spell_key == "ULT"
                            and not e.certain for e in ultimates))
        self.assertTrue(all(e.game_time in {62, 429, 434, 464} for e in ultimates), lines)
        self.assertFalse(any(e.champion_id == "Kayn" for e in events), lines)


if __name__ == "__main__":
    unittest.main(verbosity=2)
