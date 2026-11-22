"""Suv filtri (teskari osmos): 3 clear canisters + horizontal membrane housing + tank + faucet over a glass.
1: whole system, dirty water in (hook text); 2: sediment canister close, sand/rust stick to the white cartridge;
3: carbon canister, green chlorine dots soaked up; 4: membrane macro (slats with tiny gaps): blue water passes, big salt
ions bounce; 5: macro again: pressure arrow, salts flushed down the drain line, clean water to the tank; 6: glass fills
with clear water; 7: pull back. 7 shots."""
import math, os, sys, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy
from mathutils import Vector

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.015, .025, .06), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))
R = math.radians
rnd = random.Random(5)

def keys(ob, attr, fv):
    for f, v in fv: setattr(ob, attr, v); ob.keyframe_insert(attr, frame=f)

def blend(m, a):
    b3d.bsdf(m).inputs['Alpha'].default_value = a
    try: m.surface_render_method = 'BLENDED'
    except Exception: pass
    return m

def box(name, m, lo, hi):
    lo, hi = Vector(lo), Vector(hi)
    ob = b3d.prim('cube', [m], size=1, location=(lo + hi) / 2); ob.scale = hi - lo; ob.name = name; return ob

def tube(a, b, m, r=.015):
    a, b = Vector(a), Vector(b); d = b - a
    ob = b3d.prim('cylinder', [m], vertices=16, radius=r, depth=d.length, location=(a + b) / 2)
    ob.rotation_mode = 'QUATERNION'; ob.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized()); return ob

clear_m = blend(b3d.mat('Clear', (.75, .85, .95), .05), .22)
cap_m = b3d.mat('Cap', (.15, .35, .7), .35)
plate_m = b3d.mat('Plate', (.88, .88, .86), .4)
sed_m = b3d.mat('Sed', (.95, .93, .88), .9, bump=.4)
carb_m = b3d.mat('Carbon', (.06, .06, .06), .8, bump=.5)
memb_m = b3d.mat('Memb', (.92, .92, .9), .5)
pipe_m = b3d.mat('Pipe', (.9, .9, .92), .3)
drain_m = b3d.mat('DrainPipe', (.35, .35, .38), .5)
tank_m = b3d.mat('Tank', (.85, .87, .9), .35)
chrome_m = b3d.mat('Chrome', (.8, .82, .85), .12, metal=1)
floor_m = b3d.mat('Floor', (.4, .3, .22), .6)
wallb_m = b3d.mat('WallB', (.22, .27, .34), .8)
dirty_m = b3d.mat('Dirty', (.35, .18, .06), .7, emit=(.4, .2, .05), estr=.4)
chlor_m = b3d.mat('Chlor', (.4, .9, .3), .4, emit=(.35, .9, .25), estr=1.2)
water_m = b3d.mat('WaterDot', (.4, .75, 1), .3, emit=(.3, .7, 1), estr=1.2)
saltA_m = b3d.mat('Na', (1, .8, .2), .4, emit=(1, .75, .15), estr=3)
saltB_m = b3d.mat('Cl', (.9, .3, .25), .4, emit=(1, .3, .2), estr=3)
glassw_m = blend(b3d.mat('GlassW', (.5, .75, 1), .05, emit=(.3, .6, 1), estr=.6), .55)
arrow_m = b3d.mat('Arrow', (1, .55, .15), .3, emit=(1, .5, .1), estr=4)
lbl_m = b3d.mat('Lbl', (.95, .95, 1), .4, emit=(.95, .95, 1), estr=3)

