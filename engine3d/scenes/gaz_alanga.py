"""Gaz alangasi: stove burner with a ring of blue flames; under the cooktop a see-through mixing tube: gas beads from the
nozzle drag air beads in; blue close-up; dirt clogs the holes -> fewer air beads, flames turn tall and yellow;
pot above gets a black sooty bottom and grey smoke; dirt gone, blue again; pull back. 7 shots."""
import math, os, sys, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy
from mathutils import Vector

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.02, .02, .045), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))

top_m = b3d.mat('Top', (.08, .08, .09), .25, metal=.2)
wall_m = b3d.mat('Wall', (.45, .42, .5), .85, bump=.02)
crown_m = b3d.mat('Crown', (.55, .55, .58), .35, metal=.7)
cap_m = b3d.mat('Cap', (.12, .12, .13), .4)
grate_m = b3d.mat('Grate', (.06, .06, .06), .5)
pot_m = b3d.mat('Pot', (.75, .76, .8), .25, metal=.85)
potb_m = b3d.mat('PotBottom', (.75, .76, .8), .3, metal=.85)
dirt_m = b3d.mat('Dirt', (.25, .15, .06), .9, bump=.05)
tube_m = b3d.mat('Tube', (.92, .92, .95), .2)
tb = b3d.bsdf(tube_m); tb.inputs['Alpha'].default_value = .25
try: tube_m.surface_render_method = 'BLENDED'
except Exception: pass
gas_m = b3d.mat('Gas', (1, .85, .2), .3, emit=(1, .8, .15), estr=4)
air_m = b3d.mat('Air', (.6, .85, 1), .3, emit=(.5, .8, 1), estr=4)
smoke_m = b3d.mat('Smoke', (.3, .3, .32), .9)
smb = b3d.bsdf(smoke_m); smb.inputs['Alpha'].default_value = .5
try: smoke_m.surface_render_method = 'BLENDED'
except Exception: pass
BLUE, BLUE_I, YEL, YEL_I = (.04, .22, 1), (.3, .6, 1), (1, .45, .03), (1, .75, .2)
fl_m = b3d.mat('Flame', (0, 0, 0), .5, emit=BLUE, estr=2.2)
fi_m = b3d.mat('FlameIn', (0, 0, 0), .5, emit=BLUE_I, estr=3)

def keys(ob, attr, fv):
    for f, v in fv: setattr(ob, attr, v); ob.keyframe_insert(attr, frame=f)

def box(name, m, loc, dims, bev=0):
    ob = b3d.prim('cube', [m], size=1, location=loc); ob.scale = dims; ob.name = name
    if bev: ob.modifiers.new('bev', 'BEVEL').width = bev
    return ob

def tube(name, pts, r, m):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 4
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for p, c in zip(sp.points, pts): p.co = (*c, 1)
    ob = b3d.link(bpy.data.objects.new(name, cu)); ob.data.materials.append(m); return ob

# yellow phase: clog starts 30% into shot 4, cleared 35% into shot 6
Y0 = s4 + int((e4 - s4) * .3); Y1 = Y0 + 18
B0 = s6 + int((e6 - s6) * .35); B1 = B0 + 18

# ---------- kitchen ----------
b3d.prim('plane', [wall_m], size=14, location=(0, 2.2, 2), rotation=(math.radians(90), 0, 0))
ct = box('Cooktop', top_m, (0, 0, -.03), (3.4, 2.6, .06), .01); b3d.visible(ct, [(0, s2), (e2, e7 + 1)])

# ---------- burner ----------
crown = b3d.lathe('Crown', [(0, -.02), (.42, -.02), (.46, .02), (.46, .1), (.4, .12), (0, .12)]); crown.data.materials.append(crown_m)
cap = b3d.lathe('Cap', [(0, .12), (.4, .12), (.41, .15), (.3, .18), (0, .185)]); cap.data.materials.append(cap_m)
for k in range(4):  # pan support
    a = k * math.pi / 2 + math.pi / 4
    box(f'Grate{k}', grate_m, (.95 * math.cos(a), .95 * math.sin(a), .25), (.08, .08, .5), .01)
    g = box(f'GrateArm{k}', grate_m, (.72 * math.cos(a), .72 * math.sin(a), .48), (.55, .07, .06), .01); g.rotation_euler = (0, 0, a)

