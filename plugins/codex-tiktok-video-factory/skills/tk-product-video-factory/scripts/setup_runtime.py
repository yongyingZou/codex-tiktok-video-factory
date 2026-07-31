#!/usr/bin/env python3
"""Install the plugin runtime inside the plugin without modifying system Python."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import venv
from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[3]
ENV = PLUGIN / ".venv"


def main() -> int:
    if sys.version_info < (3, 10):
        raise SystemExit("需要 Python 3.10 或更高版本。")
    if not ENV.exists():
        venv.EnvBuilder(with_pip=True).create(ENV)
    folder = "Scripts" if os.name == "nt" else "bin"
    python = ENV / folder / ("python.exe" if os.name == "nt" else "python")
    subprocess.run(
        [str(python), "-m", "pip", "install", "--disable-pip-version-check",
         "-r", str(PLUGIN / "requirements.txt")],
        check=True,
    )
    missing = [name for name in ("ffmpeg", "ffprobe") if not shutil.which(name)]
    print("插件运行环境已就绪。")
    if missing:
        print("仍需安装系统 FFmpeg。运行 doctor 查看对应提示。")
    print(f"运行 Python：{python}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