# ---------- macro system ----------
b3d.prim('plane', [floor_m], size=12, location=(0, 0, 0))
box('BackWall', wallb_m, (-3, .45, 0), (3, .5, 3))
box('Plate', plate_m, (-.85, .2, .05), (.45, .23, .95))
CX = [-.6, -.2, .2]; CR, CH, CZ = .11, .5, .1
for i, x in enumerate(CX):
    b3d.smooth(b3d.prim('cylinder', [clear_m], vertices=40, radius=CR, depth=CH, location=(x, 0, CZ + CH / 2)))
    b3d.smooth(b3d.prim('cylinder', [cap_m], vertices=40, radius=CR + .015, depth=.07, location=(x, 0, CZ + CH + .035)))
    inner = [sed_m, carb_m, sed_m][i]
    b3d.smooth(b3d.prim('cylinder', [inner], vertices=32, radius=.07, depth=CH - .06, location=(x, 0, CZ + CH / 2)))
MZ = .8
b3d.smooth(b3d.prim('cylinder', [clear_m], vertices=40, radius=.075, depth=.85, location=(-.2, 0, MZ), rotation=(0, R(90), 0)))
b3d.smooth(b3d.prim('cylinder', [memb_m], vertices=32, radius=.05, depth=.78, location=(-.2, 0, MZ), rotation=(0, R(90), 0)))
for x in (-.64, .24): b3d.smooth(b3d.prim('cylinder', [cap_m], vertices=32, radius=.085, depth=.05, location=(x, 0, MZ), rotation=(0, R(90), 0)))
TX = .65
b3d.smooth(b3d.lathe('Tank', [(0, .02), (.16, .04), (.18, .2), (.16, .48), (.05, .53), (0, .53)])).location = (TX, 0, 0)
for o in bpy.data.objects:
    if o.name == 'Tank': o.data.materials.append(tank_m)
# pipes
P_IN = [(-1.3, 0, .66), (-.6, 0, .66)]
tube(*P_IN, pipe_m)
tube((-.6, 0, .66), (-.2, 0, .66), pipe_m); tube((-.2, 0, .66), (.2, 0, .66), pipe_m)
tube((.2, 0, .66), (.2, 0, .72), pipe_m); tube((.2, 0, .72), (.26, 0, .8), pipe_m)
tube((-.66, 0, .8), (-.72, 0, .9), pipe_m); tube((-.72, 0, .9), (TX, 0, .9), pipe_m); tube((TX, 0, .9), (TX, 0, .53), pipe_m)
DR = [(-.66, -.02, .78), (-.75, -.12, .5), (-.75, -.12, .02)]
tube(DR[0], DR[1], drain_m, .012); tube(DR[1], DR[2], drain_m, .012)
# faucet + glass
GX, GY = 1.0, -.15
tube((TX + .1, 0, .3), (GX, 0, .3), pipe_m); tube((GX, 0, .3), (GX, 0, .55), chrome_m, .018)
tube((GX, 0, .55), (GX, GY, .55), chrome_m, .018); tube((GX, GY, .55), (GX, GY, .5), chrome_m, .018)
b3d.lathe('Glass', [(0, 0), (.06, 0), (.065, .2), (.06, .2), (.055, .005), (0, .005)]).location = (GX, GY, 0)
bpy.data.objects['Glass'].data.materials.append(blend(b3d.mat('GlassC', (.9, .95, 1), .05), .2))
gw = b3d.prim('cylinder', [glassw_m], vertices=32, radius=.054, depth=1, location=(GX, GY, .005)); gw.visible_shadow = False
F6a, F6b = s6 + 10, e6 - 10
for f, h in [(0, .001), (F6a, .001), (F6b, .17), (N, .17)]:
    gw.scale = (1, 1, h); gw.location = (GX, GY, .005 + h / 2); gw.keyframe_insert('scale', frame=f); gw.keyframe_insert('location', frame=f)
stream = b3d.prim('cylinder', [water_m], vertices=12, radius=.007, depth=.45, location=(GX, GY, .27))
b3d.visible(stream, [(F6a - 5, F6b)])

