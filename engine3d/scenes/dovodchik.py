"""Podyezd eshigi dovodchigi: door slowly closing; close-up of the closer box and arm while the door opens;
magnified cutaway (spring, piston, oil, narrow return channel); adjusting screw; last-stretch fast latch; pull back. 7 shots."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy
from mathutils import Vector

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.02, .02, .045), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))
RX = math.pi / 2

def blend(m, a):
    b3d.bsdf(m).inputs['Alpha'].default_value = a
    try: m.surface_render_method = 'BLENDED'
    except Exception: pass
    return m

floor_m = b3d.mat('Floor', (.35, .33, .3), .7)
wall_m = b3d.mat('Wall', (.13, .2, .24), .85, bump=.02)
stair_m = b3d.mat('Stair', (.4, .38, .35), .8)
door_m = b3d.mat('Door', (.55, .25, .12), .5)
trim_m = b3d.mat('Trim', (.3, .15, .08), .5)
metal_m = b3d.mat('Metal', (.6, .62, .66), .3, metal=.8)
dark_m = b3d.mat('DarkMetal', (.12, .12, .14), .4, metal=.6)
brass_m = b3d.mat('Brass', (.85, .62, .25), .3, metal=.85)
glass_m = blend(b3d.mat('Shell', (.75, .8, .9), .1, metal=.3), .22)
spring_m = b3d.mat('Spring', (.95, .75, .2), .3, metal=.7, emit=(1, .7, .1), estr=.8)
piston_m = b3d.mat('Piston', (.85, .2, .15), .35, metal=.3)
oil_m = blend(b3d.mat('Oil', (.7, .4, .05), .2, emit=(1, .55, .05), estr=.25), .16)
bead_m = b3d.mat('Bead', (1, .7, .1), .2, emit=(1, .65, .1), estr=4)
arrow_m = b3d.mat('Arrow', (.3, .9, 1), .3, emit=(.3, .9, 1), estr=4)
red_m = b3d.mat('Narrow', (1, .15, .1), .3, emit=(1, .15, .1), estr=3)
lamp_m = b3d.mat('Lamp', (1, .9, .7), .3, emit=(1, .85, .6), estr=5)

def box(name, m, loc, dims, bev=0):
    ob = b3d.prim('cube', [m], size=1, location=loc); ob.scale = dims; ob.name = name
    if bev: ob.modifiers.new('bev', 'BEVEL').width = bev
    return ob

def cyl(m, r, d, loc, rot=(0, 0, 0), v=32):
    ob = b3d.smooth(b3d.prim('cylinder', [m], vertices=v, radius=r, depth=d, location=loc)); ob.rotation_euler = rot; return ob

# ---------- door angle over time (degrees; + swings away from camera) ----------
def L(a, b, t): return a + (b - a) * t
K = [(s1, 80), (e1, 50), (int(L(s2, e2, .2)), 50), (int(L(s2, e2, .6)), 82), (int(L(s3, e3, .3)), 82), (e3, 70),
     (e4, 40), (e5, 22), (int(L(s6, e6, .55)), 12), (int(L(s6, e6, .72)), 0), (e7 + 1, 0)]
def ang(f):
    for (f0, a0), (f1, a1) in zip(K[:-1], K[1:]):
        if f0 <= f <= f1:
            t = (f - f0) / max(1, f1 - f0)
            if a1 == 0 and a0 > 0: t = t * t          # last stretch: speeds up into the latch
            else: t = t * t * (3 - 2 * t)
            return L(a0, a1, t)
    return K[-1][1] if f > K[-1][0] else K[0][1]

# ---------- stairwell: wall with door opening, frame, steps, lamp ----------
b3d.prim('plane', [floor_m], size=14, location=(0, 0, 0))
DW, DH = 1.0, 2.1
box('WallL', wall_m, (-1.6, .1, 1.6), (3.2, .2, 3.2))
box('WallR', wall_m, (DW + 1.6, .1, 1.6), (3.2, .2, 3.2))
box('WallT', wall_m, (DW / 2, .1, DH + .55), (DW, .2, 1.1))
box('TrimL', trim_m, (-.04, -.03, DH / 2), (.08, .06, DH + .08))
box('TrimR', trim_m, (DW + .04, -.03, DH / 2), (.08, .06, DH + .08))
box('TrimT', trim_m, (DW / 2, -.03, DH + .04), (DW + .16, .06, .08))
for i in range(6): box(f'Step{i}', stair_m, (.5, 1.6 + i * .32, .09 + i * .18), (1.6, .34, .18 + i * .36))
box('BackWall', wall_m, (.5, 3.8, 1.8), (4, .2, 3.6))
box('Lamp', lamp_m, (-1.0, -.06, 2.6), (.25, .1, .12), .03)
b3d.light('POINT', 'Stair', (.6, 2.2, 2.6), 120, (1, .8, .55), .3)

door = b3d.empty('Door', (0, 0, 0)); door.rotation_mode = 'XYZ'
for o in (box('Slab', door_m, (0, 0, 0), (DW - .02, .05, DH - .02), .01),):
    o.parent = door; o.location = (DW / 2, 0, DH / 2)
hd = cyl(brass_m, .025, .14, (0, 0, 0), (RX, 0, 0)); hd.parent = door; hd.location = (.9, -.07, 1.0)
cb = box('CloserBody', dark_m, (0, 0, 0), (.38, .07, .075), .012); cb.parent = door; cb.location = (.3, -.065, 1.98)
for x in (.11, .49): c = cyl(metal_m, .035, .005, (0, 0, 0), (0, RX, 0)); c.parent = door; c.location = (x, -.065, 1.98)
SP = Vector((.42, -.1))                       # spindle, door-local xy
sp = cyl(metal_m, .018, .06, (0, 0, 0)); sp.parent = door; sp.location = (SP.x, SP.y, 2.02)
FP = Vector((.62, -.09)); ZA = 2.05           # frame shoe (world) and arm plane height
box('Shoe', dark_m, (FP.x, -.05, DH + .04), (.09, .05, .07), .01)
cyl(metal_m, .016, .1, (FP.x, FP.y, ZA + .03))
L1, L2 = .3, .45
arm1 = box('Arm1', metal_m, (0, 0, 0), (1, 1, 1), .004)
arm2 = box('Arm2', metal_m, (0, 0, 0), (1, 1, 1), .004)
elb = cyl(metal_m, .02, .04, (0, 0, ZA))
def put(ob, a, b, z, w=.03, h=.015):
    d = b - a; ob.location = (a.x + d.x / 2, a.y + d.y / 2, z); ob.rotation_euler = (0, 0, math.atan2(d.y, d.x))
    ob.scale = (d.length, w, h)
    for k in ('location', 'rotation_euler', 'scale'): ob.keyframe_insert(k, frame=f)

for f in range(0, e7 + 2, 2):
    a = math.radians(ang(f)); door.rotation_euler = (0, 0, a); door.keyframe_insert('rotation_euler', frame=f)
    P = Vector((SP.x * math.cos(a) - SP.y * math.sin(a), SP.x * math.sin(a) + SP.y * math.cos(a)))
    d = (FP - P).length; d = min(max(d, abs(L1 - L2) + 1e-3), L1 + L2 - 1e-3)
    u = (FP - P).normalized(); x = (L1 * L1 - L2 * L2 + d * d) / (2 * d); hgt = math.sqrt(max(0, L1 * L1 - x * x))
    n = Vector((u.y, -u.x))                  # pick the elbow on the camera (-y) side
    E = P + u * x + n * hgt
    if E.y > P.y + u.y * x - n.y * hgt and False: E = P + u * x - n * hgt
    put(arm1, P, E, ZA); put(arm2, E, FP, ZA - .02)
    elb.location = (E.x, E.y, ZA - .01); elb.keyframe_insert('location', frame=f)

# ---------- magnified cutaway of the closer, at CX ----------
CX, CZ = 6.0, 1.2
box('CutBack', wall_m, (CX, 1.2, CZ), (4, .1, 3))
shell = cyl(glass_m, .25, 1.6, (CX, 0, CZ), (0, RX, 0), 48)
for x in (-.8, .8): cyl(dark_m, .27, .05, (CX + x, 0, CZ), (0, RX, 0), 48)
piston = cyl(piston_m, .235, .08, (0, 0, 0), (0, RX, 0), 48)
rod = box('Rack', metal_m, (0, 0, 0), (.5, .05, .05));
oilL = cyl(oil_m, .23, 1, (0, 0, 0), (0, RX, 0), 48)
oilR = cyl(oil_m, .23, 1, (0, 0, 0), (0, RX, 0), 48)
NR = 13
rings = [b3d.smooth(b3d.prim('torus', [spring_m], major_radius=.17, minor_radius=.02, major_segments=32, minor_segments=8,
                             location=(0, 0, 0))) for _ in range(NR)]
for r in rings: r.rotation_euler = (math.radians(8), RX, 0)
def px(f): return -.45 + .7 * ang(f) / 82
for f in range(0, e7 + 2, 2):
    p = px(f); piston.location = (CX + p, 0, CZ); piston.keyframe_insert('location', frame=f)
    rod.location = (CX + p - .28, 0, CZ); rod.keyframe_insert('location', frame=f)
    l0, l1 = -.78, p - .045; oilL.location = (CX + (l0 + l1) / 2, 0, CZ); oilL.scale = (1, 1, l1 - l0)
    r0, r1 = p + .045, .78; oilR.location = (CX + (r0 + r1) / 2, 0, CZ); oilR.scale = (1, 1, r1 - r0)
    for o in (oilL, oilR): o.keyframe_insert('location', frame=f); o.keyframe_insert('scale', frame=f)
    for i, r in enumerate(rings):
        r.location = (CX + L(p + .07, .76, i / (NR - 1)), 0, CZ); r.keyframe_insert('location', frame=f)

# return channel above the cylinder: left chamber -> narrow valve at x=0 -> right chamber
CH = .42
cyl(glass_m, .035, CH - .2, (CX - .68, 0, CZ + .2 + (CH - .2) / 2))
cyl(glass_m, .035, CH - .2, (CX + .68, 0, CZ + .2 + (CH - .2) / 2))
cyl(glass_m, .035, 1.36, (CX, 0, CZ + CH), (0, RX, 0))
narrow = cyl(red_m, .045, .06, (CX, 0, CZ + CH), (0, RX, 0)); narrow.scale = (1, 1, 1)
scr = b3d.empty('Screw', (CX, 0, CZ + CH + .14))
sh = cyl(brass_m, .025, .16, (0, 0, 0), v=12); sh.parent = scr; sh.location = (0, 0, 0)
hdd = cyl(brass_m, .05, .03, (0, 0, 0), v=24); hdd.parent = scr; hdd.location = (0, 0, .09)
sl = box('Slot', dark_m, (0, 0, 0), (.08, .012, .012)); sl.parent = scr; sl.location = (0, 0, .106)
for f in range(0, e7 + 2, 4):
    t = min(1, max(0, (f - s5) / max(1, e5 - s5)))
    scr.rotation_euler = (0, 0, t * 4 * math.pi); scr.location = (CX, 0, CZ + CH + .14 - .035 * t)
    scr.keyframe_insert('rotation_euler', frame=f); scr.keyframe_insert('location', frame=f)
b3d.flicker(b3d.light('POINT', 'NarrowGlow', (CX, -.15, CZ + CH), 4, (1, .3, .1), .05), 'energy', s4, e5, 2, 7, 3, 3)

pts = [Vector((CX + x, 0, CZ + z)) for x, z in ((-.68, .05), (-.68, CH), (.68, CH), (.68, .05))]
seg = [(pts[k + 1] - pts[k]).length for k in range(3)]; TOT = sum(seg)
def at(d):
    for k, s in enumerate(seg):
        if d <= s: return pts[k].lerp(pts[k + 1], d / s)
        d -= s
    return pts[-1]
NB = 16
for k in range(NB):
    bd = b3d.prim('uv_sphere', [bead_m], radius=.022, segments=10, ring_count=6, location=(0, 0, 0))
    d = k * TOT / NB
    for f in range(s2, e5 + 2, 2):
        rate = max(0., ang(f - 2) - ang(f))          # closing speed
        d = (d + rate * .03) % TOT; bd.location = at(d); bd.keyframe_insert('location', frame=f)
    b3d.visible(bd, [(s3, e5)])

ar = b3d.arrow('PushArrow', (CX + .55, -.32, CZ - .34), (CX - .1, -.32, CZ - .34), arrow_m, .02)
b3d.visible(ar, [(int(L(s3, e3, .35)), e4)])

# ---------- lights ----------
b3d.light('AREA', 'Key', (-1.2, -2.6, 2.8), 220, (1, .88, .75), 3, rot=(50, 0, -25))
b3d.light('AREA', 'Fill', (2.2, -2.0, 1.6), 80, (.6, .7, 1), 3, rot=(65, 0, 45))
b3d.light('AREA', 'CutKey', (CX - .8, -1.8, CZ + 1.4), 120, (1, .9, .8), 2, rot=(50, 0, -20))
b3d.light('AREA', 'CutFill', (CX + 1.2, -1.4, CZ + .2), 50, (.6, .7, 1), 2, rot=(75, 0, 45))

# ---------- camera ----------
cam, tgt = b3d.camera(30)
b3d.shot(cam, tgt, s1, e1, (-.4, -3.7, 1.7), (-.3, -3.4, 1.65), (.5, .3, 1.15), lens=30)
b3d.shot(cam, tgt, s2, e2, (.95, -1.15, 2.05), (.85, -1.0, 2.02), (.3, .05, 1.98), lens=36)
b3d.shot(cam, tgt, s3, e3, (CX + .1, -3.4, CZ + .6), (CX, -3.1, CZ + .55), (CX, 0, CZ + .1), lens=30)
b3d.shot(cam, tgt, s4, e4, (CX - .6, -2.2, CZ + .9), (CX - .4, -2.1, CZ + .85), (CX, 0, CZ + .25), lens=32)
b3d.shot(cam, tgt, s5, e5, (CX + .3, -1.0, CZ + .8), (CX + .25, -.9, CZ + .75), (CX, 0, CZ + .42), lens=40)
b3d.shot(cam, tgt, s6, e6, (1.9, -2.5, 1.7), (1.7, -2.3, 1.65), (.45, 0, 1.25), lens=30)
b3d.shot(cam, tgt, s7, e7, (.5, -2.8, 1.5), (.5, -4.4, 2.2), (.5, 0, 1.2), lens=30)

b3d.render(OUT, cfg.get('frames'))
