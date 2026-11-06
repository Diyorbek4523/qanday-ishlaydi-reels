"""Gaz olovi: gas burner on a stove plate vs a campfire. Under the plate a cut-open venturi tube: gas jet from the nozzle pulls air in,
they mix and rise to the burner ports -> blue ring of flames. Campfire: little air, glowing soot specks make it yellow.
Shot 6 starves the burner of air and its flames turn lazy yellow. 7 shots."""
import bmesh, math, os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.03, .04, .09), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))

# ---------- materials ----------
floor_m = b3d.mat('Floor', (.07, .07, .1), .9, bump=.15)
plate_m = b3d.mat('Plate', (.05, .05, .06), .25, metal=.3)
cab_m = b3d.mat('Cabinet', (.1, .12, .18), .8)
alu = b3d.mat('Alu', (.72, .74, .78), .3, metal=.8)
cap_m = b3d.mat('Cap', (.06, .06, .07), .35)
tube_m = b3d.mat('Tube', (.55, .58, .64), .35, metal=.7)
tube_in = b3d.mat('TubeIn', (.3, .32, .38), .5, metal=.4)
brass = b3d.mat('Brass', (.85, .6, .2), .3, metal=.9)
pipe_m = b3d.mat('Pipe', (.9, .75, .1), .4)
gas_m = b3d.mat('Gas', (1, .55, .1), .3, emit=(1, .5, .08), estr=2.2)
air_m = b3d.mat('Air', (.6, .85, 1), .3, emit=(.5, .8, 1), estr=2.0)
fl_out = b3d.mat('FlameOut', (.08, .22, 1), .5, emit=(.08, .25, 1), estr=2.6)
fl_in = b3d.mat('FlameIn', (.45, .75, 1), .5, emit=(.45, .78, 1), estr=3.2)
log_m = b3d.mat('Log', (.25, .13, .06), .8, bump=.3)
coal_m = b3d.mat('Coal', (.3, .06, .02), .6, emit=(1, .25, .03), estr=2.0)
stone_m = b3d.mat('Stone', (.35, .35, .38), .9, bump=.3)
fire_o = b3d.mat('FireOut', (1, .4, .04), .5, emit=(1, .36, .03), estr=2.8)
fire_y = b3d.mat('FireIn', (1, .8, .25), .5, emit=(1, .75, .18), estr=3.2)
soot_m = b3d.mat('Soot', (1, .6, .1), .5, emit=(1, .55, .08), estr=4.0)
point_m = b3d.mat('Point', (1, .8, .2), .4, emit=(1, .72, .08), estr=2.6)
def box(m, c, s, bevel=0):
    b = b3d.prim('cube', [m], size=1, location=c); b.scale = s
    if bevel:
        bv = b.modifiers.new('Bv', 'BEVEL'); bv.width = bevel; bv.segments = 4; b3d.smooth(b)
    return b
def half(ob):
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, 0), plane_no=(0, 1, 0), clear_outer=False, clear_inner=True)
    bm.to_mesh(ob.data); bm.free(); return ob
def ease(u): u = min(1, max(0, u)); return u * u * (3 - 2 * u)
def lerp(a, b, u): return tuple(x + (y - x) * u for x, y in zip(a, b))

# ---------- room ----------
box(floor_m, (0, 0, -.25), (60, 40, .5))
box(cab_m, (0, 2.6, .75), (6, .2, 1.5))           # back of the stove body
plate = box(plate_m, (0, 0, 1.45), (6, 5.2, .1), bevel=.03)
front_p = box(cab_m, (0, -2.5, .7), (6, .2, 1.4)); side_l = box(cab_m, (-2.9, 0, .7), (.2, 5.2, 1.4)); side_r = box(cab_m, (2.9, 0, .7), (.2, 5.2, 1.4))
knobs = [b3d.smooth(b3d.prim('cylinder', [alu], vertices=24, radius=.22, depth=.15, location=(-1.6 + 1.6 * k_, -2.66, 1.0), rotation=(math.radians(90), 0, 0))) for k_ in range(3)]
TZ = .9  # tube axis height
# ---------- venturi tube (horizontal, x -3.2 .. -.2) and riser at x = 0 ----------
OUTP = [(.48, 0), (.34, .35), (.24, 1.0), (.3, 2.1), (.32, 3.0)]
INP = [(.42, 0), (.29, .35), (.19, 1.0), (.25, 2.1), (.27, 3.0)]
def tube(name, cut, m):
    ob = b3d.lathe(name, OUTP + list(reversed(INP)))
    if cut: half(ob)
    ob.data.materials.append(m); ob.rotation_euler = (0, math.radians(90), 0); ob.location = (-3.2, 0, TZ); return ob
