# CLI Entry Spec

## Requirements

### Requirement: Default Launch
Running `python main.py` with no arguments SHALL launch the bookshelf view.

#### Scenarios
- **Normal launch** — Opens the bookshelf window, loads library from JSON storage.
- **First launch (no library)** — Opens bookshelf with empty state and "Add Books" button.
- **Application errors** — Log errors to console; do not crash silently.

### Requirement: Direct File Open
Running `python main.py <file.epub>` SHALL open the specified EPUB file directly.

#### Scenarios
- **Valid EPUB path** — Parse the file, add to library (if not already present), open directly in reader view.
- **File not found** — Print error message to stderr, exit with non-zero code.
- **Invalid EPUB** — Print parse error to stderr, exit with non-zero code.
- **Relative path** — Resolve to absolute path before processing.

### Requirement: Help Flag
Running `python main.py --help` SHALL display usage information.

#### Scenarios
- **Help output** — Shows: description, positional arguments (optional file path), available flags, version number.

### Requirement: Version Flag
Running `python main.py --version` SHALL display the application version.
