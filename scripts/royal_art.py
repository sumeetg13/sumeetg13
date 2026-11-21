#!/usr/bin/env python3
"""Black & gold ("the-royal") SVG art for the profile README.

Pure stdlib. Run from the repo root:  python3 scripts/royal_art.py
Writes the static pieces (hero, divider, chamber plaques, footer) into assets/.
The data-driven pieces (ledger, calendar) live in scripts/royal_stats.py and
reuse the helpers below.
"""
import math
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"

# ── palette ────────────────────────────────────────────────────────────────
INK = "#050505"
ONYX = "#0c0c0c"
COAL = "#161616"
GOLD = "#d4af37"
GOLD_HI = "#f9e08b"
GOLD_LO = "#8a6a1f"
BRONZE = "#6e4f12"
MUTED = "#b89a5a"
SHADES = ["#fbe7a1", "#f2cf6b", "#d4af37", "#b8862b", "#94701f", "#6e4f12", "#4d3810"]

SERIF = "'Cinzel','Trajan Pro','Cormorant Garamond','Playfair Display',Didot,'Bodoni 72',Georgia,'Times New Roman',serif"


def f(x):
    return f"{x:.1f}".rstrip("0").rstrip(".")


# ── shared <defs> ──────────────────────────────────────────────────────────
def gold_defs(uid="g"):
    """Gold gradients, glow and grain filters. Ids are suffixed with uid."""
    return f"""
<linearGradient id="gold-{uid}" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="{GOLD_LO}"/><stop offset=".28" stop-color="{GOLD}"/>
  <stop offset=".5" stop-color="{GOLD_HI}"/><stop offset=".72" stop-color="{GOLD}"/>
  <stop offset="1" stop-color="{BRONZE}"/>
</linearGradient>
<linearGradient id="goldl-{uid}" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="1000" y2="400">
  <stop offset="0" stop-color="{GOLD_LO}"/><stop offset=".25" stop-color="{GOLD}"/>
  <stop offset=".5" stop-color="{GOLD_HI}"/><stop offset=".75" stop-color="{GOLD}"/>
  <stop offset="1" stop-color="{GOLD_LO}"/>
</linearGradient>
<linearGradient id="goldv-{uid}" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{GOLD_HI}"/><stop offset=".45" stop-color="{GOLD}"/>
  <stop offset=".55" stop-color="{GOLD_LO}"/><stop offset="1" stop-color="{GOLD}"/>
</linearGradient>
<linearGradient id="shine-{uid}" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#fff8dc" stop-opacity="0"/>
  <stop offset=".5" stop-color="#fff8dc" stop-opacity=".85"/>
  <stop offset="1" stop-color="#fff8dc" stop-opacity="0"/>
</linearGradient>
<filter id="glow-{uid}" x="-50%" y="-50%" width="200%" height="200%">
  <feGaussianBlur stdDeviation="3" result="b"/>
  <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<filter id="bloom-{uid}" x="-50%" y="-50%" width="200%" height="200%">
  <feGaussianBlur stdDeviation="9"/>
</filter>
<filter id="grain-{uid}" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency=".95" numOctaves="2" seed="4" result="n"/>
  <feColorMatrix in="n" type="matrix" values="0 0 0 0 .83  0 0 0 0 .68  0 0 0 0 .22  0 0 0 1.6 -.85" result="g"/>
  <feComposite in="g" in2="SourceGraphic" operator="in"/>
</filter>
<filter id="marble-{uid}" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="turbulence" baseFrequency=".004 .011" numOctaves="5" seed="11" result="t"/>
  <feColorMatrix in="t" type="luminanceToAlpha" result="a"/>
  <feComponentTransfer in="a" result="v"><feFuncA type="table" tableValues="0 0 0 0 0 0 .95 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0"/></feComponentTransfer>
  <feFlood flood-color="{GOLD}" flood-opacity=".55"/>
  <feComposite in2="v" operator="in" result="veins"/>
  <feComposite in="veins" in2="SourceGraphic" operator="in"/>
</filter>"""


