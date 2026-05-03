## Why

读者每次重新打开一本书都只能从头开始阅读，无法快速跳转到之前标记的位置。虽然系统已经保存了阅读进度（`ReadingState`），但用户缺少书签功能来标记和快速跳转到重要的阅读位置。

## What Changes

- 在阅读器页面添加书签按钮（添加到 SettingsBar），点击后保存当前章节+滚动位置为书签
- 新增书签面板/菜单，列出该书的所有书签，点击后跳转到对应位置
- 书签支持可选备注（可选，非必填）和删除操作
- 书签数据已通过 `Bookmark` 模型和存储层持久化，本次只需添加 UI 层

## Capabilities

### New Capabilities
- `bookmark-ui`: 书签的创建、查看、删除和跳转交互。包括书签按钮、书签列表面板、书签创建对话框

### Modified Capabilities
- `reader-view`: 新增书签创建和跳转能力（通过 SettingsBar 的信号和 BookmarkManager 集成）

## Impact

- `app/ui/settings.py`: 新增书签按钮和 `bookmark_add` 信号
- `app/ui/main_window.py`: 新增书签面板、书签创建/删除/跳转逻辑
- `app/ui/reader.py`: 可能需要暴露获取当前章节 href 的方法（目前已有 `url_changed` 信号）
- 数据层已就绪：`Bookmark` 模型、`storage.py`、`book_manager.py` 的书签 API 均已实现
