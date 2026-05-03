## Why

1. 书架目前没有"下架"入口，用户误添加书籍后无法在界面上移除。
2. TXT 转 EPUB 的封面图片（200x300）偏小，在书架上显示模糊。
3. TXT 转 EPUB 的输出目录当前硬编码为桌面，不符合用户直觉（文件应与原 TXT 放在一起）。

## What Changes

- 书架视图中，"添加书籍"卡片后增加"下架书籍"卡片（虚线边框 + 垃圾桶图标，风格一致）
- 点击"下架书籍"卡片弹出书籍列表多选对话框，确认后从书架中移除选中的书籍（仅删除元数据，不删除 EPUB 原文件）
- TXT 转 EPUB 的封面尺寸从 200x300 增加到 400x600
- TXT 转 EPUB 的输出目录改为与原 TXT 文件同一目录

## Capabilities

### New Capabilities

- `bookshelf-remove`: 书架视图中支持多选下架书籍

### Modified Capabilities

- `txt-to-epub-conversion`: 封面尺寸从 200x300 增至 400x600；输出目录改为与原 TXT 同目录

## Impact

- `app/ui/bookshelf.py`: 新增"下架"卡片绘制逻辑、`remove_book_requested` 信号
- `app/ui/main_window.py`: 连接下架信号，处理书籍移除确认对话框
- `app/core/txt_converter.py`: 封面尺寸从 200x300 增至 400x600，输出目录改为原 TXT 同目录
