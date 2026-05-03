## ADDED Requirements

### Requirement: TXT to EPUB conversion
The system SHALL convert a UTF-8 or GBK encoded TXT file into a valid EPUB 3.0 file. The output EPUB SHALL be readable by the application's built-in EPUB reader.

#### Scenario: Successful conversion of a valid TXT file
- **WHEN** the user selects a valid TXT file with non-empty content
- **THEN** the system produces a valid EPUB file in the output directory

#### Scenario: File encoding auto-detection
- **WHEN** the TXT file uses GBK or UTF-8 encoding
- **THEN** the system SHALL auto-detect the encoding and correctly decode the text content

#### Scenario: Empty TXT file
- **WHEN** the TXT file contains no text or only whitespace
- **THEN** the system SHALL display an error message and not produce an EPUB file

#### Scenario: EPUB structure compliance
- **WHEN** the EPUB file is generated
- **THEN** it SHALL contain: mimetype file, META-INF/container.xml, OPF package, and at least one XHTML content chapter

### Requirement: Text segmentation into chapters
The converter SHALL split the TXT content into multiple XHTML chapters based on blank lines. Each chapter SHALL contain approximately 5000 characters, with no chapter split mid-paragraph.

#### Scenario: Short TXT file (single chapter)
- **WHEN** the TXT content is under 5000 characters
- **THEN** the EPUB SHALL contain a single content chapter

#### Scenario: Long TXT file (multiple chapters)
- **WHEN** the TXT content exceeds 5000 characters
- **THEN** the EPUB SHALL contain multiple chapters, each around 5000 characters

### Requirement: Output file location
The converted EPUB file SHALL be saved on the user's Desktop, with the original TXT filename replaced by `.epub` extension.

#### Scenario: Unique filename
- **WHEN** a file with the same name already exists in the output directory
- **THEN** the system SHALL append a numeric suffix (e.g., `_1`, `_2`) to avoid overwriting
