## Context

阅读区使用 QWebEngineView 渲染 EPUB 内容，通过 QWebEngineScript 注入 CSS 和 JavaScript。笔记需要监听选中文本事件，在 JS 层面用 `<span>` 包裹标注内容并添加下划线样式。笔记数据通过 `runJavaScript` 传递到 Python 层，由 storage 层持久化。

## Goals / Non-Goals

**Goals:**
- 选中文本后自动添加浅紫色虚线下划线
- 弹出浮动编辑框输入笔记
- 每本书独立笔记文件
- 支持导出为 txt
- 打开书时恢复已有的下划线标注

**Non-Goals:**
- 不做多色标注（仅浅紫色一种）
- 不做跨书笔记（每本书独立）
- 不做笔记同步到云端

## Decisions

### 1. 标注实现：JS 监听 `selectionchange` + `mouseup`
**Decision:** 注入 JS 监听 `mouseup` 事件，检测 `window.getSelection()` 是否有文本选中。如有且长度 > 0，弹出浮动编辑框。编辑框使用 DOM 元素定位在选中文本下方。

用户输入笔记后，JS 将选中文本用 `<span class="annotated">` 包裹，应用 `text-decoration: underline; text-decoration-style: dashed; text-decoration-color: #B388FF`。同时将文本内容、笔记、chapter href 传回 Python 层保存。

**Rationale:** 纯 JS 方案最直接，无需 C++ 层面的 QWebChannel。

### 2. 笔记数据存储
**Decision:** 在 `data/notes/` 目录下，每本书一个 JSON 文件：`{book_id}.json`。格式：
```json
[
  {
    "id": "uuid",
    "chapter_href": "OEBPS/Text/text0007.xhtml",
    "selected_text": "被标注的文字",
    "note": "笔记内容",
    "created_at": "2026-04-23T..."
  }
]
```

**Rationale:** 简单直观，每本书独立文件易于管理和导出。

### 3. 下划线恢复：打开书时注入
**Decision:** 打开书后，从笔记文件读取当前章节的标注列表，注入 JS 在页面上查找匹配的文本节点并用 `<span class="annotated">` 包裹。

由于 EPUB 内容经过章节合并（seamless scroll），同一页面可能包含多个章节。需要遍历所有标注，在当前页面文本中查找匹配位置。

### 4. 浮动编辑框：JS 创建 DOM
**Decision:** 编辑框完全用 JS 创建为 DOM 元素（`<div>` 含 `<textarea>` 和提交/取消按钮），定位在选中文本下方。不创建 Qt 级别浮动窗口，避免 Z-order 和定位问题。

## Risks / Trade-offs

- **[Risk]** 文本匹配可能不精确（HTML 中标题、空格、换行等差异导致匹配失败）。→ **Mitigation:** 使用文本内容的标准化版本（去除多余空白、忽略大小写）进行匹配，匹配失败时不下划线恢复，不影响阅读。
- **[Risk]** 大量标注导致页面 DOM 变大。→ **Mitigation:** 普通书籍标注数通常 < 50，影响可忽略。
