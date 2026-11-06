#!/usr/bin/env python3
"""Render a "Qanday ishlaydi?" Reel (1080x1920, 30 fps) from a script JSON: blueprint drawing + big Uzbek text + music.

    python3 reel.py <script.json> <out.mp4>

Script: {"title": ..., "key": "A", "scenes": [{"dur": s, "text": "LINE|*ACCENT* LINE", "small": "...", "draw": name, "args": {...}}]}
Text: "|" breaks lines, *word* is drawn in the accent colour. Draw names are the functions in DRAW below.
Voice: give scenes a "say" (spoken Uzbek, numbers in words) and the reel gets an ElevenLabs voiceover; scene "dur"
is then fitted to the speech and the music is ducked under it. Optional "voice": {"id", "model", "lang"}.
Needs ELEVENLABS_API_KEY; the take is cached next to the script (<script>.voice.mp3 + .voice.json), so re-renders cost nothing.
Pass --no-voice to ignore "say".
"""
import base64, hashlib, json, math, os, subprocess, sys, urllib.request, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
BG, GRID, INK, ACC, RED, DIM = (10, 30, 58), (22, 52, 92), (232, 241, 255), (255, 204, 51), (255, 92, 92), (120, 150, 190)
FD = os.path.join(os.environ.get('REEL_FONT_DIR', '/usr/share/fonts/opentype/inter'), '')
def font(sz, w='Black'): return ImageFont.truetype(f'{FD}Inter-{w}.otf', sz)
F_BIG, F_SMALL, F_TAG = font(92), font(46, 'SemiBold'), font(34, 'Bold')

clamp = lambda x, a=0., b=1.: max(a, min(b, x))
seg = lambda t, a, b: clamp((t - a) / (b - a)) if b > a else float(t >= a)
eo = lambda x: 1 - (1 - clamp(x)) ** 3
def pop(x):  # overshoot ease for text pop-in
    x = clamp(x); c = 1.7
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

# ---------- drawing primitives (all take progress u 0..1) ----------
def path(d, pts, u=1., col=INK, w=8, closed=False):
    if closed: pts = pts + [pts[0]]
    if u <= 0 or len(pts) < 2: return
    L = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]; tot = sum(L) * clamp(u); out = [pts[0]]
    for i, l in enumerate(L):
        if tot >= l: out.append(pts[i + 1]); tot -= l
        else:
            if l: a, b = pts[i], pts[i + 1]; out.append((a[0] + (b[0] - a[0]) * tot / l, a[1] + (b[1] - a[1]) * tot / l))
            break
    d.line(out, fill=col, width=w, joint='curve')
def rrect(x0, y0, x1, y1, r=40, n=6):
    pts = []
    for cx, cy, a0 in [(x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)]:
        pts += [(cx + r * math.cos(math.radians(a0 + 90 * k / n)), cy + r * math.sin(math.radians(a0 + 90 * k / n))) for k in range(n + 1)]
    return pts + [pts[0]]  # closed outline
def circle(cx, cy, r, n=48, a0=0, a1=360): return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]
def arrow(d, a, b, u=1., col=ACC, w=8):
    path(d, [a, b], u, col, w)
    if u >= .99:
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        for s in (-1, 1): d.line([b, (b[0] - 34 * math.cos(ang + s * .5), b[1] - 34 * math.sin(ang + s * .5))], fill=col, width=w)
def label(d, s, xy, u=1., col=DIM, f=None, anchor='mm'):
    if u > .05: d.text(xy, s, font=f or F_TAG, fill=tuple(int(BG[i] + (col[i] - BG[i]) * clamp(u)) for i in range(3)), anchor=anchor)

# ---------- drawings: f(d, t, local scene time, args) ----------
CX, CY = W // 2, 1130
def phone(d, t, a):
    level = a.get('level', [0, 100]); x0, y0, x1, y1 = CX - 210, CY - 400, CX + 210, CY + 400
    path(d, rrect(x0, y0, x1, y1, 60), seg(t, 0, 1.0), INK, 9)
    path(d, [(CX - 50, y0 + 40), (CX + 50, y0 + 40)], seg(t, .6, 1.0), INK, 8)
    bx0, by0, bx1, by1 = CX - 110, CY - 230, CX + 110, CY + 250
    path(d, rrect(bx0, by0, bx1, by1, 20), seg(t, .8, 1.6), INK, 7); path(d, [(CX - 40, by0 - 18), (CX + 40, by0 - 18)], seg(t, 1.2, 1.6), INK, 12)
    p = level[0] + (level[1] - level[0]) * eo(seg(t, 1.4, a.get('fill_t', 3.2)))
    if p > 0:
        top = by1 - 14 - (by1 - by0 - 28) * p / 100
        d.rounded_rectangle([bx0 + 14, top, bx1 - 14, by1 - 14], 10, fill=RED if p < 20 else (ACC if p < 100 else (80, 220, 140)))
    label(d, f'{int(round(p))}%', (CX, by1 + 70), seg(t, 1.2, 1.6), INK, font(64))
    if a.get('plug'):
        path(d, [(CX, y1), (CX, y1 + 120), (CX + 160, y1 + 160)], seg(t, .4, 1.2), DIM, 10)
        if a.get('bolt', True) and t > 1.4 and int(t * 4) % 2 == 0: label(d, 'TOK', (CX + 290, y1 + 70), 1, ACC, font(48))
