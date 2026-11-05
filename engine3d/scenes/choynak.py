"""Choynak: electric kettle cut in half. Heater boils water, steam climbs a thin channel inside the handle wall down to a small bimetal disc at the
base; the disc snaps, pushes the switch, the heater and the lamp go out. Half-lathes give a cut face at y = 0. 5 shots."""
import bmesh, math, os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.05, .06, .12), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5) = list(zip(S[:-1], S[1:]))

# ---------- materials ----------
shell = b3d.mat('Shell', (.82, .84, .88), .22, metal=.6)
inner = b3d.mat('Inner', (.42, .46, .52), .4, metal=.5)
plastic = b3d.mat('Plastic', (.08, .09, .12), .4)
base_m = b3d.mat('Base', (.12, .13, .17), .4)
water = b3d.mat('Water', (.2, .55, .95), .1, emit=(.05, .3, .75), estr=.5)
b3d.bsdf(water).inputs['Alpha'].default_value = .55
try: water.surface_render_method = 'BLENDED'
except (AttributeError, TypeError): pass
bubble = b3d.mat('Bubble', (.8, .92, 1), .1, emit=(.6, .85, 1), estr=1.2)
steam = b3d.mat('Steam', (.92, .95, 1), .5, emit=(.8, .9, 1), estr=2.0)
heater = b3d.mat('Heater', (.2, .08, .05), .4, emit=(1, .25, .03), estr=0)
disc_m = b3d.mat('Disc', (1, .55, .1), .25, metal=.7, emit=(1, .4, .05), estr=.5)
sw_m = b3d.mat('Switch', (.9, .12, .1), .4)
lamp_m = b3d.mat('Lamp', (.9, .1, .1), .3, emit=(1, .1, .08), estr=3)
chan_m = b3d.mat('Channel', (.22, .25, .32), .4, metal=.3)
wood = b3d.mat('Table', (.3, .16, .08), .6, bump=.2)
wall = b3d.mat('Wall', (.1, .14, .22), .85)
point_m = b3d.mat('Point', (1, .8, .2), .4, emit=(1, .72, .08), estr=2.6)
def box(m, c, s, bevel=0):
    b = b3d.prim('cube', [m], size=1, location=c); b.scale = s
    if bevel:
        bv = b.modifiers.new('Bv', 'BEVEL'); bv.width = bevel; bv.segments = 4; b3d.smooth(b)
    return b
def tube(name, pts, m, r=.03):
    cv = bpy.data.curves.new(name, 'CURVE'); cv.dimensions = '3D'; cv.bevel_depth = r; cv.bevel_resolution = 3; cv.use_fill_caps = True
    sp = cv.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for bp, p in zip(sp.points, pts): bp.co = (*p, 1)
    cv.materials.append(m); return b3d.link(bpy.data.objects.new(name, cv))
def ease(u): u = min(1, max(0, u)); return u * u * (3 - 2 * u)
def half(ob):
    """Cut a lathe in half: keep y >= 0 so the cut face looks at the camera."""
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, 0), plane_no=(0, 1, 0), clear_outer=False, clear_inner=True)
    bm.to_mesh(ob.data); bm.free(); return ob

T_SNAP = s4 + int((e4 - s4) * .38)
BOIL0 = s1

# ---------- room ----------
box(wood, (0, 0, -.25), (40, 30, .5))
b3d.prim('plane', [wall], size=60, location=(0, 6, 20), rotation=(math.radians(90), 0, 0))

# ---------- power base ----------
b3d.lathe('PowerBase', [(.001, 0), (2.1, 0), (2.15, .12), (2.05, .4), (.001, .4)]).data.materials.append(base_m)

# ---------- kettle: back half always, front half only outside ----------
PROF = [(1.55, .55), (1.75, .75), (1.7, 3.2), (1.55, 4.4), (1.4, 4.9)]
inner_prof = [(.001, .95), (1.62, .95), (1.62, 3.2), (1.47, 4.35), (1.33, 4.85)]
def wall_prof():  # closed thin wall
    return PROF + list(reversed(inner_prof[1:]))
