#!/usr/bin/env python3
"""Backfill star history using GitHub stargazers API with timestamps."""
import json, csv, subprocess, sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path

REPOS = [
    "AI-Practices", "ConcurrentCache", "Network-Security-Based-On-ML",
    "PaperWritingSkills", "QuantumFlow", "WebServer", "zimingttkx"
]
OWNER = "zimingttkx"
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_DIR = SCRIPT_DIR.parent
CSV_PATH = REPO_DIR / "star-history.csv"


def fetch_stargazers(repo: str) -> list[str]:
    """Fetch all starred_at dates for a repo using gh api with pagination."""
    dates = []
    # Use star+json media type which includes starred_at timestamps
    result = subprocess.run(
        ["gh", "api", f"repos/{OWNER}/{repo}/stargazers",
         "--jq", ".[].starred_at",
         "--paginate",
         "-H", "Accept: application/vnd.github.v3.star+json"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"Error fetching {repo}: {result.stderr}", file=sys.stderr)
        return dates
    for line in result.stdout.strip().split("\n"):
        line = line.strip()
        if line:
            dates.append(line[:10])  # YYYY-MM-DD
    return dates


def main():
    all_dates = []
    for repo in REPOS:
        print(f"Fetching {repo}...")
        dates = fetch_stargazers(repo)
        print(f"  -> {len(dates)} stars")
        all_dates.extend(dates)

    # Count stars per day
    daily = Counter(all_dates)
    sorted_days = sorted(daily.keys())

    # Cumulative count
    cumulative = []
    running = 0
    for d in sorted_days:
        running += daily[d]
        cumulative.append((d, running))

    print(f"\nTotal stars from API: {running}")
    print(f"Date range: {sorted_days[0]} -> {sorted_days[-1]}")
    print(f"Data points: {len(cumulative)}")

    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(cumulative)
    print(f"\nSaved to {CSV_PATH}")


if __name__ == "__main__":
    main()