def chip(d, t, a):
    path(d, rrect(CX - 170, CY - 170, CX + 170, CY + 170, 18), seg(t, 0, .9), INK, 9)
    for i in range(5):
        o = -120 + 60 * i
        for s in (-1, 1):
            path(d, [(CX + o, CY + s * 170), (CX + o, CY + s * 230)], seg(t, .5 + i * .06, .8 + i * .06), INK, 8)
            path(d, [(CX + s * 170, CY + o), (CX + s * 230, CY + o)], seg(t, .5 + i * .06, .8 + i * .06), INK, 8)
    label(d, a.get('name', 'BMS'), (CX, CY), seg(t, .9, 1.3), ACC, font(80))
    if a.get('eye'):
        u = seg(t, 1.3, 1.8); path(d, circle(CX, CY - 330, 70, 40, 180, 360) + circle(CX, CY - 330, 70, 40, 0, 180), u, ACC, 7)
        if u >= 1: d.ellipse([CX - 24, CY - 354, CX + 24, CY - 306], fill=ACC)
        label(d, a.get('eye'), (CX, CY + 330), seg(t, 1.6, 2.1), DIM, F_TAG)
def gauge(d, t, a):
    lo, hi, v0, v1, unit = a.get('lo', 3.0), a.get('hi', 4.4), a.get('from', 3.7), a.get('to', 4.2), a.get('unit', 'V')
    r = 300; path(d, circle(CX, CY + 120, r, 60, 180, 360), seg(t, 0, 1.0), INK, 10)
    mark = a.get('mark')
    for k in range(8):
        ang = math.radians(180 + 180 * k / 7); c, s_ = math.cos(ang), math.sin(ang)
        path(d, [(CX + (r - 10) * c, CY + 120 + (r - 10) * s_), (CX + (r - 50) * c, CY + 120 + (r - 50) * s_)], seg(t, .6 + k * .05, .8 + k * .05), INK, 6)
    if mark is not None:
        ang = math.radians(180 + 180 * (mark - lo) / (hi - lo))
        path(d, [(CX + (r + 10) * math.cos(ang), CY + 120 + (r + 10) * math.sin(ang)), (CX + (r + 70) * math.cos(ang), CY + 120 + (r + 70) * math.sin(ang))], seg(t, 1.0, 1.3), RED, 12)
        label(d, f'{mark} {unit}', (CX + (r + 130) * math.cos(ang), CY + 120 + (r + 120) * math.sin(ang)), seg(t, 1.1, 1.5), RED, F_TAG)
    v = v0 + (v1 - v0) * eo(seg(t, 1.0, a.get('move_t', 3.0))); ang = math.radians(180 + 180 * (v - lo) / (hi - lo))
    if t > .9:
        d.line([(CX, CY + 120), (CX + (r - 70) * math.cos(ang), CY + 120 + (r - 70) * math.sin(ang))], fill=ACC, width=12); d.ellipse([CX - 22, CY + 98, CX + 22, CY + 142], fill=ACC)
    label(d, f'{v:.2f} {unit}', (CX, CY + 230), seg(t, .9, 1.2), INK, font(72))
def switch(d, t, a):
    yl = CY; open_at = a.get('open_t', 1.6); op = eo(seg(t, open_at, open_at + .4))
    path(d, [(120, yl), (CX - 120, yl)], seg(t, 0, .6), INK, 10); path(d, [(CX + 120, yl), (W - 120, yl)], seg(t, .2, .8), INK, 10)
    d.ellipse([CX - 136, yl - 16, CX - 104, yl + 16], fill=INK) if t > .6 else None; d.ellipse([CX + 104, yl - 16, CX + 136, yl + 16], fill=INK) if t > .8 else None
    ang = math.radians(-35 * op); L = 240
    if t > .8: d.line([(CX - 120, yl), (CX - 120 + L * math.cos(ang), yl + L * math.sin(ang))], fill=ACC, width=14)
    if op < .5 and t > .9:  # current dots flowing
        for k in range(8):
            x = 120 + ((t * 420 + k * 120) % (W - 240)); d.ellipse([x - 12, yl - 60 - 12, x + 12, yl - 60 + 12], fill=ACC)
    if op >= 1: label(d, a.get('word', "TO'XTA"), (CX, yl + 200), seg(t, open_at + .4, open_at + .8), RED, font(110))
