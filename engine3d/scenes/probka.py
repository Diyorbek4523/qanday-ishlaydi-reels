"""Avtomat probka: three breakers on a DIN rail; the middle one trips (lever snaps down, wires go dark). Its front cover
comes off: current (yellow beads) runs IN -> coil -> fixed contact -> moving arm -> braid -> bimetal strip -> OUT.
Overload: the bimetal glows and bends, nudges the latch, the spring-loaded arm drops - spark. Short circuit: fast red
current, the coil glows with field lines, the plunger shoots down and knocks the arm open. 7 shots."""
import math, os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.03, .04, .09), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))

# ---------- materials ----------
panel_m = b3d.mat('Panel', (.3, .32, .36), .5, metal=.5)
rail_m = b3d.mat('Rail', (.7, .72, .76), .3, metal=.9)
shell_m = b3d.mat('Shell', (.86, .87, .88), .45)
back_m = b3d.mat('Back', (.55, .57, .6), .6)
lever_m = b3d.mat('Lever', (.12, .12, .14), .4)
txt_m = b3d.mat('Txt', (.05, .05, .06), .5)
metal = b3d.mat('Metal', (.7, .72, .76), .25, metal=.9)
silver = b3d.mat('Silver', (.9, .9, .92), .15, metal=1.0)
copper = b3d.mat('Copper', (.95, .45, .2), .25, metal=.6, emit=(1, .4, .1), estr=0)
wire_m = b3d.mat('Wire', (.95, .45, .2), .3, metal=.5, emit=(1, .55, .15), estr=0)
bim_a = b3d.mat('BimA', (.95, .5, .25), .3, metal=.7, emit=(1, .3, .05), estr=0)
bim_b = b3d.mat('BimB', (.6, .62, .66), .3, metal=.8, emit=(1, .3, .05), estr=0)
plunger_m = b3d.mat('Plunger', (.4, .42, .48), .3, metal=.9)
latch_m = b3d.mat('Latch', (.2, .5, .9), .4)
spring_m = b3d.mat('Spring', (.75, .77, .8), .25, metal=.9)
cur_m = b3d.mat('Current', (1, .85, .2), .3, emit=(1, .8, .15), estr=4)
fast_m = b3d.mat('Fast', (1, .15, .08), .3, emit=(1, .1, .04), estr=1.8)
field_m = b3d.mat('Field', (.3, .6, 1), .4, emit=(.25, .55, 1), estr=2.5)
spark_m = b3d.mat('Spark', (.7, .85, 1), .3, emit=(.7, .85, 1), estr=8)

def box(m, c, s, bevel=0):
    b = b3d.prim('cube', [m], size=1, location=c); b.scale = s
    if bevel:
        bv = b.modifiers.new('Bv', 'BEVEL'); bv.width = bevel; bv.segments = 4; b3d.smooth(b)
    return b
def curve(name, pts, m, r=.03, cyclic=False):
    cv = bpy.data.curves.new(name, 'CURVE'); cv.dimensions = '3D'; cv.bevel_depth = r; cv.bevel_resolution = 3; cv.use_fill_caps = True
    sp = cv.splines.new('POLY'); sp.points.add(len(pts) - 1); sp.use_cyclic_u = cyclic
    for bp, p in zip(sp.points, pts): bp.co = (*p, 1)
    cv.materials.append(m); return b3d.link(bpy.data.objects.new(name, cv))
def lerp(a, b, u): return tuple(x + (y - x) * u for x, y in zip(a, b))
def ball(m, r, loc=(0, 0, 0)): return b3d.smooth(b3d.prim('uv_sphere', [m], segments=12, ring_count=6, radius=r, location=loc))
def keys(ob, attr, fv):
    for f, v in fv: setattr(ob, attr, v); ob.keyframe_insert(attr, frame=f)
R = math.radians

T0 = s1 + int((e1 - s1) * .6)      # hook trip
T1 = s4 + int((e4 - s4) * .35)     # overload trip
T2 = s6 + int((e6 - s6) * .22)     # short-circuit trip
ON = [(0, T0), (s2, T1), (s5, T2)]

