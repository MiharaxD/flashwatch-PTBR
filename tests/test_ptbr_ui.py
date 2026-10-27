"""Render every Brazilian guide/control page and verify canonical UI values."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import _bootstrap  # noqa: F401
from pathlib import Path
import tempfile
import time
import unittest

from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

import i18n
from onboarding import LANGUAGES, LanguageScreen, Onboarding, STEPS
from ptbr_assets import load_assets
from settings import Settings
from ui import ControlWindow
from overlay import Overlay
from timer_manager import ActiveTimer


class BrazilianUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.output = Path(__file__).resolve().parents[1] / "build/ptbr-ui"
        cls.output.mkdir(parents=True, exist_ok=True)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.settings = Settings(Path(self.temp.name) / "settings.json")
        self.settings.set("locale", "pt_BR")
        i18n.set_language("pt_BR")
        self.assets, _ = load_assets()

    def tearDown(self):
        i18n.set_language(i18n.ENGLISH)
        self.temp.cleanup()

    def test_control_and_canonical_roles(self):
        window = ControlWindow(self.settings, self.assets)
        self.assertEqual(window.combo_language.count(), 3)
        self.assertEqual(window.combo_language.currentData(), i18n.PORTUGUESE)
        self.assertEqual(window.check_visible.text(), "Mostrar overlay")
        changes = []
        window.sync_team(["Ahri"], lambda cid, role: changes.append((cid, role)))
        box = window._role_combos["Ahri"]
        box.setCurrentIndex(box.findData("JUNGLE"))
        self.assertEqual(box.currentText(), "SELVA")
        self.assertEqual(changes, [("Ahri", "JUNGLE")])
        window.set_role_display("Ahri", "SUPPORT")
        self.assertEqual(box.currentData(), "SUPPORT")
        self.assertEqual(box.currentText(), "SUPORTE")
        self.assertEqual(len(changes), 1)
        for index in range(window.stack.count()):
            window.stack.setCurrentIndex(index)
            self.app.processEvents()
            image = QPixmap(window.size())
            window.render(image)
            self.assertFalse(image.isNull())
            self.assertTrue(image.save(str(self.output / f"control-{index}.png")))
        announced = []
        window.language_changed.connect(announced.append)
        for lang in LANGUAGES:
            window.combo_language.setCurrentIndex(window.combo_language.findData(lang))
            self.assertEqual(self.settings.get("locale"), i18n.locale_for(lang))
        self.assertEqual(announced, list(LANGUAGES))
        window.deleteLater()
        self.app.processEvents()

    def test_guide_pages_and_language_cards(self):
        guide = Onboarding(self.settings)
        cards = LanguageScreen._cards()
        self.assertEqual([code for code, _ in cards], list(LANGUAGES))
        for i, (_, card) in enumerate(cards):
            self.assertLessEqual(card.right(), 1442.001)
            for _, other in cards[i + 1:]:
                self.assertFalse(card.intersects(other))
        picked = []
        guide.language_changed.connect(picked.append)
        for lang in (i18n.ENGLISH, i18n.FRENCH, i18n.PORTUGUESE):
            guide.pick_language(lang)
            i18n.set_language(lang)
            guide.retranslate()
            self.assertEqual(guide.current_language(), lang)
        self.assertEqual(picked, [i18n.ENGLISH, i18n.FRENCH, i18n.PORTUGUESE])
        self.assertEqual(Settings(self.settings._path).get("locale"), "pt_BR")
        for index, step in enumerate(STEPS):
            guide.show_step(index)
            guide._slide_motion.stop()
            guide._fade_motion.stop()
            guide._reveal_motion.stop()
            guide.slide, guide.fade, guide.reveal = 0, 1, 1
            self.app.processEvents()
            image = QPixmap(guide.size())
            guide.render(image)
            self.assertFalse(image.isNull())
            self.assertTrue(image.save(str(self.output / f"guide-{index}-{step}.png")))
        guide._loop.stop()
        guide.deleteLater()
        self.app.processEvents()

    def test_default_countdown_legibility_at_1080p_and_1440p(self):
        self.assertEqual(self.settings.get("timer_font_scale"), 1.5)
        widget = Overlay(self.settings, self.assets)
        now = time.monotonic()
        widget.set_timers([
            ActiveTimer("Ahri", "Ahri", "summoner", "Flash", "Flash", 300, now - 37),
            ActiveTimer("Lux", "Lux", "summoner", "Exhaust", "Exaustão", 240, now - 120),
        ])
        for screen_width, screen_height in ((1920, 1080), (2560, 1440)):
            widget.resize(round(screen_width * .30), 58)
            image = QPixmap(widget.size())
            image.fill(Qt.transparent)
            widget.render(image)
            metrics = widget._bar_metrics(1.0, vertical=False)
            self.assertGreaterEqual(metrics["text"], 16)
            for marker in widget._bar_markers(1.0):
                self.assertGreaterEqual(marker.text.height(), metrics["text"])
                self.assertLessEqual(marker.text.bottom(), widget.height())
            self.assertTrue(image.save(str(self.output / f"bar-{screen_width}x{screen_height}.png")))
        # Loading a saved preference must not replace a size the user selected.
        self.settings.set("timer_font_scale", .9)
        self.assertEqual(Settings(self.settings._path).get("timer_font_scale"), .9)
        widget.deleteLater()
        self.app.processEvents()


if __name__ == "__main__":
    unittest.main(verbosity=2)
