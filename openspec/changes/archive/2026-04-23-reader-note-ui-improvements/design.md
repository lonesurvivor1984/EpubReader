## Context

当前划线笔记功能：选中文字后立即弹出笔记编辑器（textarea），用户只能选择"记笔记"。工具栏按钮文案为"笔记"，实际功能是导出笔记到 txt，名称不准确。

## Goals / Non-Goals

**Goals:**
- 工具栏按钮文案改为"导出笔记"，明确表达功能
- 选中文字时弹出选择面板，提供"复制"和"笔记"两个选项
- "复制"将文字写入系统剪贴板（通过 `navigator.clipboard.writeText`）
- "笔记"进入现有划线笔记流程，保持功能不变

**Non-Goals:**
- 不修改笔记存储/导出逻辑
- 不修改划线样式或气泡显示逻辑
- 不增加更多选项（如高亮、分享等）

## Decisions

### 选择面板实现方式

**Decision**: 纯 JS 实现选择面板，类似当前笔记编辑器的注入方式

**Rationale**:
- 与现有 `_inject_note_editor` 模式一致，都是 JS 注入
- 不依赖额外 Python UI 组件，保持轻量
- 面板样式用 `position: fixed` 定位在选中区域旁边，避免滚动偏移

**Alternatives considered**:
- 用 Qt 组件弹出菜单：跨进程通信复杂，不如纯 JS 直接
- 右键菜单：需要自定义 contextmenu，可能与 EPUB 原有右键冲突

### 复制功能实现

**Decision**: 使用 `navigator.clipboard.writeText()` 实现复制

**Rationale**:
- QtWebEngine 基于 Chromium，支持 Clipboard API
- 如果 `navigator.clipboard` 不可用（非 https context），降级使用 `document.execCommand('copy')`

### 选择面板样式

- 半透明深色背景 + 毛玻璃效果，与气泡风格一致
- 两个按钮：`[📋 复制] [📝 笔记]`
- 按 Escape 或点击其他地方关闭面板

## Risks / Trade-offs

- [风险] 某些 EPUB 页面可能禁止 `navigator.clipboard` → 降级到 `execCommand`
- [风险] 选择面板位置可能在视口外 → 面板出现后检测边界，自动调整到可见区域
