#!/usr/bin/env python3
"""Deterministic preprocessing, rendering and QA for edit-plan JSON files."""

from __future__ import annotations

import json
import math
import os
import shutil
import subprocess
import tempfile
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
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
    schema_version = int(plan.get("schema_version", 1))
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
        provenance = clip.get("provenance", {})
        provenance_status = provenance.get("status")
        if provenance_status not in {"self_shot", "authorized", "seller_supplied", "unknown"}:
            errors.append(
                f"片段 {index} 必须声明素材来源状态：self_shot、authorized、"
                "seller_supplied 或 unknown"
            )
        if schema_version >= 2:
            editorial_fields = (
                "spoken_meaning", "supported_line", "action_phase", "entry_reason",
                "exit_reason", "relation_to_previous", "attention_role", "speed",
                "sound", "text_overlays", "renderer",
            )
            for field in editorial_fields:
                if field not in clip or clip[field] in (None, ""):
                    errors.append(f"片段 {index} 缺少剪辑决策字段 {field}")
            if clip.get("renderer") not in {"remotion", "ffmpeg"}:
                errors.append(f"片段 {index} 的 renderer 必须是 remotion 或 ffmpeg")
            if not isinstance(clip.get("text_overlays"), list):
                errors.append(f"片段 {index} 的 text_overlays 必须是列表")
            if not isinstance(clip.get("speed"), dict):
                errors.append(f"片段 {index} 的 speed 必须是对象")
            if not isinstance(clip.get("sound"), dict):
                errors.append(f"片段 {index} 的 sound 必须是对象")
        transform = clip.get("transform", {})
        transform_limits = {
            "scale": (1.0, 1.5),
            "focus_x": (0.0, 1.0),
            "focus_y": (0.0, 1.0),
            "brightness": (-0.2, 0.2),
            "contrast": (0.8, 1.3),
            "saturation": (0.0, 2.0),
        }
        for field, (minimum, maximum) in transform_limits.items():
            if field not in transform:
                continue
            try:
                value = float(transform[field])
            except (TypeError, ValueError):
                errors.append(f"片段 {index} 的 transform.{field} 不是数字")
                continue
            if not minimum <= value <= maximum:
                errors.append(
                    f"片段 {index} 的 transform.{field} 必须在 {minimum} 到 {maximum} 之间"
                )
        subtitle = clip.get("subtitle", {"mode": "preserve"})
        mode = subtitle.get("mode", "preserve")
        if mode not in {"preserve", "crop", "replace", "reject"}:
            errors.append(f"片段 {index} 的字幕策略无效：{mode}")
        if mode == "reject":
            errors.append(f"片段 {index} 已标记为 reject，不能进入渲染计划")
        if mode == "replace":
            region = subtitle.get("region", {})
            if any(key not in region for key in ("x", "y", "width", "height")):
                errors.append(f"片段 {index} 的字幕替换缺少完整 region")
            else:
                values = [float(region[key]) for key in ("x", "y", "width", "height")]
                if any(value < 0 or value > 1 for value in values):
                    errors.append(f"片段 {index} 的字幕 region 必须使用0到1的归一化坐标")
                if values[0] + values[2] > 1 or values[1] + values[3] > 1:
                    errors.append(f"片段 {index} 的字幕 region 超出画布")
            if not subtitle.get("cues"):
                errors.append(f"片段 {index} 的 replace 策略没有新字幕 cues")
            if not subtitle.get("source_text_intervals"):
                errors.append(f"片段 {index} 没有记录原硬字幕出现时间 source_text_intervals")
            mask_intervals = subtitle.get("mask_intervals", [])
            if not mask_intervals:
                errors.append(f"片段 {index} 没有明确的 mask_intervals，可能闪出原字幕")
            for source_interval in subtitle.get("source_text_intervals", []):
                covered = any(
                    float(mask.get("start", 0)) <= float(source_interval.get("start", 0))
                    and float(mask.get("end", 0)) >= float(source_interval.get("end", 0))
                    for mask in mask_intervals
                )
                if not covered:
                    errors.append(f"片段 {index} 的遮罩没有完整覆盖原硬字幕时间")
            for cue_index, cue in enumerate(subtitle.get("cues", []), 1):
                if not cue.get("text", "").strip():
                    errors.append(f"片段 {index} 字幕 {cue_index} 没有文字")
                if float(cue.get("end", 0)) <= float(cue.get("start", 0)):
                    errors.append(f"片段 {index} 字幕 {cue_index} 时间无效")
    publish = plan.get("publish", {})
    if len(publish.get("product_name", "")) > 30:
        errors.append("商品名称超过30个字符")
    if not publish.get("product_name", "").strip():
        errors.append("发布资料缺少商品名称")
    if not publish.get("description", "").strip():
        errors.append("发布资料缺少与本条视频对应的描述")
    tags = publish.get("tags", [])
    if not isinstance(tags, list) or not 5 <= len(tags) <= 7:
        errors.append("发布资料需要5到7个相关话题标签")
    elif any(not isinstance(tag, str) or not tag.startswith("#") or len(tag) < 2 for tag in tags):
        errors.append("每个话题标签必须是以#开头的非空字符串")
    strategy = publish.get("hashtag_strategy", {})
    if not isinstance(strategy.get("realtime_hot_verified"), bool):
        errors.append("发布资料必须声明话题标签是否经过实时热门验证")
    return errors


