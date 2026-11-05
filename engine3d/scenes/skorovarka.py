"""Skorovarka: pressure cooker cut in half on a gas ring, with an open pot beside it for shot 2. Sealed lid and rubber ring trap steam; pressure dial
climbs; thermometer goes from 100 to about 120; the valve jiggles and vents. Half-lathes give a cut face at y = 0. 7 shots."""
import bmesh, math, os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.05, .06, .12), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))

# ---------- materials ----------
steel = b3d.mat('Steel', (.78, .8, .84), .3, metal=.35)
inner = b3d.mat('Inner', (.42, .45, .5), .35, metal=.7)
plastic = b3d.mat('Plastic', (.07, .07, .09), .4)
ring_m = b3d.mat('Ring', (.95, .25, .12), .6, emit=(1, .2, .05), estr=.35)
water = b3d.mat('Water', (.25, .55, .9), .12, emit=(.05, .28, .7), estr=.45)
b3d.bsdf(water).inputs['Alpha'].default_value = .55
try: water.surface_render_method = 'BLENDED'
except (AttributeError, TypeError): pass
meat = b3d.mat('Meat', (.55, .14, .1), .55, bump=.25)
bubble = b3d.mat('Bubble', (.8, .92, 1), .1, emit=(.6, .85, 1), estr=1.2)
steam = b3d.mat('Steam', (.92, .95, 1), .5, emit=(.82, .9, 1), estr=2.0)
press = b3d.mat('PressAir', (.95, .55, .25), .5, emit=(1, .5, .15), estr=.0)
b3d.bsdf(press).inputs['Alpha'].default_value = .28
try: press.surface_render_method = 'BLENDED'
except (AttributeError, TypeError): pass
stove = b3d.mat('Stove', (.13, .14, .17), .35, metal=.6)
flame = b3d.mat('Flame', (.05, .2, .9), .5, emit=(.05, .28, 1), estr=1.7)
grate = b3d.mat('Grate', (.05, .05, .06), .5, metal=.5)
valve_m = b3d.mat('Valve', (.92, .65, .12), .3, metal=.9)
tick_m = b3d.mat('Tick', (.9, .9, .92), .4)
glass = b3d.mat('Glass', (.85, .9, .95), .1)
b3d.bsdf(glass).inputs['Alpha'].default_value = .3
try: glass.surface_render_method = 'BLENDED'
except (AttributeError, TypeError): pass
red = b3d.mat('Red', (1, .1, .08), .3, emit=(1, .1, .05), estr=2.2)
wall = b3d.mat('Wall', (.1, .13, .2), .85)
wood = b3d.mat('Table', (.3, .16, .08), .6, bump=.2)
point_m = b3d.mat('Point', (1, .8, .2), .4, emit=(1, .72, .08), estr=2.6)
def box(m, c, s, bevel=0):
    b = b3d.prim('cube', [m], size=1, location=c); b.scale = s
    if bevel:
        bv = b.modifiers.new('Bv', 'BEVEL'); bv.width = bevel; bv.segments = 4; b3d.smooth(b)
    return b
def ease(u): u = min(1, max(0, u)); return u * u * (3 - 2 * u)
def half(ob):
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, 0), plane_no=(0, 1, 0), clear_outer=False, clear_inner=True)
    bm.to_mesh(ob.data); bm.free(); return ob

# ---------- room and stove ----------
box(wood, (0, 0, -.5), (40, 30, 1))
b3d.prim('plane', [wall], size=60, location=(0, 7, 20), rotation=(math.radians(90), 0, 0))
box(stove, (0, 0, .12), (7, 5, .24), bevel=.06)
for a_ in (0, 90):
    g_ = box(grate, (0, 0, .4), (4.3, .14, .2)); g_.rotation_euler = (0, 0, math.radians(a_))
