"""Exercise actual hover, keyboard and disabled behavior without desktop capture."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import _bootstrap  # noqa: F401
import unittest
from unittest.mock import patch
from PySide6.QtCore import QAbstractAnimation, QEvent, QPoint, QPointF, Qt
from PySide6.QtGui import QEnterEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from hextech import HexButton
from theme import control_qss, display_family, menu_family


class CrystalButtons(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.button = HexButton('Executar teste')
        self.button.setProperty('role', 'primary')
        self.button.setStyleSheet(control_qss())
        self.button.resize(240, 56)
        self.button.show()
        self.app.processEvents()
        self.button.clearFocus()
        self.button._hovered = False
        self.button._transition.stop()
        self.button._set_light(0)

    def tearDown(self):
        self.button.close()
        self.button.deleteLater()
        self.app.processEvents()

    def test_hover_lands_and_leaves_without_permanent_timer(self):
        normal = self.button.grab().toImage()
        with patch('hextech.animations_enabled', return_value=True):
            self.app.sendEvent(self.button, QEnterEvent(QPointF(10,10), QPointF(10,10), QPointF(10,10)))
            QTest.qWait(240)
            self.assertAlmostEqual(self.button._light, 1)
            self.assertEqual(self.button._transition.state(), QAbstractAnimation.Stopped)
            self.assertNotEqual(normal, self.button.grab().toImage())
            self.app.sendEvent(self.button, QEvent(QEvent.Leave))
            QTest.qWait(240)
            self.assertAlmostEqual(self.button._light, 0)

    def test_keyboard_and_disabled_action(self):
        clicked = []
        self.button.clicked.connect(lambda: clicked.append(True))
        self.button.setFocus(Qt.TabFocusReason)
        QTest.qWait(220)
        self.assertTrue(self.button.hasFocus())
        self.assertAlmostEqual(self.button._light, 1)
        QTest.keyClick(self.button, Qt.Key_Space)
        self.assertEqual(len(clicked), 1)
        self.button.setEnabled(False)
        QTest.qWait(220)
        self.assertAlmostEqual(self.button._light, 0)
        QTest.mouseClick(self.button, Qt.LeftButton)
        self.assertEqual(len(clicked), 1)

    def test_reduced_motion_and_hide_cancel_transition(self):
        with patch('hextech.animations_enabled', return_value=False):
            self.button._hovered = True
            self.button._retarget()
            self.assertEqual(self.button._light, 1)
            self.assertEqual(self.button._transition.state(), QAbstractAnimation.Stopped)
        self.button.hide()
        self.assertEqual(self.button._light, 0)
        self.assertEqual(self.button._transition.state(), QAbstractAnimation.Stopped)

    def test_press_release_pulse_and_cancel(self):
        with patch('hextech.animations_enabled', return_value=True):
            QTest.mousePress(self.button, Qt.LeftButton)
            QTest.qWait(100)
            self.assertAlmostEqual(self.button._press_depth, 1)
            QTest.mouseRelease(self.button, Qt.LeftButton)
            QTest.qWait(30)
            self.assertGreater(self.button._pulse, 0)
            QTest.qWait(400)
            self.assertAlmostEqual(self.button._pulse, 0)
            self.assertAlmostEqual(self.button._press_depth, 0)
            self.assertEqual(self.button._click_motion.state(), QAbstractAnimation.Stopped)
            QTest.mousePress(self.button, Qt.LeftButton)
            QTest.mouseRelease(self.button, Qt.LeftButton, pos=self.button.rect().bottomRight()+QPoint(20,20))
            self.assertEqual(self.button._pulse, 0)

    def test_hide_cancels_all_feedback(self):
        self.button._sweep()
        self.button._press_in()
        self.button._click_flash()
        self.button.hide()
        for motion in (self.button._press_motion,self.button._shine_motion,self.button._click_motion):
            self.assertEqual(motion.state(), QAbstractAnimation.Stopped)
        self.assertEqual(self.button._press_depth+self.button._pulse, 0)

    def test_shipped_faces_load(self):
        self.assertIn('Spiegel', menu_family())
        self.assertIn('Beaufort', display_family())


if __name__ == '__main__':
    unittest.main(verbosity=2)