STYLE = f"""
text{{font-family:{SERIF}}}
.spin{{transform-box:fill-box;transform-origin:center;animation:spin 60s linear infinite}}
.spin-r{{transform-box:fill-box;transform-origin:center;animation:spin 90s linear infinite reverse}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
.breathe{{animation:breathe 4.5s ease-in-out infinite alternate}}
@keyframes breathe{{from{{opacity:.55}}to{{opacity:1}}}}
.glint{{animation:glint linear infinite}}
@keyframes glint{{0%{{stroke-dashoffset:1000}}100%{{stroke-dashoffset:-1000}}}}
.dust{{animation:dust linear infinite}}
@keyframes dust{{0%{{transform:translateY(0);opacity:0}}20%{{opacity:.9}}100%{{transform:translateY(-120px);opacity:0}}}}
.draw{{animation:draw 2.4s cubic-bezier(.3,.7,.2,1) both}}
@keyframes draw{{from{{stroke-dashoffset:var(--len)}}to{{stroke-dashoffset:0}}}}
.rise{{animation:rise .9s ease-out both}}
@keyframes rise{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}
@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}
"""


def svg(w, h, label, defs, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{label}">\n'
            f"<style>{STYLE}</style>\n<defs>{defs}</defs>\n{body}\n</svg>\n")


# ── building blocks ────────────────────────────────────────────────────────
def facets(rng, W, H, cell=95, light=(0.75, 0.4), edge_bright=0.32, glints=6, uid="g"):
    """Low-poly black facets with gold seams (jittered grid, split quads)."""
    cols, rows = int(W / cell) + 2, int(H / cell) + 2
    pts = {}
    for i in range(cols + 1):
        for j in range(rows + 1):
            jx = 0 if i in (0, cols) else rng.uniform(-.42, .42) * cell
            jy = 0 if j in (0, rows) else rng.uniform(-.42, .42) * cell
            pts[i, j] = (i * cell - cell / 2 + jx, j * cell - cell / 2 + jy)
    lx, ly = light[0] * W, light[1] * H
    maxd = math.hypot(W, H)
    tris, edges = [], set()
    for i in range(cols):
        for j in range(rows):
            a, b, c, d = pts[i, j], pts[i + 1, j], pts[i + 1, j + 1], pts[i, j + 1]
            split = rng.random() < .5
            for t in ((a, b, c), (a, c, d)) if split else ((a, b, d), (b, c, d)):
                tris.append(t)
                for p, q in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
                    edges.add(tuple(sorted((p, q))))
    out = []
    for t in tris:
        cx, cy = sum(p[0] for p in t) / 3, sum(p[1] for p in t) / 3
        near = 1 - min(1, math.hypot(cx - lx, cy - ly) / (maxd * .55))
        v = int(8 + 22 * near * near + rng.uniform(0, 14))
        out.append(f'<path d="M{f(t[0][0])},{f(t[0][1])}L{f(t[1][0])},{f(t[1][1])}L{f(t[2][0])},{f(t[2][1])}Z" '
                   f'fill="rgb({v},{v},{int(v * .93)})"/>')
    edge_list = sorted(edges)
    seams = []
    for p, q in edge_list:
        mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        near = 1 - min(1, math.hypot(mx - lx, my - ly) / (maxd * .6))
        op = (.9 if rng.random() < edge_bright else .16) * (.45 + .55 * near)
        w = 1.4 if op > .4 else .7
        seams.append(f'<path d="M{f(p[0])},{f(p[1])}L{f(q[0])},{f(q[1])}" stroke="url(#goldl-{uid})" '
                     f'stroke-width="{w}" opacity="{op:.2f}"/>')
    shine = []
    for p, q in rng.sample(edge_list, min(glints, len(edge_list))):
        dur = rng.uniform(5, 11)
        shine.append(f'<path class="glint" d="M{f(p[0])},{f(p[1])}L{f(q[0])},{f(q[1])}" pathLength="1000" '
                     f'stroke="#fff4c4" stroke-width="2" stroke-linecap="round" stroke-dasharray="70 1930" '
                     f'style="animation-duration:{dur:.1f}s;animation-delay:-{rng.uniform(0, dur):.1f}s"/>')
    return (f'<g>{"".join(out)}</g>\n<g fill="none" stroke-linecap="round">{"".join(seams)}</g>\n'
            f'<g fill="none" filter="url(#glow-{uid})">{"".join(shine)}</g>')


