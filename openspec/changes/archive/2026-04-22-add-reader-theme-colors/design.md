## Context

阅读区使用 QtWebEngine (Chromium) 渲染 EPUB 内容，背景色由 HTML 自身决定，默认白色。当前通过 QWebEngineScript 在 DocumentCreation 阶段注入 CSS 控制排版样式。用户偏好（字体大小、目录可见性）已持久化在 JSON 中。

## Goals / Non-Goals

**Goals:**
- 提供 4 种浅色主题（浅黄、浅绿、浅蓝、浅灰）供用户一键切换阅读背景
- 背景色切换实时生效，无需重新加载章节
- 颜色偏好持久化，下次打开自动恢复
- 工具栏视觉简洁，色块小巧不喧宾夺主

**Non-Goals:**
- 不提供暗色模式（需要更复杂的样式适配，超出本需求范围）
- 不支持自定义颜色（固定 4 种预设）
- 不改变 EPUB 原始样式结构（仅覆盖 background-color）

## Decisions

### 1. 背景色注入方式：复用现有 `_apply_styles` 机制
**Decision:** 将背景色注入逻辑合并到 ReaderView 已有的 `_apply_styles` 方法中，与 font-size CSS 共用同一个 `<style id="epub-reader-theme">` 标签。

**Rationale:** 避免新增脚本注入路径，减少复杂度。font-size 和 background-color 都属于运行时样式覆盖，共享同一机制。

**Alternatives considered:**
- 独立的 `set_background_color` 方法 + 单独 script：增加维护成本，且两个 style 标签注入时机不同可能导致闪烁
- DocumentCreation 级脚本注入：不适合运行时动态切换

### 2. 颜色按钮实现：SettingsBar 中用 QLabel 做色块
**Decision:** 使用 QLabel 设置固定宽高和背景色样式表，绑定鼠标点击事件发出信号。

**Rationale:** QPushButton 自带边框和 hover 效果，不适合作为纯色块展示。QLabel 配合 `setStyleSheet("background-color: ...")` 更简洁。

**Alternatives considered:**
- QToolButton：仍需覆盖样式，不如 QLabel 直接
- 自定义 QWidget：过度设计

### 3. 颜色值选择
使用极浅色调，确保文字可读性：
- 浅黄: `#FFF9E6`（暖色调，护眼）
- 浅绿: `#E8F5E9`（Material Green 50）
- 浅蓝: `#E3F2FD`（Material Blue 50）
- 浅灰: `#F5F5F5`（Material Grey 50）

### 4. 偏好存储：UserPreferences 新增 `theme_color` 字段
存储颜色 hex 字符串（如 `"#FFF9E6"`），默认值为 `""`（表示白色/默认背景）。

## Risks / Trade-offs

- **[Risk]** 部分 EPUB 的内联样式可能设置 `background-color !important`，覆盖我们的注入样式。→ **Mitigation:** 注入样式同样使用 `!important`，且作用于 `html, body` 层级，大多数 EPUB 不会在 body 上设置背景色。
- **[Trade-off]** 固定 4 种颜色不可扩展。未来如需更多颜色，可将信号改为 `theme_selected(str)` 传递颜色值，但目前 YAGNI。
