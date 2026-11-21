#!/usr/bin/env python3
"""Fetch live GitHub numbers and render the black & gold stats SVGs.

    GITHUB_TOKEN=... python3 scripts/royal_stats.py [username]

Writes assets/royal-ledger.svg and assets/royal-calendar.svg. Only public,
non-fork repositories are counted, so local runs and the Actions run agree.
"""
import datetime as dt
import json
import math
import os
import sys
import urllib.request

from royal_art import (GOLD, GOLD_HI, GOLD_LO, MUTED, OUT, SHADES, f, gold_defs,
                       rule, shine_text, svg)

USER = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("GH_USER", "sumeetg13")

QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false, first: 100) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } }
      }
    }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionCount date weekday } }
      }
    }
  }
}"""

# notebooks/markup inflate byte counts without saying much about what I write
SKIP_LANGS = {"Jupyter Notebook", "HTML", "CSS", "SCSS", "Makefile", "Dockerfile", "Procfile", "Shell"}


def fetch():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN is not set")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "royal-stats"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if "errors" in payload:
        sys.exit(f"GraphQL error: {payload['errors']}")
    return payload["data"]["user"]


def roman(n):
    vals = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
            (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
    out = ""
    for v, s in vals:
        while n >= v:
            out, n = out + s, n - v
    return out


def summarise(u):
    cc = u["contributionsCollection"]
    langs = {}
    for repo in u["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            name = e["node"]["name"]
            if name not in SKIP_LANGS:
                langs[name] = langs.get(name, 0) + e["size"]
    total = sum(langs.values()) or 1
    ranked = sorted(langs.items(), key=lambda kv: -kv[1])
    top = [(n, b / total) for n, b in ranked[:5]]
    rest = 1 - sum(p for _, p in top)
    if rest > 0.005:
        top.append(("Others", rest))
    return {
        "repos": u["repositories"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in u["repositories"]["nodes"]),
        "since": int(u["createdAt"][:4]),
        "contribs": cc["contributionCalendar"]["totalContributions"],
        "commits": cc["totalCommitContributions"],
        "prs": cc["totalPullRequestContributions"],
        "weeks": cc["contributionCalendar"]["weeks"],
        "langs": top,
    }


# ── the ledger: medallions + language eclipse ─────────────────────────────
def medallion(cx, cy, value, label, uid, i):
    r = 50
    circ = 2 * math.pi * (r - 9)
    return f"""<g>
<circle cx="{cx}" cy="{cy}" r="{r + 8}" fill="{GOLD}" opacity=".18" filter="url(#bloom-{uid})" class="breathe"/>
<g class="{'spin' if i % 2 == 0 else 'spin-r'}"><circle cx="{cx}" cy="{cy}" r="{r + 3}" fill="none" stroke="{GOLD}" stroke-width="1" stroke-dasharray="1 5"/></g>
<circle cx="{cx}" cy="{cy}" r="{r}" fill="#0a0a0a" stroke="url(#gold-{uid})" stroke-width="2.4"/>
<circle cx="{cx}" cy="{cy}" r="{r - 9}" fill="none" stroke="{GOLD_LO}" stroke-width=".8"/>
<circle class="glint" cx="{cx}" cy="{cy}" r="{r - 9}" fill="none" pathLength="1000" stroke="#fff4c4" stroke-width="2" stroke-linecap="round"
  stroke-dasharray="120 1880" style="animation-duration:{6 + i}s;animation-delay:-{i * 1.7:.1f}s" filter="url(#glow-{uid})"/>
<text x="{cx}" y="{cy + 10}" text-anchor="middle" font-size="{30 if len(str(value)) <= 3 else 23 if len(str(value)) == 4 else 19}" font-weight="700" fill="url(#goldv-{uid})">{value}</text>
<text x="{cx}" y="{cy + r + 26}" text-anchor="middle" font-size="11.5" letter-spacing="3" fill="{MUTED}">{label}</text>
</g>"""


def lang_eclipse(cx, cy, r, langs, uid):
    circ = 2 * math.pi * r
    gap = 4
    arcs, legend, offset = [], [], 0.0
    for i, (name, share) in enumerate(langs):
        seg = max(share * circ - gap, 1.5)
        color = SHADES[min(i, len(SHADES) - 1)]
        arcs.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="15" '
            f'stroke-dasharray="{f(seg)} {f(circ)}" '
            f'transform="rotate({f(-90 + 360 * offset / circ + 360 * gap / 2 / circ)} {cx} {cy})"/>')
        offset += share * circ
        ly = cy - 62 + i * 24
        legend.append(
            f'<g><path d="M{cx + 125},{ly - 5} l6,6 l-6,6 l-6,-6Z" fill="{color}"/>'
            f'<text x="{cx + 139}" y="{ly + 5}" font-size="14" fill="{GOLD_HI if i == 0 else GOLD}">{name}</text>'
            f'<text x="{cx + 290}" y="{ly + 5}" text-anchor="end" font-size="13" fill="{MUTED}">{share * 100:.1f}%</text></g>')
    return f"""
