"""Responsive geometry and Windows resize hit tests; no game/capture workers."""
import _bootstrap
import os
import tempfile
import unittest
from pathlib import Path
from PySide6.QtWidgets import QApplication
from settings import Settings
from riot_assets import RiotAssets
from ui import ControlWindow
from i18n import set_language


class ResizableShell(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_geometry_and_navigation(self):
        with tempfile.TemporaryDirectory() as tmp:
            set_language('pt_BR')
            w = ControlWindow(Settings(Path(tmp)/'settings.json'), RiotAssets())
            w.show()
            try:
                for width, height in ((900,650),(1000,720),(1448,1086),(1600,900)):
                    w.resize(width,height)
                    self.app.processEvents()
                    self.assertEqual((w.width(),w.height()),(width,height))
                    for button in w.nav_buttons:
                        scale=button.height()/64
                        room=button.width()-2*max(8,round(18*scale))-button.iconSize().width()-10*scale
                        self.assertLessEqual(button.fontMetrics().horizontalAdvance(button.property('label')), room)
                    self.assertGreater(w.maximumWidth(), w.minimumWidth())
                if os.name == 'nt' and self.app.platformName() == 'windows':
                    import ctypes
                    from ctypes import wintypes
                    user32=ctypes.windll.user32
                    user32.SendMessageW.argtypes=[wintypes.HWND,wintypes.UINT,wintypes.WPARAM,wintypes.LPARAM]
                    user32.SendMessageW.restype=ctypes.c_ssize_t
                    bounds=wintypes.RECT()
                    user32.GetWindowRect(int(w.winId()),ctypes.byref(bounds))
                    for x,y,expected in ((bounds.left+2,bounds.top+2,13),
                                         (bounds.right-2,bounds.bottom-2,17),
                                         (bounds.right-2,(bounds.top+bounds.bottom)//2,11)):
                        result=user32.SendMessageW(int(w.winId()),0x84,0,(y<<16)|(x&0xffff))
                        self.assertEqual(result,expected)
            finally:
                w.hide()
                w.deleteLater()
                self.app.processEvents()


if __name__ == '__main__':
    unittest.main(verbosity=2)
