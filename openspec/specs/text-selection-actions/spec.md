## ADDED Requirements

### Requirement: Text selection action panel
When text is selected in the reader, the system SHALL show a floating action panel with two options: "复制" (copy) and "笔记" (note). The panel SHALL appear below the selected text and SHALL dismiss when the user clicks **outside** the panel or presses Escape. Clicking inside the panel (on buttons) SHALL NOT dismiss it — the button's click handler shall execute normally.

#### Scenario: Action panel appears on text selection
- **WHEN** the user selects text and releases the mouse button
- **THEN** a floating action panel with "复制" and "笔记" buttons appears below the selected text

#### Scenario: Copy button executes and then panel closes
- **WHEN** the user clicks "复制"
- **THEN** the selected text is written to the system clipboard and the panel closes via the button handler

#### Scenario: Note button opens note editor
- **WHEN** the user clicks "笔记"
- **THEN** the note editor (textarea) appears below the selected text and the panel closes via the button handler

#### Scenario: Click outside panel dismisses it
- **WHEN** the user clicks anywhere outside the action panel or presses Escape
- **THEN** the panel closes without any action

### Requirement: Toolbar button rename
The toolbar button for exporting notes SHALL display the text "导出笔记" instead of "笔记".

#### Scenario: Toolbar button shows export label
- **WHEN** the reader view is active
- **THEN** the export button displays "导出笔记"
