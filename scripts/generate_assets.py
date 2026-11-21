#!/usr/bin/env python3
"""Generates the sakura artwork used by the profile README.

    python3 scripts/generate_assets.py          # SVGs only (stdlib)
    python3 scripts/generate_assets.py --gifs   # also GIFs (needs Pillow)

Everything is seeded, so re-running gives identical files.
"""
import html
import math
import random
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)

PINKS = ["#ffb7c5", "#ffc0cb", "#f8a1be", "#ffd1dc", "#f48fb1", "#fbc4d4"]
PETAL = "M0,10 C-6,6 -7,-3 -3,-8 L0,-5 L3,-8 C7,-3 6,6 0,10 Z"
REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"


def flower(x, y, s, fill, center="#c2185b", cls=""):
    petals = "".join(
        f'<path d="{PETAL}" transform="rotate({k * 72}) translate(0,-10)"/>' for k in range(5)
    )
    c = f' class="{cls}"' if cls else ""
    return (
        f'<g transform="translate({x:.1f},{y:.1f}) scale({s:.2f})"><g{c} fill="{fill}">{petals}'
        f'<circle r="3.2" fill="{center}"/></g></g>'
    )


def falling_petals(rng, n, w, h, size=(0.7, 1.4)):
    out = []
    for _ in range(n):
        x = rng.uniform(0, w)
        dur = rng.uniform(7, 14)
        delay = -rng.uniform(0, dur)
        sway = rng.uniform(4, 7)
        s = rng.uniform(*size)
        out.append(
            f'<g transform="translate({x:.0f},0)"><g class="fall" style="animation-duration:{dur:.1f}s;'
            f'animation-delay:{delay:.1f}s"><g class="sway" style="animation-duration:{sway:.1f}s">'
            f'<path class="spin" d="{PETAL}" fill="{rng.choice(PINKS)}" opacity="{rng.uniform(.65, 1):.2f}" '
            f'transform="scale({s:.2f})" style="animation-duration:{rng.uniform(3, 6):.1f}s"/></g></g></g>'
        )
    return "".join(out)


FALL_CSS = """
.fall{animation:fall linear infinite}
.sway{animation:sway ease-in-out infinite alternate}
.spin{animation:spin linear infinite;transform-box:fill-box;transform-origin:center}
@keyframes fall{from{transform:translateY(-30px)}to{transform:translateY(%dpx)}}
@keyframes sway{from{transform:translateX(-26px)}to{transform:translateX(26px)}}
@keyframes spin{from{transform:rotate(0) scaleX(1)}50%%{transform:rotate(180deg) scaleX(.35)}to{transform:rotate(360deg) scaleX(1)}}
@media (prefers-reduced-motion: reduce){.fall{display:none}}
"""


def branch(rng, x0, y0, angle, length, width, depth, segs, tips):
    """Recursive branch; appends (path, width) to segs and tip points to tips."""
    x1 = x0 + math.cos(angle) * length
    y1 = y0 + math.sin(angle) * length
    mx = (x0 + x1) / 2 + rng.uniform(-length, length) * 0.15
    my = (y0 + y1) / 2 + rng.uniform(-length, length) * 0.15
    segs.append((f"M{x0:.1f},{y0:.1f} Q{mx:.1f},{my:.1f} {x1:.1f},{y1:.1f}", width))
    tips.append((x1, y1, depth))
    if depth <= 0:
        return
    for _ in range(rng.choice([2, 2, 3])):
        branch(rng, x1, y1, angle + rng.uniform(-0.65, 0.65), length * rng.uniform(0.6, 0.8),
               width * 0.62, depth - 1, segs, tips)


def blossom_branch(rng, x, y, angle, length, depth, flower_scale):
    segs, tips = [], []
    branch(rng, x, y, angle, length, 9, depth, segs, tips)
    paths = "".join(
        f'<path d="{d}" stroke="#2b1420" stroke-width="{w:.1f}" fill="none" stroke-linecap="round"/>'
        for d, w in segs
    )
    blooms = []
    for tx, ty, d in tips:
        if d <= 2:
            for _ in range(3 if d == 0 else 2):
                blooms.append(flower(tx + rng.uniform(-12, 12), ty + rng.uniform(-10, 10),
                                     flower_scale * rng.uniform(0.6, 1.1), rng.choice(PINKS),
                                     cls="bloom"))
    return paths + "".join(blooms)


