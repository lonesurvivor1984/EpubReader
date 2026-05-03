"""Bookshelf view — grid of book cards with cover thumbnails."""

from __future__ import annotations

from PySide6.QtCore import Qt, QSize, QRectF, Signal
from PySide6.QtGui import (
    QPainter, QColor, QFont, QPen, QBrush, QPixmap, QStandardItem,
    QStandardItemModel, QDragEnterEvent, QDropEvent,
)
from PySide6.QtWidgets import (
    QListView, QStyledItemDelegate, QStyleOptionViewItem, QStyle,
    QStyleOptionProgressBar, QApplication,
)


# Model roles
ROLE_BOOK_ID = Qt.ItemDataRole.UserRole + 1
ROLE_TITLE = Qt.ItemDataRole.UserRole + 2
ROLE_AUTHOR = Qt.ItemDataRole.UserRole + 3
ROLE_PROGRESS = Qt.ItemDataRole.UserRole + 4
ROLE_COVER = Qt.ItemDataRole.UserRole + 5  # QPixmap
ROLE_FILE_EXISTS = Qt.ItemDataRole.UserRole + 6
ROLE_IS_ADD_CARD = Qt.ItemDataRole.UserRole + 7
ROLE_IS_REMOVE_CARD = Qt.ItemDataRole.UserRole + 8

CARD_WIDTH = 160
CARD_HEIGHT = 230
COVER_HEIGHT = 180
MARGIN = 15


