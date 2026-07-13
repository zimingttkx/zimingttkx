#!/usr/bin/env python3
"""Generate a star history chart for zimingttkx's public repos."""
import csv, subprocess, sys
from datetime import date
from pathlib import Path

OWNER = "zimingttkx"
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_DIR = SCRIPT_DIR.parent
ASSETS = REPO_DIR / "assets"
CSV_PATH = REPO_DIR / "star-history.csv"
CHART_PATH = ASSETS / "star-history.png"


def fetch_stars() -> int:
    """Fetch total stars across all non-fork repos (single API call)."""
    result = subprocess.run(
        ["gh", "api", f"users/{OWNER}/repos",
         "--jq", "[.[] | select(.fork == false) | .stargazers_count] | add // 0",
         "--paginate"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"Warning: failed to fetch stars: {result.stderr}", file=sys.stderr)
        return 0
    return int(result.stdout.strip())


def read_history() -> list[tuple[str, int]]:
    """Read existing star history CSV, return list of (date, stars) tuples."""
    if not CSV_PATH.exists():
        return []
    rows = []
    with open(CSV_PATH, newline="") as f:
        for d, s in csv.reader(f):
            rows.append((d, int(s)))
    return rows


def append_today(rows: list, total: int) -> list:
    today = date.today().isoformat()
    if rows and rows[-1][0] == today:
        rows[-1] = (today, total)  # update today's entry
    else:
        rows.append((today, total))
    return rows


def save_csv(rows: list):
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)


def draw_chart(rows: list):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from datetime import datetime

    # Nature/Science journal style
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "axes.unicode_minus": False,
    })

    dates = [datetime.strptime(r[0], "%Y-%m-%d") for r in rows]
    stars = [r[1] for r in rows]

    fig, ax = plt.subplots(figsize=(7, 2.6))

    # Clean white background
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    color = "#2166AC"
    ax.fill_between(dates, stars, alpha=0.08, color=color)
    ax.plot(dates, stars, color=color, linewidth=1.2, solid_capstyle="round")

    # Thin spines — bottom & left only, journal convention
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.spines["bottom"].set_visible(True)
    ax.spines["bottom"].set_color("#999999")
    ax.spines["bottom"].set_linewidth(0.5)
    ax.spines["left"].set_visible(True)
    ax.spines["left"].set_color("#999999")
    ax.spines["left"].set_linewidth(0.5)

    # Ticks
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax.tick_params(axis="x", colors="#666666", labelsize=8, length=0, pad=4)
    ax.tick_params(axis="y", colors="#666666", labelsize=8, length=0, pad=4)

    # Subtle horizontal gridlines
    ax.yaxis.set_major_locator(plt.MaxNLocator(5))
    ax.grid(axis="y", color="#E0E0E0", linewidth=0.4, linestyle="-")

    ax.set_ylabel("Stars", color="#444444", fontsize=9, labelpad=6)
    ax.set_xlabel("")

    # Tight science-style margins
    ax.margins(x=0.01, y=0.08)

    plt.tight_layout(pad=0.3)
    ASSETS.mkdir(exist_ok=True)
    fig.savefig(str(CHART_PATH), dpi=200, facecolor="white", edgecolor="none", bbox_inches="tight")
    plt.close(fig)
    print(f"Chart saved to {CHART_PATH}")


def main():
    total = fetch_stars()
    print(f"Total stars: {total}")
    rows = read_history()
    rows = append_today(rows, total)
    save_csv(rows)
    draw_chart(rows)


if __name__ == "__main__":
    main()