def eclipse(cx, cy, r, uid="g", halo=True):
    """The glowing gold ring on a grainy black disc."""
    halo_svg = ""
    if halo:
        halo_svg = f"""
<radialGradient id="halo-{uid}" cx=".62" cy=".32" r=".6">
  <stop offset="0" stop-color="{GOLD}" stop-opacity=".9"/><stop offset=".55" stop-color="{GOLD_LO}" stop-opacity=".35"/>
  <stop offset="1" stop-color="{GOLD_LO}" stop-opacity="0"/></radialGradient>"""
    defs = halo_svg + f"""
<radialGradient id="disc-{uid}" cx=".5" cy=".5" r=".5"><stop offset=".8" stop-color="#0a0a0a"/><stop offset="1" stop-color="#131008"/></radialGradient>"""
    body = ""
    if halo:
        body += (f'<g class="spin"><circle cx="{cx}" cy="{cy}" r="{f(r * 1.55)}" fill="url(#halo-{uid})" '
                 f'filter="url(#grain-{uid})" opacity=".95"/></g>\n'
                 f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{GOLD}" stroke-width="12" '
                 f'filter="url(#bloom-{uid})" class="breathe"/>\n')
    body += (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#disc-{uid})"/>\n'
             f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#000" filter="url(#grain-{uid})" opacity=".25"/>\n'
             f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="url(#gold-{uid})" stroke-width="3.5"/>\n'
             f'<circle class="glint" cx="{cx}" cy="{cy}" r="{r}" fill="none" pathLength="1000" stroke="#fff4c4" '
             f'stroke-width="3" stroke-dasharray="90 1910" style="animation-duration:9s" filter="url(#glow-{uid})"/>\n')
    return defs, body


def crown(x, y, s, uid="g"):
    d = ("M0,30 L-4,6 L10,18 L20,0 L30,18 L44,6 L40,30 Z")
    return (f'<g transform="translate({x},{y}) scale({s})"><path d="{d}" fill="url(#gold-{uid})"/>'
            f'<rect x="0" y="32" width="40" height="5" rx="1.5" fill="url(#gold-{uid})"/>'
            f'<circle cx="20" cy="-1" r="3" fill="{GOLD_HI}"/><circle cx="-4" cy="5" r="2.4" fill="{GOLD_HI}"/>'
            f'<circle cx="44" cy="5" r="2.4" fill="{GOLD_HI}"/></g>')


def rule(x1, x2, y, uid="g", diamond=True):
    mid = (x1 + x2) / 2
    s = (f'<path d="M{x1},{y}H{f(mid - 14)}M{f(mid + 14)},{y}H{x2}" stroke="url(#goldl-{uid})" stroke-width="1.2"/>')
    if diamond:
        s += (f'<path d="M{f(mid)},{y - 7} l7,7 l-7,7 l-7,-7Z" fill="url(#gold-{uid})"/>'
              f'<circle cx="{f(mid - 22)}" cy="{y}" r="2" fill="{GOLD}"/><circle cx="{f(mid + 22)}" cy="{y}" r="2" fill="{GOLD}"/>')
    return s


def dust(rng, x0, x1, y0, y1, n):
    out = []
    for _ in range(n):
        dur = rng.uniform(6, 14)
        out.append(f'<circle class="dust" cx="{f(rng.uniform(x0, x1))}" cy="{f(rng.uniform(y0, y1))}" '
                   f'r="{f(rng.uniform(.6, 1.9))}" fill="{GOLD_HI}" '
                   f'style="animation-duration:{dur:.1f}s;animation-delay:-{rng.uniform(0, dur):.1f}s"/>')
    return "".join(out)


def shine_text(x, y, text, size, uid, anchor="start", spacing=0, weight=700, dur=7):
    """Gold text with a light sweep passing over it."""
    common = (f'x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" letter-spacing="{spacing}" '
              f'text-anchor="{anchor}"')
    return (f'<text {common} fill="url(#goldv-{uid})">{text}</text>'
            f'<text {common} fill="url(#sweep-{uid})" style="mix-blend-mode:screen">{text}</text>'), (
        f'<linearGradient id="sweep-{uid}" gradientUnits="userSpaceOnUse" x1="-300" y1="0" x2="-100" y2="0">'
        f'<stop offset="0" stop-color="#fff8dc" stop-opacity="0"/><stop offset=".5" stop-color="#fff8dc" stop-opacity=".9"/>'
        f'<stop offset="1" stop-color="#fff8dc" stop-opacity="0"/>'
        f'<animateTransform attributeName="gradientTransform" type="translate" values="0 0;1400 0;1400 0" '
        f'keyTimes="0;.55;1" dur="{dur}s" repeatCount="indefinite"/></linearGradient>')


