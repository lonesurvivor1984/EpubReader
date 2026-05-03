"""EPUB parser — extracts metadata, chapters, TOC, and resources from EPUB files.

Handles both prefixed and default-namespace OPF files (EPUB 2 & 3).
"""

from __future__ import annotations

import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

from lxml import etree

from app.core.models import Chapter, TOCItem


# ── Exceptions ────────────────────────────────────────────────────────────────

class EpubError(Exception):
    """Base exception for EPUB-related errors."""


class InvalidEpubError(EpubError):
    """Raised when a file is not a valid EPUB."""


# ── Constants ─────────────────────────────────────────────────────────────────

CONTAINER_PATH = "META-INF/container.xml"

NS_OPF = "http://www.idpf.org/2007/opf"
NS_DC = "http://purl.org/dc/elements/1.1/"
NS_XHTML = "http://www.w3.org/1999/xhtml"
NS_NCX = "http://www.daisy.org/z3986/2005/ncx/"


def _clark_opf(tag: str) -> str:
    return f"{{{NS_OPF}}}{tag}"


def _clark_dc(tag: str) -> str:
    return f"{{{NS_DC}}}{tag}"


MIME_MAP: dict[str, str] = {
    ".html": "text/html",
    ".htm": "text/html",
    ".xhtml": "application/xhtml+xml",
    ".css": "text/css",
    ".js": "application/javascript",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    ".webp": "image/webp",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
    ".ttf": "font/ttf",
    ".otf": "font/otf",
    ".eot": "application/vnd.ms-fontobject",
    ".xml": "application/xml",
    ".ncx": "application/x-dtbncx+xml",
    ".opf": "application/oebps-package+xml",
}


# ── Parser ────────────────────────────────────────────────────────────────────

@dataclass
class ParsedEpub:
    """Complete parsed EPUB data."""
    title: str
    author: str
    language: str
    opf_base: str  # e.g. "OEBPS/" — base dir for resolving resource paths
    cover_image_id: str | None = None
    chapters: list[Chapter] = field(default_factory=list)
    toc: list[TOCItem] = field(default_factory=list)
    resources: dict[str, str] = field(default_factory=dict)
    merged_chapters: dict[str, bytes] = field(default_factory=dict)  # href -> merged HTML


def parse_epub(file_path: str | Path) -> ParsedEpub:
    """Parse an EPUB file and return structured data."""
    file_path = Path(file_path)
    if not file_path.exists():
        raise InvalidEpubError(f"File not found: {file_path}")

    try:
        zf = zipfile.ZipFile(file_path)
    except zipfile.BadZipFile:
        raise InvalidEpubError(f"Not a valid ZIP file: {file_path}")

    try:
        mt = zf.read("mimetype").decode("utf-8").strip()
        if mt != "application/epub+zip":
            _warn(f"Unexpected mimetype: {mt}")
    except KeyError:
        _warn("Missing mimetype file")

    opf_path = _read_container(zf)
    opf_dir = str(Path(opf_path).parent) if "/" in opf_path else ""
    opf_root = _parse_xml(zf, opf_path)

    title, author, language, cover_id = _extract_metadata(opf_root)
    resources = _extract_manifest(opf_root)
    chapters = _extract_spine(opf_root, resources)
    toc = _extract_toc(zf, opf_root, opf_dir)

    # Merge consecutive short chapter files into larger reading units
    chapters, toc, merged_chapters = _merge_short_chapters(
        zf, chapters, toc, opf_dir, opf_root, resources,
    )

    if not title:
        title = file_path.stem

    return ParsedEpub(
        title=title,
        author=author or "Unknown",
        language=language or "en",
        opf_base=opf_dir + "/" if opf_dir else "",
        cover_image_id=cover_id,
        chapters=chapters,
        toc=toc,
        resources=resources,
        merged_chapters=merged_chapters,
    )


def get_resource(zf: zipfile.ZipFile, resource_path: str) -> tuple[bytes, str]:
    """Extract a single resource from the EPUB ZIP."""
    try:
        data = zf.read(resource_path)
    except KeyError:
        raise EpubError(f"Resource not found in EPUB: {resource_path}")

    suffix = Path(resource_path).suffix.lower()
    mime = MIME_MAP.get(suffix, "application/octet-stream")
    return data, mime


# ── Internal helpers ──────────────────────────────────────────────────────────

def _warn(msg: str) -> None:
    print(f"[EPUB Parser] Warning: {msg}")


