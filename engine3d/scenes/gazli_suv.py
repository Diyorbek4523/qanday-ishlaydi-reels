"""Gazli suv: a soda bottle on a table. Shots 1-2 outside; 3-6 the bottle is cut in half (back half kept) so we see the
liquid with dim dissolved CO2 dots and bright, jittering gas in the head space. Shot 5 the cap unscrews and lifts, the head
space gas shoots out of the neck; shot 6 the dissolved dots grow into bubbles, rise and foam at the top. 7 shots."""
import math, os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy, bmesh

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.03, .04, .08), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))
R = math.radians; rnd = random.Random(7)

glass = b3d.mat('Glass', (.35, .75, .5), .15, emit=(.1, .35, .2), estr=.15)
glass_in = b3d.mat('GlassIn', (.25, .55, .38), .3)
liquid = b3d.mat('Liquid', (.55, .8, .95), .2, emit=(.25, .5, .7), estr=.35)
cap_m = b3d.mat('Cap', (.85, .12, .1), .35)
label_m = b3d.mat('Label', (.95, .85, .3), .5)
table_m = b3d.mat('Table', (.45, .27, .14), .6, bump=.12)
wall_m = b3d.mat('Wall', (.25, .3, .42), .7, bump=.05)
co2_dim = b3d.mat('CO2dim', (.9, .95, 1), .4, emit=(.8, .9, 1), estr=1.0)
co2 = b3d.mat('CO2', (1, 1, 1), .3, emit=(.9, .95, 1), estr=3.0)
bub = b3d.mat('Bubble', (.95, .98, 1), .1, emit=(.85, .95, 1), estr=1.6)
arrow_m = b3d.mat('Arrow', (1, .85, .2), .4, emit=(1, .8, .1), estr=4)
press_m = b3d.mat('Press', (1, .3, .15), .4, emit=(1, .25, .1), estr=3)

def keys(ob, attr, fv):
    for f, v in fv: setattr(ob, attr, v); ob.keyframe_insert(attr, frame=f)
def ball(m, r, loc=(0, 0, 0)): return b3d.smooth(b3d.prim('uv_sphere', [m], segments=12, ring_count=6, radius=r, location=loc))

def lathe(name, prof, angle=2 * math.pi, steps=64):
    bm = bmesh.new(); vs = [bm.verts.new((r, 0, z)) for r, z in prof]
    es = [bm.edges.new((vs[i], vs[i + 1])) for i in range(len(vs) - 1)]
    bmesh.ops.spin(bm, geom=vs + es, cent=(0, 0, 0), axis=(0, 0, 1), angle=angle, steps=steps, use_merge=angle > 6.2)
    if angle < 6.2:   # close the cut face of a solid half (profile from axis to axis)
        pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    return b3d.smooth(b3d.link(bpy.data.objects.new(name, me)))

# bottle outer profile (r, z); neck top at 2.3
BOT = [(0, 0), (.38, 0), (.44, .05), (.46, .2), (.46, 1.3), (.42, 1.55), (.3, 1.8), (.18, 1.98), (.15, 2.05), (.15, 2.3)]
def inner(p, t=.035): return [(max(r - t, 0), z + (t if z == 0 else 0)) for r, z in p]

# ---------- full bottle (outside shots) ----------
full = lathe('Bottle', BOT[1:]); full.data.materials.append(glass)
so = full.modifiers.new('S', 'SOLIDIFY'); so.thickness = .03
fliq = lathe('LiqFull', [(0, .04)] + [(r, z) for r, z in inner(BOT)[1:] if z < 1.84] + [(.238, 1.84), (0, 1.84)]); fliq.data.materials.append(liquid)
lab = lathe('Label', [(.47, .55), (.47, 1.05)]); lab.data.materials.append(label_m)
lso = lab.modifiers.new('S', 'SOLIDIFY'); lso.thickness = .01
OUTSIDE = [(0, s3), (s7, N)]
for o in (full, fliq, lab): b3d.visible(o, OUTSIDE)

# ---------- cut bottle (back half, y >= 0) ----------
half = lathe('BottleHalf', BOT[1:], math.pi, 32); half.data.materials.append(glass); half.data.materials.append(glass_in)
hso = half.modifiers.new('S', 'SOLIDIFY'); hso.thickness = .03; hso.material_offset = 1
LQ = [(0, .04)] + [(r, z) for r, z in inner(BOT)[1:] if z < 1.84] + [(.238, 1.84), (0, 1.84)]
liq = lathe('LiqHalf', LQ, math.pi, 32); liq.data.materials.append(liquid)
# flat cut face of the liquid at y = 0
bm = bmesh.new(); pts = [(r, z) for r, z in LQ] ; ring = [bm.verts.new((r, 0, z)) for r, z in pts] + [bm.verts.new((-r, 0, z)) for r, z in reversed(pts)]
bm.faces.new(ring); me = bpy.data.meshes.new('LiqCut'); bm.to_mesh(me); bm.free()
lcut = b3d.link(bpy.data.objects.new('LiqCut', me)); me.materials.append(liquid)
labh = lathe('LabelHalf', [(.47, .55), (.47, 1.05)], math.pi, 32); labh.data.materials.append(label_m)
lso = labh.modifiers.new('S', 'SOLIDIFY'); lso.thickness = .01
INSIDE = [(s3, s7)]
for o in (half, liq, lcut, labh): b3d.visible(o, INSIDE)

# ---------- cap ----------
cap = b3d.smooth(b3d.prim('cylinder', [cap_m], vertices=40, radius=.19, depth=.24, location=(0, 0, 2.38)))
for k in range(16):
    a = 2 * math.pi * k / 16
    r_ = b3d.prim('cube', [cap_m], size=1, location=(.19 * math.cos(a), .19 * math.sin(a), 2.38)); r_.scale = (.025, .025, .2)
    r_.rotation_euler = (0, 0, a); r_.parent = cap; r_.location = (.19 * math.cos(a), .19 * math.sin(a), 0)