def hero():
    rng = random.Random(13)
    W, H = 1000, 360
    stars = "".join(
        f'<circle cx="{rng.uniform(0, W):.0f}" cy="{rng.uniform(0, 170):.0f}" r="{rng.uniform(.6, 1.6):.1f}" '
        f'fill="#fff" class="tw" style="animation-delay:-{rng.uniform(0, 4):.1f}s"/>'
        for _ in range(60)
    )
    left = blossom_branch(rng, -10, 14, 0.12, 105, 4, 0.48)
    right = blossom_branch(rng, W + 10, 345, math.pi + 0.6, 85, 3, 0.45)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Sumeet Gupta — Software Engineer, IIT Kanpur">
<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#140b24"/><stop offset=".45" stop-color="#3b1c4a"/>
<stop offset=".8" stop-color="#8a3f6e"/><stop offset="1" stop-color="#e88aae"/></linearGradient>
<radialGradient id="veil"><stop offset="0" stop-color="#140b24" stop-opacity=".55"/><stop offset="1" stop-color="#140b24" stop-opacity="0"/></radialGradient>
<radialGradient id="glow"><stop offset="0" stop-color="#ffe3ee" stop-opacity=".55"/><stop offset="1" stop-color="#ffe3ee" stop-opacity="0"/></radialGradient>
<clipPath id="card"><rect width="{W}" height="{H}" rx="22"/></clipPath>
</defs>
<style>{FALL_CSS % (H + 40)}
.tw{{animation:tw 4s ease-in-out infinite alternate}}
@keyframes tw{{from{{opacity:.15}}to{{opacity:.9}}}}
.swayL{{animation:bL 6s ease-in-out infinite alternate;transform-origin:0 20px}}
.swayR{{animation:bL 7s ease-in-out infinite alternate-reverse;transform-origin:{W}px 300px}}
@keyframes bL{{from{{transform:rotate(-1.4deg)}}to{{transform:rotate(1.6deg)}}}}
.bloom{{animation:pulse 5s ease-in-out infinite alternate;transform-box:fill-box;transform-origin:center}}
@keyframes pulse{{from{{transform:scale(.92)}}to{{transform:scale(1.06)}}}}
.up{{animation:up 1.6s ease-out backwards}}
@keyframes up{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:none}}}}
text{{font-family:'Segoe UI',-apple-system,'Helvetica Neue',Arial,'Hiragino Sans','Noto Sans JP',sans-serif}}
{REDUCED}
</style>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="url(#sky)"/>
{stars}
<circle cx="820" cy="96" r="120" fill="url(#glow)"/>
<circle cx="820" cy="96" r="46" fill="#ffeef4"/>
<circle cx="806" cy="86" r="8" fill="#f6d9e4"/><circle cx="836" cy="110" r="5" fill="#f6d9e4"/>
<text x="500" y="250" text-anchor="middle" font-size="300" fill="#ffd1dc" opacity=".06">桜</text>
<path d="M0,300 C150,262 260,292 400,276 C560,258 640,300 800,284 C900,274 960,288 1000,280 L1000,360 L0,360Z" fill="#2a1336" opacity=".75"/>
<path d="M0,326 C180,304 330,334 520,318 C700,304 820,336 1000,318 L1000,360 L0,360Z" fill="#1b0d26"/>
<g class="swayL">{left}</g>
<g class="swayR">{right}</g>
<ellipse cx="500" cy="200" rx="330" ry="110" fill="url(#veil)"/>
<g class="up" style="animation-delay:.2s"><text x="500" y="122" text-anchor="middle" font-size="17" fill="#ffc6da" letter-spacing="8">ようこそ · WELCOME TO MY GARDEN</text></g>
<g class="up" style="animation-delay:.6s"><text x="500" y="190" text-anchor="middle" font-size="68" font-weight="700" fill="#fff0f6" letter-spacing="2">Sumeet Gupta</text></g>
<g class="up" style="animation-delay:1.1s"><text x="500" y="226" text-anchor="middle" font-size="16" fill="#ffd1dc" letter-spacing="6">SOFTWARE ENGINEER  ✿  IIT KANPUR '23</text></g>
<g class="up" style="animation-delay:1.6s"><text x="500" y="256" text-anchor="middle" font-size="15" font-style="italic" fill="#ffc6da">workflow engines · scalable systems · quant curiosity · AI agents</text></g>
{falling_petals(rng, 38, W, H)}
</g>
</svg>"""
    (OUT / "sakura-hero.svg").write_text(svg)


def divider():
    rng = random.Random(7)
    W, H = 1000, 64
    buds = "".join(flower(x, 32 + rng.uniform(-3, 3), rng.uniform(.35, .5), rng.choice(PINKS))
                   for x in (300, 380, 620, 700))
    drift = "".join(
        f'<path class="drift" d="{PETAL}" fill="{rng.choice(PINKS)}" style="animation-duration:{rng.uniform(9, 16):.1f}s;'
        f'animation-delay:-{rng.uniform(0, 16):.1f}s" transform="translate(0,{rng.uniform(10, 54):.0f}) scale({rng.uniform(.5, .9):.2f})"/>'
        for _ in range(9)
    )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="cherry blossom divider">
<defs><linearGradient id="l" x1="0" x2="1"><stop offset="0" stop-color="#f48fb1" stop-opacity="0"/>
<stop offset=".5" stop-color="#f48fb1"/><stop offset="1" stop-color="#f48fb1" stop-opacity="0"/></linearGradient></defs>
<style>
.drift{{animation:drift linear infinite;transform-box:fill-box}}
@keyframes drift{{from{{translate:-40px 0;rotate:0deg}}to{{translate:{W + 40}px 12px;rotate:720deg}}}}
.rose{{animation:rot 14s linear infinite;transform-box:fill-box;transform-origin:center}}
@keyframes rot{{to{{transform:rotate(360deg)}}}}
{REDUCED}
</style>
<path d="M120,32 C300,26 400,38 500,32 C600,26 700,38 880,32" stroke="url(#l)" stroke-width="2" fill="none"/>
{buds}
<g transform="translate(500,32) scale(.9)"><g class="rose" fill="#f48fb1">{''.join(f'<path d="{PETAL}" transform="rotate({k * 72}) translate(0,-10)"/>' for k in range(5))}<circle r="3.2" fill="#c2185b"/></g></g>
{drift}
</svg>"""
    (OUT / "sakura-divider.svg").write_text(svg)