def validate_workflow_gate(product: Path, plan: dict) -> list[str]:
    """Block rendering when semantic or human-review stages are incomplete."""
    state_path = product / "analysis" / "v1" / "workflow-state.json"
    if not state_path.is_file():
        return [
            "缺少 analysis/v1/workflow-state.json；完整素材分析和确认状态未知，禁止渲染"
        ]
    state = load(state_path)
    gates = state.get("gates", {})
    errors: list[str] = []
    product_analysis = product / "analysis" / "v1" / "product-analysis.md"
    if not product_analysis.is_file() or len(product_analysis.read_text(encoding="utf-8").strip()) < 200:
        errors.append("缺少有效的人工商品语义分析 product-analysis.md；禁止渲染")
    evidence_path = product / "analysis" / "v1" / "narrative-evidence.json"
    if not evidence_path.is_file():
        errors.append("缺少逐句叙事证据 narrative-evidence.json；禁止渲染")
    else:
        evidence = load(evidence_path)
        if not str(evidence.get("purchase_thesis", "")).strip():
            errors.append("叙事证据缺少 purchase_thesis；禁止渲染")
        if evidence.get("unresolved_contradictions", []):
            errors.append("叙事证据仍有未解决矛盾；禁止渲染")
        blocked_lines = [
            item for item in evidence.get("lines", [])
            if item.get("support_status") in {"unsupported", "contradicted"}
        ]
        if blocked_lines:
            errors.append("存在无证据或相互矛盾的口播句；禁止渲染")
    required = ("inventory", "product_model", "source_analysis", "shot_library", "directions")
    for name in required:
        status = gates.get(name, {}).get("status")
        if status not in {"pass", "approved"}:
            errors.append(f"工作流门禁 {name} 未通过：{status or 'missing'}")

    analysis = gates.get("source_analysis", {})
    for media in ("images", "videos", "audio", "hard_subtitles"):
        total = analysis.get(f"{media}_total")
        reviewed = analysis.get(f"{media}_reviewed")
        if total is None or reviewed is None:
            errors.append(f"source_analysis 缺少 {media} 完整度计数")
        elif int(reviewed) != int(total):
            errors.append(f"source_analysis 的 {media} 未完整：{reviewed}/{total}")
    if analysis.get("unreported_failures"):
        errors.append("source_analysis 仍有未说明的失败项")

    stage = plan.get("production_stage")
    if stage not in {"baseline", "batch"}:
        errors.append("剪辑计划必须声明 production_stage：baseline 或 batch")
    if stage == "batch" and gates.get("baseline", {}).get("status") != "approved":
        errors.append("基准片尚未通过完整人工视听审核，禁止批量渲染")
    return errors


