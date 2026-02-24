#!/usr/bin/env python3
"""
Generates dist/index.html from _build/services.json.
Renders the full "Engineering Editorial" landing page with
Bookshelf Spines (default) and Hex Grid themes, Pagefind search,
Diataxis filter pills, and a theme switcher.
"""
import json
import os
from collections import defaultdict
from datetime import datetime, timezone


SERVICES_JSON = os.path.join("_build", "services.json")
DIST_DIR = "dist"


def load_services():
    with open(SERVICES_JSON) as f:
        return json.load(f)


def compute_stats(services):
    total_pages = sum(s.get("pages", 0) for s in services)
    teams = len({s["team"] for s in services if s.get("team")})
    domains = len({s["domain"] for s in services if s.get("domain")})
    last_build = datetime.now(timezone.utc).strftime("%b %-d, %Y")
    return len(services), teams, domains, total_pages, last_build


def main():
    services = load_services()
    svc_count, team_count, domain_count, page_count, last_build = compute_stats(services)

    services_json_inline = json.dumps(services)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Docspine Demo — Documentation Hub</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,400&family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg-primary: #08090b;
    --bg-secondary: #0e1013;
    --bg-card: #131518;
    --bg-shelf: #0b0c0f;
    --border: #1c1f25;
    --border-active: #2a2e38;
    --text-primary: #e4e6eb;
    --text-secondary: #8b8f9a;
    --text-muted: #53565f;
    --accent: #34d399;
    --accent-dim: #1a7a52;
    --accent-glow: rgba(52, 211, 153, 0.12);
    --accent-glow-strong: rgba(52, 211, 153, 0.25);

    --domain-checkout: #f5a623;
    --domain-identity: #a78bfa;
    --domain-platform: #38bdf8;
    --domain-observability: #fb7185;

    --dt-howto: #f5a623;
    --dt-reference: #38bdf8;
    --dt-explanation: #a78bfa;
    --dt-tutorial: #34d399;

    --font-display: 'Fraunces', Georgia, serif;
    --font-body: 'DM Sans', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;

    --hex-size: 72px;
  }}

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    background: var(--bg-primary);
    color: var(--text-primary);
    font-family: var(--font-body);
    min-height: 100vh;
    overflow-x: hidden;
  }}

  body::before {{
    content: '';
    position: fixed;
    inset: 0;
    background:
      radial-gradient(ellipse 100% 50% at 50% 100%, rgba(52, 211, 153, 0.03) 0%, transparent 60%),
      radial-gradient(ellipse 40% 60% at 15% 50%, rgba(245, 166, 35, 0.02) 0%, transparent 50%),
      radial-gradient(ellipse 40% 60% at 85% 50%, rgba(167, 139, 250, 0.02) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
  }}

  body::after {{
    content: '';
    position: fixed;
    inset: 0;
    opacity: 0.03;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
  }}

  .container {{
    position: relative;
    z-index: 1;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 2rem;
  }}

  /* ═══════ Header ═══════ */
  header {{
    padding: 3rem 0 0.5rem;
    text-align: center;
    position: relative;
  }}

  .logo {{
    font-family: var(--font-display);
    font-size: 1rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    color: var(--text-muted);
    text-transform: uppercase;
    margin-bottom: 0.3rem;
  }}

  .logo span {{ color: var(--accent); }}

  header h1 {{
    font-family: var(--font-display);
    font-size: clamp(1.8rem, 4vw, 2.8rem);
    font-weight: 300;
    color: var(--text-primary);
    letter-spacing: -0.02em;
    line-height: 1.15;
    font-style: italic;
  }}

  header h1 em {{
    font-style: normal;
    font-weight: 700;
    color: var(--accent);
  }}

  .subtitle {{
    font-family: var(--font-body);
    font-size: 0.85rem;
    color: var(--text-muted);
    margin-top: 0.4rem;
    letter-spacing: 0.02em;
  }}

  /* ═══════ Theme toggle ═══════ */
  .theme-toggle {{
    position: absolute;
    top: 3rem;
    right: 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 100px;
    padding: 0.3rem 0.75rem;
    cursor: pointer;
    font-family: var(--font-mono);
    font-size: 0.65rem;
    color: var(--text-muted);
    transition: all 0.25s;
    user-select: none;
  }}

  .theme-toggle:hover {{
    border-color: var(--border-active);
    color: var(--text-secondary);
  }}

  .theme-toggle-icon {{
    font-size: 0.75rem;
  }}

  /* ═══════ Search ═══════ */
  .search-section {{
    padding: 2rem 0 1.5rem;
    position: sticky;
    top: 0;
    z-index: 10;
    background: linear-gradient(to bottom, var(--bg-primary) 60%, transparent);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
  }}

  .search-wrapper {{
    position: relative;
    max-width: 600px;
    margin: 0 auto;
  }}

  .search-icon {{
    position: absolute;
    left: 1.25rem;
    top: 50%;
    transform: translateY(-50%);
    color: var(--text-muted);
    transition: color 0.3s;
    pointer-events: none;
  }}

  .search-input {{
    width: 100%;
    padding: 0.9rem 1.25rem 0.9rem 3.25rem;
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 14px;
    color: var(--text-primary);
    font-family: var(--font-mono);
    font-size: 0.9rem;
    outline: none;
    transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  }}

  .search-input::placeholder {{
    color: var(--text-muted);
    font-family: var(--font-body);
  }}

  .search-input:focus {{
    border-color: var(--accent-dim);
    box-shadow: 0 0 0 3px var(--accent-glow), 0 8px 32px rgba(0,0,0,0.4);
    background: var(--bg-card);
  }}

  .search-input:focus + .search-icon {{ color: var(--accent); }}

  .search-shortcut {{
    position: absolute;
    right: 1.25rem;
    top: 50%;
    transform: translateY(-50%);
    padding: 0.2rem 0.5rem;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 6px;
    font-family: var(--font-mono);
    font-size: 0.65rem;
    color: var(--text-muted);
    pointer-events: none;
    transition: opacity 0.3s;
  }}

  .search-input:focus ~ .search-shortcut {{ opacity: 0; }}

  /* ═══════ Filters ═══════ */
  .filters {{
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    margin-top: 1rem;
    flex-wrap: wrap;
  }}

  .filter-pill {{
    padding: 0.3rem 0.8rem;
    background: transparent;
    border: 1px solid var(--border);
    border-radius: 100px;
    color: var(--text-secondary);
    font-family: var(--font-body);
    font-size: 0.75rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.25s;
    user-select: none;
  }}

  .filter-pill:hover {{
    border-color: var(--border-active);
    color: var(--text-primary);
  }}

  .filter-pill.active {{
    border-color: var(--accent-dim);
    color: var(--accent);
    background: var(--accent-glow);
  }}

  .filter-pill .dot {{
    display: inline-block;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    margin-right: 0.35rem;
    vertical-align: middle;
  }}

  /* ═══════ Stats ═══════ */
  .stats {{
    display: flex;
    justify-content: center;
    gap: 2rem;
    padding: 0.75rem 0 1.5rem;
  }}

  .stat {{
    font-family: var(--font-mono);
    font-size: 0.7rem;
    color: var(--text-muted);
  }}

  .stat strong {{
    color: var(--text-secondary);
    font-weight: 600;
  }}

  /* ═══════ Search Results ═══════ */
  .search-results {{
    max-width: 600px;
    margin: 0 auto;
    display: none;
  }}

  .search-results.visible {{ display: block; }}

  .results-domain-group {{
    margin-bottom: 1.5rem;
    animation: fadeSlideIn 0.3s ease both;
  }}

  .results-domain-label {{
    font-family: var(--font-mono);
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-muted);
    padding: 0 0.25rem 0.5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 0.5rem;
  }}

  .result-item {{
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.65rem 0.75rem;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.2s;
    text-decoration: none;
    color: inherit;
  }}

  .result-item:hover {{ background: rgba(255,255,255,0.03); }}
  .result-item.selected {{ background: var(--accent-glow); }}

  .result-badge {{
    flex-shrink: 0;
    padding: 0.15rem 0.45rem;
    border-radius: 4px;
    font-family: var(--font-mono);
    font-size: 0.55rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 0.2rem;
  }}

  .badge-how-to {{ background: rgba(245, 166, 35, 0.15); color: var(--dt-howto); }}
  .badge-reference {{ background: rgba(56, 189, 248, 0.15); color: var(--dt-reference); }}
  .badge-explanation {{ background: rgba(167, 139, 250, 0.15); color: var(--dt-explanation); }}
  .badge-tutorial {{ background: rgba(52, 211, 153, 0.15); color: var(--dt-tutorial); }}

  .result-content h4 {{
    font-family: var(--font-body);
    font-weight: 600;
    font-size: 0.85rem;
  }}

  .result-content p {{
    font-size: 0.75rem;
    color: var(--text-secondary);
    line-height: 1.4;
    margin-top: 0.1rem;
  }}

  .result-breadcrumb {{
    font-family: var(--font-mono);
    font-size: 0.6rem;
    color: var(--text-muted);
    margin-top: 0.2rem;
  }}

  .no-results {{
    text-align: center;
    padding: 2rem;
    color: var(--text-muted);
    font-size: 0.9rem;
    display: none;
  }}

  .no-results.visible {{ display: block; animation: fadeSlideIn 0.3s ease; }}

  /* ═══════ Bookshelf (Spines theme) ═══════ */
  .bookshelf {{
    padding: 0 0 4rem;
    transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
  }}

  .bookshelf.dimmed {{
    opacity: 0.06;
    filter: blur(10px);
    pointer-events: none;
    transform: scale(0.98) translateY(8px);
  }}

  .shelf-row {{ margin-bottom: 2.5rem; }}

  .shelf-domain-label {{
    font-family: var(--font-mono);
    font-size: 0.6rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    margin-bottom: 0.75rem;
    padding-left: 0.25rem;
  }}

  .domain-checkout .shelf-domain-label {{ color: var(--domain-checkout); }}
  .domain-identity .shelf-domain-label {{ color: var(--domain-identity); }}
  .domain-platform .shelf-domain-label {{ color: var(--domain-platform); }}
  .domain-observability .shelf-domain-label {{ color: var(--domain-observability); }}

  .shelf-surface {{
    display: flex;
    align-items: flex-end;
    gap: 0;
    padding: 0 0.5rem;
    min-height: 200px;
    position: relative;
  }}

  .shelf-surface::after {{
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, transparent 0%, var(--border-active) 10%, var(--border-active) 90%, transparent 100%);
    border-radius: 2px;
  }}

  .shelf-surface::before {{
    content: '';
    position: absolute;
    bottom: -12px;
    left: 5%;
    right: 5%;
    height: 12px;
    background: radial-gradient(ellipse at center, rgba(0,0,0,0.3) 0%, transparent 70%);
    pointer-events: none;
  }}

  .spine {{
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-end;
    padding: 0.6rem 0.3rem;
    cursor: pointer;
    transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    border-radius: 3px 3px 0 0;
    margin: 0 3px;
    animation: spineRise 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
  }}

  .spine:nth-child(1) {{ animation-delay: 0.05s; }}
  .spine:nth-child(2) {{ animation-delay: 0.12s; }}
  .spine:nth-child(3) {{ animation-delay: 0.19s; }}

  .spine:hover {{ transform: translateY(-8px); z-index: 5; }}

  .spine::before {{
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 3px 3px 0 0;
    opacity: 0;
    transition: opacity 0.35s;
    pointer-events: none;
  }}

  .spine:hover::before {{ opacity: 1; }}

  .domain-checkout .spine::before {{ box-shadow: 0 0 20px rgba(245, 166, 35, 0.3), inset 0 0 20px rgba(245, 166, 35, 0.05); }}
  .domain-identity .spine::before {{ box-shadow: 0 0 20px rgba(167, 139, 250, 0.3), inset 0 0 20px rgba(167, 139, 250, 0.05); }}
  .domain-platform .spine::before {{ box-shadow: 0 0 20px rgba(56, 189, 248, 0.3), inset 0 0 20px rgba(56, 189, 248, 0.05); }}
  .domain-observability .spine::before {{ box-shadow: 0 0 20px rgba(251, 113, 133, 0.3), inset 0 0 20px rgba(251, 113, 133, 0.05); }}

  .domain-checkout .spine {{
    background: linear-gradient(180deg, #2b2010 0%, #1f1808 40%, #2b2010 100%);
    border-left: 1px solid rgba(245, 166, 35, 0.15);
    border-right: 1px solid rgba(245, 166, 35, 0.08);
    border-top: 1px solid rgba(245, 166, 35, 0.12);
  }}
  .domain-identity .spine {{
    background: linear-gradient(180deg, #1c1630 0%, #140f24 40%, #1c1630 100%);
    border-left: 1px solid rgba(167, 139, 250, 0.15);
    border-right: 1px solid rgba(167, 139, 250, 0.08);
    border-top: 1px solid rgba(167, 139, 250, 0.12);
  }}
  .domain-platform .spine {{
    background: linear-gradient(180deg, #0f1d28 0%, #0a1520 40%, #0f1d28 100%);
    border-left: 1px solid rgba(56, 189, 248, 0.15);
    border-right: 1px solid rgba(56, 189, 248, 0.08);
    border-top: 1px solid rgba(56, 189, 248, 0.12);
  }}
  .domain-observability .spine {{
    background: linear-gradient(180deg, #281018 0%, #1f0c12 40%, #281018 100%);
    border-left: 1px solid rgba(251, 113, 133, 0.15);
    border-right: 1px solid rgba(251, 113, 133, 0.08);
    border-top: 1px solid rgba(251, 113, 133, 0.12);
  }}

  .spine-title {{
    writing-mode: vertical-rl;
    text-orientation: mixed;
    transform: rotate(180deg);
    font-family: var(--font-display);
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.03em;
    white-space: nowrap;
    flex: 1;
    display: flex;
    align-items: center;
    padding: 0.5rem 0;
  }}

  .domain-checkout .spine-title {{ color: var(--domain-checkout); }}
  .domain-identity .spine-title {{ color: var(--domain-identity); }}
  .domain-platform .spine-title {{ color: var(--domain-platform); }}
  .domain-observability .spine-title {{ color: var(--domain-observability); }}

  .spine-team {{
    writing-mode: vertical-rl;
    transform: rotate(180deg);
    font-family: var(--font-mono);
    font-size: 0.45rem;
    color: var(--text-muted);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-top: 0.4rem;
  }}

  .spine-diataxis {{
    display: flex;
    gap: 2px;
    margin-bottom: 0.4rem;
    flex-direction: row;
  }}

  .spine-dt-pip {{
    width: 4px;
    height: 4px;
    border-radius: 50%;
  }}

  .spine-notches {{
    display: flex;
    flex-direction: column;
    gap: 6px;
    position: absolute;
    right: 4px;
    top: 50%;
    transform: translateY(-50%);
    opacity: 0.2;
  }}

  .spine-notch {{
    width: 3px;
    height: 1px;
    border-radius: 1px;
  }}

  .domain-checkout .spine-notch {{ background: var(--domain-checkout); }}
  .domain-identity .spine-notch {{ background: var(--domain-identity); }}
  .domain-platform .spine-notch {{ background: var(--domain-platform); }}
  .domain-observability .spine-notch {{ background: var(--domain-observability); }}

  .spine-tooltip {{
    position: absolute;
    bottom: calc(100% + 14px);
    left: 50%;
    transform: translateX(-50%) translateY(8px);
    background: var(--bg-card);
    border: 1px solid var(--border-active);
    border-radius: 10px;
    padding: 0.75rem 1rem;
    white-space: nowrap;
    opacity: 0;
    pointer-events: none;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    z-index: 20;
    box-shadow: 0 12px 40px rgba(0,0,0,0.5);
    text-align: left;
  }}

  .spine:hover .spine-tooltip {{
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }}

  .spine-tooltip h5 {{
    font-family: var(--font-display);
    font-weight: 600;
    font-size: 0.85rem;
    color: var(--text-primary);
    margin-bottom: 0.3rem;
  }}

  .spine-tooltip-meta {{
    display: flex;
    gap: 0.8rem;
    font-family: var(--font-mono);
    font-size: 0.6rem;
    color: var(--text-muted);
  }}

  .spine.spine-dimmed {{
    opacity: 0.08 !important;
    transform: translateY(0) scale(0.97) !important;
    pointer-events: none;
    filter: grayscale(1);
  }}

  /* ═══════ Hex Catalog ═══════ */
  .hex-catalog {{
    padding: 1rem 0 4rem;
    transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
  }}

  .hex-catalog.dimmed {{
    opacity: 0.08;
    filter: blur(8px);
    pointer-events: none;
    transform: scale(0.98);
  }}

  .domains-grid {{
    display: flex;
    justify-content: center;
    gap: 3rem;
    flex-wrap: wrap;
  }}

  .domain-column {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    min-width: 170px;
  }}

  .domain-header {{
    font-family: var(--font-mono);
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    padding: 0.3rem 0.8rem;
    border-radius: 100px;
    margin-bottom: 0.5rem;
  }}

  .domain-checkout .domain-header {{ color: var(--domain-checkout); background: rgba(245, 166, 35, 0.1); }}
  .domain-identity .domain-header {{ color: var(--domain-identity); background: rgba(167, 139, 250, 0.1); }}
  .domain-platform .domain-header {{ color: var(--domain-platform); background: rgba(56, 189, 248, 0.1); }}
  .domain-observability .domain-header {{ color: var(--domain-observability); background: rgba(251, 113, 133, 0.1); }}

  .hex-stack {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
  }}

  .hex-wrapper {{
    position: relative;
    width: calc(var(--hex-size) * 2);
    height: calc(var(--hex-size) * 1.74);
    cursor: pointer;
    transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
    animation: hexAppear 0.5s ease both;
  }}

  .hex-wrapper:nth-child(1) {{ animation-delay: 0.05s; }}
  .hex-wrapper:nth-child(2) {{ animation-delay: 0.1s; }}
  .hex-wrapper:nth-child(3) {{ animation-delay: 0.15s; }}

  .hex-wrapper:hover {{ transform: translateY(-4px) scale(1.04); z-index: 2; }}

  .hex-shape {{
    width: 100%;
    height: 100%;
    clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 1rem 0.5rem;
    transition: all 0.35s;
    position: relative;
    overflow: hidden;
  }}

  .domain-checkout .hex-shape {{ background: linear-gradient(160deg, #1a1608 0%, #1f1a0a 100%); }}
  .domain-identity .hex-shape {{ background: linear-gradient(160deg, #130f1e 0%, #17102a 100%); }}
  .domain-platform .hex-shape {{ background: linear-gradient(160deg, #091517 0%, #0a191c 100%); }}
  .domain-observability .hex-shape {{ background: linear-gradient(160deg, #1a0a10 0%, #1f0c14 100%); }}

  .hex-wrapper::before {{
    content: '';
    position: absolute;
    inset: -1px;
    clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
    transition: all 0.35s;
    z-index: -1;
  }}

  .domain-checkout .hex-wrapper::before {{ background: rgba(245, 166, 35, 0.12); }}
  .domain-identity .hex-wrapper::before {{ background: rgba(167, 139, 250, 0.12); }}
  .domain-platform .hex-wrapper::before {{ background: rgba(56, 189, 248, 0.12); }}
  .domain-observability .hex-wrapper::before {{ background: rgba(251, 113, 133, 0.12); }}

  .domain-checkout .hex-wrapper:hover::before {{ background: rgba(245, 166, 35, 0.3); }}
  .domain-identity .hex-wrapper:hover::before {{ background: rgba(167, 139, 250, 0.3); }}
  .domain-platform .hex-wrapper:hover::before {{ background: rgba(56, 189, 248, 0.3); }}
  .domain-observability .hex-wrapper:hover::before {{ background: rgba(251, 113, 133, 0.3); }}

  .hex-abbr {{
    font-family: var(--font-mono);
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    margin-bottom: 0.15rem;
  }}

  .domain-checkout .hex-abbr {{ color: var(--domain-checkout); }}
  .domain-identity .hex-abbr {{ color: var(--domain-identity); }}
  .domain-platform .hex-abbr {{ color: var(--domain-platform); }}
  .domain-observability .hex-abbr {{ color: var(--domain-observability); }}

  .hex-name {{
    font-family: var(--font-body);
    font-size: 0.65rem;
    font-weight: 500;
    color: var(--text-secondary);
    line-height: 1.2;
    max-width: 90%;
  }}

  .hex-team {{
    font-family: var(--font-mono);
    font-size: 0.5rem;
    color: var(--text-muted);
    margin-top: 0.2rem;
    letter-spacing: 0.05em;
  }}

  .hex-coverage {{
    position: absolute;
    bottom: 18%;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 2px;
  }}

  .coverage-dot {{
    width: 4px;
    height: 4px;
    border-radius: 50%;
    opacity: 0.5;
  }}

  .hex-tooltip {{
    position: absolute;
    bottom: calc(100% + 10px);
    left: 50%;
    transform: translateX(-50%) translateY(8px);
    background: var(--bg-card);
    border: 1px solid var(--border-active);
    border-radius: 10px;
    padding: 0.75rem 1rem;
    white-space: nowrap;
    opacity: 0;
    pointer-events: none;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    z-index: 20;
    box-shadow: 0 12px 40px rgba(0,0,0,0.4);
  }}

  .hex-wrapper:hover .hex-tooltip {{
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }}

  .hex-tooltip h5 {{
    font-family: var(--font-body);
    font-weight: 600;
    font-size: 0.8rem;
    color: var(--text-primary);
    margin-bottom: 0.3rem;
  }}

  .hex-tooltip-meta {{
    display: flex;
    gap: 1rem;
    font-family: var(--font-mono);
    font-size: 0.65rem;
    color: var(--text-muted);
  }}

  .hex-wrapper.hex-dimmed {{
    opacity: 0.12 !important;
    transform: scale(0.92) !important;
    pointer-events: none;
  }}

  /* ═══════ Theme show/hide ═══════ */
  body.theme-spines #bookshelf {{ display: block; }}
  body.theme-spines #hexCatalog {{ display: none; }}
  body.theme-hex #bookshelf {{ display: none; }}
  body.theme-hex #hexCatalog {{ display: block; }}

  /* ═══════ Footer ═══════ */
  footer {{
    text-align: center;
    padding: 1rem 0 3rem;
    font-family: var(--font-mono);
    font-size: 0.65rem;
    color: var(--text-muted);
  }}

  footer a {{
    color: var(--accent);
    text-decoration: none;
    border-bottom: 1px solid transparent;
    transition: border-color 0.2s;
  }}

  footer a:hover {{ border-bottom-color: var(--accent); }}

  .footer-links {{
    display: flex;
    justify-content: center;
    gap: 1.5rem;
    margin-top: 0.4rem;
  }}

  /* ═══════ Animations ═══════ */
  @keyframes spineRise {{
    from {{ opacity: 0; transform: translateY(30px) scaleY(0.7); }}
    to {{ opacity: 1; transform: translateY(0) scaleY(1); }}
  }}

  @keyframes hexAppear {{
    from {{ opacity: 0; transform: translateY(12px) scale(0.9); }}
    to {{ opacity: 1; transform: translateY(0) scale(1); }}
  }}

  @keyframes fadeSlideIn {{
    from {{ opacity: 0; transform: translateY(8px); }}
    to {{ opacity: 1; transform: translateY(0); }}
  }}

  @media (max-width: 768px) {{
    .shelf-surface {{ min-height: 160px; overflow-x: auto; padding-bottom: 8px; }}
    .stats {{ gap: 1rem; flex-wrap: wrap; }}
    .domains-grid {{ gap: 2rem; }}
    .domain-column {{ min-width: 140px; }}
    :root {{ --hex-size: 58px; }}
    .theme-toggle {{ position: static; margin: 0.75rem auto 0; display: flex; width: fit-content; }}
  }}
</style>
</head>
<body class="theme-spines">

<div class="container">
  <header>
    <div class="logo">Doc<span>spine</span></div>
    <h1>Every service, <em>on the shelf</em></h1>
    <p class="subtitle">Search across all documentation or browse the stacks</p>
    <button class="theme-toggle" id="themeToggle" title="Switch view">
      <span class="theme-toggle-icon" id="themeIcon">⬡</span>
      <span id="themeLabel">Hex Grid</span>
    </button>
  </header>

  <section class="search-section">
    <div class="search-wrapper">
      <input class="search-input" type="text" placeholder="Search all documentation..." id="searchInput" autocomplete="off" spellcheck="false">
      <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
      <span class="search-shortcut">⌘K</span>
    </div>
    <div class="filters">
      <button class="filter-pill active" data-filter="all">All</button>
      <button class="filter-pill" data-filter="how-to"><span class="dot" style="background:var(--dt-howto)"></span>How-To</button>
      <button class="filter-pill" data-filter="reference"><span class="dot" style="background:var(--dt-reference)"></span>Reference</button>
      <button class="filter-pill" data-filter="explanation"><span class="dot" style="background:var(--dt-explanation)"></span>Explanation</button>
      <button class="filter-pill" data-filter="tutorial"><span class="dot" style="background:var(--dt-tutorial)"></span>Tutorial</button>
    </div>
  </section>

  <div class="stats">
    <span class="stat"><strong>{svc_count}</strong> services</span>
    <span class="stat"><strong>{team_count}</strong> teams</span>
    <span class="stat"><strong>{domain_count}</strong> domains</span>
    <span class="stat"><strong>{page_count}</strong> pages</span>
    <span class="stat">built <strong>{last_build}</strong></span>
  </div>

  <div class="search-results" id="searchResults"></div>
  <div class="no-results" id="noResults">No documentation found matching your search.</div>

  <div class="bookshelf" id="bookshelf"></div>
  <div class="hex-catalog" id="hexCatalog">
    <div class="domains-grid" id="domainsGrid"></div>
  </div>

  <footer>
    <div>Aggregated with <a href="https://nondualworks.github.io/docspine">Docspine</a></div>
    <div class="footer-links">
      <a href="llms.txt">llms.txt</a>
      <a href="https://github.com/nondualworks/docspine-demo">Source</a>
    </div>
  </footer>
</div>

<script>
// ═══════ Service data (injected at build time) ═══════
const SERVICES = {services_json_inline};

const DT_COLORS = {{
  'how-to': 'var(--dt-howto)',
  'reference': 'var(--dt-reference)',
  'explanation': 'var(--dt-explanation)',
  'tutorial': 'var(--dt-tutorial)'
}};

const DOMAIN_ORDER = ['checkout', 'identity', 'platform', 'observability'];

// ═══════ Hex abbreviation (auto-derived) ═══════
function abbrev(id) {{
  const words = id.split('-');
  return words.slice(0, 2).map(w => w[0].toUpperCase()).join('');
}}

// ═══════ Theme switcher ═══════
const THEME_KEY = 'docspine-theme';
const themeToggle = document.getElementById('themeToggle');
const themeIcon = document.getElementById('themeIcon');
const themeLabel = document.getElementById('themeLabel');

function applyTheme(theme) {{
  document.body.classList.remove('theme-spines', 'theme-hex');
  document.body.classList.add('theme-' + theme);
  if (theme === 'spines') {{
    themeIcon.textContent = '⬡';
    themeLabel.textContent = 'Hex Grid';
  }} else {{
    themeIcon.textContent = '📚';
    themeLabel.textContent = 'Spines';
  }}
}}

(function () {{
  const saved = localStorage.getItem(THEME_KEY) || 'spines';
  applyTheme(saved);
}})();

themeToggle.addEventListener('click', () => {{
  const current = document.body.classList.contains('theme-spines') ? 'spines' : 'hex';
  const next = current === 'spines' ? 'hex' : 'spines';
  applyTheme(next);
  localStorage.setItem(THEME_KEY, next);
}});

// ═══════ Build bookshelf ═══════
function buildBookshelf() {{
  const bookshelf = document.getElementById('bookshelf');
  const maxPages = Math.max(...SERVICES.map(s => s.pages || 1));
  const domains = DOMAIN_ORDER.filter(d => SERVICES.some(s => s.domain === d));

  let html = '';
  domains.forEach(domain => {{
    const svcs = SERVICES.filter(s => s.domain === domain);
    html += `<div class="shelf-row domain-${{domain}}">`;
    html += `<div class="shelf-domain-label">${{domain}}</div>`;
    html += `<div class="shelf-surface">`;

    svcs.forEach(svc => {{
      const height = 120 + ((svc.pages || 1) / maxPages) * 100;
      const width = 44 + (svc.id.length % 3) * 4;
      const notchCount = Math.min(svc.pages || 0, 6);
      let notches = '';
      for (let i = 0; i < notchCount; i++) notches += `<span class="spine-notch"></span>`;
      let pips = '';
      (svc.diataxis || []).forEach(dt => {{
        pips += `<span class="spine-dt-pip" style="background:${{DT_COLORS[dt] || '#666'}}"></span>`;
      }});

      html += `
        <div class="spine" data-service="${{svc.id}}" data-domain="${{domain}}" style="height:${{height}}px;width:${{width}}px">
          <div class="spine-diataxis">${{pips}}</div>
          <div class="spine-title">${{svc.name}}</div>
          <div class="spine-team">${{svc.team}}</div>
          <div class="spine-notches">${{notches}}</div>
          <div class="spine-tooltip">
            <h5>${{svc.name}}</h5>
            <div class="spine-tooltip-meta">
              <span>📄 ${{svc.pages}} pages</span>
              <span>👥 ${{svc.team}}</span>
            </div>
          </div>
        </div>`;
    }});

    html += `</div></div>`;
  }});

  bookshelf.innerHTML = html;
}}

// ═══════ Build hex catalog ═══════
function buildHexCatalog() {{
  const grid = document.getElementById('domainsGrid');
  const domains = DOMAIN_ORDER.filter(d => SERVICES.some(s => s.domain === d));

  let html = '';
  domains.forEach(domain => {{
    const svcs = SERVICES.filter(s => s.domain === domain);
    html += `<div class="domain-column domain-${{domain}}">`;
    html += `<div class="domain-header">${{domain}}</div>`;
    html += `<div class="hex-stack">`;

    svcs.forEach(svc => {{
      const ab = abbrev(svc.id);
      let dots = '';
      (svc.diataxis || []).forEach(dt => {{
        dots += `<span class="coverage-dot" style="background:${{DT_COLORS[dt] || '#666'}}"></span>`;
      }});

      html += `
        <div class="hex-wrapper" data-service="${{svc.id}}" data-domain="${{domain}}">
          <div class="hex-shape">
            <div class="hex-abbr">${{ab}}</div>
            <div class="hex-name">${{svc.name}}</div>
            <div class="hex-team">${{svc.team}}</div>
            <div class="hex-coverage">${{dots}}</div>
          </div>
          <div class="hex-tooltip">
            <h5>${{svc.name}}</h5>
            <div class="hex-tooltip-meta">
              <span>📄 ${{svc.pages}} pages</span>
              <span>👥 ${{svc.team}}</span>
            </div>
          </div>
        </div>`;
    }});

    html += `</div></div>`;
  }});

  grid.innerHTML = html;
}}

buildBookshelf();
buildHexCatalog();

// ═══════ Search & Filter ═══════
const searchInput = document.getElementById('searchInput');
const searchResults = document.getElementById('searchResults');
const noResults = document.getElementById('noResults');
const bookshelf = document.getElementById('bookshelf');
const hexCatalog = document.getElementById('hexCatalog');
let activeFilter = 'all';
let selectedIndex = -1;
let pagefind = null;

async function loadPagefind() {{
  if (pagefind) return;
  try {{
    pagefind = await import('./pagefind/pagefind.js');
    await pagefind.init();
  }} catch (e) {{
    pagefind = null;
  }}
}}

function hideCatalog() {{
  bookshelf.classList.add('dimmed');
  hexCatalog.classList.add('dimmed');
}}

function showCatalog() {{
  bookshelf.classList.remove('dimmed');
  hexCatalog.classList.remove('dimmed');
}}

function highlight(text, query) {{
  if (!query || !text) return text || '';
  const regex = new RegExp(`(${{query.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&')}})`, 'gi');
  return text.replace(regex, '<mark style="background:rgba(52,211,153,0.2);color:var(--accent);padding:0 2px;border-radius:2px">$1</mark>');
}}

function filterCatalog() {{
  document.querySelectorAll('.spine').forEach(el => {{
    const svc = SERVICES.find(s => s.id === el.dataset.service);
    if (!svc) return;
    const match = activeFilter === 'all' || (svc.diataxis || []).includes(activeFilter);
    el.classList.toggle('spine-dimmed', !match);
  }});
  document.querySelectorAll('.hex-wrapper').forEach(el => {{
    const svc = SERVICES.find(s => s.id === el.dataset.service);
    if (!svc) return;
    const match = activeFilter === 'all' || (svc.diataxis || []).includes(activeFilter);
    el.classList.toggle('hex-dimmed', !match);
  }});
}}

async function doSearch() {{
  const query = searchInput.value.trim();

  if (!query) {{
    searchResults.classList.remove('visible');
    searchResults.innerHTML = '';
    noResults.classList.remove('visible');
    showCatalog();
    selectedIndex = -1;
    filterCatalog();
    return;
  }}

  hideCatalog();

  if (!pagefind) await loadPagefind();

  let results = [];

  if (pagefind) {{
    try {{
      const search = await pagefind.search(query);
      const raw = await Promise.all(search.results.slice(0, 30).map(r => r.data()));
      results = raw.map(r => {{
        const segs = (r.url || '').replace(/^\\//, '').split('/');
        const domain = segs[0] || '';
        const service = segs[1] || '';
        const type = segs[2] || 'reference';
        return {{
          title: r.meta?.title || r.url,
          type,
          domain,
          service,
          path: r.url,
          desc: r.excerpt || '',
          fromPagefind: true,
        }};
      }});
    }} catch (e) {{
      // pagefind failed, fall through to empty
    }}
  }}

  if (activeFilter !== 'all') {{
    results = results.filter(r => r.type === activeFilter);
  }}

  if (results.length === 0) {{
    searchResults.classList.remove('visible');
    searchResults.innerHTML = '';
    noResults.classList.add('visible');
    return;
  }}

  noResults.classList.remove('visible');

  const grouped = {{}};
  results.forEach(r => {{
    if (!grouped[r.domain]) grouped[r.domain] = [];
    grouped[r.domain].push(r);
  }});

  let html = '';
  let idx = 0;
  for (const [domain, docs] of Object.entries(grouped)) {{
    html += `<div class="results-domain-group" style="animation-delay:${{idx * 0.04}}s">`;
    html += `<div class="results-domain-label">${{domain}} · ${{docs.length}} result${{docs.length > 1 ? 's' : ''}}</div>`;
    docs.forEach(d => {{
      const badge = d.type.replace(/_/g, '-');
      html += `<a class="result-item" href="${{d.path}}" data-idx="${{idx}}">
        <span class="result-badge badge-${{badge}}">${{d.type}}</span>
        <div class="result-content">
          <h4>${{highlight(d.title, query)}}</h4>
          <p>${{d.desc}}</p>
          <div class="result-breadcrumb">${{d.domain}}/${{d.service}}</div>
        </div>
      </a>`;
      idx++;
    }});
    html += '</div>';
  }}

  searchResults.innerHTML = html;
  searchResults.classList.add('visible');
  selectedIndex = -1;
}}

// Filter pills — toggle behavior
document.querySelectorAll('.filter-pill').forEach(pill => {{
  pill.addEventListener('click', () => {{
    if (pill.classList.contains('active') && pill.dataset.filter !== 'all') {{
      pill.classList.remove('active');
      document.querySelector('.filter-pill[data-filter="all"]').classList.add('active');
      activeFilter = 'all';
    }} else {{
      document.querySelector('.filter-pill.active').classList.remove('active');
      pill.classList.add('active');
      activeFilter = pill.dataset.filter;
    }}
    doSearch();
  }});
}});

searchInput.addEventListener('input', doSearch);

searchInput.addEventListener('keydown', (e) => {{
  const items = searchResults.querySelectorAll('.result-item');
  if (!items.length) return;
  if (e.key === 'ArrowDown') {{ e.preventDefault(); selectedIndex = Math.min(selectedIndex + 1, items.length - 1); updateSelection(items); }}
  else if (e.key === 'ArrowUp') {{ e.preventDefault(); selectedIndex = Math.max(selectedIndex - 1, 0); updateSelection(items); }}
  else if (e.key === 'Enter' && selectedIndex >= 0) {{ e.preventDefault(); items[selectedIndex].click(); }}
  else if (e.key === 'Escape') {{ searchInput.value = ''; doSearch(); searchInput.blur(); }}
}});

function updateSelection(items) {{
  items.forEach((item, i) => {{
    item.classList.toggle('selected', i === selectedIndex);
    if (i === selectedIndex) item.scrollIntoView({{ block: 'nearest' }});
  }});
}}

document.addEventListener('keydown', (e) => {{
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {{ e.preventDefault(); searchInput.focus(); searchInput.select(); }}
}});

// Spine / hex click navigation
document.addEventListener('click', (e) => {{
  const spine = e.target.closest('.spine');
  if (spine) {{
    window.location.href = spine.dataset.domain + '/' + spine.dataset.service + '/';
  }}
  const hex = e.target.closest('.hex-wrapper');
  if (hex) {{
    window.location.href = hex.dataset.domain + '/' + hex.dataset.service + '/';
  }}
}});
</script>

</body>
</html>
"""

    os.makedirs(DIST_DIR, exist_ok=True)
    out = os.path.join(DIST_DIR, "index.html")
    with open(out, "w") as f:
        f.write(html)
    print(f"✓ Landing page generated at {out}")
    print(f"  {svc_count} services / {team_count} teams / {domain_count} domains / {page_count} pages")


if __name__ == "__main__":
    main()
