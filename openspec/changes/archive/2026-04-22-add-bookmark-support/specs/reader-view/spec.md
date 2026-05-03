## ADDED Requirements

### Requirement: Current chapter tracking
The ReaderView SHALL provide a way for the MainWindow to know which chapter is currently loaded. The chapter href SHALL be derivable from the `url_changed` signal or a dedicated getter method.

#### Scenario: Chapter href available after load
- **WHEN** a chapter is loaded via `load_chapter(url)`
- **THEN** the `url_changed` signal emits a URL from which the chapter href can be extracted

#### Scenario: Chapter href is stored on URL change
- **WHEN** the URL changes
- **THEN** MainWindow stores the extracted chapter href for bookmark creation
