#!/usr/bin/env python3
"""
Generates dist/index.html from docs-registry.yaml.
Groups services by domain with links and Pagefind search.
"""
import os
import yaml
from collections import defaultdict


def main():
    dist_dir = "dist"
    registry_file = "docs-registry.yaml"

    with open(registry_file) as f:
        registry = yaml.safe_load(f)

    repos = registry.get("repos", [])
    routing = registry.get("routing", {})
    group_by = routing.get("group_by", "domain")

    groups = defaultdict(list)
    for repo in repos:
        key = repo.get(group_by, repo.get("domain", "other"))
        groups[key].append(repo)

    services_html = ""
    for group_key in sorted(groups.keys()):
        services_html += f'  <div class="domain-group">\n'
        services_html += f'    <div class="domain-name">{group_key}</div>\n'
        services_html += f'    <ul class="service-list">\n'
        for repo in groups[group_key]:
            service = repo["service"]
            domain = repo["domain"]
            nav_title = repo.get("nav_title", service)
            team = repo.get("team", "")
            href = f"{domain}/{service}/"
            services_html += f'      <li><a href="{href}">{nav_title}</a>'
            if team:
                services_html += f'<span class="team-badge">{team}</span>'
            services_html += "</li>\n"
        services_html += "    </ul>\n  </div>\n"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Docspine Demo — Documentation Hub</title>
  <link href="_pagefind/pagefind-ui.css" rel="stylesheet">
  <style>
    body {{ font-family: system-ui, -apple-system, sans-serif; max-width: 800px; margin: 2rem auto; padding: 0 1rem; color: #1a1a1a; }}
    h1 {{ margin-bottom: 0.25rem; }}
    .subtitle {{ color: #666; margin-bottom: 2rem; }}
    .domain-group {{ margin-bottom: 1.5rem; }}
    .domain-name {{ font-size: 0.85rem; font-weight: 600; color: #555; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.5rem; }}
    .service-list {{ list-style: none; padding: 0; margin: 0; }}
    .service-list li {{ padding: 0.35rem 0; }}
    .service-list a {{ color: #2563eb; text-decoration: none; font-weight: 500; }}
    .service-list a:hover {{ text-decoration: underline; }}
    .team-badge {{ font-size: 0.75rem; color: #888; margin-left: 0.5rem; }}
    .powered-by {{ margin-top: 3rem; font-size: 0.8rem; color: #aaa; }}
    .powered-by a {{ color: #aaa; }}
    hr {{ border: none; border-top: 1px solid #eee; margin: 2rem 0; }}
  </style>
</head>
<body>
  <h1>Documentation Hub</h1>
  <p class="subtitle">A live demo of <a href="https://nondualworks.github.io/docspine">Docspine</a> — federated docs aggregated from independent repos.</p>
  <div id="search"></div>
  <script src="_pagefind/pagefind-ui.js"></script>
  <script>new PagefindUI({{ element: "#search", showSubResults: true }});</script>
  <hr>
  <h2>Services</h2>
{services_html}
  <p class="powered-by">Aggregated with <a href="https://nondualworks.github.io/docspine">Docspine</a></p>
</body>
</html>
"""

    os.makedirs(dist_dir, exist_ok=True)
    with open(os.path.join(dist_dir, "index.html"), "w") as f:
        f.write(html)
    print(f"✓ Landing page generated at {dist_dir}/index.html")


if __name__ == "__main__":
    main()
