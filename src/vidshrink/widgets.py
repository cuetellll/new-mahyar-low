"""Custom-painted, animated, glowing gaming widgets for Mahyar Compressor."""
from __future__ import annotations

import math
import os
import random

from PySide6.QtCore import (Property, QEasingCurve, QPointF, QRectF, QSize, Qt, Signal, QUrl)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QDesktopServices, QFontMetrics, QLinearGradient,
                           QPainter, QPainterPath, QPen, QRadialGradient)
from PySide6.QtWidgets import QLabel, QPushButton, QSizePolicy, QWidget

from . import i18n
from .engine import fmt_time, human_size
from .i18n import tr
from .theme import (AMBER, BLUE, CYAN, DARK_SURFACE, GREEN, MAGENTA, MUTED, PURPLE, RED, TEXT, VIOLET,
                    animate, clamp, clock, draw_bar, draw_glass, draw_glow, draw_logo, font, mix, rgba)


def _aa(p: QPainter):
    p.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)


# =========================================================================== BUTTONS
class GlowButton(QPushButton):
    """Cyberpunk gaming pill button with intense neon bloom, hover swell, and travelling laser flare.
    Supports variants: 'primary', 'danger', 'amber', 'ghost'
    """

    PAD = 10

    def __init__(self, key: str = "", variant: str = "primary", small: bool = False, parent=None):
        super().__init__(parent)
        self._key, self.variant, self.small = key, variant, small
        self._hover = 0.0
        self._press = 0.0
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.NoFocus)
        self.setFixedHeight((36 if small else 54) + (self.PAD * 2 if variant != "ghost" or not small else 0))
        if variant == "ghost" and small:
            self.setFixedHeight(38)

    def setKey(self, key: str):
        self._key = key
        self.update()

    def setVariant(self, v: str):
        self.variant = v
        self.update()

    def setLabelFn(self, fn):
        self._label_fn = fn
        self.update()

    def label(self) -> str:
        fn = getattr(self, "_label_fn", None)
        if fn:
            return fn()
        return tr(self._key) if self._key else ""

    def sizeHint(self):
        return QSize(160, self.height())

    def _g(self):
        return self._hover

    def _s(self, v):
        self._hover = v
        self.update()

    hover = Property(float, _g, _s)

    def enterEvent(self, e):
        animate(self, "hover", 1.0, 200)
        super().enterEvent(e)

    def leaveEvent(self, e):
        animate(self, "hover", 0.0, 300)
        super().leaveEvent(e)

    def mousePressEvent(self, e):
        self._press = 1.0
        self.update()
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        self._press = 0.0
        self.update()
        super().mouseReleaseEvent(e)

    def paintEvent(self, _):
        p = QPainter(self)
        _aa(p)
        t = clock().t
        en = self.isEnabled()
        pad = self.PAD if self.variant != "ghost" else 5
        r = QRectF(self.rect()).adjusted(pad, pad, -pad, -pad)
        if self.variant == "ghost" and self.small:
            r = QRectF(self.rect()).adjusted(2, 2, -2, -2)

        c = r.center()
        sc = 1.0 + 0.028 * self._hover - 0.03 * self._press
        p.translate(c)
        p.scale(sc, sc)
        p.translate(-c)
        rad = r.height() / 2

        if self.variant in ("primary", "danger", "amber"):
            if self.variant == "primary":
                c1, c2 = CYAN, PURPLE
            elif self.variant == "amber":
                c1, c2 = AMBER, MAGENTA
            else:
                c1, c2 = MAGENTA, RED
            pulse = 0.5 + 0.5 * math.sin(t * 2.8)
            strength = (0.75 + 0.8 * self._hover + 0.35 * pulse) * (1.0 if en else 0.15)
            draw_glow(p, r, rad, mix(c1, c2, 0.5 + 0.2 * math.sin(t * 1.5)), strength, pad + 2)

            g = QLinearGradient(r.left(), 0, r.right(), 0)
            sh = 0.5 + 0.5 * math.sin(t * 1.5)
            g.setColorAt(0, mix(c1, MAGENTA, 0.2 * sh))
            g.setColorAt(0.55, mix(c1, c2, 0.5))
            g.setColorAt(1, mix(c2, CYAN if self.variant == "primary" else AMBER, 0.7))
            if not en:
                g.setColorAt(0, QColor(45, 30, 65))
                g.setColorAt(1, QColor(45, 30, 65))
            p.setPen(QPen(QColor(255, 255, 255, 75 if en else 15), 1.3))
            p.setBrush(g)
            p.drawRoundedRect(r, rad, rad)

            if en:
                p.save()
                path = QPainterPath()
                path.addRoundedRect(r, rad, rad)
                p.setClipPath(path)
                x = r.left() + ((t * 0.55) % 1.7 - 0.35) * r.width()
                sg = QLinearGradient(x - 55, 0, x + 55, 0)
                sg.setColorAt(0, QColor(255, 255, 255, 0))
                sg.setColorAt(0.5, QColor(255, 255, 255, 130))
                sg.setColorAt(1, QColor(255, 255, 255, 0))
                p.fillRect(r, sg)
                p.restore()

            p.setPen(QColor(255, 255, 255) if en else QColor(140, 130, 160))
            p.setFont(font(14 if not self.small else 12, True, 0.7))
            p.drawText(r, Qt.AlignCenter, self.label())
        else:
            h = self._hover
            draw_glow(p, r, rad, CYAN if h > 0.5 else PURPLE, 0.65 * h, 8)
            gb = QLinearGradient(r.topLeft(), r.bottomRight())
            gb.setColorAt(0, QColor(24, 14, 46, int(165 + 60 * h)))
            gb.setColorAt(1, QColor(10, 6, 24, int(195 + 50 * h)))
            p.setBrush(gb)
            edge = mix(rgba(PURPLE, 0.50), CYAN, h)
            p.setPen(QPen(edge, 1.3))
            p.drawRoundedRect(r, rad, rad)
            p.setPen(mix(MUTED, TEXT, h) if en else rgba(MUTED, 0.4))
            p.setFont(font(12, True))
            fm = QFontMetrics(p.font())
            txt = fm.elidedText(self.label(), Qt.ElideMiddle, int(r.width() - 16))
            p.drawText(r, Qt.AlignCenter, txt)


