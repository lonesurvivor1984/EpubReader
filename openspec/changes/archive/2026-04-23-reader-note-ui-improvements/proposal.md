## Why

工具栏上的"笔记"按钮实际功能是导出笔记，名称不够准确；选中文字时直接弹出笔记编辑框缺少复制选项，用户可能需要仅复制文字而不做标注。

## What Changes

- 工具栏按钮文案从"笔记"改为"导出笔记"，更准确描述其功能
- 选中文字时弹出功能选择面板，提供"复制"和"笔记"两个选项
  - "复制"：将选中的文字写入系统剪贴板
  - "笔记"：进入现有的划线笔记流程（弹出编辑器→输入笔记→紫色虚线下划线）

## Capabilities

### New Capabilities
- `text-selection-actions`: 选中文字后弹出复制/笔记功能选择面板

### Modified Capabilities
- `underline-annotation`: 划线笔记触发方式从"选中即弹编辑器"改为"弹出选择面板→点击笔记→再弹编辑器"

## Impact

- `app/ui/settings.py`: 按钮文案修改
- `app/ui/reader.py`: 注释掉选中即弹编辑器的逻辑，改为弹出选择面板；新增复制到剪贴板的 JS
