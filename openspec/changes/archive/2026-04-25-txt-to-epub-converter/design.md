## Context

EPUB 是 ZIP 格式的容器，包含 mimetype、META-INF/container.xml、OPF 包描述文件和 XHTML 内容。标准库 `zipfile` 可以直接用于创建，`lxml` 用于生成 XML。编码检测使用 `chardet` 库。

## Goals / Non-Goals

**Goals:**
- 在书架首页添加"TXT格式转换"按钮
- 将 TXT 文件转换为标准 EPUB 3.0 格式
- 支持 UTF-8 和 GBK 编码自动检测

**Non-Goals:**
- 不处理富文本 TXT（如 Markdown、HTML）
- 不做复杂的排版定制（字体、页边距等使用默认值）
- 转换后的 EPUB 不会自动添加到书架（需用户手动添加）

## Decisions

### EPUB 生成方式

**Decision**: 使用标准库 `zipfile` + `lxml` 手动构建 EPUB 3.0 容器。

**Rationale**: 无需额外依赖（如 ebooklib），项目已有 lxml 可用。EPUB 3.0 结构简单：ZIP 容器 + 固定文件结构。

### 编码检测

**Decision**: 使用 `chardet` 库进行编码检测，如果未安装则回退到 UTF-8/GBK 依次尝试。

**Rationale**: `chardet` 对中文 GBK 编码支持良好。作为可选依赖，未安装时仍可工作。

### 章节分割

**Decision**: 按约 5000 字符分割，优先在空行处切分，不切断段落。

**Rationale**: 5000 字符约等于 EPUB 阅读器中 2-3 屏的内容，适合移动端阅读。空行处切分保证章节完整性。

### 输出位置

**Decision**: 保存到 `DATA_DIR/converted/` 目录下，以原文件名 `.txt` 替换为 `.epub`。

**Rationale**: 与应用其他数据文件统一管理，用户容易找到输出文件。

## Risks / Trade-offs

- **chardet 依赖**: 如果打包时未包含 `chardet`，回退逻辑可能无法正确检测 GBK 编码。 mitigation: PyInstaller spec 中加入 `chardet`。
- **大文件性能**: 超大 TXT 文件（>50MB）转换时可能较慢。 mitigation: 当前实现足够处理常见小说大小（1-10MB）。
