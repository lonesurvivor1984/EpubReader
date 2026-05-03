"""Domain models — pure Python dataclasses, no framework dependencies."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class TOCItem:
    """A single entry in the table of contents."""

    label: str
    href: str  # relative path within the EPUB
    children: list[TOCItem] = field(default_factory=list)
    depth: int = 0


@dataclass
class Chapter:
    """A single spine item (reading unit)."""

    id: str
    href: str  # relative path within the EPUB
    title: str = ""


@dataclass
class Bookmark:
    """A user-created bookmark."""

    id: str
    chapter_href: str
    scroll_offset: int
    note: str = ""
    created_at: str = field(default_factory=_now)


@dataclass
class ReadingState:
    """Persisted reading position for a book."""

    chapter_href: str = ""
    scroll_offset: int = 0
    progress_pct: float = 0.0
    last_read_at: str = field(default_factory=_now)


@dataclass
class Book:
    """Represents an imported EPUB book."""

    id: str
    title: str
    author: str
    file_path: str  # absolute path to the .epub file
    file_size: int
    language: str = "en"
    cover_image_id: str | None = None
    added_at: str = field(default_factory=_now)

    # Parsed content (not persisted to JSON, built at runtime)
    chapters: list[Chapter] = field(default_factory=list)
    toc: list[TOCItem] = field(default_factory=list)

    @property
    def is_file_available(self) -> bool:
        from pathlib import Path
        return Path(self.file_path).exists()

    @property
    def reading_progress(self) -> float:
        """Return reading progress as a percentage (0-100)."""
        if not self.chapters:
            return 0.0
        return (self.progress_pct or 0.0) * 100


@dataclass
class UserPreferences:
    """Per-user reading preferences."""

    font_size: int = 16
    toc_visible: bool = True
    theme_color: str = ""  # hex color, e.g. "#FFF9E6"


@dataclass
class Annotation:
    """A user-created text annotation (highlight + note)."""

    id: str
    chapter_href: str
    selected_text: str
    note: str = ""
    created_at: str = field(default_factory=_now)
