#!/usr/bin/env python3
"""Small localhost-only UI with no web framework dependency."""

from __future__ import annotations

import json
import sys
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import factory
import pipeline


APP = Path(__file__).resolve().parents[3] / "app" / "index.html"


def safe_product(value: str, workspace: Path) -> Path:
    path = Path(value).expanduser().resolve()
    try:
        path.relative_to(workspace)
    except ValueError as error:
        raise ValueError(f"商品目录必须位于工作区内：{workspace}") from error
    if not path.is_dir():
        raise ValueError(f"商品目录不存在：{path}")
    return path


class Handler(BaseHTTPRequestHandler):
    workspace: Path

    def send_json(self, value: object, status: int = 200) -> None:
        payload = json.dumps(value, ensure_ascii=False, indent=2).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:
        if self.path != "/":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        payload = APP.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self) -> None:
        try:
            size = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(size) or b"{}")
            if self.path == "/api/markets":
                self.send_json({
                    "verified_at": factory.MARKETS_VERIFIED_AT,
                    "sources": factory.MARKET_SOURCES,
                    "markets": [
                        {
                            "code": code,
                            "name": item["name"],
                            "language": item["language"],
                            "locale": item["locale"],
                            "languages": item["languages"],
                            "currency": item["currency"],
                        }
                        for code, item in factory.MARKETS.items()
                    ],
                })
                return
            if self.path == "/api/products":
                products = []
                for path in sorted(self.workspace.iterdir()):
                    if path.is_dir() and ((path / "SP").is_dir() or (path / "product").is_dir()):
                        products.append({"name": path.name, "path": str(path)})
                self.send_json({"workspace": str(self.workspace), "products": products})
                return
            product = safe_product(body.get("product", ""), self.workspace)
            if self.path == "/api/inspect":
                self.send_json(factory.inspect_product(product))
            elif self.path == "/api/preprocess":
                inventory = factory.inspect_product(product)
                self.send_json(pipeline.preprocess(product, inventory))
            elif self.path == "/api/plan":
                markets = factory.resolve_markets(body.get("markets", []))
                if not markets:
                    raise ValueError("至少选择一个市场")
                inventory = factory.inspect_product(product)
                if not inventory["readiness"]["can_plan_video"]:
                    raise ValueError("SP/ 中没有视频")
                request = type("PlanRequest", (), {
                    "product": str(product),
                    "markets": markets,
                    "count": int(body.get("count", 3)),
                    "voice": body.get("voice", "automatic"),
                    "locales": [
                        f"{code}={locale}"
                        for code, locale in body.get("locales", {}).items()
                    ],
                })
                factory.command_plan(request)
                self.send_json(json.loads((product / "analysis/v1/job-plan.json").read_text()))
            elif self.path == "/api/facts/read":
                notes = product / "product.md"
                self.send_json({"content": notes.read_text(encoding="utf-8") if notes.exists() else ""})
            elif self.path == "/api/facts/write":
                (product / "product.md").write_text(body.get("content", ""), encoding="utf-8")
                self.send_json({"status": "saved", "path": str(product / "product.md")})
            else:
                self.send_json({"error": "unknown endpoint"}, 404)
        except Exception as error:
            self.send_json({"error": str(error)}, 400)

    def log_message(self, format: str, *args: object) -> None:
        return


def serve(workspace: Path, host: str = "127.0.0.1", port: int = 8765, open_browser: bool = True) -> None:
    Handler.workspace = workspace.resolve()
    server = ThreadingHTTPServer((host, port), Handler)
    url = f"http://{host}:{port}/"
    print(f"视频工厂：{url}")
    print(f"允许的商品工作区：{Handler.workspace}")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
