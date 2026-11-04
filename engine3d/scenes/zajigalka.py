"""Zajigalka: piezo lighter cutaway. Button compresses a spring, hammer hits the crystal, voltage runs up the wire, spark jumps the gap at the
nozzle, the valve lets gas out and the spark lights it. Interior sits at y~0 in front of the back plate; the front covers show only outside views. 7 shots."""
import math, os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.04, .05, .11), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))

# ---------- materials ----------
plastic = b3d.mat('Plastic', (.75, .1, .35), .25)
back_m = b3d.mat('BackM', (.3, .05, .16), .5)
steel = b3d.mat('Steel', (.62, .65, .7), .28, metal=.9)
head_b = b3d.mat('HeadBack', (.13, .15, .2), .55, metal=.3)
orange = b3d.mat('Button', (1, .5, .08), .35)
brass = b3d.mat('Brass', (.85, .62, .2), .3, metal=.9)
hammer_m = b3d.mat('Hammer', (.4, .43, .5), .3, metal=.9)
copper = b3d.mat('Copper', (.95, .45, .15), .35, metal=.6)
crystal = b3d.mat('Crystal', (.35, .85, .95), .12, emit=(.2, .8, 1), estr=.5)
liquid = b3d.mat('Liquid', (.3, .6, .9), .1, emit=(.1, .35, .7), estr=.6)
b3d.bsdf(liquid).inputs['Alpha'].default_value = .6
try: liquid.surface_render_method = 'BLENDED'
except (AttributeError, TypeError): pass
gas = b3d.mat('Gas', (.6, .9, 1), .3, emit=(.4, .85, 1), estr=2.2)
elec = b3d.mat('Elec', (1, .9, .3), .3, emit=(1, .72, .1), estr=1.5)
spark = b3d.mat('Spark', (.8, .9, 1), .3, emit=(.65, .85, 1), estr=9)
fl_o = b3d.mat('FlameO', (.08, .03, 0), .5, emit=(1, .36, .02), estr=1.5)
fl_i = b3d.mat('FlameI', (.1, .08, .02), .5, emit=(1, .8, .3), estr=1.25)
fl_b = b3d.mat('FlameB', (.2, .45, 1), .5, emit=(.15, .4, 1), estr=1.5)
wood = b3d.mat('Table', (.3, .16, .08), .6, bump=.2)
wall = b3d.mat('Wall', (.1, .13, .22), .85)
point_m = b3d.mat('Point', (1, .8, .2), .4, emit=(1, .72, .08), estr=2.6)

def box(m, c, s, bevel=0):
    b = b3d.prim('cube', [m], size=1, location=c); b.scale = s
    if bevel:
        bv = b.modifiers.new('Bv', 'BEVEL'); bv.width = bevel; bv.segments = 4; b3d.smooth(b)
    return b
def tube(name, pts, m, r=.03):
    cv = bpy.data.curves.new(name, 'CURVE'); cv.dimensions = '3D'; cv.bevel_depth = r; cv.bevel_resolution = 3; cv.use_fill_caps = True
    sp = cv.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts): bp.co = p; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    cv.materials.append(m); return b3d.link(bpy.data.objects.new(name, cv))
def ease(u): u = min(1, max(0, u)); return u * u * (3 - 2 * u)

# ---------- room ----------
box(wood, (0, 0, -.25), (40, 30, .5))
b3d.prim('plane', [wall], size=60, location=(0, 5, 20), rotation=(math.radians(90), 0, 0))

# ---------- body: back half always there ----------
BW, BD, TOP, DECK = 2.2, 1.0, 7.2, 4.0
box(back_m, (0, .42, DECK / 2), (BW, .1, DECK), bevel=.02)
for sx in (-1, 1): box(plastic, (sx * (BW / 2 - .05), 0, DECK / 2), (.1, BD, DECK), bevel=.02)
box(plastic, (0, 0, .05), (BW, BD, .1))
box(steel, (0, 0, DECK), (BW, BD, .12), bevel=.02)
box(head_b, (0, .4, (DECK + TOP) / 2), (BW - .06, .1, TOP - DECK))
for sx in (-1, 1): box(steel, (sx * (BW / 2 - .04), .05, (DECK + TOP) / 2), (.08, .8, TOP - DECK))
box(liquid, (0, 0, 1.55), (BW - .22, BD - .18, 2.9))
r = random.Random(4)
for k in range(10):
    b = b3d.smooth(b3d.prim('uv_sphere', [gas], segments=10, ring_count=6, radius=r.uniform(.04, .08))); x0 = r.uniform(-.8, .8); ph = r.random()
    for f in range(0, N, 4):
        u = (ph + f / 90) % 1; b.location = (x0 + .04 * math.sin(f * .2 + k), -.05, .3 + u * 2.55); b.keyframe_insert('location', frame=f)

# ---------- front covers (outside views only) ----------
ext = b3d.empty('Exterior')
box(plastic, (0, -.46, DECK / 2), (BW, .08, DECK), bevel=.035).parent = ext
box(steel, (0, -.42, 5.5), (BW, .08, 3.0)).parent = ext
for z in (4.5, 5.0, 5.5, 6.0): box(head_b, (0, -.47, z), (BW * .72, .012, .16)).parent = ext

