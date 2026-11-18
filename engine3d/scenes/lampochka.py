"""Lampochka: a hanging incandescent bulb. Switch-on flash and pop; close-up of the glowing tungsten coil; cold switch-on
with a rush of current beads; years of evaporation (particles fly to the glass, dark patch grows); the thin spot glows
white, snaps with sparks; bulb goes dark, camera pulls back. 7 shots."""
import math, os, sys, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy
from mathutils import Vector

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.02, .02, .04), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))

wall_m = b3d.mat('Wall', (.45, .38, .5), .8, bump=.02)
ceil_m = b3d.mat('Ceil', (.5, .48, .52), .8)
cord_m = b3d.mat('Cord', (.1, .1, .12), .5)
brass = b3d.mat('Brass', (.85, .65, .3), .3, metal=.8)
socket_m = b3d.mat('Socket', (.15, .15, .18), .4)
glass = b3d.mat('Glass', (.35, .38, .45), .25)
gb = b3d.bsdf(glass); gb.inputs['Alpha'].default_value = .09
try: glass.surface_render_method = 'BLENDED'
except Exception: pass
lead_m = b3d.mat('Lead', (.75, .5, .3), .3, metal=.8)
fil_m = b3d.mat('Fil', (.3, .3, .32), .4, metal=.6, emit=(1, .45, .12), estr=0)
mid_m = b3d.mat('FilMid', (.3, .3, .32), .4, metal=.6, emit=(1, .45, .12), estr=0)
bead_m = b3d.mat('Bead', (1, .85, .2), .3, emit=(1, .8, .15), estr=5)
vap_m = b3d.mat('Vapor', (.25, .25, .3), .5, emit=(.6, .6, .7), estr=.6)
spot_m = b3d.mat('Spot', (.05, .04, .04), .6)
sb = b3d.bsdf(spot_m); sb.inputs['Alpha'].default_value = 0
try: spot_m.surface_render_method = 'BLENDED'
except Exception: pass
spark_m = b3d.mat('Spark', (1, .8, .4), .3, emit=(1, .75, .3), estr=6)

def keys(ob, attr, fv):
    for f, v in fv: setattr(ob, attr, v); ob.keyframe_insert(attr, frame=f)

# ---------- room ----------
b3d.prim('plane', [wall_m], size=12, location=(0, 1.6, 1.5), rotation=(math.radians(90), 0, 0))
b3d.prim('plane', [ceil_m], size=12, location=(0, 0, 2.9))
b3d.smooth(b3d.prim('cylinder', [cord_m], vertices=16, radius=.012, depth=.36, location=(0, 0, 2.72)))

# ---------- bulb (built upright at local origin, then hung upside down) ----------
root = b3d.empty('Root', (0, 0, 2.2)); root.rotation_euler = (math.pi, 0, 0)
def par(o): o.parent = root; return o
g = b3d.lathe('Glass', [(.09, -.05), (.1, .05), (.16, .15), (.27, .3), (.3, .42), (.27, .55), (.16, .63), (.05, .66), (0, .662)])
g.data.materials.append(glass); par(g)
g.visible_shadow = False
base = par(b3d.smooth(b3d.prim('cylinder', [brass], vertices=40, radius=.1, depth=.28, location=(0, 0, -.19))))
for i in range(5): par(b3d.smooth(b3d.prim('torus', [brass], major_radius=.1, minor_radius=.012, location=(0, 0, -.08 - i * .055))))
par(b3d.smooth(b3d.prim('cylinder', [socket_m], vertices=40, radius=.13, depth=.22, location=(0, 0, -.4))))
stem = par(b3d.smooth(b3d.prim('cylinder', [glass], vertices=24, radius=.025, depth=.25, location=(0, 0, .07))))

FZ, FX = .36, .08
def tube(name, pts, m, r):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 3
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for p, c in zip(sp.points, pts): p.co = (*c, 1)
    ob = b3d.link(bpy.data.objects.new(name, cu)); ob.data.materials.append(m); return par(ob)
LEADL = [(-.02, 0, .15), (-FX, 0, .26), (-FX, 0, FZ)]
LEADR = [(.02, 0, .15), (FX, 0, .26), (FX, 0, FZ)]
tube('LeadL', [(-.02, 0, -.05)] + LEADL, lead_m, .006); tube('LeadR', [(.02, 0, -.05)] + LEADR, lead_m, .006)
def helix(x0, x1, n=90, turns=None):
    turns = turns or (x1 - x0) / .011
    return [(x0 + (x1 - x0) * i / n, .013 * math.cos(2 * math.pi * turns * i / n), FZ + .013 * math.sin(2 * math.pi * turns * i / n)) for i in range(n + 1)]
fl = tube('FilL', helix(-FX, -.018, 60), fil_m, .0032)
fr = tube('FilR', helix(.018, FX, 60), fil_m, .0032)
fm = tube('FilM', helix(-.018, .018, 30), mid_m, .0019)

P = s1 + int((e1 - s1) * .62)
BRK = s6 + int((e6 - s6) * .35)
# filament glow
for m in (fil_m, mid_m):
    b3d.key_input(m, 'Emission Strength', [(0, 4), (P - 8, 4), (P, 9), (P + 2, 0), (s2, 4), (e2 - 1, 4),
                                           (s3, .3), (s3 + int((e3 - s3) * .7), 3), (s4, 3), (e5 - 1, 3) if m is fil_m else (e5 - 1, 14),
                                           (BRK - 1, 3 if m is fil_m else 14), (BRK + 3, 0), (e7 - 1, 0)])