def swell(d, t, a):
    s = .5 + .5 * math.sin(t * 6) if t > 1.0 else 0; b = 38 * eo(seg(t, .8, 2.2)) + 6 * s
    x0, x1, y0, y1 = CX - 170, CX + 170, CY - 280, CY + 280
    pts = [(x0, y0)] + [(x0 + (x1 - x0) * k / 20, y0 - b * math.sin(math.pi * k / 20)) for k in range(21)] + [(x1 + b * math.sin(math.pi * k / 20), y0 + (y1 - y0) * k / 20) for k in range(21)] \
        + [(x1 - (x1 - x0) * k / 20, y1 + b * math.sin(math.pi * k / 20)) for k in range(21)] + [(x0 - b * math.sin(math.pi * k / 20), y1 - (y1 - y0) * k / 20) for k in range(21)]
    path(d, pts, seg(t, 0, .9), RED if t > 1.2 else INK, 10)
    if t > 1.4:
        for k in range(3):
            x = CX - 120 + 120 * k; ph = (t * 1.5 + k * .33) % 1
            path(d, [(x + 20 * math.sin((ph + j / 8) * 6), y0 - 40 - 150 * ph - j * 14) for j in range(8)], 1, RED, 7)
    label(d, a.get('word', 'QIZIYDI'), (CX, y1 + 150), seg(t, 1.6, 2.0), RED, font(80))
def bars(d, t, a):  # "80%" style comparison: list of [label, value]
    items = a['items']; n = len(items); bw = 160; gap = (W - 200 - n * bw) / max(1, n - 1)
    for i, (lab, v) in enumerate(items):
        x = 100 + i * (bw + gap); hh = 600 * v / 100 * eo(seg(t, .3 + i * .3, 1.2 + i * .3))
        d.rectangle([x, CY + 300 - hh, x + bw, CY + 300], fill=ACC if i == a.get('hi', n - 1) else DIM)
        label(d, lab, (x + bw / 2, CY + 360), seg(t, .2, .6), INK, F_TAG)
def escalator(d, t, a):  # step chain loop: steps ride up on top, turn round the wheels, come back upside down underneath
    ang = math.radians(-32); ca, sa = math.cos(ang), math.sin(ang); L, R = 640, 95
    def P(x, y): return (CX + x * ca - y * sa, CY + 60 + x * sa + y * ca)
    loop = []  # stadium in local coords, x along the incline, clockwise from bottom-left of top run
    for k in range(25): loop.append((-L / 2 + L * k / 24, -R))
    for k in range(1, 25): th = -math.pi / 2 + math.pi * k / 24; loop.append((L / 2 + R * math.cos(th), R * math.sin(th)))
    for k in range(1, 25): loop.append((L / 2 - L * k / 24, R))
    for k in range(1, 24): th = math.pi / 2 + math.pi * k / 24; loop.append((-L / 2 + R * math.cos(th), R * math.sin(th)))
    path(d, [P(*q) for q in loop], seg(t, 0, 1.0), DIM, 6, closed=True)
    for sx in (-L / 2, L / 2):
        u = seg(t, .6, 1.0); path(d, circle(*P(sx, 0), R - 20, 30), u, INK, 6)
    per = 2 * L + 2 * math.pi * R; sp = a.get('speed', 120); n = 12; hl = a.get('hl')
    def at(sd):
        sd %= per
        if sd < L: return (-L / 2 + sd, -R), 0
        sd -= L
        if sd < math.pi * R: th = -math.pi / 2 + sd / R; return (L / 2 + R * math.cos(th), R * math.sin(th)), th + math.pi / 2
        sd -= math.pi * R
        if sd < L: return (L / 2 - sd, R), math.pi
        sd -= L; th = math.pi / 2 + sd / R; return (-L / 2 + R * math.cos(th), R * math.sin(th)), th + math.pi / 2
    if t > .8:
        for i in range(n):
            (x, y), rot = at(i * per / n + sp * (t - .8)); c, s_ = math.cos(rot), math.sin(rot)
            top = y < -R + 1; col = ACC if (hl is None or hl == i) else (INK if top else DIM)
            # a step = tread (along the chain) + riser pointing away from the loop centre
            tread = [P(x - 34 * c, y - 34 * s_), P(x + 34 * c, y + 34 * s_)]; riser = [P(x - 34 * c, y - 34 * s_), P(x - 34 * c + 40 * s_, y - 34 * s_ - 40 * c)]
            d.line(tread, fill=col, width=10); d.line(riser, fill=col, width=8)
    if a.get('arrows') and t > 1.2:
        arrow(d, P(-L / 2 + 60, -R - 110), P(L / 2 - 60, -R - 110), seg(t, 1.2, 1.7), ACC, 7)
        arrow(d, P(L / 2 - 60, R + 110), P(-L / 2 + 60, R + 110), seg(t, 1.5, 2.0), RED, 7)
    if a.get('word'): label(d, a['word'], (CX, CY + 470), seg(t, 1.4, 1.8), ACC, font(80))