CHAPTERS = [
    ("壱", "about", "The Gardener", "who tends this place"),
    ("弐", "toolbox", "The Toolbox", "everything I've built with"),
    ("参", "projects", "Things I've Grown", "projects from the garden"),
    ("肆", "stats", "Seasons in Numbers", "contributions & streaks"),
    ("伍", "omikuji", "Draw an Omikuji", "a fortune slip, just for you"),
    ("陸", "guestbook", "Leave a Petal", "sign the petal wall"),
]


def chapter_titles():
    for i, (kanji, slug, title, sub) in enumerate(CHAPTERS):
        title, sub = html.escape(title), html.escape(sub)
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 74" width="640" height="74" role="img" aria-label="{title}">
<style>
text{{font-family:'Segoe UI',-apple-system,'Helvetica Neue',Arial,'Hiragino Sans','Noto Sans JP',sans-serif}}
.r{{animation:rot 12s linear infinite;transform-box:fill-box;transform-origin:center}}
@keyframes rot{{to{{transform:rotate(360deg)}}}}
.g{{animation:g 2.6s ease-in-out infinite alternate}}
@keyframes g{{from{{opacity:.35}}to{{opacity:1}}}}
{REDUCED}
</style>
<circle cx="37" cy="37" r="31" fill="#f48fb1" opacity=".16"/>
<g transform="translate(37,37) scale(1.25)"><g class="r" fill="#f8a1be" style="animation-delay:-{i * 2}s">{''.join(f'<path d="{PETAL}" transform="rotate({k * 72}) translate(0,-10)"/>' for k in range(5))}</g></g>
<text x="37" y="45" text-anchor="middle" font-size="22" font-weight="700" fill="#8e1946">{kanji}</text>
<text x="84" y="36" font-size="27" font-weight="700" fill="#e75480">{title}</text>
<text x="85" y="60" font-size="14" fill="#c2789a" letter-spacing="1.5">{sub}  <tspan class="g">· tap to unfold ✿</tspan></text>
</svg>"""
        (OUT / f"chapter-{slug}.svg").write_text(svg)


def footer():
    rng = random.Random(21)
    W, H = 1000, 150
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="petals falling into the sunset">
<defs><linearGradient id="f" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e88aae" stop-opacity="0"/>
<stop offset=".55" stop-color="#8a3f6e"/><stop offset="1" stop-color="#140b24"/></linearGradient></defs>
<style>{FALL_CSS % (H + 30)}
text{{font-family:'Segoe UI',-apple-system,'Helvetica Neue',Arial,'Hiragino Sans','Noto Sans JP',sans-serif}}
{REDUCED}
</style>
<path d="M0,40 C200,10 320,60 500,36 C700,10 820,56 1000,30 L1000,150 L0,150Z" fill="url(#f)"/>
<text x="500" y="118" text-anchor="middle" font-size="15" fill="#ffd1dc" letter-spacing="6">THANK YOU FOR WALKING THROUGH  ·  またね</text>
{falling_petals(rng, 22, W, H, (.5, 1.0))}
</svg>"""
    (OUT / "sakura-footer.svg").write_text(svg)


