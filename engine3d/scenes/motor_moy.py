"""Mashina moyi: cross-section of one engine cylinder (piston, rod, crank, oil sump). Golden oil film between piston and
cylinder walls; oil darkens with soot, film thins, sparks at the gap; fresh oil drips down, film restored; pull back. 7 shots."""
import math, os, sys, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy
from mathutils import Vector

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.02, .025, .05), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))

block_m = b3d.mat('Block', (.42, .44, .48), .45, metal=.6)
back_m = b3d.mat('Back', (.16, .17, .2), .7)
piston_m = b3d.mat('Piston', (.78, .78, .8), .25, metal=.85)
rod_m = b3d.mat('Rod', (.55, .56, .6), .3, metal=.8)
crank_m = b3d.mat('Crank', (.35, .36, .4), .35, metal=.8)
ring_m = b3d.mat('Ring', (.2, .2, .22), .3, metal=.9)
GOLD, DARK = (.95, .62, .08), (.07, .045, .02)
oil_m = b3d.mat('Oil', GOLD, .15, emit=(1, .6, .1), estr=.6)
soot_m = b3d.mat('Soot', (.01, .01, .01), .9)
spark_m = b3d.mat('Spark', (1, .5, .1), .3, emit=(1, .45, .05), estr=6)
drop_m = b3d.mat('Drop', GOLD, .1, emit=(1, .65, .1), estr=1.5)

def keys(ob, attr, fv):
    for f, v in fv: setattr(ob, attr, v); ob.keyframe_insert(attr, frame=f)

def box(name, m, loc, dims, bev=0):
    ob = b3d.prim('cube', [m], size=1, location=loc); ob.scale = dims; ob.name = name
    if bev: ob.modifiers.new('bev', 'BEVEL').width = bev
    return ob

# ---------- static block (cutaway: back plate + side walls) ----------
box('BackPlate', back_m, (0, .45, 1.4), (3.0, .1, 4.6))
for sx in (-1, 1):
    box(f'Wall{sx}', block_m, (sx * .62, 0, 2.2), (.24, .7, 2.0), .02)       # cylinder walls z 1.2..3.2
    box(f'Case{sx}', block_m, (sx * .95, 0, .35), (.2, .7, 1.7), .02)        # crankcase z -0.5..1.2
    box(f'Shoulder{sx}', block_m, (sx * .78, 0, 1.2), (.55, .7, .14), .02)
box('Head', block_m, (0, 0, 3.35), (1.5, .7, .3), .03)
box('Pan', block_m, (0, 0, -.56), (2.1, .7, .12), .02)
plug = b3d.smooth(b3d.prim('cylinder', [ring_m], vertices=24, radius=.07, depth=.35, location=(0, -.05, 3.6)))
pool = box('Pool', oil_m, (0, 0, -.37), (1.68, .64, .26))

# oil film strips between piston (x +-0.45) and walls (x +-0.5)
films = [box(f'Film{sx}', oil_m, (sx * .475, 0, 2.2), (.05, .5, 2.0)) for sx in (-1, 1)]
F5 = s5 + int((e5 - s5) * .7)
for fl in films:
    keys(fl, 'scale', [(0, (.05, .5, 2.0)), (s5, (.05, .5, 2.0)), (F5, (.012, .5, 2.0)), (s6, (.012, .5, 2.0)),
                       (s6 + int((e6 - s6) * .7), (.05, .5, 2.0))])
# oil ageing: gold -> dark (shot 4), stays dark (5), fresh again (6)
F4 = s4 + int((e4 - s4) * .75); F6 = s6 + int((e6 - s6) * .6)
b3d.key_input(oil_m, 'Base Color', [(0, GOLD), (s4, GOLD), (F4, DARK), (s6, DARK), (F6, GOLD)])
b3d.key_input(oil_m, 'Emission Strength', [(0, .6), (s4, .6), (F4, 0), (s6, 0), (F6, .6)])

# ---------- moving parts ----------
ZC, R, L = .3, .35, 1.4
crank = (b3d.prim('cylinder', [crank_m], vertices=12, radius=.5, depth=.3, location=(0, -.05, ZC), rotation=(math.radians(90), 0, 0)))
pin = b3d.smooth(b3d.prim('cylinder', [rod_m], vertices=24, radius=.09, depth=.36, location=(0, 0, 0), rotation=(math.radians(90), 0, 0)))
piston = box('Piston', piston_m, (0, 0, 1.8), (.9, .5, .6), .03)
rings = []
for k, dz in enumerate((.2, .1)):
    rg = box(f'Ring{k}', ring_m, (0, 0, 0), (1.0 / .9, 1.02, .035 / .6)); rg.parent = piston; rg.location = (0, 0, dz / .6)
