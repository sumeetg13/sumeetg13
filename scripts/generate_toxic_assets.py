#!/usr/bin/env python3
"""Generate the toxic / acid themed SVG assets for the profile README.

Pure stdlib. Run from the repo root:  python3 scripts/generate_toxic_assets.py
Writes into assets/.
"""
import math
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)

# palette
BG = "#050805"
PANEL = "#0b120b"
NEON = "#39ff14"
ACID = "#7cfc00"
LIME = "#b6ff3b"
DIM = "#1d3a10"
MID = "#2f6b16"
TEXT = "#a8ff60"
INK = "#030503"

MONO = "'JetBrains Mono','Fira Code',Consolas,'SF Mono',Menlo,'Courier New',monospace"

COMMON_STYLE = f"""
text{{font-family:{MONO}}}
@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}
"""

GLOW = """<filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
<feGaussianBlur stdDeviation="{s}" result="b"/>
<feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>"""


def f(x):
    return f"{x:.1f}".rstrip("0").rstrip(".")


# --------------------------------------------------------------------------
# shapes
# --------------------------------------------------------------------------
def blob(rng, cx, cy, r, points=11, jitter=0.35):
    """A smooth irregular closed blob (acid splat)."""
    pts = []
    for i in range(points):
        a = 2 * math.pi * i / points + rng.uniform(-0.15, 0.15)
        rr = r * (1 + rng.uniform(-jitter, jitter))
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    # Catmull-Rom -> cubic bezier
    d = f"M{f(pts[0][0])},{f(pts[0][1])}"
    n = len(pts)
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{f(c1[0])},{f(c1[1])} {f(c2[0])},{f(c2[1])} {f(p2[0])},{f(p2[1])}"
    return d + "Z"


def splatter(rng, cx, cy, R, color, n_streaks=16, n_drops=70):
    """Paint splash around a disc of radius R: streaks shooting outward + droplets."""
    out = []
    # core disc with ragged edge
    out.append(f'<path d="{blob(rng, cx, cy, R * 1.03, points=40, jitter=0.05)}" fill="{color}"/>')
    # streaks: elongated blobs pointing outward
    for _ in range(n_streaks):
        a = rng.uniform(0, 2 * math.pi)
        length = rng.uniform(0.12, 0.42) * R
        width = rng.uniform(0.035, 0.1) * R
        base = R * rng.uniform(0.85, 0.98)
        x0, y0 = cx + base * math.cos(a), cy + base * math.sin(a)
        x1, y1 = cx + (base + length) * math.cos(a), cy + (base + length) * math.sin(a)
        nx, ny = -math.sin(a) * width, math.cos(a) * width
        d = (f"M{f(x0 + nx)},{f(y0 + ny)} Q{f((x0 + x1) / 2 + nx * .6)},{f((y0 + y1) / 2 + ny * .6)} "
             f"{f(x1)},{f(y1)} Q{f((x0 + x1) / 2 - nx * .6)},{f((y0 + y1) / 2 - ny * .6)} {f(x0 - nx)},{f(y0 - ny)}Z")
        out.append(f'<path d="{d}" fill="{color}"/>')
    # lumpy splash blobs hugging the rim
    for _ in range(12):
        a = rng.uniform(0, 2 * math.pi)
        dist = R * rng.uniform(0.98, 1.12)
        out.append(f'<path d="{blob(rng, cx + dist * math.cos(a), cy + dist * math.sin(a), R * rng.uniform(0.05, 0.13), points=8, jitter=0.4)}" fill="{color}"/>')
    # droplets
    for _ in range(n_drops):
        a = rng.uniform(0, 2 * math.pi)
        dist = R * (1.02 + rng.expovariate(3.2))
        r = max(0.6, rng.uniform(0.004, 0.03) * R * (1.6 - min(dist / R - 1, 1)))
        out.append(f'<circle cx="{f(cx + dist * math.cos(a))}" cy="{f(cy + dist * math.sin(a))}" r="{f(r)}" fill="{color}"/>')
    return "\n".join(out)


def grunge(rng, cx, cy, R, n=55):
    """Dark ink specks and scratches across the green disc."""
    out = []
    for _ in range(n):
        a, d = rng.uniform(0, 2 * math.pi), R * math.sqrt(rng.random())
        x, y = cx + d * math.cos(a), cy + d * math.sin(a)
        if rng.random() < .3:
            L, t = rng.uniform(6, 22), rng.uniform(-.4, .4)
            out.append(f'<path d="M{f(x)},{f(y)} l{f(L * math.cos(t))},{f(L * math.sin(t))}" stroke="{INK}" stroke-width="{f(rng.uniform(.6, 1.8))}" stroke-linecap="round" opacity=".55"/>')
        else:
            out.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(rng.uniform(.6, 2.6))}" fill="{INK}" opacity="{rng.uniform(.25, .6):.2f}"/>')
    return "\n".join(out)


