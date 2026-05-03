# Tasks

## 1. Add default SVG cover to TXT-to-EPUB

- [x] 1.1 Add `_build_cover_svg(title: str) -> bytes` function in `txt_converter.py`: generates an SVG cover with title text centered on a gradient background
- [x] 1.2 Update `_build_opf` to include cover image item with `properties="cover-image"`
- [x] 1.3 Update `convert_txt_to_epub` to write cover.svg into EPUB zip