t_back = tube('TubeBack', True, tube_in); t_full = tube('TubeFull', False, tube_m)
r_back = half(b3d.lathe('RiserBack', [(.34, .55), (.34, 1.42), (.29, 1.42), (.29, .6), (.001, .6), (.001, .55)])); r_back.data.materials.append(tube_in)
r_full = b3d.lathe('RiserFull', [(.001, .55), (.34, .55), (.34, 1.42), (.001, 1.42)]); r_full.data.materials.append(tube_m)
nozzle = b3d.prim('cone', [brass], vertices=24, radius1=.16, radius2=.05, depth=.4, location=(-3.55, 0, TZ), rotation=(0, math.radians(90), 0))
pipe = b3d.prim('cylinder', [pipe_m], vertices=24, radius=.1, depth=3.2, location=(-5.35, 0, TZ), rotation=(0, math.radians(90), 0))
# ---------- burner on top ----------
b3d.lathe('BurnerBase', [(.001, 1.5), (.95, 1.5), (.95, 1.78), (.001, 1.78)]).data.materials.append(alu)
b3d.lathe('BurnerCap', [(.001, 1.95), (.98, 1.93), (1.0, 1.87), (.001, 1.85)]).data.materials.append(cap_m)
# grate: four bars
for a in range(4):
    g = box(cap_m, (0, 0, 2.05), (4.2, .12, .1), bevel=.03); g.rotation_euler = (0, 0, math.radians(45 + 90 * a) if a < 2 else 0)
    g.location.z = 2.05 if a < 2 else -5  # only the two diagonals
NP = 26; flames = []
for i in range(NP):
    a = 2 * math.pi * i / NP; c, s_ = math.cos(a), math.sin(a)
    for m, r1, d, rr in ((fl_out, .1, .36, 1.0), (fl_in, .05, .2, 1.0)):
        f = b3d.prim('cone', [m], vertices=12, radius1=r1, radius2=0, depth=d, location=(0, 0, 0))
        f.data.transform(__import__('mathutils').Matrix.Translation((0, 0, d / 2)))  # pivot at the base
        f.location = (rr * c, rr * s_, 1.86); f.rotation_euler = (0, math.radians(38), a); b3d.smooth(f); flames.append(f)
YEL0, YEL1 = s6 + 4, s6 + 22
def flame_mul(f):
    if s6 <= f < s7: return 1 + .55 * ease((f - YEL0) / (YEL1 - YEL0))
    return 1.
for k, f in enumerate(flames): b3d.flicker(f, 'scale', 0, N, .85, 1.1, every=3, seed=k, mul=flame_mul)
BLUE_O, BLUE_I, YO, YI = (.08, .25, 1), (.45, .78, 1), (1, .55, .08), (1, .85, .3)
for m, b, y in ((fl_out, BLUE_O, YO), (fl_in, BLUE_I, YI)):
    for inp in ('Base Color', 'Emission Color'):
        b3d.key_input(m, inp, [(0, b), (YEL0, b), (YEL1, y), (s7 - 1, y), (s7, b)])
