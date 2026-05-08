"""Reader view — QWebEngineView wrapper with navigation and position tracking."""

from __future__ import annotations

from PySide6.QtCore import QTimer, Signal, QUrl
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineScript
import urllib.parse


class ReaderPage(QWebEnginePage):
    """Custom page that tracks scroll position and ensures scrolling works."""

    scroll_position_changed = Signal(int)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._setup_scripts()
        self.loadFinished.connect(self._on_load_finished)

    def _setup_scripts(self) -> None:
        """Inject CSS via QWebEngineScript at DocumentCreation for immediate effect."""
        css = """
html, body {
    height: auto !important;
    min-height: 100% !important;
    max-height: none !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    margin: 0 !important;
    padding: 20px 40px !important;
    box-sizing: border-box !important;
}
body {
    line-height: 1.8 !important;
    max-width: 800px !important;
    margin: 0 auto !important;
    text-align: justify !important;
}
img {
    max-width: 100% !important;
    height: auto !important;
}
p {
    text-indent: 2em !important;
    margin: 0.5em 0 !important;
    text-align: justify !important;
}
div[style*="page-break"],
div.pagebreak,
.page-break {
    display: none !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}
.chapter-divider {
    margin: 60px auto 40px !important;
    text-align: center !important;
}
.chapter-title {
    font-size: 1.4em !important;
    font-weight: bold !important;
    margin-bottom: 12px !important;
    color: #666 !important;
}
.chapter-rule {
    border: none !important;
    border-top: 1px solid #ddd !important;
    width: 60% !important;
    margin: 0 auto !important;
}
.annotated {
    text-decoration: underline !important;
    text-decoration-style: dashed !important;
    text-decoration-color: #B388FF !important;
}
.annotation-tooltip {
    position: fixed !important;
    z-index: 99999;
    background: rgba(40,40,60,0.60) !important;
    backdrop-filter: blur(4px);
    -webkit-backdrop-filter: blur(4px);
    color: #f0f0f0 !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 6px !important;
    padding: 8px 12px !important;
    font-size: 13px !important;
    line-height: 1.5 !important;
    max-width: 280px !important;
    pointer-events: none !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.18) !important;
    word-break: break-word !important;
    white-space: pre-wrap !important;
}
.annotation-tooltip::after {
    content: '';
    position: absolute !important;
    bottom: 100% !important;
    left: 16px !important;
    border-left: 6px solid transparent !important;
    border-right: 6px solid transparent !important;
    border-bottom: 6px solid rgba(40,40,60,0.60) !important;
}
.note-editor {
    position: absolute !important;
    z-index: 10000 !important;
    background: #fff !important;
    border: 1px solid #ccc !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    padding: 12px !important;
    width: 280px !important;
    font-size: 14px !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 8px !important;
}
.note-editor textarea {
    width: 100% !important;
    min-height: 60px !important;
    resize: vertical !important;
    border: 1px solid #ddd !important;
    border-radius: 4px !important;
    padding: 6px !important;
    font-size: 13px !important;
    box-sizing: border-box !important;
}
.note-editor .note-btns {
    display: flex !important;
    justify-content: flex-end !important;
    gap: 8px !important;
}
.note-editor button {
    padding: 4px 14px !important;
    border: none !important;
    border-radius: 4px !important;
    cursor: pointer !important;
    font-size: 13px !important;
}
.note-editor .btn-submit {
    background: #B388FF !important;
    color: #fff !important;
}
.note-editor .btn-cancel {
    background: #f0f0f0 !important;
    color: #666 !important;
}
.action-panel {
    position: absolute !important;
    z-index: 10001 !important;
    display: flex !important;
    gap: 8px !important;
    background: rgba(40,40,60,0.60) !important;
    backdrop-filter: blur(4px);
    -webkit-backdrop-filter: blur(4px);
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 8px !important;
    padding: 6px !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.18) !important;
}
.ap-btn {
    padding: 6px 16px !important;
    border: none !important;
    border-radius: 5px !important;
    cursor: pointer !important;
    font-size: 13px !important;
    color: #f0f0f0 !important;
    background: transparent !important;
    transition: background 0.15s !important;
}
.ap-btn:hover {
    background: rgba(255,255,255,0.15) !important;
}
.ap-btn:active {
    background: rgba(255,255,255,0.25) !important;
}
"""
        # Create a script that injects the CSS before page rendering
        script = QWebEngineScript()
        script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation)
        script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
        script.setRunsOnSubFrames(False)
        script.setName("epub-reader-styles")
        script.setSourceCode(f"""
(function() {{
    var style = document.createElement('style');
    style.textContent = `{css}`;
    if (document.head) {{
        document.head.appendChild(style);
    }} else {{
        var observer = new MutationObserver(function(mutations) {{
            if (document.head) {{
                document.head.appendChild(style);
                observer.disconnect();
            }}
        }});
        observer.observe(document.documentElement, {{ childList: true }});
    }}
}})();
""")
        self.scripts().insert(script)

    def acceptNavigationRequest(self, url: QUrl, nav_type, is_main_frame: bool) -> bool:
        """Allow all navigation within the local server; intercept __annotation__ URLs."""
        url_str = url.toString()
        if "/__annotation__?" in url_str:
            self._handle_annotation(url_str)
            return False  # Don't navigate
        return True

    def _handle_annotation(self, url_str: str) -> None:
        """Parse annotation URL and notify parent."""
        if hasattr(self, "_annotation_callback"):
            query = url_str.split("?", 1)[1]
            params = urllib.parse.parse_qs(query)
            self._annotation_callback({
                "chapter_href": params.get("href", [""])[0],
                "selected_text": params.get("text", [""])[0],
                "note": params.get("note", [""])[0],
            })

    def _on_load_finished(self, ok: bool) -> None:
        if ok:
            self.runJavaScript("window.scrollY || 0", self._emit_scroll)

    def _emit_scroll(self, value) -> None:
        self.scroll_position_changed.emit(int(value))


