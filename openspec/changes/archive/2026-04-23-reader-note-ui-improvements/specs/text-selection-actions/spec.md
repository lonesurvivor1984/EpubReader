## ADDED Requirements

### Requirement: Text selection action panel
When text is selected in the reader, the system SHALL show a floating action panel with two options: "复制" (copy) and "笔记" (note). The panel SHALL appear below the selected text and SHALL dismiss when an option is chosen or when the user clicks elsewhere.

#### Scenario: Action panel appears on text selection
- **WHEN** the user selects text and releases the mouse button
- **THEN** a floating action panel with "复制" and "笔记" buttons appears below the selected text

#### Scenario: Copy option copies text to clipboard
- **WHEN** the user clicks "复制"
- **THEN** the selected text is written to the system clipboard and the panel closes

#### Scenario: Note option triggers note editor
- **WHEN** the user clicks "笔记"
- **THEN** the note editor (textarea) appears below the selected text, following the existing underline annotation flow

#### Scenario: Panel dismisses on escape or outside click
- **WHEN** the user presses Escape or clicks outside the panel
- **THEN** the panel closes without any action

### Requirement: Toolbar button rename
The toolbar button for exporting notes SHALL display the text "导出笔记" instead of "笔记".

#### Scenario: Toolbar button shows export label
- **WHEN** the reader view is active
- **THEN** the export button displays "导出笔记"