<circle cx="{cx}" cy="{cy}" r="{r + 14}" fill="{GOLD}" opacity=".28" filter="url(#bloom-{uid})" class="breathe"/>
<circle cx="{cx}" cy="{cy}" r="{r + 8}" fill="#090909" stroke="url(#gold-{uid})" stroke-width="1.6"/>
{''.join(arcs)}
<circle class="glint" cx="{cx}" cy="{cy}" r="{r}" fill="none" pathLength="1000" stroke="#fff4c4" stroke-width="15" stroke-dasharray="40 1960" opacity=".55" style="animation-duration:10s"/>
<circle cx="{cx}" cy="{cy}" r="{r - 9}" fill="#0a0a0a" stroke="{GOLD_LO}" stroke-width=".8"/>
<circle cx="{cx}" cy="{cy}" r="{r - 9}" fill="#000" filter="url(#grain-{uid})" opacity=".35"/>
<text x="{cx}" y="{cy - 4}" text-anchor="middle" font-size="12" letter-spacing="3" fill="{MUTED}">TREASURY</text>
<text x="{cx}" y="{cy + 16}" text-anchor="middle" font-size="12" letter-spacing="3" fill="{MUTED}">OF TONGUES</text>
{''.join(legend)}"""


def ledger(s):
    W, H, uid = 1000, 330, "l"
    title, sweep = shine_text(500, 52, "THE ROYAL LEDGER", 26, uid, anchor="middle", spacing=6, dur=8)
    defs = gold_defs(uid) + sweep + f"""
<radialGradient id="bg-{uid}" cx=".5" cy="0" r="1"><stop offset="0" stop-color="#17140c"/><stop offset=".6" stop-color="#0a0a0a"/><stop offset="1" stop-color="#050505"/></radialGradient>
<clipPath id="clip-{uid}"><rect width="{W}" height="{H}" rx="14"/></clipPath>"""
    meds = [
        (s["repos"], "REALMS"),          # public repositories
        (s["contribs"], "DEEDS · YR"),   # contributions this year
        (s["commits"], "DECREES · YR"),  # commits this year
        (roman(s["since"]), "EST."),     # account age
    ]
    med_svg = "".join(medallion(90 + i * 130, 168, v, lbl, uid, i) for i, (v, lbl) in enumerate(meds))
    today = dt.date.today()
    stamp = f"{today.strftime('%B').upper()} {roman(today.year)}"  # month-level, so daily runs rarely diff
    body = f"""<g clip-path="url(#clip-{uid})">
<rect width="{W}" height="{H}" fill="url(#bg-{uid})"/>
<rect width="{W}" height="{H}" fill="#000" filter="url(#marble-{uid})" opacity=".22"/>
{title}
{rule(300, 700, 72, uid)}
{med_svg}
<path d="M560,110V270" stroke="{GOLD_LO}" stroke-width=".8" stroke-dasharray="2 4"/>
{lang_eclipse(660, 178, 66, s["langs"], uid)}
<text x="500" y="314" text-anchor="middle" font-size="10.5" letter-spacing="3" fill="{GOLD_LO}">SEALED {stamp} · PUBLIC RECORDS ONLY</text>
<rect x="1.5" y="1.5" width="{W - 3}" height="{H - 3}" rx="13" fill="none" stroke="url(#gold-{uid})" stroke-width="2"/>
<rect x="8" y="8" width="{W - 16}" height="{H - 16}" rx="9" fill="none" stroke="{GOLD}" stroke-width=".6" opacity=".45"/>
</g>"""
    return svg(W, H, f"Royal ledger: {s['repos']} public repositories, {s['contribs']} contributions and "
                     f"{s['commits']} commits in the last year, on GitHub since {s['since']}.", defs, body)


# ── the calendar: a year of contributions as gold facets ──────────────────
def calendar(s):
    W, H, uid = 1000, 250, "c"
    weeks = s["weeks"]
    counts = sorted(d["contributionCount"] for w in weeks for d in w["contributionDays"] if d["contributionCount"])
    q = [counts[int(len(counts) * p)] if counts else 1 for p in (.25, .5, .75)]

    def level(c):
        if c == 0:
            return 0
        return 1 + sum(c > t for t in q)

    fills = {0: "#111", 1: SHADES[5], 2: SHADES[3], 3: SHADES[2], 4: SHADES[0]}
    sx, hy = 16.4, 17.5
    x0 = (W - sx * (len(weeks) + 1)) / 2
    y0 = 76
    tris, months, last_month, last_label_col = [], [], None, -9
    for j, w in enumerate(weeks):
        for d in w["contributionDays"]:
            r = d["weekday"]
            x, y = x0 + j * sx, y0 + r * hy
            lv = level(d["contributionCount"])
            if (j + r) % 2 == 0:
                pts = f"M{f(x)},{f(y + hy)}L{f(x + sx)},{f(y)}L{f(x + 2 * sx)},{f(y + hy)}Z"
            else:
                pts = f"M{f(x)},{f(y)}L{f(x + 2 * sx)},{f(y)}L{f(x + sx)},{f(y + hy)}Z"
            glow = ' filter="url(#glow-c)"' if lv == 4 else ""
            tris.append(f'<path d="{pts}" fill="{fills[lv]}"{glow}><title>{d["date"]}: {d["contributionCount"]}</title></path>')
            m = d["date"][:7]
            if r == 0 and m != last_month:
                last_month = m
                if j < len(weeks) - 2 and j - last_label_col >= 3:
                    last_label_col = j
                    months.append(f'<text x="{f(x + sx)}" y="{y0 - 10}" font-size="11" letter-spacing="1.5" fill="{MUTED}">'
                                  f'{dt.date.fromisoformat(d["date"]).strftime("%b").upper()}</text>')
    grid_w = sx * (len(weeks) + 1)
    title, sweep = shine_text(500, 40, "A YEAR AT COURT", 20, uid, anchor="middle", spacing=6, dur=8)
    defs = gold_defs(uid) + sweep + f"""
