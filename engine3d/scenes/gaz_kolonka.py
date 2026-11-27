"""Gaz kolonka: wall-mounted water heater. Front on (glow window) -> cutaway: cold water beads push the membrane, rod opens
the gas valve, spark lights the burner row, copper coil over the flames turns water beads hot -> low pressure: water slows,
membrane returns, flames die -> dead batteries glow red -> blocked flue: smoke piles up, draft sensor red, flames off ->
pull back with flames on. 7 shots."""
import math, os, sys, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy
from mathutils import Vector

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.02, .025, .05), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))
def at(s, e, k): return s + int((e - s) * k)

case_m = b3d.mat('Case', (.86, .86, .88), .35)
wall_m = b3d.mat('Wall', (.42, .45, .5), .85, bump=.02)
pipe_m = b3d.mat('Pipe', (.6, .6, .63), .3, metal=.8)
cu_m = b3d.mat('Copper', (.85, .42, .2), .3, metal=.85)
fin_m = b3d.mat('Fin', (.55, .4, .3), .4, metal=.6)
brass_m = b3d.mat('Brass', (.8, .6, .25), .3, metal=.8)
rub_m = b3d.mat('Rubber', (.05, .05, .06), .7)
valve_m = b3d.mat('Valve', (.3, .32, .36), .35, metal=.6)
burn_m = b3d.mat('Burner', (.25, .25, .27), .4, metal=.6)
bat_m = b3d.mat('Battery', (.1, .35, .15), .4, emit=(1, .05, .02), estr=0)
sens_m = b3d.mat('Sensor', (.3, .3, .3), .4, emit=(1, .05, .02), estr=0)
glass_m = b3d.mat('Glass', (.9, .92, .95), .2)
gb = b3d.bsdf(glass_m); gb.inputs['Alpha'].default_value = .3
smoke_m = b3d.mat('Smoke', (.25, .25, .27), .9)
sb = b3d.bsdf(smoke_m); sb.inputs['Alpha'].default_value = .6
for m in (glass_m, smoke_m):
    try: m.surface_render_method = 'BLENDED'
    except Exception: pass
cold_m = b3d.mat('Cold', (.3, .6, 1), .3, emit=(.25, .55, 1), estr=4)
hot_m = b3d.mat('Hot', (1, .4, .1), .3, emit=(1, .35, .05), estr=4)
gas_m = b3d.mat('Gas', (1, .85, .2), .3, emit=(1, .8, .15), estr=4)
fl_m = b3d.mat('Flame', (0, 0, 0), .5, emit=(.05, .25, 1), estr=2.4)
fi_m = b3d.mat('FlameIn', (0, 0, 0), .5, emit=(.35, .65, 1), estr=3)
win_m = b3d.mat('Window', (0, 0, 0), .5, emit=(.2, .45, 1), estr=3)
spark_m = b3d.mat('Spark', (1, 1, 1), .2, emit=(.8, .9, 1), estr=6)

def box(name, m, loc, dims, bev=0):
    ob = b3d.prim('cube', [m], size=1, location=loc); ob.scale = dims; ob.name = name
    if bev: ob.modifiers.new('bev', 'BEVEL').width = bev
    return ob

def tube(name, pts, r, m):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 4
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for p, c in zip(sp.points, pts): p.co = (*c, 1)
    ob = b3d.link(bpy.data.objects.new(name, cu)); ob.data.materials.append(m); return ob

def keys(ob, attr, fv):
    for f, v in fv: setattr(ob, attr, v); ob.keyframe_insert(attr, frame=f)

# ---------- timeline ----------
G1 = at(s2, e2, .5)            # membrane pushed -> gas valve opens
I1 = at(s3, e3, .2)            # spark lights the burner
OFF1 = at(s4, e4, .5)          # low pressure: valve closes
OFF2 = at(s6, e6, .55)         # blocked flue: draft sensor cuts gas
ON = [(0, e1), (I1, OFF1), (s6, OFF2), (s7, N + 2)]
GAS = [(G1, OFF1), (s6, OFF2), (s7, N + 2)]
def lvl(iv, f, ramp=6):
    v = 0.
    for a, b in iv:
        if a <= f < b: v = max(v, min(1, (f - a + 1) / ramp if a > 0 else 1, (b - f) / ramp if b < N else 1))
    return v

