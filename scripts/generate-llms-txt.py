#!/usr/bin/env python3
"""
Generates dist/llms.txt for the aggregated docs site.
"""
import os
import yaml
from collections import defaultdict

BASE_URL = "https://nondualworks.github.io/docspine-demo"


def main():
    dist_dir = "dist"
    registry_file = "docs-registry.yaml"

    with open(registry_file) as f:
        registry = yaml.safe_load(f)

    repos = registry.get("repos", [])

    lines = [
        "# Docspine Demo — Documentation Hub",
        f"> Aggregated documentation for registered services. Built with Docspine.",
        "",
    ]

    groups = defaultdict(list)
    for repo in repos:
        groups[repo.get("domain", "other")].append(repo)

    for domain in sorted(groups.keys()):
        lines.append(f"## {domain.title()}")
        for repo in groups[domain]:
            service = repo["service"]
            nav_title = repo.get("nav_title", service)
            url = f"{BASE_URL}/{domain}/{service}/"
            lines.append(f"- [{nav_title}]({url})")
        lines.append("")

    os.makedirs(dist_dir, exist_ok=True)
    out = os.path.join(dist_dir, "llms.txt")
    with open(out, "w") as f:
        f.write("\n".join(lines))
    print(f"✓ llms.txt generated at {out}")


if __name__ == "__main__":
    main()
