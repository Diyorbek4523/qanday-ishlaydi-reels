"""Changyutgich: an upright vacuum cut in half. The fan throws air out at the top, pressure drops inside, room air pushes itself in at the
floor and carries dust; the filter stops the dust, clean air leaves. Half-lathes give a clean cut face at y = 0. 5 shots."""
import bmesh, math, os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.05, .06, .12), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5) = list(zip(S[:-1], S[1:]))

# ---------- materials ----------
paint = b3d.mat('Paint', (.72, .12, .1), .3, metal=.25)
dark = b3d.mat('Dark', (.05, .05, .06), .45, metal=.3)
steel = b3d.mat('Steel', (.6, .62, .66), .35, metal=.85)
inner = b3d.mat('Inner', (.07, .09, .17), .7, emit=(.04, .06, .16), estr=1)
cut_m = b3d.mat('Cut', (.86, .82, .76), .5)
filt = b3d.mat('Filter', (.92, .9, .78), .9, emit=(.5, .48, .36), estr=.35, bump=.5)
fan_m = b3d.mat('Fan', (1, .55, .08), .35, emit=(1, .42, .03), estr=.8)
coil = b3d.mat('Coil', (.55, .27, .1), .45, metal=.2)
carpet = b3d.mat('Carpet', (.28, .1, .13), .95, bump=.9)
wall = b3d.mat('Wall', (.16, .2, .32), .85)
base = b3d.mat('Base', (.62, .6, .55), .6)
air = b3d.mat('Air', (.08, .2, .4), .35, emit=(.3, .7, 1), estr=1.5)
clean = b3d.mat('Clean', (.1, .4, .25), .35, emit=(.3, 1, .6), estr=1.4)
dust = b3d.mat('Dust', (.42, .3, .2), .9, emit=(.3, .18, .08), estr=.5)
point_m = b3d.mat('Point', (.5, .35, .05), .4, emit=(1, .72, .08), estr=1.5)
cup_m = b3d.mat('CupGlass', (.55, .7, .85), .1)
b3d.bsdf(cup_m).inputs['Alpha'].default_value = .3
try: cup_m.surface_render_method = 'BLENDED'
except (AttributeError, TypeError): pass

def half(name, prof, surf, cut):
    bm = bmesh.new(); vs = [bm.verts.new((r, 0, z)) for r, z in prof]; f = bm.faces.new(vs)
    bmesh.ops.spin(bm, geom=vs + list(f.edges) + [f], cent=(0, 0, 0), axis=(0, 0, 1), angle=math.pi, steps=48, use_merge=False)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = b3d.link(bpy.data.objects.new(name, me)); me.materials.append(surf); me.materials.append(cut)
    for p in me.polygons:
        flat = abs(p.normal.y) > .999 and abs(p.center.y) < 1e-4
        p.material_index = 1 if flat else 0; p.use_smooth = not flat
    return ob
def box(m, c, s, bevel=0):
    b = b3d.prim('cube', [m], size=1, location=c); b.scale = s
    if bevel:
        bv = b.modifiers.new('Bv', 'BEVEL'); bv.width = bevel; bv.segments = 5; b3d.smooth(b)
    return b

# profiles (r, z), z up: floor head .0-.26, tube to 1.8, dust cup to 3.0, filter, fan 3.32, motor to 4.2, exhaust slot 4.26-4.36
TUBE = [(.15, .18), (.2, .18), (.2, 1.78), (.15, 1.78)]
CUPW = [(.15, 1.72), (.2, 1.72), (.72, 1.86), (.78, 1.98), (.78, 3.0), (.72, 3.0), (.72, 2.0), (.68, 1.93), (.15, 1.79)]
UPPER = [(.72, 3.0), (.78, 3.0), (.78, 4.2), (.72, 4.26), (.67, 4.22), (.72, 4.14)]
CAP = [(.0001, 4.36), (.82, 4.36), (.86, 4.42), (.82, 4.52), (.0001, 4.52)]
FILT = [(.0001, 2.86)] + [(.08 + .64 * i / 7, (2.98 if i % 2 else 2.86)) for i in range(8)] + [(.72, 3.0), (.0001, 3.0)]
MOTOR = [(.0001, 3.5), (.36, 3.5), (.4, 3.56), (.4, 4.3), (.36, 4.36), (.0001, 4.36)]
cut = b3d.empty('Cutaway')
for nm, pr, sf, ct in (('Tube', TUBE, inner, cut_m), ('CupW', CUPW, inner, cut_m), ('Upper', UPPER, inner, cut_m), ('Cap', CAP, dark, cut_m), ('Filt', FILT, filt, filt), ('Motor', MOTOR, coil, coil)):
    half(nm, pr, sf, ct).parent = cut