b3d.lathe('Burner', [(.001, .24), (.72, .24), (.72, .34), (.001, .34)]).data.materials.append(grate)
def flames(cx, seed, shots):
    for k in range(18):
        a = k / 18 * math.tau; r0 = random.Random(seed + k)
        fl = b3d.smooth(b3d.prim('cone', [flame], vertices=10, radius1=.09, depth=.34, location=(cx + 1.05 * math.cos(a), 1.05 * math.sin(a), .4)))
        for f in range(0, N, 3):
            fl.scale = (1, 1, r0.uniform(.7, 1.15)); fl.keyframe_insert('scale', frame=f)
        b3d.visible(fl, shots)
flames(0, 1, [(s1, e1), (s3, e7)])
flames(0, 50, [(s2, e2)])

# ---------- cooker body (back half + front half for outside views) ----------
OUTER = [(1.85, .5), (1.95, .58), (1.95, 2.6), (2.05, 2.66)]
back = half(b3d.lathe('Back', [(.001, .5)] + OUTER + [(1.82, 2.66), (1.82, .7), (.001, .7)])); back.data.materials.append(inner)
front = b3d.lathe('Front', [(.001, .5)] + OUTER + [(.001, 2.66)]); front.data.materials.append(steel)
# lid
lid_back = half(b3d.lathe('LidCut', [(.001, 3.0), (1.0, 2.96), (1.75, 2.75), (2.1, 2.72), (2.1, 2.62), (1.85, 2.62), (1.0, 2.84), (.001, 2.88)])); lid_back.data.materials.append(steel)
lid_front = b3d.lathe('LidFront', [(.001, 3.0), (1.0, 2.96), (1.75, 2.75), (2.1, 2.72), (2.1, 2.62), (.001, 2.62)]); lid_front.data.materials.append(steel)
rubber = half(b3d.smooth(b3d.prim('torus', [ring_m], major_radius=1.92, minor_radius=.07, major_segments=72, minor_segments=14, location=(0, 0, 2.62))))
# open pot lid + handles
outer_h = [box(plastic, (sx * 2.45, 0, 2.15), (.9, .36, .2), bevel=.08) for sx in (-1, 1)]
lid_h = box(plastic, (-.55, 0, 3.08), (1.1, .34, .16), bevel=.06)
# valve on the lid (hides handle middle, jiggles in shot 6)
vbase = b3d.smooth(b3d.prim('cylinder', [valve_m], vertices=24, radius=.08, depth=.42, location=(.55, 0, 3.12)))
vtop = b3d.smooth(b3d.prim('cylinder', [valve_m], vertices=24, radius=.2, depth=.22, location=(.55, 0, 3.3)))
for f in range(0, N, 1):
    z = 3.3
    if f >= s6: z = 3.3 + .06 * (.5 + .5 * math.sin((f - s6) * 1.1)) + .08 * ease((f - s6) / 10)
    elif f >= s5: z = 3.3 + .08 * ease((f - s5) / 40)
    vtop.location = (.55, 0, z); vtop.keyframe_insert('location', frame=f)

# ---------- food, water, pressure glow ----------
WZ = 1.7
wat = half(b3d.lathe('WaterVol', [(.001, .72), (1.8, .72), (1.8, WZ), (.001, WZ)])); wat.data.materials.append(water)
air = half(b3d.lathe('AirVol', [(.001, WZ), (1.8, WZ), (1.8, 2.6), (.001, 2.8)])); air.data.materials.append(press)
b3d.key_input(press, 'Emission Strength', [(s3, .0), (s4, .25), (s5, 1.1), (s7, 1.1)])
for k, (x, y, z, r) in enumerate([(-.8, .4, 1.05, .34), (.1, .35, 1.0, .4), (.95, .45, 1.1, .32), (-.35, .55, 1.4, .28), (.55, .5, 1.45, .3)]):
    c = box(meat, (x, y, z), (r * 1.5, r * 1.3, r * 1.1), bevel=.08)
    c.rotation_euler = (k * .4, k * .7, k * .3)
