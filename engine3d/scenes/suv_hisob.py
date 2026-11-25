"""Suv hisoblagich: see-through pipe with a brass vane meter; water beads swirl round the impeller and spin it;
magnet pair through a sealed plate turns the dry counter (drums + red needle); a dripping tap still turns it
slowly; pull back. 7 shots."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy
from mathutils import Vector

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.02, .02, .045), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))

def blend(m, a):
    b3d.bsdf(m).inputs['Alpha'].default_value = a
    try: m.surface_render_method = 'BLENDED'
    except Exception: pass
    return m

floor_m = b3d.mat('Tile', (.36, .23, .13), .55)
wall_m = b3d.mat('Wall', (.22, .3, .42), .85, bump=.02)
pipe_m = blend(b3d.mat('Pipe', (.75, .8, .85), .15, metal=.2), .35)
brass_m = b3d.mat('Brass', (.85, .62, .25), .3, metal=.85)
imp_m = b3d.mat('Impeller', (.35, .6, .9), .35)
red_m = b3d.mat('MagRed', (.9, .12, .1), .4)
blue_m = b3d.mat('MagBlue', (.1, .3, .9), .4)
plate_m = b3d.mat('Plate', (.35, .35, .38), .4, metal=.5)
face_m = b3d.mat('Face', (.92, .92, .9), .4)
drum_m = b3d.mat('Drum', (.06, .06, .07), .4)
band_m = b3d.mat('Band', (.95, .95, .95), .4, emit=(1, 1, 1), estr=.6)
needle_m = b3d.mat('Needle', (1, .1, .05), .3, emit=(1, .1, .05), estr=2)
glass_m = blend(b3d.mat('Glass', (.8, .9, 1), .05), .15)
water_m = b3d.mat('Water', (.3, .7, 1), .2, emit=(.2, .6, 1), estr=3)
bucket_m = b3d.mat('Bucket', (.2, .5, .35), .5)

def keys(ob, attr, fv):
    for f, v in fv: setattr(ob, attr, v); ob.keyframe_insert(attr, frame=f)

def box(name, m, loc, dims, bev=0):
    ob = b3d.prim('cube', [m], size=1, location=loc); ob.scale = dims; ob.name = name
    if bev: ob.modifiers.new('bev', 'BEVEL').width = bev
    return ob

def cyl(m, r, d, loc, rot=(0, 0, 0), v=32):
    ob = b3d.smooth(b3d.prim('cylinder', [m], vertices=v, radius=r, depth=d, location=loc)); ob.rotation_euler = rot; return ob

# ---------- room ----------
b3d.prim('plane', [floor_m], size=10, location=(0, 0, 0))
b3d.prim('plane', [wall_m], size=10, location=(0, .6, 3), rotation=(math.radians(90), 0, 0))

# ---------- pipe: in from the left, meter at x=0, out right, down to a tap over a bucket ----------
Z = .5; RX = 90 * math.pi / 180
cyl(pipe_m, .08, 1.5, (-1.05, 0, Z), (0, RX, 0))
cyl(pipe_m, .08, 1.1, (.85, 0, Z), (0, RX, 0))
cyl(pipe_m, .08, .25, (1.4, 0, Z - .1), (0, 0, 0))
cyl(brass_m, .07, .12, (1.4, 0, Z - .25), (0, 0, 0))  # spout
box('TapHandle', brass_m, (1.4, 0, Z + .1), (.05, .2, .04), .01)
for x in (-.32, .32): cyl(brass_m, .11, .06, (x, 0, Z), (0, RX, 0), 6)  # nuts
bucket = b3d.lathe('Bucket', [(0, 0), (.16, 0), (.2, .26), (.19, .26), (.15, .02), (0, .02)]); bucket.data.materials.append(bucket_m)
bucket.location = (1.4, 0, 0)

# ---------- meter body (goes see-through in shots 2-4) ----------
body_m = b3d.mat('Body', (.85, .62, .25), .3, metal=.85)
body = b3d.lathe('Body', [(0, .3), (.27, .3), (.3, .33), (.3, .66), (.27, .69), (0, .69)]); body.data.materials.append(body_m)
b3d.key_input(body_m, 'Alpha', [(0, 1), (s2 - 1, 1), (s2 + 6, .15), (e4 - 4, .15), (e4 + 3, 1)])
try: body_m.surface_render_method = 'BLENDED'
except Exception: pass
cyl(plate_m, .26, .015, (0, 0, .6))

# flow speed (impeller turns per frame), slow drip in shot 6
def speed(f):
    if s2 <= f < s6: return .09
    if s6 <= f < e7: return .012
    return .0
def spin(ob, mul, f0=0, f1=None):
    a = 0.
    for f in range(0, (f1 or e7) + 1, 2):
        a += speed(f) * 2 * mul; ob.rotation_euler = (0, 0, a)
        ob.keyframe_insert('rotation_euler', frame=f)

imp = b3d.empty('ImpRoot', (0, 0, .46))
hub = cyl(imp_m, .04, .14, (0, 0, 0)); hub.parent = imp; hub.location = (0, 0, 0)
for k in range(8):
    a = k * math.pi / 4
    bl = box(f'Blade{k}', imp_m, (0, 0, 0), (.17, .012, .11)); bl.parent = imp
    bl.location = (.11 * math.cos(a), .11 * math.sin(a), 0); bl.rotation_euler = (0, 0, a)
def magnet(root, z):
    for m, s in ((red_m, 1), (blue_m, -1)):
        b = box('Mag', m, (0, 0, 0), (.08, .05, .03)); b.parent = root; b.location = (s * .04, 0, z)
magnet(imp, .085)
up = b3d.empty('UpRoot', (0, 0, .63)); magnet(up, 0)
spin(imp, 1); spin(up, 1)

# ---------- counter on top: face plate, 5 drums, red needle dial, glass ----------
cyl(face_m, .25, .02, (0, 0, .7))
drums = []
for i in range(5):
    r = b3d.empty(f'Drum{i}', (-.1 + i * .045, -.07, .745))
    d = cyl(drum_m, .03, .038, (0, 0, 0), (0, RX, 0), 20); d.parent = r; d.location = (0, 0, 0)
    for k in range(5):
        a = k * 2 * math.pi / 5
        bd = box('Band', band_m, (0, 0, 0), (.03, .012, .006)); bd.parent = r
        bd.location = (0, .031 * math.sin(a), .031 * math.cos(a)); bd.rotation_euler = (a, 0, 0)
    drums.append(r)
box('Window', drum_m, (0, -.07, .718), (.24, .075, .01))
cyl(face_m, .055, .01, (.09, .08, .715))
nroot = b3d.empty('Needle', (.09, .08, .725))
nd = box('NeedleArm', needle_m, (0, 0, 0), (.045, .008, .006)); nd.parent = nroot; nd.location = (.022, 0, 0)
cyl(glass_m, .26, .09, (0, 0, .76))
def roll(ob, axis, mul):
    a = 0.
    for f in range(0, e7 + 1, 2):
        a += speed(f) * mul
        r = [0, 0, 0]; r[axis] = a; ob.rotation_euler = r; ob.keyframe_insert('rotation_euler', frame=f)
roll(nroot, 2, 1.2)
for i, dr in enumerate(drums): roll(dr, 0, [0, 0, .004, .04, .4][i])

# ---------- water beads: pipe -> swirl round the impeller -> pipe -> tap ----------
path = [(-1.75, 0, Z), (-.35, 0, Z), (-.22, 0, .46)]
for i in range(1, 25):
    a = math.pi + 2 * math.pi * i / 24 * 1.0
    path.append((.2 * math.cos(a), .2 * math.sin(a), .46))
path += [(.22, 0, .46), (.35, 0, Z), (1.4, 0, Z), (1.4, 0, .3)]
pts = [Vector(p) for p in path]
seg = [(pts[k + 1] - pts[k]).length for k in range(len(pts) - 1)]; TOT = sum(seg)
def at(d):
    d %= TOT
    for k, s in enumerate(seg):
        if d <= s: return pts[k].lerp(pts[k + 1], d / s)
        d -= s
    return pts[-1]
NB = 30
for k in range(NB):
    bd = b3d.prim('uv_sphere', [water_m], radius=.022, segments=10, ring_count=6, location=(0, 0, 0))
    d = k * TOT / NB
    for f in range(s1, s6 + 1, 2):
        d += .045; bd.location = at(d); bd.keyframe_insert('location', frame=f)
    b3d.visible(bd, [(s2, s6)])

# shot 1 + 6-7: drips from the spout
for t0 in range(s6 + 4, e7, 16):
    dp = b3d.smooth(b3d.prim('uv_sphere', [water_m], radius=.025, segments=12, ring_count=8, location=(1.4, 0, .17)))
    dp.scale = (.8, .8, 1.2)
    keys(dp, 'location', [(t0, (1.4, 0, .17)), (t0 + 3, (1.4, 0, .16)), (t0 + 12, (1.4, 0, .04))])
    b3d.visible(dp, [(t0, t0 + 12)])

b3d.light('AREA', 'Key', (-1.2, -2.2, 2.6), 170, (1, .88, .75), 3, rot=(50, 0, -25))
b3d.light('AREA', 'Fill', (2.0, -1.8, 1.4), 60, (.6, .7, 1), 3, rot=(65, 0, 45))
b3d.light('POINT', 'Inside', (.2, -.9, 1.1), 12, (1, .9, .8), .2)

# ---------- camera ----------
cam, tgt = b3d.camera(35)
b3d.shot(cam, tgt, s1, e1, (.35, -2.4, 1.4), (.3, -2.2, 1.3), (.2, 0, .45), lens=35)
b3d.shot(cam, tgt, s2, e2, (.3, -1.0, .85), (.25, -.9, .8), (0, 0, .47), lens=38)
b3d.shot(cam, tgt, s3, e3, (-.55, -.75, .55), (-.5, -.7, .56), (0, 0, .48), lens=40)
b3d.shot(cam, tgt, s4, e4, (.4, -.6, .68), (.35, -.55, .66), (0, 0, .58), lens=40)
b3d.shot(cam, tgt, s5, e5, (0, -.42, 1.2), (0, -.36, 1.12), (0, 0, .72), lens=40)
b3d.shot(cam, tgt, s6, e6, (.9, -1.4, .75), (.95, -1.3, .7), (1.1, 0, .3), lens=35)
b3d.shot(cam, tgt, s7, e7, (.3, -2.0, 1.2), (.3, -3.4, 2.0), (.3, 0, .4), lens=35)

b3d.render(OUT, cfg.get('frames'))
