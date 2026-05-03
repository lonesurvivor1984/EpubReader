# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Cross-platform desktop EPUB reader built with Python + PySide6 (Qt). Key features: bookshelf management, EPUB 2 & 3 parsing, local HTTP server for resource serving, persistent reading progress, bookmarks, annotations, theme/font controls, and a TXT-to-EPUB converter.

## Commands

```bash
# Run from source
python main.py                    # Launch bookshelf GUI
python main.py <file.epub>        # Open a specific EPUB

# Install as package (enables CLI entry point)
pip install -e .
epub-reader

# Build Windows executable
pyinstaller EpubReader.spec --noconfirm
# Output: dist/EpubReader/EpubReader.exe
```

**Dependencies:** `PySide6>=6.6`, `lxml>=4.9`, `chardet` (optional, for TXT encoding detection).

No test suite, no linting configuration.

## Architecture

The project uses a strict **four-layer architecture**:

```
app/core/models.py          ← Pure dataclasses (no Qt), shared by all layers
app/core/epub_parser.py     ← Unzips EPUB, parses OPF/NCX/nav.xhtml, returns ParsedEpub
app/core/storage.py         ← JSON persistence (atomic writes, schema migration, backup)
app/core/book_manager.py    ← Application-layer API: coordinates parser, storage, HTTP server
utils/epub_server.py        ← Embedded HTTP server serving EPUB resources from ZIP in-memory
app/ui/                     ← PySide6 widgets (no direct storage/parser access — go through BookManager)
main.py                     ← Qt app entry point + argparse
```

**Why a local HTTP server?** `QtWebEngine` has issues loading relative paths via `file://` URLs. The embedded `EpubServer` (random port, daemon thread) serves `GET /{book_id}/{resource_path}` directly from the EPUB ZIP without disk extraction.

**Data directory:** `project_root/data/` in dev mode; `~/.epubreader/` when packaged via PyInstaller. Controlled by `app/config.py`.

**Persistence:** Single `data/library.json` (books, reading state, bookmarks; schema v1) + per-book `data/notes/{book_id}.json` for annotations. All writes are atomic (temp file → rename).

## Key Design Decisions

- **EPUB 2 & 3 support:** `epub_parser.py` prefers EPUB3 `nav.xhtml` TOC, falls back to EPUB2 `toc.ncx`.
- **Chapter merging:** Consecutive chapters under 500 chars are auto-merged to reduce navigation overhead.
- **CSS injection in ReaderView:** `ReaderPage` (custom `QWebEnginePage`) injects CSS at `DocumentCreationTime` — before load — to apply font, theme, and layout overrides without FOUC.
- **Scroll position persistence:** A timer in `ReaderView` saves scroll offset periodically; restored on next open.
- **UI does not touch storage directly:** All persistence goes through `BookManager`; UI only emits signals and calls `BookManager` methods.

## UI Layer (`app/ui/`)

- `main_window.py` — `QMainWindow` with `QStackedWidget` toggling between bookshelf and reader. Owns `BookManager` instance, routes all signals, restores last-opened book on launch.
- `bookshelf.py` — Custom `QListView` + delegate rendering cover thumbnails, title, author, progress bar.
- `reader.py` — `ReaderView` wraps `QWebEngineView`; `ReaderPage` handles CSS injection, scroll tracking, selection highlighting.
- `toc_panel.py` / `bookmark_panel.py` — Sidebar panels (tree/list); emit `navigate_to` signals consumed by `ReaderView`.
- `settings.py` — Toolbar emitting font/theme/export signals.

## OpenSpec Workflow

The project uses OpenSpec for structured change tracking. Artifacts live in `.claude/commands/opsx/`. Use `/opsx:propose` to draft a new change, `/opsx:apply` to implement it, and `/opsx:archive` to finalize. Archived changes are in `openspec/archive/`.
