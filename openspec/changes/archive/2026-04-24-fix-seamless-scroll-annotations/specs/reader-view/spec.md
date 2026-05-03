## MODIFIED Requirements

### Requirement: Seamless scroll chapter loading
When the user scrolls near the bottom of the reader, the next chapter SHALL be fetched and appended to the current page. All existing annotations (underlined notes) from the current book SHALL be restored in the newly appended chapter content using reliable text wrapping.

#### Scenario: Scrolling into a chapter with existing annotations
- **WHEN** the user scrolls into a chapter that contains previously saved annotations
- **THEN** the underlined annotation spans appear on the matching text in the newly loaded chapter

#### Scenario: Chapter loading via TOC click
- **WHEN** the user clicks a chapter in the table of contents
- **THEN** annotations for that chapter are restored via `_on_page_loaded`

## ADDED Requirements

(none)

## REMOVED Requirements

(none)
