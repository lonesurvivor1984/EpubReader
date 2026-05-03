"""Application configuration: data directory resolution for dev vs packaged."""

import sys
from pathlib import Path


def _data_dir() -> Path:
    """Return the directory for library.json and cache.

    In development: project_root/data/
    When packaged (PyInstaller): user_home/.epubreader/
    """
    if getattr(sys, "frozen", False):
        # Running as PyInstaller bundle
        return Path.home() / ".epubreader"
    # Running from source
    return Path(__file__).resolve().parent.parent / "data"


DATA_DIR = _data_dir()
LIBRARY_FILE = DATA_DIR / "library.json"
NOTES_DIR = DATA_DIR / "notes"
APP_NAME = "EpubReader"
APP_VERSION = "0.1.0"
