import json, os, glob

repos = ["surf-tracker", "Star-Wars-Simulator", "Public-transport-network", "Google-Project"]
combined = {}

for repo in repos:
    views_file = f"traffic-data/{repo}-views.json"
    if os.path.exists(views_file):
        with open(views_file) as f:
            data = json.load(f)
        combined[repo] = {
            "count": data.get("count", 0),
            "uniques": data.get("uniques", 0),
            "views": data.get("views", [])
        }

with open("docs/data.json", "w") as f:
    json.dump(combined, f, indent=2)