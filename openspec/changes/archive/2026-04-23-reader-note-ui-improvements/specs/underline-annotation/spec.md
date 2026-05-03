## MODIFIED Requirements

### Requirement: Text selection detection
The ReaderView SHALL inject JavaScript that listens for `mouseup` events on the document body. When text is selected (`window.getSelection().toString().trim().length > 0`), the script SHALL show a floating action panel with "复制" (copy) and "笔记" (note) options. The note editor is only shown after the user clicks "笔记" in the action panel.

#### Scenario: Selecting text shows action panel
- **WHEN** the user selects text and releases the mouse button
- **THEN** a floating action panel with "复制" and "笔记" options appears below the selected text

#### Scenario: No text selected — no popup
- **WHEN** the user clicks without selecting text
- **THEN** no action panel is shown