def dots(n, m, r, path_fn, f0, f1, stay=False, name='D'):
    for k in range(n):
        d = b3d.prim('uv_sphere', [m], radius=r, segments=10, ring_count=6); d.visible_shadow = False
        t0 = f0 + int((f1 - f0 - 20) * k / max(1, n)) if not stay else f0 + rnd.randint(0, max(1, (f1 - f0) // 2))
        pts = path_fn(k)
        span = max(20, (f1 - t0) - 2) if stay else 40
        fr = [(t0 + int(span * j / (len(pts) - 1)), p) for j, p in enumerate(pts)]
        keys(d, 'location', fr)
        b3d.visible(d, [(t0, (N if stay else min(fr[-1][0] + 1, f1)))] if not stay else [(t0, f1)])

# shot 1: dirty particles flowing in the inlet pipe
dots(14, dirty_m, .014, lambda k: [Vector((-1.4, 0, .66)), Vector((-.6, 0, .66)), Vector((-.6, rnd.uniform(-.05, .05), .4))], s1, e1)
# shot 2: sediment: sand/rust come down and stick on the white cartridge
def sed_path(k):
    a = rnd.uniform(0, 2 * math.pi); z = rnd.uniform(CZ + .06, CZ + CH - .06)
    return [Vector((-.6 + .095 * math.cos(a), .095 * math.sin(a), CZ + CH - .01)), Vector((-.6 + .08 * math.cos(a), .08 * math.sin(a), z)),
            Vector((-.6 + .072 * math.cos(a), .072 * math.sin(a), z))]
for k in range(60):
    d = b3d.prim('uv_sphere', [dirty_m], radius=rnd.uniform(.006, .012), segments=8, ring_count=6); d.visible_shadow = False
    pts = sed_path(k); t0 = s2 + rnd.randint(0, (e2 - s2) // 2)
    keys(d, 'location', [(t0, pts[0]), (t0 + 20, pts[1]), (t0 + 30, pts[2])]); b3d.visible(d, [(t0, e3)])
# shot 3: carbon: green chlorine dots soaked into the black block
for k in range(40):
    d = b3d.prim('uv_sphere', [chlor_m], radius=.009, segments=8, ring_count=6); d.visible_shadow = False
    a = rnd.uniform(0, 2 * math.pi); z = rnd.uniform(CZ + .06, CZ + CH - .06); t0 = s3 + rnd.randint(0, (e3 - s3) // 2)
    keys(d, 'location', [(t0, (-.2 + .1 * math.cos(a), .1 * math.sin(a), CZ + CH - .02)), (t0 + 22, (-.2 + .075 * math.cos(a), .075 * math.sin(a), z)),
                         (t0 + 34, (-.2 + .06 * math.cos(a), .06 * math.sin(a), z))])
    keys(d, 'scale', [(t0 + 26, (1, 1, 1)), (t0 + 40, (0, 0, 0))]); b3d.visible(d, [(t0, e3)])

# ---------- membrane macro (far away at x=20) ----------
MX = Vector((20, 0, 1))
box('MBack', wallb_m, MX + Vector((-3, .6, -4)), MX + Vector((3, .65, 3)))
for k in range(-6, 7):
    box('Slat', memb_m, MX + Vector((-.05, -.25, k * .12 - .045)), MX + Vector((.05, .25, k * .12 + .045)))
def micro(f0, f1, n_w, n_s, press=False):
    for k in range(n_w):
        d = b3d.prim('uv_sphere', [water_m], radius=.014, segments=10, ring_count=6); d.visible_shadow = False
        g = rnd.randint(-5, 6) * .12 - .06; t0 = f0 + rnd.randint(0, max(1, f1 - f0 - 40)); y = rnd.uniform(-.2, .2)
        keys(d, 'location', [(t0, MX + Vector((-.8, y, g + rnd.uniform(-.2, .2)))), (t0 + 18, MX + Vector((-.06, y, g))),
                             (t0 + 26, MX + Vector((.06, y, g))), (t0 + 40, MX + Vector((.7, y, g + rnd.uniform(-.15, .15))))])
        b3d.visible(d, [(t0, min(t0 + 41, f1))])
    for k in range(n_s):
        m = saltA_m if k % 2 else saltB_m
        d = b3d.prim('uv_sphere', [m], radius=.045, segments=16, ring_count=8)
        t0 = f0 + rnd.randint(0, max(1, f1 - f0 - 45)); y = rnd.uniform(-.2, .2); z = rnd.uniform(-.5, .5)
        back = MX + Vector((-.5, y, z - (.9 if press else -.15)))
        keys(d, 'location', [(t0, MX + Vector((-.9, y, z))), (t0 + 20, MX + Vector((-.1, y, z))), (t0 + 44, back)])
        b3d.visible(d, [(t0, min(t0 + 45, f1))])
micro(s4, e4, 70, 22)
micro(s5, e5, 60, 26, press=True)
for o, rg in ((None, None),):
    pass
def label(txt, loc, m, size=.12, rotz=0):
    cu = bpy.data.curves.new('L', 'FONT'); cu.body = txt; cu.size = size; cu.align_x = 'CENTER'; cu.extrude = .008
    ob = b3d.link(bpy.data.objects.new('L', cu)); ob.data.materials.append(m); ob.location = loc
    ob.rotation_euler = (R(90), 0, R(rotz)); return ob
for o in (label('SUV', MX + Vector((.55, -.3, .62)), water_m), label('TUZ', MX + Vector((-.6, -.3, .62)), saltA_m)):
    b3d.visible(o, [(s4, e5)])
for i, z in enumerate((-.35, 0, .35)):
    a = b3d.arrow(f'P{i}', MX + Vector((-1.3, -.1, z)), MX + Vector((-.85, -.1, z)), arrow_m, r=.03)
    b3d.visible(a, [(s5, e5)])
bos = label('BOSIM', MX + Vector((-1.05, -.1, .62)), arrow_m); b3d.visible(bos, [(s5, e5)])
dn = b3d.arrow('Down', MX + Vector((-.5, -.25, -.5)), MX + Vector((-.5, -.25, -1.1)), saltB_m, r=.03); b3d.visible(dn, [(s5, e5)])

# shot 6: clean water flows tank -> faucet (macro)
dots(18, water_m, .012, lambda k: [Vector((TX, 0, .9)), Vector((TX, 0, .55)), Vector((TX + .1, 0, .3)), Vector((GX, 0, .3)),
                                   Vector((GX, 0, .55)), Vector((GX, GY, .5))], s6, e6)

b3d.light('AREA', 'Key', (-1.2, -2.2, 2.4), 80, (1, .9, .78), 2.5, rot=(55, 0, -25))
b3d.light('AREA', 'Fill', (1.8, -1.5, 1.2), 30, (.6, .7, 1), 1.5, rot=(70, 0, 50))
b3d.light('AREA', 'KeyM', MX + Vector((-1, -2.2, 1.6)), 70, (1, .92, .85), 2.5, rot=(60, 0, -20))
b3d.light('POINT', 'Spot', (-.2, -.6, .6), 12, (.9, .95, 1), .3)

cam, tgt = b3d.camera(24)
b3d.shot(cam, tgt, s1, e1, (-.15, -2.0, .8), (-.1, -1.8, .75), (-.05, 0, .5), lens=24)
b3d.shot(cam, tgt, s2, e2, (-.62, -.62, .42), (-.58, -.55, .38), (-.6, 0, .35), lens=28)
b3d.shot(cam, tgt, s3, e3, (-.24, -.6, .42), (-.18, -.54, .38), (-.2, 0, .35), lens=28)
b3d.shot(cam, tgt, s4, e4, MX + Vector((0, -2.2, .1)), MX + Vector((0, -1.95, 0)), MX, lens=24)
b3d.shot(cam, tgt, s5, e5, MX + Vector((-.3, -2.4, .1)), MX + Vector((-.25, -2.2, 0)), MX + Vector((-.3, 0, -.1)), lens=24)
b3d.shot(cam, tgt, s6, e6, (.8, -1.0, .45), (.85, -.85, .4), (.85, 0, .3), lens=26)
b3d.shot(cam, tgt, s7, e7, (.2, -1.8, .7), (.2, -3.0, .9), (.2, 0, .55), lens=24)

b3d.render(OUT, cfg.get('frames'))
