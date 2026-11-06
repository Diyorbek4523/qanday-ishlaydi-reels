"""Induksion plita: black glass hob with a steel pot. Shot 2 the glass goes clear and shows the flat copper coil and its pulsing
magnetic loops; shot 3 the pot is cut open: swirling currents in its iron base, base glows, water bubbles. Shot 4: an ice cube on the
glass inside the same field stays cold. Shot 5 (silent): pot boils hard, ice still there. Shot 6: pull back. 6 shots."""
import bmesh, math, os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.04, .05, .1), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6) = list(zip(S[:-1], S[1:]))

# ---------- materials ----------
wood = b3d.mat('Counter', (.32, .18, .09), .6, bump=.2)
wall = b3d.mat('Wall', (.1, .13, .2), .85)
glass = b3d.mat('Glass', (.015, .015, .02), .08, metal=.1)
clear = b3d.mat('Clear', (.1, .14, .2), .05)
b3d.bsdf(clear).inputs['Alpha'].default_value = .18
for m in (clear,):
    try: m.surface_render_method = 'BLENDED'
    except (AttributeError, TypeError): pass
ring_m = b3d.mat('Ring', (.6, .6, .65), .4, emit=(.7, .7, .75), estr=.6)
body_m = b3d.mat('Body', (.12, .12, .14), .5, metal=.3)
copper = b3d.mat('Copper', (.95, .45, .2), .25, metal=.6, emit=(1, .45, .15), estr=.8)
steel = b3d.mat('Steel', (.75, .77, .8), .22, metal=.85)
steel_in = b3d.mat('SteelIn', (.45, .47, .52), .35, metal=.7)
base_m = b3d.mat('PanBase', (.35, .36, .4), .35, metal=.8, emit=(1, .2, .03), estr=0)
handle_m = b3d.mat('Handle', (.06, .06, .07), .4)
water = b3d.mat('Water', (.2, .55, .95), .1, emit=(.05, .3, .75), estr=.4)
b3d.bsdf(water).inputs['Alpha'].default_value = .6
try: water.surface_render_method = 'BLENDED'
except (AttributeError, TypeError): pass
field_m = b3d.mat('Field', (.3, .9, 1), .4, emit=(.25, .85, 1), estr=2.5)
cur_m = b3d.mat('Current', (1, .85, .2), .3, emit=(1, .8, .15), estr=4)
bubble = b3d.mat('Bubble', (.8, .92, 1), .1, emit=(.6, .85, 1), estr=1.2)
steam = b3d.mat('Steam', (.92, .95, 1), .5, emit=(.8, .9, 1), estr=.8)
b3d.bsdf(steam).inputs['Alpha'].default_value = .5
try: steam.surface_render_method = 'BLENDED'
except (AttributeError, TypeError): pass
ice_m = b3d.mat('Ice', (.75, .9, 1), .05, emit=(.4, .7, 1), estr=.35)
b3d.bsdf(ice_m).inputs['Alpha'].default_value = .75
try: ice_m.surface_render_method = 'BLENDED'
except (AttributeError, TypeError): pass
led = b3d.mat('Led', (1, .3, .1), .3, emit=(1, .3, .08), estr=3)
def box(m, c, s, bevel=0):
    b = b3d.prim('cube', [m], size=1, location=c); b.scale = s
    if bevel:
        bv = b.modifiers.new('Bv', 'BEVEL'); bv.width = bevel; bv.segments = 4; b3d.smooth(b)
    return b
def half(ob):
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, 0), plane_no=(0, 1, 0), clear_outer=False, clear_inner=True)
    bm.to_mesh(ob.data); bm.free(); return ob
def curve(name, pts, m, r=.03, cyclic=False):
    cv = bpy.data.curves.new(name, 'CURVE'); cv.dimensions = '3D'; cv.bevel_depth = r; cv.bevel_resolution = 3; cv.use_fill_caps = True
    sp = cv.splines.new('POLY'); sp.points.add(len(pts) - 1); sp.use_cyclic_u = cyclic
    for bp, p in zip(sp.points, pts): bp.co = (*p, 1)
    cv.materials.append(m); return b3d.link(bpy.data.objects.new(name, cv))
def ease(u): u = min(1, max(0, u)); return u * u * (3 - 2 * u)

