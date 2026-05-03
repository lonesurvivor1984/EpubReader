## Context

书签的底层数据模型（`Bookmark`）、存储层（`storage.py`）、和业务逻辑（`BookManager.add_bookmark / remove_bookmark / get_bookmarks`）已经全部实现。缺失的纯 UI 层：没有按钮创建书签、没有列表展示书签、没有跳转交互。

当前 UI 架构：
- `SettingsBar`：顶部工具栏，包含 Back、A−/A+/Reset、TOC 按钮
- `TOCPanel`：左侧可折叠面板，展示目录树
- `ReaderView`：右侧 WebEngine 阅读器
- `MainWindow`：协调层，连接信号和处理逻辑

## Goals / Non-Goals

**Goals:**
- 用户在阅读页面能一键保存书签（当前章节 + 滚动位置）
- 书签列表能在阅读时查看，点击跳转
- 书签支持删除
- 书签列表复用 TOCPanel 的位置（左侧面板内嵌）或独立按钮弹出

**Non-Goals:**
- 书签备注功能暂不实现（`note` 字段留空）
- 书签不跨书共享
- 不实现书签导出/导入

## Decisions

1. **书签按钮放在 SettingsBar**：在 TOC 按钮旁边加一个 "Bookmarks" 按钮，点击后切换左侧面板从 TOC 视图到书签列表视图。这复用了已有的面板空间，不需要额外窗口。

2. **复用 TOCPanel 或新建 BookmarkPanel**：TOCPanel 是一个独立 `QWidget`，有 `QTreeView` 展示层级数据。书签是扁平列表，不需要树形结构。方案：创建一个简单的 `BookmarkPanel` 用 `QListWidget` 展示，与 TOCPanel 通过 `QStackedWidget` 切换。但这样改动较大。更简单的方案：直接在 `MainWindow` 的 reader 页面用 `QListWidget` 创建一个浮动的书签面板，通过书签按钮的 toggle 控制可见性。

3. **最终方案 — 在 TOCPanel 中集成书签模式**：TOCPanel 本身已有 `QTreeView` 和导航信号。改为用 `QStackedWidget` 包裹两个子组件（TOC 树 + 书签列表），通过按钮切换显示哪个。这样左侧面板既可以当目录用也可以当书签用。

   实际上更简洁的做法：`TOCPanel` 保持不变，`MainWindow` 新增一个独立的 `_bookmark_panel`（`QListWidget`），放在 `_splitter` 中与 TOCPanel 同一侧（或替代 TOCPanel）。但 splitter 目前只管理两个子组件（TOCPanel + ReaderView）。

   **最简实现**：在 TOCPanel 上增加一个"书签模式"切换。TOCPanel 内部用 `QStackedWidget` 包含 `QTreeView`（TOC）和 `QListWidget`（书签）。外部通过新的 `set_mode("toc" | "bookmark")` 方法切换。TOCPanel 的 `navigate_to` 信号在两种模式下都发出 href。

4. **创建书签的触发**：SettingsBar 加 "🔖" 或 "BM" 按钮，点击后 `MainWindow` 读取 `ReaderView` 当前章节 href + 滚动位置，调用 `BookManager.add_bookmark`。

5. **获取当前章节 href**：`ReaderView` 已有 `url_changed` 信号（URL 格式为 `http://127.0.0.1:{port}/{book_id}/{chapter_href}`）。`MainWindow` 可以在信号回调中解析出 `chapter_href` 并保存为 `_current_chapter_href`。书签创建时使用该值。

## Risks / Trade-offs

- [TOCPanel 修改可能影响现有 TOC 功能] → 最小化改动，仅添加 `QStackedWidget` 包装和切换方法，不修改现有树形渲染逻辑
- [URL 解析获取 chapter_href 依赖 URL 格式] → 当前 URL 格式稳定（`http://host:port/book_id/chapter_href`），用 `url.rsplit("/", 1)` 提取
- [书签列表项没有章节标题，只有 href] → 书签面板中从 EPUB 解析的章节名中匹配标题，找不到时显示 href
