## ADDED Requirements

### Requirement: Per-book note file storage
Each book SHALL have its own note file stored at `notes/{book_id}.json`. The file format SHALL be a JSON array of annotation objects containing `id`, `chapter_href`, `selected_text`, `note`, and `created_at`.

#### Scenario: New note saved to book file
- **WHEN** an annotation is saved for a book
- **THEN** the annotation is appended to `notes/{book_id}.json`

#### Scenario: Notes loaded on book open
- **WHEN** a book is opened
- **THEN** notes are loaded from `notes/{book_id}.json` and passed to the ReaderView

### Requirement: Note export to txt
The system SHALL support exporting a book's notes to a plain text file. Each exported entry SHALL include the selected text, the note content, the chapter href, and the timestamp.

#### Scenario: Export notes as txt
- **WHEN** the user clicks the export notes button
- **THEN** a file dialog prompts for a save location and a txt file is written with all notes
