## ADDED Requirements

### Requirement: Scroll-to-bottom detection
The ReaderView SHALL inject JavaScript into loaded chapters that detects when the user scrolls within 200px of the page bottom, indicating they are about to finish the current chapter.

#### Scenario: Scroll near bottom triggers detection
- **WHEN** the user scrolls to within 200px of the bottom of the page
- **THEN** the injected script detects the condition and prepares to load the next chapter

### Requirement: Automatic next chapter loading
When scroll-to-bottom is detected and there is a next chapter available, the ReaderView SHALL fetch the next chapter's HTML from the local server and append its `<body>` content to the current page DOM, preserving scroll position.

#### Scenario: Next chapter loaded and appended
- **WHEN** the user scrolls to the bottom and a next chapter exists in the chapter list
- **THEN** the next chapter content is fetched from the server and appended to the page body with a chapter title header

#### Scenario: No more chapters to load
- **WHEN** the user scrolls to the bottom and no more chapters remain
- **THEN** no action is taken and a subtle end-of-book indicator may be shown

### Requirement: Chapter divider and title
Each automatically loaded chapter SHALL be preceded by a visible divider element containing the chapter title and a horizontal rule, so readers can distinguish where one chapter ends and the next begins.

#### Scenario: Divider appears before appended chapter
- **WHEN** a new chapter is appended to the page
- **THEN** a `<div class="chapter-divider">` with the chapter title and `<hr>` appears above the new content

### Requirement: Chapter list initialization
When a book is opened, the ReaderView SHALL receive the full ordered list of chapter hrefs, allowing it to determine which chapter comes next.

#### Scenario: Chapter list passed to reader on book open
- **WHEN** `_open_book()` is called with a book
- **THEN** the chapter href list is passed to `ReaderView.set_chapter_list()`

### Requirement: Reset on TOC/bookmark navigation
When the user navigates to a chapter via the table of contents or a bookmark, the seamless scrolling state SHALL be reset — only the target chapter is loaded, and the chapter list index is set to the selected chapter.

#### Scenario: TOC navigation resets seamless scroll
- **WHEN** the user clicks a TOC item to navigate
- **THEN** the reader loads only that chapter and resets the chapter list index