def _read_container(zf: zipfile.ZipFile) -> str:
    """Read container.xml and return the path to the .opf file."""
    try:
        raw = zf.read(CONTAINER_PATH)
    except KeyError:
        raise InvalidEpubError("Missing META-INF/container.xml")

    root = etree.fromstring(raw)
    # Try with namespace first, then without
    ns = {"ocf": "urn:oasis:names:tc:opendocument:xmlns:container"}
    rootfile = root.find(".//ocf:rootfile", ns)
    if rootfile is None:
        rootfile = root.find(".//rootfile")
    if rootfile is None:
        raise InvalidEpubError("No <rootfile> element in container.xml")

    opf_path = rootfile.get("full-path")
    if not opf_path:
        raise InvalidEpubError("<rootfile> missing full-path attribute")

    return opf_path


def _parse_xml(zf: zipfile.ZipFile, path: str) -> etree._Element:
    """Parse an XML file from the ZIP."""
    try:
        raw = zf.read(path)
    except KeyError:
        raise InvalidEpubError(f"Missing file in EPUB: {path}")
    try:
        return etree.fromstring(raw)
    except etree.XMLSyntaxError as e:
        raise InvalidEpubError(f"Malformed XML in {path}: {e}")


def _opf(tag: str) -> str:
    """Clark notation for OPF namespace elements."""
    return f"{{{NS_OPF}}}{tag}"


def _dc(tag: str) -> str:
    """Clark notation for Dublin Core namespace elements."""
    return f"{{{NS_DC}}}{tag}"


def _extract_metadata(opf_root: etree._Element) -> tuple[str, str, str, str | None]:
    """Extract title, author, language, cover_image_id from .opf metadata."""
    # OPF elements: package, metadata are in OPF namespace
    metadata = opf_root.find(_opf("metadata"))
    if metadata is None:
        return "", "", "", None

    # DC elements: title, creator, language are in DC namespace
    title_el = metadata.find(_dc("title"))
    title = title_el.text.strip() if title_el is not None and title_el.text else ""

    creators = metadata.findall(_dc("creator"))
    author = ""
    if creators:
        names = [c.text.strip() for c in creators if c.text and c.text.strip()]
        author = ", ".join(names)

    lang_el = metadata.find(_dc("language"))
    language = lang_el.text.strip() if lang_el is not None and lang_el.text else ""

    cover_id = _find_cover_id(opf_root)

    return title, author, language, cover_id


def _find_cover_id(opf_root: etree._Element) -> str | None:
    """Find the cover image ID from OPF.

    Supports both EPUB 2 (<meta name="cover" content="..."/>) and
    EPUB 3.0 (manifest item with properties="cover-image").
    """
    metadata = opf_root.find(_opf("metadata"))
    if metadata is not None:
        for meta in metadata.findall(_opf("meta")):
            if meta.get("name") == "cover":
                return meta.get("content")

    # EPUB 3.0: look for manifest item with properties="cover-image"
    manifest = opf_root.find(_opf("manifest"))
    if manifest is not None:
        for item in manifest.findall(_opf("item")):
            if item.get("properties") == "cover-image":
                return item.get("id")
    return None


def _extract_manifest(opf_root: etree._Element) -> dict[str, str]:
    """Build manifest: relative_path -> mime_type."""
    manifest = opf_root.find(_opf("manifest"))
    if manifest is None:
        return {}

    resources: dict[str, str] = {}
    for item in manifest.findall(_opf("item")):
        href = item.get("href", "")
        media_type = item.get("media-type", "")
        if href:
            resources[href] = media_type

    return resources


def _extract_spine(opf_root: etree._Element, resources: dict[str, str]) -> list[Chapter]:
    """Extract chapter list from spine in reading order."""
    spine = opf_root.find(_opf("spine"))
    if spine is None:
        _warn("No <spine> element found")
        return []

    # Build idref -> (href, title) map from manifest
    manifest_items: dict[str, tuple[str, str]] = {}
    manifest = opf_root.find(_opf("manifest"))
    if manifest is not None:
        for item in manifest.findall(_opf("item")):
            item_id = item.get("id")
            href = item.get("href", "")
            title = item.get("title", "")
            if item_id:
                manifest_items[item_id] = (href, title)

    chapters: list[Chapter] = []
    for itemref in spine.findall(_opf("itemref")):
        idref = itemref.get("idref")
        if idref and idref in manifest_items:
            href, title = manifest_items[idref]
            chapters.append(Chapter(id=idref, href=href, title=title))
        elif idref:
            _warn(f"Spine item '{idref}' not in manifest, skipping")

    if not chapters:
        _warn("No chapters found in spine")

    return chapters


