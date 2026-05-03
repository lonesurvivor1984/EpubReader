# Tasks — Bookmark Support

## 1. SettingsBar — 添加书签按钮

- [x] 1.1 在 `app/ui/settings.py` 的 SettingsBar 中添加 "BM" 按钮和 `bookmark_add` 信号
- [x] 1.2 在 `app/ui/main_window.py` 中连接 `bookmark_add` 信号到 `_on_bookmark_add` 处理函数

## 2. ReaderView — 当前章节追踪

- [x] 2.1 在 `ReaderView` 中添加 `_current_url` 属性，`url_changed` 信号回调中更新该值
- [x] 2.2 在 `MainWindow` 的 `_on_toc_navigate`（已有 URL 回调）或新增回调中提取并保存 `_current_chapter_href`

## 3. BookmarkPanel — 书签列表面板

- [x] 3.1 创建 `app/ui/bookmark_panel.py`，包含 `QListWidget` 展示书签列表
- [x] 3.2 支持书签条目显示：章节标题 + 创建时间
- [x] 3.3 支持右键上下文菜单删除书签（`remove_bookmark` 信号）
- [x] 3.4 空列表时显示占位提示

## 4. MainWindow — 书签集成

- [x] 4.1 在 MainWindow 中实例化 BookmarkPanel，放在 reader 页面中与 TOCPanel 同层（通过 QStackedWidget 切换）
- [x] 4.2 实现 `_on_bookmark_add`：读取当前章节 href + 滚动位置，调用 `BookManager.add_bookmark`
- [x] 4.3 实现书签面板切换：SettingsBar 的 BM 按钮切换 TOC 和 Bookmark 面板的可见性
- [x] 4.4 打开书籍时加载并显示已有书签
- [x] 4.5 实现书签点击跳转：连接 BookmarkPanel 的导航信号到 `_on_bookmark_navigate`

## 5. 验证

- [ ] 5.1 运行应用，打开一本书，创建书签，返回书架再打开，验证书签存在且可跳转
- [ ] 5.2 验证删除书签后列表即时更新
- [ ] 5.3 验证无书时无报错
