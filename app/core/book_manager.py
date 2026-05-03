"""BookManager — orchestrates EPUB parsing, storage, and HTTP serving."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Callable

from app.config import LIBRARY_FILE
from app.core import storage
from app.core.epub_parser import InvalidEpubError, parse_epub
from app.core.models import Book, Bookmark, ReadingState, UserPreferences
from app.utils.epub_server import EpubServer


class BookManager:
    """High-level API for the application.

    Coordinates the Storage layer, EpubParser, and EpubServer to provide
    a clean interface for the UI layer.
    """

    def __init__(self, db_path: Path | None = None) -> None:
        self._db = storage.load_db(db_path or LIBRARY_FILE)
        self._server = EpubServer()
        self._server.start()

    # ── Properties ────────────────────────────────────────────────────────

    @property
    def server_url(self) -> str:
        """Base URL for EPUB resource requests."""
        return self._server.base_url

    @property
    def preferences(self) -> UserPreferences:
        return storage.load_preferences(self._db)

    # ── Library operations ────────────────────────────────────────────────

    def list_books(self) -> list[Book]:
        """Return all books in the library (without parsed content)."""
        books = []
        for entry in self._db["library"]:
            book = Book(
                id=entry["id"],
                title=entry["title"],
                author=entry["author"],
                file_path=entry["file_path"],
                file_size=entry["file_size"],
                language=entry.get("language", "en"),
                cover_image_id=entry.get("cover_image_id"),
                added_at=entry.get("added_at", ""),
            )
            books.append(book)
        return books

    def add_book(self, file_path: str) -> Book | None:
        """Parse an EPUB file and add it to the library.

        Returns the Book if successful, None if already present.
        Raises InvalidEpubError for invalid files.
        """
        file_path = str(Path(file_path).resolve())

        # Check duplicate
        if storage.find_book_by_path(self._db, file_path):
            return None

        parsed = parse_epub(file_path)
        book = Book(
            id=str(uuid.uuid4()),
            title=parsed.title,
            author=parsed.author,
            language=parsed.language,
            cover_image_id=parsed.cover_image_id,
            file_path=file_path,
            file_size=Path(file_path).stat().st_size,
        )
        storage.add_book(self._db, book)
        self._save()
        return book

    def remove_book(self, book_id: str) -> None:
        """Remove a book from the library."""
        self._server.unregister_book(book_id)
        storage.remove_book(self._db, book_id)
        self._save()

    def relocate_book(self, book_id: str, new_path: str) -> bool:
        """Relocate a book file (if it was moved)."""
        result = storage.relocate_book(self._db, book_id, new_path)
        if result:
            self._save()
        return result

    def get_cover_data(self, book_id: str) -> bytes | None:
        """Extract cover image bytes from a registered EPUB."""
        return storage.find_book(self._db, book_id)  # type: ignore[return-value]

    # ── Reading operations ────────────────────────────────────────────────

    def open_book(self, book_id: str) -> Book | None:
        """Open a book for reading: register with server, parse content.

        Returns a fully parsed Book with chapters and TOC.
        """
        entry = storage.find_book(self._db, book_id)
        if not entry:
            return None

        file_path = entry["file_path"]
        parsed = parse_epub(file_path)

        # Register with HTTP server
        self._server.register_book(
            book_id, file_path, parsed.opf_base, parsed.merged_chapters,
        )

        book = Book(
            id=book_id,
            title=entry["title"],
            author=entry["author"],
            file_path=file_path,
            file_size=entry["file_size"],
            language=entry.get("language", "en"),
            cover_image_id=entry.get("cover_image_id"),
            added_at=entry.get("added_at", ""),
            chapters=parsed.chapters,
            toc=parsed.toc,
        )

        # Merge reading state
        state = self.load_reading_state(book_id)
        book.reading_state = state  # type: ignore[attr-defined]
        book.progress_pct = state.progress_pct  # type: ignore[attr-defined]

        return book

    def save_reading_state(self, book_id: str, state: ReadingState) -> None:
        """Save the current reading position."""
        storage.save_reading_state(self._db, book_id, state)
        self._save()

    def load_reading_state(self, book_id: str) -> ReadingState:
        """Load the saved reading position."""
        return storage.load_reading_state(self._db, book_id)

    # ── Bookmarks ─────────────────────────────────────────────────────────

    def add_bookmark(self, book_id: str, bookmark: Bookmark) -> None:
        storage.add_bookmark(self._db, book_id, bookmark)
        self._save()

    def remove_bookmark(self, book_id: str, bookmark_id: str) -> None:
        storage.remove_bookmark(self._db, book_id, bookmark_id)
        self._save()

    def get_bookmarks(self, book_id: str) -> list[Bookmark]:
        return storage.load_bookmarks(self._db, book_id)

    # ── Preferences ───────────────────────────────────────────────────────

    def save_preferences(self, prefs: UserPreferences) -> None:
        storage.save_preferences(self._db, prefs)
        self._save()

    # ── Server info ───────────────────────────────────────────────────────

    def get_resource_url(self, book_id: str, resource_path: str) -> str:
        """Build the HTTP URL for an EPUB resource."""
        return self._server.url_for(book_id, resource_path)

    def get_chapter_url(self, book_id: str, chapter_href: str) -> str:
        """Build the HTTP URL for a chapter."""
        return self.get_resource_url(book_id, chapter_href)

    # ── Lifecycle ─────────────────────────────────────────────────────────

    def shutdown(self) -> None:
        """Stop the HTTP server."""
        self._server.stop()

    # ── Internal ──────────────────────────────────────────────────────────

    def _save(self) -> None:
        storage.save_db(self._db)
