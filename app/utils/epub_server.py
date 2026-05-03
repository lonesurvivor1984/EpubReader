"""Local HTTP server that serves EPUB resources from ZIP in memory."""

from __future__ import annotations

import zipfile
from dataclasses import dataclass
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import PurePosixPath
from threading import Thread

from app.core import epub_parser


@dataclass
class _BookEntry:
    """Registered book on the server."""
    zf: zipfile.ZipFile
    opf_base: str  # e.g. "OEBPS/" — prefix for relative resource paths
    merged: dict[str, bytes] = None  # href -> merged HTML content


class EpubRequestHandler(BaseHTTPRequestHandler):
    """Handles GET /{book_id}/{resource_path} requests."""

    # Shared registry: {book_id: _BookEntry}
    books: dict[str, _BookEntry] = {}

    def do_GET(self) -> None:
        parts = self.path.strip("/").split("/", 1)
        if len(parts) != 2:
            self._send_error(400, "Bad Request")
            return

        book_id, resource_path = parts

        entry = self.books.get(book_id)
        if entry is None:
            self._send_error(404, "Book not found")
            return

        # Prepend OPF base directory to resolve the actual ZIP path
        zip_path = f"{entry.opf_base}{resource_path}" if entry.opf_base else resource_path

        # Check if this is a merged chapter (pre-combined content)
        if entry.merged and resource_path in entry.merged:
            data = entry.merged[resource_path]
            mime = "application/xhtml+xml"
        else:
            try:
                data, mime = epub_parser.get_resource(entry.zf, zip_path)
            except epub_parser.EpubError:
                self._send_error(404, f"Resource not found: {resource_path}")
                return
            except epub_parser.InvalidEpubError:
                self._send_error(500, "Invalid EPUB file")
                return
            except Exception:
                self._send_error(500, "Internal server error")
                return

        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args) -> None:
        pass

    def _send_error(self, code: int, message: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(message.encode("utf-8"))


class EpubServer:
    """Manages an embedded HTTP server for serving EPUB resources."""

    def __init__(self) -> None:
        self._server: HTTPServer | None = None
        self._thread: Thread | None = None
        self._port: int = 0

    @property
    def port(self) -> int:
        return self._port

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self._port}"

    def start(self) -> None:
        """Start the HTTP server on a random free port."""
        self._server = HTTPServer(("127.0.0.1", 0), EpubRequestHandler)
        self._port = self._server.server_address[1]
        EpubRequestHandler.books = {}
        self._thread = Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the HTTP server."""
        if self._server:
            self._server.shutdown()
            self._server = None
            EpubRequestHandler.books = {}

    def register_book(
        self,
        book_id: str,
        file_path: str,
        opf_base: str = "",
        merged: dict[str, bytes] | None = None,
    ) -> None:
        """Register an EPUB file for serving.

        Parameters
        ----------
        book_id:
            Unique identifier for this book.
        file_path:
            Path to the .epub file on disk.
        opf_base:
            Base directory of the OPF within the ZIP (e.g. "OEBPS/").
            Resource hrefs from the manifest will be prefixed with this.
        merged:
            Dict of href -> merged HTML content for chapters that were
            combined from multiple small files.
        """
        EpubRequestHandler.books[book_id] = _BookEntry(
            zf=zipfile.ZipFile(file_path),
            opf_base=opf_base,
            merged=merged or {},
        )

    def unregister_book(self, book_id: str) -> None:
        """Remove an EPUB file from the registry and close the ZipFile."""
        if book_id in EpubRequestHandler.books:
            EpubRequestHandler.books[book_id].zf.close()
            del EpubRequestHandler.books[book_id]

    def url_for(self, book_id: str, resource_path: str) -> str:
        """Build the full URL for a resource."""
        return f"{self.base_url}/{book_id}/{resource_path}"
