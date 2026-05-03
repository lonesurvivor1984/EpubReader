## ADDED Requirements

### Requirement: Toolbar TXT conversion button
The bookshelf view SHALL display a "TXT格式转换" button in the top header bar. Clicking it SHALL open a file dialog to select a TXT file.

#### Scenario: User clicks TXT conversion button
- **WHEN** the user clicks "TXT格式转换" on the bookshelf header
- **THEN** a file open dialog appears, filtering for `.txt` files

#### Scenario: User selects a TXT file
- **WHEN** the user selects a valid `.txt` file and confirms
- **THEN** the system converts the file to EPUB and shows a success dialog with the output path

#### Scenario: User cancels the file dialog
- **WHEN** the user closes the file dialog without selecting a file
- **THEN** no action is taken and the user returns to the bookshelf

#### Scenario: Conversion failure
- **WHEN** the conversion process encounters an error (e.g., unreadable file)
- **THEN** the system SHALL display an error dialog describing the failure
