"""Automatic update lifecycle using fake HTTP and temporary dummy executables.

Never constructs the capture application or executes any downloaded program.
"""
import _bootstrap  # noqa: F401
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import updater
from main import Application
from settings import Settings
from version import __version__

GOOD = b"MZ" + b"verified updater fixture" * 8
SHA = hashlib.sha256(GOOD).hexdigest()


class Response:
    def __init__(self, *, payload=None, content=GOOD):
        self.payload, self.content = payload, content
        self.headers = {"Content-Length": str(len(content))}
    def raise_for_status(self):
        pass
    def json(self):
        return self.payload
    def iter_content(self, _size):
        yield self.content[:10]
        yield self.content[10:]
    def __enter__(self):
        return self
    def __exit__(self, *_):
        pass


class AutoUpdate(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        app = Application.__new__(Application)
        self.app = app
        app.settings = Settings(self.root / "assets/settings.json")
        app._exe = self.root / updater.ASSET_NAME
        app._exe.write_bytes(b"MZ original fixture")
        app._pending_release = None
        app._update_busy = False
        app._update_percent = -1
        app._update_staged = None
        app._update_cancel = threading.Event()
        app._update_check_in_flight = False
        app._quitting = False
        app._invoker = SimpleNamespace(post=lambda callback: callback())
        app.control, app.tray, app.overlay = Mock(), Mock(), Mock()
        app.app = Mock()
        app.worker = None
        self.release = updater.Release("99.0.0", "v99.0.0", "", self.url(), len(GOOD),
                                       updater.RELEASES_PAGE, SHA)

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def url():
        return f"https://github.com/{updater.OWNER}/{updater.REPO}/releases/download/v99.0.0/{updater.ASSET_NAME}"

    def payload(self):
        return {"tag_name": "v99.0.0", "assets": [{"name": updater.ASSET_NAME,
                "browser_download_url": self.url(), "size": len(GOOD), "digest": "sha256:" + SHA}]}

    def download_instantly(self, *, release=None):
        def thread_factory(*, target, args, **_kwargs):
            return SimpleNamespace(start=lambda: target(*args))
        session = Mock()
        session.get.return_value = Response()
        real_download = updater.download
        with patch("main.threading.Thread", side_effect=thread_factory), \
                patch.object(updater, "MIN_PLAUSIBLE_BYTES", 8), \
                patch.object(updater, "download", side_effect=lambda *args, **kw: real_download(*args, session=session, **kw)):
            self.app._on_check_finished(release or self.release, False)

    def test_fork_endpoint_and_release_digest_are_resolved(self):
        self.assertEqual(updater.API_LATEST, "https://api.github.com/repos/MiharaxD/flashwatch-PTBR/releases/latest")
        session = Mock()
        session.get.return_value = Response(payload=self.payload())
        release = updater.fetch_latest(session=session)
        self.assertEqual(release.sha256, SHA)
        self.assertEqual(release.download_url, self.url())

    def test_foreign_urls_invalid_metadata_and_prereleases_are_not_updates(self):
        for bad in ("url", "digest", "size", "prerelease", "assets"):
            payload = self.payload()
            if bad == "url": payload["assets"][0]["browser_download_url"] = "https://example.invalid/file.exe"
            if bad == "digest": payload["assets"][0]["digest"] = "sha256:bad"
            if bad == "size": payload["assets"][0]["size"] = "not a size"
            if bad == "prerelease": payload["prerelease"] = True
            if bad == "assets": payload["assets"] = 42
            session = Mock()
            session.get.return_value = Response(payload=payload)
            with self.subTest(bad=bad):
                self.assertIsNone(updater.fetch_latest(session=session))

    def test_download_is_automatic_but_never_restarts_or_swaps_during_use(self):
        with patch.object(updater, "install") as install, patch.object(updater, "relaunch") as restart:
            self.download_instantly()
            install.assert_not_called()
            restart.assert_not_called()
        self.assertEqual(self.app._update_staged.read_bytes(), GOOD)
        self.assertEqual(self.app._exe.read_bytes(), b"MZ original fixture")
        self.assertFalse(self.app._update_busy)

    def test_quitting_applies_preverified_download_and_keeps_backup_without_restart(self):
        self.download_instantly()
        self.app.settings.set("test_preservation", "unchanged")
        with patch.object(updater, "relaunch") as restart:
            self.app.quit()
            restart.assert_not_called()
        self.assertEqual(self.app._exe.read_bytes(), GOOD)
        self.assertEqual(updater.backup_path(self.app._exe).read_bytes(), b"MZ original fixture")
        self.assertEqual(self.app.settings.get("test_preservation"), "unchanged")
        self.app.app.exit.assert_called_once_with(0)

    def test_explicit_update_now_applies_already_downloaded_file_without_redownload(self):
        self.download_instantly()
        with patch.object(self.app, "_finish_update") as finish, patch.object(updater, "download") as download:
            self.app._on_install_update()
            download.assert_not_called()
            finish.assert_called_once_with(self.app._exe)
        self.assertEqual(self.app._exe.read_bytes(), GOOD)

    def test_skip_after_download_does_not_apply_on_exit(self):
        self.download_instantly()
        staged = self.app._update_staged
        self.app._on_update_skipped()
        self.assertFalse(staged.exists())
        self.app.quit()
        self.assertEqual(self.app._exe.read_bytes(), b"MZ original fixture")
        self.assertEqual(self.app.settings.get("update_skipped_version"), "99.0.0")

    def test_wrong_digest_is_rejected_and_partial_file_is_removed(self):
        session = Mock()
        session.get.return_value = Response(content=GOOD[:-1] + b"!")
        destination = updater.staged_path(self.app._exe)
        with patch.object(updater, "MIN_PLAUSIBLE_BYTES", 8):
            with self.assertRaises(updater.UpdateError):
                updater.download(self.release, destination, session=session)
        self.assertFalse(destination.exists())
        self.assertFalse(destination.with_name(destination.name + ".part").exists())
        self.assertEqual(self.app._exe.read_bytes(), b"MZ original fixture")

    def test_missing_hash_stops_automatic_download(self):
        self.release.sha256 = ""
        with patch.object(updater, "download") as download:
            self.app._on_check_finished(self.release, False)
            download.assert_not_called()
        self.assertFalse(self.app._update_busy)
        self.app.control.set_update_message.assert_called()

    def test_current_and_older_releases_do_not_download(self):
        for version in (__version__, "1.0.0"):
            self.release.version = version
            with patch.object(updater, "download") as download:
                self.app._on_check_finished(self.release, False)
                download.assert_not_called()

    def test_startup_uses_background_thread_and_deduplicates_checks(self):
        with patch("main.threading.Thread") as thread:
            self.app._start_update_check()
            self.app._start_update_check()
            thread.assert_called_once()
            self.assertTrue(thread.call_args.kwargs["daemon"])
        self.app._update_check_in_flight = False
        self.app.settings.set("update_check_enabled", False)
        with patch("main.threading.Thread") as thread:
            self.app._start_update_check()
            thread.assert_not_called()

    def test_quit_mid_transfer_cancels_without_replacing_executable(self):
        self.app._update_busy = True
        self.app.quit()
        self.assertTrue(self.app._update_cancel.is_set())
        self.assertEqual(self.app._exe.read_bytes(), b"MZ original fixture")

    def test_cancelled_download_does_not_promote_partial_file(self):
        session = Mock()
        session.get.return_value = Response()
        destination = updater.staged_path(self.app._exe)
        with self.assertRaises(updater.UpdateError):
            updater.download(self.release, destination, cancelled=lambda: True, session=session)
        self.assertFalse(destination.exists())
        self.assertFalse(destination.with_name(destination.name + ".part").exists())

    def test_failed_swap_on_exit_restores_old_executable(self):
        self.download_instantly()
        staged = self.app._update_staged
        rename = Path.rename
        def fail_staged(path, target):
            if path == staged:
                raise OSError("simulated lock")
            return rename(path, target)
        with patch.object(Path, "rename", fail_staged):
            self.app.quit()
        self.assertEqual(self.app._exe.read_bytes(), b"MZ original fixture")
        self.app.app.exit.assert_called_once_with(0)

    def test_release_tool_understands_ptbr_tags_and_stamped_version_floor(self):
        path = Path(__file__).resolve().parents[1] / "tools/release_meta.py"
        spec = importlib.util.spec_from_file_location("release_meta_test", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with patch.object(module, "git", return_value="v1.0.0-ptbr\nv0.9.0"):
            self.assertEqual(module.latest_tag(), ("v1.0.0-ptbr", (1, 0, 0)))
        version_file = self.root / "version.py"
        version_file.write_text('__version__ = "1.0.2"\n', "utf-8")
        with patch.object(module, "VERSION_FILE", version_file):
            floor = module.version_floor((1, 0, 0))
            self.assertEqual(module.next_version(floor, "patch"), (1, 0, 3))


if __name__ == "__main__":
    unittest.main(verbosity=2)
