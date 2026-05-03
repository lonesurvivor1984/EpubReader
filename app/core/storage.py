"""JSON-based data persistence with atomic writes and version migration."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

from app.config import LIBRARY_FILE, NOTES_DIR
from app.core.models import Annotation, Bookmark, Book, ReadingState, UserPreferences


# ── Schema version ────────────────────────────────────────────────────────────

CURRENT_VERSION = 1


def _empty_db() -> dict[str, Any]:
    return {
        "version": CURRENT_VERSION,
        "library": [],
        "reading_state": {},
        "bookmarks": {},
        "preferences": {
            "font_size": UserPreferences.font_size,
            "toc_visible": UserPreferences.toc_visible,
            "theme_color": UserPreferences.theme_color,
        },
    }


# ── Core read / write ────────────────────────────────────────────────────────

def load_db(path: Path | None = None) -> dict[str, Any]:
    """Load the library JSON file.

    Returns an empty database structure if the file doesn't exist.
    Backs up and recreates on corruption.
    """
    path = path or LIBRARY_FILE
    if not path.exists():
        return _empty_db()

    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError):
        _backup_corrupted(path)
        return _empty_db()

    # Migrate if needed
    data = _migrate(data)
    return data


def save_db(data: dict[str, Any], path: Path | None = None) -> None:
    """Atomically write the library JSON file.

    Writes to a temp file first, then renames to prevent corruption.
    """
    path = path or LIBRARY_FILE
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write to temp file in same directory (for atomic rename)
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with open(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        Path(tmp_path).replace(path)
    except Exception:
        Path(tmp_path).unlink(missing_ok=True)
        raise


def _backup_corrupted(path: Path) -> None:
    backup = path.with_suffix(path.suffix + ".bak")
    if backup.exists():
        backup.unlink()
    path.rename(backup)
    print(f"[Storage] Corrupted file backed up as {backup.name}")


# ── Migration ─────────────────────────────────────────────────────────────────

def _migrate(data: dict[str, Any]) -> dict[str, Any]:
    """Apply migrations from current version to latest."""
    version = data.get("version", 0)

    if version < CURRENT_VERSION:
        # Future: add migration steps here per version
        # e.g., if version == 0: data = migrate_v0_to_v1(data)
        pass

    data["version"] = CURRENT_VERSION
    return data


# ── Library CRUD ─────────────────────────────────────────────────────────────

def add_book(data: dict[str, Any], book: Book) -> None:
    """Add a book to the library. Silently skips if already present."""
    # Check duplicate by file_path
    for entry in data["library"]:
        if entry["file_path"] == book.file_path:
            return
    data["library"].append(_book_to_dict(book))


def remove_book(data: dict[str, Any], book_id: str) -> None:
    """Remove a book and its reading state/bookmarks."""
    data["library"] = [b for b in data["library"] if b["id"] != book_id]
    data["reading_state"].pop(book_id, None)
    data["bookmarks"].pop(book_id, None)


def relocate_book(data: dict[str, Any], book_id: str, new_path: str) -> bool:
    """Update the file_path of a book. Returns True if found."""
    for entry in data["library"]:
        if entry["id"] == book_id:
            entry["file_path"] = new_path
            entry["file_size"] = Path(new_path).stat().st_size
            return True
    return False


def find_book(data: dict[str, Any], book_id: str) -> dict | None:
    """Find a book by ID."""
    for entry in data["library"]:
        if entry["id"] == book_id:
            return entry
    return None


def find_book_by_path(data: dict[str, Any], file_path: str) -> dict | None:
    """Find a book by absolute file path."""
    for entry in data["library"]:
        if entry["file_path"] == file_path:
            return entry
    return None


# ── Reading State ─────────────────────────────────────────────────────────────

def save_reading_state(data: dict[str, Any], book_id: str, state: ReadingState) -> None:
    """Save reading position for a book."""
    data["reading_state"][book_id] = {
        "chapter_href": state.chapter_href,
        "scroll_offset": state.scroll_offset,
        "progress_pct": state.progress_pct,
        "last_read_at": state.last_read_at,
    }


def load_reading_state(data: dict[str, Any], book_id: str) -> ReadingState:
    """Load reading position for a book."""
    raw = data.get("reading_state", {}).get(book_id)
    if not raw:
        return ReadingState()
    return ReadingState(
        chapter_href=raw.get("chapter_href", ""),
        scroll_offset=raw.get("scroll_offset", 0),
        progress_pct=raw.get("progress_pct", 0.0),
        last_read_at=raw.get("last_read_at", ""),
    )


# ── Bookmarks ─────────────────────────────────────────────────────────────────

def add_bookmark(data: dict[str, Any], book_id: str, bookmark: Bookmark) -> None:
    """Add a bookmark for a book."""
    data["bookmarks"].setdefault(book_id, [])
    data["bookmarks"][book_id].append(_bookmark_to_dict(bookmark))


def remove_bookmark(data: dict[str, Any], book_id: str, bookmark_id: str) -> None:
    """Remove a bookmark."""
    bookmarks = data["bookmarks"].get(book_id, [])
    data["bookmarks"][book_id] = [b for b in bookmarks if b["id"] != bookmark_id]


def load_bookmarks(data: dict[str, Any], book_id: str) -> list[Bookmark]:
    """Load all bookmarks for a book."""
    raw_list = data.get("bookmarks", {}).get(book_id, [])
    return [
        Bookmark(
            id=b["id"],
            chapter_href=b["chapter_href"],
            scroll_offset=b["scroll_offset"],
            note=b.get("note", ""),
            created_at=b.get("created_at", ""),
        )
        for b in raw_list
    ]


# ── Preferences ───────────────────────────────────────────────────────────────

def save_preferences(data: dict[str, Any], prefs: UserPreferences) -> None:
    """Save user preferences."""
    data["preferences"] = {
        "font_size": prefs.font_size,
        "toc_visible": prefs.toc_visible,
        "theme_color": prefs.theme_color,
    }


def load_preferences(data: dict[str, Any]) -> UserPreferences:
    """Load user preferences."""
    raw = data.get("preferences", {})
    return UserPreferences(
        font_size=raw.get("font_size", UserPreferences.font_size),
        toc_visible=raw.get("toc_visible", UserPreferences.toc_visible),
        theme_color=raw.get("theme_color", UserPreferences.theme_color),
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _book_to_dict(book: Book) -> dict[str, Any]:
    return {
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "language": book.language,
        "cover_image_id": book.cover_image_id,
        "file_path": book.file_path,
        "file_size": book.file_size,
        "added_at": book.added_at,
    }


def _bookmark_to_dict(bookmark: Bookmark) -> dict[str, Any]:
    return {
        "id": bookmark.id,
        "chapter_href": bookmark.chapter_href,
        "scroll_offset": bookmark.scroll_offset,
        "note": bookmark.note,
        "created_at": bookmark.created_at,
    }


# ── Annotations (Notes) ──────────────────────────────────────────────────────

def _notes_path(book_id: str) -> Path:
    return NOTES_DIR / f"{book_id}.json"


def save_annotations(book_id: str, annotations: list[Annotation]) -> None:
    """Save all annotations for a book."""
    path = _notes_path(book_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [_annotation_to_dict(a) for a in annotations]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_annotations(book_id: str) -> list[Annotation]:
    """Load all annotations for a book."""
    path = _notes_path(book_id)
    if not path.exists():
        return []
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    return [
        Annotation(
            id=a["id"],
            chapter_href=a["chapter_href"],
            selected_text=a["selected_text"],
            note=a.get("note", ""),
            created_at=a.get("created_at", ""),
        )
        for a in data
    ]


def remove_annotations(book_id: str) -> None:
    """Remove all annotation files for a book."""
    path = _notes_path(book_id)
    path.unlink(missing_ok=True)


def add_annotation(book_id: str, annotation: Annotation) -> None:
    """Add a single annotation."""
    existing = load_annotations(book_id)
    existing.append(annotation)
    save_annotations(book_id, existing)


def export_notes_txt(book_id: str, book_title: str, annotations: list[Annotation],
                     output_path: str) -> None:
    """Export book notes to a plain text file."""
    lines = [f"《{book_title}》笔记", f"共 {len(annotations)} 条标注\n", "=" * 50 + "\n"]
    for i, ann in enumerate(annotations, 1):
        lines.append(f"【{i}】圈选：{ann.selected_text}")
        if ann.note:
            lines.append(f"笔记：{ann.note}")
        if ann.created_at:
            lines.append(f"时间：{ann.created_at[:19].replace('T', ' ')}")
        lines.append("-" * 40)
        lines.append("")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def _annotation_to_dict(annotation: Annotation) -> dict[str, Any]:
    return {
        "id": annotation.id,
        "chapter_href": annotation.chapter_href,
        "selected_text": annotation.selected_text,
        "note": annotation.note,
        "created_at": annotation.created_at,
    }
