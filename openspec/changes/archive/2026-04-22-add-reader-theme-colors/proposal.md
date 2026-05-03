## Why

读者需要快速切换阅读背景色的功能，以提升不同光线环境下的阅读舒适度。当前阅读区仅使用固定的白色背景，缺少个性化的视觉调节选项。

## What Changes

- 在工具栏新增 4 个颜色按钮：浅黄、浅绿、浅蓝、浅灰
- 点击颜色按钮后，阅读区（WebView）背景色实时切换
- 颜色偏好持久化保存，下次打开时自动恢复

## Capabilities

### New Capabilities
- `reader-theme-colors`: 阅读区背景色切换能力，包括工具栏色块按钮、WebView 背景色注入、偏好持久化

### Modified Capabilities

## Impact

- `app/ui/settings.py`: 新增 4 个颜色按钮
- `app/ui/reader.py`: 新增背景色切换方法
- `app/ui/main_window.py`: 连接颜色按钮信号到阅读区
- `app/core/models.py`: UserPreferences 新增 theme_color 字段
- `app/config.py`: 默认颜色配置（可选）
