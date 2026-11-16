import os, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
from route_template import route

DV, ES = "detailed_view", "executive_summary"


class RouteTest(unittest.TestCase):
    def check(self, text, template, ask=False, unattended=False, explicit=False, defaulted=False):
        r = route(text, unattended)
        self.assertEqual((r["template"], r["ask"], r["explicit"], r["defaulted"]),
                         (template, ask, explicit, defaulted), "%r -> %r" % (text, r))
        self.assertTrue(r["reason"].endswith("."))
        return r

    # rule 1: explicit
    def test_explicit_detailed_overrides_cues(self):
        self.check("use the detailed view template for the town hall", DV, explicit=True)

    def test_explicit_exec(self):
        self.check("QBR deck but use the executive summary template", ES, explicit=True)

    def test_explicit_exec_short(self):
        self.check("put the scorecard in the exec template", ES, explicit=True)

    def test_explicit_detailed_template(self):
        self.check("a strategy deck on the detailed template", DV, explicit=True)

    # rules 2-3: one side matched
    def test_qbr(self):
        r = self.check("put this into slides for the QBR", DV)
        self.assertIn("QBR", r["reason"])

    def test_tailings_strategy(self):
        r = self.check("a deck explaining our tailings strategy", ES)
        self.assertIn("strategy", r["matched"][ES])

    def test_plural_and_possessive(self):
        self.check("Q3 dividends and the earnings' outlook", DV)
        self.check("our 2026 strategies and Newmont's roadmaps", ES)

    def test_word_boundary(self):
        self.check("a deck on the explanation of planets", None, ask=True)  # no 'plan' / 'explain' inside words

    def test_outlook_is_weak(self):
        self.check("an outlook deck", None, ask=True)
        r = self.check("scorecard and outlook", DV)
        self.assertEqual(r["matched"][DV], ["scorecard", "outlook"])

    def test_plan_inside_detailed_cue_does_not_count(self):
        self.check("performance against plan for Boddington", DV)

    def test_people_and_ir(self):
        self.check("headcount and labour relations update", DV)
        self.check("investor relations slides", DV)

    def test_exec_cues(self):
        self.check("onboarding training for new geologists", ES)
        self.check("all-hands vision presentation", ES)

    def test_explicit_needs_template_or_layout(self):
        r = self.check("a detailed view of our strategy", ES)
        self.assertEqual(r["matched"][ES], ["strategy"])
        self.check("detailed view layout please", DV, explicit=True)
        self.check("use the executive summary template for the scorecard", ES, explicit=True)

    def test_performance_cues(self):
        r = self.check("put together a newmont deck on our Q3 safety performance for the exec team", DV)
        self.assertIsNone(r["question"])
        self.check("Q3 performance overview for the board", DV)
        self.check("ops review dashboard", DV)

    def test_exec_weak_cues_yield_to_detailed(self):
        for text in ("QBR deck with the plan for Q4", "scorecard comparison across sites",
                     "investor relations update on our approach", "people update for the town hall"):
            r = self.check(text, DV, unattended=True)
            self.assertEqual(r["matched"][ES], [], text)

    # rule 4: both / neither
    def test_project_progress_update_asks(self):
        r = self.check("project progress update deck", None, ask=True)
        self.assertEqual((r["matched"][DV], r["matched"][ES]), (["progress update"], ["project update"]))
        self.assertIn("Detailed View", r["question"])
        self.assertIn("Executive Summary", r["question"])

    def test_bare_deck_asks(self):
        r = self.check("a deck", None, ask=True)
        self.assertIn("no template cue matched", r["reason"])

    def test_unattended_neither_defaults(self):
        r = self.check("a deck", ES, unattended=True, defaulted=True)
        self.assertIsNone(r["question"])
        self.assertIn("no template cue matched", r["reason"])

    def test_unattended_both_defaults_and_lists_cues(self):
        r = self.check("strategy and scorecard deck", ES, unattended=True, defaulted=True)
        self.assertIn("scorecard", r["reason"])
        self.assertIn("strategy", r["reason"])

    def test_both_templates_named_asks(self):
        self.check("detailed view or executive summary template?", None, ask=True)


if __name__ == "__main__":
    unittest.main()


class TestBareWords(unittest.TestCase):
    def test_monitoring_results_in_strategy_deck_is_exec(self):
        r = route("a strategy deck on how we publish the monitoring results")
        self.assertEqual(r["template"], "executive_summary"); self.assertFalse(r["ask"])
