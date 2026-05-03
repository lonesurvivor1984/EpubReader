## ADDED Requirements

### Requirement: Text selection detection
The ReaderView SHALL inject JavaScript that listens for `mouseup` events on the document body. When text is selected (`window.getSelection().toString().trim().length > 0`), the script SHALL show a floating note editor positioned below the selected text.

#### Scenario: Selecting text triggers note popup
- **WHEN** the user selects text and releases the mouse button
- **THEN** a floating note editor appears below the selected text

#### Scenario: No text selected — no popup
- **WHEN** the user clicks without selecting text
- **THEN** no note editor is shown

### Requirement: Underline styling on annotated text
Text with an associated note SHALL display a light purple dashed underline (`text-decoration: underline; text-decoration-style: dashed; text-decoration-color: #B388FF`). The underline SHALL be applied by wrapping the text in a `<span class="annotated">` element.

#### Scenario: New annotation applies underline
- **WHEN** the user submits a note for selected text
- **THEN** the selected text is wrapped in a `<span class="annotated">` with the purple dashed underline style

#### Scenario: Existing annotations restored on book open
- **WHEN** a book is opened and it has saved annotations for the current chapter
- **THEN** the annotated text is underlined on page load

### Requirement: Floating note editor UI
The note editor SHALL be a `<div>` element created in the DOM, containing a `<textarea>` for note input and Submit/Cancel buttons. It SHALL be positioned below the selected text and SHALL auto-close on Cancel or when focus is lost.

#### Scenario: Submit saves and applies underline
- **WHEN** the user types a note and clicks Submit
- **THEN** the note is saved, the text is underlined, and the editor closes

#### Scenario: Cancel closes editor
- **WHEN** the user clicks Cancel
- **THEN** the editor closes without saving or underlining
