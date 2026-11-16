#!/usr/bin/env python3
"""Build one placeholder-content demo deck per template, check it, render pages 1-4 to PNG.
Usage: python3 demo_build.py [out_dir]   (default: <repo>/out). Needs LibreOffice (soffice) and pymupdf."""
import os, shutil, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from newmont_deck import Deck, rect, text

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(HERE), "out"))
NAME, DATE = "Newmont - [Deck name]", "[Month Year]"
BULLETS = ["[Key point]", ("[Supporting detail]", 1), [("[Bold lead-in] ", True, False), ("[rest of point]", False, False)]]
CHART = {"type": "column", "categories": ["[Q1]", "[Q2]", "[Q3]", "[Q4]"],
         "series": {"[Series A]": [1, 2, 3, 4], "[Series B]": [2, 3, 2, 3]}, "title": "[Chart title]"}
PIE = {"type": "pie", "categories": ["[A]", "[B]", "[C]"], "series": {"[Share]": [1, 1, 1]}}
TABLE = {"header": ["[Metric]", "[Plan]", "[Actual]"], "rows": [["[Row]", "0.0", "0.0"], ["[Row]", "0.0", "0.0"]]}


def free(d):
    s = d.free_slide("[Process title]")
    for n in range(3):
        rect(s, 36 + n * 300, 150, 280, 90, "D9E8EC")
        text(s, 48 + n * 300, 160, 256, 70, ["[Step %d]" % (n + 1), "[Description]"], size=12, color="0C2B82")


def executive(path):
    d = Deck("executive_summary", NAME, DATE, request="demo build", activation_path="direct: demo")
    d.add("1_Cover slide Opt 1", title="[Presentation title]", subtitle="[Presenter | Month Year]")
    d.add("Three Column Panels", title="[Slide title]", lead="[Lead-in sentence]",
          col1=BULLETS, col2=BULLETS, col3=BULLETS, source="Source: [source]")
    d.add("Single chart with supporting text", title="[Slide title]", body=BULLETS, head1="[Chart heading]", chart1=CHART)
    d.add("Title and Content", title="[Slide title]", body=TABLE)
    free(d)
    d.add("Thank you Opt 1", title="Thank you")
    return d.save(path)


def detailed(path):
    d = Deck("detailed_view", NAME, DATE, request="demo build", activation_path="direct: demo")
    d.add("1_Cover slide Opt 1b", title="[Presentation title]", subtitle="[Presenter | Month Year]")
    d.add("Highlights, Risks & Mitigations", title="[Slide title]", head1="[Lead-in]", head2="[Highlights]",
          head3="[Risks & mitigations]", col1=BULLETS, col2=BULLETS)
    d.add("ScoreCard", title="[Slide title]", head1="[Table heading]", head2="[Table heading]", table1=TABLE,
          table2=TABLE, head3="[Chart heading]", head4="[Commentary]", head5="[Chart heading]", body=BULLETS,
          chart1=CHART, chart2=PIE, chart3=CHART, chart4=PIE)
    d.add("Title and Content", title="[Slide title]", body=TABLE)
    free(d)
    d.add("Thank you Opt 1", title="Thank you")
    return d.save(path)


def main():
    soffice = shutil.which("soffice")
    if not soffice:
        sys.exit("demo_build.py needs LibreOffice: no 'soffice' on PATH (install it or add it to PATH).")
    for key, build in (("executive_summary", executive), ("detailed_view", detailed)):
        stem = "demo-" + key.replace("_", "-")
        pptx = os.path.join(OUT, stem + ".pptx")
        rec = build(pptx)
        print("%s  %.1f MB  layouts: %s" % (pptx, os.path.getsize(pptx) / 1e6, ", ".join(rec["layouts_used"])))
        subprocess.run([sys.executable, "-P", os.path.join(HERE, "check_deck.py"), pptx, "--template", key,
                        "--deck-name", NAME, "--free-form-slides", "5", "--expect-slides", "6"], check=True)
        subprocess.run([soffice, "--headless", "--convert-to", "pdf",
                        "--outdir", OUT, pptx], check=True, capture_output=True)
        import pymupdf
        png_dir = os.path.join(OUT, stem)
        os.makedirs(png_dir, exist_ok=True)
        with pymupdf.open(os.path.join(OUT, stem + ".pdf")) as doc:
            for i in range(min(4, doc.page_count)):
                png = os.path.join(png_dir, "page-%d.png" % (i + 1))
                doc[i].get_pixmap(dpi=80).save(png)
                print("  " + png)


if __name__ == "__main__":
    main()
