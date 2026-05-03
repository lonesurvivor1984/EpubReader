## Why

用户可能有 TXT 格式的电子书资源，但阅读器只支持 EPUB 格式。添加 TXT 转 EPUB 功能可以让用户将 TXT 文件转换为 EPUB 后在阅读器中阅读。

## What Changes

- 在首页（书架）顶部工具栏添加"TXT格式转换"按钮
- 点击后弹出文件选择框，用户选择一个 TXT 文件
- 将 TXT 文件转换为标准 EPUB 格式（ZIP 容器 + XHTML 内容）
- 转换完成后弹出提示框，显示转换结果和 EPUB 文件保存位置
- 转换后的 EPUB 可直接添加到书架

## Capabilities

### New Capabilities

- `txt-to-epub-conversion`: TXT 文件转 EPUB 格式的转换功能，包括编码检测、段落分割、EPUB 打包
- `toolbar-txt-conversion`: 首页工具栏上的 TXT 转换入口（按钮 + 交互流程）

### Modified Capabilities

(none)

## Impact

- 新增 `app/core/txt_converter.py`: TXT 转 EPUB 核心逻辑
- `app/ui/main_window.py`: 首页工具栏添加按钮 + 转换交互
- PyInstaller 打包时需包含 `chardet` 库（用于编码检测）
