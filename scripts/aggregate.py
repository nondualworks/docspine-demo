#!/usr/bin/env python3
"""
Docspine aggregation script.
Reads docs-registry.yaml (repo→services hierarchy), clones each repo once,
builds each service's docs, copies output to dist/, and writes _build/services.json.
"""
import json
import os
import shutil
import subprocess
import sys
import yaml


def run(cmd, cwd=None):
    print(f"  $ {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    if result.returncode != 0:
        print(f"  ✗ Command failed (exit {result.returncode})", file=sys.stderr)
        sys.exit(result.returncode)


def repo_slug(url):
    """Derive a filesystem-safe slug from a git URL.
    e.g. https://github.com/nondualworks/docspine-demo-commerce.git → docspine-demo-commerce
    """
    name = url.rstrip("/").split("/")[-1]
    if name.endswith(".git"):
        name = name[:-4]
    return name


def main():
    dist_dir = "dist"
    build_dir = "_build"
    registry_file = "docs-registry.yaml"

    with open(registry_file) as f:
        registry = yaml.safe_load(f)

    routing = registry.get("routing", {})
    group_by = routing.get("group_by", "domain")
    repos = registry.get("repos", [])

    os.makedirs(dist_dir, exist_ok=True)
    os.makedirs(build_dir, exist_ok=True)

    all_services = []

    for repo_entry in repos:
        url = repo_entry["url"]
        branch = repo_entry.get("branch", "main")
        services = repo_entry.get("services", [])

        slug = repo_slug(url)
        clone_dest = os.path.join(build_dir, slug)

        print(f"\n→ Cloning {slug} @ {branch}")
        if os.path.exists(clone_dest):
            shutil.rmtree(clone_dest)
        run(f"git clone --depth=1 --branch {branch} {url} {clone_dest}")

        for svc_entry in services:
            docs_path = svc_entry["docs_path"]
            service_root = os.path.join(clone_dest, docs_path)

            manifest_path = os.path.join(service_root, "docspine.yaml")
            with open(manifest_path) as f:
                manifest = yaml.safe_load(f)

            service_id = manifest.get("service", docs_path)
            nav_title = manifest.get("nav_title", service_id)
            domain = manifest.get("domain", "other")
            team = manifest.get("team", "")
            pages = manifest.get("pages", 0)
            diataxis = manifest.get("diataxis", [])
            output_dir = manifest.get("output_dir", "site").rstrip("/")

            print(f"\n  → Building {domain}/{service_id}")

            run("just docs-build", cwd=service_root)

            src = os.path.join(service_root, output_dir)

            if group_by == "flat":
                dst = os.path.join(dist_dir, service_id)
            elif group_by == "team":
                dst = os.path.join(dist_dir, team or domain, service_id)
            else:
                dst = os.path.join(dist_dir, domain, service_id)

            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"  ✓ → dist/{domain}/{service_id}/")

            all_services.append({
                "id": service_id,
                "name": nav_title,
                "domain": domain,
                "team": team,
                "pages": pages,
                "diataxis": diataxis,
            })

    services_json_path = os.path.join(build_dir, "services.json")
    with open(services_json_path, "w") as f:
        json.dump(all_services, f, indent=2)
    print(f"\n✓ services.json written to {services_json_path} ({len(all_services)} services)")

    total = sum(r.get("services") and len(r["services"]) or 0 for r in repos)
    print(f"✓ Aggregated {total} service(s) into {dist_dir}/")


if __name__ == "__main__":
    main()
