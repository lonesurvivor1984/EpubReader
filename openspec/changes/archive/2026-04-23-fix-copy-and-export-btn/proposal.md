## Why

复制按钮点击无响应，是因为 `mousedown` 全局监听在 click 之前先触发并移除了面板，导致 click 事件的目标 DOM 已被销毁；"导出笔记"按钮宽度 45px 不够显示四个汉字。

## What Changes

- 修复选择面板的关闭逻辑：点击面板内部按钮时不关闭面板，只有点击外部区域才关闭
- 工具栏"导出笔记"按钮宽度从 45px 调整到 65px

## Capabilities

### New Capabilities

### Modified Capabilities
- `text-selection-actions`: 选择面板关闭逻辑从 "任何 mousedown 都关闭" 改为 "仅点击外部区域才关闭"
- `reader-view`: 导出笔记按钮宽度调整

## Impact

- `app/ui/reader.py`: 修改选择面板 mousedown 处理逻辑
- `app/ui/settings.py`: 按钮宽度调整
