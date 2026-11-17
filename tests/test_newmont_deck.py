import io, json, os, shutil, subprocess, sys, tempfile, unittest
from unittest import mock

SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
sys.path.insert(0, SCRIPTS)
import brand_sources
from newmont_deck import Deck, layout_roles, rect, text
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from pptx.util import Pt

NAME = "Newmont - [Test deck]"
ACT = "direct: deck/presentation/slides"
FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
CHART = {"type": "column", "categories": ["[A]", "[B]"], "series": {"[S1]": [1, 2], "[S2]": [2, 1]}}
TABLE = {"header": ["[Metric]", "[Value]"], "rows": [["[Row]", "1.0"], ["[Row]", "2.0"]]}
PLANS = {
    "executive_summary": [
        ("1_Cover slide Opt 1", dict(title="[Title]", subtitle="[Subtitle]")),
        ("Three Column Panels", dict(title="[T]", lead="[Lead]", col1=["[a]", ("[b]", 1)], col2="[c]", col3="[d]")),
        ("Single chart with supporting text", dict(title="[T]", body="[Text]", head1="[Chart]", chart1=CHART)),
        ("Title and Content", dict(title="[T]", body=TABLE)),
        ("free", None),
        ("Thank you Opt 1", dict(title="Thank you"))],
    "detailed_view": [
        ("1_Cover slide Opt 1b", dict(title="[Title]", subtitle="[Subtitle]")),
        ("Highlights, Risks & Mitigations", dict(title="[T]", head2="[H]", head3="[R]", col1="[x]", col2="[y]")),
        ("ScoreCard", dict(title="[T]", table1=TABLE, chart1=CHART, chart2={"type": "pie", "categories": ["[a]", "[b]"],
                                                                             "series": {"[s]": [1, 1]}}, body="[c]")),
        ("Title and Content", dict(title="[T]", body=TABLE)),
        ("free", None),
        ("Thank you Opt 1", dict(title="Thank you"))]}


class DeckTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.log = os.path.join(cls.tmp.name, "requests.jsonl")
        cls.env = mock.patch.dict(os.environ, {"NEWMONT_BRAND_LOG": cls.log})
        cls.env.start()
        cls.built = {}
        for template, plan in PLANS.items():
            d = Deck(template, NAME, date="[Month Year]", request="test %s" % template,
                     routing={"reason": "test routing", "defaulted": True, "template": template}, activation_path=ACT)
            for layout, fills in plan:
                if fills is None:
                    s = d.free_slide("[Free]")
                    rect(s, 36, 130, 200, 80, "D9E8EC")
                    text(s, 46, 140, 180, 60, "[Step]", size=12, color="0C2B82")
                else:
                    d.add(layout, **fills)
            path = os.path.join(cls.tmp.name, template + ".pptx")
            cls.built[template] = (path, d.save(path))

    @classmethod
    def tearDownClass(cls):
        cls.env.stop()
        cls.tmp.cleanup()

    def test_slides_layouts_and_placeholders(self):
        for template, (path, _) in self.built.items():
            with self.subTest(template=template):
                prs = Presentation(path)
                want = [l if f is not None else "Title Only" for l, f in PLANS[template]]
                self.assertEqual([s.slide_layout.name for s in prs.slides], want)
                for i, s in enumerate(prs.slides, 1):
                    for ph in s.placeholders:
                        if ph._element.tag.endswith("}sp"):
                            self.assertTrue(ph.text_frame.text.strip(), "empty placeholder %s on slide %d" % (ph.name, i))
                        if ph.placeholder_format.type is not None and ph.placeholder_format.type.name == "FOOTER":
                            self.assertEqual(ph.text_frame.text, NAME)

    def test_run_record_and_log(self):
        with open(self.log) as f:
            lines = [json.loads(l) for l in f]
        self.assertEqual(len(lines), 2)
        for template, (path, rec) in self.built.items():
            with self.subTest(template=template):
                self.assertEqual(rec["template"], template)
                self.assertTrue(rec["activated"])
                self.assertEqual(rec["activation_path"], ACT)
                self.assertFalse(rec["clarifying_question_asked"])
                self.assertFalse(rec["values_stale"])
                self.assertEqual(rec["routing_reason"], "test routing")
                self.assertTrue(rec["defaulted"])
                self.assertEqual(rec["output"], path)
                self.assertIn(template, rec["sources"])
                self.assertIn("guidelines", rec["sources"])
                self.assertEqual(rec["layouts_used"][4], "free-form:Title Only")
                self.assertEqual(len(rec["layouts_used"]), 6)
                self.assertIn("1 free-form slide", rec["notes"])
                with open(path + ".run.json") as f:
                    self.assertEqual(json.load(f), rec)

    def test_size(self):
        # Detailed View: 73 MB template -> < 10 MB. Executive Summary keeps its three masters' media (~11.3 MB).
        limits = {"detailed_view": 10e6, "executive_summary": 12e6}
        for template, (path, _) in self.built.items():
            with self.subTest(template=template):
                self.assertLess(os.path.getsize(path), limits[template])

    def check(self, path, template, *extra):
        return subprocess.run([sys.executable, "-P", os.path.join(SCRIPTS, "check_deck.py"), path, "--template",
                               template, "--deck-name", NAME] + list(extra), capture_output=True, text=True)

    def test_checker_passes(self):
        for template, (path, _) in self.built.items():
            with self.subTest(template=template):
                r = self.check(path, template, "--free-form-slides", "5", "--expect-slides", "6")
                self.assertIn("PASS", r.stdout)
                self.assertNotIn("FAIL", r.stdout, r.stdout)
                self.assertEqual(r.returncode, 0)

    def test_checker_flags_unlisted_free_slide(self):
        r = self.check(self.built["executive_summary"][0], "executive_summary")
        self.assertIn("FAIL No free shapes on any slide", r.stdout)
        self.assertIn("slide 5 on 'Title Only'", r.stdout)
        self.assertEqual(r.returncode, 1)

    def test_checker_wrong_template_theme_fails(self):
        r = self.check(self.built["executive_summary"][0], "detailed_view", "--free-form-slides", "5")
        self.assertIn("FAIL The deck's master-0 theme", r.stdout)
        self.assertEqual(r.returncode, 1)

    def test_checker_catches_off_brand_free_rectangle(self):
        prs = Presentation(self.built["executive_summary"][0])
        s = prs.slides[1]  # Three Column Panels: a named layout, not a free-form slide
        shp = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Pt(40), Pt(400), Pt(100), Pt(50))
        shp.name = "Off brand box"
        shp.fill.solid()
        shp.fill.fore_color.rgb = RGBColor(0xFF, 0x00, 0x00)
        for num in s._element.xpath('.//a:fld[@type="slidenum"]'):
            num.getparent().remove(num)
        path = os.path.join(self.tmp.name, "off-brand.pptx")
        prs.save(path)
        r = self.check(path, "executive_summary", "--free-form-slides", "5")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("slide 2 on 'Three Column Panels': 'Off brand box'", r.stdout)
        self.assertIn("colour FF0000", r.stdout)
        self.assertIn("FAIL A slide-number field", r.stdout)

    def test_checker_required_text_is_case_sensitive(self):
        path = self.built["executive_summary"][0]
        req = os.path.join(self.tmp.name, "required.txt")
        for lines, ok in ((["Thank  you", "[Lead]"], True), (["thank you"], False)):
            with open(req, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
            r = self.check(path, "executive_summary", "--free-form-slides", "5", "--required-text", req)
            self.assertEqual(r.returncode, 0 if ok else 1, r.stdout)
            self.assertIn(("PASS " if ok else "FAIL ") + "Every required text line", r.stdout)

    def test_checker_flags_prompt_and_filler_text(self):
        prs = Presentation(self.built["executive_summary"][0])
        prs.slides[1].shapes.title.text_frame.text = "Lorem ipsum dolor"
        prs.slides[2].shapes.title.text_frame.text = "Click to add title"
        path = os.path.join(self.tmp.name, "filler.pptx")
        prs.save(path)
        r = self.check(path, "executive_summary", "--free-form-slides", "5")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("FAIL No slide text contains 'Click to add' or 'Lorem ipsum'", r.stdout)
        self.assertIn("slide 2: 'Lorem ipsum dolor'", r.stdout)
        self.assertIn("slide 3: 'Click to add title'", r.stdout)
        self.assertIn("PASS No slide text contains", self.check(self.built["executive_summary"][0], "executive_summary",
                                                                 "--free-form-slides", "5").stdout)

    def test_checker_needs_template_and_deck_name(self):
        r = subprocess.run([sys.executable, "-P", os.path.join(SCRIPTS, "check_deck.py"),
                            self.built["executive_summary"][0]], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        self.assertIn("--template", r.stderr)

    def test_unknown_role_raises(self):
        d = Deck("executive_summary", NAME, activation_path=ACT)
        with self.assertRaisesRegex(ValueError, "Three Column Panels.*col1"):
            d.add("Three Column Panels", nope="x")
        self.assertEqual(d.roles("Three Column Panels")["lead"], 17)


class KitRulesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = Deck("executive_summary", NAME, activation_path=ACT)

    def test_activation_path_required(self):
        for bad in (None, "", "  "):
            with self.assertRaisesRegex(ValueError, "activation_path"):
                Deck("executive_summary", NAME, activation_path=bad)
        with self.assertRaises(ValueError):
            Deck("executive_summary", NAME)

    def test_missing_picture_raises_and_none_draws_box(self):
        with self.assertRaises(FileNotFoundError):
            self.d.add("Big statement with image - Light", title="[T]", pic1="/no/such/photo.jpg")
        s = self.d.add("Big statement with image - Light", title="[T]", pic1=None)
        self.assertIn("PHOTO: replace", [sh.name for sh in s.shapes])

    def test_chart_and_table_none_draw_replace_boxes(self):
        s = self.d.add("Single chart with supporting text", title="[T]", body="[x]", chart1=None)
        box = next(sh for sh in s.shapes if sh.name == "CHART: replace")
        self.assertEqual(str(box.fill.fore_color.rgb), "D9E8EC")
        run = box.text_frame.paragraphs[0].runs[0]
        self.assertEqual((run.text, str(run.font.color.rgb), run.font.size.pt), ("CHART: replace", "0C2B82", 10))
        self.assertFalse(any(sh.is_placeholder and sh.placeholder_format.type.name == "CHART" for sh in s.shapes))
        dv = Deck("detailed_view", NAME, activation_path=ACT)
        s = dv.add("ScoreCard", title="[T]", table1=None)
        self.assertIn("TABLE: replace", [sh.name for sh in s.shapes])

    def test_table_in_chart_placeholder_is_not_linked(self):
        s = self.d.add("Single chart with supporting text", title="[T]", body="[x]", chart1=TABLE)
        frame = next(sh for sh in s.shapes if sh.has_table)
        self.assertFalse(frame._element.xpath(".//p:nvPr/p:ph"))

    def test_duplicate_idx_raises(self):
        with self.assertRaisesRegex(ValueError, "idx 0"):
            self.d.add("Title Only", {"0": "[x]"}, title="[T]")

    def test_role_snapshots(self):
        for template in ("detailed_view", "executive_summary"):
            with self.subTest(template=template):
                with open(os.path.join(FIXTURES, "roles-%s.json" % template)) as f:
                    want = json.load(f)["layouts"]
                prs = Presentation(brand_sources.resolve([template])[template]["path"])
                got = {l.name: layout_roles(l) for l in prs.slide_masters[0].slide_layouts}
                self.assertEqual(got, want)
                self.assertTrue(all("title" in r for r in got.values()))

    def test_quarterly_performance_roles(self):
        roles = Deck("detailed_view", NAME, activation_path=ACT).roles("Quarterly Performance")
        self.assertNotIn("lead", roles)
        self.assertEqual([roles[k] for k in ("head1", "head2", "head3", "col1", "col2", "col3", "takeaway")],
                         [1, 3, 14, 13, 2, 15, 16])

    def test_stale_values_warn_and_log(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        with open(brand_sources.load_config()["values_file"]) as f:
            values = dict(json.load(f), guidelines_edition="May 2024")
        vpath = os.path.join(tmp, "values.json")
        with open(vpath, "w") as f:
            json.dump(values, f)
        env = {"NEWMONT_BRAND_VALUES": vpath, "NEWMONT_BRAND_LOG": os.path.join(tmp, "log.jsonl")}
        with mock.patch.dict(os.environ, env), mock.patch("sys.stderr", new_callable=io.StringIO) as err:
            d = Deck("executive_summary", NAME, activation_path=ACT, asked=True)
            d.add("Title Only", title="[T]")
            rec = d.save(os.path.join(tmp, "x.pptx"))
        self.assertIn("brand-values.json was digested from May 2024; the guidelines file is October 2025: "
                      "re-digest before trusting colours and chart rules", err.getvalue())
        self.assertTrue(rec["values_stale"])
        self.assertTrue(rec["clarifying_question_asked"])


class RenderTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)
        self.env = mock.patch.dict(os.environ, {"NEWMONT_BRAND_LOG": os.path.join(self.tmp, "log.jsonl")})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.d = Deck("executive_summary", NAME, activation_path=ACT)
        self.d.add("Title Only", title="[T]")
        self.d.add("Thank you Opt 1", title="Thank you")

    def test_missing_soffice_raises(self):
        with mock.patch("newmont_deck.shutil.which", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "soffice"):
                self.d.save(os.path.join(self.tmp, "deck", "x.pptx"), render=True)

    def test_render_pngs(self):
        if not shutil.which("soffice"):
            self.skipTest("LibreOffice 'soffice' is not on PATH: render test skipped")
        cwd_before = sorted(os.listdir(os.getcwd()))
        deck = os.path.join(self.tmp, "deck", "x.pptx")
        rec = self.d.save(deck, render=True)
        render = os.path.join(self.tmp, "deck", "render")
        self.assertEqual(rec["render"], [os.path.join(render, "x-page-%d.png" % n) for n in (1, 2)])
        for png in rec["render"]:
            with open(png, "rb") as f:
                self.assertEqual(f.read(8), b"\x89PNG\r\n\x1a\n")
        self.assertTrue(os.listdir(os.path.join(render, ".lo-profile")))
        self.assertEqual(sorted(os.listdir(os.getcwd())), cwd_before)
        with open(deck + ".run.json") as f:
            self.assertEqual(json.load(f)["render"], rec["render"])


class MissingSourceTest(unittest.TestCase):
    def test_empty_sources_dir_raises(self):
        with tempfile.TemporaryDirectory() as empty, mock.patch.dict(os.environ, {"NEWMONT_BRAND_SOURCES": empty}):
            with self.assertRaises(brand_sources.SourceError):
                Deck("detailed_view", NAME, activation_path=ACT)


if __name__ == "__main__":
    unittest.main()