# ---------- gas + air particles: nozzle/mouth -> tube -> riser -> ports ----------
def path(u, start, y0, z0, ang):
    if u < .18: return lerp(start, (-3.15, y0, TZ + z0), u / .18)
    if u < .62: return lerp((-3.15, y0, TZ + z0), (-.05, y0, TZ + z0 * .5), (u - .18) / .44)
    if u < .8: return lerp((-.05, y0, TZ + z0 * .5), (0, y0 * .5, 1.7), (u - .62) / .18)
    return lerp((0, y0 * .5, 1.7), (.98 * math.cos(ang), .98 * math.sin(ang), 1.86), (u - .8) / .2)
parts = []
for k in range(58):
    rr = random.Random(k); is_gas = k % 3 == 0; ph = rr.random(); spd = rr.uniform(46, 60)
    y0 = rr.uniform(-.12, .05); z0 = rr.uniform(-.12, .12); ang = rr.uniform(0, 2 * math.pi)
    if is_gas: start = (-3.4, 0, TZ)
    else:
        th = rr.uniform(0, 2 * math.pi); start = (-3.9 + rr.uniform(-.2, .3), .75 * math.cos(th) * .6 - .2, TZ + .75 * math.sin(th))
    b = b3d.smooth(b3d.prim('uv_sphere', [gas_m if is_gas else air_m], segments=10, ring_count=6, radius=.055 if is_gas else .05))
    for f in range(0, N, 2):
        u = (ph + f / spd) % 1; b.location = path(u, start, y0, z0, ang); b.keyframe_insert('location', frame=f)
    parts.append(b)
for b in parts: b3d.visible(b, [(s2, e4)])
# arrows: air in, mixture up
ar_air = b3d.arrow('AirIn', (-4.4, -.4, 1.7), (-3.5, -.4, 1.15), point_m, r=.03)
ar_mix = b3d.arrow('MixUp', (-2.2, -.45, .45), (-.8, -.45, .45), point_m, r=.03)
b3d.visible(ar_air, [(s2 + 15, e2), (s3, e3)]); b3d.visible(ar_mix, [(s3 + 20, e3)])
# secondary air drifting into the flames (shot 4)
for k in range(22):
    rr = random.Random(k + 300); ang = rr.uniform(-.9, 1.9); ph = rr.random(); z = rr.uniform(1.9, 2.2)
    b = b3d.smooth(b3d.prim('uv_sphere', [air_m], segments=10, ring_count=6, radius=.04))
    for f in range(s4, e4 + 2, 2):
        u = (ph + (f - s4) / 40) % 1; r = 2.3 - 1.1 * u
        b.location = (r * math.cos(ang), r * math.sin(ang), z - .15 * u); b.keyframe_insert('location', frame=f)
    b3d.visible(b, [(s4, e4)])
b3d.visible(b3d.arrow('O2', (1.0, -2.0, 2.35), (.75, -1.3, 2.1), point_m, r=.03), [(s4 + 12, e4)])

# ---------- campfire ----------
CF = (7.5, 7, 0)
def at(x, y, z): return (CF[0] + x, CF[1] + y, CF[2] + z)
for i in range(12):
    a = 2 * math.pi * i / 12
    b3d.smooth(b3d.prim('uv_sphere', [stone_m], segments=14, ring_count=8, radius=.32, location=at(1.5 * math.cos(a), 1.5 * math.sin(a), .15))).scale = (1.2, 1, .7)
for i in range(5):
    a = 2 * math.pi * i / 5
    lg = b3d.prim('cylinder', [log_m], vertices=16, radius=.17, depth=2.2, location=at(.55 * math.cos(a), .55 * math.sin(a), .4))
    lg.rotation_euler = (0, math.radians(-68), a + math.pi); b3d.smooth(lg)