# ---------- room + hob ----------
box(wood, (0, 0, -.9), (30, 20, .6))
b3d.prim('plane', [wall], size=60, location=(0, 7, 20), rotation=(math.radians(90), 0, 0))
top_dark = box(glass, (0, 0, -.05), (7.2, 5.4, .1), bevel=.04)
top_clear = box(clear, (0, 0, -.05), (7.2, 5.4, .1))
body = box(body_m, (0, 0, -.62), (7.0, 5.2, .02))       # floor of the hob body (inside is open, seen through clear glass)
for x, sx in ((-3.55, .1), (3.55, .1)): box(body_m, (x, 0, -.35), (sx, 5.3, .55))
box(body_m, (0, 2.65, -.35), (7.2, .1, .55))
front_w = box(body_m, (0, -2.65, -.35), (7.2, .1, .55))
ring = b3d.prim('torus', [ring_m], major_radius=1.75, minor_radius=.015, major_segments=96, minor_segments=6, location=(0, 0, .002))
ring2 = b3d.prim('torus', [ring_m], major_radius=1.05, minor_radius=.012, major_segments=72, minor_segments=6, location=(2.6, .9, .002))
b3d.smooth(b3d.prim('uv_sphere', [led], segments=12, ring_count=8, radius=.05, location=(0, -2.3, .01))).scale = (1, 1, .4)
# flat copper coil
pts = []
for i in range(9 * 48 + 1):
    t = i / 48; r = .3 + 1.35 * t / 9; a = 2 * math.pi * t; pts.append((r * math.cos(a), r * math.sin(a), -.32))
coil = curve('Coil', pts, copper, r=.055)
# ---------- pot ----------
PO = [(1.5, .0), (1.52, .08), (1.52, 1.35), (1.58, 1.4)]
PI = [(1.44, .14), (1.44, 1.38)]
def pot(name, cut, m):
    ob = b3d.lathe(name, [(.001, .14)] + list(reversed(PI)) + list(reversed(PO))[0:1] + PO[::-1][1:] + [(.001, .12)])
    if cut: half(ob)
    ob.data.materials.append(m); return ob
pot_back = half(b3d.lathe('PotBack', [(.001, .16), (1.44, .16), (1.44, 1.38), (1.58, 1.4), (1.52, 1.35), (1.52, .16)])); pot_back.data.materials.append(steel_in)
pot_front = b3d.lathe('PotFront', [(.001, .16), (1.44, .16), (1.44, 1.38), (1.58, 1.4), (1.52, 1.35), (1.52, .16)]); pot_front.data.materials.append(steel)
pbase = b3d.lathe('PotBase', [(.001, .0), (1.5, .0), (1.52, .08), (1.52, .16), (.001, .16)]); pbase.data.materials.append(base_m)
pbase_cut = half(b3d.lathe('PotBaseCut', [(.001, .0), (1.5, .0), (1.52, .08), (1.52, .16), (.001, .16)])); pbase_cut.data.materials.append(base_m)
for sx in (-1, 1): box(handle_m, (sx * 1.9, 0, 1.15), (.6, .28, .16), bevel=.06)
wat_full = b3d.lathe('WaterTop', [(.001, 1.05), (1.44, 1.05), (1.44, 1.0), (.001, 1.0)]); wat_full.data.materials.append(water)
wat_cut = half(b3d.lathe('WaterVol', [(.001, .17), (1.43, .17), (1.43, 1.05), (.001, 1.05)])); wat_cut.data.materials.append(water)
HEAT0, HEAT1 = s3 + 10, s3 + 45
b3d.key_input(base_m, 'Emission Strength', [(0, 0.), (HEAT0, 0.), (HEAT1, 2.2), (e3, 2.2), (s4, .5), (N, .5)])
# ---------- magnetic loops: from the coil up through the pot base and back round ----------
loops = []
for k in range(8):
    a = 2 * math.pi * k / 8; c, s_ = math.cos(a), math.sin(a)
    for rc, rx, rz in ((.95, .55, .75), (1.0, .85, 1.05)):
        lp = [((rc + rx * math.cos(t)) * c, (rc + rx * math.cos(t)) * s_, -.3 + rz * math.sin(t) * (1 if math.sin(t) > 0 else .2))
              for t in [2 * math.pi * i / 40 for i in range(40)]]
        L = curve(f'Loop{k}_{rc}', lp, field_m, r=.02, cyclic=True); loops.append(L)
