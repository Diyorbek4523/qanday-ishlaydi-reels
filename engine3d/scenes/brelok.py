"""Mashina brelogi (rolling code): a key fob in front, a car behind. Each press bumps a counter (41 -> 42), the number
goes through a golden padlock (secret key) and flies as a radio wave carrying a scrambled code. The car's padlock (same
key) turns it back into 42, compares with the last number 41 -> green tick, lights blink. A red recorder that copied an
old code (41) replays it -> red X. 7 shots."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.025, .03, .07), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))
R = math.radians

# ---------- materials ----------
ground_m = b3d.mat('Ground', (.16, .17, .2), .8, bump=.1)
line_m = b3d.mat('Line', (.9, .85, .5), .6)
car_m = b3d.mat('Car', (.75, .12, .1), .25, metal=.4)
glass_m = b3d.mat('Glass', (.08, .12, .18), .1, metal=.3)
tyre_m = b3d.mat('Tyre', (.05, .05, .06), .7)
rim_m = b3d.mat('Rim', (.75, .77, .8), .25, metal=.9)
head_m = b3d.mat('Head', (1, .95, .8), .2, emit=(1, .92, .7), estr=.6)
blink_m = b3d.mat('Blink', (1, .55, .1), .3, emit=(1, .5, .05), estr=0)
fob_m = b3d.mat('Fob', (.07, .07, .08), .35)
btn_m = b3d.mat('Btn', (.3, .31, .34), .4)
led_m = b3d.mat('Led', (1, .15, .1), .3, emit=(1, .1, .05), estr=0)
gold = b3d.mat('Gold', (1, .75, .25), .25, metal=1.0, emit=(1, .7, .2), estr=.15)
wave_m = b3d.mat('Wave', (.3, .8, 1), .4, emit=(.3, .8, 1), estr=3.5)
bad_m = b3d.mat('BadWave', (1, .2, .15), .4, emit=(1, .15, .1), estr=3.5)
num_m = b3d.mat('Num', (1, 1, 1), .4, emit=(1, 1, 1), estr=1.6)
code_m = b3d.mat('Code', (.3, .85, 1), .4, emit=(.3, .85, 1), estr=2.5)
rec_m = b3d.mat('Rec', (.25, .26, .3), .4, metal=.5)
ok_m = b3d.mat('Ok', (.2, 1, .35), .3, emit=(.2, 1, .35), estr=4)
no_m = b3d.mat('No', (1, .15, .1), .3, emit=(1, .12, .08), estr=4)

def box(m, c, s, bevel=0, rot=None):
    b = b3d.prim('cube', [m], size=1, location=c); b.scale = s
    if rot: b.rotation_euler = [R(a) for a in rot]
    if bevel:
        bv = b.modifiers.new('Bv', 'BEVEL'); bv.width = bevel; bv.segments = 4; b3d.smooth(b)
    return b
def keys(ob, attr, fv):
    for f, v in fv: setattr(ob, attr, v); ob.keyframe_insert(attr, frame=f)
def text(body, loc, size, m, ranges=None):
    bpy.ops.object.text_add(location=loc); o = bpy.context.object; o.data.body = body; o.data.size = size
    o.data.align_x = 'CENTER'; o.data.align_y = 'CENTER'; o.data.extrude = .015; o.data.materials.append(m); o.rotation_euler = (R(90), 0, 0)
    if ranges is not None: b3d.visible(o, ranges)
    return o
def padlock(loc, sc_=1.0):
    root = b3d.empty('Lock', loc)
    b = box(gold, (0, 0, 0), (.5 * sc_, .22 * sc_, .4 * sc_), bevel=.05); b.parent = root
    t = b3d.smooth(b3d.prim('torus', [gold], major_radius=.17 * sc_, minor_radius=.04 * sc_, location=(0, 0, 0), rotation=(R(90), 0, 0)))
    t.parent = root; t.location = (0, 0, .22 * sc_)
    k = b3d.smooth(b3d.prim('cylinder', [fob_m], vertices=16, radius=.045 * sc_, depth=.05, location=(0, 0, 0), rotation=(R(90), 0, 0)))
    k.parent = root; k.location = (0, -.11 * sc_, .02)
    return root

# ---------- ground ----------
box(ground_m, (0, 0, -.05), (30, 30, .1))
for x in (-3.5, 3.5): box(line_m, (x, 2.6, .005), (.1, 4.5, .01))

# ---------- car (broadside, at y = 3) ----------
CY = 3.2
box(car_m, (0, CY, .62), (3.4, 1.55, .62), bevel=.18)
box(car_m, (-.15, CY, 1.12), (1.9, 1.35, .5), bevel=.2)
box(glass_m, (-.15, CY - .6, 1.14), (1.7, .2, .36), bevel=.08)
for x in (-1.15, 1.15):
    for y in (CY - .72, CY + .72):
        b3d.smooth(b3d.prim('cylinder', [tyre_m], vertices=32, radius=.36, depth=.26, location=(x, y, .36), rotation=(R(90), 0, 0)))
        b3d.smooth(b3d.prim('cylinder', [rim_m], vertices=24, radius=.2, depth=.28, location=(x, y, .36), rotation=(R(90), 0, 0)))
for x, m in ((1.66, head_m), (-1.66, led_m)):
    box(m, (x, CY - .55, .75), (.1, .3, .14), bevel=.03)
bl = [box(blink_m, (x, CY - .74, .78), (.2, .06, .1), bevel=.02) for x in (-1.5, 1.5)]
blk = b3d.light('POINT', 'BlinkL', (0, CY - 1.6, 1.2), 0, (1, .6, .15), .5)
handle = box(rim_m, (.1, CY - .78, .9), (.3, .05, .06), bevel=.02)
padlock((0, CY - .1, 1.95), 1.0)                       # car's padlock (same secret key)

# ---------- fob (front) ----------
FY = -3.0
fob = b3d.empty('Fob', (0, FY, 1.15)); fob.rotation_euler = (0, R(-12), 0)
body = box(fob_m, (0, 0, 0), (.42, .16, .8), bevel=.12); body.parent = fob
btns = []
for z in (.15, -.12):
    bt = b3d.smooth(b3d.prim('cylinder', [btn_m], vertices=24, radius=.11, depth=.05, location=(0, 0, 0), rotation=(R(90), 0, 0)))
    bt.parent = fob; bt.location = (0, -.085, z); btns.append(bt)
led = b3d.smooth(b3d.prim('uv_sphere', [led_m], segments=12, ring_count=6, radius=.03, location=(0, 0, 0))); led.parent = fob; led.location = (.12, -.08, .33)
ring = b3d.smooth(b3d.prim('torus', [rim_m], major_radius=.08, minor_radius=.02, location=(0, 0, 0))); ring.parent = fob; ring.location = (0, 0, .47); ring.rotation_euler = (0, R(90), 0)
keys(fob, 'rotation_euler', [(0, (0, R(-12), R(-20))), (N, (0, R(-12), R(25)))])
padlock((0, -1.1, 1.75), .9)                             # fob's padlock

# ---------- recorder (the thief's gadget) ----------
rec = b3d.empty('Rec', (1.7, -1.4, 0))
rb = box(rec_m, (0, 0, .25), (.7, .45, .5), bevel=.05); rb.parent = rec
ant = b3d.prim('cylinder', [rim_m], vertices=8, radius=.02, depth=.7, location=(0, 0, 0)); ant.parent = rec; ant.location = (.22, 0, .82)
rl = b3d.smooth(b3d.prim('uv_sphere', [no_m], segments=12, ring_count=6, radius=.06, location=(0, 0, 0))); rl.parent = rec; rl.location = (-.18, -.24, .38)
b3d.visible(rec, [(s2, N)])

# ---------- events ----------
TRAVEL = 34
P1 = s1 + 6                         # hook press (counter 40, not shown)
P2 = s2 + 6                         # press 41 - recorder copies it
P3 = s3 + int((e3 - s3) * .4)       # press 42 (counter shown)
P4 = s4 + 8                         # 42 into the padlock -> code flies
A4 = P4 + 24 + TRAVEL               # code reaches the car (inside shot 5 or late in 4)
OK = s6 + 6                         # tick + unlock
BAD = s6 + int((e6 - s6) * .5)      # replay of the old code
def press(f):
    for bt in btns[:1]: keys(bt, 'location', [(f - 2, (0, -.085, .15)), (f, (0, -.05, .15)), (f + 4, (0, -.085, .15))])
LEDK = []
for f in (P1, P2, P3, P4): press(f); LEDK += [(f - 1, 0.), (f, 6.), (f + 8, 0.)]
b3d.key_input(led_m, 'Emission Strength', [(0, 0.)] + LEDK)
def wave(f0, m, y0=FY + .3, y1=CY - .9, z=1.4, n=3, name='W'):
    for k in range(n):
        t = b3d.smooth(b3d.prim('torus', [m], major_radius=.3, minor_radius=.025, location=(0, y0, z), rotation=(R(90), 0, 0)))
        a = f0 + 4 * k
        keys(t, 'location', [(a, (0, y0, z)), (a + TRAVEL, (0, y1, z))])
        keys(t, 'scale', [(a, (.4, .4, .4)), (a + TRAVEL, (1.8, 1.8, 1.8))])
        b3d.visible(t, [(a, a + TRAVEL)])
def fly(o, f0, f1, a, b):
    keys(o, 'location', [(f0, a), (f1, b)])
blinks = []
for f in (P1 + TRAVEL, P2 + TRAVEL, OK, OK + 12):
    blinks += [(f, 0.), (f + 1, 5.), (f + 6, 5.), (f + 7, 0.)]
b3d.key_input(blink_m, 'Emission Strength', [(0, 0.)] + blinks)
keys(blk.data, 'energy', [(0, 0)] + [(f, v * 60) for f, v in blinks])

# hook press (40) and press 41 (copied by the recorder)
wave(P1, wave_m)
c40 = text('5E09B2', (0, FY, 2.0), .26, code_m, [(P1, P1 + TRAVEL)]); fly(c40, P1, P1 + TRAVEL, (0, FY, 2.0), (0, CY - .9, 2.2))
wave(P2, wave_m)
c41 = text('7F3A9C', (0, FY, 2.0), .26, code_m, [(P2, P2 + TRAVEL)]); fly(c41, P2, P2 + TRAVEL, (0, FY, 2.0), (0, CY - .9, 2.2))
copy = text('7F3A9C', (1.7, -1.6, 1.25), .22, no_m, [(P2 + 14, N)])
recdot = text('REC', (1.7, -1.6, 1.55), .14, no_m, [(P2 + 14, s3)])
b3d.key_input(no_m, 'Emission Strength', [(0, 4.), (P2 + 14, 4.), (P2 + 18, 8.), (P2 + 24, 4.)])

# counter above the fob
text('41', (0, FY, 2.05), .5, num_m, [(s3, P3)])
n42 = text('42', (0, FY, 2.05), .5, num_m, [(P3, P4 + 24)])
fly(n42, P4, P4 + 20, (0, FY, 2.05), (0, -1.1, 1.75))
# scrambled code leaves the padlock and flies to the car
wave(P4 + 22, wave_m, y0=-.9)
c42 = text('D8E20B', (0, -.9, 2.15), .26, code_m, [(P4 + 22, A4 + 14)]); fly(c42, P4 + 22, A4, (0, -.9, 2.15), (0, CY - .5, 2.2))
# car side: decoded number vs last one
d42 = text('42', (0, CY - .5, 2.65), .42, num_m, [(A4 + 14, s7)])
last = text('OXIRGI: 41', (0, CY - .5, 3.15), .2, num_m, [(s5, s7)])
# tick and X
tick = b3d.empty('Tick', (.75, CY - .5, 2.65))
for c, s, r in (((-.13, 0, -.04), (.08, .05, .3), (0, -45, 0)), ((.1, 0, .1), (.08, .05, .62), (0, 35, 0))):
    t = box(ok_m, c, s, rot=r); t.parent = tick
b3d.visible(tick, [(OK, BAD)])
xx = b3d.empty('X', (.75, CY - .5, 2.65))
for r in (45, -45):
    t = box(no_m, (0, 0, 0), (.09, .05, .7), rot=(0, r, 0)); t.parent = xx
b3d.visible(xx, [(BAD + TRAVEL, N)])
wave(BAD, bad_m, y0=-1.2, y1=CY - .9, z=1.1)
rc = text('7F3A9C', (1.7, -1.4, 1.25), .24, no_m, [(BAD, BAD + TRAVEL + 6)]); fly(rc, BAD, BAD + TRAVEL, (1.7, -1.4, 1.25), (0, CY - .6, 2.2))
old = text('41', (0, CY - .5, 2.65), .42, no_m, [(BAD + TRAVEL, N)])
b3d.visible(d42, [(A4 + 14, BAD + TRAVEL)])

# ---------- lights ----------
b3d.light('AREA', 'Key', (4, -5, 6), 600, (1, .95, .88), 7, rot=(50, 0, 35))
b3d.light('AREA', 'Fill', (-5, -4, 3), 260, (.62, .74, 1), 6, rot=(70, 0, -45))
b3d.light('AREA', 'Back', (0, 6, 4), 250, (.6, .7, 1), 6, rot=(-60, 0, 0))

# ---------- timeline ----------
cam, tgt = b3d.camera(30)
b3d.shot(cam, tgt, s1, e1, (1.1, -6.6, 2.2), (.9, -6.1, 2.1), (0, .3, 1.35))
b3d.shot(cam, tgt, s2, e2, (4.2, -4.6, 2.3), (3.9, -4.2, 2.2), (.6, -.4, 1.0))
b3d.shot(cam, tgt, s3, e3, (.5, -5.0, 1.8), (.4, -4.7, 1.75), (0, FY, 1.55))
b3d.shot(cam, tgt, s4, e4, (1.6, -5.2, 2.4), (1.4, -4.6, 2.3), (0, -1.6, 1.7))
b3d.shot(cam, tgt, s5, e5, (.9, -.6, 2.6), (.7, -.2, 2.5), (0, CY, 2.0))
b3d.shot(cam, tgt, s6, e6, (-1.5, -2.2, 2.7), (-1.3, -1.9, 2.65), (.2, 1.8, 1.9))
b3d.shot(cam, tgt, s7, e7, (1.0, -6.0, 2.2), (1.4, -8.2, 2.9), (0, .3, 1.35))
b3d.render(OUT, cfg.get('frames'))