b3d.smooth(b3d.prim('uv_sphere', [coal_m], segments=20, ring_count=10, radius=.75, location=at(0, 0, .12))).scale = (1, 1, .3)
fire = []
for i in range(11):
    rr = random.Random(i + 50); a = rr.uniform(0, 2 * math.pi); r = rr.uniform(.1, .6)
    for m, r1, d in ((fire_o, rr.uniform(.18, .28), rr.uniform(1.0, 1.7)), (fire_y, rr.uniform(.1, .16), rr.uniform(.5, .9))):
        f = b3d.prim('cone', [m], vertices=16, radius1=r1, radius2=0, depth=d, location=(0, 0, 0))
        f.data.transform(__import__('mathutils').Matrix.Translation((0, 0, d / 2))); b3d.smooth(f)
        f.location = at(r * math.cos(a), r * math.sin(a), .25); f.rotation_euler = (rr.uniform(-.25, .25), rr.uniform(-.25, .25), 0); fire.append(f)
for k, f in enumerate(fire): b3d.flicker(f, 'scale', 0, N, .8, 1.15, every=3, seed=k + 100)
for k in range(70):  # glowing soot specks rising and swirling
    rr = random.Random(k + 500); ph = rr.random(); a0 = rr.uniform(0, 2 * math.pi); r0 = rr.uniform(.05, .5); spd = rr.uniform(40, 70)
    b = b3d.smooth(b3d.prim('uv_sphere', [soot_m], segments=8, ring_count=5, radius=rr.uniform(.025, .05)))
    for f in range(s5 - 2, N, 2):
        u = (ph + f / spd) % 1; a = a0 + u * 4
        b.location = at((r0 + .3 * u) * math.cos(a), (r0 + .3 * u) * math.sin(a), .6 + u * 3.2); b.keyframe_insert('location', frame=f)
    b3d.visible(b, [(s5, e5), (s7, e7)])

# ---------- which parts show ----------
b3d.visible(t_full, [(s2, e2)])
for o in [front_p, side_l] + knobs: b3d.visible(o, [(s1, e1), (s4, N)])
b3d.visible(r_full, [(s2, e2)])
b3d.visible(t_back, [(s3, e3)]); b3d.visible(r_back, [(s3, e3)])

# ---------- lights ----------
b3d.light('AREA', 'Key', (4, -9, 10), 700, (1, .95, .88), 8, rot=(40, 0, 20))
b3d.light('AREA', 'Fill', (-7, -6, 4), 260, (.62, .74, 1), 6, rot=(70, 0, -40))
b3d.light('POINT', 'Under', (-2, -2.2, .9), 60, (1, 1, 1), 1)
bl = b3d.light('POINT', 'BlueGlow', (0, 0, 2.4), 70, (.35, .55, 1), .6)
cl = b3d.light('POINT', 'FireGlow', at(0, -.6, 1.6), 260, (1, .55, .2), .8)
b3d.flicker(cl, 'energy', 0, N, 200, 320, every=3, seed=9)

# ---------- timeline ----------
cam, tgt = b3d.camera(30)
b3d.shot(cam, tgt, s1, e1, (-3.2, -8.6, 5.6), (-2.6, -7.8, 5.2), (2.4, 2.4, 1.9), lens=30)
b3d.shot(cam, tgt, s2, e2, (-5.6, -3.6, 1.6), (-5.0, -3.0, 1.3), (-3.2, 0, TZ), lens=30)
b3d.shot(cam, tgt, s3, e3, (-2.0, -4.6, 1.15), (-1.3, -4.1, 1.15), (-1.6, 0, 1.05), lens=30)
b3d.shot(cam, tgt, s4, e4, (2.2, -3.4, 3.4), (1.6, -2.9, 3.0), (.4, 0, 1.95), lens=30)
b3d.shot(cam, tgt, s5, e5, at(1.2, -5.6, 2.6), at(.6, -4.6, 2.3), at(0, 0, 1.6), lens=30)
b3d.shot(cam, tgt, s6, e6, (2.4, -4.6, 4.0), (1.8, -3.9, 3.6), (0, 0, 2.0), lens=30)
b3d.shot(cam, tgt, s7, e7, (-2.6, -7.8, 5.2), (-4.2, -11.5, 6.8), (2.4, 2.4, 1.9), lens=30)
b3d.render(OUT, cfg.get('frames'))
