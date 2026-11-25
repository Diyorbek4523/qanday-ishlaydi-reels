"""Konditsioner nega tomchilaydi: wall split unit drips on the floor; see-through housing: warm air -> filter -> cold coil
-> fan -> cold air out; vapour condenses on the fins, runs to the pan; drain hose carries it outside; dirty filter ->
coil ices -> pan overflows indoors; filter cleaned; pull back. 7 shots."""
import math, os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy
from mathutils import Vector

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.02, .02, .045), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))
RY = math.pi / 2
def L(a, b, t): return a + (b - a) * t

floor_m = b3d.mat('Floor', (.36, .23, .13), .55)
wall_m = b3d.mat('Wall', (.16, .22, .3), .85, bump=.02)
out_m = b3d.mat('OutWall', (.42, .36, .3), .9, bump=.03)
body_m = b3d.mat('Body', (.92, .93, .95), .35)
fin_m = b3d.mat('Fin', (.7, .75, .8), .3, metal=.6)
cu_m = b3d.mat('Copper', (.85, .45, .25), .3, metal=.9)
fan_m = b3d.mat('Fan', (.25, .3, .38), .5)
filt_m = b3d.mat('Filter', (.75, .9, 1), .6)
pan_m = b3d.mat('Pan', (.35, .45, .55), .5)
hose_m = b3d.mat('Hose', (.85, .85, .8), .6)
warm_m = b3d.mat('Warm', (1, .35, .05), .3, emit=(1, .3, .02), estr=1.3)
cold_m = b3d.mat('Cold', (.1, .45, 1), .3, emit=(.05, .4, 1), estr=1.3)
water_m = b3d.mat('Water', (.3, .7, 1), .15, emit=(.25, .6, 1), estr=2.5)
pool_m = b3d.mat('Pool', (.2, .45, .8), .05, emit=(.15, .4, .9), estr=.6)
slot_m = b3d.mat('Slot', (.05, .05, .06), .5)
led_m = b3d.mat('Led', (.2, 1, .4), .3, emit=(.2, 1, .4), estr=4)

def box(name, m, loc, dims, bev=0):
    ob = b3d.prim('cube', [m], size=1, location=loc); ob.scale = dims; ob.name = name
    if bev: ob.modifiers.new('bev', 'BEVEL').width = bev; ob.modifiers['bev'].segments = 3
    return ob
def cyl(m, r, d, loc, rot=(0, 0, 0), v=24):
    ob = b3d.smooth(b3d.prim('cylinder', [m], vertices=v, radius=r, depth=d, location=loc)); ob.rotation_euler = rot; return ob
def ball(m, r, loc=(0, 0, -5)):
    return b3d.smooth(b3d.prim('uv_sphere', [m], radius=r, segments=12, ring_count=8, location=loc))
def keys(ob, attr, fv):
    for f, v in fv: setattr(ob, attr, v); ob.keyframe_insert(attr, frame=f)

# ---------- room wall (indoor face y=0), outside face y=.25 ----------
b3d.prim('plane', [floor_m], size=14, location=(0, 0, 0))
box('WallIn', wall_m, (0, .06, 2), (6, .12, 4))
box('WallOut', out_m, (0, .19, 2), (6, .14, 4))
UZ = 2.3   # unit centre height

# ---------- unit housing (goes see-through in shots 2-6) ----------
body = box('Housing', body_m, (0, -.15, UZ), (1.0, .26, .32), .05)
b3d.key_input(body_m, 'Alpha', [(0, 1), (s2 - 1, 1), (s2 + 6, .1), (e6 - 4, .1), (e6 + 3, 1)])
try: body_m.surface_render_method = 'BLENDED'
except Exception: pass
box('Louver', slot_m, (0, -.27, UZ - .14), (.82, .03, .04), .01)
box('Led', led_m, (.38, -.283, UZ - .08), (.03, .005, .01))

# coil: slanted fin block with copper pipes
coil = b3d.empty('Coil', (0, -.17, UZ + .04)); coil.rotation_euler = (math.radians(-28), 0, 0)
for i in range(30):
    fn = box(f'Fin{i}', fin_m, (0, 0, 0), (.006, .07, .2)); fn.parent = coil; fn.location = (-.43 + i * .0297, 0, 0)
for z in (-.06, 0, .06):
    p = cyl(cu_m, .012, .9, (0, 0, 0), (0, RY, 0), 12); p.parent = coil; p.location = (0, 0, z)
