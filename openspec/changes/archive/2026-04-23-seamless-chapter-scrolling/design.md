## Context

当前 ReaderView 一次只加载一个章节 URL（通过 `load_chapter()`），用户看完后必须通过目录手动跳转到下一章。EPUB 服务器的 URL 格式为 `http://127.0.0.1:{port}/{book_id}/{chapter_href}`。阅读区使用 QWebEngineScript 注入 CSS 和 JavaScript。

## Goals / Non-Goals

**Goals:**
- 滚到页面底部时自动加载下一章并追加到当前页面，保持连续阅读体验
- 章节间用分隔线和章节标题区分
- 通过目录/书签跳转时重置为单章模式

**Non-Goals:**
- 不实现预加载（提前加载下一章到内存）——改为按需加载，滚到底部时再请求
- 不实现"向上"加载上一章
- 不改变现有书签和阅读进度保存机制

## Decisions

### 1. 滚动检测：JavaScript 监听 scroll 事件 + runJavaScript 注入内容
**Decision:** 通过 QWebEngineScript 注入一段 JS 代码，监听 window scroll 事件，当 `scrollTop + clientHeight >= scrollHeight - 200` 时（距底部 200px），通过 `window.location.hash` 标记触发信号。Python 侧通过 `ReaderPage` 的 URL 变化或定期 `runJavaScript` 检测状态，然后从服务器 fetch 下一章内容并注入 DOM。

更直接方案：注入的 JS 在到达底部时，直接用 `fetch()` 从本地服务器获取下一章 HTML，提取 `<body>` 内容后追加到当前页面底部。Python 只需在打开书籍时把服务器 base URL 和章节列表注入到 JS 变量中。

**Rationale:** 纯 JS 方案避免了 Python/JS 之间的往返通信延迟，响应更即时。本地服务器没有跨域限制，`fetch` 可直接使用。Python 侧只需一次性注入配置（URL + 章节列表），后续全自动。

**Alternatives considered:**
- Python 侧 fetch + inject：需要通过 `runJavaScript` 来回传递数据，延迟高，且 scroll 检测本身也需要 JS
- QWebChannel：QtWebChannel 是 Qt 标准的 C++/JS 通信方式，但配置复杂，对于简单的"滚到底部加载下一章"场景过度设计

### 2. 注入方式：在 `loadFinished` 时注入完整逻辑
**Decision:** 章节加载完成后，通过 `_on_page_loaded` 钩子注入：
1. 章节列表（当前 href 及后续章节列表）
2. 服务器 base URL
3. 滚动检测 + 内容加载逻辑

每次 `load_chapter()` 调用（包括 TOC 跳转）都会重新注入，确保状态正确。

### 3. 章节分隔符
**Decision:** 在每章内容前插入一个 `<div class="chapter-divider">` 包含章节标题和分隔线样式。注入 JS 时创建这个 div，使用 CSS 居中显示。

### 4. 章节列表注入
**Decision:** 注入 JS 变量包含完整的章节 href 列表和当前索引。JS 侧跟踪 `currentIndex`，每次追加一章后递增。这样即使多次滚动到底部，也能依次加载后续章节。

## Risks / Trade-offs

- **[Risk]** 注入的 `fetch()` 可能与 EPUB 原有 JS 冲突（如某些 EPUB 有自己的滚动逻辑）。→ **Mitigation:** 使用 `addEventListener` 而非覆盖 `onscroll`，且只在主 world 注入。
- **[Risk]** 大量章节连续加载后 DOM 变大，可能影响 WebView 性能。→ **Mitigation:** 普通书籍章节数通常 < 200，每章 ~10KB HTML，内存可承受。如发现问题可后续实现"虚拟滚动"（移除已离开视口的章节 DOM）。
- **[Trade-off]** 纯 JS 方案中 Python 不知道当前加载到哪一章，书签可能只记录第一个加载的章节。→ **Mitigation:** 书签始终基于 `current_chapter_href`（即第一个加载的章节），阅读进度也保存第一个章节的位置，符合用户预期。