BUB_SP = 22
for k in range(30):
    rr = random.Random(k); x0 = rr.uniform(-1.6, 1.6); y0 = rr.uniform(.05, .9); ph = rr.random(); r_ = rr.uniform(.03, .08)
    b = b3d.smooth(b3d.prim('uv_sphere', [bubble], segments=10, ring_count=6, radius=r_))
    for f in range(0, N, 2):
        speed = BUB_SP if f < s5 else BUB_SP * 2.2  # stops bubbling as hard once pressure holds it down
        u = (ph + f / speed) % 1; b.location = (x0 + .05 * math.sin(f * .3 + k), y0, .78 + u * (WZ - .82)); b.keyframe_insert('location', frame=f)
# trapped steam in the headspace: speeds up and packs in as pressure rises
SP = []
for k in range(44):
    rr = random.Random(k + 300); x0 = rr.uniform(-1.55, 1.55); y0 = rr.uniform(.03, .8); z0 = rr.uniform(WZ + .1, 2.55); vx = rr.uniform(-1, 1); vz = rr.uniform(-1, 1)
    b = b3d.smooth(b3d.prim('uv_sphere', [steam], segments=10, ring_count=6, radius=rr.uniform(.045, .08)))
    for f in range(s3, e6, 2):
        amp = .3 + .5 * ease((f - s3) / max(1, s5 - s3)); t = (f - s3) * (.05 + .1 * ease((f - s3) / max(1, s5 - s3)))
        b.location = (x0 + amp * math.sin(t + k), y0, min(2.58, max(WZ + .05, z0 + amp * .3 * math.sin(t * 1.3 + k * 2)))); b.keyframe_insert('location', frame=f)
    b3d.visible(b, [(s3 + 8, e6)] if k < 12 else [(s4, e6)])
# steam puff at the valve
for k in range(18):
    rr = random.Random(k + 500); ph = rr.random(); dx = rr.uniform(-.1, .1)
    b = b3d.smooth(b3d.prim('uv_sphere', [steam], segments=10, ring_count=6, radius=rr.uniform(.05, .1)))
    for f in range(s6, e6, 2):
        u = (ph + (f - s6) / 20) % 1; b.location = (.55 + dx + u * .5 * rr.uniform(-.2, 1), -.05, 3.45 + u * 1.2); b.keyframe_insert('location', frame=f)
    b3d.visible(b, [(s6, e6)])

# ---------- thermometer (big gauge stuck out to the left, in front of the wall) ----------
TX, TZ = -2.6, 2.0
tube_o = b3d.prim('cylinder', [glass], vertices=24, radius=.2, depth=3.0, location=(TX, -.2, TZ))
bulb = b3d.smooth(b3d.prim('uv_sphere', [red], segments=24, ring_count=16, radius=.3, location=(TX, -.2, TZ - 1.6)))
col = b3d.prim('cylinder', [red], vertices=16, radius=.12, depth=1, location=(TX, -.2, 0))
def tv(f):
    if f < s4: return 100.0
    if f < s5 + int((e5 - s5) * .55): return 100 + 20 * ease((f - s4) / (s5 + int((e5 - s5) * .55) - s4))
    return 120.0
H0, H1 = 1.0, 2.5  # column height at 100 and 120
for f in range(0, N, 2):
    h = H0 + (H1 - H0) * (tv(f) - 100) / 20
    col.scale = (1, 1, h); col.location = (TX, -.2, TZ - 1.5 + h / 2); col.keyframe_insert('scale', frame=f); col.keyframe_insert('location', frame=f)
ticks_ = []
for h, m in ((H0, tick_m), (H1, valve_m)):
    ticks_.append(box(m, (TX + .32, -.2, TZ - 1.5 + h), (.34, .04, .06)))
therm = [tube_o, bulb, col] + ticks_
for o in therm: b3d.visible(o, [(s2, e2), (s4, e6)])
for h, body in ((H0, '100\u00b0'), (H1, '120\u00b0')):
    bpy.ops.object.text_add(location=(TX - .58, -.28, TZ - 1.5 + h - .1), rotation=(math.radians(90), 0, 0)); lb = bpy.context.object
    lb.data.body = body; lb.data.size = .3; lb.data.extrude = .01; lb.data.align_x = 'CENTER'; lb.data.materials.append(tick_m if h == H0 else point_m)
    therm.append(lb)
