"""Mahyar Compressor – main window, tactical buttons, pause/resume, theme switcher, bottom mini-dock, and interactive mouse background."""
from __future__ import annotations

import math
import os
import random
import sys
import time
from pathlib import Path

from PySide6.QtCore import QLocale, QPointF, QRectF, QSettings, QSize, Qt, QUrl, QVariantAnimation
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient, QCursor, QDesktopServices, QIcon, QImage,
                           QLinearGradient, QPainter, QPainterPath, QPen, QPixmap, QRadialGradient)
from PySide6.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel, QMenu, QScrollArea,
                               QSystemTrayIcon, QVBoxLayout, QWidget)

from . import __version__, i18n
from .engine import (Job, Options, VIDEO_EXTS, Worker, detect_hardware_encoder, find_ffmpeg, fmt_time, human_size, probe)
from .i18n import tr
from .theme import (AMBER, BG, BLUE, CYAN, GREEN, MAGENTA, MUTED, PURPLE, RED, TEXT, VIOLET, clamp, clock,
                    draw_bar, draw_glass, draw_glow, draw_logo, font, mix, rgba)
from .widgets import (DONE, FAILED, PROCESSING, QUEUED, SKIPPED, DropZone, FxOverlay, GlassPanel, GlowButton,
                      IconButton, QueueItem, Segmented, SLabel, StatsWidget, ToggleRow)

M = 16          # outer margin in windowed mode
R = 24          # window corner radius
VIDEO_FILTER = "Videos (" + " ".join(f"*{e}" for e in sorted(VIDEO_EXTS)) + ");;All files (*.*)"

# 4 Neon Aurora Themes for the interactive background
THEMES = [
    ("Cyber Ultraviolet", PURPLE, VIOLET, MAGENTA, CYAN),
    ("Matrix Emerald", GREEN, CYAN, QColor(16, 185, 129), QColor(56, 189, 248)),
    ("Crimson Overdrive", RED, MAGENTA, AMBER, PURPLE),
    ("Solar Gold", AMBER, QColor(249, 115, 22), MAGENTA, CYAN),
]


def make_icon() -> QIcon:
    icon = QIcon()
    for s in (16, 24, 32, 48, 64, 128, 256):
        pm = QPixmap(s, s)
        pm.fill(Qt.transparent)
        p = QPainter(pm)
        p.setRenderHints(QPainter.Antialiasing)
        draw_logo(p, QRectF(s * 0.06, s * 0.06, s * 0.88, s * 0.88), 0.0)
        p.end()
        icon.addPixmap(pm)
    return icon


# =========================================================================== FLOATING BOTTOM MINI-DOCK
class MiniDock(QWidget):
    """Floating bottom control pill when the main studio is minimized to bottom."""

    def __init__(self, win: "MainWindow"):
        super().__init__(None)
        self.win = win
        self.setWindowTitle("Mahyar Compressor Dock")
        self.setWindowIcon(win.windowIcon())
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(760, 82)
        self._frac = 0.0

        lay = QHBoxLayout(self)
        lay.setContentsMargins(24, 12, 20, 12)
        lay.setSpacing(8)

        lay.addSpacing(245)

        self.btn_add = GlowButton("add_btn", "ghost", small=True)
        self.btn_add.setFixedWidth(116)
        self.btn_add.clicked.connect(self.win.browse)

        self.btn_pause = IconButton("pause")
        self.btn_pause.setToolTip(tr("pause"))
        self.btn_pause.setVisible(False)
        self.btn_pause.clicked.connect(self.win.on_pause_resume)

        self.btn_action = GlowButton("start", "primary", small=True)
        self.btn_action.setFixedWidth(134)
        self.btn_action.clicked.connect(self.win.on_start)

        self.btn_folder = IconButton("folder")
        self.btn_folder.setToolTip(tr("open_folder"))
        self.btn_folder.clicked.connect(self.win.open_folder)

        self.btn_expand = IconButton("expand")
        self.btn_expand.setToolTip(tr("restore_win"))
        self.btn_expand.clicked.connect(self.win.restore_from_dock)

        self.btn_quit = IconButton("close")
        self.btn_quit.setToolTip(tr("exit_full"))
        self.btn_quit.clicked.connect(self.win.force_quit)

        lay.addWidget(self.btn_add)
        lay.addWidget(self.btn_pause)
        lay.addWidget(self.btn_action)
        lay.addWidget(self.btn_folder)
        lay.addWidget(self.btn_expand)
        lay.addWidget(self.btn_quit)

    def position_at_bottom(self):
        screen = QApplication.primaryScreen()
        if screen:
            scr = screen.availableGeometry()
            x = scr.center().x() - self.width() // 2
            y = scr.bottom() - self.height() - 14
            self.move(x, y)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            child = self.childAt(e.position().toPoint())
            if child is None or child is self:
                if self.windowHandle():
                    self.windowHandle().startSystemMove()

    def mouseDoubleClickEvent(self, _):
        self.win.restore_from_dock()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)
        t = clock().t
        r = QRectF(self.rect()).adjusted(8, 8, -8, -8)

        draw_glass(p, r, r.height() / 2, CYAN, 0.75)

        lr = QRectF(r.left() + 14, r.center().y() - 18, 36, 36)
        draw_logo(p, lr, t)

        p.setPen(TEXT)
        p.setFont(font(14, True))
        p.drawText(QRectF(lr.right() + 12, r.top() + 10, 190, 20),
                   Qt.AlignLeft | Qt.AlignVCenter, "Mahyar Compressor")

        running = self.win.worker is not None
        paused = running and self.win.worker.is_paused
        pct = int(self._frac * 100)
        if paused:
            status_txt = tr("dock_status_paused", done=self.win._run_done, total=self.win._run_total, pct=pct)
            col = AMBER
        elif running:
            status_txt = tr("dock_status_run", done=self.win._run_done, total=self.win._run_total, pct=pct)
            col = CYAN
        else:
            status_txt = tr("dock_status_idle")
            col = MUTED
        p.setPen(col)
        p.setFont(font(10.5, True))
        p.drawText(QRectF(lr.right() + 12, r.top() + 30, 190, 16),
                   Qt.AlignLeft | Qt.AlignVCenter, status_txt)

        bar_r = QRectF(lr.right() + 12, r.bottom() - 12, 180, 5)
        draw_bar(p, bar_r, self._frac if running else 0.0, t, AMBER if paused else PURPLE, CYAN, 1.0)


