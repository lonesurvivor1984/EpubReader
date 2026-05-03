# Tasks

## 1. Bookshelf remove card UI

- [x] 1.1 Add `ROLE_IS_REMOVE_CARD` model role and `_paint_remove_card` method in `bookshelf.py` with trash icon and "下架书籍" label, matching add card style
- [x] 1.2 Add `remove_book_requested = Signal()` to `BookshelfView` class
- [x] 1.3 Update `populate_books()` to append both "添加书籍" and "下架书籍" cards at the end of the grid
- [x] 1.4 Handle `ROLE_IS_REMOVE_CARD` in `_on_clicked` to emit `remove_book_requested`

## 2. Book removal dialog and handler

- [x] 2.1 Create `_on_remove_book()` handler in `MainWindow` that opens a dialog with `QListWidget` checkboxes listing all books
- [x] 2.2 On confirm, call `BookManager.remove_book()` for each selected book
- [x] 2.3 Clean up annotation JSON files for removed books (add `remove_annotations(book_id)` in `storage.py`)
- [x] 2.4 Refresh bookshelf after removal
- [x] 2.5 Connect `remove_book_requested` signal to handler in `MainWindow._connect_signals()`

## 3. TXT-to-EPUB cover size and output directory

- [x] 3.1 Increase cover image dimensions from 200x300 to 400x600 in `_build_cover_image()` in `txt_converter.py`, adjusting layout parameters proportionally
- [x] 3.2 Change output directory from Desktop to `txt_path.parent` in `convert_txt_to_epub()` in `txt_converter.py`
