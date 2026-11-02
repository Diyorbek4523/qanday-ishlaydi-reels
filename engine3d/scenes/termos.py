"""Termos: cutaway of a vacuum flask. Double wall with an empty gap (no particles carry heat across) and a mirror wall that sends
radiated heat back into the tea. Half-lathes give a clean cut face at y = 0. 5 shots."""
import bmesh, math, os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.04, .06, .12), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5) = list(zip(S[:-1], S[1:]))

# ---------- materials ----------
paint = b3d.mat('Paint', (.05, .32, .36), .35, metal=.4)
steel = b3d.mat('Steel', (.6, .63, .66), .35, metal=.9)
cut_m = b3d.mat('Cut', (.72, .74, .78), .5, metal=.1)
mirror = b3d.mat('Mirror', (.95, .96, .98), .07, metal=1)
mirror_cut = b3d.mat('MirrorCut', (.9, .92, .95), .4, emit=(.8, .85, 1), estr=.5)
gap_back = b3d.mat('GapBack', (.03, .03, .08), .8, emit=(.08, .04, .25), estr=1)
tea = b3d.mat('Tea', (.72, .28, .05), .25, emit=(.8, .3, .04), estr=.35)
tea_top = b3d.mat('TeaTop', (.75, .32, .07), .2)
cork = b3d.mat('Cork', (.45, .3, .16), .8, bump=.2)
cap_m = b3d.mat('Cap', (.08, .08, .09), .4, metal=.3)
cap_cut = b3d.mat('CapCut', (.2, .2, .22), .6)
wood = b3d.mat('Table', (.3, .16, .08), .6, bump=.2)
porcelain = b3d.mat('Cup', (.85, .86, .9), .25)
steam_m = b3d.mat('Steam', (.9, .9, .95), .5, emit=(.8, .8, .85), estr=.3)
b3d.bsdf(steam_m).inputs['Alpha'].default_value = .16
try: steam_m.surface_render_method = 'BLENDED'
except (AttributeError, TypeError): pass
heat = b3d.mat('Heat', (1, .35, .05), .4, emit=(1, .22, .02), estr=2)
ray = b3d.mat('Ray', (1, .1, .03), .4, emit=(1, .08, .02), estr=2.4)
air = b3d.mat('Air', (.55, .7, .95), .4, emit=(.3, .55, 1), estr=1.1)
point_m = b3d.mat('Point', (1, .8, .2), .4, emit=(1, .72, .08), estr=2)
snow = b3d.mat('Snow', (.9, .93, 1), .5, emit=(.8, .85, 1), estr=.8)

def half(name, prof, surf, cut):
    """Spin a closed (r, z) polygon through y > 0 by 180 degrees; the two end caps form the flat cut face at y = 0."""
    bm = bmesh.new(); vs = [bm.verts.new((r, 0, z)) for r, z in prof]; f = bm.faces.new(vs)
    bmesh.ops.spin(bm, geom=vs + list(f.edges) + [f], cent=(0, 0, 0), axis=(0, 0, 1), angle=math.pi, steps=48, use_merge=False)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = b3d.link(bpy.data.objects.new(name, me)); me.materials.append(surf); me.materials.append(cut)
    for p in me.polygons:
        flat = abs(p.normal.y) > .999 and abs(p.center.y) < 1e-4
        p.material_index = 1 if flat else 0; p.use_smooth = not flat
    return ob
def turned(name, prof, m, parent=None, loc=None):
    ob = b3d.lathe(name, prof); ob.data.materials.append(m)
    if parent: ob.parent = parent
    if loc: ob.location = loc
    return ob

# profiles (r, z)
SHELL = [(.00001, .0), (.62, .0), (.64, .05), (.64, 2.05), (.40, 2.42), (.40, 2.62), (.355, 2.62), (.355, 2.40), (.585, 2.03), (.585, .1), (.00001, .1)]
FLASK = [(.00001, .28), (.40, .28), (.44, .34), (.44, 2.02), (.30, 2.28), (.30, 2.62), (.27, 2.62), (.27, 2.26), (.395, 2.0), (.395, .36), (.36, .32), (.00001, .32)]
TEA = [(.00001, .32), (.36, .32), (.395, .36), (.395, 1.82), (.00001, 1.82)]
PLUG = [(.00001, 2.22), (.22, 2.22), (.265, 2.32), (.265, 2.62), (.00001, 2.62)]
CAP = [(.00001, 2.6), (.42, 2.6), (.47, 2.66), (.47, 3.1), (.42, 3.16), (.00001, 3.16)]

cutaway = b3d.empty('Cutaway')
for nm, pr, sf, ct in (('Shell', SHELL, gap_back, cut_m), ('Flask', FLASK, mirror, mirror_cut), ('Tea', TEA, tea_top, tea), ('Plug', PLUG, cork, cork), ('Cap', CAP, cap_m, cap_cut)):
    half(nm, pr, sf, ct).parent = cutaway

whole = b3d.empty('Whole')
turned('Body', [(.001, 0), (.62, 0), (.64, .05), (.64, 2.05), (.40, 2.42), (.40, 2.62), (.001, 2.62)], paint, whole)
turned('CapW', [(.001, 2.6), (.42, 2.6), (.47, 2.66), (.47, 3.1), (.42, 3.16), (.001, 3.16)], cap_m, whole)
for z in (.25, 1.9): turned(f'Band{z}', [(.645, z), (.655, z + .01), (.655, z + .07), (.645, z + .08)], steel, whole)