back = half(b3d.lathe('BackWall', [(.001, .55)] + wall_prof() + [(.001, .95)])); back.data.materials.append(inner)
front = b3d.lathe('FrontWall', [(.001, .55)] + PROF + [(.001, 4.9)]); front.data.materials.append(shell)
lid = b3d.lathe('Lid', [(.001, 5.15), (.9, 5.12), (1.42, 4.95), (1.42, 4.85), (.001, 4.85)]); lid.data.materials.append(plastic)
knob = b3d.smooth(b3d.prim('uv_sphere', [plastic], segments=24, ring_count=14, radius=.2, location=(0, 0, 5.28)))
spout = box(shell, (-1.72, 0, 4.2), (.55, .55, .22), bevel=.08); spout.rotation_euler = (0, math.radians(-22), 0)
# handle on the right: hollow channel in its wall
HX = 1.95
handle_top = box(plastic, (2.5, .0, 4.15), (1.25, .5, .34), bevel=.1)
handle_v = box(plastic, (3.0, 0, 2.55), (.34, .5, 3.1), bevel=.1)
handle_bot = box(plastic, (2.5, 0, .95), (1.25, .5, .34), bevel=.1)
# visible channel on the cut face
chan_pts = [(1.62, -.28, 3.8), (2.15, -.28, 3.8), (2.15, -.28, 1.2)]
ch = tube('Chan', chan_pts, chan_m, r=.075)
stem = box(plastic, (2.15, .02, 2.5), (.3, .4, 2.75)); arm_ = box(plastic, (1.88, .02, 3.8), (.55, .4, .3))
# control box at the base of the handle
ctrl = box(base_m, (2.15, 0, .85), (.92, .5, .62), bevel=.05)
disc = b3d.smooth(b3d.prim('cylinder', [disc_m], vertices=40, radius=.3, depth=.05, location=(2.15, -.28, 1.0)))
sw = box(sw_m, (3.0, -.05, 1.0), (.1, .34, .5), bevel=.02)  # the visible switch; tilts at snap
pin = box(chan_m, (2.55, -.28, .95), (.65, .05, .05))
lamp = b3d.smooth(b3d.prim('uv_sphere', [lamp_m], segments=18, ring_count=12, radius=.09, location=(3.0, -.3, 1.45)))
# disc snap: bows from concave down (flat) to bulged, pin pushes switch
for f, sc_z in ((0, .6), (T_SNAP - 1, .6), (T_SNAP + 1, 3.2), (N, 3.2)):
    disc.scale = (1, 1, sc_z); disc.keyframe_insert('scale', frame=f)
for f, r in ((0, 0), (T_SNAP - 1, 0), (T_SNAP + 2, -28), (N, -28)):
    sw.rotation_euler = (0, math.radians(r), 0); sw.keyframe_insert('rotation_euler', frame=f)
for f, x in ((0, 2.55), (T_SNAP - 1, 2.55), (T_SNAP + 2, 2.72), (N, 2.72)):
    pin.location = (x, -.28, .95); pin.keyframe_insert('location', frame=f)
RED, DARK = (1, .1, .08), (.02, .02, .02)
b3d.key_input(lamp_m, 'Emission Strength', [(0, 3.), (T_SNAP - 1, 3.), (T_SNAP, 0.)])

# ---------- water, heater, bubbles ----------
wat = b3d.lathe('WaterVol', [(.001, .98), (1.6, .98), (1.6, 3.1), (.001, 3.1)]); wat.data.materials.append(water)
half(wat)
hc = b3d.smooth(b3d.prim('torus', [heater], major_radius=1.0, minor_radius=.075, major_segments=64, minor_segments=12, location=(0, .25, 1.12)))
b3d.key_input(heater, 'Emission Strength', [(0, 1.0), (s2, 2.8), (T_SNAP - 1, 3.2), (T_SNAP + 12, 0.)])
b3d.key_input(heater, 'Base Color', [(0, (.8, .2, .05)), (T_SNAP + 12, (.2, .08, .05))])
BUB_END = T_SNAP + 40
for k in range(46):
    rr = random.Random(k); x0 = rr.uniform(-1.3, 1.3); y0 = rr.uniform(.05, .9); ph = rr.random(); sp_ = rr.uniform(14, 26); r_ = rr.uniform(.04, .1)
    b = b3d.smooth(b3d.prim('uv_sphere', [bubble], segments=10, ring_count=6, radius=r_))
    for f in range(0, BUB_END, 2):
        u = (ph + f / sp_) % 1; b.location = (x0 + .06 * math.sin(f * .4 + k), y0, 1.15 + u * 1.95); b.keyframe_insert('location', frame=f)
    b3d.visible(b, [(0, BUB_END)])