def _extract_toc(
    zf: zipfile.ZipFile,
    opf_root: etree._Element,
    opf_dir: str,
) -> list[TOCItem]:
    """Extract TOC — prefer EPUB3 nav.xhtml, fallback to EPUB2 toc.ncx."""
    # Try EPUB3 nav.xhtml: look for item with properties="nav"
    for item in opf_root.findall(f".//{_opf('item')}"):
        props = item.get("properties", "")
        if "nav" in props:
            nav_href = item.get("href")
            if nav_href:
                nav_path = _resolve_path(opf_dir, nav_href)
                toc = _parse_nav_xhtml(zf, nav_path)
                if toc:
                    return toc

    # Fallback: EPUB2 toc.ncx
    for item in opf_root.findall(f".//{_opf('item')}"):
        media_type = item.get("media-type", "")
        href = item.get("href", "")
        if "ncx" in media_type or href.endswith(".ncx"):
            ncx_path = _resolve_path(opf_dir, href)
            toc = _parse_ncx(zf, ncx_path)
            if toc:
                return toc

    _warn("No TOC found (no nav.xhtml or toc.ncx)")
    return []


def _resolve_path(opf_dir: str, href: str) -> str:
    """Resolve a relative path within the EPUB."""
    if opf_dir:
        return f"{opf_dir}/{href}".lstrip("/")
    return href


def _parse_nav_xhtml(zf: zipfile.ZipFile, path: str) -> list[TOCItem] | None:
    """Parse EPUB3 navigation document (nav.xhtml)."""
    try:
        raw = zf.read(path)
    except KeyError:
        return None

    try:
        root = etree.fromstring(raw)
    except etree.XMLSyntaxError:
        return None

    ns = {"xhtml": NS_XHTML}
    nav = root.find(".//xhtml:nav", ns) or root.find(f".//{{{NS_XHTML}}}nav")
    if nav is None:
        return None

    ol = nav.find("xhtml:ol", ns) or nav.find(f"{{{NS_XHTML}}}ol")
    if ol is None:
        return None

    return _parse_nav_ol(ol)


def _parse_nav_ol(ol_el: etree._Element) -> list[TOCItem]:
    """Recursively parse <ol> elements into TOCItem list."""
    items: list[TOCItem] = []

    for li in ol_el:
        tag = li.tag
        is_li = tag == f"{{{NS_XHTML}}}li" or tag == "li"
        if not is_li:
            continue

        label = ""
        href = ""
        for child in li:
            child_tag = child.tag
            if child_tag in (f"{{{NS_XHTML}}}a", "a"):
                href = child.get("href", "")
                label = (child.text or "").strip()
            elif child_tag in (f"{{{NS_XHTML}}}span", "span"):
                label = (child.text or "").strip()

        if not label:
            label = (li.text or "").strip()

        children: list[TOCItem] = []
        for sub_child in li:
            sub_tag = sub_child.tag
            if sub_tag in (f"{{{NS_XHTML}}}ol", "ol"):
                children = _parse_nav_ol(sub_child)
                break

        if label or href:
            items.append(TOCItem(label=label, href=href, children=children))

    return items


def _parse_ncx(zf: zipfile.ZipFile, path: str) -> list[TOCItem] | None:
    """Parse EPUB2 NCX table of contents."""
    try:
        raw = zf.read(path)
    except KeyError:
        return None

    try:
        root = etree.fromstring(raw)
    except etree.XMLSyntaxError:
        return None

    ns = {"ncx": NS_NCX}
    nav_map = root.find(".//ncx:navMap", ns)
    if nav_map is None:
        return None

    return _parse_ncx_nav_map(nav_map)


def _parse_ncx_nav_map(nav_map: etree._Element) -> list[TOCItem]:
    """Recursively parse NCX navMap."""
    items: list[TOCItem] = []

    for nav_point in nav_map:
        tag = nav_point.tag
        if tag not in (f"{{{NS_NCX}}}navPoint", "navPoint"):
            continue

        label_el = nav_point.find(f"{{{NS_NCX}}}navLabel")
        content_el = nav_point.find(f"{{{NS_NCX}}}content")

        label = ""
        href = ""
        if label_el is not None:
            text_el = label_el.find(f"{{{NS_NCX}}}text")
            if text_el is not None and text_el.text:
                label = text_el.text.strip()
        if content_el is not None:
            href = content_el.get("src", "")

        # Recurse into nested navPoints
        children: list[TOCItem] = []
        for sub in nav_point:
            sub_tag = sub.tag
            if sub_tag in (f"{{{NS_NCX}}}navPoint", "navPoint"):
                children = _parse_ncx_nav_map(sub)
                break

        if label or href:
            items.append(TOCItem(label=label, href=href, children=children))

    return items


