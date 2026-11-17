import json, os, subprocess, sys, tempfile, unittest
from unittest import mock

SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
sys.path.insert(0, SCRIPTS)
import brand_sources
import pymupdf
from pptx import Presentation


def make_pptx(path, title="Newmont Template"):
    p = Presentation()
    p.core_properties.title = title
    p.save(path)


def make_pdf(path, text="Brand Identity Guidelines\nOCTOBER 2025 EDITION"):
    d = pymupdf.open()
    d.new_page().insert_text((72, 72), text)
    d.set_metadata({"title": "Newmont Brand Identity Guidelines"})
    d.save(path)
    d.close()


class SourcesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        make_pdf(os.path.join(self.dir, "Brand Guidelines October 2025.pdf"))
        make_pptx(os.path.join(self.dir, "Newmont_PPT Template_Detailed View_Feb_2026.pptx"))
        make_pptx(os.path.join(self.dir, "Newmont_PPT Template_Executive Summary_Feb_2026.pptx"))
        self.env = mock.patch.dict(os.environ, {"NEWMONT_BRAND_SOURCES": self.dir}, clear=False)
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def test_env_override_and_versions(self):
        cfg = brand_sources.load_config()
        self.assertEqual(cfg["sources_dir"], os.path.normpath(self.dir))
        s = brand_sources.resolve()
        self.assertEqual(set(s), {"guidelines", "detailed_view", "executive_summary"})
        self.assertRegex(s["guidelines"]["version"], r"^October 2025 \(sha [0-9a-f]{12}\)$")
        self.assertRegex(s["detailed_view"]["version"], r"^Feb 2026 \(sha [0-9a-f]{12}\)$")
        self.assertEqual(s["guidelines"]["title"], "Newmont Brand Identity Guidelines")
        self.assertEqual(s["detailed_view"]["title"], "Newmont Template")
        for k in ("role", "label", "path", "file_name", "version", "sha256_12", "modified", "size"):
            self.assertIn(k, s["executive_summary"])

    def test_pdf_edition_from_page_one_beats_file_name(self):
        os.replace(os.path.join(self.dir, "Brand Guidelines October 2025.pdf"),
                   os.path.join(self.dir, "Brand Guidelines.pdf"))
        self.assertTrue(brand_sources.resolve(["guidelines"])["guidelines"]["version"].startswith("October 2025 "))

    def test_role_subset_and_manifest(self):
        m = brand_sources.manifest(["detailed_view"])
        self.assertEqual(list(m["sources"]), ["detailed_view"])
        self.assertIn("resolved_at", m)

    def test_missing_file_message(self):
        os.remove(os.path.join(self.dir, "Newmont_PPT Template_Executive Summary_Feb_2026.pptx"))
        with self.assertRaises(brand_sources.SourceError) as cm:
            brand_sources.resolve()
        msg = str(cm.exception)
        self.assertIsInstance(cm.exception, RuntimeError)
        for part in ("executive_summary", "*Template_Executive Summary*.pptx", os.path.normpath(self.dir),
                     "Replace or add the file there; the skill will not fall back to older brand values."):
            self.assertIn(part, msg)

    def test_cli_exit_code_2_on_missing(self):
        os.remove(os.path.join(self.dir, "Brand Guidelines October 2025.pdf"))
        r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "brand_sources.py")], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        self.assertIn("will not fall back", r.stderr)

    def test_cli_json(self):
        r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "brand_sources.py"), "--json", "--role",
                            "guidelines"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(list(json.loads(r.stdout)["sources"]), ["guidelines"])

    def test_duplicate_matches_raise_naming_all(self):
        newer = os.path.join(self.dir, "Newmont_PPT Template_Detailed View_Aug_2026.pptx")
        make_pptx(newer)
        with self.assertRaises(brand_sources.SourceError) as cm:
            brand_sources.resolve(["detailed_view"])
        for part in ("detailed_view", "2 files", "Newmont_PPT Template_Detailed View_Aug_2026.pptx",
                     "Newmont_PPT Template_Detailed View_Feb_2026.pptx"):
            self.assertIn(part, str(cm.exception))

    def test_values_and_stale_warning(self):
        values = brand_sources.load_values()
        self.assertEqual(values["guidelines_edition"], "October 2025")
        g = brand_sources.resolve(["guidelines"])["guidelines"]
        self.assertEqual(g["edition"], "October 2025")
        self.assertIsNone(brand_sources.stale_warning(values, g))
        os.replace(os.path.join(self.dir, "Brand Guidelines October 2025.pdf"),
                   os.path.join(self.dir, "Brand Guidelines May 2026.pdf"))
        make_pdf(os.path.join(self.dir, "Brand Guidelines May 2026.pdf"), "Brand Identity Guidelines\nMAY 2026")
        r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "brand_sources.py")], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("brand-values.json was digested from October 2025; the guidelines file is May 2026: "
                      "re-digest before trusting colours and chart rules", r.stderr)

    def test_values_env_override_and_missing(self):
        with mock.patch.dict(os.environ, {"NEWMONT_BRAND_VALUES": os.path.join(self.dir, "nope.json")}):
            with self.assertRaisesRegex(brand_sources.SourceError, "nope.json"):
                brand_sources.load_values()

    def test_relative_paths_resolve_against_config_folder(self):
        cfg_path = os.path.join(self.dir, "cfg.json")
        with open(cfg_path, "w") as f:
            json.dump({"sources_dir": ".", "log_file": "logs/x.jsonl", "files": {}}, f)
        with mock.patch.dict(os.environ, {"NEWMONT_BRAND_SOURCES": "", "NEWMONT_BRAND_LOG": ""}):
            cfg = brand_sources.load_config(cfg_path)
        self.assertEqual(cfg["sources_dir"], os.path.normpath(self.dir))
        self.assertEqual(cfg["log_file"], os.path.join(os.path.normpath(self.dir), "logs", "x.jsonl"))

    def test_edition_parsing(self):
        self.assertEqual(brand_sources.edition("Template_Feb_2026"), "Feb 2026")
        self.assertEqual(brand_sources.edition("OCTOBER 2025 EDITION"), "October 2025")
        self.assertEqual(brand_sources.edition("sept-2024"), "Sep 2024")
        self.assertIsNone(brand_sources.edition("no date here"))