<clipPath id="clip-{uid}"><rect width="{W}" height="{H}" rx="14"/></clipPath>
<mask id="tri-{uid}"><use href="#tris-{uid}" fill="#fff"/></mask>
<linearGradient id="band-{uid}" gradientUnits="userSpaceOnUse" x1="-260" y1="0" x2="-60" y2="0">
  <stop offset="0" stop-color="#fff4c4" stop-opacity="0"/><stop offset=".5" stop-color="#fff4c4" stop-opacity=".55"/><stop offset="1" stop-color="#fff4c4" stop-opacity="0"/>
  <animateTransform attributeName="gradientTransform" type="translate" values="0 0;1300 0;1300 0" keyTimes="0;.5;1" dur="9s" repeatCount="indefinite"/>
</linearGradient>"""
    body = f"""<g clip-path="url(#clip-{uid})">
<rect width="{W}" height="{H}" fill="#070707"/>
<rect width="{W}" height="{H}" fill="#000" filter="url(#marble-{uid})" opacity=".18"/>
{title}
{''.join(months)}
<g id="tris-{uid}" stroke="{GOLD_LO}" stroke-width=".6" stroke-opacity=".55">{''.join(tris)}</g>
<rect x="{f(x0)}" y="{y0}" width="{f(grid_w)}" height="{f(7 * hy)}" fill="url(#band-{uid})" mask="url(#tri-{uid})"/>
<text x="{f(x0)}" y="{H - 22}" font-size="13" font-style="italic" fill="{MUTED}">{s['contribs']} deeds recorded in the last twelve moons · {s['prs']} petition{'s' if s['prs'] != 1 else ''} (PRs)</text>
<g transform="translate({f(x0 + grid_w - 170)},{H - 34})">
  <text x="-8" y="12" text-anchor="end" font-size="11" fill="{MUTED}">less</text>
  {''.join(f'<path d="M{i * 22},16 L{i * 22 + 10},0 L{i * 22 + 20},16Z" fill="{fills[i]}" stroke="{GOLD_LO}" stroke-width=".6"/>' for i in range(5))}
  <text x="118" y="12" font-size="11" fill="{MUTED}">more</text>
</g>
<rect x="1.5" y="1.5" width="{W - 3}" height="{H - 3}" rx="13" fill="none" stroke="url(#gold-{uid})" stroke-width="2"/>
</g>"""
    return svg(W, H, f"Contribution calendar: {s['contribs']} contributions in the last year, drawn as gold facets.", defs, body)


def main():
    s = summarise(fetch())
    OUT.mkdir(exist_ok=True)
    (OUT / "royal-ledger.svg").write_text(ledger(s))
    (OUT / "royal-calendar.svg").write_text(calendar(s))
    print(f"repos={s['repos']} contribs={s['contribs']} commits={s['commits']} since={s['since']}")
    print("langs:", ", ".join(f"{n} {p:.0%}" for n, p in s["langs"]))


if __name__ == "__main__":
    main()