# ice on the fins (shot 5): fin colour goes frosty white and back
b3d.key_input(fin_m, 'Base Color', [(0, (.7, .75, .8)), (int(L(s5, e5, .35)), (.7, .75, .8)),
                                    (e5, (.95, .98, 1)), (int(L(s6, e6, .5)), (.95, .98, 1)), (e6, (.7, .75, .8))])

fanroot = b3d.empty('FanRoot', (0, -.11, UZ - .07)); fanroot.rotation_euler = (0, RY, 0)
fan = cyl(fan_m, .03, .8, (0, 0, 0), v=16); fan.parent = fanroot; fan.location = (0, 0, 0)
for k in range(8):
    bl = box(f'Blade{k}', fan_m, (0, 0, 0), (.008, .03, .8)); bl.parent = fan
    a = k * math.pi / 4; bl.location = (.06 * math.cos(a), .06 * math.sin(a), 0); bl.rotation_euler = (0, 0, a)
def spd(f):
    if s5 + 10 <= f < int(L(s6, e6, .5)): return .35        # clogged filter: weak airflow
    return 1.0
a = 0.
for f in range(0, e7 + 2, 2):
    a += .5 * spd(f); fan.rotation_euler = (0, 0, a); fan.keyframe_insert('rotation_euler', frame=f)

# filter on the top intake; gets dusty in shot 5, slides out and is clean in shot 6
filt = box('Filter', filt_m, (0, -.15, UZ + .165), (.92, .2, .012))
for i in range(12):
    g = box(f'Grid{i}', filt_m, (0, 0, 0), (.004, .2, .016)); g.parent = filt
    g.location = (-.42 + i * .076, 0, 0); g.scale = (.004 / .92, 1, 1.4)
b3d.key_input(filt_m, 'Base Color', [(0, (.75, .9, 1)), (s5, (.75, .9, 1)), (s5 + 14, (.15, .11, .07)),
                                     (int(L(s6, e6, .45)), (.15, .11, .07)), (int(L(s6, e6, .6)), (.75, .9, 1))])
keys(filt, 'location', [(s6, (0, -.15, UZ + .165)), (int(L(s6, e6, .3)), (0, -.5, UZ + .3)),
                        (int(L(s6, e6, .7)), (0, -.5, UZ + .3)), (e6, (0, -.15, UZ + .165))])

# drain pan + water layer, hose through the wall to the outside
box('Pan', pan_m, (0, -.2, UZ - .135), (.95, .1, .02))
box('PanLipF', pan_m, (0, -.25, UZ - .12), (.95, .01, .04)); box('PanLipB', pan_m, (0, -.15, UZ - .12), (.95, .01, .04))
pool = box('PanWater', pool_m, (0, -.2, UZ - .122), (.93, .09, .006))
keys(pool, 'scale', [(0, (.93, .09, .006)), (s5 + 10, (.93, .09, .006)), (e5, (.93, .09, .03)), (e6, (.93, .09, .006))])
hp = [Vector(p) for p in ((.46, -.2, UZ - .14), (.55, -.08, UZ - .2), (.55, .3, UZ - .26), (.55, .34, UZ - .4), (.55, .34, 1.45))]
for a_, b_ in zip(hp[:-1], hp[1:]):
    d = b_ - a_; c = cyl(hose_m, .018, d.length, tuple((a_ + b_) / 2), v=12)
    c.rotation_mode = 'QUATERNION'; c.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())

# ---------- path helpers ----------
def mkpath(pl):
    pts = [Vector(p) for p in pl]; seg = [(pts[k + 1] - pts[k]).length for k in range(len(pts) - 1)]
    def at(d):
        d %= sum(seg)
        for k, s in enumerate(seg):
            if d <= s: return pts[k].lerp(pts[k + 1], d / s)
            d -= s
        return pts[-1]
    return at, sum(seg)
def stream(m, r, pl, n, f0, f1, v, rng=None, speed=spd):
    at, T = mkpath(pl)
    for k in range(n):
        b = ball(m, r); d = k * T / n
        for f in range(f0, f1 + 2, 2):
            d += v * speed(f); b.location = at(d); b.keyframe_insert('location', frame=f)
        b3d.visible(b, rng or [(f0, f1)])