# ---------- wall + casing ----------
b3d.prim('plane', [wall_m], size=14, location=(0, .34, 1.5), rotation=(math.radians(90), 0, 0))
box('Back', case_m, (0, .3, .9), (1.4, .03, 1.8))
for sx in (-1, 1): box(f'Side{sx}', case_m, (.7 * sx, 0, .9), (.03, .62, 1.8), .005)
box('Bottom', case_m, (0, 0, .0), (1.43, .62, .04), .005)
box('Top', case_m, (0, 0, 1.8), (1.43, .62, .04), .005)
front = box('Front', case_m, (0, -.31, .9), (1.43, .03, 1.82), .01)
win = b3d.prim('plane', [win_m], size=1, location=(0, -.33, .58), rotation=(math.radians(90), 0, 0)); win.scale = (.34, .12, 1)
knobs = []
for k, x in enumerate((-.35, .35)):
    kn = b3d.prim('cylinder', [rub_m], vertices=32, radius=.08, depth=.06, location=(x, -.35, .3), rotation=(math.radians(90), 0, 0)); knobs.append(kn)
for o in [front, win] + knobs: b3d.visible(o, [(0, s2)])
b3d.key_input(win_m, 'Emission Strength', [(f, 3 * lvl(ON, f)) for f in range(0, N + 1, 3)])

# ---------- water: cold in -> membrane block -> copper coil -> hot out ----------
cold_pts = [(.3, 0, -.5), (.3, 0, .45), (.6, 0, .45), (.6, 0, 1.05), (.6, -.15, 1.05), (.5, -.15, 1.05)]
coil_pts = [(.5, -.15, 1.05), (-.5, -.15, 1.05), (-.5, -.15, 1.17), (.5, -.15, 1.17), (.5, -.15, 1.29), (-.55, -.15, 1.29),
            (-.62, -.15, 1.29), (-.62, 0, 1.29), (-.62, 0, -.5)]
tube('ColdPipe', cold_pts, .035, pipe_m); tube('Coil', coil_pts[:6], .035, cu_m); tube('HotPipe', coil_pts[5:], .035, pipe_m)
for k in range(17):  # fins of the heat exchanger
    box(f'Fin{k}', fin_m, (-.48 + k * .06, 0, 1.17), (.008, .4, .34))
house = b3d.prim('cylinder', [glass_m], vertices=40, radius=.15, depth=.16, location=(.3, 0, .25), rotation=(0, math.radians(90), 0))
mem = b3d.prim('cylinder', [rub_m], vertices=40, radius=.13, depth=.015, location=(.3, 0, .25), rotation=(0, math.radians(90), 0))
rod = b3d.prim('cylinder', [brass_m], vertices=16, radius=.015, depth=.3, location=(.13, 0, .25), rotation=(0, math.radians(90), 0))
PUSH = -.05
mk = [(0, 0), (at(s2, e2, .25), 0), (at(s2, e2, .45), PUSH), (at(s4, e4, .25), PUSH), (OFF1, 0), (s5 - 1, 0), (s5, PUSH)]
for ob, x0 in ((mem, .3), (rod, .13)):
    for f, d in mk: ob.location.x = x0 + d; ob.keyframe_insert('location', frame=f)

