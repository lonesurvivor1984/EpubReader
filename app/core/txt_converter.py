"""Convert TXT files to EPUB 3.0 format."""

from __future__ import annotations

import uuid
import zipfile
from pathlib import Path

from lxml import etree

CHAPTER_SIZE = 5000
NS_OPF = "http://www.idpf.org/2007/opf"
NS_CONTAINER = "urn:oasis:names:tc:opendocument:xmlns:container"
NS_XHTML = "http://www.w3.org/1999/xhtml"
NS_EPUB = "http://www.idpf.org/2007/ops"


def _detect_encoding(raw: bytes) -> str:
    """Detect text encoding, preferring chardet if available."""
    # Try chardet first
    try:
        import chardet
        result = chardet.detect(raw)
        if result and result["confidence"] > 0.5:
            enc = result["encoding"].lower()
            if enc in ("gb2312", "gbk", "gb18030", "utf-8", "utf-16"):
                return enc
    except ImportError:
        pass

    # Fallback: try common encodings
    for enc in ("utf-8-sig", "utf-8", "gbk", "gb2312", "gb18030", "big5"):
        try:
            raw.decode(enc)
            return enc
        except (UnicodeDecodeError, LookupError):
            continue
    return "utf-8"


def _split_chapters(text: str) -> list[str]:
    """Split text into chapters of ~CHAPTER_SIZE characters at blank lines."""
    if len(text) <= CHAPTER_SIZE:
        return [text.strip()] if text.strip() else []

    chapters = []
    lines = text.split("\n")
    current = []
    current_len = 0

    for line in lines:
        stripped = line.strip()
        current.append(line)
        current_len += len(stripped)

        if current_len >= CHAPTER_SIZE and stripped == "":
            chapters.append("\n".join(current).strip())
            current = []
            current_len = 0

    # Remaining content
    remaining = "\n".join(current).strip()
    if remaining:
        if chapters and len(remaining) < 500:
            # Append small remainder to last chapter
            chapters[-1] += "\n\n" + remaining
        else:
            chapters.append(remaining)

    return chapters


def _build_mimetype() -> bytes:
    return b"application/epub+zip"


def _build_container() -> bytes:
    root = etree.Element(
        f"{{{NS_CONTAINER}}}container",
        version="1.0",
    )
    rootfiles = etree.SubElement(root, f"{{{NS_CONTAINER}}}rootfiles")
    etree.SubElement(
        rootfiles,
        f"{{{NS_CONTAINER}}}rootfile",
        {
            "full-path": "EPUB/package.opf",
            "media-type": "application/oebps-package+xml",
        },
    )
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8")


