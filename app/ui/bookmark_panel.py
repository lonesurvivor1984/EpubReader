"""Bookmark panel — flat list of saved reading positions."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QWidget, QVBoxLayout, QLabel


class BookmarkPanel(QWidget):
    """Sidebar panel displaying saved bookmarks for the current book.

    Clicking a bookmark emits navigate_to with (chapter_href, scroll_offset).
    Right-clicking offers a delete option, emitting remove_bookmark with the bookmark ID.
    """

    navigate_to = Signal(str, int)  # chapter_href, scroll_offset
    remove_bookmark = Signal(str)  # bookmark_id

    def __init__(self) -> None:
        super().__init__()
        self.setMinimumWidth(200)
        self.setMaximumWidth(300)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._label = QLabel("书签")
        self._label.setStyleSheet("font-weight: bold; padding: 4px 8px; font-size: 12px;")
        layout.addWidget(self._label)

        self._list = QListWidget()
        self._list.itemClicked.connect(self._on_clicked)
        self._list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._list.customContextMenuRequested.connect(self._on_context_menu)
        layout.addWidget(self._list)

        self._placeholder = QLabel("暂无书签。\n点击「书签」按钮添加。")
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._placeholder.setStyleSheet("color: #999; padding: 20px;")
        self._placeholder.hide()
        layout.addWidget(self._placeholder)

        # Internal book title lookup: {chapter_href: title}
        self._chapter_titles: dict[str, str] = {}

    def populate(
        self,
        bookmarks: list,
        chapter_titles: dict[str, str] | None = None,
    ) -> None:
        """Populate the list from bookmark dataclass list.

        bookmarks: list of Bookmark (id, chapter_href, scroll_offset, created_at)
        chapter_titles: {chapter_href: chapter_title} for display
        """
        self._list.clear()
        self._chapter_titles = chapter_titles or {}

        if not bookmarks:
            self._placeholder.show()
            return

        self._placeholder.hide()

        for bm in bookmarks:
            title = self._chapter_titles.get(bm.chapter_href, bm.chapter_href)
            item_text = f"{title}"
            if bm.created_at:
                # Show date and time
                dt = bm.created_at[:19] if len(bm.created_at) >= 19 else bm.created_at
                item_text += f"\n{dt.replace('T', ' ')}"

            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, bm.id)
            item.setData(Qt.ItemDataRole.UserRole + 1, bm.chapter_href)
            item.setData(Qt.ItemDataRole.UserRole + 2, bm.scroll_offset)
            self._list.addItem(item)

    def add_bookmark_item(self, bookmark, chapter_title: str = "") -> None:
        """Add a single bookmark to the top of the list."""
        title = chapter_title or self._chapter_titles.get(bookmark.chapter_href, bookmark.chapter_href)

        item_text = title
        if bookmark.created_at:
            dt = bookmark.created_at[:19] if len(bookmark.created_at) >= 19 else bookmark.created_at
            item_text += f"\n{dt.replace('T', ' ')}"

        item = QListWidgetItem(item_text)
        item.setData(Qt.ItemDataRole.UserRole, bookmark.id)
        item.setData(Qt.ItemDataRole.UserRole + 1, bookmark.chapter_href)
        item.setData(Qt.ItemDataRole.UserRole + 2, bookmark.scroll_offset)
        self._list.insertItem(0, item)
        self._placeholder.hide()

    def remove_bookmark_item(self, bookmark_id: str) -> None:
        """Remove a bookmark by ID from the list."""
        for i in range(self._list.count()):
            item = self._list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == bookmark_id:
                self._list.takeItem(i)
                del item
                break

        if self._list.count() == 0:
            self._placeholder.show()

    def clear(self) -> None:
        """Clear all bookmarks and show placeholder."""
        self._list.clear()
        self._placeholder.show()

    def set_chapter_titles(self, titles: dict[str, str]) -> None:
        """Set chapter title lookup for future populate calls."""
        self._chapter_titles = titles

    def _on_clicked(self, item: QListWidgetItem) -> None:
        href = item.data(Qt.ItemDataRole.UserRole + 1)
        offset = item.data(Qt.ItemDataRole.UserRole + 2)
        if href:
            self.navigate_to.emit(href, offset)

    def _on_context_menu(self, pos) -> None:
        from PySide6.QtWidgets import QMenu, QMessageBox

        item = self._list.itemAt(pos)
        if not item:
            return

        menu = QMenu(self)
        delete_action = menu.addAction("删除书签")
        action = menu.exec(self._list.viewport().mapToGlobal(pos))
        if action == delete_action:
            bm_id = item.data(Qt.ItemDataRole.UserRole)
            if bm_id:
                reply = QMessageBox.question(
                    self, "删除书签", "确定删除该书签？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.remove_bookmark.emit(bm_id)
