import json, os, sys, tempfile, unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import brand_log
from test_brand_sources import make_pdf, make_pptx

FIELDS = ("ts", "request", "activated", "activation_path", "template", "routing_reason",
          "clarifying_question_asked", "defaulted", "output", "layouts_used", "notes")


class LogTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.src = os.path.join(self.tmp.name, "src")
        os.makedirs(self.src)
        self.log = os.path.join(self.tmp.name, "nested", "requests.jsonl")
        self.env = mock.patch.dict(os.environ, {"NEWMONT_BRAND_SOURCES": self.src, "NEWMONT_BRAND_LOG": self.log})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def lines(self):
        with open(self.log) as f:
            return [json.loads(l) for l in f]

    def test_sources_error_when_dir_empty(self):
        brand_log.log_request(request="x" * 500, activated=True, activation_path="direct: deck",
                              template="executive_summary", routing_reason="r", layouts_used=["Three Column"])
        e = self.lines()[0]
        for k in FIELDS:
            self.assertIn(k, e)
        self.assertEqual(len(e["request"]), 300)
        self.assertNotIn("sources", e)
        self.assertIn("will not fall back", e["sources_error"])
        self.assertEqual(e["layouts_used"], ["Three Column"])

    def test_unreadable_config_raises(self):
        with mock.patch.dict(os.environ, {"NEWMONT_BRAND_CONFIG": os.path.join(self.tmp.name, "missing.json")}):
            with self.assertRaises(brand_log.brand_sources.SourceError):
                brand_log.log_request(request="x")
        self.assertFalse(os.path.exists(self.log))

    def test_sources_recorded_and_appends(self):
        make_pdf(os.path.join(self.src, "Brand Guidelines October 2025.pdf"))
        make_pptx(os.path.join(self.src, "X_Template_Detailed View_Feb_2026.pptx"))
        make_pptx(os.path.join(self.src, "X_Template_Executive Summary_Feb_2026.pptx"))
        brand_log.log_request(request="a", activated=False, activation_path="not activated: non-PowerPoint request")
        brand_log.log_request(request="b", activated=True, clarifying_question_asked=True)
        a, b = self.lines()
        self.assertTrue(a["sources"]["guidelines"].startswith("October 2025 (sha "))
        self.assertFalse(a["activated"])
        self.assertTrue(b["clarifying_question_asked"])
        self.assertEqual([e["request"] for e in brand_log.tail(1)], ["b"])

    def test_rebuild_replaces_last_line(self):
        brand_log.log_request(request="a", output="/x/a.pptx", notes="first")
        brand_log.log_request(request="b", output="/x/b.pptx", notes="first")
        brand_log.log_request(request="b", output="/x/b.pptx", notes="rebuild")
        self.assertEqual([(e["request"], e["notes"]) for e in self.lines()], [("a", "first"), ("b", "rebuild")])
        brand_log.log_request(request="a", output="/x/a.pptx", notes="again")  # not the last line: appended
        brand_log.log_request(request="b", output="/x/other.pptx")  # different output: appended
        brand_log.log_request(request="b")  # no output: never deduped
        brand_log.log_request(request="b")
        self.assertEqual([e["request"] for e in self.lines()], ["a", "b", "a", "b", "b", "b"])
        self.assertEqual(os.listdir(os.path.dirname(self.log)), ["requests.jsonl"])  # no temp file left


if __name__ == "__main__":
    unittest.main()
