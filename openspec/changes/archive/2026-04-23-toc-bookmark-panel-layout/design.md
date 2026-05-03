## Context

当前左侧面板使用 QStackedWidget 存放 TOCPanel 和 BookmarkPanel，通过 `_showing_bookmarks` 标志切换显示。目录按钮触发 `_on_toc_toggle` 控制左侧面板整体可见性，书签按钮在 TOC 和 Bookmark 面板之间切换。

## Goals / Non-Goals

**Goals:**
- 目录和书签同时可见，上下布局
- 目录占 80% 高度，书签占 20% 高度
- 书签按钮控制书签区域的展开/收起（默认展开）
- 目录按钮保持现有行为（控制整个左侧面板可见性）

**Non-Goals:**
- 不做可拖拽调整大小的分割条（过于复杂）
- 不改变书签的添加/删除/导航功能

## Decisions

### 1. 布局方案：QVBoxLayout + 固定高度比例
**Decision:** 用 QVBoxLayout 替换左侧的 QStackedWidget，将 TOCPanel 和 BookmarkPanel 直接添加到 layout 中。通过设置 TOCPanel 和 BookmarkPanel 的 `setMaximumHeight` 和 `setMinimumHeight` 控制比例。

更优雅方案：使用 QSplitter（垂直方向），设置初始比例为 80:20。用户可自行微调。

**Rationale:** QSplitter 是 Qt 标准做法，支持用户后续调整比例，且初始比例可通过 `setSizes` 设置。

## Risks / Trade-offs

- **[Risk]** 书签区域初始 20% 高度可能太小，内容显示不全。→ **Mitigation:** 书签使用 QListWidget，可滚动。20% 只是初始值，用户可通过拖拽分割条调整。