def _clip_filter(width: int, height: int, clip: dict | None = None) -> str:
    transform = (clip or {}).get("transform", {})
    scale = float(transform.get("scale", 1.0))
    focus_x = float(transform.get("focus_x", 0.5))
    focus_y = float(transform.get("focus_y", 0.5))
    brightness = float(transform.get("brightness", 0.0))
    contrast = float(transform.get("contrast", 1.0))
    saturation = float(transform.get("saturation", 1.0))
    filters = [
        f"scale={width}:{height}:force_original_aspect_ratio=increase",
        f"crop={width}:{height}",
        "setsar=1",
        "fps=30",
    ]
    if scale != 1.0:
        filters.extend([
            f"scale=trunc(iw*{scale:.4f}/2)*2:trunc(ih*{scale:.4f}/2)*2",
            f"crop={width}:{height}:(in_w-out_w)*{focus_x:.4f}:(in_h-out_h)*{focus_y:.4f}",
        ])
    if brightness != 0.0 or contrast != 1.0 or saturation != 1.0:
        filters.append(
            f"eq=brightness={brightness:.4f}:contrast={contrast:.4f}:saturation={saturation:.4f}"
        )
    filters.append("format=yuv420p")
    return ",".join(filters)


def _font_file(configured: str | None = None) -> str | None:
    if configured and Path(configured).is_file():
        return configured
    candidates = []
    if os.name == "nt":
        candidates = [
            "C:/Windows/Fonts/YuGothM.ttc",
            "C:/Windows/Fonts/meiryo.ttc",
            "C:/Windows/Fonts/arial.ttf",
        ]
    elif __import__("sys").platform == "darwin":
        candidates = [
            "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
            "/System/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc",
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        ]
    else:
        candidates = [
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    return next((path for path in candidates if Path(path).is_file()), None)


def _filter_path(path: Path) -> str:
    return str(path).replace("\\", "/").replace(":", r"\:").replace("'", r"\'")


def _subtitle_filters(
    clip: dict, width: int, height: int, temp: Path, clip_index: int
) -> list[str]:
    subtitle = clip.get("subtitle", {})
    if subtitle.get("mode", "preserve") != "replace":
        return []
    region = subtitle["region"]
    x = round(float(region["x"]) * width)
    y = round(float(region["y"]) * height)
    box_width = round(float(region["width"]) * width)
    box_height = round(float(region["height"]) * height)
    style = subtitle.get("style", {})
    background = style.get("background", "black@0.78")
    font = _font_file(style.get("font_file"))
    font_size = int(style.get("font_size", max(34, round(height * 0.031))))
    font_color = style.get("font_color", "white")
    border_color = style.get("border_color", "black")
    border_width = int(style.get("border_width", 2))
    line_spacing = int(style.get("line_spacing", 8))
    filters = []
    mask_intervals = subtitle.get("mask_intervals") or [
        {
            "start": min(float(cue["start"]) for cue in subtitle["cues"]),
            "end": max(float(cue["end"]) for cue in subtitle["cues"]),
        }
    ]
    for interval in mask_intervals:
        enable = f"between(t,{float(interval['start']):.3f},{float(interval['end']):.3f})"
        filters.append(
            f"drawbox=x={x}:y={y}:w={box_width}:h={box_height}:"
            f"color={background}:t=fill:enable='{enable}'"
        )
    for cue_index, cue in enumerate(subtitle["cues"], 1):
        text_file = temp / f"subtitle-{clip_index:03d}-{cue_index:03d}.txt"
        text_file.write_text(cue["text"], encoding="utf-8")
        enable = f"between(t,{float(cue['start']):.3f},{float(cue['end']):.3f})"
        font_part = f":fontfile='{_filter_path(Path(font))}'" if font else ""
        filters.append(
            f"drawtext=textfile='{_filter_path(text_file)}'{font_part}:"
            "expansion=none:"
            f"fontsize={font_size}:fontcolor={font_color}:"
            f"borderw={border_width}:bordercolor={border_color}:"
            f"line_spacing={line_spacing}:"
            f"x={x}+({box_width}-text_w)/2:"
            f"y={y}+({box_height}-text_h)/2:"
            f"enable='{enable}'"
        )
    return filters


def _render_clip(
    source: Path,
    target: Path,
    clip: dict,
    width: int,
    height: int,
    temp: Path,
    clip_index: int,
) -> None:
    start = float(clip["start"])
    duration = float(clip["end"]) - start
    mode = clip.get("source_audio", "mute")
    info = media_info(source)
    video_filters = [_clip_filter(width, height, clip)]
    video_filters.extend(_subtitle_filters(clip, width, height, temp, clip_index))
    vf = ",".join(video_filters)
    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-ss", f"{start:.3f}", "-t", f"{duration:.3f}", "-i", str(source),
    ]
    if mode == "keep" and info["has_audio"]:
        command += [
            "-vf", vf,
            "-af", "aresample=48000,asetpts=PTS-STARTPTS",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2",
            "-movflags", "+faststart", str(target),
        ]
    else:
        command += [
            "-f", "lavfi", "-t", f"{duration:.3f}", "-i", "anullsrc=r=48000:cl=stereo",
            "-vf", vf,
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
    provider = voice.get("provider", "edge-tts")
    if provider == "aivisspeech":
        api = voice.get("api", "http://127.0.0.1:10101").rstrip("/")
        speaker = voice.get("speaker")
        if speaker is None:
            raise ValueError("AivisSpeech 口播必须在 voiceover.speaker 中指定已确认的 style ID")
        try:
            query_url = api + "/audio_query?" + urllib.parse.urlencode(
                {"text": text, "speaker": int(speaker)}
            )
            request = urllib.request.Request(query_url, data=b"", method="POST")
            with urllib.request.urlopen(request, timeout=10) as response:
                query = json.loads(response.read().decode("utf-8"))
            query["speedScale"] = float(voice.get("speed_scale", query.get("speedScale", 1.0)))
            query["pitchScale"] = float(voice.get("pitch_scale", query.get("pitchScale", 0.0)))
            query["intonationScale"] = float(
                voice.get("intonation_scale", query.get("intonationScale", 1.0))
            )
            query["volumeScale"] = float(voice.get("volume_scale", query.get("volumeScale", 1.0)))
            query["prePhonemeLength"] = float(
                voice.get("pre_phoneme_length", query.get("prePhonemeLength", 0.05))
            )
            query["postPhonemeLength"] = float(
                voice.get("post_phoneme_length", query.get("postPhonemeLength", 0.08))
            )
            synthesis_url = api + "/synthesis?" + urllib.parse.urlencode({"speaker": int(speaker)})
            synthesis = urllib.request.Request(
                synthesis_url,
                data=json.dumps(query, ensure_ascii=False).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(synthesis, timeout=120) as response:
                target.write_bytes(response.read())
        except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
            raise RuntimeError(
                "AivisSpeech 当前不可用。请启动 AivisSpeech 并确认 127.0.0.1:10101 可访问；"
                "渲染器不会静默回退到 Edge TTS。"
            ) from error
        return target
    if provider != "edge-tts":
        raise ValueError(f"通用渲染器不支持口播提供商：{provider}")
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


def _range_overlap(left: dict, right: dict) -> float:
    if left.get("source") != right.get("source"):
        return 0.0
    return max(
        0.0,
        min(float(left["end"]), float(right["end"]))
        - max(float(left["start"]), float(right["start"])),
    )


def compare_edit_plans(candidate: dict, historical: dict) -> dict:
    """Measure semantic shot-range reuse, including trimmed near-duplicates."""
    current = candidate.get("timeline", [])
    previous = historical.get("timeline", [])
    durations = [max(0.0, float(clip["end"]) - float(clip["start"])) for clip in current]
    total = sum(durations)
    covered = 0.0
    reused = 0
    for clip, duration in zip(current, durations):
        overlap = max((_range_overlap(clip, old) for old in previous), default=0.0)
        covered += min(duration, overlap)
        if duration and overlap / duration >= 0.6:
            reused += 1
    first_overlap = 0.0
    last_overlap = 0.0
    if current and previous:
        first_duration = durations[0]
        last_duration = durations[-1]
        if first_duration:
            first_overlap = _range_overlap(current[0], previous[0]) / first_duration
        if last_duration:
            last_overlap = _range_overlap(current[-1], previous[-1]) / last_duration
    return {
        "historical_id": historical.get("id"),
        "historical_direction": historical.get("direction"),
        "duration_overlap_share": round(covered / total, 3) if total else 0.0,
        "reused_shot_share": round(reused / len(current), 3) if current else 0.0,
        "opening_overlap_share": round(first_overlap, 3),
        "ending_overlap_share": round(last_overlap, 3),
        "same_direction": bool(candidate.get("direction"))
        and candidate.get("direction") == historical.get("direction"),
    }


def historical_uniqueness(product: Path, plan_path: Path, plan: dict) -> dict:
    """Hard production gate for additions to an existing product/market batch."""
    market = plan.get("market", "UNKNOWN")
    plans_dir = product / "output" / market / "edit-plans"
    comparisons = []
    for path in sorted(plans_dir.glob("*.json")):
        if path.resolve() == plan_path.resolve():
            continue
        historical = load(path)
        comparisons.append(compare_edit_plans(plan, historical))
    policy = {
        "max_duration_overlap_share": 0.55,
        "max_reused_shot_share": 0.60,
        "max_opening_overlap_share": 0.50,
        "max_ending_overlap_share": 0.50,
        **plan.get("historical_uniqueness_policy", {}),
    }
    novelty = plan.get("novelty", {})
    declaration_errors = []
    if comparisons:
        if novelty.get("selection_basis") != "shot_library":
            declaration_errors.append("新增视频必须声明 novelty.selection_basis=shot_library")
        if not str(novelty.get("purchase_reason", "")).strip():
            declaration_errors.append("新增视频必须声明独立购买理由 novelty.purchase_reason")
        if not str(novelty.get("difference_from_history", "")).strip():
            declaration_errors.append("新增视频必须说明 novelty.difference_from_history")
    failures = []
    for item in comparisons:
        reasons = []
        if item["duration_overlap_share"] > policy["max_duration_overlap_share"]:
            reasons.append("与历史成片的源画面时长重合过高")
        if item["reused_shot_share"] > policy["max_reused_shot_share"]:
            reasons.append("大部分镜头是历史镜头的相同或裁短版本")
        if item["opening_overlap_share"] > policy["max_opening_overlap_share"]:
            reasons.append("开头重复历史成片")
        if item["ending_overlap_share"] > policy["max_ending_overlap_share"]:
            reasons.append("结尾重复历史成片")
        if item["same_direction"]:
            reasons.append("销售方向与历史成片相同")
        if reasons:
            failures.append({**item, "reasons": reasons})
    return {
        "status": "fail" if declaration_errors or failures else "pass",
        "policy": policy,
        "declaration_errors": declaration_errors,
        "comparisons": comparisons,
        "failures": failures,
        "note": "内部生产排重闸门，不是平台审核阈值；通过后仍需并排完整观看。",
    }


def render(product: Path, plan_path: Path) -> dict:
    plan = load(plan_path)
    errors = validate_plan(plan, product) + validate_workflow_gate(product, plan)
    uniqueness = historical_uniqueness(product, plan_path, plan)
    if uniqueness["status"] == "fail":
        save(
            product / f"output/{plan.get('market', 'UNKNOWN')}/reports/"
            f"{plan.get('id', 'unknown')}-historical-uniqueness.json",
            uniqueness,
        )
        errors.append(
            "历史成片排重失败："
            + json.dumps(
                uniqueness["declaration_errors"] + uniqueness["failures"],
                ensure_ascii=False,
            )
        )
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
            _render_clip(product / clip["source"], target, clip, width, height, temp, index)
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


def remix_depth(plan: dict) -> dict:
    timeline = plan.get("timeline", [])
    durations = [max(0.0, float(clip["end"]) - float(clip["start"])) for clip in timeline]
    total = sum(durations)
    by_source: dict[str, float] = {}
    for clip, duration in zip(timeline, durations):
        by_source[clip["source"]] = by_source.get(clip["source"], 0.0) + duration
    largest_source = max(by_source.items(), key=lambda item: item[1], default=(None, 0.0))
    transformed = sum(bool(clip.get("transform")) for clip in timeline)
    preserved = sum(clip.get("subtitle", {}).get("mode", "preserve") == "preserve" for clip in timeline)
    kept_audio = sum(clip.get("source_audio", "mute") == "keep" for clip in timeline)
    provenance = [clip.get("provenance", {}).get("status", "undeclared") for clip in timeline]
    policy = {
        "min_unique_sources": 4,
        "max_continuous_clip_seconds": 2.0,
        "max_single_source_share": 0.45,
        "max_preserved_subtitle_share": 0.4,
        "min_transformed_shot_share": 0.6,
        **plan.get("remix_policy", {}),
    }
    clip_count = len(timeline)
    metrics = {
        "unique_source_count": len(by_source),
        "longest_continuous_clip_seconds": round(max(durations, default=0.0), 3),
        "largest_source": largest_source[0],
        "largest_single_source_share": round(largest_source[1] / total, 3) if total else 0.0,
        "preserved_subtitle_share": round(preserved / clip_count, 3) if clip_count else 0.0,
        "kept_source_audio_share": round(kept_audio / clip_count, 3) if clip_count else 0.0,
        "transformed_shot_share": round(transformed / clip_count, 3) if clip_count else 0.0,
        "provenance_counts": {status: provenance.count(status) for status in sorted(set(provenance))},
    }
    warnings = []
    if metrics["unique_source_count"] < policy["min_unique_sources"]:
        warnings.append("使用的独立来源少于内部经验目标")
    if metrics["longest_continuous_clip_seconds"] > policy["max_continuous_clip_seconds"]:
        warnings.append("存在超过内部经验阈值的连续源片段")
    if metrics["largest_single_source_share"] > policy["max_single_source_share"]:
        warnings.append("单一来源占比超过内部经验阈值")
    if metrics["preserved_subtitle_share"] > policy["max_preserved_subtitle_share"]:
        warnings.append("保留原硬字幕的镜头占比较高")
    if metrics["transformed_shot_share"] < policy["min_transformed_shot_share"]:
        warnings.append("记录了画面重构的镜头占比较低")
    if "unknown" in provenance or "undeclared" in provenance:
        warnings.append("存在来源或授权状态未知的素材")
    return {
        "status": "review" if warnings else "pass",
        "metrics": metrics,
        "internal_heuristics": policy,
        "warnings": warnings,
        "disclaimer": "内部生产启发式，不是TikTok官方阈值，也不保证审核结果。",
    }


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
        uniqueness = historical_uniqueness(product, plan_path, plan)
        check("historical_video_uniqueness", uniqueness["status"] == "pass", uniqueness)
        purposes = [clip.get("purpose") for clip in plan["timeline"]]
        check("timeline_has_sales_purpose", all(purposes), purposes)
        if int(plan.get("schema_version", 1)) >= 2:
            editorial_fields = (
                "supported_line", "action_phase", "entry_reason", "exit_reason",
                "relation_to_previous", "attention_role", "speed", "sound", "renderer",
            )
            missing_editorial = [
                {"clip": index, "field": field}
                for index, clip in enumerate(plan["timeline"], 1)
                for field in editorial_fields
                if field not in clip or clip[field] in (None, "")
            ]
            check("editorial_decisions_complete", not missing_editorial, missing_editorial)
        publish = plan.get("publish", {})
        check("product_name_length", len(publish.get("product_name", "")) <= 30, publish.get("product_name"))
        symbol_chars = [
            char for char in publish.get("product_name", "")
            if unicodedata.category(char) in {"So", "Sk"}
        ]
        check("product_name_has_no_emoji", not symbol_chars, symbol_chars)
        description = publish.get("description", "")
        check("publish_description_present", bool(description.strip()), description)
        tags = publish.get("tags", [])
        check("publish_tag_count", isinstance(tags, list) and 5 <= len(tags) <= 7, tags)
        check(
            "publish_tag_format",
            isinstance(tags, list) and all(
                isinstance(tag, str) and tag.startswith("#") and len(tag) > 1 for tag in tags
            ),
            tags,
        )
        strategy = publish.get("hashtag_strategy", {})
        check(
            "hashtag_trend_status_declared",
            isinstance(strategy.get("realtime_hot_verified"), bool),
            strategy,
        )
        expected_locale = plan.get("locale")
        check("market_locale_set", bool(expected_locale), expected_locale)
        claims = plan.get("claims", [])
        invalid_claims = [
            claim for claim in claims
            if claim.get("evidence") not in {"confirmed_user", "product_source", "repeated_source"}
        ]
        check("claims_have_usable_evidence", not invalid_claims, invalid_claims)
        replacement_regions = []
        unsafe_regions = []
        oversized_regions = []
        long_cues = []
        for clip_index, clip in enumerate(plan["timeline"], 1):
            subtitle = clip.get("subtitle", {})
            if subtitle.get("mode") != "replace":
                continue
            region = subtitle["region"]
            replacement_regions.append({"clip": clip_index, **region})
            if float(region["y"]) + float(region["height"]) > 0.9:
                unsafe_regions.append({"clip": clip_index, **region})
            if float(region["width"]) * float(region["height"]) > 0.18:
                oversized_regions.append({"clip": clip_index, **region})
            max_chars = int(subtitle.get("style", {}).get("max_chars_per_line", 18))
            max_lines = int(subtitle.get("style", {}).get("max_lines", 2))
            for cue in subtitle.get("cues", []):
                lines = cue["text"].splitlines()
                if len(lines) > max_lines or any(len(line) > max_chars for line in lines):
                    long_cues.append({"clip": clip_index, "text": cue["text"]})
        check("subtitle_replacement_regions_valid", not unsafe_regions, {
            "regions": replacement_regions,
            "too_close_to_ui_area": unsafe_regions,
        })
        check("subtitle_replacement_not_oversized", not oversized_regions, oversized_regions)
        check("replacement_captions_fit_region", not long_cues, long_cues)
        report = {
            "status": "pass" if all(c["status"] == "pass" for c in checks) else "fail",
            "checks": checks,
            "remix_depth": remix_depth(plan),
            "manual_review_required": [
                "开头是否有停止滑动的能力",
                "镜头与口播含义是否一致",
                "商品事实与促销是否准确",
                "不同成片是否拥有不同销售逻辑",
                "封面是否与成片相关且自然",
                "真人正脸是否确有必要；不确定是否AI时是否按真人处理",
                "字幕遮罩是否遮挡商品、手部动作或重要演示",
                "字幕替换区域是否过大、残留字形或形成明显补丁",
                "裁切是否损伤商品主体、手部动作或使用效果",
                "替换字幕是否与口播同步且没有闪出原硬字幕",
                "画面、声音、文字与叙事是否形成实质性的新表达",
                "每个切点是否由动作或语义驱动，而不是机械按时长切割",
                "局部变速、文字、转场和音效是否确有叙事作用",
                "完整观看时口播、动作声、环境声和BGM是否自然衔接",
                "内部混剪深度警告是否可以接受；不得把阈值解释成平台保证",
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
        plans.append({"path": str(path), "plan": plan})
    comparisons = []
    for left_index, left in enumerate(plans):
        for right in plans[left_index + 1:]:
            metrics = compare_edit_plans(right["plan"], left["plan"])
            failed = (
                metrics["duration_overlap_share"] > 0.55
                or metrics["reused_shot_share"] > 0.60
                or metrics["opening_overlap_share"] > 0.50
                or metrics["ending_overlap_share"] > 0.50
                or metrics["same_direction"]
            )
            comparisons.append({
                "left": left["plan"].get("id"),
                "right": right["plan"].get("id"),
                **metrics,
                "status": "fail" if failed else "pass",
            })
    report = {
        "status": "pass" if all(c["status"] == "pass" for c in comparisons) else "fail",
        "market": market,
        "plan_count": len(plans),
        "comparisons": comparisons,
        "note": "同时识别完全相同和裁短后的近似时间段；仍不能替代新旧成片并排完整观看。",
    }
    save(product / f"output/{market}/reports/batch-diversity.json", report)
    return report