# =========================================================================== TOP HUD HEADER
class TitleBar(QWidget):
    def __init__(self, win: "MainWindow"):
        super().__init__(win)
        self.win = win
        self.setFixedHeight(70)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(24, 0, 24, 0)
        lay.setSpacing(8)
        lay.addStretch(1)

        self.btn_theme = IconButton("theme")
        self.btn_pin = IconButton("pin")
        self.btn_lang = IconButton("lang")
        self.btn_dock = IconButton("dock")
        self.btn_fs = IconButton("fullscreen")
        self.btn_min = IconButton("min")
        self.btn_close = IconButton("close")

        for b in (self.btn_theme, self.btn_pin, self.btn_lang, self.btn_dock, self.btn_fs, self.btn_min, self.btn_close):
            lay.addWidget(b)

        self.btn_theme.clicked.connect(win.cycle_theme)
        self.btn_pin.clicked.connect(win.toggle_always_on_top)
        self.btn_dock.clicked.connect(win.minimize_to_dock)
        self.btn_fs.clicked.connect(win.toggle_fullscreen)
        self.btn_min.clicked.connect(win.minimize_to_dock)
        self.btn_close.clicked.connect(win.force_quit)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton and not self.win.isFullScreen():
            child = self.childAt(e.position().toPoint())
            if child is None or child is self:
                if self.win.windowHandle():
                    self.win.windowHandle().startSystemMove()

    def mouseDoubleClickEvent(self, _):
        self.win.toggle_fullscreen()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)
        t = clock().t
        lr = QRectF(28, 15, 42, 42)
        draw_glow(p, lr, 13, mix(PURPLE, CYAN, 0.5 + 0.5 * math.sin(t)), 1.15 + 0.3 * math.sin(t * 2), 12)
        draw_logo(p, lr, t)

        path = QPainterPath()
        f = font(26, True)
        path.addText(84, 41, f, "Mahyar Compressor")
        g = QLinearGradient(84 + 80 * math.sin(t * 0.8) - 60, 0, 84 + 260 + 80 * math.sin(t * 0.8), 0)
        g.setSpread(QLinearGradient.ReflectSpread)
        g.setColorAt(0, QColor(255, 255, 255))
        g.setColorAt(0.45, CYAN)
        g.setColorAt(1, PURPLE)
        p.setPen(Qt.NoPen)
        p.setBrush(g)
        p.drawPath(path)

        p.setPen(rgba(MUTED, 0.95))
        p.setFont(font(10.5, True, 2.0))
        tag = f"◈ {tr('tagline').upper()}" if i18n.LANG == "en" else f"◈ {tr('tagline')}"
        p.drawText(QRectF(86, 44, 420, 18), Qt.AlignLeft | Qt.AlignVCenter, tag)

        p.setPen(rgba(CYAN, 0.92))
        p.setFont(font(10.5, True))
        wm = path.boundingRect().right() + 12
        p.drawText(QRectF(wm, 18, 90, 18), Qt.AlignLeft | Qt.AlignVCenter, f"PRO v{__version__}")