# ── static pieces ──────────────────────────────────────────────────────────
def hero():
    rng = random.Random(1)
    W, H, uid = 1000, 400, "h"
    ecl_defs, ecl = eclipse(790, 198, 122, uid)
    name, sweep = shine_text(70, 178, "SUMEET GUPTA", 54, uid, spacing=6)
    mono, sweep2 = shine_text(790, 222, "SG", 88, "h2", anchor="middle", spacing=4, dur=9)
    defs = gold_defs(uid) + gold_defs("h2") + ecl_defs + sweep + sweep2 + f"""
<linearGradient id="vign-{uid}" x1="0" x2="1"><stop offset="0" stop-color="#000" stop-opacity=".82"/>
<stop offset=".55" stop-color="#000" stop-opacity=".45"/><stop offset="1" stop-color="#000" stop-opacity="0"/></linearGradient>
<clipPath id="clip-{uid}"><rect width="{W}" height="{H}" rx="14"/></clipPath>"""
    body = f"""<g clip-path="url(#clip-{uid})">
<rect width="{W}" height="{H}" fill="{INK}"/>
{facets(rng, W, H, light=(.79, .45), edge_bright=.5, uid=uid, glints=10)}
<rect width="{W}" height="{H}" fill="#000" filter="url(#marble-{uid})" opacity=".4"/>
<rect width="{W * .7}" height="{H}" fill="url(#vign-{uid})"/>
{ecl}
{mono}
<text x="790" y="262" text-anchor="middle" font-size="12" letter-spacing="5" fill="{MUTED}">EST · MMXX</text>
<g class="spin-r"><circle cx="790" cy="198" r="104" fill="none" stroke="{GOLD}" stroke-width=".8" stroke-dasharray="2 7" opacity=".7"/></g>
{crown(76, 70, .9, uid)}
{name}
<text x="72" y="214" font-size="14.5" letter-spacing="5" fill="{GOLD}">SOFTWARE ENGINEER · IIT KANPUR · MMXXIII</text>
{rule(72, 540, 240, uid)}
<text x="72" y="282" font-size="17" font-style="italic" fill="{MUTED}">Architect of scalable systems — workflow engines,</text>
<text x="72" y="306" font-size="17" font-style="italic" fill="{MUTED}">AI agents &amp; the mathematics of markets.</text>
{dust(rng, 40, 980, 120, 400, 34)}
<rect x="1.5" y="1.5" width="{W - 3}" height="{H - 3}" rx="13" fill="none" stroke="url(#gold-{uid})" stroke-width="2"/>
<rect x="8" y="8" width="{W - 16}" height="{H - 16}" rx="9" fill="none" stroke="{GOLD}" stroke-width=".6" opacity=".5"/>
</g>"""
    return svg(W, H, "Sumeet Gupta — Software Engineer, IIT Kanpur 2023. A gold eclipse ring over black faceted marble.", defs, body)


def divider():
    W, H, uid = 1000, 40, "d"
    defs = gold_defs(uid) + f"""
<linearGradient id="fadeL-{uid}" gradientUnits="userSpaceOnUse" x1="80" x2="468"><stop offset="0" stop-color="{GOLD}" stop-opacity="0"/><stop offset="1" stop-color="{GOLD}"/></linearGradient>
<linearGradient id="fadeR-{uid}" gradientUnits="userSpaceOnUse" x1="532" x2="920"><stop offset="0" stop-color="{GOLD}"/><stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></linearGradient>"""
    body = f"""
<path d="M80,20H468" stroke="url(#fadeL-{uid})" stroke-width="1.3"/>
<path d="M532,20H920" stroke="url(#fadeR-{uid})" stroke-width="1.3"/>
<path class="glint" d="M80,20H920" pathLength="1000" stroke="#fff4c4" stroke-width="2" stroke-dasharray="60 1940" style="animation-duration:6s" filter="url(#glow-{uid})"/>
<g filter="url(#glow-{uid})"><path d="M500,6 l14,14 l-14,14 l-14,-14Z" fill="url(#gold-{uid})" class="breathe"/></g>
<path d="M500,12 l8,8 l-8,8 l-8,-8Z" fill="{INK}"/>
<circle cx="500" cy="20" r="2.4" fill="{GOLD_HI}"/>
<path d="M476,20 l-6,-5 l-6,5 l6,5Z M524,20 l6,-5 l6,5 l-6,5Z" fill="{GOLD}"/>
"""
    return svg(W, H, "gold divider", defs, body)


