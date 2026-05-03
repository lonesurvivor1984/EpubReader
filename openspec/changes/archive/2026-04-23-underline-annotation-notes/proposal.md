## Why

读者在阅读过程中需要对感兴趣的内容做笔记，当前没有任何标注功能。划线笔记可以让读者标记关键段落并附带个人思考，提升阅读价值。

## What Changes

- 在 WebView 阅读区中，用户选中文本后，自动在文字底部添加浅紫色虚线下划线
- 选中文本后弹出小型编辑框（浮动在页面上），用于输入笔记内容
- 每本书的笔记保存为独立文件（`notes/{book_id}.json`）
- 工具栏新增"笔记"按钮，点击可查看/导出所有笔记为 txt 文件
- 已标注的段落打开书时自动恢复下划线显示

## Capabilities

### New Capabilities
- `underline-annotation`: 选中文本后添加浅紫色虚线下划线、弹出笔记编辑框
- `note-storage`: 每本书独立笔记文件，JSON 格式持久化，支持导出 txt

### Modified Capabilities

## Impact

- `app/ui/reader.py`: 新增选中文本检测、CSS 下划线注入、浮动编辑框注入 JS
- `app/ui/main_window.py`: 新增工具栏笔记按钮、查看/导出笔记对话框
- `app/core/storage.py`: 新增笔记读写函数
- `app/core/models.py`: 新增 Annotation 数据模型
