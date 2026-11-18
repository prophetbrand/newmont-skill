import json, os, subprocess, sys, tempfile, unittest, zipfile
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
sys.path.insert(0, SCRIPTS)
import brand_sources
import package_for_copilot as pkg
from test_brand_sources import make_pdf, make_pptx

ENV_KEYS = ("NEWMONT_BRAND_SOURCES", "NEWMONT_BRAND_LOG", "NEWMONT_BRAND_CONFIG", "NEWMONT_BRAND_VALUES")
DV_NAME = "Newmont_PPT Template_Detailed View_Feb_2026.pptx"
EXPECTED = ["SKILL.md", pkg.MOVED_FILE, "brand-values.json", "brand-sources.json",
            "brand-sources/Brand Guidelines October 2025.pdf",
            "brand-sources/Newmont_PPT Template_Executive Summary_Feb_2026.pptx", "brand-sources/" + DV_NAME] + \
           ["scripts/" + s for s in pkg.SCRIPTS] + ["references/" + r for r in pkg.REFERENCES]
REAL_DV = os.path.join(ROOT, "brand-sources", "Newmont_PPT Template_Detailed View_Feb_2026.pptx")


def clean_env(**extra):
    env = {k: v for k, v in os.environ.items() if k not in ENV_KEYS}
    env.update(extra)
    return env


def run_packager(out, config=None, *args):
    env = clean_env(**({"NEWMONT_BRAND_CONFIG": config} if config else {}))
    return subprocess.run([sys.executable, "-P", os.path.join(SCRIPTS, "package_for_copilot.py"), "--out", out]
                          + list(args), env=env, capture_output=True, text=True)


