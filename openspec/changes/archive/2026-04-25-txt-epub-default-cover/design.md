## Context

当前 TXT 转 EPUB 不生成封面，书架视图显示空白。EPUB 3.0 支持 SVG 封面图片，通过 OPF manifest 中标记 `properties="cover-image"` 即可。

## Goals / Non-Goals

**Goals:**
- 为 TXT 转 EPUB 添加 SVG 默认封面
- 封面上显示文件名作为标题

**Non-Goals:**
- 不支持自定义封面图片

## Decisions

### 封面实现方式

**Decision**: 使用 SVG 矢量图作为封面，内联生成（不依赖外部图片文件）。

**Rationale**: SVG 是纯文本格式，可直接在代码中模板化生成，无需额外资源文件。SVG 支持文字居中、渐变背景、圆角等效果，视觉效果良好。

### OPF 配置

**Decision**: 在 manifest 中添加 `cover.svg` item 并标记 `properties="cover-image"`，不单独创建 cover-page XHTML（可选，非必需）。

## Risks / Trade-offs

- SVG 封面在某些老旧 EPUB 阅读器可能不被支持，但主流阅读器（包括本应用的 QtWebEngine）支持良好。