class ReaderView(QWidget):
    """Wrapper around QWebEngineView for EPUB reading.

    Provides:
    - Chapter loading via HTTP URLs
    - Scroll position tracking (save/restore)
    - Font size control via CSS injection
    """

    scroll_changed = Signal(int)
    url_changed = Signal(str)
    annotation_created = Signal(dict)  # {chapter_href, selected_text, note}

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._page = ReaderPage()
        self._page._annotation_callback = self._on_annotation_from_js
        self._page.scroll_position_changed.connect(self.scroll_changed.emit)
        self._page.loadFinished.connect(self._on_page_loaded)

        self._webview = QWebEngineView()
        self._webview.setPage(self._page)
        layout.addWidget(self._webview)

        # Auto-save timer for scroll position
        self._scroll_timer = QTimer(self)
        self._scroll_timer.setInterval(30000)  # 30 seconds
        self._scroll_timer.timeout.connect(self._poll_scroll)
        self._scroll_timer.start()

        self._current_font_size = 16
        self._current_url: str = ""
        self._current_bg_color: str = ""
        self._chapter_hrefs: list[str] = []
        self._chapter_index: int = 0
        self._annotations: list[dict] = []

    @property
    def current_url(self) -> str:
        """Return the currently loaded chapter URL."""
        return self._current_url

    @property
    def current_chapter_href(self) -> str:
        """Extract the chapter href from the current URL.

        URL format: http://host:port/{book_id}/{chapter_href}
        Returns the chapter_href part (e.g. "Text/text0014.xhtml").
        """
        if not self._current_url:
            return ""
        # URL is like http://127.0.0.1:12345/book_id/Text/file.xhtml
        # Split off protocol+host and book_id to get the remaining path
        # Strip http://host:port/ (variable port length)
        idx = self._current_url.find("/", self._current_url.find("://") + 3)
        if idx == -1:
            return ""
        # Skip book_id segment
        rest = self._current_url[idx + 1:]
        slash_pos = rest.find("/")
        if slash_pos == -1:
            return ""
        return rest[slash_pos + 1:]

    def load_chapter(self, url: str) -> None:
        """Load a chapter from the given URL."""
        self._current_url = url
        self._webview.setUrl(QUrl(url))
        self.url_changed.emit(url)

    def get_scroll_position(self, callback=None) -> None:
        """Asynchronously get the current scroll position."""
        def handler(val):
            self.scroll_changed.emit(int(val))
            if callback:
                callback(int(val))
        self._page.runJavaScript("window.scrollY || 0", handler)

    def set_scroll_position(self, offset: int) -> None:
        """Restore scroll position."""
        if offset > 0:
            self._page.runJavaScript(f"window.scrollTo(0, {offset})")

    def _poll_scroll(self) -> None:
        """Periodic scroll position poll for auto-save."""
        self.get_scroll_position()

    def set_font_size(self, size: int) -> None:
        """Adjust base font size via CSS injection."""
        self._current_font_size = size
        self._apply_styles()

    def _apply_styles(self) -> None:
        """Inject CSS for font size and background color."""
        parts = [f"html {{ font-size: {self._current_font_size}px !important; }}"]
        if self._current_bg_color:
            parts.append(f"html, body {{ background-color: {self._current_bg_color} !important; }}")
        css = "\n".join(parts)
        js = f"""
        (function() {{
            var style = document.getElementById('epub-reader-theme');
            if (!style) {{
                style = document.createElement('style');
                style.id = 'epub-reader-theme';
                document.head.appendChild(style);
            }}
            style.textContent = `{css}`;
        }})();
        """
        self._page.runJavaScript(js)

    def set_background_color(self, color: str) -> None:
        """Set the reading area background color (hex string, e.g. '#FFF9E6').

        Pass an empty string to reset to the default (white).
        """
        self._current_bg_color = color
        self._apply_styles()

    def _on_page_loaded(self, ok: bool) -> None:
        """Re-apply injected styles after chapter navigation."""
        if ok:
            self._apply_styles()
            self._inject_seamless_scroll()
            self._inject_note_editor()
            # Always restore annotations for current chapter
            if self._annotations:
                self.restore_annotations(self._annotations)

    def _on_annotation_from_js(self, data: dict) -> None:
        """Handle annotation data sent from JS via epub:// URL interception."""
        self.annotation_created.emit(data)

    def _inject_note_editor(self) -> None:
        """Inject JS that detects text selection, shows action panel (copy/note).
        All CSS is already injected via DocumentCreation scripts.
        """
        chapter_href = self.current_chapter_href.replace("OEBPS/", "")
        js = f"""
(function() {{
    if (window.__noteEditorInit) return;
    window.__noteEditorInit = true;

    // Capture base URL at init time
    var origin = window.location.origin;
    var path = window.location.pathname;
    var basePath = path.substring(0, path.lastIndexOf('/') + 1);
    var baseUrl = origin + basePath;
    var currentChapter = "{chapter_href}";

    // ── Tooltip: show note on hover over .annotated spans ──
    document.body.addEventListener('mouseover', function(e) {{
        var span = e.target.closest('.annotated');
        if (!span || span._tooltipActive) return;
        var note = span.getAttribute('data-note');
        if (!note) return;

        span._tooltipActive = true;
        var tip = document.createElement('div');
        tip.className = 'annotation-tooltip';
        tip.textContent = note;
        document.body.appendChild(tip);

        var rect = span.getBoundingClientRect();
        tip.style.left = Math.round(rect.left) + 'px';
        tip.style.top = Math.round(rect.bottom + 10) + 'px';
        span._tooltipEl = tip;
    }});

    document.body.addEventListener('mouseout', function(e) {{
        var span = e.target.closest('.annotated');
        if (!span) return;
        var related = e.relatedTarget;
        if (related && span.contains(related)) return;

        if (span._tooltipEl) {{
            span._tooltipEl.remove();
            span._tooltipEl = null;
        }}
        span._tooltipActive = false;
    }});

    // ── Action panel on text selection ──
    var actionPanelVisible = false;
    var editorVisible = false;
    var currentRange = null;
    var currentText = '';

    document.body.addEventListener('mouseup', function(e) {{
        // If action panel or editor is visible, ignore
        if (actionPanelVisible || editorVisible) return;

        var sel = window.getSelection();
        var text = sel.toString().trim();
        if (!text || text.length < 2) return;

        var target = e.target;
        if (target.closest('.note-editor') || target.closest('.annotation-tooltip') || target.closest('.action-panel')) return;

        // Save the selection range
        currentRange = sel.getRangeAt(0).cloneRange();
        currentText = text;

        // Show action panel
        showActionPanel();
    }});

    function showActionPanel() {{
        if (actionPanelVisible) return;
        actionPanelVisible = true;

        var panel = document.createElement('div');
        panel.className = 'action-panel';
        panel.innerHTML = '<button class="ap-btn ap-btn-copy">复制</button><button class="ap-btn ap-btn-note">笔记</button>';

        document.body.appendChild(panel);

        // Position panel below selection
        var rect = currentRange.getBoundingClientRect();
        panel.style.left = rect.left + 'px';
        panel.style.top = (rect.bottom + 10 + window.scrollY) + 'px';

        // Check viewport boundaries and adjust
        var pRect = panel.getBoundingClientRect();
        if (pRect.right > window.innerWidth) {{
            panel.style.left = (window.innerWidth - pRect.width - 10) + 'px';
        }}
        if (pRect.bottom > window.innerHeight) {{
            panel.style.top = (rect.top - pRect.height - 10 + window.scrollY) + 'px';
        }}

        // Copy button — use execCommand('copy') as primary (more reliable in web views)
        panel.querySelector('.ap-btn-copy').addEventListener('mousedown', function(ev) {{
            ev.stopPropagation();  // prevent document.body mousedown from firing
        }});
        panel.querySelector('.ap-btn-copy').addEventListener('click', function() {{
            var text = currentText;
            // Primary: execCommand (reliable for file:// URLs in QtWebEngine)
            var ta = document.createElement('textarea');
            ta.value = text;
            ta.style.position = 'fixed';
            ta.style.left = '-9999px';
            document.body.appendChild(ta);
            ta.select();
            var ok = false;
            try {{ ok = document.execCommand('copy'); }} catch(e) {{}}
            document.body.removeChild(ta);
            hideActionPanel();
            window.getSelection().removeAllRanges();
        }});

        // Note button
        panel.querySelector('.ap-btn-note').addEventListener('mousedown', function(ev) {{
            ev.stopPropagation();
        }});
        panel.querySelector('.ap-btn-note').addEventListener('click', function() {{
            hideActionPanel();
            showNoteEditor();
        }});
    }}

    function hideActionPanel() {{
        var panel = document.querySelector('.action-panel');
        if (panel) panel.remove();
        actionPanelVisible = false;
    }}

    function showNoteEditor() {{
        if (editorVisible) return;
        editorVisible = true;

        var editor = document.createElement('div');
        editor.className = 'note-editor';
        editor.innerHTML = `<textarea placeholder="输入笔记..."></textarea>
            <div class="note-btns">
                <button class="btn-cancel">取消</button>
                <button class="btn-submit">确定</button>
            </div>`;

        // Position editor below selection
        var rect = currentRange.getBoundingClientRect();
        editor.style.left = rect.left + 'px';
        editor.style.top = (rect.bottom + 10 + window.scrollY) + 'px';

        document.body.appendChild(editor);
        editor.querySelector('textarea').focus();

        function closeEditor() {{
            editor.remove();
            editorVisible = false;
            window.getSelection().removeAllRanges();
        }}

        editor.querySelector('.btn-cancel').addEventListener('click', closeEditor);
        editor.querySelector('.btn-submit').addEventListener('click', function() {{
            var note = editor.querySelector('textarea').value.trim();
            var selectedText = currentText;

            // Wrap selected text in span.annotated
            var span = document.createElement('span');
            span.className = 'annotated';
            span.setAttribute('data-note', note);
            currentRange.surroundContents(span);

            // Sync to shared annotations
            window.__epubAnnotations = window.__epubAnnotations || [];
            window.__epubAnnotations.push({{
                chapter_href: currentChapter,
                selected_text: selectedText,
                note: note
            }});

            // Send data to Python via HTTP URL
            var url = baseUrl + "__annotation__?href=" + encodeURIComponent(currentChapter)
                + "&text=" + encodeURIComponent(selectedText)
                + "&note=" + encodeURIComponent(note);
            window.location.href = url;

            closeEditor();
        }});

        // Close on Escape
        editor.addEventListener('keydown', function(ev) {{
            if (ev.key === 'Escape') closeEditor();
        }});
    }}

    // Dismiss action panel on outside click or Escape
    document.body.addEventListener('mousedown', function(e) {{
        if (actionPanelVisible && !e.target.closest('.action-panel')) {{
            hideActionPanel();
        }}
    }});

    document.addEventListener('keydown', function(e) {{
        if (e.key === 'Escape') {{
            if (editorVisible) {{
                var ed = document.querySelector('.note-editor');
                if (ed) ed.remove();
                editorVisible = false;
            }}
            if (actionPanelVisible) {{
                hideActionPanel();
            }}
        }}
    }});
}})();
"""
        self._page.runJavaScript(js)

    def restore_annotations(self, annotations: list[dict]) -> None:
        """Re-apply underlines for existing annotations in the current page."""
        if not annotations:
            return

        import json
        ann_json = json.dumps(annotations)
        js = f"""
(function() {{
    var incoming = {ann_json};

    // Merge all annotations into shared global array
    window.__epubAnnotations = window.__epubAnnotations || [];
    for (var newAnn of incoming) {{
        var exists = window.__epubAnnotations.find(function(a) {{
            return a.selected_text === newAnn.selected_text;
        }});
        if (!exists) window.__epubAnnotations.push(newAnn);
    }}

    // Build matches: walk text nodes and find annotation text
    var matches = [];
    var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
    var node;
    while (node = walker.nextNode()) {{
        var tn = node;
        var parent = tn.parentNode;
        if (!parent || parent.className === 'annotated' || parent.tagName === 'SCRIPT' || parent.tagName === 'STYLE') continue;
        var tc = tn.textContent;
        for (var ann of incoming) {{
            var idx = tc.indexOf(ann.selected_text);
            if (idx === -1) continue;
            matches.push({{
                node: tn,
                offset: idx,
                length: ann.selected_text.length,
                note: ann.note || '已标注'
            }});
        }}
    }}

    // Sort in reverse document order so wrapping doesn't shift later nodes
    matches.sort(function(a, b) {{
        if (a.node !== b.node) {{
            return a.node.compareDocumentPosition(b.node) & 2 ? 1 : -1;
        }}
        return b.offset - a.offset;
    }});

    for (var m of matches) {{
        try {{
            var rightPart = m.node.splitText(m.offset);
            var remainder = rightPart.splitText(m.length);
            var span = document.createElement('span');
            span.className = 'annotated';
            span.setAttribute('data-note', m.note);
            span.appendChild(rightPart);
            m.node.parentNode.insertBefore(span, remainder);
        }} catch(e) {{}}
    }}
}})();
"""
        self._page.runJavaScript(js)

    def set_chapter_list(self, current_href: str, hrefs: list[str]) -> None:
        """Set the ordered list of chapter hrefs and current position.

        Called when a book is opened or when navigating via TOC/bookmarks.
        """
        self._chapter_hrefs = list(hrefs)
        try:
            self._chapter_index = hrefs.index(current_href)
        except ValueError:
            self._chapter_index = 0

    def set_annotations(self, annotations: list[dict]) -> None:
        """Store annotations for restore on current page and seamless chapter loads."""
        self._annotations = annotations

    def _inject_seamless_scroll(self) -> None:
        """Inject JS that auto-loads next chapter when scrolling near bottom."""
        if not self._chapter_hrefs:
            return

        # URL: http://host:port/{book_id}/{chapter_href}
        # We need base = http://host:port/{book_id}/ so next URL = base + chapter_href
        idx = self._current_url.find("/", self._current_url.find("://") + 3)
        if idx != -1:
            rest = self._current_url[idx + 1:]
            slash_pos = rest.find("/")
            if slash_pos != -1:
                base_url = self._current_url[: idx + 1 + slash_pos + 1]
            else:
                base_url = self._current_url
        else:
            base_url = self._current_url

        import json
        chapter_json = json.dumps(self._chapter_hrefs)
        ann_json = json.dumps(self._annotations)
        js_idx = self._chapter_index

        js = f"""
(function() {{
    if (window.__seamlessInit) return;
    window.__seamlessInit = true;

    var chapterHrefs = {chapter_json};
    var chapterIndex = {js_idx};
    var baseUrl = "{base_url}";
    var loading = false;

    // Sync annotations from global window variable (shared with note editor & restore)
    window.__epubAnnotations = window.__epubAnnotations || {ann_json};

    function restoreAnnotationsIn(el) {{
        var anns = window.__epubAnnotations;
        if (!anns || anns.length === 0 || !el) return;

        // Use splitText (not surroundContents) for reliable text wrapping
        var walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null, false);
        var textNodes = [];
        var nd;
        while (nd = walker.nextNode()) {{
            textNodes.push(nd);
        }}

        for (var tn of textNodes) {{
            var parent = tn.parentNode;
            if (!parent || parent.className === 'annotated') continue;
            var tc = tn.textContent;
            for (var ann of anns) {{
                var idx = tc.indexOf(ann.selected_text);
                if (idx === -1) continue;
                try {{
                    var rightPart = tn.splitText(idx);
                    var remainder = rightPart.splitText(ann.selected_text.length);
                    var span = document.createElement('span');
                    span.className = 'annotated';
                    span.setAttribute('data-note', ann.note || '已标注');
                    span.appendChild(rightPart);
                    tn.parentNode.insertBefore(span, remainder);
                }} catch(e) {{}}
            }}
        }}
    }}

    function loadNextChapter() {{
        if (loading) return;
        var nextIdx = chapterIndex + 1;
        if (nextIdx >= chapterHrefs.length) return;

        loading = true;
        var nextHref = chapterHrefs[nextIdx];
        var url = baseUrl + nextHref;

        fetch(url)
            .then(function(r) {{
                if (!r.ok) throw new Error('Not found');
                return r.text();
            }})
            .then(function(html) {{
                var parser = new DOMParser();
                var doc = parser.parseFromString(html, 'text/html');
                var body = doc.querySelector('body');
                if (!body) return;

                var div = document.createElement('div');
                div.className = 'chapter-divider';

                var hr = document.createElement('hr');
                hr.className = 'chapter-rule';
                div.appendChild(hr);

                document.body.appendChild(div);

                var child;
                while (body.firstChild) {{
                    child = body.firstChild;
                    document.body.appendChild(child);
                }}

                // Restore annotations in all newly appended content
                restoreAnnotationsIn(document.body);

                chapterIndex = nextIdx;
                loading = false;
            }})
            .catch(function() {{
                loading = false;
            }});
    }}

    var scrollTimeout;
    window.addEventListener('scroll', function() {{
        if (scrollTimeout) return;
        scrollTimeout = setTimeout(function() {{
            scrollTimeout = null;
            var scrollTop = window.scrollY || window.pageYOffset || 0;
            var clientHeight = document.documentElement.clientHeight || document.body.clientHeight;
            var scrollHeight = document.body.scrollHeight || document.documentElement.scrollHeight;
            if (scrollTop + clientHeight >= scrollHeight - 200) {{
                loadNextChapter();
            }}
        }}, 200);
    }});
}})();
"""
        self._page.runJavaScript(js)

    def start_scroll_tracking(self) -> None:
        """Start periodic scroll position polling."""
        self._scroll_timer.start()

    def stop_scroll_tracking(self) -> None:
        """Stop periodic scroll position polling."""
        self._scroll_timer.stop()
