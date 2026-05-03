## Why

从目录点击章节时，划线笔记正常显示（`_on_page_loaded` → `restore_annotations`）。但无缝滚动加载下一章时，划线笔记不出现——`restoreAnnotationsIn` 使用 `surroundContents` 包裹文本，该方法在跨元素边界时静默失败，而 `_on_page_loaded` 使用的 `splitText` 方案没有此问题。

## What Changes

- 修复无缝滚动 `_inject_seamless_scroll` 中的 `restoreAnnotationsIn` 函数：用 `splitText` 替换 `surroundContents`，与 `restore_annotations` 保持一致
- 将 `restoreAnnotationsIn` 改为基于 text node 遍历，逐个 text node 执行 `indexOf` 匹配 + `splitText` 包裹

## Capabilities

### New Capabilities

(none — 纯 bug fix)

### Modified Capcapabilities

- `reader-view`: 无缝滚动章节加载时，划线笔记恢复逻辑从 `surroundContents` 改为 `splitText`

## Impact

- `app/ui/reader.py`: 修改 `_inject_seamless_scroll` 中注入的 JS `restoreAnnotationsIn` 函数