# flames: base empties on the ring, cone parented above; height scaled, yellow ones taller and lazier
NF = 22; rnd = random.Random(5); flames = []
for k in range(NF):
    a = 2 * math.pi * k / NF
    e = b3d.empty(f'F{k}', (.47 * math.cos(a), .47 * math.sin(a), .07)); e.rotation_euler = (0, math.radians(28), a)
    o = b3d.prim('cone', [fl_m], vertices=16, radius1=.055, depth=.22, location=(0, 0, 0)); o.parent = e; o.location = (0, 0, .11); b3d.smooth(o)
    i = b3d.prim('cone', [fi_m], vertices=12, radius1=.028, depth=.1, location=(0, 0, 0)); i.parent = e; i.location = (0, 0, .05); b3d.smooth(i)
    o.visible_shadow = i.visible_shadow = False
    flames.append(e)
def tall(f):  # 1 = neat blue, ~2.3 = lazy yellow
    if f < Y0 or f >= B1: return 1.0
    if f < Y1: return 1 + 1.3 * (f - Y0) / (Y1 - Y0)
    if f < B0: return 2.3
    return 2.3 - 1.3 * (f - B0) / (B1 - B0)
for k, e in enumerate(flames):
    for f in range(0, N + 3, 3):
        t = tall(f); w = 1 + (t - 1) * .35
        h = t * (.9 + .2 * rnd.random()) if t > 1.05 else (.95 + .1 * rnd.random())
        e.scale = (w, w, h); e.keyframe_insert('scale', frame=f)
        if t > 1.05:  # yellow flames wobble and lean up
            e.rotation_euler = (rnd.uniform(-.15, .15), math.radians(28 - 18 * (t - 1) / 1.3), 2 * math.pi * k / NF)
        else: e.rotation_euler = (0, math.radians(28), 2 * math.pi * k / NF)
        e.keyframe_insert('rotation_euler', frame=f)
ph = [(0, 0), (Y0, 0), (Y1, 1), (B0, 1), (B1, 0)]
def mix(c0, c1, v): return tuple(a + (b - a) * v for a, b in zip(c0, c1))
b3d.key_input(fl_m, 'Emission Color', [(f, mix(BLUE, YEL, v)) for f, v in ph])
b3d.key_input(fi_m, 'Emission Color', [(f, mix(BLUE_I, YEL_I, v)) for f, v in ph])
b3d.key_input(fl_m, 'Emission Strength', [(0, 2.2), (Y0, 2.2), (Y1, 2), (B0, 2), (B1, 2.2)])
FL = b3d.light('POINT', 'FlameGlow', (0, 0, .35), 60, BLUE, .4)
for f, v in ph:
    FL.data.color = mix(BLUE, (1, .6, .2), v); FL.data.keyframe_insert('color', frame=f)
    FL.data.energy = 60 + 90 * v; FL.data.keyframe_insert('energy', frame=f)

# dirt blobs clogging the crown holes
rd = random.Random(9)
for k in range(14):
    a = 2 * math.pi * k / 14 + rd.uniform(-.1, .1)
    d = b3d.smooth(b3d.prim('uv_sphere', [dirt_m], radius=rd.uniform(.03, .05), segments=12, ring_count=8,
                             location=(.46 * math.cos(a), .46 * math.sin(a), .06)))
    d.scale = (1, 1, .7); b3d.visible(d, [(Y0 - 6, B0)])

# ---------- under the cooktop: nozzle + see-through mixing tube ----------
NX = -2.1
box('NozzleBody', crown_m, (NX - .25, 0, -.5), (.3, .2, .2), .02)
b3d.prim('cone', [crown_m], vertices=20, radius1=.09, radius2=.03, depth=.15, location=(NX - .03, 0, -.5), rotation=(0, math.radians(90), 0))
tpath = [(NX + .1, 0, -.5), (-.25, 0, -.5), (-.05, 0, -.42), (0, 0, -.25), (0, 0, -.04)]
tube('MixTube', tpath, .12, tube_m)
gpath = [Vector((NX, 0, -.5))] + [Vector(p) for p in tpath[1:]] + [Vector((0, 0, .1))]
apath = [Vector((NX + .25, 0, -.12)), Vector((NX + .3, 0, -.45))] + [Vector(p) for p in tpath[1:]] + [Vector((0, 0, .1))]
def mk(path):
    seg = [(path[k + 1] - path[k]).length for k in range(len(path) - 1)]; tot = sum(seg)
    def at(d):
        d %= tot
        for k, s in enumerate(seg):
            if d <= s: return path[k].lerp(path[k + 1], d / s)
            d -= s
        return path[-1]
    return at, tot