for z in (3.62, 3.76, 3.9, 4.04, 4.18):  # dark winding bands on the motor
    wd = half(f'Wind{z}', [(.0001, z), (.41, z), (.41, z + .07), (.0001, z + .07)], dark, dark); wd.parent = cut; wd.location.y = -.004
box(dark, (0, .25, .13), (2.2, .5, .26)).parent = cut
box(inner, (0, -.02, .13), (1.0, .02, .18)).parent = cut

whole = b3d.empty('Whole')
OUTER = [(.001, 3.0), (.78, 3.0), (.78, 4.2), (.82, 4.36), (.86, 4.42), (.82, 4.52), (.001, 4.52)]
body = b3d.lathe('Body', OUTER); body.data.materials.append(paint); body.parent = whole
cw = b3d.lathe('CupGlass', [(.001, 1.72), (.2, 1.72), (.72, 1.86), (.78, 1.98), (.78, 3.0), (.001, 3.0)]); cw.data.materials.append(cup_m); cw.parent = whole
rr = random.Random(2)
for k in range(30):  # dust already in the see-through cup
    p = b3d.smooth(b3d.prim('ico_sphere', [dust], subdivisions=2, radius=rr.uniform(.07, .13))); a = rr.uniform(0, 6.28); q = rr.uniform(.25, .6); p.location = (q * math.cos(a), q * math.sin(a), 1.98 + rr.uniform(0, .18)); p.parent = whole
for z in (3.5, 3.7, 3.9, 4.1):  # exhaust vents on the red housing
    vt = b3d.lathe(f'Vent{z}', [(.785, z), (.795, z + .01), (.795, z + .05), (.785, z + .06)]); vt.data.materials.append(dark); vt.parent = whole
tube_w = b3d.lathe('TubeW', [(.001, .18), (.2, .18), (.2, 1.78), (.001, 1.78)]); tube_w.data.materials.append(steel); tube_w.parent = whole
band = b3d.lathe('Band', [(.79, 2.96), (.81, 2.98), (.81, 3.06), (.79, 3.08)]); band.data.materials.append(dark); band.parent = whole
box(dark, (0, -.05, .13), (2.2, 1.1, .26), bevel=.08).parent = whole
box(b3d.mat('Strip', (.5, .1, .08), .4, emit=(1, .3, .1), estr=1.2), (0, -.61, .15), (1.7, .02, .05)).parent = whole
for sg in (-1, 1):
    wh = b3d.smooth(b3d.prim('cylinder', [steel], vertices=32, radius=.13, depth=.08, location=(sg * 1.13, .1, .13), rotation=(0, math.radians(90), 0))); wh.parent = whole
# handle: a smooth curve up from the motor housing
cv = bpy.data.curves.new('Handle', 'CURVE'); cv.dimensions = '3D'; cv.bevel_depth = .1; cv.bevel_resolution = 4
sp = cv.splines.new('BEZIER'); sp.bezier_points.add(4)
for bp, p in zip(sp.bezier_points, ((.74, 0, 3.8), (1.4, 0, 4.6), (1.0, 0, 5.45), (.2, 0, 5.3), (0, 0, 4.5))):
    bp.co = p; bp.handle_left_type = bp.handle_right_type = 'AUTO'
cv.materials.append(dark); hand = b3d.link(bpy.data.objects.new('Handle', cv)); hand.parent = whole

# room
b3d.prim('plane', [carpet], size=40, location=(0, 6, 0))
b3d.prim('plane', [wall], size=40, location=(0, 6, 8), rotation=(math.radians(90), 0, 0))
box(base, (0, 5.95, .2), (40, .1, .4))

