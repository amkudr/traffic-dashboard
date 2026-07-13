import json, os

repos = ["surf-tracker", "Star-Wars-Simulator", "Public-transport-network", "Google-Project"]

views_combined  = {}
clones_combined = {}

for repo in repos:
    views_file  = f"traffic-data/{repo}-views.json"
    clones_file = f"traffic-data/{repo}-clones.json"

    if os.path.exists(views_file):
        with open(views_file) as f:
            data = json.load(f)
        views_combined[repo] = {
            "count":   data.get("count",   0),
            "uniques": data.get("uniques", 0),
            "views":   data.get("views",   [])
        }

    if os.path.exists(clones_file):
        with open(clones_file) as f:
            data = json.load(f)
        clones_combined[repo] = {
            "count":   data.get("count",   0),
            "uniques": data.get("uniques", 0),
            "clones":  data.get("clones",  [])
        }

with open("docs/data.json", "w") as f:
    json.dump(views_combined, f, indent=2)

with open("docs/clones.json", "w") as f:
    json.dump(clones_combined, f, indent=2)

print(f"Exported {len(views_combined)} repos -> docs/data.json")
print(f"Exported {len(clones_combined)} repos -> docs/clones.json")