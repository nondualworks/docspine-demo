#!/usr/bin/env python3
"""
Generates dist/llms.txt for the aggregated docs site.
Reads from _build/services.json (written by aggregate.py).
Falls back to parsing docs-registry.yaml directly for local runs before aggregation.
"""
import json
import os
import yaml
from collections import defaultdict

BASE_URL = "https://nondualworks.github.io/docspine-demo"
SERVICES_JSON = os.path.join("_build", "services.json")
REGISTRY_FILE = "docs-registry.yaml"


def load_services():
    if os.path.exists(SERVICES_JSON):
        with open(SERVICES_JSON) as f:
            return json.load(f)

    # Fallback: derive service list from docs-registry.yaml
    # This only has id/domain stubs — no team or page count
    print(f"  (services.json not found, falling back to {REGISTRY_FILE})")
    with open(REGISTRY_FILE) as f:
        registry = yaml.safe_load(f)

    services = []
    for repo_entry in registry.get("repos", []):
        for svc_entry in repo_entry.get("services", []):
            docs_path = svc_entry["docs_path"]
            services.append({
                "id": docs_path,
                "name": docs_path.replace("-", " ").title(),
                "domain": "",
                "team": "",
                "pages": 0,
                "diataxis": [],
            })
    return services


def main():
    dist_dir = "dist"
    services = load_services()

    lines = [
        "# Docspine Demo — Documentation Hub",
        "> Aggregated documentation for registered services. Built with Docspine.",
        "",
    ]

    groups = defaultdict(list)
    for svc in services:
        groups[svc.get("domain") or "other"].append(svc)

    for domain in sorted(groups.keys()):
        lines.append(f"## {domain.title()}")
        for svc in groups[domain]:
            name = svc.get("name") or svc["id"]
            url = f"{BASE_URL}/{domain}/{svc['id']}/"
            lines.append(f"- [{name}]({url})")
        lines.append("")

    os.makedirs(dist_dir, exist_ok=True)
    out = os.path.join(dist_dir, "llms.txt")
    with open(out, "w") as f:
        f.write("\n".join(lines))
    print(f"✓ llms.txt generated at {out} ({len(services)} services)")


if __name__ == "__main__":
    main()
