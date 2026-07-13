import json, os
from datetime import datetime, timezone

repos = ["surf-tracker", "Star-Wars-Simulator", "Public-transport-network", "Google-Project"]

HISTORY_FILE = "traffic-data/history.json"

# ── Load existing history ────────────────────────────────────────────────────
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE) as f:
        history = json.load(f)
else:
    history = {}

# history schema:
# {
#   "<repo>": {
#     "views":  { "<timestamp>": {"count": N, "uniques": N} },
#     "clones": { "<timestamp>": {"count": N, "uniques": N} }
#   }
# }

def merge_entries(existing_dict, new_entries):
    """Merge a list of {timestamp, count, uniques} entries into a dict keyed by timestamp.
    Newer data from the API wins (GitHub can revise counts within the 14-day window).
    GitHub occasionally returns today's partial-day data with tomorrow's UTC date; we
    remap any future timestamp back to today so it is stored and displayed correctly."""
    today_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00Z")
    for entry in new_entries:
        ts = entry["timestamp"]
        # Remap any future-dated entry to today
        if ts > today_ts:
            ts = today_ts
        # Merge: accumulate counts if key already exists (could be same day, different source)
        if ts in existing_dict:
            existing_dict[ts]["count"]   += entry["count"]
            existing_dict[ts]["uniques"] = max(existing_dict[ts]["uniques"], entry["uniques"])
        else:
            existing_dict[ts] = {"count": entry["count"], "uniques": entry["uniques"]}
    return existing_dict

# ── Merge new API data into history ─────────────────────────────────────────
for repo in repos:
    if repo not in history:
        history[repo] = {"views": {}, "clones": {}}

    views_file  = f"traffic-data/{repo}-views.json"
    clones_file = f"traffic-data/{repo}-clones.json"

    if os.path.exists(views_file):
        with open(views_file) as f:
            data = json.load(f)
        history[repo]["views"] = merge_entries(history[repo]["views"], data.get("views", []))

    if os.path.exists(clones_file):
        with open(clones_file) as f:
            data = json.load(f)
        history[repo]["clones"] = merge_entries(history[repo]["clones"], data.get("clones", []))

# ── Persist updated history ──────────────────────────────────────────────────
with open(HISTORY_FILE, "w") as f:
    json.dump(history, f, indent=2, sort_keys=True)

print(f"History saved -> {HISTORY_FILE}")

# ── Build docs/data.json and docs/clones.json from full history ──────────────
views_combined  = {}
clones_combined = {}

for repo in repos:
    repo_hist = history.get(repo, {"views": {}, "clones": {}})

    # Sort entries by timestamp (ascending)
    views_entries = sorted(
        [{"timestamp": ts, **vals} for ts, vals in repo_hist["views"].items()],
        key=lambda x: x["timestamp"]
    )
    clones_entries = sorted(
        [{"timestamp": ts, **vals} for ts, vals in repo_hist["clones"].items()],
        key=lambda x: x["timestamp"]
    )

    total_views   = sum(e["count"]   for e in views_entries)
    unique_views  = sum(e["uniques"] for e in views_entries)
    total_clones  = sum(e["count"]   for e in clones_entries)
    unique_clones = sum(e["uniques"] for e in clones_entries)

    views_combined[repo] = {
        "count":   total_views,
        "uniques": unique_views,
        "views":   views_entries
    }
    clones_combined[repo] = {
        "count":   total_clones,
        "uniques": unique_clones,
        "clones":  clones_entries
    }

with open("docs/data.json", "w") as f:
    json.dump(views_combined, f, indent=2)

with open("docs/clones.json", "w") as f:
    json.dump(clones_combined, f, indent=2)

print(f"Exported {len(views_combined)} repos -> docs/data.json")
print(f"Exported {len(clones_combined)} repos -> docs/clones.json")