# table, cup, steam, snow in the far background
b3d.prim('cube', [wood], size=1, location=(0, 0, -.1)).scale = (12, 8, .2)
CX, CY = 1.25, -.35
cup = turned('Cup', [(.001, 0), (.2, 0), (.3, .32), (.3, .34), (.27, .34), (.18, .05), (.001, .05)], porcelain, loc=(CX, CY, 0))
cup_tea = turned('CupTea', [(.001, .25), (.24, .25), (.24, .27), (.001, .27)], tea, loc=(CX, CY, 0))
r = random.Random(3); steam = []
for k in range(12):
    pf = b3d.smooth(b3d.prim('ico_sphere', [steam_m], subdivisions=2, radius=.11)); steam.append(pf); ph = k / 12; sx = r.uniform(-.08, .08); sy = r.uniform(-.08, .08)
    for f in range(0, N + 1, 6):
        u = ((f / 55) + ph) % 1
        pf.location = (CX + sx + .09 * math.sin(u * 7 + k), CY + sy, .3 + u * 1.5); pf.scale = [(.5 + 2.2 * u) * (1 - u * .5)] * 3
        pf.keyframe_insert('location', frame=f); pf.keyframe_insert('scale', frame=f)
for k in range(60):
    sn = b3d.prim('ico_sphere', [snow], subdivisions=1, radius=r.uniform(.014, .03)); x0, y0, z0, v = r.uniform(-5, 5), r.uniform(4.2, 7), r.uniform(0, 6), r.uniform(.006, .014)
    for f in range(0, N + 1, 12):
        sn.location = (x0 + .2 * math.sin(f * .02 + k), y0, 6 - ((6 - z0) + f * v) % 6); sn.keyframe_insert('location', frame=f)

# ---------- particles ----------
def jitter(m, rad, x0, x1, z0, z1, n, ranges, seed=1, y=-.03):
    rr = random.Random(seed)
    for k in range(n):
        p = b3d.smooth(b3d.prim('uv_sphere', [m], segments=12, ring_count=8, radius=rad)); x, z = rr.uniform(x0, x1), rr.uniform(z0, z1); vx, vz = rr.uniform(-.012, .012), rr.uniform(-.012, .012)
        a, b = ranges
        for f in range(a, b, 2):
            x += vx * 2; z += vz * 2
            if x < x0 or x > x1: vx = -vx; x = min(x1, max(x0, x))
            if z < z0 or z > z1: vz = -vz; z = min(z1, max(z0, z))
            p.location = (x, y, z); p.keyframe_insert('location', frame=f)
        b3d.visible(p, [ranges])
jitter(heat, .026, .02, .375, .5, 1.75, 34, (s3, e3), seed=2)      # hot and busy in the tea
jitter(air, .022, .72, 1.25, .35, 1.8, 16, (s3, e3), seed=5)       # room air outside; none in the gap

# radiated heat: red dots leave the tea, hit the mirror wall at x = .395 and come back
for row, z in enumerate((.55, .85, 1.15, 1.45, 1.72)):
    for k in range(4):
        d = b3d.smooth(b3d.prim('uv_sphere', [ray], segments=12, ring_count=8, radius=.028)); per = 34; off = k * per / 4 + row * 5
        for f in range(s4, e4, 2):
            u = ((f - s4 + off) % per) / per
            if u < .5: x = .03 + .355 * u * 2; dz = u * 2 * .12
            else: x = .385 - .355 * (u - .5) * 2; dz = .12 + (u - .5) * 2 * .12
            d.location = (x, -.03, z - .12 + dz); d.keyframe_insert('location', frame=f)
        b3d.visible(d, [(s4, e4)])

# yellow pointers at the gap (shot 2)
pa = b3d.arrow('PointL', (-1.45, -.05, 1.15), (-.72, -.05, 1.15), point_m, r=.03)
pb = b3d.arrow('PointR', (1.45, -.05, .75), (.72, -.05, .75), point_m, r=.03)
b3d.visible(pa, [(s2 + 18, e2)]); b3d.visible(pb, [(s2 + 18, e2)])

# ---------- lights ----------
b3d.light('AREA', 'Key', (1.5, -4, 4), 260, (1, .93, .85), 4, rot=(55, 0, 20))
b3d.light('AREA', 'Fill', (-3.5, -3, 2), 170, (.6, .72, 1), 3, rot=(70, 0, -50))
b3d.light('POINT', 'Rim', (0, 3, 3), 180, (.7, .8, 1), 1)
b3d.light('POINT', 'TeaGlow', (.2, -1, 1.1), 10, (1, .5, .2), .3)

# ---------- timeline ----------
cam, tgt = b3d.camera(30)
b3d.shot(cam, tgt, s1, e1, (-1.2, -5.4, 1.8), (-.8, -4.5, 1.7), (.25, 0, 1.45), lens=30)        # hook: flask + steaming cup
b3d.shot(cam, tgt, s2, e2, (.5, -5.4, 1.75), (.1, -4.6, 1.65), (0, 0, 1.45), lens=30)           # cutaway
b3d.shot(cam, tgt, s3, e3, (.75, -1.9, 1.15), (.6, -1.6, 1.15), (.55, 0, 1.1), lens=30)         # gap close-up: particles either side, none between
b3d.shot(cam, tgt, s4, e4, (.05, -1.9, 1.2), (.2, -1.6, 1.15), (.28, 0, 1.15), lens=30)         # mirror bounce
b3d.shot(cam, tgt, s5, e5, (-.5, -4.3, 1.6), (-1.2, -7.0, 2.4), (.3, 0, 1.45), lens=30)         # end: outside again
b3d.visible(whole, [(s1, e1), (s5, e5)]); b3d.visible(cutaway, [(s2, e4)])
for o in [cup, cup_tea] + steam: b3d.visible(o, [(s1, e1), (s5, e5)])

b3d.render(OUT, cfg.get('frames'))