def _build_cover_image(title: str) -> tuple[str, bytes]:
    """Generate a cover image (PNG) with title text on a gradient background.

    Returns (filename, png_bytes).
    """
    import os
    # Must set before creating any Qt GUI objects
    if not os.environ.get('QT_QPA_PLATFORM'):
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'

    from PySide6.QtCore import Qt, QRect, QLine, QBuffer, QIODevice
    from PySide6.QtGui import (
        QColor, QImage, QPainter, QLinearGradient,
        QFont, QPainterPath,
    )

    W, H = 400, 600

    # Sanitize and truncate title
    safe_title = title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    if len(safe_title) > 30:
        safe_title = safe_title[:27] + "..."

    img = QImage(W, H, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(QColor(0, 0, 0, 0))

    painter = QPainter(img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

    # Gradient background
    grad = QLinearGradient(0, 0, W, H)
    grad.setColorAt(0.0, QColor("#667eea"))
    grad.setColorAt(1.0, QColor("#764ba2"))
    painter.fillRect(0, 0, W, H, grad)

    # Decorative inner border
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(255, 255, 255, 20))
    path = QPainterPath()
    path.addRoundedRect(QRect(30, 40, W - 60, H - 80), 8, 8)
    painter.drawPath(path)

    # Decorative line
    painter.setPen(QColor(255, 255, 255, 76))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawLine(QLine(150, 295, 250, 295))

    # Title text
    font = QFont()
    font.setFamily("sans-serif")
    font.setPixelSize(24)
    font.setBold(True)
    painter.setFont(font)
    painter.setPen(Qt.GlobalColor.white)
    painter.drawText(QRect(40, 220, W - 80, 100),
                     Qt.AlignmentFlag.AlignCenter, safe_title)

    # Subtitle
    font.setPixelSize(12)
    font.setBold(False)
    painter.setFont(font)
    painter.setPen(QColor(255, 255, 255, 153))
    painter.drawText(QRect(40, 320, W - 80, 30),
                     Qt.AlignmentFlag.AlignCenter, "EpubReader")

    painter.end()

    # Save as PNG into buffer
    buf = QBuffer()
    buf.open(QIODevice.OpenModeFlag.WriteOnly)
    img.save(buf, "PNG")
    return "cover.png", bytes(buf.data())


def _build_opf(chapter_count: int, title: str) -> tuple[str, bytes]:
    uid = str(uuid.uuid4())

    package = etree.Element(
        f"{{{NS_OPF}}}package",
        version="3.0",
        nsmap={None: NS_OPF, "epub": NS_EPUB},
        unique_identifier="uid",
    )

    # Metadata
    metadata = etree.SubElement(package, f"{{{NS_OPF}}}metadata")
    etree.SubElement(metadata, f"{{{NS_OPF}}}identifier", id="uid").text = f"urn:uuid:{uid}"
    etree.SubElement(metadata, f"{{{NS_OPF}}}title").text = title
    etree.SubElement(metadata, f"{{{NS_OPF}}}language").text = "zh"
    etree.SubElement(
        metadata,
        f"{{{NS_OPF}}}meta",
        {"property": "dcterms:modified"},
    ).text = "2026-01-01T00:00:00Z"

    # Manifest
    manifest = etree.SubElement(package, f"{{{NS_OPF}}}manifest")
    etree.SubElement(
        manifest,
        f"{{{NS_OPF}}}item",
        {
            "id": "cover",
            "href": "cover.png",
            "media-type": "image/png",
            "properties": "cover-image",
        },
    )
    etree.SubElement(
        manifest,
        f"{{{NS_OPF}}}item",
        {
            "id": "nav",
            "href": "nav.xhtml",
            "media-type": "application/xhtml+xml",
            "properties": "nav",
        },
    )
    for i in range(1, chapter_count + 1):
        etree.SubElement(
            manifest,
            f"{{{NS_OPF}}}item",
            {
                "id": f"chapter-{i}",
                "href": f"chapter-{i}.xhtml",
                "media-type": "application/xhtml+xml",
            },
        )

    # Spine
    spine = etree.SubElement(package, f"{{{NS_OPF}}}spine")
    etree.SubElement(spine, f"{{{NS_OPF}}}itemref", {"idref": "cover"})
    etree.SubElement(spine, f"{{{NS_OPF}}}itemref", {"idref": "nav"})
    for i in range(1, chapter_count + 1):
        etree.SubElement(spine, f"{{{NS_OPF}}}itemref", {"idref": f"chapter-{i}"})

    opf_path = "EPUB/package.opf"
    return opf_path, etree.tostring(
        package, xml_declaration=True, encoding="UTF-8"
    )


def _build_nav_xhtml(title: str, chapter_count: int) -> bytes:
    html = etree.Element(f"{{{NS_XHTML}}}html")
    html.set("lang", "zh")

    head = etree.SubElement(html, f"{{{NS_XHTML}}}head")
    etree.SubElement(head, f"{{{NS_XHTML}}}title").text = title
    etree.SubElement(head, f"{{{NS_XHTML}}}meta", {"charset": "utf-8"})

    body = etree.SubElement(html, f"{{{NS_XHTML}}}body")
    nav = etree.SubElement(
        body, f"{{{NS_XHTML}}}nav", {f"{{{NS_EPUB}}}type": "toc"}
    )
    etree.SubElement(nav, f"{{{NS_XHTML}}}h1").text = "目录"
    ol = etree.SubElement(nav, f"{{{NS_XHTML}}}ol")
    for i in range(1, chapter_count + 1):
        li = etree.SubElement(ol, f"{{{NS_XHTML}}}li")
        etree.SubElement(
            li,
            f"{{{NS_XHTML}}}a",
            {"href": f"chapter-{i}.xhtml"},
        ).text = f"第{i}章"

    return etree.tostring(html, xml_declaration=True, encoding="UTF-8", method="html")


def _build_chapter_xhtml(text: str, chapter_num: int) -> bytes:
    html = etree.Element(f"{{{NS_XHTML}}}html")
    html.set("lang", "zh")

    head = etree.SubElement(html, f"{{{NS_XHTML}}}head")
    etree.SubElement(head, f"{{{NS_XHTML}}}meta", {"charset": "utf-8"})

    body = etree.SubElement(html, f"{{{NS_XHTML}}}body")
    etree.SubElement(body, f"{{{NS_XHTML}}}h2").text = f"第{chapter_num}章"

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    for para_text in paragraphs:
        p_elem = etree.SubElement(body, f"{{{NS_XHTML}}}p")
        lines = [l for l in para_text.split("\n") if l.strip()]
        if lines:
            p_elem.text = lines[0].strip()
            for line in lines[1:]:
                br = etree.SubElement(p_elem, f"{{{NS_XHTML}}}br")
                br.tail = line.strip()

    return etree.tostring(html, xml_declaration=True, encoding="UTF-8", method="html")


def convert_txt_to_epub(txt_path: str, output_dir: str = "") -> str:
    """Convert a TXT file to EPUB 3.0 format.

    Returns the path to the generated EPUB file.
    """
    txt_path = Path(txt_path)
    if not txt_path.exists():
        raise FileNotFoundError(f"TXT file not found: {txt_path}")

    # Read and decode
    raw = txt_path.read_bytes()
    encoding = _detect_encoding(raw)
    text = raw.decode(encoding)

    if not text.strip():
        raise ValueError("TXT file is empty or contains only whitespace")

    # Split into chapters
    chapters = _split_chapters(text)
    if not chapters:
        raise ValueError("No content found in TXT file")

    # Output path
    output_dir = Path(output_dir) if output_dir else txt_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    base_name = txt_path.stem
    out_path = output_dir / f"{base_name}.epub"
    # Handle duplicates
    counter = 1
    while out_path.exists():
        out_path = output_dir / f"{base_name}_{counter}.epub"
        counter += 1

    # Build EPUB
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # mimetype must be first and uncompressed
        zf.writestr("mimetype", _build_mimetype(), compress_type=zipfile.ZIP_STORED)
        zf.writestr("META-INF/container.xml", _build_container())

        cover_name, cover_data = _build_cover_image(txt_path.stem)
        opf_path, opf_data = _build_opf(len(chapters), txt_path.stem)
        zf.writestr(f"EPUB/{cover_name}", cover_data)
        zf.writestr(opf_path, opf_data)
        zf.writestr("EPUB/nav.xhtml", _build_nav_xhtml(txt_path.stem, len(chapters)))

        for i, chapter_text in enumerate(chapters, 1):
            zf.writestr(
                f"EPUB/chapter-{i}.xhtml",
                _build_chapter_xhtml(chapter_text, i),
            )

    return str(out_path)