b3d.key_input(mid_m, 'Emission Color', [(s5, (1, .45, .12)), (s5 + 25, (1, .95, .85)), (BRK, (1, .95, .85))])
b3d.visible(fm, [(0, BRK)])

# light
L = b3d.light('POINT', 'BulbLight', (0, 0, 2.2 - FZ), 0, (1, .7, .4), .05)
for f, v in [(0, 60), (P - 8, 60), (P, 200), (P + 2, 0), (s2, 25), (e2 - 1, 25), (s3, 4),
             (s3 + int((e3 - s3) * .7), 40), (s4, 50), (e5 - 1, 30), (BRK - 1, 30), (BRK + 1, 150), (BRK + 4, 0), (e7 - 1, 0)]:
    L.data.energy = v; L.data.keyframe_insert('energy', frame=f)
b3d.light('AREA', 'Fill', (1.5, -2.5, 1.0), 60, (.6, .7, 1), 2.5, rot=(70, 0, 30))

def W(p):  # local (upright) -> world (hung)
    return Vector((p[0], -p[1], 2.2 - p[2]))

# current beads (shot 3): up the left lead, across the coil, down the right lead
path = [W(p) for p in [(-.02, 0, -.05)] + LEADL + [(0, 0, FZ + .02)] + list(reversed(LEADR)) + [(.02, 0, -.05)]]
seg = [(path[i + 1] - path[i]).length for i in range(len(path) - 1)]; TOT = sum(seg)
def at(d):
    d %= TOT
    for i, s in enumerate(seg):
        if d <= s: return path[i].lerp(path[i + 1], d / s)
        d -= s
    return path[-1]
NB = 14
for k in range(NB):
    b = b3d.prim('uv_sphere', [bead_m], radius=.009, segments=12, ring_count=8, location=(0, 0, 0))
    for f in range(s3, e3, 2):
        sp = .045 * (1 + 2.0 * max(0, 1 - (f - s3) / max(1, (e3 - s3) * .6)))  # fast at switch-on, then slower
        b.location = at(k * TOT / NB + sp * (f - s3)); b.keyframe_insert('location', frame=f)
    b3d.visible(b, [(s3, e3)])

# evaporation (shot 4): particles from coil to glass dome
rnd = random.Random(3)
for k in range(26):
    p = b3d.prim('uv_sphere', [vap_m], radius=.006, segments=8, ring_count=6, location=(0, 0, 0))
    a = rnd.uniform(0, 2 * math.pi); el = rnd.uniform(.15, 1.2)
    src = W((rnd.uniform(-FX, FX), 0, FZ)); dst = W((.27 * math.cos(a) * math.cos(el), .27 * math.sin(a) * math.cos(el), .42 + .22 * math.sin(el)))
    t0 = s4 + rnd.randint(0, max(1, (e4 - s4) - 30))
    keys(p, 'location', [(s4, src), (t0, src), (t0 + 28, dst), (e4 - 1, dst)])
    b3d.visible(p, [(t0, e4)])
spot = b3d.smooth(b3d.prim('uv_sphere', [spot_m], radius=.17, location=W((0, 0, .6))))
spot.scale = (1, 1, .3); spot.visible_shadow = False
stem.visible_shadow = False
b3d.key_input(spot_m, 'Alpha', [(0, 0), (s4 + 10, 0), (e4 - 5, .55), (e7 - 1, .55)])

# sparks at the break
for k in range(12):
    s = b3d.prim('uv_sphere', [spark_m], radius=.005, segments=8, ring_count=6, location=W((0, 0, FZ)))
    d = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))).normalized() * rnd.uniform(.06, .16)
    keys(s, 'location', [(BRK, W((0, 0, FZ))), (BRK + 14, W((0, 0, FZ)) + d)])
    keys(s, 'scale', [(BRK, (1, 1, 1)), (BRK + 14, (.1, .1, .1))])
    b3d.visible(s, [(BRK, BRK + 15)])

# ---------- camera ----------
cam, tgt = b3d.camera(35)
F = Vector((0, 0, 2.2 - FZ))
b3d.shot(cam, tgt, s1, e1, (0, -2.6, 1.45), (0, -2.0, 1.6), (0, 0, 1.85), lens=35)
b3d.shot(cam, tgt, s2, e2, (.12, -.5, 1.8), (.04, -.4, 1.83), F, lens=50)
b3d.shot(cam, tgt, s3, e3, (-.3, -.75, 1.75), (.2, -.75, 1.8), (0, 0, 2.02), lens=40)
b3d.shot(cam, tgt, s4, e4, (.55, -.85, 1.45), (.4, -.75, 1.5), (0, 0, 1.72), lens=35)
b3d.shot(cam, tgt, s5, e5, (.04, -.5, 1.84), (0, -.42, 1.84), F, lens=80)
b3d.shot(cam, tgt, s6, e6, (0, -.45, 1.86), (0, -.6, 1.86), F, lens=50)
b3d.shot(cam, tgt, s7, e7, (0, -1.4, 1.6), (0, -3.0, 1.35), (0, 0, 1.95), lens=35)

b3d.render(OUT, cfg.get('frames'))
