"""Settings toolbar — inline controls for font size and TOC toggle."""

from __future__ import annotations

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QSizePolicy,
    QSpacerItem, QLabel,
)


THEME_COLORS: list[str] = [
    "#FFF9E6",  # 浅黄
    "#E8F5E9",  # 浅绿
    "#E3F2FD",  # 浅蓝
    "#F5F5F5",  # 浅灰
]


class ColorSwatch(QLabel):
    """Small clickable color block that emits a signal on click."""

    def __init__(self, color: str, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self._color = color
        self.setFixedSize(20, 20)
        self.setStyleSheet(f"background-color: {color}; border: 1px solid #ccc; border-radius: 3px;")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(color)

    def mousePressEvent(self, event) -> None:
        self.parent().theme_selected.emit(self._color)  # type: ignore[attr-defined]
        super().mousePressEvent(event)


class SettingsBar(QWidget):
    """Horizontal toolbar with reading controls."""

    font_increase = Signal()
    font_decrease = Signal()
    font_reset = Signal()
    toc_toggle = Signal()
    bookmark_add = Signal()
    notes_export = Signal()
    theme_selected = Signal(str)
    go_back = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setFixedHeight(36)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        # Back button
        self._btn_back = QPushButton("← 返回")
        self._btn_back.setFixedWidth(70)
        self._btn_back.setMaximumHeight(28)
        self._btn_back.clicked.connect(self.go_back.emit)
        layout.addWidget(self._btn_back)

        layout.addItem(QSpacerItem(20, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        # Font size controls
        self._btn_font_minus = QPushButton("A−")
        self._btn_font_minus.setFixedWidth(36)
        self._btn_font_minus.setMaximumHeight(28)
        self._btn_font_minus.clicked.connect(self.font_decrease.emit)

        self._btn_font_plus = QPushButton("A+")
        self._btn_font_plus.setFixedWidth(36)
        self._btn_font_plus.setMaximumHeight(28)
        self._btn_font_plus.clicked.connect(self.font_increase.emit)

        self._btn_font_reset = QPushButton("重置")
        self._btn_font_reset.setFixedWidth(50)
        self._btn_font_reset.setMaximumHeight(28)
        self._btn_font_reset.clicked.connect(self.font_reset.emit)

        layout.addWidget(self._btn_font_minus)
        layout.addWidget(self._btn_font_plus)
        layout.addWidget(self._btn_font_reset)

        # TOC toggle
        self._btn_toc = QPushButton("目录")
        self._btn_toc.setFixedWidth(45)
        self._btn_toc.setMaximumHeight(28)
        self._btn_toc.clicked.connect(self.toc_toggle.emit)
        layout.addWidget(self._btn_toc)

        # Bookmark button
        self._btn_bookmark = QPushButton("书签")
        self._btn_bookmark.setFixedWidth(45)
        self._btn_bookmark.setMaximumHeight(28)
        self._btn_bookmark.clicked.connect(self.bookmark_add.emit)
        layout.addWidget(self._btn_bookmark)

        # Notes button
        self._btn_notes = QPushButton("导出笔记")
        self._btn_notes.setFixedWidth(65)
        self._btn_notes.setMaximumHeight(28)
        self._btn_notes.clicked.connect(self.notes_export.emit)
        layout.addWidget(self._btn_notes)

        # Separator
        sep = QLabel("|")
        sep.setStyleSheet("color: #ccc;")
        layout.addWidget(sep)

        # Theme color swatches
        self._swatches: list[ColorSwatch] = []
        for color in THEME_COLORS:
            swatch = ColorSwatch(color, self)
            self._swatches.append(swatch)
            layout.addWidget(swatch)
