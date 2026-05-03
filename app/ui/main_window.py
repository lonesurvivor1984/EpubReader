"""Main window — QStackedLayout with bookshelf and reader views."""

from __future__ import annotations

import os

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QCloseEvent, QPainter
from PySide6.QtWidgets import (
    QMainWindow, QStackedWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QMessageBox, QFileDialog, QLabel,
    QSplitter, QApplication, QDialog, QListWidget, QListWidgetItem,
    QDialogButtonBox,
)

from app.config import DATA_DIR
from app.core import storage
from app.core.book_manager import BookManager
from app.core.models import Annotation, Bookmark, ReadingState, UserPreferences
from app.ui.bookshelf import BookshelfView
from app.ui.reader import ReaderView
from app.ui.toc_panel import TOCPanel
from app.ui.settings import SettingsBar
from app.ui.bookmark_panel import BookmarkPanel


class MainWindow(QMainWindow):
    """Top-level application window."""

    VIEW_BOOKSHELF = 0
    VIEW_READER = 1

    def __init__(self, *, open_file: str | None = None) -> None:
        super().__init__()
        self.setWindowTitle("EpubReader")
        self.resize(1100, 750)
        self.setAcceptDrops(True)

        self._manager = BookManager()
        self._current_book_id: str | None = None

        # Restore preferences
        prefs = self._manager.preferences
        self._font_size = prefs.font_size
        self._toc_visible = prefs.toc_visible
        self._theme_color = prefs.theme_color

        self._build_ui()
        self._connect_signals()

        # Show bookshelf
        self._refresh_bookshelf()

        # Open file directly if provided
        if open_file:
            self._open_epub_file(open_file)

    # ── UI Construction ────────────────────────────────────────────────

    def _build_ui(self) -> None:
        # Central stacked widget
        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        # ── Bookshelf page ──
        bookshelf_page = QWidget()
        bookshelf_layout = QVBoxLayout(bookshelf_page)
        bookshelf_layout.setContentsMargins(10, 10, 10, 10)

        # Header bar: title + buttons
        header_bar = QHBoxLayout()
        self._header = QLabel("📚 EpubReader")
        self._header.setStyleSheet("font-size: 22px; font-weight: bold; padding: 10px;")
        header_bar.addWidget(self._header)
        header_bar.addStretch()

        self._btn_txt_convert = QPushButton("TXT格式转换")
        self._btn_txt_convert.setMaximumHeight(32)
        header_bar.addWidget(self._btn_txt_convert)

        bookshelf_layout.addLayout(header_bar)

        self._bookshelf = BookshelfView()
        self._bookshelf.doubleClicked.connect(self._on_book_activated)
        self._bookshelf.add_book_requested.connect(self._on_add_book)
        self._bookshelf.remove_book_requested.connect(self._on_remove_book)
        bookshelf_layout.addWidget(self._bookshelf)

        self._stack.addWidget(bookshelf_page)

        # ── Reader page ──
        reader_page = QWidget()
        reader_layout = QVBoxLayout(reader_page)
        reader_layout.setContentsMargins(0, 0, 0, 0)
        reader_layout.setSpacing(0)

        # Settings bar at top
        self._settings_bar = SettingsBar()
        reader_layout.addWidget(self._settings_bar)

        # Splitter: left panel (TOC + Bookmark) + Reader
        self._splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel: vertical splitter with TOC on top, Bookmarks on bottom
        self._left_splitter = QSplitter(Qt.Orientation.Vertical)
        self._left_splitter.setContentsMargins(0, 0, 0, 0)
        self._toc_panel = TOCPanel()
        self._bookmark_panel = BookmarkPanel()
        self._left_splitter.addWidget(self._toc_panel)
        self._left_splitter.addWidget(self._bookmark_panel)
        # TOC 80%, Bookmarks 20%
        self._left_splitter.setSizes([600, 150])

        self._reader = ReaderView()

        self._splitter.addWidget(self._left_splitter)
        self._splitter.addWidget(self._reader)
        # Left panel ~20%, reader ~80%
        self._splitter.setStretchFactor(0, 1)
        self._splitter.setStretchFactor(1, 4)
        # Set initial sizes (will be respected on first show)
        self._splitter.setSizes([220, 800])

        # Initial TOC visibility
        self._left_splitter.setVisible(self._toc_visible)

        reader_layout.addWidget(self._splitter)

        self._stack.addWidget(reader_page)

    # ── Signal Connections ─────────────────────────────────────────────

    def _connect_signals(self) -> None:
        self._settings_bar.font_increase.connect(self._on_font_increase)
        self._settings_bar.font_decrease.connect(self._on_font_decrease)
        self._settings_bar.font_reset.connect(self._on_font_reset)
        self._settings_bar.toc_toggle.connect(self._on_toc_toggle)
        self._settings_bar.bookmark_add.connect(self._on_bookmark_add)
        self._settings_bar.notes_export.connect(self._on_notes_export)
        self._settings_bar.go_back.connect(self._go_back_to_bookshelf)
        self._toc_panel.navigate_to.connect(self._on_toc_navigate)
        self._bookmark_panel.navigate_to.connect(self._on_bookmark_navigate)
        self._bookmark_panel.remove_bookmark.connect(self._on_bookmark_remove)
        self._reader.scroll_changed.connect(self._on_scroll_changed)
        self._settings_bar.theme_selected.connect(self._on_theme_selected)
        self._reader.annotation_created.connect(self._on_annotation_created)
        self._btn_txt_convert.clicked.connect(self._on_txt_convert)

    # ── Bookshelf ──────────────────────────────────────────────────────

    def _refresh_bookshelf(self) -> None:
        """Reload books from storage and populate the bookshelf view."""
        books = self._manager.list_books()
        entries = []

        for book in books:
            cover = self._load_cover(book.id, book.cover_image_id)
            reading_state = self._manager.load_reading_state(book.id)

            entries.append({
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "progress": reading_state.progress_pct,
                "cover": cover,
                "file_exists": book.is_file_available,
            })

        self._bookshelf.populate_books(entries)
        self._stack.setCurrentIndex(self.VIEW_BOOKSHELF)

    def _load_cover(self, book_id: str, cover_image_id: str | None) -> QPixmap | None:
        """Load cover image from the EPUB file."""
        if not cover_image_id:
            return None

        try:
            from pathlib import Path
            import zipfile
            from app.core.epub_parser import parse_epub, get_resource

            book_entry = None
            for b in self._manager.list_books():
                if b.id == book_id:
                    book_entry = b
                    break
            if not book_entry:
                return None

            parsed = parse_epub(book_entry.file_path)

            # cover_image_id is the manifest item ID, not the href.
            # Look up the href by matching the ID in the OPF manifest.
            from lxml import etree
            cover_href = None
            with zipfile.ZipFile(book_entry.file_path) as zf:
                opf_container = zf.read("META-INF/container.xml")
                container_root = etree.fromstring(opf_container)
                ns = {"ocf": "urn:oasis:names:tc:opendocument:xmlns:container"}
                rootfile = container_root.find(".//ocf:rootfile", ns)
                if rootfile is None:
                    rootfile = container_root.find(".//rootfile")
                if rootfile is not None:
                    opf_file = rootfile.get("full-path", "")
                    opf_data = zf.read(opf_file)
                    opf_tree = etree.fromstring(opf_data)
                    for item in opf_tree.findall(
                        f".//{{http://www.idpf.org/2007/opf}}item"
                    ):
                        if item.get("id") == cover_image_id:
                            cover_href = item.get("href")
                            break
                        # Also match by media-type for cover images
                        if item.get("properties") == "cover-image":
                            cover_href = item.get("href")

                if cover_href:
                    full_path = f"{parsed.opf_base}{cover_href}"
                    data, mime = get_resource(zf, full_path)
                    pixmap = QPixmap()
                    if "svg" in mime or cover_href.endswith(".svg"):
                        from PySide6.QtSvg import QSvgRenderer
                        from PySide6.QtCore import QByteArray
                        renderer = QSvgRenderer(QByteArray(data))
                        if renderer.isValid():
                            pixmap = QPixmap(400, 600)
                            pixmap.fill(Qt.GlobalColor.transparent)
                            painter = QPainter(pixmap)
                            renderer.render(painter)
                            painter.end()
                    else:
                        pixmap.loadFromData(data)
                    if not pixmap.isNull():
                        return pixmap
        except Exception:
            pass
        return None

    def _on_book_activated(self, index) -> None:
        """Handle double-click on a book card."""
        book_id = self._bookshelf.get_book_id_at(index)
        if not book_id:
            return

        book = self._manager.list_books()
        book_entry = None
        for b in book:
            if b.id == book_id:
                book_entry = b
                break

        if book_entry and not book_entry.is_file_available:
            self._handle_missing_file(book_id)
            return

        self._open_book(book_id)

    def _handle_missing_file(self, book_id: str) -> None:
        """Handle a book whose source file is missing."""
        reply = QMessageBox.question(
            self,
            "文件未找到",
            "电子书文件已被移动或删除。是否重新定位？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "定位电子书文件", "", "电子书文件 (*.epub)"
            )
            if file_path:
                self._manager.relocate_book(book_id, file_path)
                self._refresh_bookshelf()

    # ── Reader ─────────────────────────────────────────────────────────

    def _open_book(self, book_id: str) -> None:
        """Open a book in the reader view."""
        book = self._manager.open_book(book_id)
        if not book:
            return

        self._current_book_id = book_id

        # Populate TOC
        if book.toc:
            self._toc_panel.populate(book.toc)
        else:
            # Fall back to flat chapter list
            from app.core.models import TOCItem
            toc_items = [TOCItem(label=ch.title or ch.href, href=ch.href) for ch in book.chapters]
            self._toc_panel.populate(toc_items)

        # Apply saved preferences
        self._reader.set_font_size(self._font_size)

        # Populate bookmarks
        bookmarks = self._manager.get_bookmarks(book_id)
        chapter_titles = {ch.href: (ch.title or ch.href) for ch in book.chapters}
        self._bookmark_panel.set_chapter_titles(chapter_titles)
        self._bookmark_panel.populate(bookmarks, chapter_titles)

        # Restore reading position
        chapter_hrefs = [ch.href for ch in book.chapters]
        loaded_href = ""
        state = self._manager.load_reading_state(book_id)
        if state.chapter_href and book.chapters:
            url = self._manager.get_chapter_url(book_id, state.chapter_href)
            self._reader.load_chapter(url)
            loaded_href = state.chapter_href
            QTimer.singleShot(500, lambda: self._reader.set_scroll_position(state.scroll_offset))
        elif book.toc:
            # Open at the first TOC entry (usually title page)
            first_toc = book.toc[0]
            url = self._manager.get_chapter_url(book_id, first_toc.href)
            self._reader.load_chapter(url)
            loaded_href = first_toc.href
        elif book.chapters:
            url = self._manager.get_chapter_url(book_id, book.chapters[0].href)
            self._reader.load_chapter(url)
            loaded_href = book.chapters[0].href

        # Pass chapter list for seamless scrolling
        if loaded_href and chapter_hrefs:
            self._reader.set_chapter_list(loaded_href, chapter_hrefs)

        # Apply saved font size
        self._reader.set_font_size(self._font_size)

        # Apply saved theme color
        if self._theme_color:
            self._reader.set_background_color(self._theme_color)

        # Load and restore existing annotations
        annotations = storage.load_annotations(book_id)
        if annotations:
            ann_list = [
                {"chapter_href": a.chapter_href, "selected_text": a.selected_text, "note": a.note}
                for a in annotations
            ]
            self._reader.set_annotations(ann_list)

        self._stack.setCurrentIndex(self.VIEW_READER)
        self._reader.start_scroll_tracking()
        self.setWindowTitle(f"EpubReader — {book.title}")

    def _on_add_book(self) -> None:
        """Open file dialog to add an EPUB book."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "添加电子书", "", "电子书文件 (*.epub)"
        )
        if file_path:
            self._open_epub_file(file_path)

    def _open_epub_file(self, file_path: str) -> None:
        """Add an EPUB file to the library and open it."""
        import os
        if not os.path.exists(file_path):
            QMessageBox.critical(self, "错误", f"文件未找到: {file_path}")
            return

        try:
            book = self._manager.add_book(file_path)
            if book:
                self._open_book(book.id)
            else:
                # Already in library, find it and open
                for b in self._manager.list_books():
                    if b.file_path == str(os.path.abspath(file_path)):
                        self._open_book(b.id)
                        return
                QMessageBox.warning(self, "错误", "无法打开电子书文件。")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无效的电子书文件: {e}")

    # ── Settings Handlers ──────────────────────────────────────────────

    def _on_font_increase(self) -> None:
        self._font_size = min(self._font_size + 2, 32)
        self._reader.set_font_size(self._font_size)
        self._save_preferences()

    def _on_font_decrease(self) -> None:
        self._font_size = max(self._font_size - 2, 10)
        self._reader.set_font_size(self._font_size)
        self._save_preferences()

    def _on_font_reset(self) -> None:
        self._font_size = 16
        self._reader.set_font_size(self._font_size)
        self._save_preferences()

    def _on_theme_selected(self, color: str) -> None:
        """Apply selected theme color to reader."""
        self._reader.set_background_color(color)
        self._theme_color = color
        self._save_preferences()

    def _on_toc_toggle(self) -> None:
        # Toggle left panel visibility
        self._toc_visible = not self._toc_visible
        self._left_splitter.setVisible(self._toc_visible)
        self._save_preferences()

    def _on_toc_navigate(self, href: str) -> None:
        """Navigate to a TOC item."""
        if self._current_book_id:
            self._reader.set_chapter_list(href, self._reader._chapter_hrefs or [href])
            url = self._manager.get_chapter_url(self._current_book_id, href)
            self._reader.load_chapter(url)

    def _on_bookmark_add(self) -> None:
        """Create a bookmark at the current reading position."""
        if not self._current_book_id:
            return

        chapter_href = self._reader.current_chapter_href
        if not chapter_href:
            return

        self._reader.get_scroll_position(
            callback=lambda offset: self._do_add_bookmark(chapter_href, offset)
        )

    def _do_add_bookmark(self, chapter_href: str, scroll_offset: int) -> None:
        import uuid
        from app.core.models import Bookmark

        bookmark = Bookmark(
            id=str(uuid.uuid4()),
            chapter_href=chapter_href,
            scroll_offset=scroll_offset,
        )
        self._manager.add_bookmark(self._current_book_id, bookmark)
        # Add to panel immediately
        self._bookmark_panel.add_bookmark_item(bookmark)

    def _on_bookmark_navigate(self, chapter_href: str, scroll_offset: int) -> None:
        """Navigate to a bookmark position."""
        if not self._current_book_id:
            return

        current_href = self._reader.current_chapter_href
        url = self._manager.get_chapter_url(self._current_book_id, chapter_href)

        # Update chapter list index for seamless scrolling
        self._reader.set_chapter_list(chapter_href, self._reader._chapter_hrefs or [chapter_href])

        if chapter_href == current_href:
            # Same chapter — page already loaded, scroll immediately
            self._reader.set_scroll_position(scroll_offset)
        else:
            # Different chapter — wait for page load before scrolling
            def _on_load_finished(ok: bool) -> None:
                if ok:
                    self._reader.set_scroll_position(scroll_offset)
                self._reader._page.loadFinished.disconnect(_on_load_finished)

            self._reader._page.loadFinished.connect(_on_load_finished)
            self._reader.load_chapter(url)

    def _on_bookmark_remove(self, bookmark_id: str) -> None:
        """Delete a bookmark."""
        if self._current_book_id:
            self._manager.remove_bookmark(self._current_book_id, bookmark_id)
            self._bookmark_panel.remove_bookmark_item(bookmark_id)

    def _on_scroll_changed(self, offset: int) -> None:
        """Save reading position on scroll change."""
        if self._current_book_id:
            state = ReadingState(
                scroll_offset=offset,
                progress_pct=0.0,  # TODO: calculate from chapter position
                last_read_at="",
            )
            self._manager.save_reading_state(self._current_book_id, state)

    def _on_annotation_created(self, data: dict) -> None:
        """Save a new annotation from the reader."""
        if not self._current_book_id:
            return
        annotation = Annotation(
            id=str(__import__("uuid").uuid4()),
            chapter_href=data["chapter_href"],
            selected_text=data["selected_text"],
            note=data.get("note", ""),
        )
        storage.add_annotation(self._current_book_id, annotation)

    def _on_notes_export(self) -> None:
        """Export book notes to txt."""
        if not self._current_book_id:
            return

        annotations = storage.load_annotations(self._current_book_id)
        if not annotations:
            QMessageBox.information(self, "笔记", "当前书籍暂无笔记。")
            return

        # Get book title
        book_title = ""
        for b in self._manager.list_books():
            if b.id == self._current_book_id:
                book_title = b.title
                break

        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出笔记", f"{book_title}_笔记.txt", "文本文件 (*.txt)"
        )
        if file_path:
            storage.export_notes_txt(self._current_book_id, book_title, annotations, file_path)
            QMessageBox.information(self, "笔记导出", f"已导出 {len(annotations)} 条笔记到:\n{file_path}")

    def _go_back_to_bookshelf(self) -> None:
        """Return to the bookshelf view."""
        self._reader.stop_scroll_tracking()
        self._current_book_id = None
        self._refresh_bookshelf()
        self.setWindowTitle("EpubReader")

    def _on_remove_book(self) -> None:
        """Open a dialog to select books for removal."""
        books = self._manager.list_books()
        if not books:
            QMessageBox.information(self, "下架书籍", "书架上没有可下架的书籍。")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("下架书籍")
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)
        label = QLabel("请选择要下架的书籍（可同时选择多本）：")
        layout.addWidget(label)

        list_widget = QListWidget()
        for book in books:
            item = QListWidgetItem(f"{book.title} — {book.author}")
            item.setCheckState(Qt.CheckState.Unchecked)
            item.setData(Qt.ItemDataRole.UserRole, book.id)
            list_widget.addItem(item)
        layout.addWidget(list_widget)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            to_remove = [
                list_widget.item(i).data(Qt.ItemDataRole.UserRole)
                for i in range(list_widget.count())
                if list_widget.item(i).checkState() == Qt.CheckState.Checked
            ]
            if to_remove:
                for book_id in to_remove:
                    self._manager.remove_book(book_id)
                    storage.remove_annotations(book_id)
                self._refresh_bookshelf()

    def _on_txt_convert(self) -> None:
        """Handle TXT to EPUB conversion."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择TXT文件", "", "文本文件 (*.txt)"
        )
        if not file_path:
            return

        from pathlib import Path
        from app.core.txt_converter import convert_txt_to_epub

        try:
            out_path = convert_txt_to_epub(file_path)
            QMessageBox.information(
                self,
                "转换成功",
                f"EPUB 文件已生成:\n{out_path}",
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "转换失败",
                f"无法转换该文件:\n{e}",
            )

    # ── Preferences ────────────────────────────────────────────────────

    def _save_preferences(self) -> None:
        prefs = UserPreferences(
            font_size=self._font_size,
            toc_visible=self._toc_visible,
            theme_color=self._theme_color,
        )
        self._manager.save_preferences(prefs)

    # ── Drag and Drop (from desktop) ───────────────────────────────────

    def on_files_dropped(self, file_paths: list[str]) -> None:
        """Handle EPUB files dropped onto the bookshelf."""
        for fp in file_paths:
            self._open_epub_file(fp)

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith(".epub"):
                    event.acceptProposedAction()
                    return

    def dropEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            epub_files = [
                url.toLocalFile()
                for url in event.mimeData().urls()
                if url.toLocalFile().lower().endswith(".epub")
            ]
            if epub_files:
                self.on_files_dropped(epub_files)
                event.acceptProposedAction()

    # ── Cleanup ────────────────────────────────────────────────────────

    def closeEvent(self, event: QCloseEvent) -> None:
        """Clean up resources on exit."""
        self._manager.shutdown()
        super().closeEvent(event)
