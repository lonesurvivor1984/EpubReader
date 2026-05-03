# Reading Spec

## Requirements

### Requirement: Scrolling Reading
The reading view SHALL display EPUB chapter content in a continuous scrolling format.

#### Scenarios
- **Single chapter** — Chapter HTML renders in QWebEngineView with native scrolling.
- **Chapter navigation** — Clicking internal anchors (`<a href="#section1">`) scrolls to the anchor within the page.
- **Next chapter** — Reaching the end of a chapter does NOT auto-advance; user uses TOC or keyboard shortcut.

### Requirement: TOC Panel
A sidebar panel SHALL display the book's table of contents for navigation.

#### Scenarios
- **Hierarchical TOC** — Nested TOC items display with indentation (e.g., Part > Chapter > Section).
- **Click to navigate** — Clicking a TOC item navigates to the corresponding chapter/section in the WebEngineView.
- **Current position highlight** — The TOC item for the currently visible section is highlighted.
- **Show/hide** — The TOC panel can be toggled visible/hidden via a button or keyboard shortcut (e.g., F2).

### Requirement: Reading Progress Tracking
The application SHALL track and persist the user's reading position.

#### Scenarios
- **Auto-save** — Reading position (chapter href + scroll offset) is saved every 30 seconds.
- **Save on navigate** — Position is saved when the user navigates to a different chapter.
- **Save on close** — Position is saved when the reader view is closed (returning to bookshelf or exiting).
- **Restore on open** — When opening a book with saved state, navigate to the saved chapter and scroll to the saved offset.

### Requirement: Font Size Control
Users SHALL be able to adjust the reading font size.

#### Scenarios
- **Increase font** — Click "+" or use Ctrl+= to increase base font size.
- **Decrease font** — Click "-" or use Ctrl+- to decrease base font size.
- **Reset font** — Click "Reset" or use Ctrl+0 to return to default font size.
- **Persistence** — Font size preference is persisted per-user (not per-book) and restored on next launch.

### Requirement: Theme Toggle
Users SHALL be able to switch between light and dark reading themes.

#### Scenarios
- **Light theme** — Default. White/light background, dark text.
- **Dark theme** — Dark background, light text. Achieved via CSS injection into the WebEngineView.
- **Toggle** — Click theme button or use keyboard shortcut to switch.
- **Persistence** — Theme preference is persisted per-user and restored on next launch.

### Requirement: Keyboard Shortcuts
Common reading actions SHALL be accessible via keyboard shortcuts.

#### Scenarios
- **Toggle TOC** — F2 or Ctrl+T
- **Increase font** — Ctrl+=
- **Decrease font** — Ctrl+-
- **Reset font** — Ctrl+0
- **Toggle theme** — Ctrl+D
- **Back to bookshelf** — Escape (when not in a text input)