# =========================================================================== MAIN STUDIO WINDOW
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("MahyarCompressor", "MahyarCompressor")
        lang = self.settings.value("lang", "")
        if not lang:
            lang = "fa"
        i18n.set_lang(str(lang))

        self.setWindowTitle("Mahyar Compressor")
        self.setWindowIcon(make_icon())
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window | Qt.WindowMinimizeButtonHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.resize(1280, 820)

        self.ffmpeg = find_ffmpeg()
        self.hw_vendor, self.hw_label = detect_hardware_encoder(self.ffmpeg)
        self.items: list[QueueItem] = []
        self.worker: Worker | None = None
        self.jobs_map: dict[int, QueueItem] = {}
        self.outdir = str(self.settings.value("outdir", "") or "")
        self.last_dir = ""
        self._theme_idx = int(self.settings.value("theme_idx", 0) or 0) % len(THEMES)
        self._pinned = False
        self._img: QImage | None = None
        self._glow_pm: QPixmap | None = None
        self._corner_path: QPainterPath | None = None
        self._corner_rect = QRectF()
        self._skip, self._n, self._avg = 1, 0, 4.0
        self._bg: QImage | None = None
        self._bg_t = -1.0
        self._run_total = 0
        self._run_done = 0

        # Initialize dock & tray attributes BEFORE _build_ui()
        self.dock: MiniDock | None = None
        self.tray: QSystemTrayIcon | None = None

        # Smooth mouse-reactive coordinates (normalized 0.0 .. 1.0)
        self._mx, self._my = 0.5, 0.5
        self._tx, self._ty = 0.5, 0.5
        self._mouse_trail: list[list[float]] = []

        rnd = random.Random(19)
        self._stars = [(rnd.random(), rnd.random(), rnd.uniform(0.012, 0.042), rnd.uniform(1.0, 2.5),
                        rnd.uniform(0, 6.28)) for _ in range(64)]

        self._build_ui()
        self.dock = MiniDock(self)
        self._setup_tray()
        self._set_empty_state(animated=False)
        self._load_settings()
        self.retranslate()
        clock().tick.connect(self._on_tick)

    # ------------------------------------------------------------------ Creative HUD Actions (Theme, Pin, Report)
    def cycle_theme(self):
        self._theme_idx = (self._theme_idx + 1) % len(THEMES)
        self._bg_t = -1.0
        self._save()
        name = THEMES[self._theme_idx][0]
        self.fx.show_toast(tr("theme_switched", name=name), THEMES[self._theme_idx][1])
        self.update()

    def toggle_always_on_top(self):
        self._pinned = not self._pinned
        self.titlebar.btn_pin.setActiveState(self._pinned)
        was_vis = self.isVisible()
        was_fs = self.isFullScreen()
        flags = Qt.FramelessWindowHint | Qt.Window | Qt.WindowMinimizeButtonHint
        if self._pinned:
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        if was_vis:
            if was_fs:
                self.showFullScreen()
            else:
                self.showNormal()
        self.fx.show_toast(tr("pin_on") if self._pinned else tr("pin_off"), CYAN if self._pinned else MUTED)

    def copy_report(self):
        done = [it for it in self.items if it.status in (DONE, SKIPPED)]
        tin = sum(i.in_size for i in done)
        tout = sum(i.out_size if i.status == DONE else i.in_size for i in done)
        saved = max(0, tin - tout)
        pct = (1.0 - tout / tin) * 100 if tin > 0 else 0.0
        lines = [
            f"=== Mahyar Compressor PRO v{__version__} Report ===",
            f"Files Processed: {len(done)} / {len(self.items)}",
            f"Total Input: {human_size(tin)}",
            f"Total Output: {human_size(tout)}",
            f"Space Saved: {human_size(saved)} (-{pct:.1f}%)",
        ]
        for it in self.items:
            lines.append(f" • {os.path.basename(it.path)} ({it.info.width}x{it.info.height}, {human_size(it.in_size)})")
        QApplication.clipboard().setText("\n".join(lines))
        self.fx.show_toast(tr("report_copied"), GREEN)

    # ------------------------------------------------------------------ System Tray & Bottom Dock
    def _setup_tray(self):
        self.tray = QSystemTrayIcon(self.windowIcon(), self)
        self.tray.setToolTip("Mahyar Compressor")
        self.tray_menu = QMenu()
        self.tray_menu.setStyleSheet(
            "QMenu{background:#0b061a;color:#f8fafc;border:1px solid #22d3ee;border-radius:10px;padding:6px;}"
            "QMenu::item{padding:8px 22px;border-radius:6px;font-weight:bold;}"
            "QMenu::item:selected{background:rgba(34,211,238,0.22);color:#22d3ee;}"
            "QMenu::separator{height:1px;background:rgba(168,85,247,0.3);margin:4px 8px;}"
        )
        self.act_show = QAction("", self, triggered=self.restore_from_dock)
        self.act_dock = QAction("", self, triggered=self.minimize_to_dock)
        self.act_add = QAction("", self, triggered=self.browse)
        self.act_start = QAction("", self, triggered=self.on_start)
        self.act_pause = QAction("", self, triggered=self.on_pause_resume)
        self.act_folder = QAction("", self, triggered=self.open_folder)
        self.act_quit = QAction("", self, triggered=self.force_quit)

        self.tray_menu.addAction(self.act_show)
        self.tray_menu.addAction(self.act_dock)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(self.act_add)
        self.tray_menu.addAction(self.act_start)
        self.tray_menu.addAction(self.act_pause)
        self.tray_menu.addAction(self.act_folder)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(self.act_quit)

        self.tray.setContextMenu(self.tray_menu)
        self.tray.activated.connect(self._on_tray_activated)
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray.show()

    def _on_tray_activated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self.restore_from_dock()

    def minimize_to_dock(self):
        self.hide()
        if self.dock is not None:
            self.dock.position_at_bottom()
            self.dock.show()
            self.dock.raise_()
        if self.tray is not None and self.tray.isVisible():
            self.tray.showMessage("Mahyar Compressor", tr("tray_minimized_msg"), QSystemTrayIcon.Information, 2200)

    def restore_from_dock(self):
        if self.dock is not None:
            self.dock.hide()
        if self._was_fullscreen:
            self.showFullScreen()
        else:
            self.showNormal()
        self.raise_()
        self.activateWindow()

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self._was_fullscreen = False
            self.root_lay.setContentsMargins(M, M, M, M)
            self.showNormal()
        else:
            self._was_fullscreen = True
            self.root_lay.setContentsMargins(0, 0, 0, 0)
            self.showFullScreen()
        self._glow_pm = None
        self.update()

    def force_quit(self):
        self._force_closing = True
        if self.dock is not None:
            self.dock.close()
        if self.tray is not None:
            self.tray.hide()
        self.close()
        QApplication.quit()

    # ------------------------------------------------------------------ UI REDESIGN (CYBER COCKPIT)
    def _build_ui(self):
        self._was_fullscreen = True
        self._force_closing = False

        self.root_lay = QVBoxLayout(self)
        self.root_lay.setContentsMargins(0, 0, 0, 0)
        self.root_lay.setSpacing(0)

        # 1) Top Cyber Header Bar
        self.titlebar = TitleBar(self)
        self.titlebar.btn_lang.clicked.connect(self._toggle_lang)
        self.root_lay.addWidget(self.titlebar)

        # 2) Top Telemetry Ribbon
        telemetry_wrap = QHBoxLayout()
        telemetry_wrap.setContentsMargins(28, 4, 28, 12)
        self.stats = StatsWidget()
        telemetry_wrap.addWidget(self.stats, 1)
        self.root_lay.addLayout(telemetry_wrap)

        # 3) Main Cockpit Split: Left = Command Deck + Tactical Launchpad | Right = Drop Portal + Queue
        body = QHBoxLayout()
        body.setContentsMargins(28, 0, 28, 24)
        body.setSpacing(22)
        self.root_lay.addLayout(body, 1)

        # ---- Left Column: Command Deck
        panel = GlassPanel()
        panel.setFixedWidth(392)
        pv = QVBoxLayout(panel)
        pv.setContentsMargins(20, 16, 20, 16)
        pv.setSpacing(3)

        self.lbl_quality = SLabel("quality")
        self.seg_preset = Segmented(["p_tiny", "p_bal", "p_high"])
        self.lbl_pdesc = QLabel()
        self.lbl_pdesc.setWordWrap(True)
        self.lbl_pdesc.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.lbl_pdesc.setFixedHeight(30)
        self.lbl_pdesc.setStyleSheet("background:transparent;color:rgba(180,165,225,230);")
        self.lbl_pdesc.setFont(font(11))

        self.lbl_target = SLabel("target_mode")
        self.seg_target = Segmented(["t_none", "t_discord", "t_telegram", "t_web"])

        self.lbl_codec = SLabel("codec")
        self.seg_codec = Segmented(["c_h265", "c_h264"])

        self.lbl_res = SLabel("res")
        self.seg_res = Segmented(["r_orig", "1080p", "720p", "480p"])

        self.lbl_fps = SLabel("fps")
        self.seg_fps = Segmented(["f_orig", "f_60", "f_30"])

        self.tg_gpu = ToggleRow("gpu", "gpu_hint")
        self.tg_mute = ToggleRow("mute", "mute_hint")
        self.tg_turbo = ToggleRow("turbo", "turbo_hint")

        self.lbl_out = SLabel("out")
        out_row = QHBoxLayout()
        out_row.setContentsMargins(0, 0, 0, 0)
        out_row.setSpacing(6)
        self.btn_out = GlowButton("", "ghost", small=True)
        self.btn_out.clicked.connect(self.choose_outdir)
        self.btn_reset = IconButton("reset")
        self.btn_reset.clicked.connect(self.reset_outdir)
        out_row.addWidget(self.btn_out, 1)
        out_row.addWidget(self.btn_reset)

        pv.addWidget(self.lbl_quality)
        pv.addWidget(self.seg_preset)
        pv.addWidget(self.lbl_pdesc)
        pv.addWidget(self.lbl_target)
        pv.addWidget(self.seg_target)
        pv.addWidget(self.lbl_codec)
        pv.addWidget(self.seg_codec)
        pv.addWidget(self.lbl_res)
        pv.addWidget(self.seg_res)
        pv.addWidget(self.lbl_fps)
        pv.addWidget(self.seg_fps)
        pv.addSpacing(2)
        pv.addWidget(self.tg_gpu)
        pv.addWidget(self.tg_mute)
        pv.addWidget(self.tg_turbo)
        pv.addWidget(self.lbl_out)
        pv.addLayout(out_row)
        pv.addStretch(1)

        # Primary Launchpad Row: [LAUNCH / STOP] + [PAUSE / RESUME]
        launch_row = QHBoxLayout()
        launch_row.setSpacing(8)
        self.btn_start = GlowButton("start", "primary")
        self.btn_start.clicked.connect(self.on_start)
        self.btn_pause = GlowButton("pause", "amber")
        self.btn_pause.setFixedWidth(128)
        self.btn_pause.setVisible(False)
        self.btn_pause.clicked.connect(self.on_pause_resume)
        launch_row.addWidget(self.btn_start, 1)
        launch_row.addWidget(self.btn_pause)
        pv.addLayout(launch_row)

        quick_row = QHBoxLayout()
        quick_row.setSpacing(8)
        self.btn_folder = GlowButton("open_folder", "ghost", small=True)
        self.btn_folder.setEnabled(False)
        self.btn_folder.clicked.connect(self.open_folder)
        self.btn_mini = GlowButton("mini_mode", "ghost", small=True)
        self.btn_mini.clicked.connect(self.minimize_to_dock)
        quick_row.addWidget(self.btn_folder, 1)
        quick_row.addWidget(self.btn_mini, 1)
        pv.addLayout(quick_row)

        body.addWidget(panel)

        # ---- Right Column: Holographic Drop Portal + Tactical Queue Matrix
        self.right_stage = QWidget()
        rv = QVBoxLayout(self.right_stage)
        rv.setContentsMargins(0, 0, 0, 0)
        rv.setSpacing(10)

        self.drop = DropZone()
        self.drop.clicked.connect(self.browse)
        rv.addWidget(self.drop, 1)

        # Tactical Queue Action Bar with creative buttons
        self.q_head = QWidget()
        qh = QHBoxLayout(self.q_head)
        qh.setContentsMargins(8, 4, 0, 2)
        qh.setSpacing(6)
        self.q_title = SLabel("queue")
        qh.addWidget(self.q_title)
        qh.addStretch(1)

        self.btn_add_more = GlowButton("add_btn", "ghost", small=True)
        self.btn_add_more.setFixedWidth(122)
        self.btn_add_more.clicked.connect(self.browse)

        self.btn_add_dir = GlowButton("add_folder", "ghost", small=True)
        self.btn_add_dir.setFixedWidth(122)
        self.btn_add_dir.clicked.connect(self.browse_folder)

        self.btn_retry = GlowButton("retry_failed", "ghost", small=True)
        self.btn_retry.setFixedWidth(134)
        self.btn_retry.setVisible(False)
        self.btn_retry.clicked.connect(self.retry_failed)

        self.btn_clear_done = GlowButton("clear_done", "ghost", small=True)
        self.btn_clear_done.setFixedWidth(128)
        self.btn_clear_done.clicked.connect(self.clear_completed)

        self.btn_clear = GlowButton("clear", "ghost", small=True)
        self.btn_clear.setFixedWidth(116)
        self.btn_clear.clicked.connect(self.clear_all)

        self.btn_report = IconButton("copy")
        self.btn_report.setToolTip(tr("copy_report"))
        self.btn_report.clicked.connect(self.copy_report)

        for b in (self.btn_add_more, self.btn_add_dir, self.btn_retry, self.btn_clear_done, self.btn_clear, self.btn_report):
            qh.addWidget(b)
        rv.addWidget(self.q_head)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet(
            "QScrollArea{background:transparent;border:none;}"
            "QScrollArea > QWidget > QWidget{background:transparent;}"
            "QScrollBar:vertical{background:transparent;width:8px;margin:6px 0;}"
            "QScrollBar::handle:vertical{background:rgba(34,211,238,160);border-radius:4px;min-height:30px;}"
            "QScrollBar::handle:vertical:hover{background:rgba(168,85,247,220);}"
            "QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0;}"
            "QScrollBar::add-page:vertical,QScrollBar::sub-page:vertical{background:transparent;}")
        self.scroll.viewport().setAutoFillBackground(False)
        self.list_w = QWidget()
        self.list_w.setAutoFillBackground(False)
        self.list_lay = QVBoxLayout(self.list_w)
        self.list_lay.setContentsMargins(0, 0, 6, 0)
        self.list_lay.setSpacing(4)
        self.list_lay.addStretch(1)
        self.scroll.setWidget(self.list_w)
        self.list_w.setAutoFillBackground(False)
        self.scroll.viewport().setAutoFillBackground(False)
        rv.addWidget(self.scroll, 3)

        body.addWidget(self.right_stage, 1)

        self.seg_preset.changed.connect(lambda i: (self._update_pdesc(), self._save()))
        self.seg_target.changed.connect(lambda i: self._save())
        self.seg_codec.changed.connect(lambda i: self._save())
        self.seg_res.changed.connect(lambda i: self._save())
        self.seg_fps.changed.connect(lambda i: self._save())
        self.tg_gpu.toggled.connect(lambda v: self._save())
        self.tg_mute.toggled.connect(lambda v: self._save())
        self.tg_turbo.toggled.connect(lambda v: self._save())

        self.fx = FxOverlay(self)
        self.fx.setGeometry(self.rect())
        self.fx.raise_()

    # ------------------------------------------------------------------ settings / i18n
    def _load_settings(self):
        s = self.settings
        self.seg_preset.setIndex(int(s.value("preset", 1)), False)
        self.seg_target.setIndex(int(s.value("target", 0)), False)
        self.seg_codec.setIndex(int(s.value("codec", 0)), False)
        self.seg_res.setIndex(int(s.value("res", 0)), False)
        self.seg_fps.setIndex(int(s.value("fps", 0)), False)
        self.tg_gpu.setChecked(str(s.value("gpu", "false")) == "true", False)
        self.tg_mute.setChecked(str(s.value("mute", "false")) == "true", False)
        self.tg_turbo.setChecked(str(s.value("turbo", "false")) == "true", False)

    def _save(self):
        s = self.settings
        s.setValue("preset", self.seg_preset.index())
        s.setValue("target", self.seg_target.index())
        s.setValue("codec", self.seg_codec.index())
        s.setValue("res", self.seg_res.index())
        s.setValue("fps", self.seg_fps.index())
        s.setValue("gpu", "true" if self.tg_gpu.state else "false")
        s.setValue("mute", "true" if self.tg_mute.state else "false")
        s.setValue("turbo", "true" if self.tg_turbo.state else "false")
        s.setValue("outdir", self.outdir)
        s.setValue("lang", i18n.LANG)
        s.setValue("theme_idx", self._theme_idx)

    def _update_pdesc(self):
        self.lbl_pdesc.setText(tr(("pd_tiny", "pd_bal", "pd_high")[self.seg_preset.index()]))

    def _toggle_lang(self):
        i18n.set_lang("fa" if i18n.LANG == "en" else "en")
        self._save()
        self.retranslate()

    def retranslate(self):
        self.titlebar.btn_lang.label = "FA" if i18n.LANG == "en" else "EN"
        self.titlebar.btn_theme.setToolTip(tr("theme_btn"))
        self.titlebar.btn_pin.setToolTip(tr("pin_top"))
        self.titlebar.btn_dock.setToolTip(tr("mini_mode"))
        self.titlebar.btn_fs.setToolTip(tr("fullscreen"))
        self.titlebar.btn_close.setToolTip(tr("exit_full"))
        self.titlebar.update()

        if hasattr(self, "act_show"):
            self.act_show.setText(tr("tray_show"))
            self.act_dock.setText(tr("mini_mode"))
            self.act_add.setText(tr("tray_add"))
            self.act_start.setText(tr("tray_start"))
            self.act_pause.setText(tr("tray_pause"))
            self.act_folder.setText(tr("tray_folder"))
            self.act_quit.setText(tr("tray_quit"))

        for w in (self.q_title, self.lbl_quality, self.lbl_target, self.lbl_codec,
                  self.lbl_res, self.lbl_fps, self.lbl_out):
            w.retranslate()
        self.lbl_pdesc.setFont(font(11))
        self._update_pdesc()
        if self.hw_vendor:
            self.tg_gpu.hint_key = tr("gpu_detected", vendor=self.hw_label)
        else:
            self.tg_gpu.hint_key = tr("gpu_none")
        for w in (self.tg_gpu, self.tg_mute, self.tg_turbo, self.seg_preset, self.seg_target,
                  self.seg_codec, self.seg_res, self.seg_fps, self.btn_start, self.btn_pause,
                  self.btn_folder, self.btn_mini, self.btn_clear, self.btn_clear_done,
                  self.btn_retry, self.btn_add_more, self.btn_add_dir, self.btn_report,
                  self.drop, self.stats):
            w.update()
        if self.dock is not None:
            self.dock.update()
        for it in self.items:
            it.update()
        self._refresh_out_btn()
        self.update()

    def _refresh_out_btn(self):
        self.btn_out.setLabelFn(lambda: ("📁  " + (Path(self.outdir).name or self.outdir)) if self.outdir
                                else "📁  " + tr("out_same"))
        self.btn_reset.setVisible(bool(self.outdir))

    # ------------------------------------------------------------------ Interactive Mouse-Reactive Background
    def _on_tick(self):
        if self.dock is not None and self.dock.isVisible():
            self.dock.update()
        if self.isMinimized() or not self.isVisible():
            return

        gp = self.mapFromGlobal(QCursor.pos())
        w, h = max(1, self.width()), max(1, self.height())
        self._tx = clamp(gp.x() / w, 0.0, 1.0)
        self._ty = clamp(gp.y() / h, 0.0, 1.0)
        dx = self._tx - self._mx
        dy = self._ty - self._my
        self._mx += dx * 0.14
        self._my += dy * 0.14

        if abs(dx) + abs(dy) > 0.002:
            self._mouse_trail.append([self._mx * w, self._my * h, 1.0])
            if len(self._mouse_trail) > 22:
                self._mouse_trail.pop(0)

        for pt in self._mouse_trail:
            pt[2] -= 0.045
        self._mouse_trail = [pt for pt in self._mouse_trail if pt[2] > 0]

        self._n += 1
        if self._n % self._skip:
            return
        t0 = time.perf_counter()
        self.repaint()
        ms = (time.perf_counter() - t0) * 1000
        self._avg += (ms - self._avg) * 0.12
        self._skip = 1 if self._avg < 8 else 2 if self._avg < 16 else 3

    def resizeEvent(self, e):
        self.fx.setGeometry(self.rect())
        self._glow_pm = None
        super().resizeEvent(e)

    def _make_glow_pixmap(self) -> QPixmap:
        pm = QPixmap(self.size())
        pm.fill(Qt.transparent)
        if self.isFullScreen():
            return pm
        p = QPainter(pm)
        p.setRenderHints(QPainter.Antialiasing)
        inner = QRectF(self.rect()).adjusted(M, M, -M, -M)
        _, c1, c2, _, c4 = THEMES[self._theme_idx]
        g = QLinearGradient(0, 0, self.width(), self.height())
        g.setColorAt(0, c1)
        g.setColorAt(0.5, c2)
        g.setColorAt(1, c4)
        for i in range(M, 0, -1):
            f = 1 - i / (M + 1.0)
            pen = QPen(QBrush(g), i * 2.2)
            op = 0.16 * f * f
            p.setOpacity(op)
            p.setPen(pen)
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(inner, R + i * 0.5, R + i * 0.5)
        p.end()
        return pm

    def _aurora(self, w: int, h: int, t: float) -> QImage:
        s = 0.22
        iw, ih = max(4, int(w * s)), max(4, int(h * s))
        if self._img is None or self._img.size() != QSize(iw, ih):
            self._img = QImage(iw, ih, QImage.Format_ARGB32_Premultiplied)
        img = self._img
        img.fill(BG)
        q = QPainter(img)
        q.setRenderHint(QPainter.Antialiasing)

        ox = (self._mx - 0.5) * 0.28
        oy = (self._my - 0.5) * 0.28
        _, c1, c2, c3, c4 = THEMES[self._theme_idx]

        blobs = (
            (c1, 0.20 + ox, 0.18 + oy, 0.62, 0.13, 0.0),
            (c2, 0.80 - ox, 0.22 + oy, 0.65, 0.10, 1.7),
            (c3, 0.68 + ox * 0.7, 0.86 - oy, 0.58, 0.12, 3.1),
            (c4, 0.14 - ox, 0.82 - oy * 0.7, 0.55, 0.09, 4.6),
            (c4, self._mx, self._my, 0.46, 0.0, 0.0),
        )
        for col, cx, cy, rf, sp, ph in blobs:
            x = (cx + (0.18 * math.sin(t * sp * 2 + ph) if sp > 0 else 0)) * iw
            y = (cy + (0.16 * math.cos(t * sp * 2.6 + ph * 1.7) if sp > 0 else 0)) * ih
            r = rf * max(iw, ih)
            g = QRadialGradient(x, y, r)
            g.setColorAt(0, rgba(col, 0.52))
            g.setColorAt(0.55, rgba(col, 0.18))
            g.setColorAt(1, rgba(col, 0.0))
            q.setPen(Qt.NoPen)
            q.setBrush(g)
            q.drawEllipse(QPointF(x, y), r, r)
        q.end()
        return img

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        t = clock().t
        fs = self.isFullScreen()
        inner = QRectF(self.rect()) if fs else QRectF(self.rect()).adjusted(M, M, -M, -M)
        _, c1, c2, c3, c4 = THEMES[self._theme_idx]

        if self._bg is None or self._bg.size() != inner.size().toSize() or t - self._bg_t > 0.035:
            if self._bg is None or self._bg.size() != inner.size().toSize():
                self._bg = QImage(inner.size().toSize(), QImage.Format_ARGB32_Premultiplied)
            bq = QPainter(self._bg)
            bq.setRenderHint(QPainter.SmoothPixmapTransform)
            bq.drawImage(QRectF(self._bg.rect()), self._aurora(self._bg.width(), self._bg.height(), t))
            bq.fillRect(self._bg.rect(), QColor(4, 2, 10, 125))
            bq.end()
            self._bg_t = t
        p.drawImage(inner.topLeft(), self._bg)

        mx_px = inner.left() + self._mx * inner.width()
        my_px = inner.top() + self._my * inner.height()
        spot = QRadialGradient(mx_px, my_px, 340)
        spot.setColorAt(0.0, rgba(c4, 0.16))
        spot.setColorAt(0.45, rgba(c1, 0.08))
        spot.setColorAt(1.0, rgba(c1, 0.0))
        p.setPen(Qt.NoPen)
        p.setBrush(spot)
        p.drawEllipse(QPointF(mx_px, my_px), 340, 340)

        for tx, ty, life in self._mouse_trail:
            p.setBrush(rgba(c4, life * 0.25))
            p.drawEllipse(QPointF(tx, ty), 8 * life, 8 * life)

        star_pts = []
        p.setPen(Qt.NoPen)
        for i, (x, y, spd, size, ph) in enumerate(self._stars):
            yy = (y - t * spd + (self._my - 0.5) * 0.06 * spd * 25) % 1.0
            xx = (x + 0.012 * math.sin(t * 0.6 + ph) + (self._mx - 0.5) * 0.06 * spd * 25) % 1.0
            sx = inner.left() + xx * inner.width()
            sy = inner.top() + yy * inner.height()
            star_pts.append((sx, sy))
            a = 0.25 + 0.48 * (0.5 + 0.5 * math.sin(t * 1.8 + ph))
            spark_col = c4 if i % 3 == 0 else c1 if i % 3 == 1 else QColor(255, 255, 255)
            p.setBrush(QColor(spark_col.red(), spark_col.green(), spark_col.blue(), int(255 * a)))
            p.drawEllipse(QPointF(sx, sy), size, size)

        for sx, sy in star_pts:
            dist = math.hypot(sx - mx_px, sy - my_px)
            if dist < 170:
                alpha = (1.0 - dist / 170.0) * 0.35
                p.setPen(QPen(rgba(c4, alpha), 1.0))
                p.drawLine(QPointF(mx_px, my_px), QPointF(sx, sy))

        if not fs:
            if self._corner_path is None or self._corner_rect != inner:
                cp = QPainterPath()
                cp.addRect(inner.adjusted(-2, -2, 2, 2))
                rr = QPainterPath()
                rr.addRoundedRect(inner, R, R)
                self._corner_path = cp.subtracted(rr)
                self._corner_rect = QRectF(inner)
            p.setCompositionMode(QPainter.CompositionMode_Clear)
            p.fillPath(self._corner_path, Qt.black)
            p.setCompositionMode(QPainter.CompositionMode_SourceOver)

            if self._glow_pm is None:
                self._glow_pm = self._make_glow_pixmap()
            p.setOpacity(0.75 + 0.25 * math.sin(t * 1.8))
            p.drawPixmap(0, 0, self._glow_pm)
            p.setOpacity(1.0)
            cg = QConicalGradient(inner.center(), -(t * 32) % 360)
            for pos, c in ((0.0, c1), (0.25, c2), (0.5, c4), (0.75, c3), (1.0, c1)):
                cg.setColorAt(pos, rgba(c, 0.90))
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(QBrush(cg), 1.8))
            p.drawRoundedRect(inner, R, R)

    # ------------------------------------------------------------------ drag & drop / browse
    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
            self.drop.set_active(True)

    def dragLeaveEvent(self, e):
        self.drop.set_active(False)

    def dropEvent(self, e):
        self.drop.set_active(False)
        paths = [u.toLocalFile() for u in e.mimeData().urls() if u.isLocalFile()]
        self.add_files(paths)
        e.acceptProposedAction()

    def browse(self):
        files, _ = QFileDialog.getOpenFileNames(self, tr("dialog"), self.settings.value("lastdir", ""), VIDEO_FILTER)
        if files:
            self.settings.setValue("lastdir", os.path.dirname(files[0]))
            self.add_files(files)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, tr("dialog_folder"), self.settings.value("lastdir", ""))
        if folder:
            self.settings.setValue("lastdir", folder)
            self.add_files([folder])

    # ------------------------------------------------------------------ queue management
    def add_files(self, paths: list[str]):
        if not self.ffmpeg:
            self.fx.show_toast(tr("no_ffmpeg"), RED)
            return
        found: list[str] = []
        for p in paths:
            if os.path.isdir(p):
                for root, _, fs in os.walk(p):
                    for f in sorted(fs):
                        if Path(f).suffix.lower() in VIDEO_EXTS:
                            found.append(os.path.join(root, f))
            elif Path(p).suffix.lower() in VIDEO_EXTS and os.path.isfile(p):
                found.append(p)
        have = {it.path for it in self.items}
        bad = 0
        was_empty = not self.items
        for f in found:
            if f in have:
                continue
            info = probe(self.ffmpeg, f)
            if not info:
                bad += 1
                continue
            have.add(f)
            it = QueueItem(f, info)
            it.removable = self.worker is None
            it.removeRequested.connect(self.remove_item)
            self.list_lay.insertWidget(self.list_lay.count() - 1, it)
            self.items.append(it)
            QApplication.processEvents()
        if bad:
            self.fx.show_toast(tr("bad_files", n=bad), AMBER)
        if was_empty and self.items:
            self._set_has_items()
        self._refresh_stats()

    def remove_item(self, it: QueueItem):
        if it in self.items and self.worker is None:
            self.items.remove(it)
            it.setParent(None)
            it.deleteLater()
            if not self.items:
                self._set_empty_state(animated=True)
            self._refresh_stats()

    def clear_completed(self):
        if self.worker is not None:
            return
        done_items = [it for it in self.items if it.status in (DONE, SKIPPED)]
        for it in done_items:
            self.items.remove(it)
            it.setParent(None)
            it.deleteLater()
        if not self.items:
            self._set_empty_state(animated=True)
        self._refresh_stats()

    def retry_failed(self):
        if self.worker is not None:
            return
        failed_items = [it for it in self.items if it.status == FAILED]
        for it in failed_items:
            it.reset()
        self._refresh_stats()
        if failed_items:
            self.on_start()

    def clear_all(self):
        if self.worker is not None:
            return
        for it in list(self.items):
            self.items.remove(it)
            it.setParent(None)
            it.deleteLater()
        self._set_empty_state(animated=True)
        self._refresh_stats()

    def _anim_drop_height(self, a: int, b: int, on_done=None):
        anim = QVariantAnimation(self)
        anim.setDuration(480)
        anim.setStartValue(a)
        anim.setEndValue(b)
        from PySide6.QtCore import QEasingCurve
        anim.setEasingCurve(QEasingCurve.InOutCubic)
        anim.valueChanged.connect(lambda v: self.drop.setFixedHeight(int(v)))
        if on_done:
            anim.finished.connect(on_done)
        anim.start(QVariantAnimation.DeleteWhenStopped)
        self._drop_anim = anim

    def _set_has_items(self):
        self.q_head.setVisible(True)
        self.scroll.setVisible(True)
        self._anim_drop_height(max(self.drop.height(), 125), 125)

    def _set_empty_state(self, animated: bool):
        self.stats.set_overall(0.0, 500)
        if self.dock is not None:
            self.dock._frac = 0.0
        self.q_head.setVisible(False)
        self.scroll.setVisible(False)

        def free():
            self.drop.setMinimumHeight(110)
            self.drop.setMaximumHeight(16777215)

        if animated:
            self._anim_drop_height(self.drop.height(), self.right_stage.height(), free)
        else:
            free()

    # ------------------------------------------------------------------ options / output
    def choose_outdir(self):
        d = QFileDialog.getExistingDirectory(self, tr("dialog_out"), self.outdir or "")
        if d:
            self.outdir = d
            self._save()
            self._refresh_out_btn()

    def reset_outdir(self):
        self.outdir = ""
        self._save()
        self._refresh_out_btn()

    def current_options(self) -> Options:
        target_mb = [0.0, 25.0, 50.0, 10.0][self.seg_target.index()]
        return Options(
            preset=self.seg_preset.index(),
            codec=self.seg_codec.index(),
            res=self.seg_res.index(),
            fps=self.seg_fps.index(),
            gpu=self.tg_gpu.state,
            mute=self.tg_mute.state,
            turbo=self.tg_turbo.state,
            hw_vendor=self.hw_vendor,
            target_mb=target_mb,
        )

    @staticmethod
    def _unique(dst: Path, used: set) -> Path:
        n, cand = 2, dst
        while cand.exists() or str(cand) in used:
            cand = dst.with_name(f"{dst.stem}_{n}{dst.suffix}")
            n += 1
        used.add(str(cand))
        return cand

    # ------------------------------------------------------------------ Pause / Resume & Run
    def on_pause_resume(self):
        if self.worker is None:
            return
        paused = self.worker.toggle_pause()
        self.btn_pause.setKey("resume" if paused else "pause")
        if self.dock is not None:
            self.dock.btn_pause.setKind("play" if paused else "pause")
            self.dock.btn_pause.setToolTip(tr("resume" if paused else "pause"))
            self.dock.update()
        self.fx.show_toast(tr("paused_toast" if paused else "resumed_toast"), AMBER if paused else CYAN)

    def on_start(self):
        if self.worker is not None:
            self.btn_start.setKey("stopping")
            self.btn_start.setEnabled(False)
            self.btn_pause.setVisible(False)
            if self.dock is not None:
                self.dock.btn_action.setKey("stopping")
                self.dock.btn_action.setEnabled(False)
                self.dock.btn_pause.setVisible(False)
            self.worker.cancel()
            return
        todo = [it for it in self.items if it.status in (QUEUED, FAILED)]
        if not todo:
            self.fx.show_toast(tr("nothing"), AMBER)
            return
        if not self.ffmpeg:
            self.fx.show_toast(tr("no_ffmpeg"), RED)
            return
        used: set[str] = set()
        jobs: list[Job] = []
        self.jobs_map = {}
        for i, it in enumerate(todo):
            folder = Path(self.outdir) if self.outdir else Path(it.path).parent
            try:
                folder.mkdir(parents=True, exist_ok=True)
            except OSError:
                pass
            dst = self._unique(folder / f"{Path(it.path).stem}_mahyar.mp4", used)
            jobs.append(Job(i, it.path, str(dst), it.info))
            self.jobs_map[i] = it
            it.reset()
        for it in self.items:
            it.removable = False
        self._run_total, self._run_done = len(jobs), 0
        self.stats.set_overall(0.0, 200)
        if self.dock is not None:
            self.dock._frac = 0.0
        self.worker = Worker(self.ffmpeg, jobs, self.current_options(), self)
        self.worker.started_file.connect(lambda j: self.jobs_map[j].set_processing())
        self.worker.progress.connect(self._on_progress)
        self.worker.finished_file.connect(self._on_file_done)
        self.worker.failed_file.connect(self._on_file_failed)
        self.worker.gpu_fallback.connect(lambda j: self.fx.show_toast(tr("gpu_fallback"), AMBER))
        self.worker.all_done.connect(self._on_all_done)
        self.btn_start.setKey("stop")
        self.btn_start.setVariant("danger")
        self.btn_pause.setKey("pause")
        self.btn_pause.setVisible(True)
        if self.dock is not None:
            self.dock.btn_action.setKey("stop")
            self.dock.btn_action.setVariant("danger")
            self.dock.btn_pause.setKind("pause")
            self.dock.btn_pause.setVisible(True)
        self.btn_folder.setEnabled(False)
        self.worker.start()

    def _on_progress(self, jid, frac, speed, eta):
        it = self.jobs_map.get(jid)
        if it:
            it.set_progress(frac, speed, eta)
        ov = (self._run_done + frac) / max(1, self._run_total)
        self.stats.set_overall(ov, 180)
        if self.dock is not None:
            self.dock._frac = ov

    def _on_file_done(self, jid, out_path, in_size, out_size):
        it = self.jobs_map[jid]
        it.set_done(out_path, in_size, out_size)
        if out_path:
            self.last_dir = os.path.dirname(out_path)
        self._run_done += 1
        ov = self._run_done / max(1, self._run_total)
        self.stats.set_overall(ov, 400)
        if self.dock is not None:
            self.dock._frac = ov
        self._refresh_stats()

    def _on_file_failed(self, jid, msg):
        self.jobs_map[jid].set_failed(msg)
        self._run_done += 1
        ov = self._run_done / max(1, self._run_total)
        self.stats.set_overall(ov, 400)
        if self.dock is not None:
            self.dock._frac = ov
        self._refresh_stats()

    def _on_all_done(self, cancelled: bool):
        w, self.worker = self.worker, None
        if w:
            w.wait(2000)
            w.deleteLater()
        for it in self.items:
            it.removable = True
            if it.status == PROCESSING:
                it.reset()
        self.btn_start.setEnabled(True)
        self.btn_start.setKey("start")
        self.btn_start.setVariant("primary")
        self.btn_pause.setVisible(False)
        if self.dock is not None:
            self.dock.btn_action.setEnabled(True)
            self.dock.btn_action.setKey("start")
            self.dock.btn_action.setVariant("primary")
            self.dock.btn_pause.setVisible(False)
        self.btn_folder.setEnabled(bool(self.last_dir))
        self._refresh_stats()
        if cancelled:
            self.stats.set_overall(0.0, 300)
            if self.dock is not None:
                self.dock._frac = 0.0
            self.fx.show_toast(tr("stopped"), AMBER)
            return
        saved = sum(max(0, it.in_size - it.out_size) for it in self.items if it.status == DONE)
        if any(it.status == DONE for it in self.items):
            self.fx.burst(QPointF(self.width() * 0.3, self.height() * 0.7), 160)
            self.fx.burst(QPointF(self.width() * 0.7, self.height() * 0.6), 110)
            self.fx.show_toast(tr("all_done", size=human_size(saved)), GREEN)
        elif any(it.status == FAILED for it in self.items):
            self.fx.show_toast(tr("failed"), RED)

    def _refresh_stats(self):
        done = [it for it in self.items if it.status in (DONE, SKIPPED)]
        has_failed = any(it.status == FAILED for it in self.items)
        self.btn_retry.setVisible(has_failed and self.worker is None)
        self.stats.set_totals(len(done), len(self.items), sum(i.in_size for i in done),
                              sum(i.out_size if i.status == DONE else i.in_size for i in done))

    def open_folder(self):
        target = self.last_dir or self.outdir
        if target and os.path.exists(target):
            QDesktopServices.openUrl(QUrl.fromLocalFile(target))

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_O and e.modifiers() & Qt.ControlModifier:
            self.browse()
            e.accept()
        elif e.key() == Qt.Key_F11:
            self.toggle_fullscreen()
            e.accept()
        elif e.key() == Qt.Key_P and e.modifiers() & Qt.ControlModifier:
            self.on_pause_resume()
            e.accept()
        elif e.key() in (Qt.Key_Return, Qt.Key_Enter) and not (e.modifiers() & Qt.AltModifier):
            self.on_start()
            e.accept()
        elif e.key() == Qt.Key_Escape:
            if self.worker is not None:
                self.on_start()
            elif self.isFullScreen():
                self.toggle_fullscreen()
            else:
                self.minimize_to_dock()
            e.accept()
        else:
            super().keyPressEvent(e)

    def closeEvent(self, e):
        if self.worker:
            self.worker.cancel()
            self.worker.wait(4000)
        if self.dock is not None:
            self.dock.close()
        if self.tray is not None:
            self.tray.hide()
        self._save()
        super().closeEvent(e)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Mahyar Compressor")
    app.setQuitOnLastWindowClosed(False)
    app.setStyle("Fusion")
    app.setWindowIcon(make_icon())
    win = MainWindow()
    win.showFullScreen()
    args = [a for a in sys.argv[1:] if os.path.exists(a)]
    if args:
        win.add_files(args)
    sys.exit(app.exec())
