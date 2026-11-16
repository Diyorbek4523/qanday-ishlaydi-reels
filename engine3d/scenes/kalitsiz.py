"""Kalitsiz kirish (keyless entry): a car broadside, a key fob nearby. Touching the door handle makes the car send a weak
short-range radio question (blue rings, range ring on the ground; a far key stays asleep). The near key wakes up, runs the
question through its golden padlock (secret key) and answers with a code (orange). The car checks it -> tick, padlock opens,
lights blink. Inside the cabin zone (green ring) the START button lights up. 7 shots."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.025, .03, .07), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))
R = math.radians

# ---------- materials ----------
ground_m = b3d.mat('Ground', (.16, .17, .2), .8, bump=.1)
line_m = b3d.mat('Line', (.9, .85, .5), .6)
car_m = b3d.mat('Car', (.1, .35, .75), .25, metal=.4)
glass_m = b3d.mat('Glass', (.08, .12, .18), .1, metal=.3)
tyre_m = b3d.mat('Tyre', (.05, .05, .06), .7)
rim_m = b3d.mat('Rim', (.75, .77, .8), .25, metal=.9)
head_m = b3d.mat('Head', (1, .95, .8), .2, emit=(1, .92, .7), estr=.4)
tail_m = b3d.mat('Tail', (.8, .1, .08), .3, emit=(1, .1, .05), estr=.5)
blink_m = b3d.mat('Blink', (1, .55, .1), .3, emit=(1, .5, .05), estr=0)
handle_m = b3d.mat('Handle', (.8, .82, .85), .25, metal=.8, emit=(.3, .8, 1), estr=0)
fob_m = b3d.mat('Fob', (.07, .07, .08), .35)
fob2_m = b3d.mat('Fob2', (.2, .2, .22), .5)
btn_m = b3d.mat('Btn', (.3, .31, .34), .4)
led_m = b3d.mat('Led', (.2, 1, .35), .3, emit=(.2, 1, .35), estr=0)
off_m = b3d.mat('LedOff', (.15, .15, .16), .5)
gold = b3d.mat('Gold', (1, .75, .25), .25, metal=1.0, emit=(1, .7, .2), estr=.15)
ask_m = b3d.mat('Ask', (.3, .8, 1), .4, emit=(.3, .8, 1), estr=3.5)
ans_m = b3d.mat('Ans', (1, .6, .15), .4, emit=(1, .55, .1), estr=3.5)
zone_m = b3d.mat('Zone', (.3, .8, 1), .4, emit=(.3, .8, 1), estr=2.5)
in_m = b3d.mat('In', (.2, 1, .35), .3, emit=(.2, 1, .35), estr=3)
grey_m = b3d.mat('Grey', (.6, .62, .66), .5, emit=(.6, .62, .66), estr=.8)
ok_m = b3d.mat('Ok', (.2, 1, .35), .3, emit=(.2, 1, .35), estr=4)
start_m = b3d.mat('Start', (.25, .27, .3), .3, emit=(.2, 1, .35), estr=0)
white_m = b3d.mat('White', (1, 1, 1), .4, emit=(1, 1, 1), estr=1.6)

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
    return root, t
def make_fob(loc, body_m, led):
    fob = b3d.empty('Fob', loc)
    body = box(body_m, (0, 0, 0), (.42, .16, .8), bevel=.12); body.parent = fob
    for z in (.15, -.12):
        bt = b3d.smooth(b3d.prim('cylinder', [btn_m], vertices=24, radius=.11, depth=.05, location=(0, 0, 0), rotation=(R(90), 0, 0)))
        bt.parent = fob; bt.location = (0, -.085, z)
    l = b3d.smooth(b3d.prim('uv_sphere', [led], segments=12, ring_count=6, radius=.045, location=(0, 0, 0))); l.parent = fob; l.location = (.12, -.08, .33)
    ring = b3d.smooth(b3d.prim('torus', [rim_m], major_radius=.08, minor_radius=.02, location=(0, 0, 0))); ring.parent = fob; ring.location = (0, 0, .47); ring.rotation_euler = (0, R(90), 0)
    return fob

# ---------- ground ----------
box(ground_m, (0, 0, -.05), (30, 30, .1))
for x in (-3.5, 3.5): box(line_m, (x, 2.6, .005), (.1, 4.5, .01))

# ---------- car (broadside, at y = CY) ----------
CY = 3.2
box(car_m, (0, CY, .62), (3.4, 1.55, .62), bevel=.18)
box(car_m, (-.15, CY, 1.12), (1.9, 1.35, .5), bevel=.2)
box(glass_m, (-.15, CY - .6, 1.14), (1.7, .2, .36), bevel=.08)
for x in (-1.15, 1.15):
    for y in (CY - .72, CY + .72):
        b3d.smooth(b3d.prim('cylinder', [tyre_m], vertices=32, radius=.36, depth=.26, location=(x, y, .36), rotation=(R(90), 0, 0)))
        b3d.smooth(b3d.prim('cylinder', [rim_m], vertices=24, radius=.2, depth=.28, location=(x, y, .36), rotation=(R(90), 0, 0)))
for x, m in ((1.66, head_m), (-1.66, tail_m)):
    box(m, (x, CY - .55, .75), (.1, .3, .14), bevel=.03)
[box(blink_m, (x, CY - .74, .78), (.2, .06, .1), bevel=.02) for x in (-1.5, 1.5)]
blk = b3d.light('POINT', 'BlinkL', (0, CY - 1.6, 1.2), 0, (1, .6, .15), .5)
HX, HY, HZ = .1, CY - .8, .9
handle = box(handle_m, (HX, HY, HZ), (.34, .07, .08), bevel=.02)
clock, cshack = padlock((0, CY - .1, 1.95), 1.0)                 # car's padlock (same secret key)

# ---------- keys ----------
KY = -.6
fob = make_fob((0, KY, 1.2), fob_m, led_m)
far = make_fob((3.9, -3.4, 1.0), fob2_m, off_m); far.rotation_euler = (0, R(-10), R(-25))
klock, _ = padlock((.75, KY, 1.25), .7)                          # the key's padlock

# ---------- events ----------
TR = 26
def rings(f0, m, a, b, n=3, r0=.35, r1=1.6):
    for k in range(n):
        t = b3d.smooth(b3d.prim('torus', [m], major_radius=.3, minor_radius=.025, location=a, rotation=(R(90), 0, 0)))
        f = f0 + 4 * k
        keys(t, 'location', [(f, a), (f + TR, b)]); keys(t, 'scale', [(f, (r0,) * 3), (f + TR, (r1,) * 3)])
        b3d.visible(t, [(f, f + TR)])
A, B = (HX, HY - .1, HZ + .1), (0, KY + .2, 1.3)
blinks, hk, lk = [], [(0, 0.)], [(0, 0.)]
def touch(f):                      # the handle lights up when a hand touches it
    hk.extend([(f - 2, 0.), (f, 5.), (f + 14, 5.), (f + 22, 0.)])
def unlock(f):
    for g in (f, f + 12): blinks.extend([(g, 0.), (g + 1, 5.), (g + 6, 5.), (g + 7, 0.)])

# 1: hook - the whole exchange once, quickly
Q1 = s1 + 14; touch(Q1); rings(Q1 + 2, ask_m, A, B); rings(Q1 + TR + 6, ans_m, B, A, r0=1.2, r1=.4); unlock(Q1 + 2 * TR + 12)
lk += [(Q1 + TR, 0.), (Q1 + TR + 2, 6.), (Q1 + 2 * TR + 10, 6.), (Q1 + 2 * TR + 16, 0.)]
# 2: touch the handle -> the question goes out
T2 = s2 + 12; touch(T2)
for k in range(3): rings(T2 + 4 + 26 * k, ask_m, A, (HX, HY - 2.4, HZ + .3), r0=.3, r1=2.2)
qm = text('?', (HX, HY - .5, HZ + .75), .5, ask_m, [(T2 + 4, e2)])
keys(qm, 'scale', [(T2 + 4, (.3,) * 3), (T2 + 16, (1,) * 3)])
# 3: short range - ring on the ground; the far key sleeps, the near one wakes up
zone = b3d.smooth(b3d.prim('torus', [zone_m], major_radius=4.0, minor_radius=.05, major_segments=96, location=(HX, HY, .04)))
b3d.visible(zone, [(s3, s4)]); keys(zone, 'scale', [(s3, (.15, .15, 1)), (s3 + 30, (1, 1, 1))])
zzz = text('Zzz', (3.9, -3.4, 1.85), .32, grey_m, [(s3 + 30, s4)])
b3d.visible(far, [(s3, s4)])
W3 = s3 + int((e3 - s3) * .55); lk += [(W3 - 2, 0.), (W3, 6.)]      # awake from here on
rings(s3 + 8, ask_m, A, B)
# 4: question in, through the padlock, answer out
A4 = s4 + 24
q4 = text('7F3A ?', (0, 1.6, 2.0), .26, ask_m, [(s4, s4 + int((e4 - s4) * .5))])
keys(q4, 'location', [(s4, (0, 1.6, 2.0)), (A4, (0, KY, 1.95))])
R4 = s4 + int((e4 - s4) * .5)
a4 = text('D8E2', (.75, KY, 1.85), .28, ans_m, [(R4, e4)])
keys(a4, 'location', [(R4, (.75, KY, 1.85)), (R4 + 14, (.3, KY, 2.1)), (e4, (.1, 2.2, 2.2))])
rings(R4 + 12, ans_m, B, A, r0=.5, r1=1.6)
# 5: the car checks the answer -> tick, padlock opens, lights blink
a5 = text('D8E2', (0, KY, 2.1), .3, ans_m, [(s5, s6)])
keys(a5, 'location', [(s5, (0, .6, 2.1)), (s5 + 20, (-.1, CY - .5, 2.75))])
rings(s5, ans_m, (0, .4, 1.4), A, r0=1.2, r1=.4)
OK = s5 + int((e5 - s5) * .45)
tick = b3d.empty('Tick', (.75, CY - .5, 2.75))
for c, s, r in (((-.13, 0, -.04), (.08, .05, .3), (0, -45, 0)), ((.1, 0, .1), (.08, .05, .62), (0, 35, 0))):
    t = box(ok_m, c, s, rot=r); t.parent = tick
b3d.visible(tick, [(OK, s6)])
keys(cshack, 'location', [(OK, (0, 0, .22)), (OK + 8, (.1, 0, .42))])
keys(cshack, 'rotation_euler', [(OK, (R(90), 0, 0)), (OK + 8, (R(90), R(-25), 0))])
unlock(OK + 4)
b3d.visible(clock, [(0, s6)]); b3d.visible(klock, [(0, s6)])
# 6: the key is inside the cabin zone -> the START button works
keys(fob, 'location', [(0, (0, KY, 1.2)), (s6 - 1, (0, KY, 1.2)), (s6, (-.15, CY - .2, 1.95)), (N, (-.15, CY - .2, 1.95))])
cab = b3d.smooth(b3d.prim('torus', [in_m], major_radius=1.25, minor_radius=.035, major_segments=64, location=(-.15, CY, 1.55)))
cab.scale = (1, .75, 1); b3d.visible(cab, [(s6 + 10, N)])
G6 = s6 + int((e6 - s6) * .55)
SX, SY, SZ = 1.75, CY - 1.3, 1.75
sb = b3d.smooth(b3d.prim('cylinder', [start_m], vertices=48, radius=.34, depth=.1, location=(SX, SY, SZ), rotation=(R(90), 0, 0)))
sr = b3d.smooth(b3d.prim('torus', [rim_m], major_radius=.36, minor_radius=.03, location=(SX, SY, SZ), rotation=(R(90), 0, 0)))
st = text('START', (SX, SY - .07, SZ), .15, white_m)
for o in (sb, sr, st): b3d.visible(o, [(s6, N)])
keys(sb, 'location', [(G6 - 6, (SX, SY, SZ)), (G6, (SX, SY + .06, SZ)), (G6 + 6, (SX, SY, SZ))])
b3d.key_input(start_m, 'Emission Strength', [(0, 0.), (G6 - 1, 0.), (G6 + 2, 3.5)])
b3d.key_input(head_m, 'Emission Strength', [(0, .4), (G6 + 4, .4), (G6 + 10, 6.)])
hl = b3d.light('SPOT', 'HeadL', (1.8, CY - .55, .75), 0, (1, .95, .8), .3, rot=(90, 0, -90))
keys(hl.data, 'energy', [(0, 0), (G6 + 4, 0), (G6 + 10, 500)])

b3d.key_input(handle_m, 'Emission Strength', sorted(hk))
b3d.key_input(led_m, 'Emission Strength', sorted(lk))
b3d.key_input(blink_m, 'Emission Strength', [(0, 0.)] + sorted(blinks))
keys(blk.data, 'energy', [(0, 0)] + [(f, v * 60) for f, v in sorted(blinks)])
keys(fob, 'rotation_euler', [(0, (0, R(-12), R(-18))), (N, (0, R(-12), R(22)))])

# ---------- lights ----------
b3d.light('AREA', 'Key', (4, -5, 6), 600, (1, .95, .88), 7, rot=(50, 0, 35))
b3d.light('AREA', 'Fill', (-5, -4, 3), 260, (.62, .74, 1), 6, rot=(70, 0, -45))
b3d.light('AREA', 'Back', (0, 6, 4), 250, (.6, .7, 1), 6, rot=(-60, 0, 0))

# ---------- timeline ----------
cam, tgt = b3d.camera(30)
b3d.shot(cam, tgt, s1, e1, (1.3, -4.4, 2.0), (1.1, -4.0, 1.95), (0, .9, 1.25))
b3d.shot(cam, tgt, s2, e2, (1.5, -.4, 1.7), (1.3, 0, 1.6), (HX, HY, HZ + .2))
b3d.shot(cam, tgt, s3, e3, (2.5, -9.5, 7.0), (2.2, -9.0, 6.6), (1.2, .4, .4))
b3d.shot(cam, tgt, s4, e4, (1.3, -3.6, 1.9), (1.1, -3.2, 1.85), (.3, KY, 1.6))
b3d.shot(cam, tgt, s5, e5, (2.8, -2.4, 2.6), (2.5, -2.0, 2.5), (.2, CY - .4, 1.8))
b3d.shot(cam, tgt, s6, e6, (2.9, -2.6, 2.7), (2.6, -2.2, 2.6), (.6, CY - .6, 1.5))
b3d.shot(cam, tgt, s7, e7, (1.2, -4.6, 2.3), (1.7, -7.4, 3.1), (0, 1.6, 1.3))
b3d.render(OUT, cfg.get('frames'))