# --------------------------------------------------------------------------- GIFs

def gifs():
    from PIL import Image, ImageDraw, ImageFilter

    def bez(p0, p1, p2, p3, n=8):
        return [tuple((1 - t) ** 3 * a + 3 * (1 - t) ** 2 * t * b + 3 * (1 - t) * t * t * c + t ** 3 * d
                      for a, b, c, d in zip(p0, p1, p2, p3)) for t in (i / n for i in range(n + 1))]

    petal_pts = (bez((0, 10), (-6, 6), (-7, -3), (-3, -8)) + [(0, -5)]
                 + bez((3, -8), (7, -3), (6, 6), (0, 10)))

    def petal(draw, x, y, s, rot, squash, fill):
        c, si = math.cos(rot), math.sin(rot)
        pts = [(x + (px * squash * c - py * si) * s, y + (px * squash * si + py * c) * s) for px, py in petal_pts]
        draw.polygon(pts, fill=fill)

    def hexc(h, a=255):
        h = h.lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)

    def sky(w, h, stops):
        img = Image.new("RGBA", (w, h))
        d = ImageDraw.Draw(img)
        for y in range(h):
            t = y / (h - 1)
            for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
                if t0 <= t <= t1:
                    k = (t - t0) / (t1 - t0)
                    a, b = hexc(c0), hexc(c1)
                    d.line([(0, y), (w, y)], fill=tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(4)))
                    break
        return img

    def tree_scene(path, W, H, seed, frames=72, n_petals=70, window=False):
        S = 2
        w, h = W * S, H * S
        rng = random.Random(seed)
        base = sky(w, h, [(0, "#140b24"), (.5, "#3b1c4a"), (.85, "#8a3f6e"), (1, "#e88aae")])
        d = ImageDraw.Draw(base)
        for _ in range(70):
            x, y, r = rng.uniform(0, w), rng.uniform(0, h * .5), rng.uniform(1, 2.6)
            d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, rng.randint(70, 220)))
        mx, my, mr = w * .74, h * .22, w * .1
        glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse([mx - mr * 2, my - mr * 2, mx + mr * 2, my + mr * 2], fill=(255, 220, 235, 70))
        base = Image.alpha_composite(base, glow.filter(ImageFilter.GaussianBlur(w * .04)))
        d = ImageDraw.Draw(base)
        d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=hexc("#ffeef4"))
        d.polygon([(0, h * .86)] + [(x, h * .84 + math.sin(x / w * 6.2) * h * .025) for x in range(0, w + 1, 8)]
                  + [(w, h), (0, h)], fill=hexc("#2a1336"))

        # tree
        tree = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        td = ImageDraw.Draw(tree)
        tips = []

        def grow(x0, y0, ang, ln, wd, depth):
            x1, y1 = x0 + math.cos(ang) * ln, y0 + math.sin(ang) * ln
            steps = 6
            for i in range(steps):
                t0, t1 = i / steps, (i + 1) / steps
                td.line([(x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0), (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1)],
                         fill=hexc("#2b1420"), width=max(2, int(wd * (1 - .3 * t0))))
            tips.append((x1, y1, depth))
            if depth:
                for _ in range(rng.choice([2, 2, 3])):
                    grow(x1, y1, ang + rng.uniform(-.6, .6), ln * rng.uniform(.66, .8), wd * .66, depth - 1)

        tx = w * (.36 if not window else .2)
        grow(tx, h * .9, -math.pi / 2 + (0 if not window else .45), h * .22, w * .045, 6)
        canopy = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        cd = ImageDraw.Draw(canopy)
        shades = [("#a8406b", 0), ("#d9668f", 0), ("#f48fb1", 1), ("#f8a1be", 1), ("#f9b0c6", 2), ("#ffc0cb", 2), ("#ffd6e2", 3)]
        blobs = []
        for x, y, dep in tips:
            if dep <= 3:
                for _ in range(26 if dep <= 1 else 8):
                    c, layer = rng.choice(shades)
                    blobs.append((layer, x + rng.gauss(0, w * .03), y + rng.gauss(0, w * .022) - layer * 3,
                                  rng.uniform(w * .005, w * .012), c))
        for layer, cx, cy, r, c in sorted(blobs):  # dark underside first, highlights on top
            cd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=hexc(c, rng.randint(200, 255)))
        for x, y, dep in tips:
            if dep <= 1 and rng.random() < .22:
                fx, fy = x + rng.uniform(-14, 14), y + rng.uniform(-14, 14)
                for k in range(5):
                    petal(cd, fx + 7 * math.sin(k * 1.2566), fy - 7 * math.cos(k * 1.2566), .9, k * 1.2566, 1,
                          hexc("#fff0f5"))
                cd.ellipse([fx - 2.5, fy - 2.5, fx + 2.5, fy + 2.5], fill=hexc("#e75480"))
        base = Image.alpha_composite(base, tree)
        base = Image.alpha_composite(base, canopy)
        d = ImageDraw.Draw(base)
        for _ in range(60):  # fallen petals
            petal(d, rng.uniform(0, w), rng.uniform(h * .89, h * .99), rng.uniform(.9, 1.4), rng.uniform(0, 6.3), .6,
                  hexc(rng.choice(PINKS), 200))

        petals = [dict(x=rng.uniform(-.1, 1.05) * w, ph=rng.random(), amp=rng.uniform(10, 40) * S,
                       wob=rng.choice([1, 2]), spin=rng.choice([1, 2, 3]), s=rng.uniform(.8, 1.4) * S / 2,
                       wind=rng.choice([0, 1]), c=hexc(rng.choice(PINKS), rng.randint(190, 255)))
                  for _ in range(n_petals)]
        out = []
        for f in range(frames):
            t = f / frames
            fr = base.copy()
            fd = ImageDraw.Draw(fr)
            for p in petals:
                u = (p["ph"] + t) % 1
                y = -20 * S + u * (h + 40 * S)
                x = (p["x"] + p["amp"] * math.sin(2 * math.pi * (p["wob"] * t + p["ph"]))
                     + p["wind"] * u * w * .15)
                petal(fd, x, y, p["s"] * 1.4, 2 * math.pi * (p["spin"] * t + p["ph"]),
                      .35 + .65 * abs(math.cos(2 * math.pi * (p["spin"] * t + p["ph"]))), p["c"])
            fr = fr.resize((W, H), Image.LANCZOS)
            if window:  # round "moon window": hard-edged circle, corners keyed out below
                bg = Image.new("RGBA", (W, H), (0, 255, 0, 255))
                mask = Image.new("L", (W, H), 0)
                ImageDraw.Draw(mask).ellipse([3, 3, W - 4, H - 4], fill=255)
                bg.paste(fr, (0, 0), mask)
                ImageDraw.Draw(bg).ellipse([2, 2, W - 3, H - 3], outline=hexc("#f48fb1"), width=4)
                fr = bg
            out.append(fr.convert("RGB"))
        pal = out[len(out) // 2].quantize(colors=255, method=Image.Quantize.MEDIANCUT)
        q = [o.quantize(palette=pal, dither=Image.Dither.NONE) for o in out]
        extra = {}
        if window:  # make the square corners transparent
            extra["transparency"] = q[0].getpixel((0, 0))
        q[0].save(OUT / path, save_all=True, append_images=q[1:], duration=70, loop=0, optimize=True,
                  disposal=1, **extra)

    tree_scene("sakura-tree.gif", 480, 360, 3)
    tree_scene("sakura-window.gif", 300, 300, 11, n_petals=45, window=True)


if __name__ == "__main__":
    hero()
    divider()
    chapter_titles()
    footer()
    if "--gifs" in sys.argv:
        gifs()
    print("assets written to", OUT)
