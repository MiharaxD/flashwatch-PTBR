"""Hextech surfaces and finite, accessible crystal hover transitions."""
from __future__ import annotations

import ctypes
import os
import math
from functools import lru_cache

from PySide6.QtCore import QEasingCurve, QEvent, QPointF, QRectF, Qt, QVariantAnimation
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen, QPolygonF
from PySide6.QtWidgets import QFrame, QPushButton, QStyle, QStyleOptionButton

GOLD = "#c8aa6e"
CYAN = "#68dcff"


@lru_cache(maxsize=1)
def animations_enabled() -> bool:
    """Honor Windows' client-area animation accessibility preference."""
    if os.name == "nt":
        enabled = ctypes.c_int(1)
        if ctypes.windll.user32.SystemParametersInfoW(0x1042, 0, ctypes.byref(enabled), 0):
            return bool(enabled.value)
    return True


def cut_path(rect: QRectF, cut: float = 8) -> QPainterPath:
    x, y, r, b = rect.left(), rect.top(), rect.right(), rect.bottom()
    cut = min(cut, rect.height() / 4, rect.width() / 4)
    path = QPainterPath(QPointF(x + cut, y))
    for point in ((r-cut,y), (r,y+cut), (r,b-cut), (r-cut,b),
                  (x+cut,b), (x,b-cut), (x,y+cut)):
        path.lineTo(*point)
    path.closeSubpath()
    return path


def metal_frame(p: QPainter, rect: QRectF, *, strong: bool = True) -> None:
    p.save()
    p.setRenderHint(QPainter.Antialiasing)
    gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
    gradient.setColorAt(0, QColor("#efd295" if strong else "#a88a53"))
    gradient.setColorAt(.48, QColor("#514329"))
    gradient.setColorAt(1, QColor("#a3834d" if strong else "#514329"))
    p.setBrush(Qt.NoBrush)
    p.setPen(QPen(QColor("#02080e"), 6 if strong else 3))
    p.drawPath(cut_path(rect.adjusted(2,2,-2,-2), 16))
    p.setPen(QPen(gradient, 2.5 if strong else 1.2))
    p.drawPath(cut_path(rect.adjusted(1,1,-1,-1), 16))
    if strong:
        p.setPen(QPen(QColor("#e3c88c"), .8))
        p.drawPath(cut_path(rect.adjusted(5,5,-5,-5), 13))
        p.setPen(QPen(QColor(GOLD), 1.6))
        for x, sign in ((rect.left(), 1), (rect.right(), -1)):
            p.drawLine(QPointF(x+sign*3, rect.top()+21), QPointF(x+sign*3, rect.top()+12))
            p.drawLine(QPointF(x+sign*3, rect.top()+12), QPointF(x+sign*12, rect.top()+3))
            p.drawLine(QPointF(x+sign*12, rect.top()+3), QPointF(x+sign*25, rect.top()+3))
    if strong and rect.width() > 650:
        cx = rect.center().x()
        p.setPen(QPen(QColor(GOLD), 1.3))
        p.setBrush(QColor('#04121e'))
        p.drawPolygon(QPolygonF([QPointF(cx,rect.top()), QPointF(cx+6,rect.top()+6),
                                QPointF(cx,rect.top()+12), QPointF(cx-6,rect.top()+6)]))
    p.restore()


def engraving(p, rect, rings=False):
    """Quiet geometric etching; vector drawing stays crisp at any window size."""
    p.save()
    p.setClipPath(cut_path(rect, 16))
    p.setPen(QPen(QColor(48, 122, 151, 13), .7))
    for x in range(-int(rect.height()), int(rect.width()), 56):
        p.drawLine(QPointF(x,0), QPointF(x+rect.height(), rect.height()))
        p.drawLine(QPointF(x,rect.height()), QPointF(x+rect.height(), 0))
    if rings:
        center = QPointF(rect.right()-45,rect.center().y()+25)
        for r in (24,37,62,91,119,126,151):
            p.setPen(QPen(QColor(170,142,88,28), .8))
            p.drawEllipse(center,r,r)
        for a in range(0,360,30):
            theta=math.radians(a)
            p.drawLine(center+QPointF(math.cos(theta)*65,math.sin(theta)*65),
                       center+QPointF(math.cos(theta)*148,math.sin(theta)*148))
    p.restore()