def biohazard(mask_id, size=1.0):
    """Biohazard symbol in a 60-unit box centred on 0,0 as a <mask> def + use-rect.

    Returns (defs, body) where body is a rect filled with currentColor masked
    into the symbol shape.
    """
    angles = [-90, 30, 150]
    white, black = [], []
    for a in angles:
        r = math.radians(a)
        white.append(f'<circle cx="{f(11 * math.cos(r))}" cy="{f(11 * math.sin(r))}" r="15" fill="#fff"/>')
        black.append(f'<circle cx="{f(15 * math.cos(r))}" cy="{f(15 * math.sin(r))}" r="10.5" fill="#000"/>')
    slits = []
    for a in angles:
        slits.append(f'<rect x="-0.8" y="-13" width="1.6" height="13" fill="#000" transform="rotate({a + 90})"/>')
    defs = (f'<mask id="{mask_id}" maskUnits="userSpaceOnUse" x="-40" y="-40" width="80" height="80">'
            + "".join(white) + "".join(black)
            + '<circle r="9.2" fill="none" stroke="#fff" stroke-width="3.2"/>'
            + "".join(slits)
            + '<circle r="3.4" fill="#000"/>'
            + "</mask>")
    body = f'<rect x="-40" y="-40" width="80" height="80" mask="url(#{mask_id})"/>'
    return defs, body


def drip_path(x, w, length):
    """A drip hanging from y=0: a sheet edge narrowing to a rounded bulb."""
    h = length
    return (f"M{f(x - w)},0 C{f(x - w * .55)},{f(h * .35)} {f(x - w * .32)},{f(h * .7)} {f(x - w * .42)},{f(h * .86)} "
            f"A{f(w * .42)},{f(w * .42)} 0 1 0 {f(x + w * .42)},{f(h * .86)} "
            f"C{f(x + w * .32)},{f(h * .7)} {f(x + w * .55)},{f(h * .35)} {f(x + w)},0Z")


def drips(rng, width, count, color, max_len, top=0, cls="drip"):
    out = []
    for i in range(count):
        x = rng.uniform(20, width - 20)
        w = rng.uniform(5, 12)
        L = rng.uniform(0.35, 1.0) * max_len
        dur = rng.uniform(4.5, 8.5)
        delay = -rng.uniform(0, dur)
        out.append(f'<g transform="translate(0,{top})"><path class="{cls}" d="{drip_path(x, w, L)}" fill="{color}" '
                   f'style="animation-duration:{dur:.1f}s;animation-delay:{delay:.1f}s"/>'
                   f'<circle class="drop" cx="{f(x)}" cy="{f(L * .86)}" r="{f(w * .38)}" fill="{color}" '
                   f'style="animation-duration:{dur:.1f}s;animation-delay:{delay:.1f}s"/></g>')
    return "\n".join(out)


def bubbles(rng, x0, x1, y_bottom, rise, count, color):
    out = []
    for _ in range(count):
        x = rng.uniform(x0, x1)
        r = rng.uniform(1.5, 5)
        dur = rng.uniform(3.5, 8)
        delay = -rng.uniform(0, dur)
        out.append(f'<circle class="bub" cx="{f(x)}" cy="{f(y_bottom)}" r="{f(r)}" fill="none" stroke="{color}" '
                   f'stroke-width="1.2" style="--rise:-{rise}px;animation-duration:{dur:.1f}s;animation-delay:{delay:.1f}s"/>')
    return "\n".join(out)


def hazard_band(y, h, width, pid, speed=6):
    """Black/green diagonal hazard stripes, scrolling."""
    return (f'<defs><pattern id="{pid}" width="28" height="{h}" patternUnits="userSpaceOnUse">'
            f'<rect width="28" height="{h}" fill="{INK}"/>'
            f'<path d="M0,{h} L14,0 L28,0 L14,{h}Z" fill="{NEON}"/></pattern></defs>'
            f'<g><rect class="band" x="-56" y="{y}" width="{width + 112}" height="{h}" fill="url(#{pid})" '
            f'style="animation-duration:{speed}s"/></g>')


