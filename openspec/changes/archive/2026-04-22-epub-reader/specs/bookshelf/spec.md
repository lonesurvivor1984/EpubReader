# Bookshelf Spec

## Requirements

### Requirement: Bookshelf Display
The application SHALL display a grid view of all books in the user's library on launch.

#### Scenarios
- **Empty library** — The bookshelf shows an empty state with a prominent "Add Books" button.
- **Library with books** — Each book is displayed as a card with: cover thumbnail, title (bold), author (smaller, gray), and a progress indicator (percentage or bar).
- **Large library** — The grid scrolls vertically; layout adapts to window width (responsive column count).

### Requirement: Cover Thumbnail
Each book card SHALL display a cover image extracted from the EPUB file.

#### Scenarios
- **EPUB has cover metadata** — Use the image referenced by `<meta name="cover">` in the `.opf` file.
- **EPUB has no cover** — Display a default placeholder icon with the book title.
- **Cover extraction fails** — Display a placeholder icon.

### Requirement: Add Book
Users SHALL be able to add EPUB files to the library.

#### Scenarios
- **Click "Add Book"** — Opens a file picker filtered to `.epub` files. Selected files are parsed and added to the library.
- **Drag and drop** — Dropping `.epub` files onto the bookshelf window adds them to the library.
- **Duplicate file** — If a file with the same absolute path already exists in the library, show a warning dialog (do not duplicate the entry).
- **Invalid file** — If the dropped file is not a valid EPUB, show an error toast. Do not crash.

### Requirement: Open Book
Clicking a book card SHALL open the book in the reading view.

#### Scenarios
- **First-time open** — Opens at the first chapter.
- **Returning** — Opens at the last-read position (chapter + scroll offset) if saved in reading state.

### Requirement: File Removed Detection
If a book's source file has been moved or deleted, the bookshelf SHALL indicate this.

#### Scenarios
- **File missing on launch** — The card shows a "File not found" badge. Clicking opens a file picker to relocate.
- **User chooses to relocate** — Update the `file_path` in library data. Re-parse the EPUB.
- **User chooses to remove** — Remove the book from the library and its reading state/bookmarks.
