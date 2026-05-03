# Tasks

## 1. Core conversion module

- [x] 1.1 Create `app/core/txt_converter.py` with `convert_txt_to_epub(txt_path: str, output_dir: str) -> str` function: reads TXT (with encoding auto-detect), splits into ~5000 char chapters, generates EPUB 3.0 using zipfile + lxml
- [x] 1.2 Add `chardet` to PyInstaller hidden imports in `EpubReader.spec`

## 2. UI integration

- [x] 2.1 Add "TXT格式转换" button to bookshelf header in `MainWindow._build_ui()`
- [x] 2.2 Connect button to handler: open file dialog → call converter → show success/error dialog with output path
