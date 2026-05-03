## ADDED Requirements

### Requirement: Bookshelf remove card
The bookshelf view SHALL display a "下架书籍" card next to the "添加书籍" card at the end of the grid. The remove card SHALL use the same visual style as the add card (dashed border, icon, label).

#### Scenario: Remove card is rendered at grid end
- **WHEN** the bookshelf grid is populated with books
- **THEN** the last two items in the grid are the "添加书籍" card and the "下架书籍" card

#### Scenario: Remove card visual style matches add card
- **WHEN** the remove card is rendered
- **THEN** it uses a dashed gray border, a trash/removal icon, and the label "下架书籍"

### Requirement: Book removal confirmation dialog
Clicking the "下架书籍" card SHALL open a confirmation dialog listing all books in the library with checkboxes, allowing the user to select one or more books to remove.

#### Scenario: Dialog shows all books with checkboxes
- **WHEN** the user clicks the "下架书籍" card
- **THEN** a dialog opens showing all library books with checkboxes and titles

#### Scenario: User cancels the removal dialog
- **WHEN** the user closes the dialog without confirming
- **THEN** no books are removed and the user returns to the bookshelf

### Requirement: Book removal execution
When the user confirms book removal in the dialog, the selected books SHALL be removed from the library. Removal SHALL only delete library metadata (book entry, reading state, bookmarks, annotations), NOT the original EPUB file.

#### Scenario: Remove one or more books
- **WHEN** the user selects books in the dialog and clicks confirm
- **THEN** the selected books are removed from the library and the bookshelf refreshes

#### Scenario: Remove a book that was previously read
- **WHEN** a removed book has saved reading state, bookmarks, and annotations
- **THEN** all associated reading state, bookmarks, and annotations are also removed

#### Scenario: Remove all books
- **WHEN** the user selects all books and confirms removal
- **THEN** the library becomes empty and the bookshelf shows only the "添加书籍" and "下架书籍" cards