rod_piv = b3d.empty('RodPiv'); rod = box('Rod', rod_m, (0, 0, 0), (.14, .2, L), .02); rod.parent = rod_piv; rod.location = (0, -.02, L / 2)
crank.rotation_mode = 'XYZ'
REV = 18  # frames per crank revolution
for f in range(0, N + 1, 1):
    th = 2 * math.pi * f / REV
    cp = Vector((R * math.sin(th), -.12, ZC + R * math.cos(th)))
    pz = ZC + R * math.cos(th) + math.sqrt(L * L - (R * math.sin(th)) ** 2)
    pin.location = cp; pin.keyframe_insert('location', frame=f)
    piston.location = (0, 0, pz + .12); piston.keyframe_insert('location', frame=f)
    d = Vector((0, 0, pz)) - Vector((cp.x, 0, cp.z))
    rod_piv.location = cp; rod_piv.keyframe_insert('location', frame=f)
    rod_piv.rotation_euler = (0, math.atan2(d.x, d.z), 0); rod_piv.keyframe_insert('rotation_euler', frame=f)
    crank.rotation_euler = (math.radians(90), th, 0); crank.keyframe_insert('rotation_euler', frame=f)
for ob in (pin, piston, rod_piv, crank):
    if ob.animation_data and ob.animation_data.action:
        try:
            for fc in ob.animation_data.action.fcurves:
                for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
        except AttributeError: pass

# ---------- soot (shot 4-5): black specks drifting in the oil pool and along the film ----------
rnd = random.Random(7)
for k in range(40):
    if k < 26: p0 = Vector((rnd.uniform(-.8, .8), rnd.uniform(-.33, -.3), rnd.uniform(-.48, -.26)))
    else: p0 = Vector((rnd.choice((-1, 1)) * .475, -.26, rnd.uniform(1.3, 3.1)))
    sp = b3d.prim('uv_sphere', [soot_m], radius=rnd.uniform(.015, .03), segments=10, ring_count=6, location=p0)
    t0 = s4 + rnd.randint(0, max(1, int((e4 - s4) * .6)))
    keys(sp, 'location', [(t0, p0), (e5, p0 + Vector((rnd.uniform(-.08, .08), 0, rnd.uniform(-.05, .05))))])
    keys(sp, 'scale', [(t0, (.1, .1, .1)), (t0 + 15, (1, 1, 1)), (s6, (1, 1, 1)), (s6 + 20, (.01, .01, .01))])
    b3d.visible(sp, [(t0, s6 + 21)])

# ---------- sparks at the piston-wall gap (shot 5) ----------
SPK = s5 + int((e5 - s5) * .45)
for k in range(10):
    sx = -1 if k % 2 == 0 else 1
    s_ = b3d.prim('uv_sphere', [spark_m], radius=.025, segments=10, ring_count=6, location=(0, 0, 0))
    s_.parent = piston; s_.location = (sx * .5 / .9, -.52 / .5 * .5, rnd.uniform(-.45, .45))
    b3d.flicker(s_, 'scale', SPK, e5, .2, 1.6, every=2, seed=k)
    b3d.visible(s_, [(SPK, e5)])
HL = b3d.light('POINT', 'SparkLight', (-.47, -.6, 2.0), 0, (1, .45, .1), .05)
for f, v in [(0, 0), (SPK - 1, 0), (SPK, 25), (e5 - 1, 25), (e5, 0)]:
    HL.data.energy = v; HL.data.keyframe_insert('energy', frame=f)

# ---------- fresh oil drops sliding down the films (shot 6) ----------
for k in range(14):
    sx = -1 if k % 2 == 0 else 1
    d = b3d.smooth(b3d.prim('uv_sphere', [drop_m], radius=.035, segments=16, ring_count=10, location=(0, 0, 0)))
    d.scale = (.8, .8, 1.3)
    t0 = s6 + (k // 2) * 5
    keys(d, 'location', [(t0, (sx * .475, -.27, 3.15)), (t0 + 40, (sx * .475, -.27, 1.25))])
    b3d.visible(d, [(t0, min(t0 + 40, e6))])

b3d.light('AREA', 'Key', (-2.2, -3.5, 3.8), 260, (1, .88, .75), 3, rot=(55, 0, -30))
b3d.light('AREA', 'Fill', (2.5, -3.0, 1.0), 120, (.6, .7, 1), 3, rot=(70, 0, 40))
b3d.light('POINT', 'Front', (0, -1.4, 1.6), 60, (1, .9, .8), .5)

# ---------- camera ----------
cam, tgt = b3d.camera(35)
b3d.shot(cam, tgt, s1, e1, (1.2, -6.6, 1.9), (.7, -6.0, 1.7), (0, 0, 1.4), lens=35)
b3d.shot(cam, tgt, s2, e2, (.5, -3.8, 2.3), (.3, -3.4, 2.2), (0, 0, 1.9), lens=35)
b3d.shot(cam, tgt, s3, e3, (.3, -2.0, 2.15), (.36, -1.8, 2.1), (.47, -.25, 2.0), lens=55)
b3d.shot(cam, tgt, s4, e4, (.3, -3.4, 1.0), (.2, -3.1, .95), (0, 0, .7), lens=35)
b3d.shot(cam, tgt, s5, e5, (-.3, -2.0, 2.15), (-.36, -1.8, 2.1), (-.47, -.25, 2.0), lens=55)
b3d.shot(cam, tgt, s6, e6, (.4, -3.7, 2.0), (.25, -3.3, 1.9), (0, 0, 1.8), lens=35)
b3d.shot(cam, tgt, s7, e7, (0, -4.2, 1.7), (0, -7.8, 1.9), (0, 0, 1.4), lens=35)

b3d.render(OUT, cfg.get('frames'))
