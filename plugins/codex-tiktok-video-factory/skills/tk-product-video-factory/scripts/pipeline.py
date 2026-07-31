#!/usr/bin/env python3
"""Deterministic preprocessing, rendering and QA for edit-plan JSON files."""

from __future__ import annotations

import json
import math
import shutil
import subprocess
import tempfile
import unicodedata
from pathlib import Path


def run(command: list[str], *, capture: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        command,
        check=True,
        capture_output=capture,
        text=capture,
    )


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def media_info(path: Path) -> dict:
    result = run(
        [
            "ffprobe", "-v", "error", "-show_streams", "-show_format",
            "-of", "json", str(path),
        ],
        capture=True,
    )
    raw = json.loads(result.stdout)
    video = next((s for s in raw.get("streams", []) if s.get("codec_type") == "video"), {})
    audio = next((s for s in raw.get("streams", []) if s.get("codec_type") == "audio"), None)
    return {
        "duration": float(raw.get("format", {}).get("duration", 0) or 0),
        "width": video.get("width"),
        "height": video.get("height"),
        "fps": video.get("avg_frame_rate"),
        "has_audio": audio is not None,
    }


def preprocess(product: Path, inventory: dict, *, force: bool = False) -> dict:
    """Create one full-duration contact sheet and audio probe for every source video."""
    analysis = product / "analysis" / "v1"
    overview_dir = analysis / "contact-sheets"
    overview_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for item in inventory["inputs"]["source_videos"]:
        source = product / item["path"]
        target = overview_dir / f"{source.stem}.jpg"
        info = item.get("media", {})
        duration = float(info.get("duration", 0) or 0)
        record = {
            "source": item["path"],
            "contact_sheet": str(target.relative_to(product)),
            "status": "cached" if target.exists() and not force else "pending",
            "duration": duration,
        }
        if not target.exists() or force:
            rate = 12 / max(duration, 1)
            vf = (
                f"fps={rate:.8f},"
                "scale=270:480:force_original_aspect_ratio=decrease,"
                "pad=270:480:(ow-iw)/2:(oh-ih)/2:black,"
                "drawtext=text='%{pts\\:hms}':x=8:y=8:fontsize=18:"
                "fontcolor=white:borderw=2:bordercolor=black,"
                "tile=3x4:padding=4:margin=4:color=black"
            )
            try:
                run([
                    "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-i", str(source), "-vf", vf, "-frames:v", "1", str(target),
                ])
                record["status"] = "ok"
            except subprocess.CalledProcessError as error:
                record["status"] = "error"
                record["error"] = str(error)
        records.append(record)
    result = {
        "schema_version": 1,
        "total": len(records),
        "processed": sum(item["status"] in {"ok", "cached"} for item in records),
        "failed": sum(item["status"] == "error" for item in records),
        "videos": records,
        "semantic_status": "awaiting_codex_review",
        "instructions": "Inspect every contact sheet, original video audio, and hard subtitles.",
    }
    save(analysis / "preprocess-report.json", result)
    return result


def validate_plan(plan: dict, product: Path) -> list[str]:
    errors: list[str] = []
    for key in ("id", "market", "timeline", "output"):
        if not plan.get(key):
            errors.append(f"缺少字段：{key}")
    if not isinstance(plan.get("timeline"), list) or not plan.get("timeline"):
        errors.append("timeline 必须包含至少一个片段")
        return errors
    for index, clip in enumerate(plan["timeline"], 1):
        for key in ("source", "start", "end", "purpose"):
            if key not in clip:
                errors.append(f"片段 {index} 缺少 {key}")
        source = product / clip.get("source", "")
        if not source.is_file():
            errors.append(f"片段 {index} 的素材不存在：{clip.get('source')}")
        try:
            if float(clip.get("end", 0)) <= float(clip.get("start", 0)):
                errors.append(f"片段 {index} 的结束时间必须大于开始时间")
        except (TypeError, ValueError):
            errors.append(f"片段 {index} 的时间格式错误")
    publish = plan.get("publish", {})
    if len(publish.get("product_name", "")) > 30:
        errors.append("商品名称超过30个字符")
    return errors


def _clip_filter(width: int, height: int) -> str:
    return (
        f"scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},setsar=1,fps=30,format=yuv420p"
    )


def _render_clip(source: Path, target: Path, clip: dict, width: int, height: int) -> None:
    start = float(clip["start"])
    duration = float(clip["end"]) - start
    mode = clip.get("source_audio", "mute")
    info = media_info(source)
    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-ss", f"{start:.3f}", "-t", f"{duration:.3f}", "-i", str(source),
    ]
    if mode == "keep" and info["has_audio"]:
        command += [
            "-vf", _clip_filter(width, height),
            "-af", "aresample=48000,asetpts=PTS-STARTPTS",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2",
            "-movflags", "+faststart", str(target),
        ]
    else:
        command += [
            "-f", "lavfi", "-t", f"{duration:.3f}", "-i", "anullsrc=r=48000:cl=stereo",
            "-vf", _clip_filter(width, height),
            "-map", "0:v:0", "-map", "1:a:0", "-shortest",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2",
            "-movflags", "+faststart", str(target),
        ]
    run(command)


