# Change: EPUB Local Reader

## Why

Build a cross-platform desktop EPUB reader with scrolling-style reading, starting from a bookshelf view. Users should be able to open EPUB files, browse their library, read with proper CSS/typography, and have their reading progress and bookmarks persisted.

## What Changes

- **Bookshelf UI**: Grid view showing all imported books with cover thumbnails, title, and reading progress percentage. Supports drag-and-drop and file-picker import.
- **EPUB Parser**: Unpack EPUB ZIP files, parse `container.xml` → `.opf` → extract metadata, manifest, spine order, table of contents. Handle both EPUB 2 (ncx) and EPUB 3 (nav.xhtml) TOC formats.
- **Local HTTP Server**: Serve EPUB resources (HTML chapters, CSS, images, fonts) via `localhost` so QtWebEngine resolves relative paths correctly without writing to disk.
- **Reader View**: Single-book QWebEngineView with continuous scrolling. Sidebar TOC panel for chapter navigation. Font size control and light/dark theme toggle.
- **JSON Storage**: Persist library metadata, bookmarks, and reading position (per-book) to `data/library.json`. Restore last-read position on open.
- **CLI Entry**: `python main.py` launches the bookshelf. Optional `main.py <file.epub>` opens a specific file directly.
- **Project Structure**: Domain → Application → UI → CLI layered architecture for long-term maintainability.

## Impact

- New codebase (no existing code to modify).
- Adds PySide6 + QtWebEngine as dependencies.
- Creates `data/` directory for runtime storage.

## Non-goals (for v1)

- Multi-tab or multi-book simultaneous reading
- Full-text search
- Annotations/highlights on the page
- Export notes
- Cloud sync