class PackageTest(unittest.TestCase):
    """Synthetic sources: a small guidelines PDF and Executive Summary, and a Detailed View padded past 25 MB with an
    orphan part, which the sample-slide strip drops, so the packaged copy is small."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        src = os.path.join(cls.tmp.name, "src")
        os.makedirs(src)
        make_pdf(os.path.join(src, "Brand Guidelines October 2025.pdf"))
        make_pptx(os.path.join(src, "Newmont_PPT Template_Executive Summary_Feb_2026.pptx"))
        dv = os.path.join(src, "Newmont_PPT Template_Detailed View_Feb_2026.pptx")
        make_pptx(dv)
        with zipfile.ZipFile(dv, "a", zipfile.ZIP_STORED) as z:  # still a valid pptx, now 26 MB
            z.writestr("ppt/media/padding.bin", b"\0" * 26_000_000)
        with open(os.path.join(ROOT, "brand-sources.json"), encoding="utf-8") as f:
            cfg = json.load(f)
        cfg.update(sources_dir=src, values_file=os.path.join(ROOT, "brand-values.json"))
        cls.config = os.path.join(cls.tmp.name, "brand-sources.json")
        with open(cls.config, "w", encoding="utf-8") as f:
            json.dump(cfg, f)
        cls.zip = os.path.join(cls.tmp.name, "dist", "skill.zip")
        cls.result = run_packager(cls.zip, cls.config)
        cls.extracted = os.path.join(cls.tmp.name, "x")
        if cls.result.returncode == 0:
            with zipfile.ZipFile(cls.zip) as z:
                z.extractall(cls.extracted)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)

    def test_limits(self):
        with zipfile.ZipFile(self.zip) as z:
            infos = z.infolist()
            skill = z.read("SKILL.md").decode("utf-8")
        self.assertLess(len(skill), 20_000)
        self.assertIn("SKILL.md: %d characters" % len(skill), self.result.stdout)
        for i in infos:
            self.assertLess(i.file_size, 25_000_000, i.filename)
        self.assertLess(sum(i.file_size for i in infos), 50_000_000)
        self.assertLess(os.path.getsize(self.zip), 50_000_000)

    def test_expected_files_including_slimmed_detailed_view(self):
        with zipfile.ZipFile(self.zip) as z:
            names = z.namelist()
            dv = z.getinfo("brand-sources/" + DV_NAME).file_size
        self.assertEqual(sorted(names), sorted(EXPECTED))
        self.assertLess(dv, 1_000_000)

    def test_detailed_view_derived_note(self):
        self.assertIn("NOTE: %s is 26.0 MB; packaging it without its sample slides" % DV_NAME, self.result.stderr)
        self.assertNotIn("WARNING: skipping", self.result.stderr)
        with open(os.path.join(self.extracted, "SKILL.md"), encoding="utf-8") as f:
            skill = f.read()
        self.assertIn("sample slides removed", skill)
        self.assertIn("PowerPoint Template – Detailed View is a derived copy", skill)
        self.assertNotIn("is not in this package", skill)
        self.assertIn('python3 -c "import pptx"', skill)

    def test_skill_md_sections(self):
        with open(os.path.join(self.extracted, "SKILL.md"), encoding="utf-8") as f:
            skill = f.read()
        with open(os.path.join(self.extracted, pkg.MOVED_FILE), encoding="utf-8") as f:
            moved = f.read()
        heads = [l[3:] for l in skill.splitlines() if l.startswith("## ")]
        self.assertEqual(len(heads), len(pkg.KEEP))
        for head, key in zip(heads, pkg.KEEP):
            self.assertTrue(head.startswith(key), head)
        for gone in ("## How a request flows", "Not in this package", "Example. \"put together",
                     "pip install", "**Setup check**"):
            self.assertNotIn(gone, skill)
        self.assertIn("sys.path.insert(0, 'scripts')  # this skill's scripts/", skill)
        self.assertIn("d.save('/tmp/newmont-work/tailings-strategy.pptx')", skill)
        self.assertIn("**One save per deck.**", skill)
        self.assertIn("| `Two Column Comparison`", moved)
        self.assertIn("**Colour.**", moved)
        self.assertIn("## Reply format", moved)
        self.assertIn("## Restyling an existing deck", moved)
        self.assertIn("## Other formats", moved)
        self.assertIn("--nm-pale:#D9E8EC", moved)
        self.assertIn("## Other formats", skill)
        self.assertNotIn("End every reply with", skill.split("## Reply format")[1][:400])

    def test_resolve_from_extracted_zip(self):
        config = os.path.join(self.extracted, "brand-sources.json")
        with open(config, encoding="utf-8") as f:
            self.assertEqual(json.load(f)["sources_dir"], "brand-sources")
        with mock.patch.dict(os.environ, clean_env(NEWMONT_BRAND_CONFIG=config), clear=True):
            got = brand_sources.resolve()
            self.assertEqual(os.path.dirname(got["executive_summary"]["path"]),
                             os.path.join(self.extracted, "brand-sources"))
            self.assertEqual(got["guidelines"]["edition"], "October 2025")
            self.assertLess(got["detailed_view"]["size"], 1_000_000)

    def test_extracted_cli(self):
        cli = [sys.executable, "-P", os.path.join(self.extracted, "scripts", "brand_sources.py")]
        ok = subprocess.run(cli + ["--role", "guidelines", "--role", "executive_summary"], env=clean_env(),
                            capture_output=True, text=True, cwd=self.tmp.name)
        self.assertEqual(ok.returncode, 0, ok.stderr)
        every = subprocess.run(cli, env=clean_env(), capture_output=True, text=True, cwd=self.tmp.name)
        self.assertEqual(every.returncode, 0, every.stderr)
        self.assertIn("detailed_view", every.stdout)

    def test_template_choice_executive_summary(self):
        out = os.path.join(self.tmp.name, "es.zip")
        r = run_packager(out, self.config, "--template", "executive_summary")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("not selected with --template executive_summary", r.stdout)

    def test_template_choice_detailed_view(self):
        out = os.path.join(self.tmp.name, "dv.zip")
        r = run_packager(out, self.config, "--template", "detailed_view")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("not selected with --template detailed_view", r.stdout)
        with zipfile.ZipFile(out) as z:
            self.assertIn("brand-sources/" + DV_NAME, z.namelist())

    def test_still_oversize_after_strip_is_skipped(self):
        def fake_slim(src, dst):
            with open(dst, "wb") as f:
                f.write(b"\0" * 100)
            return 25_000_000
        with mock.patch.dict(os.environ, clean_env(NEWMONT_BRAND_CONFIG=self.config), clear=True), \
                mock.patch.object(pkg, "slim_template", fake_slim), tempfile.TemporaryDirectory() as work:
            data, files, missing, _ = pkg.plan("both", work)
        self.assertIn("detailed_view", missing)
        self.assertIn("over the 25 MB per-file limit", missing["detailed_view"][1])
        self.assertFalse(any(DV_NAME in n for n, _ in files))
        self.assertIn("Detailed View is not in this package", data[0][1].decode("utf-8"))


class LimitTest(unittest.TestCase):
    def test_file_over_25_mb(self):
        with self.assertRaisesRegex(SystemExit, "per-file limit: big.pptx"):
            pkg.check_limits([("a.md", 10), ("big.pptx", 25_000_000)])

    def test_total_over_50_mb(self):
        with self.assertRaisesRegex(SystemExit, "package would be 51.0 MB"):
            pkg.check_limits([("a", 17_000_000), ("b", 17_000_000), ("c", 17_000_000)])

    def test_skill_md_over_limit_reports_count(self):
        with open(os.path.join(ROOT, "SKILL.md"), encoding="utf-8") as f:
            text = f.read()
        with self.assertRaisesRegex(SystemExit, r"generated SKILL.md is \d+ characters \(limit 20000\)"):
            pkg.build_skill_md(text, "x" * 20_000)

    def test_missing_section_fails(self):
        with self.assertRaisesRegex(SystemExit, "expected one '## Phase 2'"):
            pkg.build_skill_md("---\nname: n\ndescription: d\n---\n## Phase 1\n", "")


@unittest.skipUnless(os.path.exists(REAL_DV), "approved brand sources are not in brand-sources/")
class RealSourcesTest(unittest.TestCase):
    def test_real_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "newmont-brand-copilot-skill.zip")
            r = run_packager(out)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("packaging it without its sample slides", r.stderr)
            with zipfile.ZipFile(out) as z:
                self.assertEqual(sorted(z.namelist()), sorted(EXPECTED))
                self.assertLess(z.getinfo("brand-sources/" + DV_NAME).file_size, 25_000_000)
                self.assertLess(len(z.read("SKILL.md").decode("utf-8")), 20_000)
                self.assertTrue(all(i.file_size < 25_000_000 for i in z.infolist()))
            self.assertLess(os.path.getsize(out), 50_000_000)


if __name__ == "__main__":
    unittest.main()

class StudioProfileTest(unittest.TestCase):
    def test_copilot_studio_profile_templates_with_derived_notes(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, "src"); os.makedirs(src)
            make_pdf(os.path.join(src, "Brand Guidelines October 2025.pdf"))
            make_pptx(os.path.join(src, "Newmont_PPT Template_Executive Summary_Feb_2026.pptx"))
            make_pptx(os.path.join(src, DV_NAME))
            with open(os.path.join(ROOT, "brand-sources.json"), encoding="utf-8") as f:
                cfg = json.load(f)
            cfg.update(sources_dir=src, values_file=os.path.join(ROOT, "brand-values.json"))
            config = os.path.join(tmp, "brand-sources.json")
            with open(config, "w", encoding="utf-8") as f:
                json.dump(cfg, f)
            out = os.path.join(tmp, "studio.zip")
            r = run_packager(out, config, "--template", "executive_summary", "--profile", "copilot-studio")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("members:", r.stdout)
            self.assertIn("downsampled images", r.stderr)
            with zipfile.ZipFile(out) as z:
                skill = z.read("SKILL.md").decode("utf-8")
                packed_cfg = json.loads(z.read("brand-sources.json").decode("utf-8"))
                self.assertFalse(any(DV_NAME in n for n in z.namelist()))
            approved_shas = {r: brand_sources.sha256(os.path.join(src, n))[:12] for r, n in (
                ("guidelines", "Brand Guidelines October 2025.pdf"),
                ("executive_summary", "Newmont_PPT Template_Executive Summary_Feb_2026.pptx"))}
            self.assertIn("Brand Identity Guidelines is a derived copy", skill)
            self.assertIn("Executive Summary is a derived copy", skill)
            self.assertIn("reports the approved sha", skill)
            for role, approved in approved_shas.items():
                self.assertEqual(packed_cfg["files"][role].get("approved_sha256_12"), approved, role)
            self.assertNotIn("approved_sha256_12", packed_cfg["files"]["detailed_view"])
            both = run_packager(os.path.join(tmp, "both.zip"), config, "--profile", "copilot-studio")
            self.assertEqual(both.returncode, 0, both.stderr)
            with zipfile.ZipFile(os.path.join(tmp, "both.zip")) as z:
                self.assertIn("brand-sources/" + DV_NAME, z.namelist())
                self.assertIn("Detailed View is a derived copy", z.read("SKILL.md").decode("utf-8"))

    def test_strip_picture_originals(self):
        layout = ('<p:sldLayout xmlns:a="a" xmlns:r="r"><p:pic><a:blip r:embed="rId2"><a:extLst><a:ext uri="x">'
                  '<a14:imgProps><a14:imgLayer r:embed="rId3"/></a14:imgProps></a:ext></a:extLst></a:blip></p:pic>'
                  '<a:extLst><a:ext uri="keep"/></a:extLst></p:sldLayout>')
        rels = ('<Relationships><Relationship Id="rId2" Type="image" Target="../media/image1.jpeg"/>'
                '<Relationship Id="rId3" Type="hdphoto" Target="../media/hdphoto1.wdp"/></Relationships>')
        types = ('<Types><Default Extension="wdp" ContentType="image/vnd.ms-photo"/>'
                 '<Default Extension="xml" ContentType="application/xml"/></Types>')
        with tempfile.TemporaryDirectory() as tmp:
            src, dst = os.path.join(tmp, "src.pptx"), os.path.join(tmp, "dst.pptx")
            with zipfile.ZipFile(src, "w") as z:
                z.writestr("[Content_Types].xml", types)
                z.writestr("ppt/slideLayouts/slideLayout1.xml", layout)
                z.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", rels)
                z.writestr("ppt/media/hdphoto1.wdp", b"x" * 100)
            self.assertEqual(pkg.strip_picture_originals(src, dst), os.path.getsize(dst))
            with zipfile.ZipFile(dst) as z:
                self.assertNotIn("ppt/media/hdphoto1.wdp", z.namelist())
                out_rels = z.read("ppt/slideLayouts/_rels/slideLayout1.xml.rels").decode("utf-8")
                out_layout = z.read("ppt/slideLayouts/slideLayout1.xml").decode("utf-8")
                out_types = z.read("[Content_Types].xml").decode("utf-8")
        self.assertNotIn("hdphoto1.wdp", out_rels)
        self.assertIn('Id="rId2"', out_rels)
        self.assertNotIn("imgProps", out_layout)
        self.assertIn('r:embed="rId2"', out_layout)
        self.assertIn('<a:extLst><a:ext uri="keep"/></a:extLst>', out_layout)
        self.assertNotIn('Extension="wdp"', out_types)
        self.assertIn('Extension="xml"', out_types)


if __name__ == "__main__":
    unittest.main()