def microwave(d, t, a):  # oven box + travelling wave + water molecules that twist with the field
    x0, y0, x1, y1 = CX - 380, CY - 260, CX + 380, CY + 260
    path(d, rrect(x0, y0, x1, y1, 30), seg(t, 0, .9), INK, 9); path(d, rrect(x0 + 40, y0 + 40, x1 - 200, y1 - 40, 20), seg(t, .4, 1.1), DIM, 6)
    for k in range(3): label(d, '●', (x1 - 100, y0 + 120 + 90 * k), seg(t, .8 + k * .1, 1.0 + k * .1), DIM, F_TAG)
    if a.get('mag', True):
        path(d, rrect(x1 - 170, y1 - 130, x1 - 30, y1 - 50, 10), seg(t, .9, 1.2), ACC, 6); label(d, 'MAGNETRON', (x1 - 100, y1 + 50), seg(t, 1.0, 1.4), ACC, F_TAG)
    if t > 1.0:
        amp = 60 * eo(seg(t, 1.0, 1.5)); ph = t * 9
        pts = [(x0 + 60 + k * (x1 - x0 - 280) / 60, CY - 120 + amp * math.sin(k / 60 * 4 * math.pi * 2 - ph)) for k in range(61)]
        d.line(pts, fill=ACC, width=7, joint='curve')
    m = a.get('mol', 0); heat = a.get('heat', False)
    if m:
        for i in range(m):
            mx = x0 + 120 + i * (x1 - x0 - 320) / max(1, m - 1); my = CY + 90
            rot = (.9 * math.sin(t * 14 + i) if t > 1.2 else 0) + i
            jit = (6 * math.sin(t * 31 + i * 2) if heat and t > 1.5 else 0)
            u = seg(t, .8 + i * .1, 1.1 + i * .1)
            if u <= 0: continue
            ox, oy = mx + jit, my - jit; d.ellipse([ox - 30, oy - 30, ox + 30, oy + 30], outline=RED if heat and t > 1.8 else INK, width=7)
            for sgn in (-1, 1):
                hx, hy = ox + 52 * math.cos(rot + sgn * .9), oy + 52 * math.sin(rot + sgn * .9); d.ellipse([hx - 16, hy - 16, hx + 16, hy + 16], outline=DIM, width=6)
        label(d, 'H₂O', (CX - 100, CY + 200), seg(t, 1.0, 1.4), DIM, F_TAG)
    if heat and t > 1.8:
        for k in range(3):
            x = CX - 260 + 160 * k; ph = (t * 1.5 + k * .33) % 1
            path(d, [(x + 18 * math.sin((ph + j / 8) * 6), y1 + 60 - 120 * ph - j * 12 + 120) for j in range(8)], 1, RED, 6)
    if a.get('word'): label(d, a['word'], (CX, y1 + 200), seg(t, 1.4, 1.8), a.get('word_col') == 'red' and RED or ACC, font(80))
def along(pts, s):  # point at distance s along a polyline
    for p, q in zip(pts, pts[1:]):
        l = math.dist(p, q)
        if s <= l: return (p[0] + (q[0] - p[0]) * s / l, p[1] + (q[1] - p[1]) * s / l) if l else p
        s -= l
    return pts[-1]
def plen(pts): return sum(math.dist(p, q) for p, q in zip(pts, pts[1:]))
def wavy(d, x0, x1, y, ph, col=RED, w=6):  # short wavy heat arrow from x0 to x1
    n = 16; pts = [(x0 + (x1 - x0) * k / n, y + 12 * math.sin(k / n * 3 * math.pi - ph)) for k in range(n + 1)]
    d.line(pts, fill=col, width=w, joint='curve'); s = 1 if x1 > x0 else -1
    for v in (-1, 1): d.line([pts[-1], (pts[-1][0] - s * 24, pts[-1][1] + v * 16)], fill=col, width=w)
def wing(d, t, a):  # cambered airfoil at an angle of attack; streamlines bend down behind it, air over the top runs faster
    c, aoa, cy = 600, math.radians(a.get('aoa', 7)), CY + 40
    def R(x, y):  # rotate about mid chord, nose up
        dx, dy = x - CX, y - cy; return (CX + dx * math.cos(aoa) - dy * math.sin(aoa), cy + dx * math.sin(aoa) + dy * math.cos(aoa))
    up, lo = [], []
    for k in range(41):
        xc = (1 - math.cos(math.pi * k / 40)) / 2; m, p, th = .05, .4, .13
        yc = m / p ** 2 * (2 * p * xc - xc ** 2) if xc < p else m / (1 - p) ** 2 * ((1 - 2 * p) + 2 * p * xc - xc ** 2)
        yt = 5 * th * (.2969 * math.sqrt(xc) - .126 * xc - .3516 * xc ** 2 + .2843 * xc ** 3 - .1036 * xc ** 4)
        x = CX - c / 2 + c * xc; up.append(R(x, cy - c * (yc + yt))); lo.append(R(x, cy - c * (yc - yt)))
    foil = up + lo[::-1]
    def stream(y0, x):
        s = 1 / (1 + math.exp(-(x - CX - 160) / 110)); down = a.get('down', 80) * s * (1 - abs(y0) / 600)
        bump = (-50 if y0 < 0 else 22) * math.exp(-((x - CX + 40) / 230) ** 2) * 200 / (abs(y0) + 120)
        return cy + y0 + down + bump
    if a.get('flow', True):
        for y0 in (-250, -160, -85, 85, 160, 250):
            path(d, [(x, stream(y0, x)) for x in range(60, 1041, 20)], seg(t, .3, 1.1), DIM, 4)
            if t > 1.1:
                for k in range(6):
                    x = 60 + (a.get('speed', 300) * (1.4 if y0 < 0 else 1) * t + k * 165) % 930
                    d.line([(xx, stream(y0, xx)) for xx in range(int(x), int(x) + 61, 10)], fill=ACC if y0 < 0 else INK, width=7)
    d.polygon(foil, fill=BG); path(d, foil, seg(t, 0, 1.0), INK, 9, closed=True)
    if a.get('press'):
        for i, x in enumerate((CX - 160, CX, CX + 160)):
            label(d, '−', (x, cy - 140 - (x - CX) * .12), seg(t, 1.0 + i * .15, 1.3 + i * .15), ACC, font(110))
            label(d, '+', (x, cy + 120 + (x - CX) * .12), seg(t, 1.4 + i * .15, 1.7 + i * .15), INK, font(90))
    if a.get('lift'):
        arrow(d, (CX, cy - 30), (CX, cy - 300), eo(seg(t, 1.2, 1.8)), ACC, 14)
        label(d, "KO'TARISH KUCHI", (CX, cy - 350), seg(t, 1.6, 2.0), ACC, F_TAG)
    if a.get('word'): label(d, a['word'], (CX, cy + 400), seg(t, 1.4, 1.8), ACC, font(80))
