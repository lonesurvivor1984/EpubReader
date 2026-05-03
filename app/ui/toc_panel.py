"""TOC Panel — hierarchical tree view for chapter navigation."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QStandardItem, QStandardItemModel, QFont
from PySide6.QtWidgets import QTreeView, QWidget, QVBoxLayout


class TOCPanel(QWidget):
    """Sidebar panel displaying the book's table of contents.

    Clicking a TOC item emits a signal with the href to navigate to.
    """

    navigate_to = Signal(str)  # href

    def __init__(self) -> None:
        super().__init__()
        self.setMinimumWidth(200)
        self.setMaximumWidth(300)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._tree = QTreeView()
        self._tree.setHeaderHidden(True)
        self._tree.setIndentation(16)
        self._tree.clicked.connect(self._on_clicked)

        # Style: remove selection border
        self._tree.setStyleSheet("""
            QTreeView::item:selected {
                background-color: #e0e7ff;
                color: #1e1b4b;
                border-radius: 4px;
            }
            QTreeView { border: none; }
        """)

        layout.addWidget(self._tree)

    def populate(self, toc: list) -> None:
        """Populate the tree from a list of TOCItem dataclasses.

        Each TOCItem has: label, href, children (list of TOCItem).
        """
        self._model = QStandardItemModel()
        self._tree.setModel(self._model)
        self._model.clear()
        self._model.setHorizontalHeaderLabels(["Contents"])

        self._add_items(toc, parent=None)

    def _add_items(self, items: list, parent) -> None:
        for item in items:
            row_item = QStandardItem(item.label)
            row_item.setData(item.href, Qt.ItemDataRole.UserRole)
            row_item.setFont(QFont("Segoe UI", 9))

            if item.children:
                self._add_items(item.children, row_item)

            if parent is None:
                self._model.appendRow(row_item)
            else:
                parent.appendRow(row_item)

    def _on_clicked(self, index) -> None:
        href = index.data(Qt.ItemDataRole.UserRole)
        if href:
            self.navigate_to.emit(href)

    def highlight_current(self, href: str) -> None:
        """Highlight the TOC item matching the given href.

        Uses a simple href match — for more precise tracking,
        an IntersectionObserver would be needed.
        """
        if not hasattr(self, "_model"):
            return

        for row in range(self._model.rowCount()):
            self._highlight_recursive(self._model.item(row), href)

    def _highlight_recursive(self, item: QStandardItem, href: str) -> None:
        item_href = item.data(Qt.ItemDataRole.UserRole)
        if item_href == href:
            # Clear previous highlights
            self._clear_highlights()
            self._tree.setCurrentIndex(item.index())
        for i in range(item.rowCount()):
            self._highlight_recursive(item.child(i), href)

    def _clear_highlights(self) -> None:
        self._tree.clearSelection()