# ---------- mechanism ----------
PX = .5                             # piezo column x
BTN_UP, BTN_DOWN = 6.72, 6.2        # button bottom face
HAM_REST, HAM_HIT = 5.3, 4.92       # hammer bottom face
HAM_H = .42; SPR_L0 = 1.0
T_REL = s3 + int((e3 - s3) * .68)   # hammer released here
def btn_z(f):
    if f < s2: return BTN_DOWN       # hook: already lit
    if f < s3 + 6: return BTN_UP
    return BTN_UP + (BTN_DOWN - BTN_UP) * ease((f - s3 - 6) / max(1, T_REL - s3 - 6))
def ham_z(f):
    if f < T_REL: return HAM_REST
    return HAM_REST + (HAM_HIT - HAM_REST) * min(1, (f - T_REL) / 3)  # very fast
button = box(orange, (PX, 0, 0), (.9, .7, .62), bevel=.06)
hammer = box(hammer_m, (PX, 0, 0), (.42, .42, HAM_H), bevel=.03)
pts = []
for i in range(0, 121):
    a = i / 120 * 2 * math.pi * 7; pts.append((.19 * math.cos(a), .19 * math.sin(a), i / 120 * SPR_L0))
cv = bpy.data.curves.new('Spring', 'CURVE'); cv.dimensions = '3D'; cv.bevel_depth = .024; cv.bevel_resolution = 2
sp = cv.splines.new('POLY'); sp.points.add(len(pts) - 1)
for p, c in zip(sp.points, pts): p.co = (*c, 1)
cv.materials.append(steel); spring = b3d.link(bpy.data.objects.new('Spring', cv))
for f in range(0, N, 1):
    bz, hz = btn_z(f), ham_z(f); hz_top = hz + HAM_H
    button.location = (PX, 0, bz + .31); hammer.location = (PX, 0, hz + HAM_H / 2)
    spring.location = (PX, 0, hz_top); spring.scale = (1, 1, max(.05, (bz - hz_top) / SPR_L0))
    for o, d in ((button, 'location'), (hammer, 'location'), (spring, 'location'), (spring, 'scale')): o.keyframe_insert(d, frame=f)
box(steel, (PX, 0, 4.15), (.56, .56, .18))                # crystal seat
cry = box(crystal, (PX, 0, 4.53), (.42, .42, .74), bevel=.03)
for sx in (-1, 1): box(head_b, (PX + sx * .32, .1, 5.45), (.05, .5, 2.7))  # guide rails

NX = -.45
tube('Nozzle', [(NX, 0, DECK), (NX, 0, 5.5), (NX, 0, 6.82)], brass, r=.085)
box(brass, (NX, 0, DECK + .3), (.34, .34, .3), bevel=.03)    # valve body
b3d.smooth(b3d.prim('cone', [brass], vertices=24, radius1=.13, radius2=.06, depth=.22, location=(NX, 0, 6.92)))
WIRE = [(PX - .21, 0, 4.55), (.05, -.05, 4.7), (.05, -.05, 5.8), (.03, -.05, 6.5), (-.02, 0, 6.93)]
tube('Wire', WIRE, copper, r=.035)
def wire_at(u):
    n = len(WIRE) - 1; t = min(u, .9999) * n; i = int(t); k = t - i; P = lambda j: WIRE[max(0, min(n, j))]
    a, b, c, d = P(i - 1), P(i), P(i + 1), P(i + 2)
    return tuple(.5 * ((2 * b[m]) + (c[m] - a[m]) * k + (2 * a[m] - 5 * b[m] + 4 * c[m] - d[m]) * k * k + (3 * b[m] - a[m] - 3 * c[m] + d[m]) * k ** 3) for m in range(3))

# crystal charges: glow keyed after the hit, sparks inside
b3d.key_input(crystal, 'Emission Strength', [(0, .5), (T_REL + 1, .5), (T_REL + 3, 1.5), (e6, 1.5), (e6 + 1, .6)])
for k in range(26):
    d = b3d.smooth(b3d.prim('uv_sphere', [elec], segments=10, ring_count=6, radius=.028)); rr = random.Random(k)
    x0, z0, y0 = rr.uniform(-.17, .17), rr.uniform(-.3, .3), -.24
    for f in range(s4, e4, 2):
        d.location = (PX + x0 + .03 * math.sin(f * .7 + k), y0, 4.53 + z0 + .05 * math.sin(f * .5 + k * 2)); d.keyframe_insert('location', frame=f)
    b3d.visible(d, [(s4, e4)])
RUN = [(s4 + 18, e4), (s5, e6)]
for k in range(12):
    d = b3d.smooth(b3d.prim('uv_sphere', [elec], segments=10, ring_count=6, radius=.05)); ph = k / 12
    for a, b in RUN:
        for f in range(a, b, 2):
            d.location = wire_at((ph + (f - a) / 34) % 1); d.keyframe_insert('location', frame=f)
    b3d.visible(d, RUN)