for o in therm[5:]: b3d.visible(o, [(s2, e2), (s4, e6)])
# open pot: steam just flies away in shot 2
for k in range(18):
    rr = random.Random(k + 800); x0 = rr.uniform(-1.4, 1.4); ph = rr.random(); dx = rr.uniform(-.5, .5)
    b = b3d.smooth(b3d.prim('uv_sphere', [steam], segments=10, ring_count=6, radius=rr.uniform(.05, .1)))
    for f in range(s2, e2, 2):
        u = (ph + (f - s2) / 26) % 1; b.location = (x0 + dx * u, .25, WZ + .05 + u * 3.0); b.keyframe_insert('location', frame=f)
    b3d.visible(b, [(s2, e2)])

# ---------- arrows ----------
b3d.visible(b3d.arrow('RingPt', (1.6, -1.4, 3.3), (1.85, -.4, 2.72), point_m, r=.035), [(s3 + 8, e3)])
b3d.visible(b3d.arrow('Down1', (-.5, -.2, 2.55), (-.5, -.2, 1.95), point_m, r=.04), [(s4 + 8, e5)])
b3d.visible(b3d.arrow('Down2', (.7, -.2, 2.55), (.7, -.2, 1.95), point_m, r=.04), [(s4 + 8, e5)])
b3d.visible(b3d.arrow('Up', (1.1, -.5, 3.1), (.75, -.4, 3.35), point_m, r=.03), [(s6, e6)])

# ---------- what shows when ----------
b3d.visible(front, [(s1, e1), (s7, e7)])
b3d.visible(lid_front, [(s1, e1), (s7, e7)])
b3d.visible(lid_back, [(s3, e6)])
b3d.visible(wat, [(s2, e6)]); b3d.visible(air, [(s3, e6)]); b3d.visible(rubber, [(s3, e6)])
for o in (vbase, vtop, lid_h): b3d.visible(o, [(s1, e1), (s3, e7)])
for o in outer_h: b3d.visible(o, [(s1, e1), (s7, e7)])

# ---------- lights ----------
b3d.light('AREA', 'Key', (5, -9, 9), 1000, (1, .95, .88), 8, rot=(40, 0, 25))
b3d.light('AREA', 'Fill', (-6, -7, 4), 340, (.62, .74, 1), 6, rot=(70, 0, -40))
b3d.light('POINT', 'Inside', (0, -1.0, 2.2), 45, (1, 1, 1), 1)

# ---------- timeline ----------
cam, tgt = b3d.camera(30)
b3d.shot(cam, tgt, s1, e1, (2.2, -9.8, 4.2), (1.5, -8.8, 3.8), (0, 0, 2.0), lens=30)
b3d.shot(cam, tgt, s2, e2, (-.95, -8.7, 2.9), (-.85, -8.3, 2.8), (-.75, 0, 2.3), lens=30)
b3d.shot(cam, tgt, s3, e3, (1.2, -7.2, 3.0), (1.0, -6.6, 2.9), (.7, 0, 2.2), lens=30)
b3d.shot(cam, tgt, s4, e4, (-.95, -8.7, 2.9), (-.9, -8.45, 2.85), (-.75, 0, 2.2), lens=30)
b3d.shot(cam, tgt, s5, e5, (-.9, -8.45, 2.85), (-.85, -8.15, 2.8), (-.75, 0, 2.2), lens=30)
b3d.shot(cam, tgt, s6, e6, (1.0, -5.2, 4.1), (.8, -4.8, 4.2), (.5, 0, 3.5), lens=30)
b3d.shot(cam, tgt, s7, e7, (1.5, -8.8, 3.8), (2.6, -12.0, 4.8), (0, 0, 2.0), lens=30)
b3d.render(OUT, cfg.get('frames'))
