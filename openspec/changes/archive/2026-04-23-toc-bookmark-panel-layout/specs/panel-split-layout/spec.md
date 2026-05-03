## ADDED Requirements

### Requirement: Split panel layout for TOC and bookmarks
The left side panel SHALL display both the TOC and bookmarks panels simultaneously in a vertical layout. The TOC panel SHALL occupy 80% of the available height, and the bookmarks panel SHALL occupy 20% of the available height. Users SHALL be able to adjust the split by dragging a divider.

#### Scenario: Both panels visible on book open
- **WHEN** a book is opened in the reader view
- **THEN** the left panel shows TOC at top (80%) and bookmarks at bottom (20%)

#### Scenario: User can adjust panel sizes
- **WHEN** the user drags the divider between TOC and bookmarks
- **THEN** the relative heights of both panels adjust accordingly

### Requirement: Bookmark button toggles bookmarks area visibility
The bookmark button in the toolbar SHALL expand or collapse the bookmarks area within the left panel, instead of switching between panels. When collapsed, the TOC fills the entire left panel.

#### Scenario: Bookmark button toggles visibility
- **WHEN** the user clicks the bookmark button
- **THEN** the bookmarks area is shown if hidden, or hidden if shown
