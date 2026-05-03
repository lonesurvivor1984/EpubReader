## Context

书架视图中只有"添加书籍"卡片，用户无法通过界面移除已添加的书籍。当前 `BookManager.remove_book()` 方法已存在，但缺少 UI 入口。同时需要清理关联的 annotation 文件（当前 `storage.remove_book` 不处理 annotation 文件）。

TXT 转 EPUB 当前封面尺寸 200x300，书架显示偏小。输出目录当前为 Desktop，用户期望与原 TXT 文件同目录。

## Goals / Non-Goals

**Goals:**
- 书架添加"下架书籍"卡片入口
- 支持多选下架书籍（含确认对话框）
- 下架时清理书籍元数据 + 笔记文件
- TXT 转 EPUB 封面尺寸翻倍（400x600）
- TXT 转 EPUB 输出到原 TXT 同目录

**Non-Goals:**
- 下架不删除原始 EPUB 文件（仅从书架移除）
- 不支持单本书右键菜单下架（未来可扩展）

## Decisions

### 下架 UI 方案

**Decision**: 在书架网格末尾添加"下架书籍"卡片（虚线边框 + 图标 + 文字），风格与"添加书籍"卡片一致。点击后弹出对话框列出所有书籍供多选。

**Rationale**: 
- 与现有"添加书籍"卡片风格统一，用户易于发现
- 多选对话框比右键菜单更直观，适合批量操作
- 使用 `QInputDialog` 自定义对话框 + `QListWidget` 带 checkbox

### 下架清理范围

**Decision**: 下架时调用 `BookManager.remove_book()`（已处理 library entry + reading_state + bookmarks + server unregistration），额外删除对应 book_id 的 annotation JSON 文件。

### 封面尺寸

**Decision**: `_build_cover_image` 中 `W, H` 从 `200, 300` 改为 `400, 600`，其余布局参数按比例调整。

### TXT 转 EPUB 输出目录

**Decision**: 输出目录从 `Path.home() / "Desktop"` 改为 `txt_path.parent`（原 TXT 文件所在目录）。

## Risks / Trade-offs

- 书架上只有少量书籍时，"添加"和"下架"卡片占据一行的大部分空间，视觉上可能略显空旷。这是可接受的，网格布局会自动调整。
- 下架对话框的 `QListWidget` 带 checkbox 需要自定义 item widget，PySide6 中可用 `setCheckState` 实现。
- 下架后 annotation 文件被删除，不可恢复。这是预期行为，因为书籍已从书架移除。