# ---------- gas: inlet -> valve -> manifold -> burner row ----------
box('Valve', valve_m, (-.15, 0, .25), (.24, .2, .22), .02)
tube('GasIn', [(-.15, 0, -.5), (-.15, 0, .14)], .03, brass_m)
tube('GasUp', [(-.15, 0, .36), (-.15, 0, .5), (-.15, 0, .52)], .03, brass_m)
box('Manifold', brass_m, (0, 0, .52), (1.05, .08, .06), .01)
NOZ = [-.48 + k * .12 for k in range(9)]
for k, x in enumerate(NOZ): box(f'Nozzle{k}', burn_m, (x, 0, .6), (.07, .24, .1), .01)
rnd = random.Random(4); flames = []
for x in NOZ:
    for y in (-.07, 0, .07):
        e = b3d.empty('F', (x, y, .65))
        o = b3d.prim('cone', [fl_m], vertices=14, radius1=.03, depth=.16, location=(0, 0, 0)); o.parent = e; o.location = (0, 0, .08); b3d.smooth(o)
        i = b3d.prim('cone', [fi_m], vertices=10, radius1=.016, depth=.07, location=(0, 0, 0)); i.parent = e; i.location = (0, 0, .035)
        o.visible_shadow = i.visible_shadow = False; flames.append(e)
for e in flames:
    for f in range(0, N + 3, 2):
        v = max(.001, lvl(ON, f)); h = v * (.85 + .3 * rnd.random())
        e.scale = (v, v, h); e.keyframe_insert('scale', frame=f)
FL = b3d.light('POINT', 'FlameGlow', (0, -.2, .8), 0, (.4, .6, 1), .4)
for f in range(0, N + 3, 3): FL.data.energy = 90 * lvl(ON, f) * (.85 + .3 * rnd.random()); FL.data.keyframe_insert('energy', frame=f)
# spark electrode
box('Electrode', valve_m, (.56, -.13, .66), (.02, .02, .12))
spark = b3d.prim('uv_sphere', [spark_m], radius=.035, segments=12, ring_count=8, location=(.53, -.13, .71)); spark.visible_shadow = False
b3d.visible(spark, [(f, f + 2) for f in range(I1 - 16, I1, 4)])

# ---------- beads ----------
def mkpath(pts):
    path = [Vector(p) for p in pts]; seg = [(path[k + 1] - path[k]).length for k in range(len(path) - 1)]; tot = sum(seg)
    def pos(d):
        d %= tot
        for k, s in enumerate(seg):
            if d <= s: return path[k].lerp(path[k + 1], d / s)
            d -= s
        return path[-1]
    return pos, tot
def speed(f):  # water speed: starts in shot 2, slows on low pressure in shot 4
    if f < at(s2, e2, .2): return 0
    if s4 <= f < s5: return 1 - .75 * min(1, max(0, (f - at(s4, e4, .1)) / 25))
    return 1
def beads(pts, m, nb, sp, vis, rad=.028):
    pos, tot = mkpath(pts)
    for k in range(nb):
        bd = b3d.prim('uv_sphere', [m], radius=rad, segments=10, ring_count=6, location=(0, 0, 0)); bd.visible_shadow = False
        dist = k * tot / nb
        for f in range(s2, N + 2, 2):
            dist += .045 * sp(f); bd.location = pos(dist); bd.keyframe_insert('location', frame=f)
        b3d.visible(bd, vis)
beads(cold_pts, cold_m, 22, speed, [(s2, s5), (s6, N + 1)])
beads(coil_pts, hot_m, 46, speed, [(s2, s5), (s6, N + 1)])
b3d.key_input(hot_m, 'Emission Color', [(f, (1, .35, .05) if lvl(ON, f) > .5 else (.25, .55, 1)) for f in range(s2, N + 1, 4)])
b3d.key_input(hot_m, 'Base Color', [(f, (1, .4, .1) if lvl(ON, f) > .5 else (.3, .6, 1)) for f in range(s2, N + 1, 4)])
gp = [(-.15, 0, -.5), (-.15, 0, .52), (-.5, 0, .52), (.5, 0, .52)]
pos, tot = mkpath([(-.15, 0, -.5), (-.15, 0, .52)])
for k in range(10):
    bd = b3d.prim('uv_sphere', [gas_m], radius=.025, segments=10, ring_count=6, location=(0, 0, 0)); bd.visible_shadow = False
    d = k * tot / 10
    for f in range(s2, N + 2, 2): d += .04; bd.location = pos(d); bd.keyframe_insert('location', frame=f)
    b3d.visible(bd, GAS)

