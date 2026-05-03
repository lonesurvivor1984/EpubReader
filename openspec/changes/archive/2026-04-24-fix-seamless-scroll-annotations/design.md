## Context

`_inject_seamless_scroll` 注入的 JS 包含 `restoreAnnotationsIn(el)` 函数，用于在无缝滚动加载下一章时恢复划线笔记。该函数用 `surroundContents` 包裹匹配文本，但此方法在 Range 跨越元素边界时会静默失败。而 `_on_page_loaded` 调用的 `restore_annotations` 使用 `splitText` 逐个 text node 包裹，从未失败。

## Goals / Non-Goals

**Goals:**
- 修复无缝滚动时划线笔记不显示的问题
- 与 `restore_annotations` 使用一致的可靠包裹方案

**Non-Goals:**
- 不改变无缝滚动的加载逻辑
- 不改变 TOC 点击加载的行为

## Decisions

### 文本包裹方案

**Decision**: 将 `restoreAnnotationsIn` 的包裹逻辑从 `surroundContents` 改为 `splitText`，与 `restore_annotations` 保持一致。

**Rationale**: `surroundContents` 对跨元素边界的文本（如被 `<br>`、`<span>` 等元素分隔的文本）会静默失败。`splitText` 只操作 text node，不会遇到边界问题。此前 `restore_annotations` 已从 `surroundContents` 迁移到 `splitText`，无缝滚动函数应同步。

**实现方式**: 将 `restoreAnnotationsIn` 改为基于 TreeWalker 的 text node 遍历（与 `restore_annotations` 相同），对每个 text node 执行 `indexOf` 匹配，然后用 `splitText` 创建 `span.annotated`。

## Risks / Trade-offs

- 无。这是纯粹的 bug fix，与已验证的 `splitText` 方案保持一致。
