"""Distribution name, licenses, and protection from replacing PT-BR with upstream."""
import _bootstrap
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import i18n
import updater

spec = importlib.util.spec_from_file_location("flashwatch_build", _bootstrap.ROOT / "build.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class BrazilianPackaging(unittest.TestCase):
    def test_build_does_not_collect_unrelated_path_dlls(self):
        with patch.dict(os.environ, {"PATH": "unrelated-pdf-tool", "PYTHONPATH": "unrelated-python-tool"}):
            env = build.build_environment()
        self.assertNotIn("unrelated", env["PATH"])
        self.assertNotIn("PYTHONPATH", env)
        self.assertIn("System32", env["PATH"])

    def test_spec_includes_name_licenses_and_ocr(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(build, "ROOT", Path(tmp)):
            generated = build.write_spec(True, None).read_text("utf-8")
        self.assertIn("name='FlashWatch-PTBR'", generated)
        self.assertIn("LICENSE", generated)
        self.assertIn("Mulish-OFL.txt", generated)
        self.assertIn('collect_all("rapidocr_onnxruntime")', generated)
        self.assertIn('collect_dynamic_libs("onnxruntime")', generated)
        self.assertIn("upx=False", generated)
        license_text = (_bootstrap.ROOT / "LICENSE").read_text("utf-8")
        self.assertIn("MIT License", license_text)
        self.assertIn("Copyright (c) 2026 abenfraj", license_text)

    def test_updater_requires_localized_asset(self):
        session = Mock()
        payload = {"tag_name": "v1.0.0", "assets": [{
            "name": "Flashwatch.exe", "browser_download_url": "https://example.invalid/upstream.exe"
        }]}
        session.get.return_value.json.return_value = payload
        self.assertIsNone(updater.fetch_latest(session=session))
        payload["assets"][0]["name"] = "FlashWatch-PTBR.exe"
        self.assertIsNotNone(updater.fetch_latest(session=session))

    def test_error_messages_use_brazilian_catalog(self):
        try:
            i18n.set_language("pt_BR")
            with self.assertRaisesRegex(updater.UpdateError, "não foi encontrado"):
                updater.install(Path("missing-ptbr-sample.exe"), Path("unused.exe"))
        finally:
            i18n.set_language(i18n.ENGLISH)


if __name__ == "__main__":
    unittest.main(verbosity=2)