# ── Chapter merging ───────────────────────────────────────────────────────────

_MERGE_THRESHOLD = 500  # text chars; chapters below this are "short"


def _measure_text(data: bytes) -> int:
    """Count non-tag text characters in HTML."""
    text = re.sub(r'<[^>]+>', '', data.decode('utf-8', errors='replace'))
    return len(text.strip())


def _merge_short_chapters(
    zf: zipfile.ZipFile,
    chapters: list[Chapter],
    toc: list[TOCItem],
    opf_dir: str,
    opf_root: etree._Element,
    resources: dict[str, str],
) -> tuple[list[Chapter], list[TOCItem], dict[str, bytes]]:
    """Merge consecutive short chapter files into larger reading units."""
    if not chapters:
        return chapters, toc, {}

    opf_base = opf_dir + "/" if opf_dir else ""
    sizes: list[int] = []
    for ch in chapters:
        try:
            full_path = f"{opf_base}{ch.href}" if opf_base else ch.href
            data = zf.read(full_path)
            sizes.append(_measure_text(data))
        except KeyError:
            sizes.append(0)

    # Build groups: long chapters start new groups, short ones merge
    groups: list[list[int]] = []
    current: list[int] = []
    for i, sz in enumerate(sizes):
        if not current:
            current.append(i)
        elif sz >= _MERGE_THRESHOLD:
            groups.append(current)
            current = [i]
        else:
            current.append(i)
    if current:
        groups.append(current)

    # If all chapters are short, don't merge
    all_short = all(sz < _MERGE_THRESHOLD for sz in sizes)
    if all_short and len(groups) == 1 and len(groups[0]) == len(chapters):
        return chapters, toc, {}

    # Build merged content
    merged_chapters: list[Chapter] = []
    merged_html: dict[str, bytes] = {}

    for group in groups:
        first = group[0]
        first_ch = chapters[first]

        if len(group) == 1:
            merged_chapters.append(first_ch)
            continue

        parts: list[str] = []
        for idx in group:
            full_path = f"{opf_base}{chapters[idx].href}" if opf_base else chapters[idx].href
            try:
                html = zf.read(full_path).decode('utf-8', errors='replace')
            except KeyError:
                continue
            body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)
            if body_match:
                parts.append(body_match.group(1).strip())

        if not parts:
            merged_chapters.append(first_ch)
            continue

        merged_body = '\n'.join(parts)
        first_path = f"{opf_base}{first_ch.href}" if opf_base else first_ch.href
        try:
            first_html = zf.read(first_path).decode('utf-8', errors='replace')
        except KeyError:
            merged_chapters.append(first_ch)
            continue

        merged_full = re.sub(
            r'<body[^>]*>.*?</body>',
            lambda m: f'<body>\n{merged_body}\n</body>',
            first_html, flags=re.DOTALL,
        )

        merged_chapters.append(Chapter(id=first_ch.id, href=first_ch.href, title=first_ch.title))
        merged_html[first_ch.href] = merged_full.encode('utf-8')
        # _warn(f"Merged {len(group)} files into '{first_ch.href}' ({sum(sizes[i] for i in group)} chars)")

    # Rebuild TOC
    new_toc = _rebuild_toc(groups, chapters, toc)

    return merged_chapters, new_toc, merged_html


def _rebuild_toc(
    groups: list[list[int]],
    chapters: list[Chapter],
    original_toc: list[TOCItem],
) -> list[TOCItem]:
    """Rebuild TOC to reflect merged chapter structure."""
    toc_labels: dict[str, str] = {}
    toc_children: dict[str, list[TOCItem]] = {}

    def _collect(items: list[TOCItem]) -> None:
        for item in items:
            if item.href:
                toc_labels[item.href] = item.label
            if item.children:
                toc_children.setdefault(item.href, []).extend(item.children)
                _collect(item.children)

    _collect(original_toc)

    new_toc: list[TOCItem] = []
    for group in groups:
        first = group[0]
        ch = chapters[first]
        label = toc_labels.get(ch.href, ch.title or ch.href)
        children: list[TOCItem] = []
        if ch.href in toc_children:
            children.extend(toc_children[ch.href])
        for idx in group[1:]:
            c = chapters[idx]
            cl = toc_labels.get(c.href, c.title or c.href)
            if cl not in [x.label for x in children] and c.href not in [x.href for x in children]:
                children.append(TOCItem(label=cl, href=c.href, depth=1))
        if children:
            new_toc.append(TOCItem(label=label, href=ch.href, children=children))
        else:
            new_toc.append(TOCItem(label=label, href=ch.href))

    return new_toc
