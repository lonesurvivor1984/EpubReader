# Implementation Tasks

## 1. 工具栏按钮文案

- [x] 1.1 将 `app/ui/settings.py` 中"笔记"按钮文案改为"导出笔记"

## 2. 选择面板 JS

- [x] 2.1 修改 `_inject_note_editor`：选中文字时弹出选择面板（复制/笔记），而非直接弹出笔记编辑器
- [x] 2.2 选择面板样式：`position: fixed`、半透明深色背景、毛玻璃效果
- [x] 2.3 "复制"按钮逻辑：`navigator.clipboard.writeText()` + 降级到 `execCommand('copy')`，关闭面板
- [x] 2.4 "笔记"按钮逻辑：关闭选择面板，显示现有的笔记编辑器
- [x] 2.5 选择面板按 Escape 或点击外部关闭
