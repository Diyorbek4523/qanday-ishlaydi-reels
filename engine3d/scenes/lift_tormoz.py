"""Lift safety: a cutaway shaft with a cabin hanging on 4 steel ropes from the drive sheave, a speed governor pulley on top
with its own rope loop (tension pulley in the pit) tied to the cabin's safety lever, and spring buffers in the pit.
Shot 1 wide, 2 the ropes light up one by one, 3 the ropes snap and the cabin starts to fall while the governor spins up,
4 governor close-up: flyweights swing out and lock it (red), 5 under the cabin: wedges ride up and clamp the rails (sparks),
cabin stops, 6 pit buffers, 7 pull back. 7 shots."""
import math, os, sys, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy
from mathutils import Matrix

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.03, .035, .08), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))
R = math.radians

wall_m = b3d.mat('Wall', (.78, .72, .62), .7, bump=.05)
slab_m = b3d.mat('Slab', (.55, .5, .46), .7, bump=.08)
shaft_m = b3d.mat('Shaft', (.32, .35, .42), .7, bump=.05)
rail_m = b3d.mat('Rail', (.6, .62, .66), .3, metal=.8)
cab_m = b3d.mat('Cabin', (.85, .55, .2), .4, metal=.3)
cab_in = b3d.mat('CabinIn', (.95, .88, .72), .5)
steel = b3d.mat('Steel', (.75, .77, .8), .25, metal=.9)
dark = b3d.mat('Dark', (.12, .12, .14), .5, metal=.4)
motor_m = b3d.mat('Motor', (.2, .45, .35), .4, metal=.5)
gov_m = b3d.mat('Gov', (.2, .4, .9), .35, metal=.4, emit=(.2, .45, 1), estr=.4)
fly_m = b3d.mat('Fly', (.9, .8, .2), .3, metal=.5, emit=(1, .75, .1), estr=.5)
grope_m = b3d.mat('GovRope', (.25, .45, .9), .5, emit=(.2, .45, 1), estr=.3)
wedge_m = b3d.mat('Wedge', (.75, .3, .15), .3, metal=.6, emit=(1, .35, .05), estr=0)
spark_m = b3d.mat('Spark', (1, .8, .3), .3, emit=(1, .7, .2), estr=6)
spring_m = b3d.mat('Spring', (.9, .2, .15), .35, metal=.5, emit=(1, .25, .1), estr=0)
snap_m = b3d.mat('Snap', (1, .9, .6), .3, emit=(1, .85, .5), estr=6)
rope_ms = [b3d.mat(f'Rope{i}', (.15, .15, .15), .6, metal=.5, emit=(1, .75, .2), estr=0) for i in range(4)]

def box(m, c, s, bevel=0):
    b = b3d.prim('cube', [m], size=1, location=c); b.scale = s
    if bevel: bv = b.modifiers.new('Bv', 'BEVEL'); bv.width = bevel; bv.segments = 3
    return b
def keys(ob, attr, fv):
    for f, v in fv: setattr(ob, attr, v); ob.keyframe_insert(attr, frame=f)
def linear(ob):
    ad = ob.animation_data
    if not ad or not ad.action: return
    try: curves = ad.action.fcurves
    except AttributeError:
        curves = [c for l in ad.action.layers for st in l.strips for cb in st.channelbags for c in cb.fcurves]
    for c in curves:
        for k in c.keyframe_points: k.interpolation = 'LINEAR'
def parent(ob, p): ob.parent = p; ob.matrix_parent_inverse = Matrix.Translation(-p.location)

TOP = 10.0; RX = .85; Y0 = .3
# ---------- building / shaft ----------
box(slab_m, (0, 0, -.15), (12, 6, .3))
box(shaft_m, (0, 1.0, TOP / 2), (2.2, .1, TOP))
for x in (-1.15, 1.15): box(shaft_m, (x, .35, TOP / 2), (.1, 1.4, TOP))
for z in (2.5, 5.0, 7.5):
    for side in (-1, 1): box(slab_m, (side * 2.75, .2, z - .1), (3.2, 2.0, .2))
