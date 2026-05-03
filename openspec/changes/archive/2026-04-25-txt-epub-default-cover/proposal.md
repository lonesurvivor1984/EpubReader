## Why

TXT 转 EPUB 生成的文件没有封面，书架显示为空白占位符。添加默认封面可以让转换后的 EPUB 在书架上更美观。

## What Changes

- 在 `app/core/txt_converter.py` 中生成 EPUB 时，嵌入一个默认封面图片（SVG 矢量图，以 TXT 文件名为封面文字）
- OPF manifest 中添加封面 image item，metadata 中标记 cover-image property

## Capabilities

### New Capabilities

- `txt-epub-cover`: TXT 转 EPUB 时生成默认封面图片

### Modified Capabilities

(none)

## Impact

- `app/core/txt_converter.py`: 新增封面 SVG 生成逻辑，OPF manifest 和 spine 中添加封面页