class LogoTest(unittest.TestCase):
    def test_extract_logo_from_executive_summary(self):
        with tempfile.TemporaryDirectory() as d:
            r = brand_sources.extract_logo(os.path.join(d, "logo.png"))
            self.assertEqual(os.path.basename(r["native"]), "logo.emf")
            self.assertEqual(r["found_on"], "master 0")
            self.assertGreater(os.path.getsize(r["native"]), 0)
            if r["png"]:  # converted only when soffice is on PATH
                with open(r["png"], "rb") as f:
                    self.assertEqual(f.read(4), b"\x89PNG")
            self.assertEqual(sorted(os.listdir(d)), sorted(os.path.basename(p) for p in (r["native"], r["png"]) if p))

    def test_no_picture_raises(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(brand_sources, "_pictures", side_effect=lambda shapes: iter(())):
            with self.assertRaisesRegex(brand_sources.SourceError, "No picture found"):
                brand_sources.extract_logo(os.path.join(d, "logo.png"))


if __name__ == "__main__":
    unittest.main()


class TestEnvRelativeToCwd(unittest.TestCase):
    def test_env_override_resolves_against_cwd(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            old = os.getcwd(); os.chdir(d)
            try:
                os.environ["NEWMONT_BRAND_SOURCES"] = "./empty"
                self.assertEqual(brand_sources.load_config()["sources_dir"], os.path.join(os.path.realpath(d), "empty"))
            finally:
                os.chdir(old); os.environ.pop("NEWMONT_BRAND_SOURCES", None)