# ---------- batteries (shot 5) ----------
box('BatBox', valve_m, (0, -.05, -.12), (.5, .22, .18), .01)
for x in (-.11, .11):
    b3d.prim('cylinder', [bat_m], vertices=24, radius=.07, depth=.2, location=(x, -.2, -.12), rotation=(0, math.radians(90), 0))
b3d.key_input(bat_m, 'Emission Strength', [(0, 0), (s5, 0), (s5 + 8, 3)] + [(f, 1 + 2 * (k % 2)) for k, f in enumerate(range(s5 + 16, e5, 8))] + [(e5, 0)])

# ---------- draft hood, flue, sensor, smoke (shot 6) ----------
hood = b3d.lathe('Hood', [(.6, 1.42), (.6, 1.47), (.17, 1.7), (.17, 1.8)]); hood.data.materials.append(valve_m); hood.scale = (1, .45, 1)
b3d.prim('cylinder', [pipe_m], vertices=40, radius=.17, depth=1.3, location=(0, 0, 2.45))
sens = b3d.prim('cylinder', [sens_m], vertices=24, radius=.05, depth=.03, location=(.38, -.33, 1.6), rotation=(math.radians(90), 0, 0))
b3d.visible(sens, [(s6, N + 1)])
b3d.key_input(sens_m, 'Emission Strength', [(0, 0), (OFF2 - 12, 0), (OFF2 - 4, 5), (e6, 5), (s7, 0)])
rs = random.Random(8)
for k in range(14):
    p = b3d.smooth(b3d.prim('uv_sphere', [smoke_m], radius=.06, segments=12, ring_count=8, location=(0, 0, 0))); p.visible_shadow = False
    t0 = s6 + rs.randint(0, max(1, OFF2 - s6 - 10))
    if k < 8:   # rises and piles up under the blockage
        keys(p, 'location', [(t0, (rs.uniform(-.2, .2), 0, 1.0)), (t0 + 30, (rs.uniform(-.1, .1), 0, 1.55))])
    else:        # spills out under the hood rim towards the room
        x = rs.uniform(-.5, .5)
        keys(p, 'location', [(t0, (x, -.1, 1.1)), (t0 + 35, (x * 1.1, -.55, 1.35))])
    keys(p, 'scale', [(t0, (.4, .4, .4)), (t0 + 30, (1.6, 1.6, 1.6))])
    b3d.visible(p, [(t0, e6)])

b3d.light('AREA', 'Key', (-1.6, -2.6, 2.6), 170, (1, .9, .8), 3, rot=(55, 0, -25))
b3d.light('AREA', 'Fill', (2.0, -2.2, 1.2), 70, (.6, .7, 1), 3, rot=(70, 0, 45))
b3d.light('POINT', 'Inside', (0, -.25, .2), 25, (1, .95, .9), .4)

# ---------- camera ----------
cam, tgt = b3d.camera(35)
b3d.shot(cam, tgt, s1, e1, (0, -3.6, 1.2), (0, -3.1, 1.1), (0, 0, .95))
b3d.shot(cam, tgt, s2, e2, (.3, -1.7, .45), (.2, -1.55, .42), (.12, 0, .3), (.05, 0, .3))
b3d.shot(cam, tgt, s3, e3, (-.35, -1.85, .95), (0, -1.65, .95), (0, 0, .85))
b3d.shot(cam, tgt, s4, e4, (.45, -2.1, .75), (.3, -1.9, .7), (.05, 0, .5))
b3d.shot(cam, tgt, s5, e5, (-.55, -1.6, .15), (-.4, -1.45, .1), (0, -.1, -.05))
b3d.shot(cam, tgt, s6, e6, (.7, -2.3, 2.0), (.5, -2.1, 1.85), (0, 0, 1.45))
b3d.shot(cam, tgt, s7, e7, (0, -2.5, 1.1), (0, -4.4, 1.4), (0, 0, .9))

b3d.render(OUT, cfg.get('frames'))
