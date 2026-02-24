# docspine-demo

A live demonstration of [Docspine](https://nondualworks.github.io/docspine) — federated documentation aggregated from independent repos.

**Live site:** https://nondualworks.github.io/docspine-demo

## What this is

This repo is a Docspine aggregation pipeline. It:
1. Reads `docs-registry.yaml` — a list of registered team repos
2. Clones each repo and runs `just docs-build`
3. Assembles the HTML output into one site with unified search
4. Deploys to GitHub Pages via GitHub Actions

The pipeline runs on every push to `main` and on a daily schedule to pick up upstream doc changes.

## Registered services

| Service | Team | Domain |
|---------|------|--------|
| [Checkout API](https://nondualworks.github.io/docspine-demo/checkout/checkout-api/) | platform | checkout |

## Try it yourself

1. Fork this repo
2. Edit `docs-registry.yaml` to point at your team repos (each needs a `docspine.yaml` and `Justfile`)
3. Enable GitHub Pages: Settings → Pages → Source: GitHub Actions
4. Push — your aggregated docs site deploys automatically

See the [Docspine deployment guide](https://nondualworks.github.io/docspine/deployment/github-pages/) for full instructions.

## How it works

```
docs-registry.yaml
       ↓
.github/workflows/deploy.yml  (GitHub Actions)
       ↓
scripts/aggregate.py          (clone repos, run just docs-build, assemble dist/)
scripts/generate-landing-page.py
scripts/generate-llms-txt.py
       ↓
npx pagefind --site dist      (build search index)
       ↓
GitHub Pages
```