# fan: spins about Z, a full disc so it stands out of the cut face
fan = b3d.empty('Fan', (0, 0, 3.32))
hub = b3d.smooth(b3d.prim('cylinder', [fan_m], vertices=32, radius=.14, depth=.2)); hub.parent = fan
disc = b3d.prim('cylinder', [fan_m], vertices=48, radius=.62, depth=.03, location=(0, 0, -.09)); disc.parent = fan
for k in range(8):
    a = k * math.pi / 4; bl = box(fan_m, (.38 * math.cos(a), .38 * math.sin(a), 0), (.46, .035, .16)); bl.rotation_euler = (0, 0, a + .5); bl.parent = fan
shaft = b3d.prim('cylinder', [steel], vertices=16, radius=.05, depth=.34, location=(0, 0, .16)); shaft.parent = fan
for f in range(s2, e4, 2):
    fan.rotation_euler = (0, 0, f * .42); fan.keyframe_insert('rotation_euler', index=2, frame=f)

# ---------- flows ----------
def poly(pts):
    d = [0]
    for a, b in zip(pts, pts[1:]): d.append(d[-1] + math.dist(a, b))
    return pts, d
def at(P, u):
    pts, d = P; t = u * d[-1]
    for i in range(len(pts) - 1):
        if t <= d[i + 1] or i == len(pts) - 2:
            k = (t - d[i]) / max(d[i + 1] - d[i], 1e-6); return tuple(a + (b - a) * k for a, b in zip(pts[i], pts[i + 1]))
Y = -.04
def dots(m, n, make, ranges, rad=.032, per=70, seed=1):
    r = random.Random(seed); a, b = ranges
    for k in range(n):
        d = b3d.smooth(b3d.prim('uv_sphere', [m], segments=10, ring_count=6, radius=rad)); P = make(r); ph = k / n
        for f in range(a, b, 2):
            u = (ph + (f - a) / per) % 1; d.location = at(P, u); d.keyframe_insert('location', frame=f)
        b3d.visible(d, [ranges])
def s_of(r): return r.choice((-1, 1))

def out_air(r):     # fan -> round the motor -> out of the slot under the cap
    s = s_of(r); o = r.uniform(.0, .08)
    return poly([(s * .15, Y, 3.2), (s * .5, Y, 3.45), (s * (.52 + o), Y, 4.0), (s * (.56 + o), Y, 4.3), (s * 2.0, Y, 4.42 + o)])
def in_air(r):      # room air -> floor mouth -> up the tube into the cup
    s = s_of(r); x0 = r.uniform(.8, 2.4); z0 = r.uniform(.06, 1.5)
    return poly([(s * x0, Y - r.uniform(0, .6), z0), (s * .85, Y, .1), (s * .1, Y, .1), (s * .04, Y, .3), (s * .04, Y, 1.75), (s * r.uniform(.1, .6), Y, 2.75)])
def dust_in(r):     # floor -> tube -> up to the filter -> falls into the pile
    s = s_of(r); xf = r.uniform(.1, .62)
    return poly([(s * r.uniform(.6, 1.7), Y - r.uniform(0, .8), .05), (s * .1, Y, .1), (s * .04, Y, .3), (s * .04, Y, 1.75), (s * xf, Y, 2.82), (s * xf * 1.02, Y, 2.15)])
def clean_out(r):   # through the filter, fan, motor, slot
    s = s_of(r); x1 = r.uniform(.1, .6); o = r.uniform(0, .08)
    return poly([(s * .04, Y, 1.75), (s * x1, Y, 2.7), (s * x1, Y, 3.1), (s * .5, Y, 3.45), (s * (.52 + o), Y, 4.0), (s * (.56 + o), Y, 4.3), (s * 2.0, Y, 4.42 + o)])

dots(air, 32, out_air, (s2, e2), per=42, seed=2)                        # shot 2: fan throws air out
dots(air, 14, out_air, (s3, e3), per=42, seed=3)
dots(air, 44, in_air, (s3, e3), per=56, seed=4)                         # shot 3: room air pushes itself in
dots(dust, 26, dust_in, (s4, e4), per=60, seed=5, rad=.036)             # shot 4: dust stops at the filter, falls
dots(clean, 26, clean_out, (s4, e4), per=60, seed=6)                    # shot 4: clean air goes on

