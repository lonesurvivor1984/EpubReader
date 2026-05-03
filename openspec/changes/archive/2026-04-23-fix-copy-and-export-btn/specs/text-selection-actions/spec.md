## MODIFIED Requirements

### Requirement: Action panel dismiss behavior
The action panel SHALL dismiss only when the user clicks **outside** the panel or presses Escape. Clicking inside the panel (on buttons or other content) SHALL NOT dismiss the panel — the button's click handler shall execute normally.

#### Scenario: Copy button executes and then panel closes
- **WHEN** the user clicks "复制" on the action panel
- **THEN** the selected text is copied to clipboard and the panel closes via the button handler, not dismiss logic

#### Scenario: Note button opens note editor
- **WHEN** the user clicks "笔记" on the action panel
- **THEN** the note editor appears below the selected text and the panel closes via the button handler

#### Scenario: Click outside panel dismisses it
- **WHEN** the user clicks anywhere outside the action panel
- **THEN** the panel closes without any action

## ADDED Requirements

(none)

## REMOVED Requirements

(none)
