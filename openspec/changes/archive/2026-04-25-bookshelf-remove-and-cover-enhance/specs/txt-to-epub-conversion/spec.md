## MODIFIED Requirements

### Requirement: Output file location
The converted EPUB file SHALL be saved in the same directory as the source TXT file, with the original TXT filename replaced by `.epub` extension.

#### Scenario: Unique filename
- **WHEN** a file with the same name already exists in the output directory
- **THEN** the system SHALL append a numeric suffix (e.g., `_1`, `_2`) to avoid overwriting

## ADDED Requirements

### Requirement: Cover image size
The default cover image generated for TXT-to-EPUB conversion SHALL be 400x600 pixels (PNG format).

#### Scenario: Cover dimensions are 400x600
- **WHEN** a TXT file is converted to EPUB
- **THEN** the embedded cover.png has dimensions of 400x600 pixels