def solar(d, t, a):  # sun -> light -> panel (or a cell cross-section) -> wire -> inverter -> lamp
    sx, sy = 880, 790
    path(d, circle(sx, sy, 62, 36), seg(t, 0, .6), ACC, 8)
    for k in range(8):
        ang = 2 * math.pi * k / 8 + t * .4
        path(d, [(sx + 85 * math.cos(ang), sy + 85 * math.sin(ang)), (sx + 118 * math.cos(ang), sy + 118 * math.sin(ang))], seg(t, .3, .7), ACC, 6)
    cell = a.get('cell')
    if cell:
        x0, x1, ym, y0, y1 = 170, 880, 1040, 920, 1200
        path(d, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], seg(t, 0, 1.0), INK, 8, closed=True)
        if t > .6:
            for x in range(x0 + 10, x1, 40): d.line([(x, ym), (x + 20, ym)], fill=ACC, width=6)
        label(d, 'N', (x0 + 60, (y0 + ym) / 2), seg(t, .6, 1.0), INK, font(64)); label(d, 'P', (x0 + 60, (ym + y1) / 2), seg(t, .7, 1.1), INK, font(64))
        label(d, 'KREMNIY', (x0 + 120, y1 + 50), seg(t, .8, 1.2), DIM, F_TAG)
        targets = [(x0 + 160 + 110 * k, y0) for k in range(6)]; start = (CX, y1 + 4)
        if a.get('elec', True) and t > 1.2:
            for k in range(5):  # freed electrons drift up through the cell
                ph = (t * .7 + k / 5) % 1; x = x0 + 200 + 115 * k; y = y1 - 30 - (y1 - y0 - 60) * ph
                d.ellipse([x - 13, y - 13, x + 13, y + 13], fill=INK)
    else:
        P = [(170, 1000), (700, 900), (790, 1170), (260, 1270)]
        path(d, P, seg(t, 0, 1.0), INK, 8, closed=True)
        lerp = lambda p, q, u: (p[0] + (q[0] - p[0]) * u, p[1] + (q[1] - p[1]) * u)
        for i in range(1, 6): path(d, [lerp(P[0], P[1], i / 6), lerp(P[3], P[2], i / 6)], seg(t, .5, 1.0), DIM, 4)
        for j in range(1, 3): path(d, [lerp(P[0], P[3], j / 3), lerp(P[1], P[2], j / 3)], seg(t, .5, 1.0), DIM, 4)
        targets = [lerp(lerp(P[0], P[1], u), lerp(P[3], P[2], u), .45) for u in (.15, .3, .45, .6, .75, .9)]; start = lerp(P[3], P[2], .5)
    if a.get('photons', True) and t > .9:
        for k, (tx, ty) in enumerate(targets):
            ph = (t * 1.1 + k / 6) % 1
            if ph < .85: d.line([(sx + (tx - sx) * ph, sy + (ty - sy) * ph), (sx + (tx - sx) * (ph + .15), sy + (ty - sy) * (ph + .15))], fill=ACC, width=6)
    inv = a.get('inv'); lx, ly, ix = 880, 1450, start[0]
    wires = [[start, (ix, 1395)], [(ix + 120, 1450), (lx - 50, 1450)]] if inv else [[start, (ix, 1450), (lx - 50, 1450)]]
    if a.get('wire', True):
        for w_ in wires: path(d, w_, seg(t, .6, 1.2), INK, 7)
    if inv:
        path(d, rrect(ix - 120, 1395, ix + 120, 1505, 16), seg(t, .8, 1.3), ACC, 7)
        label(d, 'INVERTOR', (ix, 1450), seg(t, 1.0, 1.4), ACC, F_TAG)
        label(d, 'DC', (ix - 60, 1340), seg(t, 1.2, 1.6), INK, F_TAG); label(d, 'AC ~', (ix + 230, 1405), seg(t, 1.2, 1.6), INK, F_TAG)
    lit = a.get('flow') and t > 1.2
    if a.get('wire', True):
        path(d, circle(lx, ly, 46, 30), seg(t, 1.0, 1.3), ACC if lit else INK, 7)
        if lit:
            d.ellipse([lx - 34, ly - 34, lx + 34, ly + 34], fill=ACC)
            for k in range(6): ang = 2 * math.pi * k / 6; d.line([(lx + 62 * math.cos(ang), ly + 62 * math.sin(ang)), (lx + 88 * math.cos(ang), ly + 88 * math.sin(ang))], fill=ACC, width=6)
            for w_ in wires:
                L_ = plen(w_); n = max(2, int(L_ / 70))
                for k in range(n): x, y = along(w_, (t * 160 + k * L_ / n) % L_); d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=INK)
    if a.get('word'): label(d, a['word'], (CX, 1620), seg(t, 1.4, 1.8), ACC, font(80))