for side in (-1, 1): box(wall_m, (side * 2.75, 1.15, TOP / 2), (3.2, .1, TOP))
box(slab_m, (0, .2, TOP - .1), (2.4, 2.0, .2))
for x in (-RX, RX): box(rail_m, (x, Y0, TOP / 2), (.06, .12, TOP))

# ---------- cabin motion ----------
CH = 1.9; Z0 = 4.2; ZM = 6.0
SNAP = s3 + 8; CLAMP = s5 + 8; STOP = s5 + 14
ZS = Z0 + (ZM - Z0) * (SNAP - 0) / (SNAP)   # = ZM at SNAP
def zc(f):
    if f <= SNAP: return Z0 + (ZM - Z0) * f / SNAP
    if f <= CLAMP: u = (f - SNAP) / (CLAMP - SNAP); return ZM - 2.6 * u ** 1.6
    zcl = ZM - 2.6
    if f <= STOP: return zcl - .12 * (f - CLAMP) / (STOP - CLAMP)
    return zcl - .12
ZEND = zc(N)
cab = b3d.empty('Cabin', (0, Y0, Z0))
CW, CD = 1.5, 1.3
for c, s, m in (((0, 0, .05), (CW, CD, .1), cab_m), ((0, 0, CH), (CW, CD, .1), cab_m), ((0, CD / 2, CH / 2), (CW, .06, CH), cab_in),
                ((-CW / 2, 0, CH / 2), (.06, CD, CH), cab_in), ((CW / 2, 0, CH / 2), (.06, CD, CH), cab_in)):
    b = box(m, c, s, .01); b.parent = cab
frame_b = box(dark, (0, 0, -.12), (CW - .12, .3, .14), .01); frame_b.parent = cab        # safety plank under the cabin
lamp = b3d.light('POINT', 'CabLamp', (0, 0, 1.6), 40, (1, .9, .75), .3); lamp.parent = cab
fs = list(range(0, N, 2)) + [N - 1, SNAP, CLAMP, STOP]
fs = sorted(set(fs))
keys(cab, 'location', [(f, (0, Y0, zc(f))) for f in fs]); linear(cab)

# wedges (safety gear): pairs each side of each rail, ride up and squeeze at CLAMP
wedges = []
for x in (-RX, RX):
    for dy in (-1, 1):
        w = box(wedge_m, (0, 0, 0), (.13, .07, .3), .01); w.parent = cab
        keys(w, 'location', [(0, (x, dy * .13, -.12)), (CLAMP - 4, (x, dy * .13, -.12)), (CLAMP, (x, dy * .085, -.02))])
        wedges.append(w)
b3d.key_input(wedge_m, 'Emission Strength', [(0, 0), (CLAMP - 4, 0), (CLAMP, 5), (STOP + 20, 3), (e5, 2)])
# sparks at the rails when wedges bite
rng = random.Random(3)
for i in range(16):
    x = rng.choice((-RX, RX)); sp = b3d.prim('uv_sphere', [spark_m], radius=.025, segments=8, ring_count=6, location=(0, 0, 0))
    sp.parent = cab; a = rng.uniform(0, 2 * math.pi); d = rng.uniform(.15, .45)
    keys(sp, 'location', [(CLAMP - 1, (x, 0, -.1)), (CLAMP + 7, (x + d * math.cos(a) * .6, -.25 - rng.uniform(0, .3), -.1 + d * math.sin(a)))])
    b3d.visible(sp, [(CLAMP, CLAMP + 8)])

# lever from the cabin to the governor rope
GX = -.95; GR = .15; GY = -.5
lever = box(steel, (0, 0, 0), (.1, .2, .06)); lever.parent = cab; lever.location = (-.76, -.43, 1.0)
lever2 = box(steel, (0, 0, 0), (.07, .07, .25)); lever2.parent = cab; lever2.location = (GX + GR, GY - Y0, 1.0)