DRIP_CSS = """
.drip{transform-box:fill-box;transform-origin:50% 0;animation:drip ease-in infinite}
@keyframes drip{0%{transform:scaleY(.25)}70%{transform:scaleY(1)}100%{transform:scaleY(.25)}}
.drop{animation:fall ease-in infinite;opacity:0}
@keyframes fall{0%,66%{opacity:0;transform:translateY(0)}70%{opacity:1;transform:translateY(0)}100%{opacity:0;transform:translateY(140px)}}
.bub{animation:rise linear infinite}
@keyframes rise{0%{transform:translateY(0);opacity:0}15%{opacity:.9}100%{transform:translateY(var(--rise));opacity:0}}
.band{animation:band linear infinite}
@keyframes band{to{transform:translateX(56px)}}
.pulse{animation:pulse 2.8s ease-in-out infinite alternate}
@keyframes pulse{from{opacity:.45}to{opacity:1}}
.spin{transform-box:fill-box;transform-origin:center;animation:spin 40s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.flick{animation:flick 5s steps(1) infinite}
@keyframes flick{0%,100%{opacity:1}92%{opacity:.35}93%{opacity:1}95%{opacity:.5}96%{opacity:1}}
.blink{animation:blink 1.1s steps(1) infinite}
@keyframes blink{50%{opacity:0}}
"""


def svg(w, h, label, body, extra_css=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{label}">\n'
            f"<style>{COMMON_STYLE}{DRIP_CSS}{extra_css}</style>\n{body}\n</svg>\n")


# --------------------------------------------------------------------------
# hero
# --------------------------------------------------------------------------
def hero():
    rng = random.Random(13)
    W, H = 1000, 380
    cx, cy, R = 205, 196, 118
    mdefs, mbody = biohazard("bio")
    grid = "".join(f'<path d="M{x},0V{H}" stroke="{DIM}" stroke-width=".6" opacity=".45"/>' for x in range(0, W + 1, 40))
    grid += "".join(f'<path d="M0,{y}H{W}" stroke="{DIM}" stroke-width=".6" opacity=".45"/>' for y in range(0, H + 1, 40))
    body = f"""<defs>
<radialGradient id="halo" cx="{cx / W}" cy="{cy / H}" r=".42"><stop offset="0" stop-color="{NEON}" stop-opacity=".35"/><stop offset="1" stop-color="{NEON}" stop-opacity="0"/></radialGradient>
<radialGradient id="disc" cx=".45" cy=".4" r=".7"><stop offset="0" stop-color="{LIME}"/><stop offset=".55" stop-color="{NEON}"/><stop offset="1" stop-color="#1fae0b"/></radialGradient>
<linearGradient id="fade" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="{BG}" stop-opacity="0"/><stop offset="1" stop-color="{BG}"/></linearGradient>
{GLOW.format(s=3)}
{mdefs}
</defs>
<rect width="{W}" height="{H}" fill="{BG}"/>
{grid}
<rect width="{W}" height="{H}" fill="url(#halo)"/>
<g class="pulse">{splatter(rng, cx, cy, R, "url(#disc)")}</g>
{grunge(rng, cx, cy, R * .9)}
<circle cx="{cx}" cy="{cy}" r="{R * .93}" fill="none" stroke="{INK}" stroke-width="9"/>
<g transform="translate({cx},{cy}) scale(2.95)"><g class="spin" fill="{INK}">{mbody}</g></g>
{drips(rng, W, 15, NEON, 70)}
<rect x="0" y="0" width="{W}" height="6" fill="{NEON}"/>
<g class="flick" filter="url(#glow)">
<text x="410" y="150" font-size="58" font-weight="800" fill="{NEON}" letter-spacing="2">SUMEET GUPTA</text>
</g>
<text x="413" y="188" font-size="17" fill="{TEXT}" letter-spacing="3">SOFTWARE ENGINEER · IIT KANPUR '23</text>
<g transform="translate(413,212)">
<rect width="420" height="34" rx="4" fill="none" stroke="{NEON}" stroke-width="1.5" stroke-dasharray="6 4"/>
<text x="14" y="22" font-size="13.5" fill="{NEON}" letter-spacing="1.5">⚠ HAZARD CLASS 6 · HIGHLY REACTIVE CODE</text>
</g>
<text x="413" y="276" font-size="13" fill="{MID}" letter-spacing="1">&gt; containment: java · node · python · camunda · aws<tspan class="blink" fill="{NEON}"> █</tspan></text>
{bubbles(rng, 400, 980, H - 28, 55, 20, ACID)}
{hazard_band(H - 22, 22, W, "hz")}
"""
    return svg(W, H, "Sumeet Gupta — Software Engineer, IIT Kanpur 2023. A biohazard emblem splashed in neon acid.", body)


