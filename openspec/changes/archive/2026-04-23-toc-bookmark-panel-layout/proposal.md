## Why

当前目录和书签面板使用 QStackedWidget 互斥显示（切换模式），用户需要频繁切换才能同时查看目录和书签。将两者同时展示在左侧，目录为主（80%）、书签为辅（20%），可提升阅读导航效率。

## What Changes

- 将左侧面板从 QStackedWidget（互斥显示）改为 QVBoxLayout（上下布局）
- TOCPanel 占 80% 高度，BookmarkPanel 占 20% 高度
- 书签按钮点击时，展开/收起书签区域（默认展开）
- 目录按钮切换左侧面板整体可见性（保持现有行为）

## Capabilities

### New Capabilities
- `panel-split-layout`: 左侧面板上下分割布局能力，TOC 占 80%、书签占 20%

### Modified Capabilities

## Impact

- `app/ui/main_window.py`: 将 QStackedWidget 替换为 QVBoxLayout + 分割布局
- `app/ui/settings.py`: 书签按钮行为从"切换面板"改为"展开/收起书签区域"
