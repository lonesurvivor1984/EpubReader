## ADDED Requirements

### Requirement: Theme color buttons in toolbar
The toolbar SHALL display 4 color swatch buttons: light yellow (`#FFF9E6`), light green (`#E8F5E9`), light blue (`#E3F2FD`), and light gray (`#F5F5F5`). Each swatch SHALL be visually distinct, small in size, and positioned after the existing toolbar controls.

#### Scenario: Toolbar displays 4 color swatches
- **WHEN** the reader view is shown
- **THEN** the toolbar displays 4 color swatch buttons with the specified colors

#### Scenario: Swatch button click emits signal
- **WHEN** the user clicks a color swatch button
- **THEN** the SettingsBar emits a `theme_selected` signal with the corresponding hex color value

### Requirement: Reader background color change
The ReaderView SHALL apply the selected background color to the rendered EPUB content by injecting CSS that sets `background-color` on `html` and `body` elements with `!important` priority. The color change SHALL take effect immediately without reloading the chapter.

#### Scenario: Clicking a swatch changes reading area background
- **WHEN** the user clicks the light yellow swatch
- **THEN** the reader's background changes to `#FFF9E6` without reloading the page

#### Scenario: Color overrides EPUB default background
- **WHEN** the EPUB content has a default white background
- **THEN** the injected color overrides it due to `!important` priority

### Requirement: Theme color persistence
The selected theme color SHALL be persisted in UserPreferences and automatically restored when the user opens a book in a subsequent session. The default value SHALL be an empty string (no color override, i.e., white/default background).

#### Scenario: Theme color saved on selection
- **WHEN** the user selects a theme color
- **THEN** the color hex value is saved to UserPreferences and persisted to disk

#### Scenario: Theme color restored on book open
- **WHEN** the user opens a book and a theme color was previously saved
- **THEN** the reader applies the saved background color automatically
