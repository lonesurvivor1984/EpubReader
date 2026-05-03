# EPUB Parsing Spec

## Requirements

### Requirement: EPUB 2 and 3 Support
The parser SHALL correctly parse both EPUB 2 and EPUB 3 format files.

#### Scenarios
- **EPUB 2 (ncx TOC)** — Parse `toc.ncx` for table of contents.
- **EPUB 3 (nav.xhtml TOC)** — Parse `<nav>` element in `nav.xhtml` for table of contents.
- **Missing TOC** — Fall back to spine order as a flat chapter list.
- **Both ncx and nav.xhtml present** — Prefer `nav.xhtml` (EPUB 3).

### Requirement: Metadata Extraction
The parser SHALL extract book metadata from the `.opf` file.

#### Scenarios
- **Title present** — Extract `<dc:title>` text.
- **Author present** — Extract `<dc:creator>` text. Support multiple creators.
- **Language present** — Extract `<dc:language>` (defaults to "en" if missing).
- **No metadata** — Use filename as title, "Unknown" as author.

### Requirement: Chapter Ordering
The parser SHALL determine chapter reading order from the `.opf` spine.

#### Scenarios
- **Complete spine** — Use `<spine>` element order as reading order.
- **Spine with gaps** — Items in spine but not in manifest are skipped with a warning.
- **Empty spine** — Treat as single-chapter book with a warning.

### Requirement: Resource Manifest
The parser SHALL build a complete resource manifest from the `.opf` manifest.

#### Scenarios
- **HTML chapters** — `application/xhtml+xml` or `text/html` MIME types.
- **CSS stylesheets** — `text/css` MIME type, served at correct relative paths.
- **Images** — `image/jpeg`, `image/png`, `image/gif`, `image/svg+xml` MIME types.
- **Fonts** — `font/woff`, `font/woff2`, `font/ttf`, `application/vnd.ms-fontobject` MIME types.
- **Unknown MIME** — Serve as `application/octet-stream`.

### Requirement: Resource Path Resolution
All EPUB resources SHALL be served with correct relative paths.

#### Scenarios
- **Same-directory CSS** — `chapter.html` references `styles.css` → served from `/bookID/styles.css`.
- **Parent-directory CSS** — `chapter.html` references `../styles/base.css` → served from `/bookID/styles/base.css`.
- **Image in subfolder** — HTML references `images/cover.jpg` → served from `/bookID/images/cover.jpg`.

### Requirement: Parse Error Handling
The parser SHALL handle malformed EPUB files gracefully.

#### Scenarios
- **Invalid ZIP** — Raise `InvalidEpubError` with descriptive message.
- **Missing container.xml** — Raise `InvalidEpubError`.
- **Malformed XML** — Log warning, use available data, continue if possible.
- **Missing .opf** — Raise `InvalidEpubError`.