# ---------- ropes from the drive sheave ----------
SHZ = TOP + .7; SR = .45
ropes = []
for i, x in enumerate((-.15, -.05, .05, .15)):
    r_ = b3d.prim('cylinder', [rope_ms[i]], vertices=8, radius=.022, depth=1, location=(0, 0, 0))
    r_.data.transform(Matrix.Translation((0, 0, -.5)))
    r_.location = (x, Y0, SHZ)
    L = lambda f: SHZ - (zc(f) + CH)
    fv = [(f, (1, 1, L(f))) for f in fs if f <= SNAP] + [(SNAP + 3, (1, 1, 1.2)), (SNAP + 12, (1, 1, .9)), (N - 1, (1, 1, .9))]
    keys(r_, 'scale', fv); linear(r_)
    ropes.append(r_)
    stub = b3d.prim('cylinder', [rope_ms[i]], vertices=8, radius=.022, depth=.5, location=(0, 0, 0)); stub.parent = cab
    stub.location = (x, 0, CH + .3); b3d.visible(stub, [(SNAP, N)])
for i, m in enumerate(rope_ms):
    a = s2 + 6 + i * 14
    b3d.key_input(m, 'Emission Strength', [(0, 0), (a, 0), (a + 4, 2.5), (e2 - 2, 2.5), (e2 + 2, 0)])
snapfl = b3d.prim('uv_sphere', [snap_m], radius=.35, segments=16, ring_count=8, location=(0, Y0 - .1, ZM + CH + .2))
b3d.visible(snapfl, [(SNAP, SNAP + 4)])
mot = box(motor_m, (1.0, Y0, SHZ - .15), (.9, .7, .7), .05)
sheave = b3d.prim('cylinder', [steel], vertices=48, radius=SR, depth=.4, location=(0, Y0, SHZ), rotation=(R(90), 0, 0))

# ---------- speed governor ----------
GZ = TOP + .45
gov = b3d.prim('cylinder', [gov_m], vertices=48, radius=GR, depth=.1, location=(GX, GY, GZ), rotation=(R(90), 0, 0))
hub = b3d.prim('cylinder', [dark], vertices=24, radius=.07, depth=.14, location=(0, 0, 0)); hub.parent = gov; hub.location = (0, 0, 0); hub.rotation_euler = (0, 0, 0)
flies = []
for k in (0, 1):
    fl = box(fly_m, (0, 0, 0), (.09, .045, .03), .01); fl.parent = gov
    sgn = 1 if k == 0 else -1
    keys(fl, 'location', [(0, (sgn * .05, 0, .07)), (SNAP + 14, (sgn * .05, 0, .07)), (s4 + 22, (sgn * .12, 0, .07))])
    flies.append(fl)
pawl = box(dark, (GX + GR + .07, GY, GZ + .14), (.06, .08, .14), .01)
b3d.key_input(fly_m, 'Emission Strength', [(0, .5), (s4 + 16, .5), (s4 + 22, 5)])
b3d.key_input(gov_m, 'Emission Strength', [(0, .4), (s4 + 22, .4), (s4 + 24, 3)])
b3d.key_input(gov_m, 'Emission Color', [(0, (.2, .45, 1)), (s4 + 22, (.2, .45, 1)), (s4 + 24, (1, .1, .05))])
LOCK = s4 + 24
def grot(f):  # governor angle follows the cabin travel until it locks
    ff = min(f, LOCK)
    return (zc(ff) - Z0) / GR * 1.0
gfv = [(f, (R(90), grot(f), 0)) for f in fs]
keys(gov, 'rotation_euler', gfv); linear(gov)
for ob, fz in ((sheave, None),):
    keys(ob, 'rotation_euler', [(f, (R(90), (zc(min(f, SNAP)) - Z0) / SR, 0)) for f in fs if f <= SNAP + 2] + [(N - 1, (R(90), (ZM - Z0) / SR, 0))]); linear(ob)
