## 1. Replace QStackedWidget with QSplitter

- [x] 1.1 Remove QStackedWidget wrapping TOCPanel and BookmarkPanel in `_build_ui()`
- [x] 1.2 Add vertical QSplitter with TOCPanel on top and BookmarkPanel on bottom, set initial sizes to 80:20 ratio

## 2. Update Bookmark Button Behavior

- [x] 2.1 Change `_on_toc_toggle` — bookmark button now toggles bookmark panel visibility within the splitter instead of switching panels
- [x] 2.2 Remove `_showing_bookmarks` flag and related panel-switching logic
