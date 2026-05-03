# Tasks: EPUB Local Reader

## Phase 1: Project Foundation

- [x] 1.1 Create project structure: `app/`, `app/core/`, `app/ui/`, `data/`, `build/`
- [x] 1.2 Create `pyproject.toml` with dependencies (PySide6, lxml)
- [x] 1.3 Create `main.py` CLI entry with argparse (--help, --version, optional file argument)
- [x] 1.4 Create `app/config.py` with data directory resolution (dev vs packaged paths)

## Phase 2: Domain Layer (Pure Python)

- [x] 2.1 Create `app/core/models.py` — Book, Chapter, TOCItem, Bookmark, ReadingState dataclasses
- [x] 2.2 Create `app/core/epub_parser.py` — ZIP extraction, container.xml parsing, .opf parsing
- [x] 2.3 Implement EPUB 2 TOC parsing (toc.ncx)
- [x] 2.4 Implement EPUB 3 TOC parsing (nav.xhtml)
- [x] 2.5 Implement resource manifest building and MIME type mapping
- [x] 2.6 Implement metadata extraction (title, author, language, cover)
- [x] 2.7 Implement error handling for malformed EPUB files

## Phase 3: Data Persistence

- [x] 3.1 Create `app/core/storage.py` — JSON read/write with atomic writes
- [x] 3.2 Implement library CRUD (add/remove/relocate book)
- [x] 3.3 Implement reading state save/load per book
- [x] 3.4 Implement bookmark CRUD per book
- [x] 3.5 Implement user preferences save/load (font size, theme, TOC visibility)
- [x] 3.6 Implement data migration/version handling

## Phase 4: Infrastructure — Local HTTP Server

- [x] 4.1 Create `app/utils/epub_server.py` — ThreadingHTTPServer subclass
- [x] 4.2 Implement `/bookID/resourcePath` routing
- [x] 4.3 Implement on-demand ZIP extraction to memory
- [x] 4.4 Implement correct Content-Type headers per MIME type
- [x] 4.5 Implement port auto-selection (port = 0)
- [x] 4.6 Handle concurrent requests (threading)

## Phase 5: Application Layer

- [x] 5.1 Create `app/core/book_manager.py` — Orchestrates parser + storage + server
- [x] 5.2 Implement "add book" flow: validate EPUB → parse → save to library
- [x] 5.3 Implement "open book" flow: start server → build book model → return reader data
- [x] 5.4 Implement file-removed detection (check file_path exists on library load)
- [x] 5.5 Implement cover image extraction (meta name="cover" → manifest → image path)

## Phase 6: UI — Main Window & Bookshelf

- [x] 6.1 Create `app/ui/main_window.py` — QStackedLayout with bookshelf and reader views
- [x] 6.2 Create `app/ui/bookshelf.py` — QListView with QStyledItemDelegate for grid cards
- [x] 6.3 Implement book card rendering: cover thumbnail, title, author, progress bar
- [x] 6.4 Implement "Add Book" card with dashed border
- [x] 6.5 Implement file dialog for adding books (filter: *.epub)
- [x] 6.6 Implement drag-and-drop EPUB files onto window
- [x] 6.7 Implement empty state view (no books in library)
- [x] 6.8 Implement "file not found" badge on missing books

## Phase 7: UI — Reader View

- [x] 7.1 Create `app/ui/reader.py` — QWebEngineView wrapper with navigation controls
- [x] 7.2 Implement chapter loading via local HTTP server URLs
- [x] 7.3 Implement reading position save (JavaScript: window.scrollY)
- [x] 7.4 Implement reading position restore (JavaScript: window.scrollTo)
- [x] 7.5 Implement auto-save timer (every 30 seconds)
- [x] 7.6 Create `app/ui/toc_panel.py` — QTreeView with hierarchical TOC items
- [x] 7.7 Implement TOC click → navigate to chapter in WebEngineView
- [x] 7.8 Implement current position highlighting in TOC (via runJavaScript + IntersectionObserver)
- [x] 7.9 Implement TOC panel show/hide toggle

## Phase 8: UI — Settings & Preferences

- [x] 8.1 Create `app/ui/settings.py` — Settings dialog or inline toolbar controls
- [x] 8.2 Implement font size control (+/-/reset) via CSS injection
- [x] 8.3 Implement light/dark theme toggle via CSS filter injection
- [x] 8.4 Implement keyboard shortcuts (F2 toggle TOC, Ctrl+/- font, Ctrl+D theme, Esc back)
- [x] 8.5 Persist preferences on change, restore on startup

## Phase 9: Polish & Packaging Prep

- [x] 9.1 Implement progress calculation (chapter order / total chapters)
- [x] 9.2 Implement book removal from bookshelf UI
- [x] 9.3 Add error dialogs for invalid EPUB files
- [ ] 9.4 Add loading spinner during EPUB parse and chapter load
- [x] 9.5 Create build scripts: `build_windows.py` (PyInstaller), placeholder for Mac/Linux
- [ ] 9.6 Test with sample EPUB files (EPUB 2 and EPUB 3)
