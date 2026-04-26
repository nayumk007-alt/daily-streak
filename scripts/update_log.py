#!/usr/bin/env python3
"""Append today's entry to daily_log.md if not already present.

Exit codes:
    0  - wrote a new entry (workflow should commit & push)
    78 - already logged today (workflow should skip commit)
    >0 - unexpected error
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

LOG_FILE = Path("daily_log.md")
HEADER = "# Daily Activity Log\n"


def _resolve_tz(name: str):
    # On Linux runners (the Actions environment) IANA tzdata is always present.
    # On Windows local dev it's missing unless `pip install tzdata` was run, so
    # degrade to UTC instead of crashing.
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError:
        print(f"[warn] tz '{name}' unavailable locally; falling back to UTC",
              file=sys.stderr)
        return timezone.utc


TZ = _resolve_tz(os.environ.get("STREAK_TZ", "UTC"))


def already_logged_today(content: str, date_str: str) -> bool:
    return f"## {date_str}" in content


def build_entry(date_str: str, time_str: str, note: str) -> str:
    note = note.strip() or "Automated daily checkpoint."
    return (
        f"\n## {date_str}\n"
        f"- **Time:** {time_str}\n"
        f"- **Note:** {note}\n"
    )


def main() -> int:
    now = datetime.now(TZ)
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S %Z")
    note = os.environ.get("STREAK_NOTE", "")

    if not LOG_FILE.exists():
        LOG_FILE.write_text(HEADER, encoding="utf-8")

    content = LOG_FILE.read_text(encoding="utf-8")
    if already_logged_today(content, date_str):
        print(f"[skip] {date_str} already logged")
        return 78

    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(build_entry(date_str, time_str, note))
    print(f"[ok] appended entry for {date_str}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
