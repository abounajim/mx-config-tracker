"""
MX Config Tracker — app.py
────────────────────────────────────────────────────────────────
PyWebView desktop wrapper. Exposes a Python bridge so the HTML
diff viewer can read snapshot files from the shared drive
without any GitHub API or internet access.

Build exe:
    pip install pywebview pyinstaller
    pyinstaller --onefile --noconsole --add-data "diff_viewer.html;." app.py

Run in dev:
    python app.py
────────────────────────────────────────────────────────────────
"""

import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import webview
import config


# ── Resolve HTML path (works both in dev and inside .exe) ───────

def get_html_path() -> str:
    if getattr(sys, '_MEIPASS', None):
        # Running as PyInstaller bundle
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).parent
    return str(base / "diff_viewer.html")


# ── Python bridge (exposed to JavaScript) ───────────────────────

class Bridge:
    """
    All methods here are callable from JavaScript via:
        window.pywebview.api.method_name(args)
    They must return JSON-serialisable values.
    """

    def get_config(self) -> dict:
        """Return current config so the UI can show env, root, etc."""
        return {
            "environment": config.ENVIRONMENT,
            "snapshots_root": str(config.SNAPSHOTS_ROOT),
            "csv_separator": config.CSV_SEPARATOR,
        }

    def list_environments(self) -> list[str]:
        """Return list of environment folders under SNAPSHOTS_ROOT."""
        root = Path(config.SNAPSHOTS_ROOT)
        if not root.exists():
            return []
        return sorted([
            d.name for d in root.iterdir()
            if d.is_dir() and not d.name.startswith('.')
        ])

    def list_snapshots(self, environment: str) -> list[str]:
        """Return sorted list of snapshot timestamps for a given environment."""
        env_path = Path(config.SNAPSHOTS_ROOT) / environment
        if not env_path.exists():
            return []
        folders = sorted([
            d.name for d in env_path.iterdir()
            if d.is_dir() and not d.name.startswith('.')
        ], reverse=True)
        return folders

    def list_objects(self, environment: str, snapshot: str) -> list[str]:
        """Return list of CSV filenames in a given snapshot folder."""
        snap_path = Path(config.SNAPSHOTS_ROOT) / environment / snapshot
        if not snap_path.exists():
            return []
        return sorted([f.name for f in snap_path.glob("*.csv")])

    def read_file(self, environment: str, snapshot: str, filename: str) -> dict:
        """
        Read a CSV file from the snapshot folder.
        Returns { headers: [...], rows: [[...], ...] }
        """
        file_path = Path(config.SNAPSHOTS_ROOT) / environment / snapshot / filename
        if not file_path.exists():
            return {"error": f"File not found: {file_path}"}
        try:
            with open(file_path, newline='', encoding='utf-8-sig') as f:
                reader = csv.reader(f, delimiter=config.CSV_SEPARATOR, quotechar='"')
                all_rows = [row for row in reader if any(c.strip() for c in row)]
            if not all_rows:
                return {"headers": [], "rows": []}
            return {
                "headers": all_rows[0],
                "rows": all_rows[1:]
            }
        except Exception as e:
            return {"error": str(e)}

    def get_all_objects(self, environment: str, snap_base: str, snap_cmp: str) -> dict:
        """
        Return all objects with their file lists for both snapshots.
        Used to build the object list in the UI.
        """
        base_path = Path(config.SNAPSHOTS_ROOT) / environment / snap_base
        cmp_path  = Path(config.SNAPSHOTS_ROOT) / environment / snap_cmp
        base_files = set(f.name for f in base_path.glob("*.csv")) if base_path.exists() else set()
        cmp_files  = set(f.name for f in cmp_path.glob("*.csv")) if cmp_path.exists() else set()
        all_files = sorted(base_files | cmp_files)
        return {
            "files": all_files,
            "base_only": sorted(base_files - cmp_files),
            "cmp_only": sorted(cmp_files - base_files),
        }


# ── Main ────────────────────────────────────────────────────────

def main():
    bridge = Bridge()
    html_path = get_html_path()

    window = webview.create_window(
        title="MX Config Tracker",
        url=f"file:///{html_path}",
        js_api=bridge,
        width=1600,
        height=960,
        min_size=(1024, 600),
        background_color="#0d1117",
    )
    webview.start(debug=False)


if __name__ == "__main__":
    main()