# --------------------------------------------------------------------------
# divider
# --------------------------------------------------------------------------
def divider():
    rng = random.Random(7)
    W, H = 1000, 70
    mdefs, mbody = biohazard("bio-d")
    body = f"""<defs>
<linearGradient id="l" x1="0" x2="1"><stop offset="0" stop-color="{NEON}" stop-opacity="0"/><stop offset=".5" stop-color="{NEON}"/><stop offset="1" stop-color="{NEON}" stop-opacity="0"/></linearGradient>
{GLOW.format(s=2)}{mdefs}
</defs>
<rect x="60" y="14" width="880" height="3" fill="url(#l)" filter="url(#glow)"/>
{drips(rng, 880, 9, NEON, 38, top=16).replace('translate(0,16)', 'translate(60,16)')}
<g transform="translate(500,16)"><circle r="15" fill="{NEON}" filter="url(#glow)"/><g transform="scale(.42)"><g class="spin" fill="{INK}">{mbody}</g></g></g>
"""
    return svg(W, H, "acid divider", body)


# --------------------------------------------------------------------------
# chapter headers
# --------------------------------------------------------------------------
def chapter(num, title, sub, name):
    W, H = 640, 74
    mdefs, mbody = biohazard(f"bio-{name}")
    body = f"""<defs>{GLOW.format(s=2)}{mdefs}
<pattern id="hz-{name}" width="14" height="74" patternUnits="userSpaceOnUse" patternTransform="skewX(-30)"><rect width="14" height="74" fill="{INK}"/><rect width="7" height="74" fill="{NEON}"/></pattern>
</defs>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="10" fill="{PANEL}" stroke="{MID}" stroke-width="1.5"/>
<rect x="1" y="1" width="12" height="{H - 2}" rx="4" fill="url(#hz-{name})"/>
<g transform="translate(52,37)"><circle r="25" fill="{NEON}" class="pulse" filter="url(#glow)"/><g transform="scale(.7)"><g class="spin" fill="{INK}">{mbody}</g></g></g>
<text x="92" y="35" font-size="25" font-weight="800" fill="{NEON}" filter="url(#glow)" letter-spacing="1"><tspan fill="{MID}">{num} //</tspan> {title}</text>
<text x="93" y="58" font-size="13" fill="{TEXT}" letter-spacing="1.5">{sub}  <tspan class="pulse" fill="{NEON}">· click to unseal ▸</tspan></text>
"""
    return svg(W, H, title, body)


# --------------------------------------------------------------------------
# footer
# --------------------------------------------------------------------------
def footer():
    rng = random.Random(21)
    W, H = 1000, 150
    pool = "M0,150 L0,96 " + " ".join(
        f"Q{x - 25},{96 + rng.uniform(-10, 8):.0f} {x},{96 + rng.uniform(-4, 4):.0f}" for x in range(50, W + 1, 50)
    ) + f" L{W},150Z"
    body = f"""<defs>{GLOW.format(s=3)}
<linearGradient id="pool" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="{NEON}"/><stop offset="1" stop-color="#0c3d05"/></linearGradient></defs>
<rect width="{W}" height="{H}" fill="{BG}"/>
{hazard_band(0, 18, W, "hzf", speed=8)}
{drips(rng, W, 12, NEON, 40, top=18)}
<text x="500" y="72" text-anchor="middle" font-size="22" font-weight="800" fill="{NEON}" filter="url(#glow)" letter-spacing="4" class="flick">END OF TRANSMISSION · STAY TOXIC ☣</text>
<path d="{pool}" fill="url(#pool)" opacity=".9"/>
{bubbles(rng, 20, 980, 140, 40, 26, LIME)}
<text x="500" y="132" text-anchor="middle" font-size="12" fill="{INK}" letter-spacing="2">dispose of this README responsibly</text>
"""
    return svg(W, H, "End of transmission — stay toxic", body)


def main():
    files = {
        "toxic-hero.svg": hero(),
        "toxic-divider.svg": divider(),
        "toxic-footer.svg": footer(),
        "lab-subject.svg": chapter("01", "SUBJECT FILE", "the specimen behind the code", "subject"),
        "lab-arsenal.svg": chapter("02", "THE ARSENAL", "compounds handled daily", "arsenal"),
        "lab-specimens.svg": chapter("03", "SPECIMENS", "experiments that escaped the lab", "specimens"),
        "lab-readings.svg": chapter("04", "RADIATION READINGS", "geiger counter on my commits", "readings"),
        "lab-vials.svg": chapter("05", "PICK A VIAL", "drink at your own risk", "vials"),
    }
    for name, content in files.items():
        (OUT / name).write_text(content)
        print(f"wrote assets/{name} ({len(content) / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