def heatpump(d, t, a):  # refrigerant loop: cold coil takes heat in, compressor squeezes it hot, hot coil throws heat out, valve chills it
    xl, xr, yt, yb = 235, 845, 960, 1300; hl = a.get('hl')
    for i, (x0, x1) in enumerate(((70, 400), (680, 1010))): path(d, rrect(x0, 880, x1, 1380, 30), seg(t, i * .2, .8 + i * .2), INK, 8)
    label(d, a.get('left', 'XONA'), (xl, 1440), seg(t, .6, 1.0), INK, F_TAG); label(d, a.get('right', 'TASHQARI'), (xr, 1440), seg(t, .7, 1.1), INK, F_TAG)
    zig = lambda x, ya, yb_: [(x, ya)] + [(x + 38 * (1 if k % 2 else -1), ya + (yb_ - ya) * k / 9) for k in range(1, 9)] + [(x, yb_)]
    pieces = [(zig(xl, yb, yt), INK), ([(xl, yt), (CX, yt)], DIM), ([(CX, yt), (xr, yt)], RED), (zig(xr, yt, yb), RED), ([(xr, yb), (CX, yb)], ACC), ([(CX, yb), (xl, yb)], INK)]
    loop = [p for pts, _ in pieces for p in pts]
    path(d, loop, seg(t, .5, 1.4), DIM, 6)
    if t > 1.2:
        lens = [plen(pts) for pts, _ in pieces]; tot = sum(lens)
        for k in range(16):
            s = (t * a.get('speed', 170) + k * tot / 16) % tot; i = 0
            while s > lens[i]: s -= lens[i]; i += 1
            x, y = along(pieces[i][0], s)
            if math.dist((x, y), (CX, yt)) < 60 or math.dist((x, y), (CX, yb)) < 45: continue
            d.ellipse([x - 13, y - 13, x + 13, y + 13], fill=pieces[i][1])
    ca = ACC if hl == 'comp' else INK
    d.ellipse([CX - 58, yt - 58, CX + 58, yt + 58], fill=BG); path(d, circle(CX, yt, 58, 36), seg(t, .9, 1.3), ca, 8)
    if t > 1.3:
        for k in range(3): ang = t * 5 + k * 2 * math.pi / 3; d.line([(CX, yt), (CX + 40 * math.cos(ang), yt + 40 * math.sin(ang))], fill=ca, width=7)
    label(d, 'KOMPRESSOR', (CX, yt - 95), seg(t, 1.0, 1.4), ca, F_TAG)
    cv = ACC if hl == 'valve' else INK
    d.rectangle([CX - 42, yb - 32, CX + 42, yb + 32], fill=BG)
    if t > 1.0: d.line([(CX - 40, yb - 30), (CX + 40, yb + 30), (CX + 40, yb - 30), (CX - 40, yb + 30), (CX - 40, yb - 30)], fill=cv, width=7)
    label(d, 'KLAPAN', (CX, yb + 70), seg(t, 1.0, 1.4), cv, F_TAG)
    if a.get('heat_in') and t > 1.4:
        for k, y in enumerate((1040, 1130, 1220)): wavy(d, 95, 175, y, t * 8 + k, RED)
    if a.get('heat_out') and t > 1.4:
        for k, y in enumerate((1040, 1130, 1220)): wavy(d, 905, 990, y, t * 8 + k, RED)
    if a.get('word'): label(d, a['word'], (CX, 1560), seg(t, 1.4, 1.8), RED if a.get('word_col') == 'red' else ACC, font(80))
def none(d, t, a): pass
DRAW = {k: v for k, v in globals().items() if k in ('phone', 'chip', 'gauge', 'switch', 'swell', 'bars', 'escalator', 'microwave', 'wing', 'solar', 'heatpump', 'none')}

