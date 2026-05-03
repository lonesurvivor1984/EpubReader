# Design: EPUB Local Reader

## Architecture

```
main.py (CLI entry)
    │
    ├── BookManager (app/core/)          Application Layer
    │   ├── EpubParser                   EPUB ZIP → parsed data
    │   ├── Storage                      JSON read/write
    │   └── EpubServer                   Local HTTP for resources
    │
    ├── MainWindow (app/ui/)              UI Layer
    │   ├── BookshelfView                Grid of book cards
    │   ├── ReaderView                   QWebEngineView + scroll
    │   ├── TOCPanel                     Side navigation
    │   └── SettingsDialog               Font, theme, etc.
    │
    └── Domain Models (app/core/models)   Pure Python
        ├── Book, Chapter, TOCItem
        └── Bookmark, ReadingState
```

### Layer Responsibilities

| Layer | Module | Responsibility |
|-------|--------|---------------|
| CLI | `main.py`, `app/cli.py` | Parse args, launch app |
| Application | `BookManager`, `Storage`, `EpubServer` | Orchestrate book operations |
| Domain | `models.py` | Pure data classes (no framework deps) |
| UI | `app/ui/*.py` | PySide6 widgets, event handling |
| Infrastructure | `epub_parser.py`, `epub_server.py` | File I/O, HTTP serving |

## Key Technical Decisions

### 1. Resource Serving: Local HTTP Server

EPUB is a ZIP file. QtWebEngine needs to resolve relative paths like `../images/cover.jpg` in CSS.

**Decision**: Embedded `http.server.ThreadingHTTPServer` on a random localhost port.

```
QtWebEngine                     ThreadingHTTPServer
     │                                │
     │  GET /:id/chapter1.html        │
     ├───────────────────────────────▶│  Extract from ZIP in memory
     │  ◀── 200 text/html ◀──────────│  Set correct Content-Type
     │                                │
     │  GET /:id/styles.css           │
     ├───────────────────────────────▶│  Extract from ZIP in memory
     │  ◀── 200 text/css ◀───────────│  Set correct Content-Type
```

Why not temp directory? No disk pollution, no cache management needed, on-demand extraction.
Why not custom URL scheme? QtWebEngine's scheme registration has edge cases with CSS `url()` references.

Port selection: `port = 0` → OS assigns a free port, stored in `BookManager` for the session.

### 2. EPUB Parsing Strategy

```
book.epub
  ├── mimetype                          → Always "application/epub+zip"
  ├── META-INF/container.xml            → <rootfile full-path="OEBPS/content.opf"/>
  └── OEBPS/
      ├── content.opf                   → Metadata + Manifest + Spine
      ├── toc.ncx (EPUB2) or nav.xhtml (EPUB3)  → TOC
      ├── chapter1.xhtml                → Chapter HTML
      ├── styles.css                    → Stylesheet
      └── images/cover.jpg              → Image resources
```

Steps:
1. Open ZIP with `zipfile.ZipFile`
2. Read `META-INF/container.xml` → get `.opf` path
3. Parse `.opf` with `lxml.etree` → extract title, author, cover image ID
4. Build spine order from `<spine>` element → ordered chapter list
5. Parse TOC from `toc.ncx` (EPUB2) or `nav.xhtml` (EPUB3) → hierarchical TOC items
6. All extracted data stored in domain models

### 3. Reading State Management

```
QtWebEngine → JavaScript injection → scroll position
     │
     │  window.scrollY  (read on navigate/interval)
     │  window.scrollTo(0, y) (restore on open)
     │
     ▼
Python reads via QWebEnginePage.runJavaScript()
```

- Save position every 30 seconds and on tab close
- Store: `{book_id: {chapter_href, scroll_offset, progress_pct, last_read_at}}`
- On open: navigate to chapter → `scrollTo(0, saved_offset)`

### 4. TOC Panel Synchronization

```
┌──────────────┬─────────────────────────┐
│  TOC Panel   │  ReaderView             │
│              │                         │
│  Chapter 1   │                         │
│  Ch 2 ←───   │  QWebEngineView         │
│  Chapter 3   │  (scrolls here)         │
│              │                         │
│  Scroll      │                         │
│  position ──▶│ highlight current TOC   │
└──────────────┴─────────────────────────┘
```

- User clicks TOC → `navigateTo(href)` in WebEngineView
- WebEngineView loads → `runJavaScript("document.location.hash")` → update TOC highlight
- Use IntersectionObserver JS to track which heading is visible

### 5. Bookshelf View

- `QListView` with `QStyledItemDelegate` for custom grid cards
- Each card: cover thumbnail (QPixmap), title (bold), author (gray), progress bar
- Cover extraction: parse `.opf` for `<meta name="cover">` or first image in manifest
- "Add Book" card: dashed border, opens `QFileDialog.getOpenFileName`
- Drag-and-drop: override `dragEnterEvent` / `dropEvent` on main window

### 6. JSON Data Schema

```json
{
  "version": 1,
  "library": [{
    "id": "uuid4",
    "title": "string",
    "author": "string",
    "cover_image_id": "string|null",
    "file_path": "absolute/path/to/book.epub",
    "file_size": "int",
    "added_at": "ISO-8601"
  }],
  "reading_state": {
    "book_id": {
      "chapter_href": "string",
      "scroll_offset": "int",
      "progress_pct": "float 0-1",
      "last_read_at": "ISO-8601"
    }
  },
  "bookmarks": {
    "book_id": [{
      "id": "bm_uuid",
      "chapter_href": "string",
      "scroll_offset": "int",
      "note": "string",
      "created_at": "ISO-8601"
    }]
  }
}
```

File location: `data/library.json` relative to project root (or `~/.epubreader/` if packaged).

### 7. Theming

Light/dark theme implemented via CSS injection into QWebEngineView:

```javascript
// Dark mode CSS injected after page load
const darkCSS = `
  :root { filter: invert(1) hue-rotate(180deg); }
  img { filter: invert(1) hue-rotate(180deg); }
`;
```

Simple `invert()` approach preserves EPUB's own CSS while providing dark background.

### 8. Single Book Constraint

Only one book open at a time. Opening a book navigates from bookshelf to reader view (stacked widget or `QStackedLayout`). Back button returns to bookshelf.

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| QtWebEngine crashes on malformed EPUB HTML | High | Wrap in try/except, show error dialog |
| Large EPUBs (>100MB) cause memory issues | Medium | Stream HTTP responses, don't load all into RAM |
| EPUB 3 with complex CSS grid/flex may render differently | Low | Chromium handles this well; document limitations |
| JSON file corruption | Medium | Write to temp file then atomic rename |
| Port conflict for HTTP server | Low | Use port 0 (OS-assigned free port) |