UL = b3d.light('POINT', 'UnderLight', (-1.0, -1.2, -.7), 80, (1, .9, .8), .5)
for path, m, nb, half in ((gpath, gas_m, 22, False), (apath, air_m, 22, True)):
    at, tot = mk(path)
    for k in range(nb):
        bd = b3d.prim('uv_sphere', [m], radius=.03, segments=10, ring_count=6, location=(0, 0, 0)); bd.visible_shadow = False
        dist = k * tot / nb
        for f in range(s2, e3, 2):
            dist += .05; bd.location = at(dist); bd.keyframe_insert('location', frame=f)
        b3d.visible(bd, [(s2, e3)])

# ---------- pot (shots 5-7): bottom blackens with soot, grey smoke ----------
pot = b3d.lathe('Pot', [(0, .55), (.78, .55), (.82, .6), (.82, 1.25), (.86, 1.28), (.78, 1.28), (.76, .62), (0, .62)]); pot.data.materials.append(pot_m)
potb = b3d.lathe('PotBottom', [(0, .545), (.8, .545), (.82, .6), (.83, .7), (0, .7)]); potb.data.materials.append(potb_m)
for o in (pot, potb): b3d.visible(o, [(s5, e7 + 1)])
b3d.key_input(potb_m, 'Base Color', [(0, (.75, .76, .8)), (s5, (.55, .55, .57)), (e5, (.03, .03, .03))])
b3d.key_input(potb_m, 'Metallic', [(0, .85), (s5, .6), (e5, .05)])
b3d.key_input(potb_m, 'Roughness', [(0, .3), (s5, .5), (e5, .95)])
rs = random.Random(3)
for k in range(18):
    p = b3d.smooth(b3d.prim('uv_sphere', [smoke_m], radius=.06, segments=12, ring_count=8, location=(0, 0, 0))); p.visible_shadow = False
    a = rs.uniform(0, 2 * math.pi); x0, y0 = .86 * math.cos(a), .86 * math.sin(a)
    t0 = s5 + rs.randint(0, max(1, e5 - s5 - 20))
    keys(p, 'location', [(t0, (x0, y0, .6)), (t0 + 45, (x0 * 1.25, y0 * 1.25, 1.9))])
    keys(p, 'scale', [(t0, (.5, .5, .5)), (t0 + 45, (3, 3, 3))])
    b3d.visible(p, [(t0, min(t0 + 45, s6 + 15))])

b3d.light('AREA', 'Key', (-1.5, -2.5, 3.0), 160, (1, .88, .75), 3, rot=(50, 0, -25))
b3d.light('AREA', 'Fill', (2.2, -2.0, 1.5), 60, (.6, .7, 1), 3, rot=(65, 0, 45))

# ---------- camera ----------
cam, tgt = b3d.camera(35)
b3d.shot(cam, tgt, s1, e1, (0, -3.0, 1.7), (0, -2.6, 1.45), (0, 0, .2), lens=35)
b3d.shot(cam, tgt, s2, e2, (-2.0, -1.75, .15), (-1.6, -1.6, .08), (-1.75, 0, -.42), (-1.45, 0, -.42), lens=35)
b3d.shot(cam, tgt, s3, e3, (-.2, -1.35, .55), (.15, -1.25, .5), (0, 0, .18), lens=40)
b3d.shot(cam, tgt, s4, e4, (.45, -1.4, .75), (.3, -1.3, .7), (0, 0, .3), lens=40)
b3d.shot(cam, tgt, s5, e5, (.7, -2.9, .42), (.5, -2.6, .4), (0, 0, .5), lens=35)
b3d.shot(cam, tgt, s6, e6, (-.4, -2.1, 1.3), (-.1, -1.95, 1.2), (0, 0, .35), lens=35)
b3d.shot(cam, tgt, s7, e7, (0, -2.4, 1.6), (0, -4.6, 2.6), (0, 0, .5), lens=35)

b3d.render(OUT, cfg.get('frames'))
