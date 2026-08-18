import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = (
    Path(__file__).parents[1]
    / "plugins"
    / "codex-tiktok-video-factory"
    / "skills"
    / "tk-product-video-factory"
    / "scripts"
    / "factory.py"
)
SPEC = importlib.util.spec_from_file_location("factory", SCRIPT)
factory = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(factory)


class FactoryTests(unittest.TestCase):
    def test_render_gate_requires_complete_analysis_and_baseline_approval(self):
        with tempfile.TemporaryDirectory() as temp:
            product = Path(temp)
            plan = {"production_stage": "batch"}
            missing = factory.pipeline.validate_workflow_gate(product, plan)
            self.assertTrue(any("workflow-state.json" in error for error in missing))

            state = {
                "gates": {
                    "inventory": {"status": "pass"},
                    "product_model": {"status": "approved"},
                    "source_analysis": {
                        "status": "pass",
                        "images_total": 2, "images_reviewed": 2,
                        "videos_total": 3, "videos_reviewed": 3,
                        "audio_total": 3, "audio_reviewed": 2,
                        "hard_subtitles_total": 3, "hard_subtitles_reviewed": 3,
                        "unreported_failures": False,
                    },
                    "shot_library": {"status": "pass"},
                    "directions": {"status": "approved"},
                    "baseline": {"status": "pending"},
                }
            }
            state_path = product / "analysis/v1/workflow-state.json"
            state_path.parent.mkdir(parents=True)
            state_path.write_text(__import__("json").dumps(state), encoding="utf-8")
            (state_path.parent / "product-analysis.md").write_text(
                "# 商品分析\n\n" + "商品本质、问题产生场景、用户感受、使用场景、解决机制、直接帮助和边界。" * 12,
                encoding="utf-8",
            )
            evidence_path = state_path.parent / "narrative-evidence.json"
            evidence_path.write_text(__import__("json").dumps({
                "purchase_thesis": "目标用户在问题场景中遇到具体问题，商品通过机制提供有限帮助",
                "unresolved_contradictions": [],
                "lines": [{"line": "supported", "support_status": "supported"}],
            }), encoding="utf-8")
            incomplete = factory.pipeline.validate_workflow_gate(product, plan)
            self.assertTrue(any("audio 未完整" in error for error in incomplete))
            self.assertTrue(any("基准片尚未" in error for error in incomplete))

            state["gates"]["source_analysis"]["audio_reviewed"] = 3
            state["gates"]["baseline"]["status"] = "approved"
            state_path.write_text(__import__("json").dumps(state), encoding="utf-8")
            self.assertEqual(factory.pipeline.validate_workflow_gate(product, plan), [])

            evidence_path.write_text(__import__("json").dumps({
                "purchase_thesis": "错误购买逻辑",
                "unresolved_contradictions": ["问题来源与使用场景冲突"],
                "lines": [{"line": "unsupported", "support_status": "unsupported"}],
            }), encoding="utf-8")
            blocked = factory.pipeline.validate_workflow_gate(product, plan)
            self.assertTrue(any("未解决矛盾" in error for error in blocked))
            self.assertTrue(any("无证据" in error for error in blocked))

    def test_schema_v2_requires_editorial_decisions(self):
        with tempfile.TemporaryDirectory() as folder:
            product = Path(folder)
            source = product / "SP" / "clip.mp4"
            source.parent.mkdir(parents=True)
            source.touch()
            plan = {
                "schema_version": 2,
                "id": "A01",
                "market": "JP",
                "output": "output/JP/videos/A01.mp4",
                "timeline": [{
                    "source": "SP/clip.mp4", "start": 0, "end": 1,
                    "purpose": "hook", "spoken_meaning": "problem",
                    "provenance": {"status": "unknown"},
                    "transform": {}, "subtitle": {"mode": "preserve"},
                }],
                "publish": {
                    "product_name": "商品名", "description": "説明",
                    "tags": ["#商品", "#カテゴリ", "#機能", "#場面", "#悩み"],
                    "hashtag_strategy": {"realtime_hot_verified": False},
                },
            }
            errors = factory.pipeline.validate_plan(plan, product)
            self.assertTrue(any("supported_line" in error for error in errors))
            self.assertTrue(any("renderer" in error for error in errors))

    def test_market_aliases_are_unique(self):
        self.assertEqual(factory.resolve_markets(["日本", "TH", "日本"]), ["JP", "TH"])
        self.assertEqual(factory.voice_for("TH", "female"), "th-TH-PremwadeeNeural")
        self.assertIsNone(factory.voice_for("JP", "none"))
        self.assertNotIn("KR", factory.MARKETS)
        self.assertEqual(factory.market_profile("SG", "zh-CN")["language"], "中文")
        self.assertEqual(factory.voice_for("BE", "female", "fr-BE"), "fr-BE-CharlineNeural")

    def test_empty_product_reports_missing_inputs(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "123_demo"
            (root / "product").mkdir(parents=True)
            (root / "SP").mkdir()
            result = factory.inspect_product(root, write=False)
            self.assertFalse(result["readiness"]["can_analyze"])
            self.assertFalse(result["readiness"]["can_plan_video"])
            self.assertEqual(result["counts"]["total"], 0)
            self.assertEqual(len(result["readiness"]["warnings"]), 2)

    def test_subtitle_replacement_requires_full_mask_coverage(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "SP" / "clip.mp4"
            source.parent.mkdir()
            source.touch()
            plan = {
                "id": "T01",
                "market": "JP",
                "locale": "ja-JP",
                "output": "output/JP/videos/T01.mp4",
                "publish": {"product_name": "テスト"},
                "timeline": [{
                    "source": "SP/clip.mp4",
                    "start": 0,
                    "end": 3,
                    "purpose": "hook",
                    "provenance": {"status": "unknown"},
                    "subtitle": {
                        "mode": "replace",
                        "region": {"x": 0.1, "y": 0.7, "width": 0.8, "height": 0.1},
                        "source_text_intervals": [{"start": 0, "end": 3}],
                        "mask_intervals": [{"start": 0.2, "end": 3}],
                        "cues": [{"start": 0, "end": 3, "text": "テスト"}]
                    }
                }]
            }
            errors = factory.pipeline.validate_plan(plan, root)
            self.assertTrue(any("完整覆盖原硬字幕时间" in error for error in errors))

    def test_subtitle_crop_is_valid_and_larger_reframe_is_supported(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "SP" / "clip.mp4"
            source.parent.mkdir()
            source.touch()
            plan = {
                "id": "T03",
                "market": "JP",
                "locale": "ja-JP",
                "output": "output/JP/videos/T03.mp4",
                "publish": {
                    "product_name": "テスト商品",
                    "description": "白い服の日の悩みを確認✨",
                    "tags": ["#商品", "#カテゴリ", "#特徴", "#場面", "#悩み"],
                    "hashtag_strategy": {"realtime_hot_verified": False},
                },
                "timeline": [{
                    "source": "SP/clip.mp4",
                    "start": 0,
                    "end": 2,
                    "purpose": "crop edge subtitle without covering the product",
                    "provenance": {"status": "unknown"},
                    "transform": {"scale": 1.5, "focus_x": 0.5, "focus_y": 1.0},
                    "subtitle": {"mode": "crop"},
                }],
            }
            self.assertEqual(factory.pipeline.validate_plan(plan, root), [])

    def test_publish_metadata_requires_complete_search_structure(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "SP" / "clip.mp4"
            source.parent.mkdir()
            source.touch()
            base = {
                "id": "T02",
                "market": "JP",
                "locale": "ja-JP",
                "output": "output/JP/videos/T02.mp4",
                "timeline": [{
                    "source": "SP/clip.mp4",
                    "start": 0,
                    "end": 2,
                    "purpose": "hook",
                    "provenance": {"status": "unknown"},
                    "subtitle": {"mode": "preserve"},
                }],
            }
            invalid = dict(base)
            invalid["publish"] = {
                "product_name": "テスト商品",
                "description": "",
                "tags": ["#商品", "#便利"],
            }
            errors = factory.pipeline.validate_plan(invalid, root)
            self.assertTrue(any("描述" in error for error in errors))
            self.assertTrue(any("5到7个" in error for error in errors))
            self.assertTrue(any("实时热门验证" in error for error in errors))

            valid = dict(base)
            valid["publish"] = {
                "product_name": "テスト商品",
                "description": "悩みから商品の変化まで伝える説明です✨",
                "description_cn": "中文核对",
                "tags": ["#商品", "#カテゴリ", "#特徴", "#場面", "#悩み"],
                "hashtag_strategy": {
                    "core_product": ["#商品", "#カテゴリ"],
                    "video_specific": ["#特徴", "#場面", "#悩み"],
                    "realtime_hot_verified": False,
                },
            }
            self.assertEqual(factory.pipeline.validate_plan(valid, root), [])

    def test_remix_depth_reports_internal_risk_without_claiming_platform_guarantee(self):
        plan = {
            "timeline": [
                {
                    "source": "SP/a.mp4", "start": 0, "end": 3,
                    "source_audio": "mute", "provenance": {"status": "unknown"},
                    "transform": {}, "subtitle": {"mode": "preserve"},
                },
                {
                    "source": "SP/b.mp4", "start": 1, "end": 2,
                    "source_audio": "mute", "provenance": {"status": "seller_supplied"},
                    "transform": {"scale": 1.05}, "subtitle": {"mode": "replace"},
                },
            ]
        }
        report = factory.pipeline.remix_depth(plan)
        self.assertEqual(report["status"], "review")
        self.assertEqual(report["metrics"]["unique_source_count"], 2)
        self.assertIn("不是TikTok官方阈值", report["disclaimer"])

    def test_compare_edit_plans_detects_trimmed_historical_reuse(self):
        historical = {
            "id": "A01",
            "direction": "運転中のUV対策",
            "timeline": [
                {"source": "SP/a.mp4", "start": 1.0, "end": 3.0},
                {"source": "SP/b.mp4", "start": 4.0, "end": 6.0},
            ],
        }
        candidate = {
            "id": "B01",
            "direction": "暑さの不安",
            "timeline": [
                {"source": "SP/a.mp4", "start": 1.1, "end": 2.9},
                {"source": "SP/b.mp4", "start": 4.2, "end": 5.8},
            ],
        }
        report = factory.pipeline.compare_edit_plans(candidate, historical)
        self.assertGreater(report["duration_overlap_share"], 0.9)
        self.assertEqual(report["reused_shot_share"], 1.0)

    def test_historical_uniqueness_blocks_old_plan_as_candidate_pool(self):
        with tempfile.TemporaryDirectory() as temp:
            product = Path(temp)
            plans = product / "output/JP/edit-plans"
            plans.mkdir(parents=True)
            historical = {
                "id": "A01",
                "market": "JP",
                "direction": "UV対策",
                "timeline": [
                    {"source": "SP/a.mp4", "start": 1.0, "end": 3.0},
                    {"source": "SP/b.mp4", "start": 4.0, "end": 6.0},
                ],
            }
            (plans / "A01.json").write_text(json.dumps(historical), encoding="utf-8")
            candidate = {
                "id": "B01",
                "market": "JP",
                "direction": "暑さの不安",
                "timeline": [
                    {"source": "SP/a.mp4", "start": 1.1, "end": 2.9},
                    {"source": "SP/b.mp4", "start": 4.2, "end": 5.8},
                ],
                "novelty": {
                    "selection_basis": "shot_library",
                    "purchase_reason": "暑さへの不安",
                    "difference_from_history": "運転ではなく素材の使用感",
                },
            }
            candidate_path = plans / "B01.json"
            candidate_path.write_text(json.dumps(candidate), encoding="utf-8")
            report = factory.pipeline.historical_uniqueness(product, candidate_path, candidate)
            self.assertEqual(report["status"], "fail")
            self.assertTrue(report["failures"])

    def test_historical_uniqueness_accepts_distinct_shot_library_selection(self):
        with tempfile.TemporaryDirectory() as temp:
            product = Path(temp)
            plans = product / "output/JP/edit-plans"
            plans.mkdir(parents=True)
            historical = {
                "id": "A01", "market": "JP", "direction": "UV対策",
                "timeline": [{"source": "SP/a.mp4", "start": 1.0, "end": 3.0}],
            }
            (plans / "A01.json").write_text(json.dumps(historical), encoding="utf-8")
            candidate = {
                "id": "B01", "market": "JP", "direction": "暑さの不安",
                "timeline": [{"source": "SP/c.mp4", "start": 5.0, "end": 7.0}],
                "novelty": {
                    "selection_basis": "shot_library",
                    "purchase_reason": "暑さへの不安",
                    "difference_from_history": "別の問題と別素材",
                },
            }
            candidate_path = plans / "B01.json"
            candidate_path.write_text(json.dumps(candidate), encoding="utf-8")
            report = factory.pipeline.historical_uniqueness(product, candidate_path, candidate)
            self.assertEqual(report["status"], "pass")

    def test_feedback_command_records_violation_event(self):
        with tempfile.TemporaryDirectory() as temp:
            args = type("Args", (), {
                "product": temp,
                "market": "JP",
                "video_id": "B01",
                "workflow_version": "v1",
                "result": "violation",
                "violation_type": "unoriginal_content",
                "appeal_state": "not_started",
                "notes": "First confirmed production feedback",
                "metrics": "{\"views\": 0}",
            })()
            self.assertEqual(factory.command_feedback(args), 0)
            payload = __import__("json").loads(
                (Path(temp) / "analysis/v1/publish-feedback.json").read_text(encoding="utf-8")
            )
            self.assertEqual(payload["events"][0]["video_id"], "B01")
            self.assertEqual(payload["events"][0]["result"], "violation")


if __name__ == "__main__":
    unittest.main()