# ---------- panel ----------
box(panel_m, (0, .5, 1.6), (9, .1, 7))
box(rail_m, (0, .42, 1.6), (9, .08, .35))
def breaker(x, lever_keys, front_ranges=None, main=False):
    box(back_m, (x, .3, 1.6), (2.0, .1, 3.6))
    for sx in (-1, 1): box(shell_m, (x + sx * .98, 0, 1.6), (.06, .66, 3.6))
    box(shell_m, (x, 0, -.17), (2.0, .66, .06))
    top = box(shell_m, (x, -.35, 3.17), (2.0, .1, .5), bevel=.02)
    box(shell_m, (x, 0, 3.4), (2.0, .66, .06))
    low = box(shell_m, (x, -.35, 1.37), (2.0, .1, 3.1), bevel=.02)
    bpy.ops.object.text_add(location=(x, -.41, .75)); t = bpy.context.object; t.data.body = 'C16'; t.data.size = .32
    t.data.align_x = 'CENTER'; t.data.extrude = .01; t.data.materials.append(txt_m); t.rotation_euler = (R(90), 0, 0)
    if front_ranges: b3d.visible(low, front_ranges); b3d.visible(t, front_ranges)
    pv = b3d.empty(f'LeverPv{x}', (x, -.42, 3.17))
    h = box(lever_m, (0, 0, 0), (.32, .5, .14), bevel=.04); h.parent = pv; h.location = (0, -.22, 0)
    keys(pv, 'rotation_euler', [(f, (R(a), 0, 0)) for f, a in lever_keys])
    for wx in (-.5, .55):  # incoming wires
        curve(f'Wire{x}{wx}', [(x + wx, 0, 3.1), (x + wx, 0, 3.8), (x + wx * 1.3, .1, 6.5)], wire_m if main else copper, r=.07)
UP, DN = -35, 35
breaker(0, [(0, UP), (T0, UP), (T0 + 3, DN), (s2 - 1, DN), (s2, UP), (T1, UP), (T1 + 3, DN), (s5 - 1, DN), (s5, UP), (T2, UP), (T2 + 3, DN), (N, DN)],
        front_ranges=[(s1, s2), (s7, N)], main=True)
breaker(-2.15, [(0, UP)]); breaker(2.15, [(0, UP)])
b3d.key_input(wire_m, 'Emission Strength', [(0, 1.2), (T0, 1.2), (T0 + 2, 0.), (s2 - 1, 0.), (s2, 1.2), (T1, 1.2), (T1 + 2, 0.), (s5 - 1, 0.), (s5, 2.5), (T2, 2.5), (T2 + 2, 0.), (N, 0.)])

# ---------- internals of the middle breaker ----------
box(metal, (-.5, 0, 3.0), (.4, .4, .3), bevel=.02); box(metal, (.55, 0, 3.0), (.4, .4, .3), bevel=.02)
cpts = []
for i in range(8 * 32 + 1):
    t = i / 32; a = 2 * math.pi * t; cpts.append((-.5 + .24 * math.cos(a), .24 * math.sin(a), 2.75 - t * .13))
coil = curve('Coil', cpts, copper, r=.035)
plunger = b3d.smooth(b3d.prim('cylinder', [plunger_m], vertices=24, radius=.11, depth=.95, location=(-.5, 0, 2.2)))
keys(plunger, 'location', [(0, (-.5, 0, 2.2)), (T2, (-.5, 0, 2.2)), (T2 + 3, (-.5, 0, 1.55)), (N, (-.5, 0, 1.55))])
curve('W1', [(-.5, 0, 2.86), (-.5, 0, 2.76)], copper, r=.035)
curve('W2', [(-.5, .2, 1.7), (-.8, .2, 1.7), (-.8, .2, 1.14)], copper, r=.035)
box(silver, (-.8, 0, 1.08), (.18, .22, .1))
arm_pv = b3d.empty('ArmPv', (.35, 0, .95))
arm = box(metal, (0, 0, 0), (1.15, .14, .08), bevel=.02); arm.parent = arm_pv; arm.location = (-.575, 0, 0)
pad = box(silver, (0, 0, 0), (.16, .2, .05)); pad.parent = arm_pv; pad.location = (-1.15, 0, .06)
keys(arm_pv, 'rotation_euler', [(f, (0, R(a), 0)) for f, a in ((0, 0), (T1, 0), (T1 + 3, -20), (s5 - 1, -20), (s5, 0), (T2 + 2, 0), (T2 + 5, -20), (N, -20))])
b3d.smooth(b3d.prim('cylinder', [metal], vertices=16, radius=.06, depth=.3, location=(.35, 0, .95), rotation=(R(90), 0, 0)))
spts = [(.05 + .07 * math.cos(2 * math.pi * i / 16), .07 * math.sin(2 * math.pi * i / 16), .25 + .5 * i / (16 * 7)) for i in range(16 * 7 + 1)]
curve('Spring', spts, spring_m, r=.015)
bim = b3d.empty('BimPv', (.62, 0, 2.62))
for dx, m in ((-.045, bim_a), (.045, bim_b)):
    b = box(m, (0, 0, 0), (.09, .2, 1.3)); b.parent = bim; b.location = (dx, 0, -.65)