b3d.key_input(field_m, 'Emission Strength', [(f, 3.2 if (f // 6) % 2 else 1.0) for f in range(0, N, 6)])
for L in loops: b3d.visible(L, [(s2 + 8, e4)])
# extra loops through the ice cube (shot 4)
ICE = (2.6, .9)
for k in range(3):
    lp = [(ICE[0] + .5 * math.cos(t) - .1 + .1 * k, ICE[1] + (k - 1) * .25, -.3 + .95 * math.sin(t) * (1 if math.sin(t) > 0 else .2)) for t in [2 * math.pi * i / 40 for i in range(40)]]
    b3d.visible(curve(f'IceLoop{k}', lp, field_m, r=.018, cyclic=True), [(s4, e4)])
coil2 = curve('Coil2', [((.3 + .75 * t / 6) * math.cos(2 * math.pi * t) + ICE[0], (.3 + .75 * t / 6) * math.sin(2 * math.pi * t) + ICE[1], -.32)
                         for t in [i / 48 for i in range(6 * 48 + 1)]], copper, r=.045)
ice = box(ice_m, (ICE[0], ICE[1], .3), (.6, .6, .6), bevel=.1)
ice.rotation_euler = (0, 0, math.radians(20))
# ---------- swirling currents in the base (shot 3) ----------
for k in range(36):
    rr = random.Random(k); r = rr.uniform(.35, 1.35); ph = rr.random(); w = rr.choice((1, 1, -1))
    b = b3d.smooth(b3d.prim('uv_sphere', [cur_m], segments=8, ring_count=5, radius=.045))
    for f in range(s3, e3 + 2, 2):
        a = w * (ph * 2 * math.pi + (f - s3) * .12); b.location = (r * math.cos(a), r * math.sin(a), .085); b.keyframe_insert('location', frame=f)
    b3d.visible(b, [(s3 + 6, e3)])
# ---------- bubbles + steam once it heats ----------
BUB0 = HEAT1
for k in range(40):
    rr = random.Random(k + 100); x0 = rr.uniform(-1.2, 1.2); y0 = rr.uniform(.05, .6); ph = rr.random(); sp_ = rr.uniform(12, 22)
    b = b3d.smooth(b3d.prim('uv_sphere', [bubble], segments=10, ring_count=6, radius=rr.uniform(.04, .09)))
    for f in range(BUB0 - 2, N, 2):
        u = (ph + f / sp_) % 1; b.location = (x0 + .05 * math.sin(f * .4 + k), y0, .2 + u * .82); b.keyframe_insert('location', frame=f)
    b3d.visible(b, [(BUB0, e3)])
for k in range(26):
    rr = random.Random(k + 200); x0 = rr.uniform(-1.1, 1.1); y0 = rr.uniform(-1.1, 1.1); ph = rr.random()
    b = b3d.smooth(b3d.prim('uv_sphere', [steam], segments=10, ring_count=6, radius=rr.uniform(.04, .08)))
    for f in range(s4 - 2, N, 2):
        u = (ph + f / 34) % 1; b.location = (x0 * (1 - .3 * u), y0 * (1 - .3 * u), 1.1 + u * 1.6); b.keyframe_insert('location', frame=f)
    b3d.visible(b, [(s4, N)])

# ---------- which parts show ----------
b3d.visible(top_dark, [(s1, e1), (s4, N)])
b3d.visible(top_clear, [(s2, e3)])
b3d.visible(front_w, [(s1, e1), (s4, N)])
b3d.visible(pot_front, [(s1, e2), (s4, N)]); b3d.visible(pbase, [(s1, e2), (s4, N)])
b3d.visible(pbase_cut, [(s3, e3)]); b3d.visible(pot_back, [(s3, e3)]); b3d.visible(wat_cut, [(s3, e3)])
b3d.visible(wat_full, [(s1, e2), (s4, N)])
b3d.visible(coil, [(s2, e3)])
b3d.visible(coil2, [(s4, e4)])

# ---------- lights ----------
b3d.light('AREA', 'Key', (5, -8, 9), 800, (1, .95, .88), 8, rot=(40, 0, 25))
b3d.light('AREA', 'Fill', (-6, -7, 4), 300, (.62, .74, 1), 6, rot=(70, 0, -40))
b3d.light('POINT', 'Under', (0, -1.5, -.15), 60, (1, .8, .6), 1)

# ---------- timeline ----------
cam, tgt = b3d.camera(30)
b3d.shot(cam, tgt, s1, e1, (2.6, -8.4, 5.4), (1.9, -7.4, 4.8), (.6, 0, .7), lens=30)
b3d.shot(cam, tgt, s2, e2, (-.6, -5.2, 2.2), (.3, -4.6, 1.8), (0, 0, -.2), lens=30)
b3d.shot(cam, tgt, s3, e3, (.6, -5.0, 1.0), (.3, -4.3, .9), (0, 0, .35), lens=30)
b3d.shot(cam, tgt, s4, e4, (4.4, -3.6, 2.4), (4.0, -3.0, 2.1), (2.3, .7, .3), lens=30)
b3d.shot(cam, tgt, s5, e5, (-1.6, -6.0, 3.6), (-.6, -5.4, 3.2), (1.0, .3, .7), lens=30)
b3d.shot(cam, tgt, s6, e6, (1.9, -7.4, 4.8), (3.0, -11.0, 6.8), (.8, 0, .7), lens=30)
b3d.render(OUT, cfg.get('frames'))
