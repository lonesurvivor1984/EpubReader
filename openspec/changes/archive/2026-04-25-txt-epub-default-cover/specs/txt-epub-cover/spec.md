## ADDED Requirements

### Requirement: Default cover for TXT-to-EPUB conversion
The EPUB file generated from TXT conversion SHALL include a default cover image. The cover SHALL be an SVG image with the book title rendered as text, suitable for display in the bookshelf view.

#### Scenario: Cover image present in generated EPUB
- **WHEN** a TXT file is converted to EPUB
- **THEN** the EPUB contains a cover image item in the OPF manifest with `properties="cover-image"`

#### Scenario: Cover displays title text
- **WHEN** the cover SVG is rendered
- **THEN** it displays the original TXT filename as the title text in a decorative layout