for x in (-.3, 0, .3):   # warm air in through the filter to the coil, cold air out through the louver
    stream(warm_m, .018, [(x, -.25, UZ + .55), (x, -.15, UZ + .2), (x, -.17, UZ + .05)], 6, s2, e6, .012)
    stream(cold_m, .018, [(x, -.13, UZ - .02), (x, -.24, UZ - .14), (x, -.55, UZ - .4)], 6, s2, e6, .014)

# condensation: droplets grow on the fins then run down to the pan
R = random.Random(4)
for k in range(26):
    x = R.uniform(-.4, .4); z0 = R.uniform(UZ + .0, UZ + .12); y0 = -.2 - (z0 - UZ) * .5
    b = ball(water_m, .011, (x, y0, z0))
    t0 = s3 + R.randint(0, 40)
    for c in range(4):
        t = t0 + c * 34
        if t > e6: break
        keys(b, 'location', [(t, (x, y0, z0)), (t + 20, (x, y0, z0)), (t + 30, (x, -.2, UZ - .12))])
        keys(b, 'scale', [(t, (.1, .1, .1)), (t + 18, (1, 1, 1.3)), (t + 30, (1, 1, 1.3)), (t + 31, (.1, .1, .1))])
    b3d.visible(b, [(s3, e6)])

# water through the hose and out
stream(water_m, .013, [tuple(p) for p in hp], 10, s3, e7, .012)
def drips(x, y, z0, z1, fs, f0, f1, m=water_m):
    for t in range(f0, f1, fs):
        d = ball(m, .016, (x, y, z0)); d.scale = (.85, .85, 1.25)
        keys(d, 'location', [(t, (x, y, z0)), (t + 4, (x, y, z0 - .01)), (t + 16, (x, y, z1))])
        b3d.visible(d, [(t, t + 16)])
drips(.55, .34, 1.43, .02, 9, s3, e7)                             # outside, from the hose end
drips(-.2, -.27, UZ - .17, .02, 11, s1, e1)                         # hook: drips on the floor
drips(.15, -.27, UZ - .17, .02, 10, int(L(s5, e5, .4)), int(L(s6, e6, .5)))
drips(-.25, -.27, UZ - .17, .02, 13, int(L(s5, e5, .6)), int(L(s6, e6, .45)))
pud = cyl(pool_m, .22, .004, (0, -.35, .003), v=32); pud.scale = (1.2, .7, 1)
keys(pud, 'scale', [(0, (.5, .35, 1)), (e1, (1, .6, 1)), (e5, (1.3, .75, 1))])

# ---------- lights ----------
b3d.light('AREA', 'Key', (-1.4, -2.4, 3.2), 200, (1, .88, .75), 3, rot=(45, 0, -25))
b3d.light('AREA', 'Fill', (1.8, -1.8, 2.0), 70, (.6, .7, 1), 3, rot=(65, 0, 45))
b3d.light('POINT', 'UnitGlow', (0, -.7, UZ), 15, (1, 1, 1), .3)
b3d.light('POINT', 'OutKey', (1.3, 1.4, 2.2), 260, (.7, .8, 1), .5)
b3d.light('POINT', 'OutFill', (-.6, 1.6, .8), 80, (1, .8, .6), .5)

# ---------- camera ----------
cam, tgt = b3d.camera(30)
b3d.shot(cam, tgt, s1, e1, (-.65, -2.2, 1.75), (-.55, -2.05, 1.8), (0, -.15, 1.6), lens=26)
b3d.shot(cam, tgt, s2, e2, (.4, -1.45, 2.5), (.32, -1.3, 2.45), (0, -.15, UZ), lens=34)
b3d.shot(cam, tgt, s3, e3, (-.25, -.8, UZ + .2), (-.2, -.72, UZ + .17), (-.12, -.19, UZ + .04), lens=40)
b3d.shot(cam, tgt, s4, e4, (1.9, 2.1, 1.45), (1.75, 1.9, 1.4), (.55, .3, 1.05), lens=32)
b3d.shot(cam, tgt, s5, e5, (.55, -1.35, 1.95), (.48, -1.25, 1.95), (0, -.2, UZ - .1), lens=32)
b3d.shot(cam, tgt, s6, e6, (-.55, -1.5, 2.55), (-.48, -1.35, 2.5), (0, -.3, UZ + .05), lens=33)
b3d.shot(cam, tgt, s7, e7, (0, -2.3, 2.0), (0, -3.7, 2.3), (0, 0, 1.8), lens=30)

b3d.render(OUT, cfg.get('frames'))
