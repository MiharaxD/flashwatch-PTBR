"""Champion-grouped fixed cards. Offscreen only; no game/desktop capture."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import _bootstrap  # noqa: F401
from dataclasses import asdict
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QApplication

import i18n
from overlay import (Overlay, LAYOUT_BAR, LAYOUT_CARDS, LAYOUT_LIST,
                     paint_card_cooldown_mask)
from ptbr_assets import load_assets
from settings import Settings, SPELL_ICON_DIR
from timer_manager import ActiveTimer
from theme import menu_family


class ChampionCards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        menu_family()       # load bundled font on the offscreen Qt backend
        cls.output = Path(__file__).resolve().parents[1] / "build/champion-cards-icons"
        cls.output.mkdir(parents=True, exist_ok=True)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.settings = Settings(Path(self.temp.name) / "settings.json")
        self.settings.update({"locale": "pt_BR", "overlay_layout": LAYOUT_CARDS,
                              "hide_until_in_game": False}, save=False)
        i18n.set_language("pt_BR")
        self.assets, _ = load_assets()
        for champion in self.assets.champions.values():
            champion.ultimate.icon_path = SPELL_ICON_DIR / f"{champion.ultimate.ddragon_id}.png"
        self.widget = Overlay(self.settings, self.assets)

    def tearDown(self):
        self.widget.deleteLater()
        self.app.processEvents()
        i18n.set_language(i18n.ENGLISH)
        self.temp.cleanup()

    def timer(self, cid, key, left, *, uncertain=False):
        champion = self.assets.champions[cid]
        ultimate = key == "ULT"
        return ActiveTimer(cid, champion.name, "ultimate" if ultimate else "summoner", key,
                           champion.ultimate.name if ultimate else self.assets.spells[key].name,
                           300, time.monotonic() - (300 - left),
                           approximate=ultimate, uncertain=uncertain)

    def render(self, name):
        image = QPixmap(self.widget.size())
        image.fill(Qt.transparent)
        self.widget.render(image)
        self.assertTrue(image.save(str(self.output / name)))
        return image

    def test_one_portrait_with_three_timers_and_no_state_changes(self):
        timers = [self.timer("DrMundo", "Ghost", 232), self.timer("DrMundo", "ULT", 103),
                  self.timer("DrMundo", "Flash", 105, uncertain=True)]
        before = [asdict(timer) for timer in timers]
        self.widget.set_timers(timers)
        self.widget.resize(260, 180)
        slots = self.widget._card_slots(1.0)
        self.assertEqual(len(slots), 1)
        self.assertEqual([row.timer.spell_key for row in slots[0].spells], ["ULT", "Flash", "Ghost"])
        cells = slots[0].spells
        self.assertEqual(len({cell.badge.top() for cell in cells}), 1)
        self.assertTrue(cells[0].badge.center().x() < cells[1].badge.center().x() < cells[2].badge.center().x())
        for cell in cells:
            self.assertGreater(cell.text.top(), cell.badge.bottom())
            self.assertLessEqual(abs(cell.text.center().x() - cell.badge.center().x()), 1)
        with patch.object(self.widget, "_paint_portrait", wraps=self.widget._paint_portrait) as portraits:
            with patch("overlay.paint_card_cooldown_mask", wraps=paint_card_cooldown_mask) as masks:
                self.render("mundo.png")
        self.assertEqual(portraits.call_count, 1)
        self.assertEqual(masks.call_count, 3)
        self.assertEqual([asdict(timer) for timer in timers], before)
        self.settings.set("theme", "dark", save=False)
        self.render("mundo-dark.png")

    def test_unobserved_slots_assume_ready_without_timers_and_order_stays_stable(self):
        flash = self.timer("DrMundo", "Flash", 105)
        self.widget.set_timers([flash])
        self.widget.resize(260, 150)
        rows = self.widget._card_slots(1.0)[0].spells
        self.assertIsNone(rows[0].timer)
        self.assertIs(rows[1].timer, flash)
        self.assertIsNone(rows[2].timer)
        before = asdict(flash)
        with patch.object(self.widget, "_paint_countdown", wraps=self.widget._paint_countdown) as counts, \
                patch("overlay.paint_card_cooldown_mask", wraps=paint_card_cooldown_mask) as masks:
            self.render("assumed-ready.png")
        self.assertEqual(masks.call_count, 1)
        self.assertEqual(counts.call_count, 1)
        self.assertNotIn(i18n.tr("overlay.ready"), [call.args[3] for call in counts.call_args_list])
        self.assertEqual(self.widget._timers, [flash])
        self.assertEqual(asdict(flash), before)
        ghost = self.timer("DrMundo", "Ghost", 1)
        self.widget.set_timers([ghost, flash])
        self.assertEqual([r.timer.spell_key for r in self.widget._card_slots(1.0)[0].spells[1:]],
                         ["Flash", "Ghost"])
        self.widget.set_timers([flash, ghost])
        self.assertEqual([r.timer.spell_key for r in self.widget._card_slots(1.0)[0].spells[1:]],
                         ["Flash", "Ghost"])
        self.widget.set_timers([ghost])
        reserved = self.widget._card_slots(1.0)[0].spells
        self.assertIsNone(reserved[1].timer)
        self.assertIs(reserved[2].timer, ghost)

    def test_observed_ready_has_normal_icon_and_no_label_in_every_language(self):
        expired = self.timer("DrMundo", "Ghost", 0)
        self.widget.set_timers([expired])
        self.widget.resize(200, 135)
        for locale in ("pt_BR", "en_US", "fr_FR"):
            i18n.set_language(locale)
            self.assertEqual(expired.display(), i18n.tr("overlay.ready"))
            self.assertEqual(self.widget._card_display(expired), "")
            with patch.object(self.widget, "_paint_countdown", wraps=self.widget._paint_countdown) as counts, \
                    patch("overlay.paint_card_cooldown_mask", wraps=paint_card_cooldown_mask) as masks:
                self.render(f"ready-{locale}.png")
            self.assertEqual(masks.call_count, 0)
            self.assertEqual(counts.call_count, 0)
            self.assertEqual(self.widget._timers, [expired])

    def test_cooldown_mask_is_translucent_with_visible_x_and_clipped_to_icon(self):
        base = QColor(220, 80, 30)
        image = QPixmap(32, 40)
        image.fill(base)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing, True)
        paint_card_cooldown_mask(painter, QRect(4, 4, 24, 24), 1.0)
        painter.end()
        pixels = image.toImage()
        shaded = pixels.pixelColor(7, 16)
        self.assertLess(shaded.red(), base.red())
        self.assertGreater(shaded.red(), 105)  # original icon still contributes
        self.assertGreater(shaded.blue(), base.blue())
        self.assertLess(shaded.blue(), 118)
        cross = pixels.pixelColor(16, 16)
        self.assertTrue(min(cross.red(), cross.green(), cross.blue()) > 210)
        for point in ((4, 4), (1, 16), (16, 32)):
            self.assertEqual(pixels.pixelColor(*point), base)
        self.assertTrue(image.save(str(self.output / "mask-pixels.png")))

    def test_five_champions_fit_at_1080p_and_1440p(self):
        ids = ["DrMundo", "Viego", "Ahri", "Jinx", "Thresh"]
        self.widget.set_timers([self.timer(cid, key, left, uncertain=(key == "Flash"))
                                for cid in ids for key, left in (("ULT", 103), ("Flash", 105), ("Ghost", 232))])
        for width in (1920, 2560):
            self.widget.resize(round(width * .56), 128)
            for theme in ("light", "dark", "neon"):
                self.settings.set("theme", theme, save=False)
                self.render(f"five-{width}-{theme}.png")
                slots = self.widget._card_slots(1.0)
                self.assertEqual(len(slots), 5)
                self.assertEqual(len({s.timer.champion_id for s in slots}), 5)
                for index, slot in enumerate(slots):
                    self.assertTrue(self.widget.rect().contains(slot.rect))
                    for other in slots[index + 1:]:
                        self.assertFalse(slot.rect.intersects(other.rect))
                    for row in slot.spells:
                        self.assertTrue(slot.rect.contains(row.badge))
                        self.assertTrue(slot.rect.contains(row.text))
                        self.assertFalse(row.badge.intersects(row.text))
                        self.assertGreater(row.text.top(), row.badge.bottom())
                    for cell_index, first in enumerate(slot.spells):
                        for second in slot.spells[cell_index + 1:]:
                            self.assertFalse(first.text.intersects(second.text))
                            self.assertFalse(first.badge.intersects(second.badge))

    def test_extra_summoners_and_large_fonts_are_not_dropped_within_a_card(self):
        for scale in (.6, 1.0, 2.0):
            self.settings.set("overlay_scale", scale, save=False)
            self.settings.set("timer_font_scale", 2.0, save=False)
            self.widget.sync_countdown_style()
            self.widget.set_timers([self.timer("DrMundo", key, 50) for key in ("ULT", "Flash", "Ghost", "Teleport")])
            self.widget.resize(500, 46)
            self.render(f"extra-{scale}.png")
            slots = self.widget._card_slots(scale)
            self.assertEqual(len(slots), 1)
            self.assertEqual(len(slots[0].spells), 4)
            self.assertTrue(all(row.timer is not None for row in slots[0].spells))
            self.assertTrue(all(slots[0].rect.contains(row.text) for row in slots[0].spells))

    def test_bar_and_list_keep_one_entry_per_timer(self):
        timers = [self.timer("DrMundo", key, 0 if key == "Ghost" else 70)
                  for key in ("ULT", "Flash", "Ghost")]
        self.widget.set_timers(timers)
        for layout in (LAYOUT_BAR, LAYOUT_LIST):
            self.settings.set("overlay_layout", layout, save=False)
            self.widget.sync_layout()
            self.widget.resize(600, 300)
            with patch.object(self.widget, "_paint_countdown", wraps=self.widget._paint_countdown) as countdowns, \
                    patch("overlay.paint_card_cooldown_mask", wraps=paint_card_cooldown_mask) as masks:
                self.render(f"unchanged-{layout}.png")
            self.assertEqual(countdowns.call_count, 3)
            self.assertEqual(masks.call_count, 0)
            self.assertIn(i18n.tr("overlay.ready"), [call.args[3] for call in countdowns.call_args_list])
            self.assertEqual(len(self.widget._timers), 3)

    def test_cards_preview_in_control_and_every_guide_step(self):
        from onboarding import Onboarding, STEPS
        from ui import ControlWindow
        window = ControlWindow(self.settings, self.assets)
        window.go_to_display_page()
        image = QPixmap(window.size())
        window.render(image)
        self.assertTrue(image.save(str(self.output / "control-cards.png")))
        guide = Onboarding(self.settings)
        for index, step in enumerate(STEPS):
            guide.show_step(index)
            guide._slide_motion.stop()
            guide._fade_motion.stop()
            guide._reveal_motion.stop()
            guide.slide, guide.fade, guide.reveal = 0, 1, 1
            self.app.processEvents()
            image = QPixmap(guide.size())
            guide.render(image)
            self.assertTrue(image.save(str(self.output / f"guide-{step}.png")))
        guide._loop.stop()
        guide.deleteLater()
        window.deleteLater()
        self.app.processEvents()


if __name__ == "__main__":
    unittest.main(verbosity=2)
