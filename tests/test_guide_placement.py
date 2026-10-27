"""Guide placement with simulated match state. Never opens/captures a game."""
import _bootstrap  # noqa: F401
from pathlib import Path
import queue
import tempfile
import time
import unittest
from unittest.mock import Mock

from main import Application
from message_parser import MessageParser
from ocr import PipelineStatus
from ptbr_assets import load_assets
from settings import Settings
from timer_manager import TimerManager


class GuidePlacement(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        app = Application.__new__(Application)
        self.app = app
        app.settings = Settings(Path(self.temp.name) / "settings.json")
        app.assets, _ = load_assets()
        app.timers = TimerManager(app.assets, app.settings)
        app.overlay = Mock()
        app.control = Mock()
        app.control.isVisible.return_value = False
        app.tray = Mock()
        app.action_lock = Mock()
        app.action_overlay = Mock()
        app.action_demo = Mock()
        app.demo_timer = Mock()
        app.notifier = Mock()
        app.worker = None
        app.zone_frames = {}
        app.results = queue.Queue()
        app._known_champions = set()
        app._applied_roles = {}
        app._demo = False
        app._placing_live_overlay = False
        app._latest_status = PipelineStatus(in_game=True)
        app._boot_message = ""
        app._show_control = Mock()

    def tearDown(self):
        self.temp.cleanup()

    def test_placing_in_existing_game_stays_visible_and_preserves_real_timers(self):
        app = self.app
        parser = MessageParser(app.assets)
        app.timers.handle_events([parser.parse_line("Ahri usou Flash"),
                                  parser.parse_line("Nasus usou R")], force=True)
        before = {timer.key: timer for timer in app.timers.snapshot()}
        self.assertEqual(len(before), 2)
        app._on_place_overlay()
        for _ in range(20):
            app._refresh_ui()
        self.assertFalse(app.settings.get("overlay_locked"))
        self.assertFalse(app._demo)
        self.assertTrue(app._placing_live_overlay)
        self.assertEqual({timer.key: timer for timer in app.timers.snapshot()}, before)
        app.overlay.raise_.assert_called_once()
        app.overlay.apply_lock.assert_called_with(False)
        app.tray.showMessage.assert_not_called()
        app.demo_timer.start.assert_not_called()

    def test_new_game_still_ends_offline_placement_and_restores_click_through(self):
        app = self.app
        app._latest_status.in_game = False
        app._on_place_overlay()
        self.assertTrue(app._demo)
        self.assertFalse(app.settings.get("overlay_locked"))
        app._latest_status.in_game = True
        app._refresh_ui()
        self.assertFalse(app._demo)
        self.assertTrue(app.settings.get("overlay_locked"))
        app.tray.showMessage.assert_called_once()

    def test_finishing_guide_locks_live_placement(self):
        app = self.app
        app._on_place_overlay()
        app._on_guide_finished()
        self.assertTrue(app.settings.get("overlay_locked"))
        self.assertFalse(app._placing_live_overlay)
        app._show_control.assert_called_once()
        app.tray.showMessage.assert_not_called()

    def test_session_change_locks_live_placement(self):
        app = self.app
        app._on_place_overlay()
        app.results.put({"session_changed": True, "status": PipelineStatus(in_game=True)})
        app._drain_results()
        self.assertTrue(app.settings.get("overlay_locked"))
        self.assertFalse(app._placing_live_overlay)
        app.tray.showMessage.assert_not_called()

    def test_ui_keeps_finished_cards_but_bar_and_list_still_drop_them(self):
        app = self.app
        parser = MessageParser(app.assets)
        app.timers.handle_events([parser.parse_line("Nasus usou R")], force=True)
        for timer in app.timers.snapshot():
            timer.started_at = time.monotonic() - timer.duration - 61
        for layout, expected in (("cards", 1), ("bar", 0), ("list", 0), ("cards", 1)):
            app.settings.set("overlay_layout", layout, save=False)
            app._refresh_ui()
            self.assertEqual(len(app.overlay.set_timers.call_args.args[0]), expected)
        app._on_reset()
        app._refresh_ui()
        self.assertEqual(app.overlay.set_timers.call_args.args[0], [])

    def test_session_end_clears_finished_cards_before_next_match(self):
        app = self.app
        app.settings.set("overlay_layout", "cards", save=False)
        parser = MessageParser(app.assets)
        app.timers.handle_events([parser.parse_line("Nasus usou R")], force=True)
        for timer in app.timers.snapshot():
            timer.started_at = time.monotonic() - timer.duration - 61
        app._refresh_ui()
        self.assertEqual(len(app.overlay.set_timers.call_args.args[0]), 1)
        app.results.put({"session_changed": True, "status": PipelineStatus(in_game=False)})
        app._drain_results()
        app._refresh_ui()
        self.assertEqual(app.overlay.set_timers.call_args.args[0], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
