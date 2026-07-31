#!/usr/bin/env python3
"""Zero-dependency front door for the TikTok product video factory."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pipeline
from market_catalog import (
    MARKETS,
    SOURCES as MARKET_SOURCES,
    VERIFIED_AT as MARKETS_VERIFIED_AT,
    VOICE_BY_LOCALE,
)


SAMPLES = {
    "AT": "Wenn Sie dieses Produkt praktisch finden, sehen Sie sich jetzt die Details an.",
    "BE": "Lijkt dit product handig? Bekijk dan nu de details.",
    "BR": "Se este produto parece útil, confira os detalhes.",
    "DE": "Wenn Sie dieses Produkt praktisch finden, sehen Sie sich jetzt die Details an.",
    "ES": "Si este producto te parece útil, consulta ahora los detalles.",
    "FR": "Si ce produit vous semble pratique, découvrez les détails.",
    "GB": "If this looks useful, tap to see the details.",
    "ID": "Kalau produk ini terasa berguna, cek detailnya sekarang.",
    "IE": "If this looks useful, tap to see the details.",
    "IT": "Se questo prodotto ti sembra utile, scopri ora i dettagli.",
    "JP": "この商品が気になった方は、ぜひチェックしてみてください。",
    "MX": "Si este producto te parece útil, revisa ahora los detalles.",
    "MY": "Kalau produk ini nampak berguna, semak butirannya sekarang.",
    "NL": "Lijkt dit product handig? Bekijk dan nu de details.",
    "PH": "Kung mukhang kapaki-pakinabang ito, tingnan ang detalye ngayon.",
    "PL": "Jeśli ten produkt wydaje się przydatny, sprawdź szczegóły.",
    "SG": "If this looks useful, tap to see the details.",
    "TH": "หากสนใจสินค้านี้ ลองกดดูรายละเอียดได้เลยค่ะ",
    "US": "If this looks useful, tap to see the details.",
    "VN": "Nếu bạn thấy sản phẩm này hữu ích, hãy xem chi tiết nhé.",
}
LOCALE_SAMPLES = {
    "en-PH": "If this looks useful, tap to see the details.",
    "en-SG": "If this looks useful, tap to see the details.",
    "fr-BE": "Si ce produit vous semble pratique, découvrez les détails.",
    "ms-MY": "Kalau produk ini nampak berguna, semak butirannya sekarang.",
    "nl-BE": "Lijkt dit product handig? Bekijk dan nu de details.",
    "ta-SG": "இந்தப் பொருள் பயனுள்ளதாகத் தோன்றினால், விவரங்களைப் பாருங்கள்.",
    "zh-CN": "如果你觉得这个商品实用，可以点开看看详情。",
}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".avif", ".heic"}
VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".webm", ".mkv"}


def find_command(name: str) -> str | None:
    """Find a command on PATH or beside the active virtualenv Python."""
    on_path = shutil.which(name)
    if on_path:
        return on_path
    suffix = ".exe" if sys.platform == "win32" else ""
    sibling = Path(sys.executable).parent / f"{name}{suffix}"
    if sibling.is_file():
        return str(sibling)
    plugin_env = (
        Path(__file__).resolve().parents[3]
        / ".venv"
        / ("Scripts" if sys.platform == "win32" else "bin")
        / f"{name}{suffix}"
    )
    return str(plugin_env) if plugin_env.is_file() else None


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def ffprobe(path: Path) -> dict:
    binary = find_command("ffprobe")
    if not binary:
        return {"status": "unavailable", "error": "ffprobe not installed"}
    result = subprocess.run(
        [binary, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        return {"status": "error", "error": result.stderr.strip()}
    raw = json.loads(result.stdout)
    video = next((s for s in raw.get("streams", []) if s.get("codec_type") == "video"), {})
    audio = next((s for s in raw.get("streams", []) if s.get("codec_type") == "audio"), None)
    return {
        "status": "ok",
        "duration": float(raw.get("format", {}).get("duration", 0) or 0),
        "width": video.get("width"),
        "height": video.get("height"),
        "frame_rate": video.get("avg_frame_rate"),
        "video_codec": video.get("codec_name"),
        "has_audio": audio is not None,
        "audio_codec": audio.get("codec_name") if audio else None,
    }


def collect(root: Path, folder: str, extensions: set[str], media: bool) -> list[dict]:
    source = root / folder
    if not source.exists():
        return []
    files = sorted(p for p in source.rglob("*") if p.is_file() and p.suffix.lower() in extensions)
    records = []
    for path in files:
        record = {
            "path": str(path.relative_to(root)),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
            "analysis_status": "pending",
        }
        if media:
            record["media"] = ffprobe(path)
        records.append(record)
    return records


def resolve_markets(values: list[str]) -> list[str]:
    aliases = {info["name"]: code for code, info in MARKETS.items()}
    resolved = []
    for value in values:
        code = aliases.get(value, value.upper())
        if code not in MARKETS:
            raise SystemExit(f"不支持的市场：{value}。运行 markets 查看当前列表。")
        if code not in resolved:
            resolved.append(code)
    return resolved


def inspect_product(root: Path, write: bool = True) -> dict:
    if not root.is_dir():
        raise SystemExit(f"商品目录不存在：{root}")
    images = collect(root, "product", IMAGE_EXTS, media=False)
    source_images = collect(root, "SP", IMAGE_EXTS, media=False)
    videos = collect(root, "SP", VIDEO_EXTS, media=True)
    inventory = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "product_folder": str(root.resolve()),
        "product_id": root.name.split("_", 1)[0],
        "inputs": {
            "product_images": images,
            "source_images": source_images,
            "source_videos": videos,
            "product_notes": "product.md" if (root / "product.md").is_file() else None,
        },
        "counts": {
            "product_images": len(images),
            "source_images": len(source_images),
            "source_videos": len(videos),
            "total": len(images) + len(source_images) + len(videos),
        },
        "readiness": {
            "can_analyze": bool(images or source_images or videos),
            "can_plan_video": bool(videos),
            "warnings": [],
        },
    }
    warnings = inventory["readiness"]["warnings"]
    if not images:
        warnings.append("product/ 中没有识别到商品图片")
    if not videos:
        warnings.append("SP/ 中没有识别到视频，不能生成真实混剪计划")
    bad_media = [
        item["path"] for item in videos if item.get("media", {}).get("status") != "ok"
    ]
    if bad_media:
        warnings.append(f"{len(bad_media)} 个视频无法读取媒体信息")
    if write:
        dump(root / "analysis" / "v1" / "inventory.json", inventory)
    return inventory


def command_doctor(_: argparse.Namespace) -> int:
    checks = {
        "python": {"ok": sys.version_info >= (3, 10), "detail": sys.version.split()[0]},
        "ffmpeg": {"ok": bool(find_command("ffmpeg")), "detail": find_command("ffmpeg")},
        "ffprobe": {"ok": bool(find_command("ffprobe")), "detail": find_command("ffprobe")},
        "edge-tts": {"ok": bool(find_command("edge-tts")), "detail": find_command("edge-tts")},
    }
    optional = ["scenedetect", "paddleocr"]
    for name in optional:
        checks[name] = {"ok": bool(find_command(name)), "detail": find_command(name), "optional": True}
    print(json.dumps(checks, ensure_ascii=False, indent=2))
    required_ok = all(v["ok"] for k, v in checks.items() if k in {"python", "ffmpeg", "ffprobe"})
    if not checks["edge-tts"]["ok"]:
        print("\n提示：尚未安装默认多语言口播。运行：python3 -m pip install edge-tts")
    return 0 if required_ok else 1


def command_markets(_: argparse.Namespace) -> int:
    print(f"核验日期：{MARKETS_VERIFIED_AT}")
    for code, item in MARKETS.items():
        choices = " / ".join(option["language"] for option in item["languages"])
        print(f"{code:>2}  {item['name']:<8} {choices:<20} {item['locale']:<8} {item['currency']}")
    print("来源：")
    for source in MARKET_SOURCES:
        print(f"- {source}")
    return 0


def market_profile(code: str, locale: str | None = None) -> dict:
    item = dict(MARKETS[code])
    selected = locale or item["locale"]
    allowed = {choice["locale"]: choice["language"] for choice in item["languages"]}
    if selected not in allowed:
        raise SystemExit(
            f"{item['name']}不支持内容语言 {selected}；可选：{', '.join(allowed)}"
        )
    item["locale"] = selected
    item["language"] = allowed[selected]
    item["voices"] = VOICE_BY_LOCALE[selected]
    return item


def locale_overrides(values: list[str] | None) -> dict[str, str]:
    result = {}
    for value in values or []:
        if "=" not in value:
            raise SystemExit(f"语言覆盖格式应为 MARKET=locale：{value}")
        market, locale = value.split("=", 1)
        code = resolve_markets([market])[0]
        result[code] = locale
    return result


def voice_for(code: str, preference: str, locale: str | None = None) -> str | None:
    if preference == "none":
        return None
    gender = "male" if preference == "male" else "female"
    return market_profile(code, locale)["voices"].get(gender)


def command_voice_test(args: argparse.Namespace) -> int:
    code = resolve_markets([args.market])[0]
    binary = find_command("edge-tts")
    if not binary:
        raise SystemExit("尚未安装 Edge TTS。请先在项目根目录运行 python3 bootstrap.py。")
    profile = market_profile(code, args.locale)
    voice = voice_for(code, args.voice, args.locale)
    output = Path(args.output or f"voice-test-{code}-{args.voice}.mp3").expanduser().resolve()
    text = args.text or LOCALE_SAMPLES.get(profile["locale"], SAMPLES[code])
    result = subprocess.run(
        [binary, "--voice", voice, "--text", text, "--write-media", str(output)],
        check=False,
    )
    if result.returncode:
        return result.returncode
    print(f"试听音频：{output}")
    print(f"市场：{profile['name']}；语言：{profile['language']}；音色：{voice}")
    return 0


def command_inspect(args: argparse.Namespace) -> int:
    inventory = inspect_product(Path(args.product).expanduser().resolve())
    print(json.dumps(inventory["counts"], ensure_ascii=False, indent=2))
    for warning in inventory["readiness"]["warnings"]:
        print(f"警告：{warning}")
    print(f"清单：{Path(args.product).expanduser().resolve() / 'analysis/v1/inventory.json'}")
    return 0 if inventory["readiness"]["can_analyze"] else 2


def command_plan(args: argparse.Namespace) -> int:
    root = Path(args.product).expanduser().resolve()
    inventory = inspect_product(root)
    markets = resolve_markets(args.markets)
    overrides = locale_overrides(getattr(args, "locales", None))
    if not inventory["readiness"]["can_plan_video"]:
        raise SystemExit("SP/ 中没有视频；已停止，未伪造混剪任务。")
    job = {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "awaiting_product_fact_confirmation",
        "product_folder": str(root),
        "product_id": inventory["product_id"],
        "input_counts": inventory["counts"],
        "markets": [
            dict({
                "code": code,
                **market_profile(code, overrides.get(code)),
                "video_count": args.count,
                "tts": {
                    "provider": "none" if args.voice == "none" else "edge-tts",
                    "preference": args.voice,
                    "voice": voice_for(code, args.voice, overrides.get(code)),
                },
            })
            for code in markets
        ],
        "market_catalog": {
            "verified_at": MARKETS_VERIFIED_AT,
            "sources": MARKET_SOURCES,
        },
        "required_next_artifacts": [
            "product-facts.json",
            "source-videos.json",
            "shot-library.json",
            "video-directions.json",
        ],
        "gate": "Confirm product facts and directions before rendering.",
    }
    job_path = root / "analysis" / "v1" / "job-plan.json"
    dump(job_path, job)
    for code in markets:
        base = root / "output" / code
        for folder in ["videos", "covers", "publish", "reports", "edit-plans"]:
            (base / folder).mkdir(parents=True, exist_ok=True)
    print(f"任务计划：{job_path}")
    for market in job["markets"]:
        print(
            f"- {market['name']}：{market['language']}，{market['video_count']} 条，"
            f"语音 {market['tts']['voice']}"
        )
    print("状态：等待商品事实与视频方向确认；尚未渲染。")
    return 0


def command_preprocess(args: argparse.Namespace) -> int:
    root = Path(args.product).expanduser().resolve()
    inventory = inspect_product(root)
    report = pipeline.preprocess(root, inventory, force=args.force)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["failed"] == 0 else 2


def command_render(args: argparse.Namespace) -> int:
    root = Path(args.product).expanduser().resolve()
    plan_path = Path(args.edit_plan).expanduser().resolve()
    result = pipeline.render(root, plan_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def command_qa(args: argparse.Namespace) -> int:
    root = Path(args.product).expanduser().resolve()
    plan_path = Path(args.edit_plan).expanduser().resolve()
    report = pipeline.qa(root, plan_path)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "pass" else 2


def command_qa_batch(args: argparse.Namespace) -> int:
    root = Path(args.product).expanduser().resolve()
    market = resolve_markets([args.market])[0]
    report = pipeline.qa_batch(root, market)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "pass" else 2


def command_serve(args: argparse.Namespace) -> int:
    import webapp
    webapp.serve(
        Path(args.workspace).expanduser().resolve(),
        port=args.port,
        open_browser=not args.no_browser,
    )
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="TikTok 商品视频工厂")
    commands = result.add_subparsers(dest="command", required=True)
    doctor = commands.add_parser("doctor", help="检查本机能力")
    doctor.set_defaults(func=command_doctor)
    markets = commands.add_parser("markets", help="查看支持的市场")
    markets.set_defaults(func=command_markets)
    voice_test = commands.add_parser("voice-test", help="试听目标市场的推荐音色")
    voice_test.add_argument("--market", required=True, help="例如 JP、泰国、US")
    voice_test.add_argument("--voice", choices=["female", "male"], default="female")
    voice_test.add_argument("--locale", help="多语言市场的内容语言，例如 en-SG")
    voice_test.add_argument("--text", help="可选的试听文案")
    voice_test.add_argument("--output", help="输出 MP3 路径")
    voice_test.set_defaults(func=command_voice_test)
    inspect = commands.add_parser("inspect", help="完整清点商品输入")
    inspect.add_argument("product", help="商品目录")
    inspect.set_defaults(func=command_inspect)
    preprocess = commands.add_parser("preprocess", help="为全部视频生成分析总览")
    preprocess.add_argument("product", help="商品目录")
    preprocess.add_argument("--force", action="store_true", help="重新生成缓存")
    preprocess.set_defaults(func=command_preprocess)
    plan = commands.add_parser("plan", help="建立多市场生产任务")
    plan.add_argument("product", help="商品目录")
    plan.add_argument("--markets", nargs="+", required=True, help="例如 JP TH US")
    plan.add_argument("--count", type=int, default=3, help="每个市场的视频数量")
    plan.add_argument("--voice", choices=["automatic", "female", "male", "none"], default="automatic")
    plan.add_argument("--locale", dest="locales", action="append", help="市场语言覆盖，例如 SG=zh-CN")
    plan.set_defaults(func=command_plan)
    render = commands.add_parser("render", help="按已确认的剪辑计划生成视频")
    render.add_argument("product", help="商品目录")
    render.add_argument("edit_plan", help="剪辑计划 JSON")
    render.set_defaults(func=command_render)
    qa = commands.add_parser("qa", help="检查剪辑计划和成片")
    qa.add_argument("product", help="商品目录")
    qa.add_argument("edit_plan", help="剪辑计划 JSON")
    qa.set_defaults(func=command_qa)
    qa_batch = commands.add_parser("qa-batch", help="检查同市场成片计划是否过度重复")
    qa_batch.add_argument("product", help="商品目录")
    qa_batch.add_argument("--market", required=True)
    qa_batch.set_defaults(func=command_qa_batch)
    serve = commands.add_parser("serve", help="打开极简本地操作页面")
    serve.add_argument("--workspace", required=True, help="允许访问的商品工作区")
    serve.add_argument("--port", type=int, default=8765)
    serve.add_argument("--no-browser", action="store_true")
    serve.set_defaults(func=command_serve)
    return result


def main() -> int:
    args = parser().parse_args()
    if getattr(args, "count", 1) < 1:
        raise SystemExit("视频数量必须大于 0")
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
