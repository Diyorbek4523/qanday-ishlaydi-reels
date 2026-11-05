"""Molniya: a zipper. Two tapes with teeth run up the screen; a slider travels up. Above the slider teeth stand apart (open V), below it they sit
staggered and locked. A cutaway slider shows the Y channel; close-up shows the bump of one tooth entering the hollow of the next. 5 shots."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.05, .05, .12), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5) = list(zip(S[:-1], S[1:]))

# ---------- materials ----------
fabric = b3d.mat('Fabric', (.1, .22, .55), .85, bump=.12)
tape_l = b3d.mat('TapeL', (.85, .22, .22), .8, bump=.1)
tape_r = b3d.mat('TapeR', (.14, .55, .85), .8, bump=.1)
tooth_a = b3d.mat('ToothA', (.95, .72, .25), .25, metal=.9)
tooth_b = b3d.mat('ToothB', (.8, .82, .88), .25, metal=.9)
slider_m = b3d.mat('Slider', (.32, .34, .4), .3, metal=.9)
slider_in = b3d.mat('SliderIn', (.1, .11, .15), .5, metal=.4)
wedge_m = b3d.mat('Wedge', (1, .45, .1), .35, emit=(1, .35, .03), estr=.5)
pull_m = b3d.mat('Pull', (.75, .77, .82), .2, metal=1)
point_m = b3d.mat('Point', (1, .8, .2), .4, emit=(1, .72, .08), estr=2.6)
hollow_m = b3d.mat('Hollow', (.08, .05, .02), .6)
bump_m = b3d.mat('Bump', (1, .85, .25), .3, emit=(1, .7, .1), estr=1.2)

def ease(u): u = min(1, max(0, u)); return u * u * (3 - 2 * u)
def box(m, c, s, bevel=0):
    b = b3d.prim('cube', [m], size=1, location=c); b.scale = s
    if bevel:
        bv = b.modifiers.new('Bv', 'BEVEL'); bv.width = bevel; bv.segments = 3; b3d.smooth(b)
    return b

# ---------- background: jacket cloth ----------
box(fabric, (0, .3, 4), (30, .2, 40))

# ---------- slider travel: slider front (top) z ----------
Z0, Z1 = -5, 13
def sz(f):
    if f < s2: return 1.2 + 2.0 * (f - s1) / max(1, e1 - s1)
    if f < s4: return 3.2 + 1.3 * (f - s2) / max(1, s4 - s2)  # slow, centred for the channel shots
    if f < s5: return 4.5 + .85 * (f - s4) / max(1, s5 - s4)
    return 5.35 + 3.2 * ease((f - s5) / max(1, e5 - s5))

# ---------- teeth ----------
PITCH = .3; TW, TH, TD = .34, .135, .14
LOCK_X = .055; OPEN = 0.21   # half-gap per unit height above slider (Y opening)
SL_H = 1.25                 # slider length; teeth merge inside it
COUNT = int((Z1 - Z0) / PITCH)
TAPE_W = 2.6
def tooth_x(z, f):
    d = z - (sz(f) - SL_H)  # below slider back: d<0 locked
    if d <= 0: return LOCK_X
    return LOCK_X + (d / SL_H) ** 1.6 * .42 + max(0, z - sz(f)) * OPEN
step = 3
for side, mt, tp in ((-1, tooth_a, tape_l), (1, tooth_b, tape_r)):
    # tape: a strip per tooth pitch that follows the teeth, so the edge opens smoothly
    for i in range(COUNT):
        z = Z0 + i * PITCH + (PITCH / 2 if side > 0 else 0)
        t = b3d.smooth(box(mt, (0, 0, z), (TW, TD, TH), bevel=.03))
        bump = b3d.smooth(b3d.prim('uv_sphere', [mt], segments=10, ring_count=6, radius=.075, location=(-side * .15, 0, .0)))
        bump.scale = (1 / TW, 1 / TD * .9, 1 / TH * .85)
        bump.location = (-side * .42, 0, 0); bump.parent = t
        st = box(tp, (0, .03, z), (TAPE_W, .05, PITCH + .01))
        for f in range(0, N, step):
            x = tooth_x(z, f)
            t.location = (side * x, 0, z); t.keyframe_insert('location', frame=f)
            st.location = (side * (x + .14 + TAPE_W / 2), .03, z); st.keyframe_insert('location', frame=f)

# ---------- slider (front half hides for the cutaway) ----------
sl = b3d.empty('Slider')
# bottom plate with the Y channel walls
box(slider_in, (0, .13, -SL_H / 2), (1.15, .06, SL_H), bevel=.02).parent = sl
for side in (-1, 1):
    # walls bend from wide (top) to narrow (bottom): the arms of the Y
    for k in range(9):
        u = k / 8; zz = -SL_H * u; xx = side * (.56 - .14 * u * u)
        box(slider_m, (xx, 0, zz), (.11, .26, .19), bevel=.02).parent = sl
we = b3d.smooth(b3d.prim('cone', [wedge_m], vertices=3, radius1=.26, depth=.5, rotation=(math.radians(180), 0, 0)))
we.scale = (1, .55, 1); we.location = (0, 0, -.2); we.parent = sl
cover = b3d.empty('Cover'); cover.parent = sl
box(slider_m, (0, -.2, -SL_H / 2), (1.3, .12, SL_H + .05), bevel=.05).parent = cover
b3d.smooth(b3d.prim('cylinder', [pull_m], vertices=24, radius=.1, depth=.16, location=(0, -.31, -.2), rotation=(math.radians(90), 0, 0))).parent = cover
tab = box(pull_m, (0, -.34, -.95), (.28, .05, 1.25), bevel=.02); tab.parent = cover
for f in range(0, N, 2):
    sl.location = (0, 0, sz(f)); sl.keyframe_insert('location', frame=f)
b3d.visible(cover, [(s1, e1), (s5, e5)])
b3d.visible(we, [(s2, e4)])

# ---------- pointers ----------
b3d.visible(b3d.arrow('DnL', (-.95, -.35, 5.15), (-.5, -.35, 4.45), point_m, r=.035), [(s3, e3)])
b3d.visible(b3d.arrow('DnR', (.95, -.35, 5.15), (.5, -.35, 4.45), point_m, r=.035), [(s3, e3)])

# ---------- lights ----------
b3d.light('AREA', 'Key', (3, -7, 8), 480, (1, .95, .88), 8, rot=(40, 0, 18))
b3d.light('AREA', 'Fill', (-5, -6, 2), 180, (.62, .74, 1), 6, rot=(80, 0, -30))
b3d.light('POINT', 'Near', (0, -1.6, 3.2), 22, (1, 1, 1), .6)

# ---------- timeline ----------
cam, tgt = b3d.camera(35)
b3d.shot(cam, tgt, s1, e1, (2.2, -9.5, 3.8), (1.3, -8.6, 3.8), (0, 0, 3.2), lens=35)
b3d.shot(cam, tgt, s2, e2, (.7, -5.6, 3.8), (.3, -5.0, 3.9), (0, 0, 3.4), lens=35)
b3d.shot(cam, tgt, s3, e3, (-.5, -4.3, 4.4), (-.2, -3.9, 4.2), (0, 0, 3.7), lens=35)
b3d.shot(cam, tgt, s4, e4, (.3, -2.3, 3.7), (.12, -2.0, 3.85), (0, 0, 3.45), (0, 0, 3.8), lens=35)
b3d.shot(cam, tgt, s5, e5, (.9, -7.6, 4.6), (1.6, -11.2, 6.0), (0, 0, 5.2), lens=35)
b3d.render(OUT, cfg.get('frames'))
