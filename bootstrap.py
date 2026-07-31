#!/usr/bin/env python3
"""Create an isolated runtime and install the default zero-account TTS."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import venv
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ENV = ROOT / ".venv"


def executable(name: str) -> Path:
    folder = "Scripts" if os.name == "nt" else "bin"
    suffix = ".exe" if os.name == "nt" else ""
    return ENV / folder / f"{name}{suffix}"


def main() -> int:
    if sys.version_info < (3, 10):
        raise SystemExit("需要 Python 3.10 或更高版本。")
    if not ENV.exists():
        print("正在创建独立运行环境…")
        venv.EnvBuilder(with_pip=True).create(ENV)
    python = executable("python")
    print("正在安装默认多语言语音工具…")
    subprocess.run(
        [str(python), "-m", "pip", "install", "--disable-pip-version-check", "-r", str(ROOT / "requirements.txt")],
        check=True,
    )
    missing = [name for name in ("ffmpeg", "ffprobe") if not shutil.which(name)]
    if missing:
        print("\n尚缺少：" + "、".join(missing))
        if sys.platform == "darwin":
            print("安装命令：brew install ffmpeg")
        elif os.name == "nt":
            print("安装命令：winget install Gyan.FFmpeg")
        else:
            print("Ubuntu/Debian 安装命令：sudo apt install ffmpeg")
        print("安装后重新运行 doctor。")
    print("\n安装完成。运行：")
    print(
        f'  "{python}" plugins/codex-tiktok-video-factory/'
        "skills/tk-product-video-factory/scripts/factory.py doctor"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