keys(bim, 'rotation_euler', [(f, (0, R(a), 0)) for f, a in ((0, 0), (s3, 0), (e3, 5), (T1, 9), (s5 - 1, 9), (s5, 0), (N, 0))])
for m in (bim_a, bim_b): b3d.key_input(m, 'Emission Strength', [(0, 0.), (s3, 0.), (e3, .8), (T1, 1.1), (s5 - 1, 1.1), (s5, 0.), (N, 0.)])
latch = box(latch_m, (.42, 0, 1.22), (.22, .16, .12), bevel=.02)
keys(latch, 'location', [(0, (.42, 0, 1.22)), (T1 - 2, (.42, 0, 1.22)), (T1, (.3, 0, 1.22)), (s5 - 1, (.3, 0, 1.22)), (s5, (.42, 0, 1.22)), (T2 + 2, (.42, 0, 1.22)), (T2 + 4, (.3, 0, 1.22)), (N, (.3, 0, 1.22))])
curve('Braid', [(.3, .1, .97), (.5, .1, 1.0), (.62, .1, 1.3)], copper, r=.03)
curve('W3', [(.62, 0, 2.62), (.58, 0, 2.86)], copper, r=.035)
b3d.key_input(copper, 'Emission Strength', [(0, 0.), (s5, 0.), (s5 + 20, 1.2), (T2, 1.5), (T2 + 3, 0.), (N, 0.)])
# field lines round the coil
for k in range(4):
    w, h = .45 + .12 * k, .75 + .12 * k
    L = curve(f'FL{k}', [(-.5 + w * math.cos(2 * math.pi * i / 40), -.32, 2.25 + h * math.sin(2 * math.pi * i / 40)) for i in range(40)], field_m, r=.012, cyclic=True)
    b3d.visible(L, [(s5 + int((e5 - s5) * .35), T2 + 3)])
pull = b3d.arrow('Pull', (-.5, -.4, 1.85), (-.5, -.4, 1.35), field_m, r=.025); b3d.visible(pull, [(s6, T2 + 6)])
# sparks
for T in (T1, T2):
    sp = ball(spark_m, .12, (-.8, -.05, 1.0)); b3d.visible(sp, [(T + 2, T + 9)])
    b3d.flicker(sp, 'scale', T + 2, T + 9, .6, 1.6, every=1, seed=T)
    lt = b3d.light('POINT', f'SparkL{T}', (-.8, -.4, 1.0), 0, (.7, .85, 1), .1)
    keys(lt.data, 'energy', [(T + 1, 0), (T + 2, 400), (T + 6, 200), (T + 9, 0)])
# current beads
PATH = [(-.5, -.3, 3.0), (-.5, -.3, 1.72), (-.8, -.3, 1.72), (-.8, -.3, 1.0), (.35, -.3, .97), (.62, -.3, 1.32), (.62, -.3, 2.6), (.56, -.3, 3.0)]
seg = [math.dist(PATH[i], PATH[i + 1]) for i in range(len(PATH) - 1)]; TOT = sum(seg)
def along(u):
    d = (u % 1) * TOT
    for i, L in enumerate(seg):
        if d <= L: return lerp(PATH[i], PATH[i + 1], d / L)
        d -= L
    return PATH[-1]
for k in range(14):
    p = ball(cur_m, .05)
    for f in range(s2, T1 + 1, 2): p.location = along((f - s2) / 90 + k / 14); p.keyframe_insert('location', frame=f)
    b3d.visible(p, [(s2, T1 + 1)])
    q = ball(fast_m, .065)
    for f in range(s5, T2 + 1, 1): q.location = along((f - s5) / 26 + k / 14); q.keyframe_insert('location', frame=f)
    b3d.visible(q, [(s5, T2 + 1)])

# ---------- lights ----------
b3d.light('AREA', 'Key', (3, -6, 5), 380, (1, .95, .88), 6, rot=(55, 0, 25))
b3d.light('AREA', 'Fill', (-4, -5, 2), 160, (.62, .74, 1), 5, rot=(75, 0, -35))


# ---------- timeline ----------
cam, tgt = b3d.camera(30)
b3d.shot(cam, tgt, s1, e1, (.6, -6.6, 2.6), (.4, -5.9, 2.5), (0, 0, 2.0), lens=30)
b3d.shot(cam, tgt, s2, e2, (.7, -4.6, 2.1), (.5, -4.2, 2.0), (0, 0, 1.75), lens=30)
b3d.shot(cam, tgt, s3, e3, (1.3, -2.3, 2.2), (1.15, -2.05, 2.1), (.55, 0, 1.9), lens=30)
b3d.shot(cam, tgt, s4, e4, (.4, -3.3, 1.6), (.3, -3.05, 1.55), (-.1, 0, 1.35), lens=30)
b3d.shot(cam, tgt, s5, e5, (-1.3, -2.4, 2.4), (-1.15, -2.15, 2.3), (-.5, 0, 2.05), lens=30)
b3d.shot(cam, tgt, s6, e6, (-.6, -3.3, 2.0), (-.45, -3.5, 2.1), (-.3, 0, 1.6), lens=30)
b3d.shot(cam, tgt, s7, e7, (.3, -4.8, 2.3), (.6, -7.4, 2.8), (0, 0, 1.9), lens=30)
b3d.render(OUT, cfg.get('frames'))
