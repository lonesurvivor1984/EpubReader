## 1. Model & Preferences

- [x] 1.1 Add `theme_color: str = ""` field to `UserPreferences` in `app/core/models.py`

## 2. SettingsBar — Color Swatches

- [x] 2.1 Add `theme_selected = Signal(str)` signal to `SettingsBar`
- [x] 2.2 Create 4 QLabel color swatches (light yellow, green, blue, gray) with fixed size and stylesheet
- [x] 2.3 Wire each swatch's mouse press event to emit `theme_selected` with its hex color

## 3. ReaderView — Background Color

- [x] 3.1 Add `set_background_color(color: str)` method to `ReaderView` that injects CSS `background-color` on `html, body`
- [x] 3.2 Merge background color into existing `_apply_styles` method (shared `<style id="epub-reader-theme">` tag)

## 4. MainWindow — Wiring

- [x] 4.1 Connect `SettingsBar.theme_selected` signal to a handler that calls `ReaderView.set_background_color` and saves preferences
- [x] 4.2 Restore saved theme color in `_open_book` after loading the book

## 5. Verification

- [x] 5.1 Test clicking each swatch changes reading area background immediately
- [x] 5.2 Test theme color persists across app restart