# governor rope loop (two vertical runs) + pit tension pulley
tp = b3d.prim('cylinder', [gov_m], vertices=32, radius=GR, depth=.08, location=(GX, GY, .5), rotation=(R(90), 0, 0))
tw = box(dark, (GX, GY, .2), (.12, .12, .3))
for xx in (GX - GR, GX + GR):
    gr = b3d.prim('cylinder', [grope_m], vertices=8, radius=.016, depth=GZ - .5, location=(xx, GY, (GZ + .5) / 2))
b3d.key_input(grope_m, 'Emission Strength', [(0, .3), (s3 + 4, .3), (s3 + 10, 2.5), (e4, 2.5), (e4 + 2, .3)])

# ---------- pit buffers ----------
springs = []
for x in (-.4, .4):
    base = b3d.prim('cylinder', [dark], vertices=24, radius=.18, depth=.1, location=(x, Y0, .05))
    for k in range(7):
        t = b3d.prim('torus', [spring_m], major_radius=.13, minor_radius=.025, major_segments=24, minor_segments=8, location=(x, Y0, .14 + k * .085))
    cap = b3d.prim('cylinder', [dark], vertices=24, radius=.17, depth=.06, location=(x, Y0, .14 + 7 * .085))
b3d.key_input(spring_m, 'Emission Strength', [(0, 0), (s6 + 4, 0), (s6 + 12, 2.5), (e6, 2.5), (e6 + 2, .4)])

# ---------- lights ----------
b3d.light('AREA', 'Key', (4, -7, 8), 1400, (1, .95, .88), 8, rot=(55, 0, 30))
b3d.light('AREA', 'Fill', (-4, -6, 4), 600, (.62, .74, 1), 7, rot=(70, 0, -40))
b3d.light('POINT', 'Machine', (0, -.9, TOP + 1.7), 140, (1, .95, .85), .4)
b3d.light('POINT', 'Pit', (0, -1.2, 1.4), 90, (1, .9, .8), .4)
alarm = b3d.light('POINT', 'Alarm', (0, -1.0, ZM + 1.0), 0, (1, .2, .1), .3)
keys(alarm.data, 'energy', [(0, 0), (SNAP, 0), (SNAP + 1, 150), (STOP, 150), (STOP + 12, 0)])

# ---------- timeline ----------
zcl = ZEND
cam, tgt = b3d.camera(30)
b3d.shot(cam, tgt, s1, e1, (1.5, -10.0, 5.8), (1.2, -9.3, 6.0), (0, Y0, 5.4))
b3d.shot(cam, tgt, s2, e2, (1.4, -2.6, SHZ - .6), (1.0, -2.3, SHZ - .9), (0, Y0, SHZ - 1.2))
b3d.shot(cam, tgt, s3, e3, (2.6, -5.0, ZM + 2.0), (2.3, -5.4, ZM + 1.2), (-.4, Y0, ZM + 1.6), (-.4, Y0, ZM + .5))
b3d.shot(cam, tgt, s4, e4, (GX + .5, -1.4, GZ - .1), (GX + .35, -1.2, GZ - .05), (GX, GY, GZ))
b3d.shot(cam, tgt, s5, e5, (1.0, -1.9, zcl - .75), (.95, -1.6, zcl - .55), (.75, Y0, zcl + .05))
b3d.shot(cam, tgt, s6, e6, (1.3, -2.6, 1.4), (1.0, -2.3, 1.2), (0, Y0, .5))
b3d.shot(cam, tgt, s7, e7, (1.4, -8.6, 5.4), (1.8, -10.8, 5.6), (0, Y0, 5.0))
b3d.render(OUT, cfg.get('frames'))