def _tts(plan: dict, target: Path) -> Path | None:
    voice = plan.get("voiceover", {})
    text = voice.get("text", "").strip()
    if not text or voice.get("provider") == "none":
        return None
    if voice.get("provider", "edge-tts") != "edge-tts":
        raise ValueError("通用渲染器当前只自动执行 edge-tts；其他提供商需先生成 voiceover.file")
    binary = shutil.which("edge-tts")
    if not binary:
        runtime = __import__("sys")
        suffix = ".exe" if runtime.platform == "win32" else ""
        sibling = Path(runtime.executable).parent / f"edge-tts{suffix}"
        binary = str(sibling) if sibling.exists() else None
    if not binary:
        raise RuntimeError("找不到 edge-tts，请运行 bootstrap.py")
    run([
        binary, "--voice", voice["voice"], "--rate", voice.get("rate", "+0%"),
        "--text", text, "--write-media", str(target),
    ])
    return target


def render(product: Path, plan_path: Path) -> dict:
    plan = load(plan_path)
    errors = validate_plan(plan, product)
    if errors:
        raise ValueError("\n".join(errors))
    width = int(plan.get("canvas", {}).get("width", 1080))
    height = int(plan.get("canvas", {}).get("height", 1920))
    output = product / plan["output"]
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="tk-factory-") as temp_name:
        temp = Path(temp_name)
        clips = []
        for index, clip in enumerate(plan["timeline"], 1):
            target = temp / f"clip-{index:03d}.mp4"
            _render_clip(product / clip["source"], target, clip, width, height)
            clips.append(target)
        concat_file = temp / "concat.txt"
        concat_file.write_text(
            "".join(f"file '{path.as_posix()}'\n" for path in clips),
            encoding="utf-8",
        )
        base = temp / "base.mp4"
        run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_file),
            "-c", "copy", str(base),
        ])
        narration_file = None
        narration_duration = 0.0
        voice_cfg = plan.get("voiceover", {})
        supplied = voice_cfg.get("file")
        if supplied:
            narration_file = product / supplied
        else:
            narration_file = _tts(plan, temp / "voice.mp3")
        if narration_file:
            narration_duration = media_info(narration_file)["duration"]
            available = media_info(base)["duration"] - float(voice_cfg.get("start", 0))
            if narration_duration > available + 0.08:
                raise ValueError(
                    f"口播时长 {narration_duration:.2f}s 超过可用画面 {available:.2f}s；"
                    "请缩短文案、提高语速或增加相关镜头。"
                )
        command = [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(base),
        ]
        filter_parts = []
        mix_inputs = ["[0:a]"]
        next_index = 1
        if narration_file:
            command += ["-i", str(narration_file)]
            delay = int(float(voice_cfg.get("start", 0)) * 1000)
            filter_parts.append(
                f"[{next_index}:a]adelay={delay}|{delay},volume={voice_cfg.get('volume', 1.0)}[voice]"
            )
            mix_inputs.append("[voice]")
            next_index += 1
        music = plan.get("music", {})
        if music.get("file"):
            command += ["-stream_loop", "-1", "-i", str(product / music["file"])]
            filter_parts.append(
                f"[{next_index}:a]volume={music.get('volume', 0.12)}[music]"
            )
            mix_inputs.append("[music]")
        filter_parts.append(
            "".join(mix_inputs)
            + f"amix=inputs={len(mix_inputs)}:duration=first:dropout_transition=2,"
              "loudnorm=I=-14:LRA=11:TP=-1.5[aout]"
        )
        command += [
            "-filter_complex", ";".join(filter_parts),
            "-map", "0:v:0", "-map", "[aout]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart", "-shortest", str(output),
        ]
        run(command)
    cover_cfg = plan.get("cover", {})
    cover = product / cover_cfg.get(
        "output", f"output/{plan['market']}/covers/{plan['id']}.jpg"
    )
    cover.parent.mkdir(parents=True, exist_ok=True)
    run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-ss", str(cover_cfg.get("time", 0.5)), "-i", str(output),
        "-frames:v", "1", "-q:v", "2", str(cover),
    ])
    publish = product / f"output/{plan['market']}/publish/{plan['id']}.json"
    save(publish, plan.get("publish", {}))
    result = {
        "status": "rendered",
        "video": str(output),
        "cover": str(cover),
        "publish": str(publish),
        "duration": media_info(output)["duration"],
        "narration_duration": narration_duration,
    }
    save(product / f"output/{plan['market']}/reports/{plan['id']}-render.json", result)
    return result


