"""Fixed cards survive ready-timer cleanup. Entirely offline/offscreen."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import _bootstrap  # noqa: F401
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication

import i18n
from message_parser import MessageParser
from overlay import Overlay, paint_card_cooldown_mask
from ptbr_assets import load_assets
from settings import Settings, SPELL_ICON_DIR
from theme import menu_family
from timer_manager import TimerManager


class PersistentCards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        menu_family()
        cls.output = Path(__file__).resolve().parents[1] / "build/persistent-cards"
        cls.output.mkdir(parents=True, exist_ok=True)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.settings = Settings(Path(self.temp.name) / "settings.json")
        self.settings.update({"locale": "pt_BR", "overlay_layout": "cards",
                              "hide_until_in_game": False, "theme": "dark"}, save=False)
        self.assets, _ = load_assets()
        for champion in self.assets.champions.values():
            champion.ultimate.icon_path = SPELL_ICON_DIR / f"{champion.ultimate.ddragon_id}.png"
        i18n.set_language("pt_BR")
        self.parser = MessageParser(self.assets)
        self.manager = TimerManager(self.assets, self.settings)
        self.clock_patch = patch("timer_manager.time.monotonic", return_value=1000.0)
        self.clock = self.clock_patch.start()
        self.widget = Overlay(self.settings, self.assets)
        self.widget.resize(250, 135)

    def tearDown(self):
        self.widget.deleteLater()
        self.app.processEvents()
        self.clock_patch.stop()
        self.temp.cleanup()
        i18n.set_language(i18n.ENGLISH)

    def casts(self):
        events = self.parser.parse_lines(["Dr. Mundo usou R", "Dr. Mundo usou Flash",
                                          "Dr. Mundo usou Fantasma"])
        self.assertEqual(len(events), 3)
        self.manager.handle_events(events, force=True)
        self.assertEqual(self.manager.active_count(), 3)

    def expire(self):
        self.clock.return_value += max(t.duration for t in self.manager.snapshot()) + 61
        return self.manager.tick()

    def test_card_and_all_known_icons_remain_after_real_purge_without_alert_replay(self):
        self.casts()
        self.widget.set_timers(self.manager.snapshot(keep_ready=True))
        notifications = self.expire()
        self.assertEqual([note.kind for note in notifications], ["ready"] * 3)
        self.assertEqual(self.manager.active_count(), 0)
        self.assertEqual(self.manager._timers, {})
        self.assertEqual(self.manager.snapshot(), [])
        self.clock.return_value += 3600
        self.assertEqual(self.manager.tick(), [])
        records = self.manager.snapshot(keep_ready=True)
        self.assertEqual(len(records), 3)
        self.assertTrue(all(t.is_ready() for t in records))
        self.widget.set_timers(records)
        slots = self.widget._card_slots(1.0)
        self.assertEqual(len(slots), 1)
        self.assertEqual([cell.timer.spell_key for cell in slots[0].spells], ["ULT", "Flash", "Ghost"])
        with patch.object(self.widget, "_paint_countdown", wraps=self.widget._paint_countdown) as counts, \
                patch("overlay.paint_card_cooldown_mask", wraps=paint_card_cooldown_mask) as masks:
            image = QPixmap(self.widget.size())
            image.fill(Qt.transparent)
            self.widget.render(image)
        self.assertEqual(counts.call_count, 0)
        self.assertEqual(masks.call_count, 0)
        self.assertTrue(image.save(str(self.output / "all-ready-after-one-hour.png")))

    def test_hide_ready_and_linger_still_apply_to_regular_snapshot_only(self):
        self.casts()
        self.expire()
        for hide in (True, False):
            for linger in (0, 5, 60):
                with self.subTest(hide=hide, linger=linger):
                    self.settings.update({"hide_ready_entries": hide,
                                          "ready_linger_seconds": linger}, save=False)
                    self.assertEqual(self.manager.snapshot(), [])
                    self.assertEqual(len(self.manager.snapshot(keep_ready=True)), 3)

    def test_new_cast_replaces_finished_record_without_duplicate_or_old_duration(self):
        self.casts()
        self.expire()
        previous = next(t for t in self.manager.snapshot(keep_ready=True) if t.spell_key == "Flash")
        event = self.parser.parse_line("Dr. Mundo usou Flash")
        self.manager.handle_events([event], force=True)
        records = self.manager.snapshot(keep_ready=True)
        current = next(t for t in records if t.spell_key == "Flash")
        self.assertEqual(len(records), 3)
        self.assertIsNot(current, previous)
        self.assertFalse(current.is_ready())
        self.assertEqual(self.manager.active_count(), 1)
        self.assertEqual(self.manager.snapshot(), [current])

    def test_reset_clears_finished_cards_for_every_session_reset_reason(self):
        for reason in ("manual reset", "session changed", "language changed"):
            with self.subTest(reason=reason):
                self.casts()
                self.expire()
                self.assertEqual(len(self.manager.snapshot(keep_ready=True)), 3)
                self.manager.reset(reason=reason)
                self.assertEqual(self.manager.snapshot(keep_ready=True), [])
                self.widget.set_timers(self.manager.snapshot(keep_ready=True))
                self.assertEqual(self.widget._card_slots(1.0), [])

    def test_clear_demo_removes_finished_demo_cards_but_keeps_real_champion(self):
        self.casts()
        self.manager.add_demo(first=True)
        self.expire()
        self.assertGreater(len(self.manager.snapshot(keep_ready=True)), 3)
        self.manager.clear_demo()
        self.assertEqual({t.champion_id for t in self.manager.snapshot(keep_ready=True)}, {"DrMundo"})
        self.assertEqual(len(self.manager.snapshot(keep_ready=True)), 3)

    def test_role_correction_updates_finished_card_records(self):
        self.casts()
        self.expire()
        self.manager.set_role("DrMundo", "TOP")
        self.assertEqual({t.role for t in self.manager.snapshot(keep_ready=True)}, {"TOP"})

    def test_confirmed_clock_restart_also_discards_previous_match_cards(self):
        self.casts()
        self.expire()
        self.manager._clock_ref = (1200, self.clock.return_value)
        self.assertFalse(self.manager._update_clock(30))
        self.clock.return_value += 1
        self.assertTrue(self.manager._update_clock(31))
        self.assertEqual(self.manager.snapshot(keep_ready=True), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