# spark: jagged bolt across the gap between wire tip and nozzle
A, B = (-.02, -.02, 6.93), (NX + .06, -.02, 7.0)
bolts = []
for k in range(3):
    rr = random.Random(k + 9); pts = [A]
    for i in range(1, 5):
        u = i / 5; pts.append((A[0] + u * (B[0] - A[0]), -.02 + rr.uniform(-.02, .02), A[2] + u * (B[2] - A[2]) + rr.uniform(-.05, .05)))
    pts.append(B)
    cv = bpy.data.curves.new(f'Bolt{k}', 'CURVE'); cv.dimensions = '3D'; cv.bevel_depth = .024
    sp = cv.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for p, c in zip(sp.points, pts): p.co = (*c, 1)
    cv.materials.append(spark); bolts.append(b3d.link(bpy.data.objects.new(f'Bolt{k}', cv)))
SP_F = list(range(s5 + 20, e5, 4)) + list(range(s6, s6 + 26, 4))
for k, o in enumerate(bolts):
    b3d.visible(o, [(f, f + 4) for i, f in enumerate(SP_F) if i % 3 == k] or [(0, 0)])
glow_s = b3d.light('POINT', 'SparkGlow', (-.3, -.3, 6.95), 0, (.7, .85, 1), .1)
for f, v in ((0, 0), (s5 + 19, 0), (s5 + 20, 26), (s6 + 26, 26), (s6 + 27, 0)):
    glow_s.data.energy = v; glow_s.data.keyframe_insert('energy', frame=f)
# gas up the nozzle and out, then flame
GAS = [(s6, e6)]
for k in range(16):
    d = b3d.smooth(b3d.prim('uv_sphere', [gas], segments=10, ring_count=6, radius=.05)); ph = k / 16
    for a, b in GAS:
        for f in range(a, b, 2):
            u = (ph + (f - a) / 20) % 1; d.location = (NX + .03 * math.sin(k + f * .4), -.13, DECK + .2 + u * 2.8); d.keyframe_insert('location', frame=f)
    b3d.visible(d, GAS)
FL = [(s1, e1), (s6 + 14, e7)]
flame = b3d.empty('Flame', (NX, 0, 7.02))
def blob(m, sc_, z):
    o = b3d.smooth(b3d.prim('uv_sphere', [m], segments=24, ring_count=16, radius=1, location=(0, 0, z))); o.scale = sc_; o.parent = flame
    for v in o.data.vertices:  # teardrop
        if v.co.z > 0: k = (1 - v.co.z) ** .5; v.co.x *= k; v.co.y *= k
    return o
blob(fl_o, (.3, .3, .72), .66); blob(fl_i, (.16, .16, .42), .5); blob(fl_b, (.12, .12, .16), .1)
b3d.flicker(flame, 'scale', s1, e1, .92, 1.1, every=3, seed=1); b3d.flicker(flame, 'scale', s6 + 14, e7, .92, 1.1, every=3, seed=2)
b3d.visible(flame, FL)
fglow = b3d.light('POINT', 'FlameGlow', (NX, -.6, 7.9), 90, (1, .6, .25), .5); b3d.visible(fglow, FL)
pts1 = b3d.arrow('PressPt', (PX + .1, -.5, 8.0), (PX + .1, -.5, 7.45), point_m, r=.04); b3d.visible(pts1, [(s3, T_REL)])

# ---------- lights ----------
b3d.light('AREA', 'Key', (5, -9, 11), 1500, (1, .95, .88), 8, rot=(40, 0, 25))
b3d.light('AREA', 'Fill', (-7, -8, 5), 620, (.62, .74, 1), 6, rot=(70, 0, -40))
b3d.light('POINT', 'HeadFill', (0, -2.6, 5.6), 50, (1, 1, 1), 1)

# ---------- timeline ----------
cam, tgt = b3d.camera(30)
b3d.shot(cam, tgt, s1, e1, (2.2, -17, 5.4), (1.4, -15, 5.2), (0, 0, 5.0), lens=30)
b3d.shot(cam, tgt, s2, e2, (-1.3, -10.2, 4.9), (-.7, -9.0, 4.8), (0, 0, 4.1), lens=30)
b3d.shot(cam, tgt, s3, e3, (1.1, -5.6, 5.9), (.8, -4.9, 5.7), (.25, 0, 5.4), lens=30)
b3d.shot(cam, tgt, s4, e4, (.9, -3.2, 4.9), (.6, -2.8, 4.9), (.35, 0, 4.85), lens=30)
b3d.shot(cam, tgt, s5, e5, (-.3, -4.7, 6.4), (-.45, -3.0, 6.7), (-.1, 0, 6.3), (-.3, 0, 6.8), lens=30)
b3d.shot(cam, tgt, s6, e6, (-1.1, -5.3, 6.0), (-1.1, -6.0, 6.3), (-.4, 0, 6.2), (-.4, 0, 6.6), lens=30)
b3d.shot(cam, tgt, s7, e7, (1.4, -12.5, 5.2), (2.4, -16.5, 5.6), (0, 0, 4.4), lens=30)
b3d.visible(ext, [(s1, e1), (s7, e7)])
b3d.render(OUT, cfg.get('frames'))