# ---------- text ----------
def text_block(d, s, t, y=420, f=F_BIG, maxw=W - 140):
    lines = []
    for raw in s.split('|'):
        words, cur = raw.split(), []
        for w_ in words:
            test = ' '.join(cur + [w_]).replace('*', '')
            if cur and d.textlength(test, font=f) > maxw: lines.append(cur); cur = [w_]
            else: cur.append(w_)
        lines.append(cur)
    lh = f.size * 1.12; y0 = y - lh * (len(lines) - 1) / 2; k = 0
    for li, words in enumerate(lines):
        full = ' '.join(words).replace('*', ''); x = (W - d.textlength(full, font=f)) / 2
        for w_ in words:
            acc = '*' in w_; w_ = w_.replace('*', '')  # *WORD*? keeps the punctuation
            u = seg(t, .08 * k, .08 * k + .25); k += 1
            if u > 0:
                dy = (1 - pop(u)) * 40; col = ACC if acc else INK
                d.text((x, y0 + li * lh + dy), w_, font=f, fill=tuple(int(BG[i] + (col[i] - BG[i]) * u) for i in range(3)), anchor='lm')
            x += d.textlength(w_ + ' ', font=f)

def background():
    im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
    for x in range(0, W, 60): d.line([(x, 0), (x, H)], fill=GRID, width=1 if x % 300 else 2)
    for y in range(0, H, 60): d.line([(0, y), (W, y)], fill=GRID, width=1 if y % 300 else 2)
    return im

# ---------- music: soft pad + pluck arpeggio + whoosh at cuts ----------
NOTE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
def music(dur, cuts, key='A', sr=44100):
    n = int(dur * sr); tt = np.arange(n) / sr; out = np.zeros(n); root = 57 + NOTE[key] - 9  # A3 = 57
    prog = [(0, 3, 7), (-4, 0, 3), (3, 7, 10), (-2, 2, 5)]  # i VI III VII
    hz = lambda m: 440 * 2 ** ((m - 69) / 12); bar = 2.4
    for b in range(int(dur / bar) + 1):
        s0, s1 = int(b * bar * sr), min(n, int((b + 1) * bar * sr + .3 * sr))
        if s0 >= n: break
        seg_t = tt[s0:s1] - b * bar; env = np.minimum(1, seg_t / .4) * np.exp(-seg_t * .25)
        for iv in prog[b % 4]:
            f = hz(root + iv); out[s0:s1] += .05 * env * (np.sin(2 * np.pi * f * tt[s0:s1]) + .5 * np.sin(2 * np.pi * f * 1.003 * tt[s0:s1]) + .25 * np.sin(4 * np.pi * f * tt[s0:s1]))
        for j in range(8):  # pluck eighths
            ps = s0 + int(j * bar / 8 * sr); pe = min(n, ps + int(.5 * sr))
            if ps >= n: break
            m = root + 12 + prog[b % 4][j % 3] + (12 if j % 4 == 3 else 0); lt = tt[ps:pe] - tt[ps]
            out[ps:pe] += .07 * np.exp(-lt * 9) * np.sin(2 * np.pi * hz(m) * lt)
        ks = s0; ke = min(n, ks + int(.25 * sr)); lt = tt[ks:ke] - tt[ks]  # soft kick each bar half
        for off in (0, int(bar / 2 * sr)):
            a_, b_ = ks + off, min(n, ks + off + len(lt))
            if a_ < n: out[a_:b_] += .25 * np.exp(-lt[:b_ - a_] * 18) * np.sin(2 * np.pi * (50 + 60 * np.exp(-lt[:b_ - a_] * 30)) * lt[:b_ - a_])
    rng = np.random.default_rng(1)
    for c in cuts:
        a_ = int(max(0, c - .35) * sr); b_ = min(n, a_ + int(.5 * sr))
        if a_ >= n: continue
        nz = rng.standard_normal(b_ - a_); nz = np.convolve(nz, np.ones(12) / 12, 'same'); lt = np.linspace(0, 1, b_ - a_)
        out[a_:b_] += .12 * nz * np.sin(np.pi * lt) ** 2
    fade = np.minimum(1, np.minimum(tt / .3, (dur - tt) / 1.2)); out *= fade
    out = np.tanh(out * 1.4) / np.tanh(1.4) * .8
    return (out * 32767).astype(np.int16), sr

# ---------- voice: one ElevenLabs take for the whole reel, split into scenes by character timestamps ----------
VOICE = {'id': 'agoC45V78njTIxYzwmSb', 'model': 'eleven_v4', 'lang': 'uz', 'settings': {'stability': 0.0, 'similarity_boost': 0.8}}  # Davronbek (Uzbek journalist); stability 0 + [tags] = the lively read the user picked (2026-11-01)
LEAD, TAIL = .3, 1.2  # silence before the first word, hold after the last

def eleven_key():
    """The user-level Windows value wins over the inherited one, so a key changed in Windows works without restarting the app."""
    if os.name == 'nt':
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment') as k: return winreg.QueryValueEx(k, 'ELEVENLABS_API_KEY')[0]
        except OSError: pass
    return os.environ['ELEVENLABS_API_KEY']