class IconButton(QPushButton):
    """Circular HUD icon button with glowing neon halo and hover magnification.
    Supports kinds:
    'min', 'close', 'lang', 'reset', 'fullscreen', 'dock', 'expand',
    'folder', 'add', 'play', 'pause', 'pin', 'theme', 'copy', 'retry'
    """

    def __init__(self, kind: str, parent=None):
        super().__init__(parent)
        self.kind = kind
        self.active_state = False
        self._hover = 0.0
        self._label = ""
        self.setFixedSize(40, 40)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.NoFocus)

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, val: str):
        self._label = val
        self.update()

    def setKind(self, kind: str):
        self.kind = kind
        self.update()

    def setActiveState(self, active: bool):
        self.active_state = active
        self.update()

    def _g(self):
        return self._hover

    def _s(self, v):
        self._hover = v
        self.update()

    hover = Property(float, _g, _s)

    def enterEvent(self, e):
        animate(self, "hover", 1.0, 160)
        super().enterEvent(e)

    def leaveEvent(self, e):
        animate(self, "hover", 0.0, 260)
        super().leaveEvent(e)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            e.accept()
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            e.accept()
        super().mouseReleaseEvent(e)

    def paintEvent(self, _):
        p = QPainter(self)
        _aa(p)
        h = max(self._hover, 0.85 if self.active_state else 0.0)
        if self.kind == "close":
            col = RED
        elif self.kind in ("pause", "retry"):
            col = AMBER
        elif self.kind == "theme":
            col = MAGENTA
        elif self.kind in ("dock", "expand", "fullscreen", "pin"):
            col = CYAN
        else:
            col = PURPLE

        r = QRectF(self.rect()).adjusted(4, 4, -4, -4)
        draw_glow(p, r, r.height() / 2, col, 0.95 * h, 6)
        p.setPen(QPen(rgba(col, 0.42 + 0.55 * h), 1.3))
        p.setBrush(QColor(18, 10, 36, int(165 + 75 * h)))
        p.drawEllipse(r)
        c = r.center()
        p.setPen(QPen(mix(MUTED, QColor(255, 255, 255), h), 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        s = 5.0
        if self.kind == "min":
            p.drawLine(QPointF(c.x() - s, c.y() + 1), QPointF(c.x() + s, c.y() + 1))
        elif self.kind == "close":
            p.drawLine(QPointF(c.x() - s, c.y() - s), QPointF(c.x() + s, c.y() + s))
            p.drawLine(QPointF(c.x() - s, c.y() + s), QPointF(c.x() + s, c.y() - s))
        elif self.kind == "lang":
            p.setFont(font(10.5, True))
            p.drawText(r, Qt.AlignCenter, self.label)
        elif self.kind in ("reset", "retry"):
            path = QPainterPath()
            path.arcMoveTo(QRectF(c.x() - s, c.y() - s, 2 * s, 2 * s), 60)
            path.arcTo(QRectF(c.x() - s, c.y() - s, 2 * s, 2 * s), 60, 280)
            p.setBrush(Qt.NoBrush)
            p.drawPath(path)
        elif self.kind == "fullscreen":
            b = 5.5
            k = 2.6
            for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                p.drawLine(QPointF(c.x() + dx * b, c.y() + dy * b), QPointF(c.x() + dx * (b - k), c.y() + dy * b))
                p.drawLine(QPointF(c.x() + dx * b, c.y() + dy * b), QPointF(c.x() + dx * b, c.y() + dy * (b - k)))
        elif self.kind == "dock":
            path = QPainterPath()
            path.moveTo(c.x() - 4.5, c.y() - 3.5)
            path.lineTo(c.x(), c.y() + 1.5)
            path.lineTo(c.x() + 4.5, c.y() - 3.5)
            p.setBrush(Qt.NoBrush)
            p.drawPath(path)
            p.drawLine(QPointF(c.x() - 5.5, c.y() + 5), QPointF(c.x() + 5.5, c.y() + 5))
        elif self.kind == "expand":
            path = QPainterPath()
            path.moveTo(c.x() - 4.5, c.y() + 2.5)
            path.lineTo(c.x(), c.y() - 2.5)
            path.lineTo(c.x() + 4.5, c.y() + 2.5)
            p.setBrush(Qt.NoBrush)
            p.drawPath(path)
            p.drawLine(QPointF(c.x() - 5.5, c.y() - 5.5), QPointF(c.x() + 5.5, c.y() - 5.5))
        elif self.kind == "add":
            p.drawLine(QPointF(c.x() - s, c.y()), QPointF(c.x() + s, c.y()))
            p.drawLine(QPointF(c.x(), c.y() - s), QPointF(c.x(), c.y() + s))
        elif self.kind == "folder":
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(QRectF(c.x() - 6, c.y() - 4, 12, 8.5), 2, 2)
            p.drawLine(QPointF(c.x() - 5, c.y() - 5.5), QPointF(c.x() - 1, c.y() - 5.5))
        elif self.kind == "pause":
            p.drawLine(QPointF(c.x() - 3.2, c.y() - 5), QPointF(c.x() - 3.2, c.y() + 5))
            p.drawLine(QPointF(c.x() + 3.2, c.y() - 5), QPointF(c.x() + 3.2, c.y() + 5))
        elif self.kind == "play":
            tri = QPainterPath()
            tri.moveTo(c.x() - 3.5, c.y() - 5.2)
            tri.lineTo(c.x() + 5.2, c.y())
            tri.lineTo(c.x() - 3.5, c.y() + 5.2)
            tri.closeSubpath()
            p.setBrush(QColor(255, 255, 255))
            p.setPen(Qt.NoPen)
            p.drawPath(tri)
        elif self.kind == "pin":
            # Pushpin icon
            p.drawLine(QPointF(c.x() - 4, c.y() - 5), QPointF(c.x() + 4, c.y() - 5))
            p.drawLine(QPointF(c.x() - 3, c.y() - 5), QPointF(c.x() - 4.5, c.y() + 1))
            p.drawLine(QPointF(c.x() + 3, c.y() - 5), QPointF(c.x() + 4.5, c.y() + 1))
            p.drawLine(QPointF(c.x() - 5, c.y() + 1), QPointF(c.x() + 5, c.y() + 1))
            p.drawLine(QPointF(c.x(), c.y() + 1), QPointF(c.x(), c.y() + 6.5))
        elif self.kind == "theme":
            # Glowing tri-color palette orb
            for ang, col_dot in ((0, CYAN), (120, MAGENTA), (240, GREEN)):
                rad_a = math.radians(ang)
                px = c.x() + 4.2 * math.cos(rad_a)
                py = c.y() + 4.2 * math.sin(rad_a)
                p.setPen(Qt.NoPen)
                p.setBrush(col_dot)
                p.drawEllipse(QPointF(px, py), 2.6, 2.6)
        elif self.kind == "copy":
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(QRectF(c.x() - 5, c.y() - 5, 7.5, 9), 1.5, 1.5)
            p.drawRoundedRect(QRectF(c.x() - 2, c.y() - 2, 7.5, 9), 1.5, 1.5)


# =========================================================================== CONTROLS
class Segmented(QWidget):
    """Gaming HUD segmented control with a sliding glowing neon pill."""

    changed = Signal(int)

    def __init__(self, labels: list[str], height: int = 40, parent=None):
        super().__init__(parent)
        self.labels = labels
        self._idx = 0
        self._pos = 0.0
        self._hov = -1
        self.setFixedHeight(height)
        self.setMouseTracking(True)
        self.setCursor(Qt.PointingHandCursor)

    def _g(self):
        return self._pos

    def _s(self, v):
        self._pos = v
        self.update()

    slide = Property(float, _g, _s)

    def index(self) -> int:
        return self._idx

    def setIndex(self, i: int, anim: bool = True):
        self._idx = i
        if anim:
            animate(self, "slide", float(i), 360, QEasingCurve.OutBack)
        else:
            self._pos = float(i)
            self.update()

    def _at(self, x: float) -> int:
        return int(clamp(x / max(1, self.width()) * len(self.labels), 0, len(self.labels) - 1e-6))

    def mouseMoveEvent(self, e):
        self._hov = self._at(e.position().x())
        self.update()

    def leaveEvent(self, e):
        self._hov = -1
        self.update()

    def mousePressEvent(self, e):
        i = self._at(e.position().x())
        if i != self._idx:
            self.setIndex(i)
            self.changed.emit(i)

    def paintEvent(self, _):
        p = QPainter(self)
        _aa(p)
        n = len(self.labels)
        r = QRectF(self.rect()).adjusted(4, 3, -4, -3)
        rad = r.height() / 2

        p.setPen(QPen(rgba(CYAN, 0.25), 1))
        p.setBrush(QColor(8, 5, 20, 225))
        p.drawRoundedRect(r, rad, rad)

        sw = r.width() / n
        hl = QRectF(r.left() + self._pos * sw + 3, r.top() + 3, sw - 6, r.height() - 6)

        draw_glow(p, hl, hl.height() / 2, CYAN, 1.0, 7)
        g = QLinearGradient(hl.left(), 0, hl.right(), 0)
        g.setColorAt(0, PURPLE)
        g.setColorAt(0.5, VIOLET)
        g.setColorAt(1, CYAN)
        p.setPen(QPen(QColor(255, 255, 255, 70), 1))
        p.setBrush(g)
        p.drawRoundedRect(hl, hl.height() / 2, hl.height() / 2)

        p.setFont(font(11.5, True))
        for i, key in enumerate(self.labels):
            sel = clamp(1 - abs(i - self._pos))
            col = mix(MUTED, QColor(255, 255, 255), sel)
            if i == self._hov and sel < 0.5:
                col = mix(col, CYAN, 0.7)
            p.setPen(col)
            cell = QRectF(r.left() + i * sw, r.top(), sw, r.height())
            fm = QFontMetrics(p.font())
            p.drawText(cell, Qt.AlignCenter, fm.elidedText(tr(key), Qt.ElideRight, int(sw - 6)))


class ToggleRow(QWidget):
    """Gaming HUD Toggle with animated neon LED thumb and circuit track."""

    toggled = Signal(bool)

    def __init__(self, key: str, hint_key: str, parent=None):
        super().__init__(parent)
        self.key, self.hint_key = key, hint_key
        self._on = 0.0
        self.state = False
        self.setFixedHeight(44)
        self.setCursor(Qt.PointingHandCursor)

    def _g(self):
        return self._on

    def _s(self, v):
        self._on = v
        self.update()

    on = Property(float, _g, _s)

    def setChecked(self, v: bool, anim: bool = True):
        self.state = v
        if anim:
            animate(self, "on", 1.0 if v else 0.0, 280, QEasingCurve.OutBack)
        else:
            self._on = 1.0 if v else 0.0
            self.update()

    def mouseReleaseEvent(self, e):
        if self.rect().contains(e.position().toPoint()):
            self.setChecked(not self.state)
            self.toggled.emit(self.state)

    def paintEvent(self, _):
        p = QPainter(self)
        _aa(p)
        w, h = self.width(), self.height()
        sw, sh = 46.0, 24.0
        tr_ = QRectF(w - sw - 6, (h - sh) / 2, sw, sh)
        o = clamp(self._on)

        draw_glow(p, tr_, sh / 2, CYAN, 1.0 * o, 8)
        g = QLinearGradient(tr_.left(), 0, tr_.right(), 0)
        g.setColorAt(0, mix(QColor(16, 10, 32, 220), PURPLE, o))
        g.setColorAt(1, mix(QColor(22, 14, 42, 220), CYAN, o))
        p.setPen(QPen(rgba(CYAN if o > 0.5 else PURPLE, 0.3 + 0.5 * o), 1.2))
        p.setBrush(g)
        p.drawRoundedRect(tr_, sh / 2, sh / 2)

        kx = tr_.left() + 3 + self._on * (sw - sh)
        thumb_r = QRectF(kx, tr_.top() + 3, sh - 6, sh - 6)
        draw_glow(p, thumb_r, (sh - 6) / 2, QColor(255, 255, 255), 0.9 * o, 5)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(255, 255, 255))
        p.drawEllipse(thumb_r)

        p.setPen(TEXT)
        p.setFont(font(12, True))
        p.drawText(QRectF(2, 3, w - sw - 18, 19), Qt.AlignLeft | Qt.AlignVCenter, tr(self.key))
        p.setPen(MUTED)
        p.setFont(font(10))
        fm = QFontMetrics(p.font())
        p.drawText(QRectF(2, 22, w - sw - 18, 16), Qt.AlignLeft | Qt.AlignVCenter,
                   fm.elidedText(tr(self.hint_key), Qt.ElideRight, int(w - sw - 18)))


class SLabel(QLabel):
    """Cyberpunk section header with neon accent."""

    def __init__(self, key: str, parent=None):
        super().__init__(parent)
        self.key = key
        self.setStyleSheet("background: transparent; color: rgba(34,211,238,230);")
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.retranslate()

    def retranslate(self):
        self.setFont(font(10.5, True, 1.3))
        self.setText(f"◈  {tr(self.key).upper()}" if i18n.LANG == "en" else f"◈  {tr(self.key)}")


class GlassPanel(QWidget):
    """Dark Obsidian Glass Container with cyber border."""

    def paintEvent(self, _):
        p = QPainter(self)
        _aa(p)
        r = QRectF(self.rect()).adjusted(2, 2, -2, -2)
        draw_glass(p, r, 22, PURPLE, 0.45)


# =========================================================================== DROP ZONE
class DropZone(QWidget):
    """Holographic Cyber Drop Portal with rotating laser rings & format badges."""

    clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._active = 0.0
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(110)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def sizeHint(self):
        return QSize(400, 150)

    def _ga(self):
        return self._active

    def _sa(self, v):
        self._active = v
        self.update()

    active = Property(float, _ga, _sa)

    def set_active(self, on: bool):
        animate(self, "active", 1.0 if on else 0.0, 260)

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked.emit()

    def _icon(self, p: QPainter, cx: float, cy: float, s: float, t: float, act: float):
        for i in range(3):
            ph = (t * 0.55 + i * 0.33) % 1.0
            p.setPen(QPen(rgba(CYAN if i % 2 == 0 else PURPLE, (1 - ph) * (0.5 + 0.4 * act)), 1.8))
            p.setBrush(Qt.NoBrush)
            rr = s * (1.0 + ph * 1.15)
            p.drawEllipse(QPointF(cx, cy), rr, rr)

        scale = 1 + 0.14 * act
        s *= scale
        draw_glow(p, QRectF(cx - s, cy - s, 2 * s, 2 * s), s, CYAN, 1.15 + act, 10)
        g = QLinearGradient(cx - s, cy - s, cx + s, cy + s)
        g.setColorAt(0, CYAN)
        g.setColorAt(0.5, PURPLE)
        g.setColorAt(1, MAGENTA)
        p.setPen(QPen(rgba(TEXT, 0.8), 1.5))
        p.setBrush(g)
        p.drawEllipse(QPointF(cx, cy), s, s)

        bob = math.sin(t * 3.2) * s * 0.08 + act * s * 0.12
        p.setPen(QPen(QColor(255, 255, 255), s * 0.13, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.drawLine(QPointF(cx, cy - s * 0.42 + bob), QPointF(cx, cy + s * 0.30 + bob))
        path = QPainterPath()
        path.moveTo(cx - s * 0.30, cy + s * 0.02 + bob)
        path.lineTo(cx, cy + s * 0.34 + bob)
        path.lineTo(cx + s * 0.30, cy + s * 0.02 + bob)
        p.setBrush(Qt.NoBrush)
        p.drawPath(path)
        p.drawLine(QPointF(cx - s * 0.42, cy + s * 0.58), QPointF(cx + s * 0.42, cy + s * 0.58))

    def paintEvent(self, _):
        p = QPainter(self)
        _aa(p)
        t = clock().t
        w, h = self.width(), self.height()
        act = self._active
        pad = 10
        r = QRectF(pad, pad, w - 2 * pad, h - 2 * pad)
        k = clamp((h - 145) / 120.0)

        pulse = 0.5 + 0.5 * math.sin(t * 2.2)
        col = mix(PURPLE, CYAN, 0.5 + 0.5 * math.sin(t * 0.9))
        draw_glow(p, r, 24, col, 0.45 + 0.35 * pulse + 0.9 * act, 10)

        bg = QLinearGradient(r.topLeft(), r.bottomRight())
        bg.setColorAt(0, QColor(14, 10, 34, int(175 + 55 * act)))
        bg.setColorAt(1, QColor(6, 4, 18, int(215 + 35 * act)))
        p.setPen(Qt.NoPen)
        p.setBrush(bg)
        p.drawRoundedRect(r, 24, 24)

        cg = QConicalGradient(r.center(), -(t * 60) % 360)
        for pos, c in ((0.0, CYAN), (0.33, PURPLE), (0.66, MAGENTA), (1.0, CYAN)):
            cg.setColorAt(pos, c)
        pen = QPen(QBrush(cg), 2.2)
        pen.setStyle(Qt.CustomDashLine)
        pen.setDashPattern([4.0, 4.0])
        pen.setDashOffset(-t * 8)
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(r, 24, 24)

        titles = (tr("drop_title"), tr("drop_sub"))
        titles_c = (tr("drop_more"), tr("drop_more_sub"))
        cx, cy = w / 2, h / 2

        if k > 0.02:
            p.save()
            p.setOpacity(k)
            self._icon(p, cx, cy - 46 * k, 36, t, act)
            p.setPen(TEXT)
            p.setFont(font(21, True))
            p.drawText(QRectF(0, cy + 8, w, 34), Qt.AlignCenter, titles[0])
            p.setPen(MUTED)
            p.setFont(font(13))
            p.drawText(QRectF(0, cy + 42, w, 22), Qt.AlignCenter, titles[1])

            chips = ["MP4", "MKV", "MOV", "AVI", "WEBM", "HEVC 10-BIT"]
            p.setFont(font(10, True))
            cw, gap = 64, 8
            x0 = cx - (len(chips) * cw + (len(chips) - 1) * gap) / 2
            for i, c in enumerate(chips):
                cr = QRectF(x0 + i * (cw + gap), cy + 74, cw, 22)
                p.setPen(QPen(rgba(CYAN if i % 2 == 0 else PURPLE, 0.55), 1))
                p.setBrush(QColor(22, 12, 44, 190))
                p.drawRoundedRect(cr, 11, 11)
                p.setPen(rgba(TEXT, 0.92))
                p.drawText(cr, Qt.AlignCenter, c)
            p.restore()

        if k < 0.98:
            p.save()
            p.setOpacity(1 - k)
            self._icon(p, r.left() + 54, cy, 22, t, act)
            p.setPen(TEXT)
            p.setFont(font(16, True))
            p.drawText(QRectF(r.left() + 96, cy - 24, w - 130, 26), Qt.AlignLeft | Qt.AlignVCenter, titles_c[0])
            p.setPen(MUTED)
            p.setFont(font(12))
            p.drawText(QRectF(r.left() + 96, cy + 2, w - 130, 22), Qt.AlignLeft | Qt.AlignVCenter, titles_c[1])
            p.restore()


# =========================================================================== QUEUE ITEM
QUEUED, PROCESSING, DONE, FAILED, SKIPPED = range(5)


class QueueItem(QWidget):
    """Cyber Deck Queue Card with interactive Play, Open Folder, and Remove buttons."""

    removeRequested = Signal(object)
    H = 84

    def __init__(self, path: str, info, parent=None):
        super().__init__(parent)
        self.path, self.info = path, info
        self.status = QUEUED
        self.target = 0.0
        self.shown = 0.0
        self.speed = 0.0
        self.eta = 0.0
        self.in_size = info.size
        self.out_size = 0
        self.out_path = ""
        self.err = ""
        self.removable = True
        self._appear = 0.0
        self._rm_hover = False
        self._play_hover = False
        self._dir_hover = False
        self._lt = clock().t
        self.setFixedHeight(self.H)
        self.setMouseTracking(True)
        animate(self, "appear", 1.0, 500, QEasingCurve.OutBack)

    def _ga(self):
        return self._appear

    def _sa(self, v):
        self._appear = v
        self.update()

    appear = Property(float, _ga, _sa)

    def set_processing(self):
        self.status, self.target, self.shown = PROCESSING, 0.0, 0.0
        self.speed = self.eta = 0.0
        self.update()

    def set_progress(self, frac, speed, eta):
        self.target, self.speed, self.eta = frac, speed, eta

    def set_done(self, out_path: str, in_size: int, out_size: int):
        self.target = 1.0
        self.in_size, self.out_size, self.out_path = in_size, out_size, out_path
        self.status = DONE if out_path else SKIPPED
        self.update()

    def set_failed(self, msg: str):
        self.status, self.err = FAILED, msg
        self.update()

    def reset(self):
        self.status, self.target, self.shown, self.err = QUEUED, 0.0, 0.0, ""
        self.update()

    @property
    def saved_ratio(self) -> float:
        return 1 - self.out_size / self.in_size if self.in_size else 0.0

    def _rm_rect(self) -> QRectF:
        return QRectF(self.width() - 48, self.height() / 2 - 24, 32, 32)

    def _dir_rect(self) -> QRectF:
        return QRectF(self.width() - 86, self.height() / 2 - 24, 32, 32)

    def _play_rect(self) -> QRectF:
        return QRectF(self.width() - 124, self.height() / 2 - 24, 32, 32)

    def _badge_rect(self) -> QRectF:
        r = QRectF(self.rect()).adjusted(3, 4, -3, -4)
        return QRectF(r.right() - 216, r.top() + 12, 82, 30)

    def mouseMoveEvent(self, e):
        st = self.status
        pos = e.position()
        rm_h = self.removable and st != PROCESSING and self._rm_rect().contains(pos)
        dir_h = st != PROCESSING and self._dir_rect().contains(pos)
        play_h = st != PROCESSING and self._play_rect().contains(pos)

        if (rm_h, dir_h, play_h) != (self._rm_hover, self._dir_hover, self._play_hover):
            self._rm_hover, self._dir_hover, self._play_hover = rm_h, dir_h, play_h
            self.update()

        if rm_h or dir_h or play_h or (st == DONE and self.out_path):
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def leaveEvent(self, e):
        self._rm_hover = self._dir_hover = self._play_hover = False
        self.update()

    def mouseReleaseEvent(self, e):
        st = self.status
        pos = e.position()
        if st != PROCESSING:
            if self.removable and self._rm_rect().contains(pos):
                self.removeRequested.emit(self)
                return
            if self._dir_rect().contains(pos):
                target = os.path.dirname(self.out_path or self.path)
                if target and os.path.exists(target):
                    QDesktopServices.openUrl(QUrl.fromLocalFile(target))
                return
            if self._play_rect().contains(pos):
                target = self.out_path if (st == DONE and self.out_path) else self.path
                if target and os.path.exists(target):
                    QDesktopServices.openUrl(QUrl.fromLocalFile(target))
                return
        if st == DONE and self.out_path:
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.out_path))

    def mouseDoubleClickEvent(self, e):
        target = self.out_path if (self.status == DONE and self.out_path) else self.path
        if target and os.path.exists(target):
            QDesktopServices.openUrl(QUrl.fromLocalFile(target))

    def _draw_mini_circle_btn(self, p: QPainter, rect: QRectF, kind: str, hovered: bool, col: QColor):
        draw_glow(p, rect, 16, col, 0.85 * (1.0 if hovered else 0.0), 5)
        p.setPen(QPen(rgba(col, 0.7 if hovered else 0.28), 1.2))
        p.setBrush(rgba(col if hovered else QColor(255, 255, 255), 0.25 if hovered else 0.06))
        p.drawEllipse(rect)
        c = rect.center()
        ic_col = QColor(255, 255, 255) if hovered else MUTED
        p.setPen(QPen(ic_col, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        if kind == "rm":
            q = 4.2
            p.drawLine(QPointF(c.x() - q, c.y() - q), QPointF(c.x() + q, c.y() + q))
            p.drawLine(QPointF(c.x() - q, c.y() + q), QPointF(c.x() + q, c.y() - q))
        elif kind == "dir":
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(QRectF(c.x() - 5, c.y() - 3.5, 10, 7), 1.5, 1.5)
            p.drawLine(QPointF(c.x() - 4, c.y() - 5), QPointF(c.x() - 1, c.y() - 5))
        elif kind == "play":
            tri = QPainterPath()
            tri.moveTo(c.x() - 2.5, c.y() - 4.5)
            tri.lineTo(c.x() + 4.5, c.y())
            tri.lineTo(c.x() - 2.5, c.y() + 4.5)
            tri.closeSubpath()
            p.setPen(Qt.NoPen)
            p.setBrush(ic_col)
            p.drawPath(tri)

    def paintEvent(self, _):
        t = clock().t
        dt = min(0.05, t - self._lt)
        self._lt = t
        self.shown += (self.target - self.shown) * min(1.0, dt * 9)
        a = self._appear
        p = QPainter(self)
        _aa(p)
        p.setOpacity(clamp(a))
        p.translate(0, (1 - a) * 16)
        r = QRectF(self.rect()).adjusted(3, 4, -3, -4)
        st = self.status

        accent = {QUEUED: PURPLE, PROCESSING: CYAN, DONE: GREEN, FAILED: RED, SKIPPED: AMBER}[st]

        if st == PROCESSING:
            draw_glow(p, r, 18, CYAN, 0.85 + 0.3 * math.sin(t * 3.0), 9)
        elif st == DONE:
            draw_glow(p, r, 18, GREEN, 0.35, 7)

        bg = QLinearGradient(r.topLeft(), r.bottomRight())
        bg.setColorAt(0, QColor(18, 11, 36, 220))
        bg.setColorAt(1, QColor(8, 5, 18, 240))
        p.setBrush(bg)
        p.setPen(QPen(rgba(accent, 0.65 if st == PROCESSING else 0.30), 1.3))
        p.drawRoundedRect(r, 18, 18)

        blade = QRectF(r.left(), r.top() + 10, 4, r.height() - 20)
        draw_glow(p, blade, 2, accent, 1.2, 5)
        p.setPen(Qt.NoPen)
        p.setBrush(accent)
        p.drawRoundedRect(blade, 2, 2)

        ic = QPointF(r.left() + 42, r.top() + 32)
        s = 22.0
        ig = QLinearGradient(ic.x() - s, ic.y() - s, ic.x() + s, ic.y() + s)
        ig.setColorAt(0, rgba(accent, 0.65))
        ig.setColorAt(1, rgba(mix(accent, VIOLET, 0.5), 0.20))
        p.setPen(Qt.NoPen)
        p.setBrush(ig)
        p.drawEllipse(ic, s, s)

        if st == PROCESSING:
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(QColor(255, 255, 255, 235), 3, Qt.SolidLine, Qt.RoundCap))
            p.drawArc(QRectF(ic.x() - s - 3, ic.y() - s - 3, 2 * s + 6, 2 * s + 6), int(-t * 320 * 16), 110 * 16)
            p.setPen(QPen(rgba(CYAN, 0.7), 1.5))
            p.drawEllipse(ic, s + 3, s + 3)

        p.setPen(Qt.NoPen)
        p.setBrush(QColor(255, 255, 255))
        if st in (DONE, SKIPPED):
            p.setPen(QPen(QColor(255, 255, 255), 3.2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.setBrush(Qt.NoBrush)
            ck = QPainterPath()
            ck.moveTo(ic.x() - 9, ic.y() + 1)
            ck.lineTo(ic.x() - 2, ic.y() + 8)
            ck.lineTo(ic.x() + 10, ic.y() - 7)
            p.drawPath(ck)
        elif st == FAILED:
            p.setPen(QPen(QColor(255, 255, 255), 3.2, Qt.SolidLine, Qt.RoundCap))
            p.drawLine(QPointF(ic.x(), ic.y() - 8), QPointF(ic.x(), ic.y() + 2))
            p.drawPoint(QPointF(ic.x(), ic.y() + 9))
        else:
            tri = QPainterPath()
            tri.moveTo(ic.x() - 6, ic.y() - 9)
            tri.lineTo(ic.x() + 10, ic.y())
            tri.lineTo(ic.x() - 6, ic.y() + 9)
            tri.closeSubpath()
            p.drawPath(tri)

        left = r.left() + 78
        right_w = 225 if st in (DONE, SKIPPED, FAILED) else 140
        avail = max(80, int(r.right() - left - right_w))
        p.setPen(TEXT)
        p.setFont(font(14, True))
        fm = QFontMetrics(p.font())
        p.drawText(QRectF(left, r.top() + 11, avail, 22), Qt.AlignLeft | Qt.AlignVCenter,
                   fm.elidedText(os.path.basename(self.path), Qt.ElideMiddle, avail))

        info = self.info
        if st == QUEUED:
            sub = f"{info.width}×{info.height}  ·  {fmt_time(info.duration)}  ·  {human_size(info.size)}"
            subc = MUTED
        elif st == PROCESSING:
            sub = (f"{self.speed:.1f}×  ·  {tr('eta')} {fmt_time(self.eta)}" if self.speed > 0
                   else tr("preparing"))
            subc = mix(CYAN, TEXT, 0.4)
        elif st == DONE:
            sub = f"{human_size(self.in_size)}  →  {human_size(self.out_size)}"
            subc = mix(GREEN, TEXT, 0.4)
        elif st == SKIPPED:
            sub = tr("already_small")
            subc = AMBER
        else:
            sub = self.err or tr("failed")
            subc = RED
        p.setPen(subc)
        p.setFont(font(11.5))
        fm = QFontMetrics(p.font())
        p.drawText(QRectF(left, r.top() + 34, avail, 18), Qt.AlignLeft | Qt.AlignVCenter,
                   fm.elidedText(sub, Qt.ElideRight, avail))

        if st == PROCESSING:
            rr = QRectF(r.right() - 120, r.top() + 12, 108, 34)
            p.setPen(CYAN)
            p.setFont(font(24, True))
            p.drawText(rr, Qt.AlignRight | Qt.AlignVCenter, f"{int(self.shown * 100)}%")
        else:
            if st in (DONE, SKIPPED, FAILED):
                col, txt = ((GREEN, f"−{self.saved_ratio * 100:.0f}%") if st == DONE else
                            (AMBER, tr("optimal_badge")) if st == SKIPPED else (RED, tr("failed_badge")))
                br = self._badge_rect()
                draw_glow(p, br, 15, col, 0.75, 6)
                p.setPen(QPen(rgba(col, 0.8), 1.2))
                p.setBrush(QColor(18, 10, 32, 210))
                p.drawRoundedRect(br, 15, 15)
                p.setPen(mix(col, QColor(255, 255, 255), 0.4))
                p.setFont(font(13, True))
                p.drawText(br, Qt.AlignCenter, txt)

            # Per-card quick action buttons: Play, Open Folder, Remove
            self._draw_mini_circle_btn(p, self._play_rect(), "play", self._play_hover, CYAN)
            self._draw_mini_circle_btn(p, self._dir_rect(), "dir", self._dir_hover, PURPLE)
            self._draw_mini_circle_btn(p, self._rm_rect(), "rm", self._rm_hover and self.removable, RED)

        bar = QRectF(left, r.bottom() - 17, r.right() - left - 20, 6)
        if st == PROCESSING:
            draw_bar(p, bar, self.shown, t, PURPLE, CYAN, 1.2)
        elif st == DONE:
            draw_bar(p, bar, 1.0, t, GREEN, CYAN, 0.7)
        elif st == SKIPPED:
            draw_bar(p, bar, 1.0, t, AMBER, AMBER, 0.3)
        elif st == FAILED:
            draw_bar(p, bar, 1.0, t, RED, MAGENTA, 0.4)
        else:
            draw_bar(p, bar, 0.0, t, PURPLE, CYAN)


# =========================================================================== STATS DASHBOARD
class StatsWidget(QWidget):
    """Gaming HUD Telemetry Ribbon with illuminated live counters and laser tracking bar."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._din = 0.0
        self._dout = 0.0
        self._overall = 0.0
        self.files_done = 0
        self.files_total = 0
        self.setMinimumHeight(88)

    def _g1(self):
        return self._din

    def _s1(self, v):
        self._din = v
        self.update()

    din = Property(float, _g1, _s1)

    def _g2(self):
        return self._dout

    def _s2(self, v):
        self._dout = v
        self.update()

    dout = Property(float, _g2, _s2)

    def _g3(self):
        return self._overall

    def _s3(self, v):
        self._overall = v
        self.update()

    overall = Property(float, _g3, _s3)

    def set_totals(self, files_done: int, files_total: int, in_b: int, out_b: int):
        self.files_done, self.files_total = files_done, files_total
        animate(self, "din", float(in_b), 900)
        animate(self, "dout", float(out_b), 900)

    def set_overall(self, v: float, ms: int = 250):
        animate(self, "overall", float(v), ms, QEasingCurve.OutQuad)

    def paintEvent(self, _):
        p = QPainter(self)
        _aa(p)
        t = clock().t
        w, h = self.width(), self.height()
        r = QRectF(1, 1, w - 2, h - 2)

        draw_glass(p, r, 20, CYAN, 0.38)
        draw_bar(p, QRectF(22, h - 13, w - 44, 5), self._overall, t, PURPLE, CYAN, 1.0)

        weights = [0.80, 1.0, 1.15, 1.25]
        unit = (w - 44) / sum(weights)
        saved_ratio = 1 - self._dout / self._din if self._din > 1 and self._dout > 0 else 0.0
        saved_bytes = max(0.0, self._din - self._dout)
        items = [
            (tr("files"), f"{self.files_done} / {self.files_total}", None, TEXT),
            (tr("original"), human_size(self._din), None, TEXT),
            (tr("compressed"), human_size(self._dout), None, mix(CYAN, TEXT, 0.35)),
            (tr("saved"), f"−{saved_ratio * 100:.0f}%" if saved_ratio > 0.001 else "—",
             tr("saved_sub", size=human_size(saved_bytes)) if saved_ratio > 0.001 else None, GREEN),
        ]
        for i, (cap, val, sub, col) in enumerate(items):
            x = 22 + sum(weights[:i]) * unit
            cw = weights[i] * unit
            p.setPen(MUTED)
            p.setFont(font(10, True, 1.2))
            p.drawText(QRectF(x, 8, cw - 6, 16), Qt.AlignLeft | Qt.AlignVCenter,
                       f"◈ {cap.upper()}" if i18n.LANG == "en" else f"◈ {cap}")
            p.setFont(font(22, True))
            if i == 3 and saved_ratio > 0.001:
                gg = QLinearGradient(x, 0, x + 120, 0)
                gg.setColorAt(0, GREEN)
                gg.setColorAt(1, CYAN)
                p.setPen(QPen(QBrush(gg), 1))
            else:
                p.setPen(col)
            p.drawText(QRectF(x, 24, cw - 6, 32), Qt.AlignLeft | Qt.AlignVCenter, val)
            if sub:
                p.setPen(rgba(GREEN, 0.9))
                p.setFont(font(10))
                p.drawText(QRectF(x + 2, 54, cw - 6, 14), Qt.AlignLeft | Qt.AlignVCenter, sub)


# =========================================================================== OVERLAY (CYBER SPARKS + TOAST)
class FxOverlay(QWidget):
    """Cybernetic spark particles and glowing laser toast alerts."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.parts: list[list] = []
        self._lt = clock().t
        self._toast = ""
        self._toast_col = PURPLE
        self._toast_t0 = -99.0

    def show_toast(self, text: str, color: QColor = PURPLE):
        self._toast, self._toast_col, self._toast_t0 = text, color, clock().t
        self.update()

    def burst(self, origin: QPointF, n: int = 150):
        cols = [PURPLE, CYAN, MAGENTA, GREEN, AMBER, QColor(255, 255, 255)]
        for _ in range(n):
            ang = random.uniform(-math.pi * 0.95, -math.pi * 0.05)
            sp = random.uniform(260, 880)
            self.parts.append([origin.x(), origin.y(), math.cos(ang) * sp, math.sin(ang) * sp,
                               random.uniform(0, 6.28), random.uniform(-9, 9), random.choice(cols),
                               random.uniform(5, 10), random.uniform(1.6, 2.8)])
        self.update()

    def paintEvent(self, _):
        t = clock().t
        dt = min(0.05, t - self._lt)
        self._lt = t
        p = QPainter(self)
        _aa(p)
        alive = []
        for q in self.parts:
            q[3] += 1250 * dt
            q[2] *= 1 - 0.9 * dt
            q[0] += q[2] * dt
            q[1] += q[3] * dt
            q[4] += q[5] * dt
            q[8] -= dt * 0.55
            if q[1] < self.height() + 30 and q[8] > 0:
                alive.append(q)
                p.save()
                p.translate(q[0], q[1])
                p.rotate(math.degrees(q[4]))
                p.setOpacity(clamp(q[8]))
                p.setPen(Qt.NoPen)
                p.setBrush(q[6])
                sz = q[7]
                p.drawRoundedRect(QRectF(-sz / 2, -sz / 4, sz, sz / 2), 1.5, 1.5)
                p.restore()
        self.parts = alive

        age = t - self._toast_t0
        if 0 <= age < 4.6:
            slide = clamp(age / 0.45)
            fade = clamp((4.6 - age) / 0.5)
            slide = 1 - (1 - slide) ** 3
            p.setFont(font(14.5, True))
            fm = QFontMetrics(p.font())
            wtxt = fm.horizontalAdvance(self._toast) + 60
            r = QRectF((self.width() - wtxt) / 2, 18 + 70 * slide - 60, wtxt, 46)
            p.setOpacity(fade)
            draw_glow(p, r, 23, self._toast_col, 1.2, 12)
            p.setPen(QPen(rgba(self._toast_col, 0.85), 1.5))
            p.setBrush(QColor(12, 7, 26, 240))
            p.drawRoundedRect(r, 23, 23)
            p.setPen(QColor(255, 255, 255))
            p.drawText(r, Qt.AlignCenter, self._toast)
