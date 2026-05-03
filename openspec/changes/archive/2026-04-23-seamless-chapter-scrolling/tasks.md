## 1. ReaderView — Chapter List Tracking

- [x] 1.1 Add `_chapter_hrefs: list[str]` and `_chapter_index: int` fields to `ReaderView`
- [x] 1.2 Add `set_chapter_list(href: str, hrefs: list[str])` method to set the full chapter list and current position

## 2. ReaderView — Seamless Scroll Injection

- [x] 2.1 Add `_inject_seamless_scroll()` method that runs JavaScript to:
  - Store chapter list and server base URL in JS variables
  - Inject scroll detection logic (within 200px of bottom)
  - On trigger: fetch next chapter via `fetch()`, extract `<body>`, append to DOM with chapter divider
- [x] 2.2 Call `_inject_seamless_scroll()` in `_on_page_loaded` after styles are re-applied

## 3. ReaderView — Chapter Divider CSS

- [x] 3.1 Add chapter divider styles to the injected CSS (centered title, horizontal rule, spacing)

## 4. MainWindow — Wire Chapter List

- [x] 4.1 In `_open_book()`, pass the chapter href list to `ReaderView.set_chapter_list()` after loading the book

## 5. TOC/Bookmark Navigation — Reset

- [x] 5.1 Ensure `_on_toc_navigate()` calls `set_chapter_list()` to reset the index to the selected chapter
- [x] 5.2 Ensure `_on_bookmark_navigate()` calls `set_chapter_list()` to reset the index to the bookmarked chapter
