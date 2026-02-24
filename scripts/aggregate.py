#!/usr/bin/env python3
"""
Docspine aggregation script.
Reads docs-registry.yaml, builds each registered repo's docs,
and assembles them into a single dist/ directory.
"""
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

    for repo in repos:
        url = repo["url"]
        domain = repo["domain"]
        service = repo["service"]
        branch = repo.get("branch", "main")
        docs_path = repo.get("docs_path", ".")

        print(f"\n→ Building {domain}/{service}")
        print(f"  from {url} @ {branch} ({docs_path})")

        clone_dest = os.path.join(build_dir, service)
        if os.path.exists(clone_dest):
            shutil.rmtree(clone_dest)
        run(f"git clone --depth=1 --branch {branch} {url} {clone_dest}")

        service_root = os.path.join(clone_dest, docs_path)

        manifest_path = os.path.join(service_root, "docspine.yaml")
        with open(manifest_path) as f:
            manifest = yaml.safe_load(f)

        output_dir = manifest.get("output_dir", "site/").rstrip("/")

        run("just docs-build", cwd=service_root)

        src = os.path.join(service_root, output_dir)

        if group_by == "flat":
            dst = os.path.join(dist_dir, service)
        elif group_by == "team":
            dst = os.path.join(dist_dir, repo.get("team", domain), service)
        else:
            dst = os.path.join(dist_dir, domain, service)

        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print(f"  ✓ → dist/{domain}/{service}/")

    print(f"\n✓ Aggregated {len(repos)} service(s) into {dist_dir}/")


if __name__ == "__main__":
    main()
