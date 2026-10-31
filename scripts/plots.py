"""Standalone SVG plots from retained numeric analysis; no installs."""

from html import escape
from pathlib import Path

from factuality_uncertainty.io import load

ROOT = Path(__file__).resolve().parents[1]
COLORS = ["#2563eb", "#dc2626", "#0f766e"]


def chart(title, xlabel, ylabel, series, note, output, diagonal=False):
    def x(v): return 80 + v * 640
    def y(v): return 420 - v * 350
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="760" height="500" viewBox="0 0 760 500" role="img">',
             f'<title>{escape(title)}</title><rect width="100%" height="100%" fill="white"/>',
             f'<text x="30" y="30" font-family="sans-serif" font-size="18">{escape(title)}</text>']
    for i in range(6):
        v = i / 5
        parts.extend([f'<path d="M80 {y(v)}H720" stroke="#ddd"/>',
                      f'<text x="45" y="{y(v)+4}" font-family="sans-serif" font-size="12">{v:.1f}</text>',
                      f'<text x="{x(v)-10}" y="442" font-family="sans-serif" font-size="12">{v:.1f}</text>'])
    if diagonal:
        parts.append('<path d="M80 420L720 70" stroke="#999" stroke-dasharray="4 4"/>')
    for i, (label, points) in enumerate(series):
        color = COLORS[i]
        xy = " ".join(f"{x(a):.2f},{y(b):.2f}" for a, b in points)
        parts.append(f'<polyline points="{xy}" fill="none" stroke="{color}" stroke-width="2"/>')
        parts.extend(f'<circle cx="{x(a):.2f}" cy="{y(b):.2f}" r="4" fill="{color}"/>' for a, b in points)
        parts.append(f'<text x="440" y="{55+i*20}" fill="{color}" font-family="sans-serif" font-size="12">{escape(label)}</text>')
    parts.extend([f'<text x="390" y="465" text-anchor="middle" font-family="sans-serif" font-size="14">{escape(xlabel)}</text>',
                  f'<text transform="translate(20 250) rotate(-90)" text-anchor="middle" font-family="sans-serif" font-size="14">{escape(ylabel)}</text>',
                  f'<text x="30" y="490" font-family="sans-serif" font-size="10">{escape(note)}</text>', '</svg>'])
    path = ROOT / "reports/figures" / output
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists(): raise ValueError("preserve_original_plot")
    path.write_text("\n".join(parts) + "\n")


def main():
    a = load(ROOT / "reports/main/analysis.json")
    summary = a["summaries"]["test:abstention"]
    series = [(name, [(b["mean_probability"], b["accuracy"]) for b in summary[key]["bins"] if b["count"]])
              for name, key in [("Raw confidence", "raw_calibration"), ("Held-out histogram map", "empirical_calibration")]]
    chart("AI-02 synthetic test reliability", "Mean predicted correctness probability", "Observed correctness fraction", series,
          "Fixed bins; invented templates; no uncertainty bars or population calibration guarantee.", "reliability.svg", True)
    for split in ["test", "shift"]:
        series = [(arm, [(p["coverage"], p["risk"]) for p in a["risk_coverage"][split+":"+arm]])
                  for arm in ["retrieval", "literal", "abstention"]]
        chart("AI-02 synthetic " + split + " risk coverage", "Fraction of scheduled questions answered", "Error fraction among selected questions", series,
              "Ranking diagnostic, including thresholds beyond operating acceptance. Shift calibration unavailable.", "risk-coverage-"+split+".svg")


if __name__ == "__main__": main()