def crystal_light(p: QPainter, rect: QRectF, amount: float) -> None:
    """Blue glass facets stay at the edges, clear of the button's label."""
    if amount <= 0:
        return
    p.save()
    p.setRenderHint(QPainter.Antialiasing)
    p.setClipPath(cut_path(rect, 16))
    p.setOpacity(p.opacity() * amount)
    glow = QLinearGradient(rect.topLeft(), rect.bottomLeft())
    glow.setColorAt(0, QColor(100, 224, 255, 75))
    glow.setColorAt(.3, QColor(20, 112, 185, 12))
    glow.setColorAt(.7, QColor(20, 112, 185, 8))
    glow.setColorAt(1, QColor(34, 196, 255, 110))
    p.fillPath(cut_path(rect, 16), glow)
    for width, alpha in ((7,18), (4,35), (1.3,220)):
        p.setPen(QPen(QColor(99,219,255,alpha), width))
        p.setBrush(Qt.NoBrush)
        p.drawPath(cut_path(rect.adjusted(1,1,-1,-1), 15))
    p.restore()


class HexButton(QPushButton):
    """Native QPushButton behavior with a painted metal/crystal skin."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._light = 0.0
        self._hovered = False
        self._transition = QVariantAnimation(self)
        self._transition.setDuration(160)
        self._transition.setEasingCurve(QEasingCurve.OutCubic)
        self._transition.valueChanged.connect(self._set_light)
        self._press_depth = 0.0
        self._pulse = 0.0
        self._shine = 0.0
        self._press_motion = self._motion(100, self._set_depth)
        self._click_motion = self._motion(360, self._set_pulse)
        self._shine_motion = self._motion(1250, self._set_shine)
        self.pressed.connect(self._press_in)
        self.released.connect(self._press_out)
        self.clicked.connect(self._click_flash)

    def _motion(self, duration, setter):
        motion = QVariantAnimation(self)
        motion.setDuration(duration)
        motion.setEasingCurve(QEasingCurve.OutCubic)
        motion.valueChanged.connect(setter)
        return motion

    def _set_depth(self, value):
        self._press_depth = float(value)
        self.update()

    def _set_pulse(self, value):
        self._pulse = float(value)
        self.update()

    def _set_shine(self, value):
        self._shine = float(value)
        self.update()

    def _press_in(self):
        self._press_motion.stop()
        if not animations_enabled():
            self._set_depth(1)
            return
        self._press_motion.setDuration(80)
        self._press_motion.setStartValue(self._press_depth)
        self._press_motion.setEndValue(1.0)
        self._press_motion.start()

    def _press_out(self):
        self._press_motion.stop()
        if not self.isVisible() or not self.isEnabled():
            self._set_depth(0)
            return
        if not animations_enabled():
            self._set_depth(0)
            return
        self._press_motion.setDuration(180)
        self._press_motion.setStartValue(self._press_depth)
        self._press_motion.setEndValue(0.0)
        self._press_motion.start()

    def _click_flash(self):
        if not self.isVisible() or not self.isEnabled() or not animations_enabled():
            return
        self._click_motion.stop()
        self._click_motion.setStartValue(1.0)
        self._click_motion.setEndValue(0.0)
        self._click_motion.start()

    def _sweep(self):
        self._shine_motion.stop()
        if not animations_enabled() or not self.isEnabled():
            self._shine = 0
            return
        self._shine_motion.setEasingCurve(QEasingCurve.InOutSine)
        self._shine_motion.setStartValue(0.0)
        self._shine_motion.setEndValue(1.0)
        self._shine_motion.start()

    def _stop_feedback(self):
        for motion in (self._press_motion, self._click_motion, self._shine_motion):
            motion.stop()
        self._press_depth = self._pulse = self._shine = 0.0

    def _set_light(self, value):
        self._light = float(value)
        self.update()

    def _retarget(self):
        target = float(self.isEnabled() and (self._hovered or self.hasFocus()))
        self._transition.stop()
        if not animations_enabled() or not self.isVisible():
            self._set_light(target)
        else:
            self._transition.setStartValue(self._light)
            self._transition.setEndValue(target)
            self._transition.start()

    def enterEvent(self, event):
        self._hovered = True
        self._sweep()
        self._retarget()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self._retarget()
        super().leaveEvent(event)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self._sweep()
        self._retarget()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self._retarget()

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.EnabledChange and hasattr(self, '_transition'):
            if not self.isEnabled():
                self._stop_feedback()
            self._retarget()

    def hideEvent(self, event):
        self._stop_feedback()
        self._transition.stop()
        self._hovered = False
        self._light = 0.0
        super().hideEvent(event)

    def paintEvent(self, event):
        role = self.property('role') or ''
        if role in ('chrome', 'chrome_close', 'link', 'quiet'):
            super().paintEvent(event)
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        depth = self._press_depth
        inset = 1 + depth*1.5
        rect = QRectF(self.rect()).adjusted(inset,inset,-inset,-inset)
        active = self.isChecked() or role == 'primary'
        fill = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        fill.setColorAt(0, QColor('#113c48' if active else '#101e2b'))
        fill.setColorAt(1, QColor('#04121e'))
        if not self.isEnabled():
            p.setOpacity(.42)
        if role != 'nav' or active or self._light:
            p.fillPath(cut_path(rect), fill)
            metal_frame(p, rect, strong=active)
        if role == 'danger':
            p.setPen(QPen(QColor('#93534c'), 1))
            p.drawPath(cut_path(rect))
        crystal_light(p, rect, self._light * (1-depth*.55))
        if self._light > 0 or self._pulse > 0:
            p.save()
            p.setClipPath(cut_path(rect, 16))
            # Measure distance along the actual bevel: the glint turns each
            # chamfer rather than sweeping a straight gradient across the face.
            edge = cut_path(rect.adjusted(2,2,-2,-2), 14)
            length = edge.length()
            steps = max(48, int(length/4))
            envelope = math.sin(math.pi*self._shine)**.35
            p.setBrush(Qt.NoBrush)
            for index in range(steps):
                t = (index+.5)/steps
                delta = abs(t-self._shine)
                delta = min(delta,1-delta)
                intensity = max(0,1-delta/.12)**2 * self._light * envelope
                if intensity < .01:
                    continue
                start = edge.pointAtPercent(edge.percentAtLength(length*index/steps))
                end = edge.pointAtPercent(edge.percentAtLength(length*(index+1)/steps))
                for width, alpha in ((6,45),(3,125),(1.25,255)):
                    p.setPen(QPen(QColor(205,250,255,int(alpha*intensity)),
                                  width, Qt.SolidLine, Qt.RoundCap))
                    p.drawLine(start,end)
            # Soft blue inner bevel holds while hovered, with a bright release pulse.
            p.setPen(QPen(QColor(190,248,255,int(110*self._light+130*self._pulse)), 1))
            p.drawPath(cut_path(rect.adjusted(3,3,-3,-3), 13))
            if self._pulse > 0:
                pulse = QLinearGradient(rect.topLeft(),rect.bottomLeft())
                pulse.setColorAt(0,QColor(210,255,255,int(105*self._pulse)))
                pulse.setColorAt(.45,QColor(70,200,255,int(30*self._pulse)))
                pulse.setColorAt(1,QColor(130,242,255,int(120*self._pulse)))
                p.fillPath(cut_path(rect,16),pulse)
                expansion = (1-self._pulse)*9
                p.setPen(QPen(QColor(195,250,255,int(230*self._pulse)),1.6))
                p.drawPath(cut_path(rect.adjusted(expansion,expansion,-expansion,-expansion),max(3,16-expansion)))
            p.restore()
        if self.hasFocus():
            p.setPen(QPen(QColor(CYAN), 1.2, Qt.DotLine))
            p.setBrush(Qt.NoBrush)
            p.drawPath(cut_path(rect.adjusted(5,5,-5,-5), 5))
        p.translate(0, depth*1.2)
        option = QStyleOptionButton()
        self.initStyleOption(option)
        if role == 'nav':
            scale = self.height()/64.0
            padding = max(8, round(18*scale))
            size = self.iconSize().width()
            icon_rect = QRectF(padding, (self.height()-size)/2, size, size)
            self.icon().paint(p, icon_rect.toRect())
            text_rect = QRectF(icon_rect.right()+10*scale, 0,
                               self.width()-icon_rect.right()-10*scale-padding, self.height())
            p.setPen(QColor('#f0e6d2' if self.isChecked() else '#c8c3b8'))
            p.setFont(self.font())
            p.setClipRect(text_rect)
            p.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft,
                       self.fontMetrics().elidedText(str(self.property('label') or self.text()).strip(),
                                                    Qt.ElideRight, int(text_rect.width())))
        else:
            option.rect = option.rect.adjusted(12, 4, -12, -4)
            self.style().drawControl(QStyle.CE_PushButtonLabel, option, p, self)
        p.end()


class HexPanel(QFrame):
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(self.rect()).adjusted(1,1,-1,-1)
        fill = QLinearGradient(rect.topLeft(), rect.bottomRight())
        fill.setColorAt(0, QColor('#0a1b29'))
        fill.setColorAt(1, QColor('#010a13'))
        p.fillPath(cut_path(rect,10), fill)
        role = str(self.property('role'))
        engraving(p, rect, rings=role in ('hero_2','rail'))
        metal_frame(p, rect, strong=role.startswith('hero') or role == 'rail')
