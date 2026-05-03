#!/usr/bin/env python3
"""EPUB Reader — cross-platform desktop EPUB reader with scrolling-style reading."""

import argparse
import sys
from pathlib import Path

from app.config import APP_VERSION, DATA_DIR, LIBRARY_FILE


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="epub-reader",
        description="A cross-platform EPUB reader with scrolling-style reading.",
    )
    parser.add_argument(
        "file",
        nargs="?",
        type=Path,
        help="Open a specific EPUB file directly",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {APP_VERSION}",
    )
    args = parser.parse_args()

    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if args.file:
        file_path = args.file.resolve()
        if not file_path.exists():
            print(f"Error: file not found: {file_path}", file=sys.stderr)
            sys.exit(1)
        _launch(file_path=str(file_path))
    else:
        _launch()


def _launch(*, file_path: str | None = None) -> None:
    """Start the Qt application.

    Parameters
    ----------
    file_path:
        Absolute path to an EPUB file to open directly.
        If None, the bookshelf view is shown.
    """
    from PySide6.QtWidgets import QApplication
    from app.ui.main_window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("EpubReader")
    app.setApplicationVersion(APP_VERSION)

    window = MainWindow(open_file=file_path)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
