import importlib.util
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


if __name__ == "__main__":
    unittest.main()
