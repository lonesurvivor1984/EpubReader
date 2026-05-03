## Why

当前阅读模式下，每看完一章都必须回到目录手动点击下一章，阅读流程被频繁打断。用户希望获得类似纸质书的连续阅读体验——滚到章节末尾时自动加载下一章内容，无需额外操作。

## What Changes

- 阅读区滚动到末尾时自动检测并加载下一章内容，追加到当前页面底部
- 章节之间显示分隔线和章节标题，区分不同章节
- 通过目录/书签跳转时重置为单章视图（预加载模式关闭）
- 预加载的下一章内容在后台静默获取，不影响当前滚动体验
- 阅读进度保存仍基于第一个加载章节的 href 和滚动偏移

## Capabilities

### New Capabilities
- `seamless-chapter-scroll`: 滚动到底部自动加载下一章的能力，包括滚动检测、内容获取、DOM 追加、章节列表管理

### Modified Capabilities

## Impact

- `app/ui/reader.py`: 新增章节列表跟踪、滚动检测脚本、DOM 追加注入逻辑
- `app/ui/main_window.py`: 打开书籍时传递章节列表到 ReaderView