OPEN = s5 + int((e5 - s5) * .2)
keys(cap, 'rotation_euler', [(s5, (0, 0, 0)), (OPEN, (0, 0, R(-300)))])
keys(cap, 'location', [(0, (0, 0, 2.38)), (s5, (0, 0, 2.38)), (OPEN, (0, 0, 2.42)), (OPEN + 12, (.45, -.1, 2.85)), (s7 - 1, (.6, -.1, 2.9))])
keys(cap, 'location', [(s7, (0, 0, 2.38))])

# ---------- scene dressing ----------
tb = b3d.prim('cube', [table_m], size=1, location=(0, 0, -.15)); tb.scale = (6, 4, .3)
wl = b3d.prim('cube', [wall_m], size=1, location=(0, 2.2, 2)); wl.scale = (10, .2, 6)

# ---------- dissolved CO2 (dim dots on the cut face) and bubbles in shot 6 ----------
B0 = s6; B1 = e6
dots = []
for k in range(70):
    while True:
        x = rnd.uniform(-.38, .38); z = rnd.uniform(.12, 1.75)
        rr = .38 if z < 1.3 else .38 - (z - 1.3) * .5
        if abs(x) < rr - .03: break
    d = ball(co2_dim, .018, (x, -.012, z)); dots.append(d)
    t0 = B0 + rnd.randint(0, int((B1 - B0) * .55)); t1 = t0 + rnd.randint(25, 45)
    keys(d, 'scale', [(t0, (1, 1, 1)), (t0 + 8, (2.4, 2.4, 2.4))])
    keys(d, 'location', [(t0, (x, -.012, z)), (t1, (x * .7, -.03, 1.82))])
    b3d.visible(d, [(s3, min(t1, s7))])
# head-space gas: bright, jittering under pressure; shoots out of the neck in shot 5
heads = []
for k in range(16):
    hx, hz = rnd.uniform(-.12, .12), rnd.uniform(1.9, 2.25)
    g = ball(co2, .035, (hx, -.03, hz)); heads.append(g)
    kf = []
    for f in range(s3, OPEN, 3): kf.append((f, (hx + rnd.uniform(-.03, .03), -.03, hz + rnd.uniform(-.03, .03))))
    ang = rnd.uniform(-1, 1)
    t0 = OPEN + k
    kf += [(t0, (hx * .5, -.03, 2.2)), (t0 + 14, (ang * .5, -.1, 3.0 + rnd.uniform(0, .4)))]
    keys(g, 'location', kf)
    keys(g, 'scale', [(t0, (1, 1, 1)), (t0 + 14, (2.2, 2.2, 2.2))])
    b3d.visible(g, [(s3, min(t0 + 14, e5))])
# foam on the surface in shot 6
for k in range(26):
    x = rnd.uniform(-.3, .3)
    f_ = ball(bub, .04 + rnd.uniform(0, .03), (x, -.04, 1.86 + rnd.uniform(0, .05)))
    t = B0 + int((B1 - B0) * .35) + rnd.randint(0, 30)
    keys(f_, 'scale', [(t, (.1, .1, .1)), (t + 10, (1, 1, 1))])
    keys(f_, 'location', [(t, (x, -.04, 1.86)), (B1, (x * 1.1, -.04, 1.95 + rnd.uniform(0, .25)))])
    b3d.visible(f_, [(t, s7)])
# pressure arrows in shot 3 (pushing gas into water) and escape arrows in shot 5
pa = [b3d.arrow(f'P{k}', (x, -.08, 2.25), (x, -.08, 1.95), press_m, .018) for k, x in enumerate((-.08, .08))]
for a in pa: b3d.visible(a, [(s3, e3)])
ea = [b3d.arrow(f'E{k}', (x, -.1, 2.35), (x * 3, -.1, 2.95), arrow_m, .02) for k, x in enumerate((-.1, 0., .1))]
for a in ea: b3d.visible(a, [(OPEN, e5)])

# ---------- lights ----------
b3d.light('AREA', 'Key', (3, -4, 4), 420, (1, .95, .88), 5, rot=(50, 0, 35))
b3d.light('AREA', 'Fill', (-3, -3.5, 2), 200, (.62, .74, 1), 4, rot=(70, 0, -40))
b3d.light('POINT', 'Rim', (0, .6, 3.2), 40, (.7, .9, 1), .5)

# ---------- timeline ----------
cam, tgt = b3d.camera(30)
b3d.shot(cam, tgt, s1, e1, (1.0, -4.3, 1.9), (.7, -3.8, 1.8), (0, 0, 1.2))
b3d.shot(cam, tgt, s2, e2, (.5, -1.7, 2.5), (.35, -1.5, 2.4), (0, 0, 2.2))
b3d.shot(cam, tgt, s3, e3, (.3, -3.4, 2.1), (.2, -3.0, 2.05), (0, 0, 1.75))
b3d.shot(cam, tgt, s4, e4, (.2, -2.3, 1.1), (.1, -2.0, 1.1), (0, 0, 1.0))
b3d.shot(cam, tgt, s5, e5, (.4, -3.6, 2.4), (.3, -3.9, 2.5), (0, 0, 2.15))
b3d.shot(cam, tgt, s6, e6, (.3, -2.6, 1.3), (.2, -2.9, 1.45), (0, 0, 1.35))
b3d.shot(cam, tgt, s7, e7, (.7, -3.8, 1.8), (1.0, -5.0, 2.1), (0, 0, 1.2))
b3d.render(OUT, cfg.get('frames'))
