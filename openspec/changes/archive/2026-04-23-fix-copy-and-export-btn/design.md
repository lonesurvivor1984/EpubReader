## Context

`_inject_note_editor` 中有一段 `mousedown` 监听器监听 document.body，任何点击都移除 action panel。但按钮的 click 事件在 mousedown 之后触发，此时 panel 已被移除，click 事件目标消失，复制功能永远不执行。

## Goals / Non-Goals

**Goals:**
- 修复复制按钮：点击面板按钮时不被 dismiss
- 修复导出笔记按钮：宽度足够显示文字

**Non-Goals:**
- 不改变选择面板的 UI/交互设计

## Decisions

### 选择面板关闭逻辑

**Decision**: 在 `mousedown` 处理函数中检查 `e.target.closest('.action-panel')`，如果点击在面板内部则不关闭。

**Rationale**: 最小改动，与现有 `note-editor` / `annotation-tooltip` 的守卫模式一致。

## Risks / Trade-offs

- 无。这是纯粹的 bug fix，无副作用。
