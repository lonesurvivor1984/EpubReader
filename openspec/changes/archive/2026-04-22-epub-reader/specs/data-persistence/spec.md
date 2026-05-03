# Data Persistence Spec

## Requirements

### Requirement: Library Data Storage
The application SHALL persist all library data to a JSON file.

#### Scenarios
- **Default location** — `data/library.json` in the project directory (or `~/.epubreader/library.json` when packaged).
- **Atomic writes** — Write to a temporary file, then rename to `library.json` to prevent corruption.
- **Missing file on launch** — Create a new empty library structure.
- **Invalid JSON on launch** — Back up the corrupted file (append `.bak`), create a new empty library, show a warning.

### Requirement: Library Data Schema
The JSON file SHALL follow the defined schema with version tracking.

#### Scenarios
- **Version mismatch** — If `version` is older than current, apply migration logic. If unable to migrate, back up and create new.
- **Unknown fields** — Unknown fields are preserved (round-tripped) but ignored by the application.
- **New fields added in future** — New features add fields with sensible defaults; existing entries are not invalidated.

### Requirement: Reading State
The application SHALL persist per-book reading state.

#### Scenarios
- **Save reading state** — Store `{book_id: {chapter_href, scroll_offset, progress_pct, last_read_at}}`.
- **Load reading state** — On book open, check for saved state and restore position.
- **Book not found** — If the book has no saved state, open at the first chapter.

### Requirement: Bookmarks
The application SHALL persist per-book bookmarks.

#### Scenarios
- **Bookmark structure** — Each bookmark has: `{id, chapter_href, scroll_offset, note, created_at}`.
- **Add bookmark** — Create entry in `bookmarks[book_id]` array, save to JSON.
- **Load bookmarks** — On book open, load all bookmarks for the book.
- **Remove bookmark** — Delete entry from `bookmarks[book_id]` array, save to JSON.

### Requirement: User Preferences
The application SHALL persist user-level preferences.

#### Scenarios
- **Font size** — Integer value (default 16px).
- **Theme** — "light" or "dark" (default "light").
- **TOC panel visibility** — Boolean (default true).
- **Location** — Same JSON file, top-level `preferences` key.
- **Load on startup** — Restore preferences when the application launches.
