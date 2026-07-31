#!/usr/bin/env python3
"""Start the local UI after bootstrap has created the project environment."""

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def main() -> int:
    parser = argparse.ArgumentParser(description="启动 TikTok 商品视频工厂")
    parser.add_argument("--workspace", required=True, help="商品文件夹所在工作区")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    python = ROOT / ".venv" / ("Scripts" if os.name == "nt" else "bin") / (
        "python.exe" if os.name == "nt" else "python"
    )
    if not python.exists():
        raise SystemExit("尚未初始化，请先运行 python3 bootstrap.py")
    command = [
        str(python),
        str(ROOT / "plugins/codex-tiktok-video-factory/skills/tk-product-video-factory/scripts/factory.py"),
        "serve", "--workspace", str(Path(args.workspace).expanduser().resolve()),
        "--port", str(args.port),
    ]
    if args.no_browser:
        command.append("--no-browser")
    try:
        return subprocess.run(command, check=False).returncode
    except KeyboardInterrupt:
        print("\n视频工厂已停止。")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
