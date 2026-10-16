"""Evaluate rule coverage against explicitly planted sample flaws."""

import json
from pathlib import Path

from prdiq.rules import review_prd


SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_data"


def evaluate() -> list[dict[str, object]]:
    planted = json.loads((SAMPLE_DIR / "planted_flaws.json").read_text(encoding="utf-8"))
    rows = []
    for filename, expected_ids in planted.items():
        text = (SAMPLE_DIR / filename).read_text(encoding="utf-8")
        reported_ids = {finding.check_id for finding in review_prd(text).findings}
        expected = set(expected_ids)
        rows.append({
            "sample": filename,
            "planted": len(expected),
            "found": len(expected & reported_ids),
            "missed": sorted(expected - reported_ids),
            "false_alarms": sorted(reported_ids - expected),
        })
    return rows


def main() -> None:
    rows = evaluate()
    for row in rows:
        print(f"{row['sample']}: {row['found']}/{row['planted']} planted flaws found")
        print(f"  missed: {row['missed'] or 'none'}")
        print(f"  false alarms: {row['false_alarms'] or 'none'}")
    found = sum(int(row["found"]) for row in rows)
    planted_count = sum(int(row["planted"]) for row in rows)
    false_alarms = sum(len(row["false_alarms"]) for row in rows)
    print(f"Total: {found}/{planted_count} planted flaws found; {false_alarms} false alarms")
    print("These are author-created fixtures, not a held-out or real-world accuracy estimate.")


if __name__ == "__main__":
    main()