def qa(product: Path, plan_path: Path) -> dict:
    plan = load(plan_path)
    output = product / plan["output"]
    checks = []

    def check(name: str, ok: bool, detail: object) -> None:
        checks.append({"name": name, "status": "pass" if ok else "fail", "detail": detail})

    errors = validate_plan(plan, product)
    check("edit_plan_schema", not errors, errors)
    if not output.is_file():
        check("output_exists", False, str(output))
        report = {"status": "fail", "checks": checks}
    else:
        info = media_info(output)
        check("output_exists", True, str(output))
        check("vertical_canvas", info["height"] > info["width"], info)
        check("audio_present", info["has_audio"], info)
        expected_duration = sum(float(c["end"]) - float(c["start"]) for c in plan["timeline"])
        check("duration_matches_plan", abs(info["duration"] - expected_duration) < 0.2, {
            "actual": info["duration"], "expected": expected_duration
        })
        black = subprocess.run(
            [
                "ffmpeg", "-hide_banner", "-nostats", "-i", str(output),
                "-vf", "blackdetect=d=0.35:pic_th=0.98", "-an", "-f", "null", "-",
            ],
            check=False, capture_output=True, text=True,
        )
        black_events = [line for line in black.stderr.splitlines() if "black_start:" in line]
        check("no_long_black_frames", not black_events, black_events)
        silence = subprocess.run(
            [
                "ffmpeg", "-hide_banner", "-nostats", "-i", str(output),
                "-af", "silencedetect=n=-45dB:d=1.2", "-vn", "-f", "null", "-",
            ],
            check=False, capture_output=True, text=True,
        )
        silence_events = [line for line in silence.stderr.splitlines() if "silence_start:" in line]
        check("no_unexpected_long_silence", not silence_events, silence_events)
        seen = set()
        duplicates = []
        for clip in plan["timeline"]:
            key = (clip["source"], round(float(clip["start"]), 2), round(float(clip["end"]), 2))
            if key in seen:
                duplicates.append(key)
            seen.add(key)
        check("no_exact_duplicate_ranges", not duplicates, duplicates)
        purposes = [clip.get("purpose") for clip in plan["timeline"]]
        check("timeline_has_sales_purpose", all(purposes), purposes)
        publish = plan.get("publish", {})
        check("product_name_length", len(publish.get("product_name", "")) <= 30, publish.get("product_name"))
        symbol_chars = [
            char for char in publish.get("product_name", "")
            if unicodedata.category(char) in {"So", "Sk"}
        ]
        check("product_name_has_no_emoji", not symbol_chars, symbol_chars)
        expected_locale = plan.get("locale")
        check("market_locale_set", bool(expected_locale), expected_locale)
        claims = plan.get("claims", [])
        invalid_claims = [
            claim for claim in claims
            if claim.get("evidence") not in {"confirmed_user", "product_source", "repeated_source"}
        ]
        check("claims_have_usable_evidence", not invalid_claims, invalid_claims)
        report = {
            "status": "pass" if all(c["status"] == "pass" for c in checks) else "fail",
            "checks": checks,
            "manual_review_required": [
                "开头是否有停止滑动的能力",
                "镜头与口播含义是否一致",
                "商品事实与促销是否准确",
                "不同成片是否拥有不同销售逻辑",
                "封面是否与成片相关且自然",
            ],
        }
    target = product / f"output/{plan.get('market', 'UNKNOWN')}/reports/{plan.get('id', 'unknown')}-qa.json"
    save(target, report)
    return report


def qa_batch(product: Path, market: str) -> dict:
    plans_dir = product / "output" / market / "edit-plans"
    plans = []
    for path in sorted(plans_dir.glob("*.json")):
        plan = load(path)
        ranges = {
            (c["source"], round(float(c["start"]), 1), round(float(c["end"]), 1))
            for c in plan.get("timeline", [])
        }
        plans.append({"path": str(path), "id": plan.get("id"), "direction": plan.get("direction"), "ranges": ranges})
    comparisons = []
    for left_index, left in enumerate(plans):
        for right in plans[left_index + 1:]:
            union = left["ranges"] | right["ranges"]
            overlap = left["ranges"] & right["ranges"]
            ratio = len(overlap) / len(union) if union else 0
            comparisons.append({
                "left": left["id"],
                "right": right["id"],
                "exact_range_jaccard": round(ratio, 3),
                "same_direction": bool(left["direction"]) and left["direction"] == right["direction"],
                "status": "fail" if ratio > 0.5 or (
                    left["direction"] and left["direction"] == right["direction"]
                ) else "pass",
            })
    report = {
        "status": "pass" if all(c["status"] == "pass" for c in comparisons) else "fail",
        "market": market,
        "plan_count": len(plans),
        "comparisons": comparisons,
        "note": "该检查只能识别相同时间段和相同方向，不能替代对叙事逻辑的人工复核。",
    }
    save(product / f"output/{market}/reports/batch-diversity.json", report)
    return report