# dust on the carpet: crumbs lying about, and in the hook dust skating towards the head
r = random.Random(9)
for k in range(46):
    x, y = r.uniform(-3, 3), r.uniform(-2.2, 1.5)
    if abs(x) < .85 and abs(y) < .6: continue
    b3d.prim('ico_sphere', [dust], subdivisions=1, radius=r.uniform(.018, .05), location=(x, y, .02))
for k in range(16):
    d = b3d.smooth(b3d.prim('uv_sphere', [dust], segments=10, ring_count=6, radius=.035)); a0 = r.uniform(0, 6.28); R0 = r.uniform(1.0, 2.0); ph = k / 16
    for f in range(s1, e1, 2):
        u = (ph + (f - s1) / 34) % 1; q = R0 * (1 - u) + .55 * u
        d.location = (q * math.cos(a0), q * .6 * math.sin(a0), .05 + .1 * u); d.scale = [1 - .6 * u] * 3; d.keyframe_insert('location', frame=f); d.keyframe_insert('scale', frame=f)
    b3d.visible(d, [(s1, e1)])

# pile grows in the cup during shot 4
for k in range(60):
    p = b3d.smooth(b3d.prim('ico_sphere', [dust], subdivisions=2, radius=r.uniform(.06, .12)))
    x = r.uniform(.2, .66) * r.choice((-1, 1)); p.location = (x, -.02, 1.98 + r.uniform(0, .05) + (.16 + .1 * r.random()) * (k / 60) * (1.2 - abs(x)))
    g0 = s4 + int((e4 - s4) * .8 * k / 60); p.scale = (.001,) * 3; p.keyframe_insert('scale', frame=g0); p.scale = (1, 1, 1); p.keyframe_insert('scale', frame=g0 + 8)
    b3d.visible(p, [(s4, e4)])

# ---------- pointers: exhaust (shot 2), room air (shot 3) ----------
for nm, a, b, rg in (('OutL', (-.92, -.05, 4.5), (-1.3, -.05, 4.72), (s2, e2)), ('OutR', (.92, -.05, 4.5), (1.3, -.05, 4.72), (s2, e2)),
                     ('InL', (-2.4, -.05, .95), (-1.3, -.05, .38), (s3, e3)), ('InR', (2.4, -.05, .95), (1.3, -.05, .38), (s3, e3))):
    b3d.visible(b3d.arrow(nm, a, b, point_m, r=.042), [rg])

# ---------- lights ----------
b3d.light('AREA', 'Key', (3, -5, 7), 340, (1, .93, .85), 6, rot=(40, 0, 25))
b3d.light('AREA', 'Fill', (-5, -4, 3), 170, (.6, .72, 1), 4, rot=(70, 0, -50))
b3d.light('POINT', 'Rim', (0, 4, 5), 150, (.7, .8, 1), 1.5)

# ---------- timeline ----------
cam, tgt = b3d.camera(30)
b3d.shot(cam, tgt, s1, e1, (2.4, -8.0, 3.8), (1.9, -7.0, 3.3), (.1, 0, 2.75), lens=30)   # hook: vacuum on the carpet, dust skating in
b3d.shot(cam, tgt, s2, e2, (-.7, -4.2, 3.2), (-.5, -3.7, 3.3), (0, 0, 3.75), lens=30)    # cut: fan close-up from below, air out at the top
b3d.shot(cam, tgt, s3, e3, (1.2, -6.6, 2.0), (.7, -5.8, 1.8), (0, 0, 1.55), lens=30)      # room air pushes in at the floor
b3d.shot(cam, tgt, s4, e4, (.9, -5.0, 2.9), (.4, -4.3, 2.9), (0, 0, 2.9), lens=30)        # dust stops, pile grows, clean air leaves
b3d.shot(cam, tgt, s5, e5, (1.2, -7.2, 3.3), (2.6, -9.8, 3.9), (0, 0, 2.75), lens=30)      # end: outside again
b3d.visible(whole, [(s1, e1), (s5, e5)]); b3d.visible(cut, [(s2, e4)]); b3d.visible(fan, [(s2, e4)])

b3d.render(OUT, cfg.get('frames'))