def plaque(numeral, title, sub, uid):
    W, H = 640, 74
    defs = gold_defs(uid) + f"""
<linearGradient id="bg-{uid}" x1="0" x2="1"><stop offset="0" stop-color="#151515"/><stop offset="1" stop-color="#080808"/></linearGradient>
<clipPath id="clip-{uid}"><rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="8"/></clipPath>"""
    body = f"""
<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="8" fill="url(#bg-{uid})"/>
<g clip-path="url(#clip-{uid})">
  <rect x="2" y="2" width="{W - 4}" height="{H - 4}" fill="#000" filter="url(#marble-{uid})" opacity=".45"/>
  <rect x="-160" y="-20" width="70" height="{H + 40}" fill="url(#shine-{uid})" opacity=".22" transform="skewX(-24)">
    <animateTransform attributeName="transform" type="translate" values="0 0;900 0;900 0" keyTimes="0;.45;1" dur="7s" repeatCount="indefinite" additive="sum"/>
  </rect>
</g>
<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="8" fill="none" stroke="url(#gold-{uid})" stroke-width="1.8"/>
<rect x="7" y="7" width="{W - 14}" height="{H - 14}" rx="5" fill="none" stroke="{GOLD}" stroke-width=".6" opacity=".55"/>
<path d="M7,17 l10,-10 M{W - 7},17 l-10,-10 M7,{H - 17} l10,10 M{W - 7},{H - 17} l-10,10" stroke="{GOLD}" stroke-width="1"/>
<circle cx="44" cy="37" r="31" fill="{GOLD}" opacity=".35" filter="url(#bloom-{uid})" class="breathe"/>
<circle cx="44" cy="37" r="24" fill="#0a0a0a" stroke="url(#gold-{uid})" stroke-width="2.4"/>
<g class="spin"><circle cx="44" cy="37" r="28.5" fill="none" stroke="{GOLD}" stroke-width=".8" stroke-dasharray="1.5 4.5"/></g>
<text x="44" y="45" text-anchor="middle" font-size="21" font-weight="700" fill="url(#goldv-{uid})">{numeral}</text>
<text x="88" y="37" font-size="25" font-weight="700" letter-spacing="3" fill="url(#goldv-{uid})">{title}</text>
<text x="89" y="58" font-size="13.5" font-style="italic" fill="{MUTED}">{sub} <tspan class="breathe" fill="{GOLD}" font-style="normal">· enter the chamber ▸</tspan></text>
"""
    return svg(W, H, title, defs, body)


def footer():
    rng = random.Random(5)
    W, H, uid = 1000, 210, "f"
    ecl_defs, ecl = eclipse(500, 92, 50, uid)
    defs = gold_defs(uid) + ecl_defs + f"""
<linearGradient id="fade-{uid}" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity=".9"/><stop offset=".6" stop-color="#000" stop-opacity=".35"/><stop offset="1" stop-color="#000" stop-opacity=".8"/></linearGradient>
<clipPath id="clip-{uid}"><rect width="{W}" height="{H}" rx="14"/></clipPath>"""
    body = f"""<g clip-path="url(#clip-{uid})">
<rect width="{W}" height="{H}" fill="{INK}"/>
{facets(rng, W, H, cell=80, light=(.5, .45), uid=uid, glints=6)}
<rect width="{W}" height="{H}" fill="url(#fade-{uid})"/>
{ecl}
<text x="500" y="104" text-anchor="middle" font-size="30" font-weight="700" letter-spacing="3" fill="url(#goldv-{uid})">FIN</text>
<text x="500" y="176" text-anchor="middle" font-size="17" font-style="italic" fill="{MUTED}">long live clean code — thank you for your audience</text>
{rule(330, 670, 194, uid)}
{dust(rng, 40, 960, 60, 210, 22)}
<rect x="1.5" y="1.5" width="{W - 3}" height="{H - 3}" rx="13" fill="none" stroke="url(#gold-{uid})" stroke-width="2"/>
</g>"""
    return svg(W, H, "Fin — long live clean code", defs, body)


def main():
    OUT.mkdir(exist_ok=True)
    files = {
        "royal-hero.svg": hero(),
        "royal-divider.svg": divider(),
        "royal-footer.svg": footer(),
        "chamber-sovereign.svg": plaque("I", "THE SOVEREIGN", "who holds the throne", "c1"),
        "chamber-armoury.svg": plaque("II", "THE ARMOURY", "weapons of the realm", "c2"),
        "chamber-jewels.svg": plaque("III", "CROWN JEWELS", "treasures of the kingdom", "c3"),
        "chamber-ledger.svg": plaque("IV", "THE ROYAL LEDGER", "the kingdom in numbers", "c4"),
        "chamber-decrees.svg": plaque("V", "SEALED DECREES", "break a seal, learn your fate", "c5"),
    }
    for name, content in files.items():
        (OUT / name).write_text(content)
        print(f"wrote assets/{name} ({len(content) / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
