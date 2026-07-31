#!/usr/bin/env python3
"""Cross-platform launcher for the repository checkout."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def main() -> int:
    folder = "Scripts" if os.name == "nt" else "bin"
    python = ROOT / ".venv" / folder / ("python.exe" if os.name == "nt" else "python")
    if not python.exists():
        raise SystemExit("尚未初始化，请先运行：python bootstrap.py")
    script = (
        ROOT / "plugins/codex-tiktok-video-factory/skills/"
        "tk-product-video-factory/scripts/factory.py"
    )
    return subprocess.run([str(python), str(script), *__import__("sys").argv[1:]], check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