class BookshelfDelegate(QStyledItemDelegate):
    """Custom delegate rendering for book cards."""

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index) -> None:
        is_add_card = index.data(ROLE_IS_ADD_CARD)
        is_remove_card = index.data(ROLE_IS_REMOVE_CARD)
        if is_add_card:
            self._paint_add_card(painter, option, index)
        elif is_remove_card:
            self._paint_remove_card(painter, option, index)
        else:
            self._paint_book_card(painter, option, index)

    def _paint_book_card(self, painter: QPainter, option: QStyleOptionViewItem, index) -> None:
        r = option.rect
        painter.save()

        # Background
        painter.fillRect(r, QColor("#f5f5f5") if not option.state & QStyle.State_Selected else QColor("#e0e7ff"))

        # Card border with slight shadow
        shadow = QColor(0, 0, 0, 20)
        painter.fillRect(QRectF(r.x() + 2, r.y() + 2, r.width(), r.height()), QBrush(shadow))

        card_rect = QRectF(r.x() + 1, r.y() + 1, r.width() - 2, r.height() - 2)
        painter.fillRect(card_rect, QColor("#ffffff"))
        pen = QPen(QColor("#e0e0e0"), 1)
        painter.setPen(pen)
        painter.drawRect(card_rect)

        # Cover thumbnail
        cover = index.data(ROLE_COVER)
        cover_rect = QRectF(r.x() + MARGIN, r.y() + MARGIN, r.width() - MARGIN * 2, COVER_HEIGHT - MARGIN)
        if cover and isinstance(cover, QPixmap) and not cover.isNull():
            scaled = cover.scaled(
                cover_rect.size().toSize(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            x = int(cover_rect.x() + (cover_rect.width() - scaled.width()) / 2)
            y = int(cover_rect.y())
            painter.drawPixmap(x, y, scaled)
        else:
            # Placeholder
            painter.fillRect(cover_rect, QColor("#e8e8e8"))
            painter.setPen(QColor("#999"))
            painter.drawText(cover_rect, Qt.AlignmentFlag.AlignCenter, "无封面")

        # Title (bold, truncated)
        title = index.data(ROLE_TITLE) or ""
        title_rect = QRectF(r.x() + MARGIN, r.y() + COVER_HEIGHT + 4, r.width() - MARGIN * 2, 20)
        font = painter.font()
        font.setBold(True)
        font.setPointSize(9)
        painter.setFont(font)
        painter.setPen(QColor("#222"))
        fm = painter.fontMetrics()
        title = fm.elidedText(title, Qt.TextElideMode.ElideRight, int(title_rect.width()))
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignHCenter | Qt.TextFlag.TextSingleLine, title)

        # Author (gray, small)
        author = index.data(ROLE_AUTHOR) or ""
        author_rect = QRectF(r.x() + MARGIN, r.y() + COVER_HEIGHT + 22, r.width() - MARGIN * 2, 16)
        font.setBold(False)
        font.setPointSize(8)
        painter.setFont(font)
        painter.setPen(QColor("#888"))
        fm = painter.fontMetrics()
        author = fm.elidedText(author, Qt.TextElideMode.ElideRight, int(author_rect.width()))
        painter.drawText(author_rect, Qt.AlignmentFlag.AlignHCenter | Qt.TextFlag.TextSingleLine, author)

        # Progress bar
        progress = index.data(ROLE_PROGRESS) or 0.0
        bar_rect = QRectF(r.x() + MARGIN, r.y() + COVER_HEIGHT + 44, r.width() - MARGIN * 2, 6)
        painter.fillRect(bar_rect, QColor("#e0e0e0"))
        fill_width = bar_rect.width() * min(max(progress, 0.0), 1.0)
        painter.fillRect(QRectF(bar_rect.x(), bar_rect.y(), fill_width, bar_rect.height()), QColor("#6366f1"))

        # "File not found" badge
        file_exists = index.data(ROLE_FILE_EXISTS)
        if file_exists is False:
            badge_rect = QRectF(r.x() + 4, r.y() + 4, r.width() - 8, 18)
            painter.fillRect(badge_rect, QColor("#ef4444"))
            painter.setPen(QColor("#fff"))
            font.setPointSize(7)
            painter.setFont(font)
            painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, "文件缺失")

        painter.restore()

    def _paint_add_card(self, painter: QPainter, option: QStyleOptionViewItem, index) -> None:
        r = option.rect
        painter.save()

        # Dashed border card
        pen = QPen(QColor("#c0c0c0"), 2, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.drawRect(r.x() + 4, r.y() + 4, r.width() - 8, r.height() - 8)

        # Plus icon
        painter.setPen(QColor("#999"))
        font = painter.font()
        font.setPointSize(36)
        painter.setFont(font)
        painter.drawText(r, Qt.AlignmentFlag.AlignCenter, "+")

        # Label
        font.setPointSize(10)
        painter.setFont(font)
        painter.drawText(r.x(), r.y() + r.height() - 30, r.width(), 24, Qt.AlignmentFlag.AlignCenter, "添加书籍")

        painter.restore()

    def _paint_remove_card(self, painter: QPainter, option: QStyleOptionViewItem, index) -> None:
        r = option.rect
        painter.save()

        # Dashed border card (same style as add card)
        pen = QPen(QColor("#c0c0c0"), 2, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.drawRect(r.x() + 4, r.y() + 4, r.width() - 8, r.height() - 8)

        # "-" icon (matching "+" style)
        painter.setPen(QColor("#999"))
        font = painter.font()
        font.setPointSize(36)
        painter.setFont(font)
        painter.drawText(r, Qt.AlignmentFlag.AlignCenter, "−")

        # Label
        font = painter.font()
        font.setPointSize(10)
        painter.setFont(font)
        painter.setPen(QColor("#999"))
        painter.drawText(r.x(), r.y() + r.height() - 30, r.width(), 24, Qt.AlignmentFlag.AlignCenter, "下架书籍")

        painter.restore()

    def sizeHint(self, option, index) -> QSize:
        return QSize(CARD_WIDTH, CARD_HEIGHT)


class BookshelfView(QListView):
    """Grid view of books in the library."""

    add_book_requested = Signal()
    remove_book_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._model = QStandardItemModel()
        self.setModel(self._model)

        delegate = BookshelfDelegate()
        self.setItemDelegate(delegate)

        # Grid layout
        self.setViewMode(QListView.ViewMode.IconMode)
        self.setResizeMode(QListView.ResizeMode.Adjust)
        self.setMovement(QListView.Movement.Static)
        self.setUniformItemSizes(True)
        self.setSpacing(10)
        self.setWrapping(True)
        self.setFlow(QListView.Flow.LeftToRight)

        # Disable inline editing
        self.setEditTriggers(QListView.EditTrigger.NoEditTriggers)

        # Accept drops
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(False)

        # Handle clicks (for "+" card)
        self.clicked.connect(self._on_clicked)

    def _on_clicked(self, index) -> None:
        if index.data(ROLE_IS_ADD_CARD):
            self.add_book_requested.emit()
        elif index.data(ROLE_IS_REMOVE_CARD):
            self.remove_book_requested.emit()

    def populate_books(self, books: list) -> None:
        """Populate the grid with book entries.

        Each book dict should have: id, title, author, cover (QPixmap|None),
        progress (float 0-1), file_exists (bool).
        """
        self._model.clear()

        for book in books:
            item = QStandardItem()
            item.setData(book["id"], ROLE_BOOK_ID)
            item.setData(book["title"], ROLE_TITLE)
            item.setData(book["author"], ROLE_AUTHOR)
            item.setData(book["progress"], ROLE_PROGRESS)
            item.setData(book.get("cover"), ROLE_COVER)
            item.setData(book["file_exists"], ROLE_FILE_EXISTS)
            item.setData(False, ROLE_IS_ADD_CARD)
            self._model.appendRow(item)

        # Add "Add Books" card at the end
        add_item = QStandardItem()
        add_item.setData(True, ROLE_IS_ADD_CARD)
        add_item.setData(False, ROLE_IS_REMOVE_CARD)
        self._model.appendRow(add_item)

        # Add "Remove Books" card
        remove_item = QStandardItem()
        remove_item.setData(False, ROLE_IS_ADD_CARD)
        remove_item.setData(True, ROLE_IS_REMOVE_CARD)
        self._model.appendRow(remove_item)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith(".epub"):
                    event.acceptProposedAction()
                    return
        super().dragEnterEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:
        if event.mimeData().hasUrls():
            epub_files = [
                url.toLocalFile()
                for url in event.mimeData().urls()
                if url.toLocalFile().lower().endswith(".epub")
            ]
            if epub_files:
                event.acceptProposedAction()
                # Signal is handled by MainWindow
                self.window().on_files_dropped(epub_files)
                return
        super().dropEvent(event)

    def get_book_id_at(self, index) -> str | None:
        """Get the book ID for a clicked index."""
        return index.data(ROLE_BOOK_ID)