# steam above water
for k in range(22):
    rr = random.Random(k + 200); x0 = rr.uniform(-1.2, 1.2); ph = rr.random()
    b = b3d.smooth(b3d.prim('uv_sphere', [steam], segments=10, ring_count=6, radius=rr.uniform(.05, .11)))
    for f in range(0, BUB_END, 2):
        u = (ph + f / 30) % 1; b.location = (x0 * (1 - u) + 1.5 * u, rr.uniform(0, .01) + .3, 3.15 + u * .7); b.keyframe_insert('location', frame=f)
    b3d.visible(b, [(s2, BUB_END)])
# steam running along the channel to the disc
for k in range(16):
    ph = k / 16
    b = b3d.smooth(b3d.prim('uv_sphere', [steam], segments=10, ring_count=6, radius=.07))
    for f in range(s3, T_SNAP + 20, 2):
        u = (ph + (f - s3) / 28) % 1
        if u < .17: p = (1.62 + u / .17 * .53, -.31, 3.8)
        else: p = (2.15, -.31, 3.8 - (u - .17) / .83 * 2.65)
        b.location = p; b.keyframe_insert('location', frame=f)
    b3d.visible(b, [(s3, T_SNAP + 20)])
b3d.visible(b3d.arrow('ToDisc', (2.65, -.4, 2.6), (2.28, -.4, 1.25), point_m, r=.035), [(s2 + 18, e2), (s3 + 30, e3)])

# ---------- which parts show ----------
b3d.visible(front, [(s1, e1), (s5, e5)])
for o in (wat,):
    b3d.visible(o, [(s2, e4)])
b3d.visible(ch, [(s2, e4)]); b3d.visible(stem, [(s2, e4)]); b3d.visible(arm_, [(s2, e4)])
b3d.visible(disc, [(s2, e4)]); b3d.visible(pin, [(s2, e4)])
b3d.visible(ctrl, [(s1, e1), (s5, e5)])

# ---------- lights ----------
b3d.light('AREA', 'Key', (5, -8, 9), 900, (1, .95, .88), 8, rot=(40, 0, 25))
b3d.light('AREA', 'Fill', (-6, -7, 4), 320, (.62, .74, 1), 6, rot=(70, 0, -40))
b3d.light('POINT', 'Inside', (.2, -1.2, 3.6), 45, (1, 1, 1), 1)

# ---------- timeline ----------
cam, tgt = b3d.camera(30)
b3d.shot(cam, tgt, s1, e1, (2.4, -12.5, 3.4), (1.6, -11.2, 3.3), (.4, 0, 2.5), lens=30)
b3d.shot(cam, tgt, s2, e2, (.6, -9.4, 3.2), (1.3, -7.6, 2.9), (1.3, 0, 2.2), lens=30)
b3d.shot(cam, tgt, s3, e3, (.8, -8.6, 3.8), (1.3, -7.8, 3.6), (1.0, 0, 2.9), lens=30)
b3d.shot(cam, tgt, s4, e4, (2.4, -3.8, 1.6), (2.5, -3.4, 1.5), (2.45, 0, 1.2), lens=30)
b3d.shot(cam, tgt, s5, e5, (1.6, -11.2, 3.3), (2.8, -14.8, 4.2), (.4, 0, 2.5), lens=30)
b3d.render(OUT, cfg.get('frames'))