def voice_take(S, cache, sr=44100):
    v = {**VOICE, **S.get('voice', {})}; says = [sc.get('say', '').strip() for sc in S['scenes']]
    text = ' '.join(x for x in says if x); key = hashlib.sha1(json.dumps([v, says]).encode()).hexdigest()[:12]
    mp3, meta = cache + '.voice.mp3', cache + '.voice.json'
    if not (os.path.exists(meta) and json.load(open(meta)).get('key') == key):
        body = {'text': text, 'model_id': v['model'], **({'language_code': v['lang']} if v.get('lang') and v['model'] == 'eleven_v4' else {}),
                **({'voice_settings': v['settings']} if v.get('settings') else {})}  # e.g. {"stability": 0, "similarity_boost": .8} for a livelier read; [tags] in say steer emotion
        rq = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{v['id']}/with-timestamps?output_format=mp3_44100_128", json.dumps(body).encode(),
                                    {'xi-api-key': eleven_key(), 'Content-Type': 'application/json'})
        r = json.load(urllib.request.urlopen(rq, timeout=300)); open(mp3, 'wb').write(base64.b64decode(r['audio_base64']))
        json.dump({'key': key, 'text': text, 'alignment': r['alignment']}, open(meta, 'w'), ensure_ascii=False)
    al = json.load(open(meta))['alignment']; t0 = al['character_start_times_seconds']; t1 = al['character_end_times_seconds']
    pcm = np.frombuffer(subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', mp3, '-f', 's16le', '-ac', '1', '-ar', str(sr), '-'], capture_output=True, check=True).stdout, np.int16)
    # speech start of each scene (by character offset); scenes without "say" are kept at their own dur
    marks, pos = [], 0
    for x in says:
        marks.append(t0[min(pos, len(t0) - 1)] if x else None); pos += len(x) + 1 if x else 0
    return pcm.astype(np.float64) / 32768, marks, t1[-1]

def fit_scenes(scenes, marks, end):
    """Each scene lasts from its first word to the next scene's first word (LEAD before the first, TAIL after the last)."""
    starts, t = [], 0.
    for i, sc in enumerate(scenes):
        starts.append(t)
        nxt = next((m for m in marks[i + 1:] if m is not None), None)
        if marks[i] is None: t += sc['dur']
        elif nxt is None: t += end - marks[i] + TAIL + (LEAD if i == 0 else 0)
        else: t += nxt - marks[i] + (LEAD if i == 0 else 0)
    return np.array(starts + [t])

def mix_voice(mus, vo, sr=44100):
    """Duck the music under the voice (smoothed voice envelope drives music gain) and lay the voice on top."""
    n = len(mus); voc = np.zeros(n); a = int(LEAD * sr); voc[a:a + len(vo)] = vo[:max(0, n - a)]
    env = np.abs(voc); k = int(.25 * sr); env = np.convolve(env, np.ones(k) / k, 'same'); env = np.clip(env / (env.max() + 1e-9) * 3, 0, 1)
    out = mus * (.55 - .35 * env) + voc * 1.0
    return out / max(1., np.abs(out).max() / .95)

def main(script_path, out, use_voice=True):
    S = json.load(open(script_path)); scenes = S['scenes']; starts = np.cumsum([0] + [s['dur'] for s in scenes])
    vo = None
    if use_voice and any(sc.get('say') for sc in scenes):
        vo, marks, end = voice_take(S, os.path.splitext(os.path.abspath(script_path))[0]); starts = fit_scenes(scenes, marks, end)
    dur = float(starts[-1]); bg = background(); wav = out.rsplit('.', 1)[0] + '.wav'
    pcm, sr = music(dur, list(starts[1:-1]), S.get('key', 'A'))
    if vo is not None: pcm = (mix_voice(pcm / 32767, vo, sr) * 32767).astype(np.int16)
    with wave.open(wav, 'wb') as w_: w_.setnchannels(1); w_.setsampwidth(2); w_.setframerate(sr); w_.writeframes(pcm.tobytes())
    ff = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', wav,
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', *(['-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '44100'] if vo is not None else []), '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for fi in range(int(dur * FPS)):
        t = fi / FPS; si = int(np.searchsorted(starts, t, 'right') - 1); sc = scenes[si]; lt = t - starts[si]
        im = bg.copy(); d = ImageDraw.Draw(im)
        d.rectangle([0, 0, W * t / dur, 10], fill=ACC)  # progress bar
        label(d, S.get('tag', 'QANDAY ISHLAYDI?'), (W // 2, 120), 1, DIM, F_TAG)
        text_block(d, sc['text'], lt, y=sc.get('y', 400))
        if sc.get('small'): label(d, sc['small'], (W // 2, sc.get('small_y', sc.get('y', 400) + 210)), seg(lt, .6, 1.0), DIM, F_SMALL)
        DRAW[sc.get('draw', 'none')](d, lt, sc.get('args', {}))
        ff.stdin.write(im.tobytes())
    ff.stdin.close(); ff.wait()
    if S.get('cover') is not None:
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', str(S['cover']), '-i', out, '-frames:v', '1', '-q:v', '2', out.rsplit('.', 1)[0] + '-cover.jpg'])
    print(out, round(dur, 2), 's')

if __name__ == '__main__': main(*sys.argv[1:3], use_voice='--no-voice' not in sys.argv)
