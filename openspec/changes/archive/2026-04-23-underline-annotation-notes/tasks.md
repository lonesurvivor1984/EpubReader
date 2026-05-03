# Implementation Tasks

## 1. Models & Storage

- [x] 1.1 Add `Annotation` dataclass to `app/core/models.py` (id, chapter_href, selected_text, note, created_at)
- [x] 1.2 Add `NOTES_DIR` to `app/config.py`
- [x] 1.3 Add `save_annotations()`, `load_annotations()`, `export_notes_txt()` functions to `app/core/storage.py`

## 2. ReaderView — Text Selection & Note Popup

- [x] 2.1 Add `annotation_created = Signal(dict)` signal to ReaderView (emits {chapter_href, selected_text, note})
- [x] 2.2 Add `_inject_note_editor()` JS that:
  - Listens for `mouseup`, detects text selection
  - Creates floating note editor DOM below selection
  - On submit: wraps text in `<span class="annotated">`, emits data to Python
  - On cancel: closes editor
- [x] 2.3 Add `restore_annotations(chapter_href, annotations)` method that injects underlines for existing notes

## 3. MainWindow — Wire Annotations

- [x] 3.1 Connect `annotation_created` signal to storage save handler
- [x] 3.2 In `_open_book()`, load and pass existing annotations to ReaderView
- [x] 3.3 Add toolbar "笔记" button to view/export notes
