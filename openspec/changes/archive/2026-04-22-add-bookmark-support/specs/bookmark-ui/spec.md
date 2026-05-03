## ADDED Requirements

### Requirement: Bookmark creation button
The SettingsBar SHALL display a bookmark button. When clicked, it SHALL emit a `bookmark_add` signal that the MainWindow connects to create a bookmark at the current reading position.

#### Scenario: User clicks bookmark button
- **WHEN** the user clicks the "BM" button in the SettingsBar
- **THEN** a bookmark is created with the current chapter href and scroll offset

#### Scenario: Bookmark creation when no book is open
- **WHEN** no book is currently open
- **THEN** clicking the bookmark button has no effect

### Requirement: Bookmark list panel
The application SHALL display a bookmark list panel that shows all bookmarks for the current book. Each entry SHALL show the chapter title (or href fallback) and creation time. The panel SHALL be toggleable via a button.

#### Scenario: Toggle bookmark panel visibility
- **WHEN** the user clicks the bookmark panel toggle button
- **THEN** the bookmark list panel is shown if hidden, or hidden if shown

#### Scenario: Bookmark list displays existing bookmarks
- **WHEN** a book with saved bookmarks is opened
- **THEN** the bookmark list panel shows all bookmarks with chapter title and timestamp

#### Scenario: Empty bookmark list
- **WHEN** the current book has no bookmarks
- **THEN** the panel displays a placeholder message (e.g., "No bookmarks yet")

### Requirement: Bookmark navigation
Clicking a bookmark in the list SHALL navigate the reader to the saved chapter and scroll position.

#### Scenario: Navigate to bookmark
- **WHEN** the user clicks a bookmark entry in the list
- **THEN** the reader loads the saved chapter and scrolls to the saved offset

### Requirement: Bookmark deletion
Each bookmark entry SHALL have a delete action (right-click context menu or delete button). Deleting a bookmark SHALL remove it from persistent storage.

#### Scenario: Delete a bookmark
- **WHEN** the user deletes a bookmark from the list
- **THEN** the bookmark is removed from storage and the list updates immediately
