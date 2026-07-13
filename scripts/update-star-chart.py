#!/usr/bin/env python3
"""Generate a star history chart for zimingttkx's public repos."""
import json, os, csv, subprocess, sys
from datetime import date
from pathlib import Path

REPOS = [
    "AI-Practices", "ConcurrentCache", "Network-Security-Based-On-ML",
    "PaperWritingSkills", "QuantumFlow", "WebServer", "zimingttkx"
]
OWNER = "zimingttkx"
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_DIR = SCRIPT_DIR.parent
ASSETS = REPO_DIR / "assets"
CSV_PATH = REPO_DIR / "star-history.csv"
CHART_PATH = ASSETS / "star-history.png"


def fetch_stars() -> int:
    """Fetch total stars across all non-fork repos using gh CLI."""
    total = 0
    for repo in REPOS:
        result = subprocess.run(
            ["gh", "api", f"repos/{OWNER}/{repo}", "--jq", ".stargazers_count"],
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            total += int(result.stdout.strip())
        else:
            print(f"Warning: failed to fetch {repo}: {result.stderr}", file=sys.stderr)
    return total


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

    dates = [datetime.strptime(r[0], "%Y-%m-%d") for r in rows]
    stars = [r[1] for r in rows]

    fig, ax = plt.subplots(figsize=(8, 3))

    # Dark background to blend well on GitHub dark mode
    fig.patch.set_facecolor("#0D1117")
    ax.set_facecolor("#0D1117")

    color = "#3B82F6"
    ax.fill_between(dates, stars, alpha=0.15, color=color)
    ax.plot(dates, stars, color=color, linewidth=2, marker="o", markersize=4,
            markerfacecolor=color, markeredgewidth=0)

    # Formatting
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.tick_params(colors="#8B949E", labelsize=9)
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.set_ylabel("Total Stars", color="#C9D1D9", fontsize=10)
    ax.set_xlabel("")
    ax.grid(axis="y", color="#21262D", linewidth=0.5)
    ax.tick_params(axis="x", colors="#8B949E")

    # Annotate last value
    if len(stars) >= 1:
        ax.annotate(
            str(stars[-1]),
            (dates[-1], stars[-1]),
            textcoords="offset points", xytext=(8, -6),
            color=color, fontsize=12, fontweight="bold",
        )

    plt.tight_layout(pad=0.5)
    ASSETS.mkdir(exist_ok=True)
    fig.savefig(str(CHART_PATH), dpi=150, facecolor=fig.get_facecolor(), edgecolor="none")
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
