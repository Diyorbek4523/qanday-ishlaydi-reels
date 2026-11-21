"""Mog'or: an outer room corner in winter. Hook: black mould in the corner; cold corner (blue overlay, +20 vs +10 labels,
warm air loops away from the corner); vapour rises from a mug; vapour reaches the cold corner and condenses into droplets;
spores drift in and mould grows; window opens, fresh-air arrows, droplets dry; pull back. 7 shots."""
import math, os, sys, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy
from mathutils import Vector

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.015, .025, .06), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))
R = math.radians

def blend(m, a):
    b3d.bsdf(m).inputs['Alpha'].default_value = a
    try: m.surface_render_method = 'BLENDED'
    except Exception: pass
    return m

wall_m = b3d.mat('Wall', (.78, .7, .58), .85, bump=.015)
wall_out = b3d.mat('WallOut', (.55, .5, .46), .9)
floor_m = b3d.mat('Floor', (.42, .27, .16), .6)
snow_m = b3d.mat('Snow', (.85, .9, 1), .7)
frame_m = b3d.mat('Frame', (.92, .92, .9), .4)
glass_m = blend(b3d.mat('Glass', (.6, .75, .9), .05), .25)
rad_m = b3d.mat('Radiator', (.9, .9, .88), .35)
mould_m = b3d.mat('Mould', (.06, .07, .045), .95, bump=.3)
water_m = b3d.mat('Water', (.75, .88, 1), .03, emit=(.6, .8, 1), estr=.4)
warm_m = b3d.mat('Warm', (1, .55, .15), .3, emit=(1, .5, .1), estr=4)
vap_m = blend(b3d.mat('Vapour', (.75, .9, 1), .3, emit=(.6, .85, 1), estr=2.5), .8)
spore_m = b3d.mat('Spore', (.5, .6, .35), .5, emit=(.55, .7, .3), estr=2)
fresh_m = b3d.mat('Fresh', (.4, .85, 1), .3, emit=(.3, .8, 1), estr=4)
mug_m = b3d.mat('Mug', (.75, .2, .15), .4)
table_m = b3d.mat('Table', (.45, .3, .18), .6)
cold_m = [blend(b3d.mat(f'Cold{i}', (.2, .5, 1), .5, emit=(.2, .5, 1), estr=1.5), 0) for i in range(3)]

def keys(ob, attr, fv):
    for f, v in fv: setattr(ob, attr, v); ob.keyframe_insert(attr, frame=f)

def box(name, m, lo, hi):
    lo, hi = Vector(lo), Vector(hi)
    ob = b3d.prim('cube', [m], size=1, location=(lo + hi) / 2); ob.scale = hi - lo; ob.name = name; return ob

H = 2.8; T = .35
# ---------- corner: wall1 along y (x 0..T), wall2 along x (y 0..T) with a window hole ----------
box('Wall1', wall_m, (0, -4.5, 0), (T, T, H))
WX0, WX1, WZ0, WZ1 = -2.9, -1.7, .95, 2.15
box('W2a', wall_m, (-4.5, 0, 0), (WX0, T, H))
box('W2b', wall_m, (WX1, 0, 0), (0, T, H))
box('W2c', wall_m, (WX0, 0, 0), (WX1, T, WZ0))
box('W2d', wall_m, (WX0, 0, WZ1), (WX1, T, H))
box('Ceil', wall_m, (-4.5, -4.5, H), (T, T, H + .1))
b3d.prim('plane', [floor_m], size=10, location=(-2, -2, 0))
b3d.prim('plane', [snow_m], size=30, location=(0, 15.4, -.4))
# window frame + opening pane (hinged at WX0)
for lo, hi in [((WX0, .02, WZ0), (WX1, .1, WZ0 + .06)), ((WX0, .02, WZ1 - .06), (WX1, .1, WZ1)),
               ((WX0, .02, WZ0), (WX0 + .06, .1, WZ1)), ((WX1 - .06, .02, WZ0), (WX1, .1, WZ1))]:
    box('Fr', frame_m, lo, hi)
hinge = b3d.empty('Hinge', (WX0 + .06, .06, 0))
pane = box('Pane', glass_m, (0, -.01, WZ0 + .06), (WX1 - WX0 - .12, .01, WZ1 - .06)); pane.parent = hinge
pf = box('PaneBar', frame_m, (0, -.02, (WZ0 + WZ1) / 2 - .02), (WX1 - WX0 - .12, .02, (WZ0 + WZ1) / 2 + .02)); pf.parent = hinge
OP = s6 + int((e6 - s6) * .3)
keys(hinge, 'rotation_euler', [(0, (0, 0, 0)), (s6, (0, 0, 0)), (OP, (0, 0, R(-70))), (e7, (0, 0, R(-70)))])
# radiator under window
for k in range(9):
    b3d.smooth(box('Rib', rad_m, (WX0 + .05 + k * .125, -.16, .18), (WX0 + .14 + k * .125, -.06, .78)))
box('Pipe', rad_m, (WX0 + .02, -.13, .22), (WX1 - .02, -.09, .26))
# small table + mug
box('Top', table_m, (-2.3, -2.0, .7), (-1.5, -1.3, .75))
for x, y in [(-2.25, -1.95), (-1.55, -1.95), (-2.25, -1.35), (-1.55, -1.35)]: box('Leg', table_m, (x - .025, y - .025, 0), (x + .025, y + .025, .7))
MUG = Vector((-1.75, -1.55, .75))
b3d.smooth(b3d.prim('cylinder', [mug_m], vertices=32, radius=.06, depth=.12, location=MUG + Vector((0, 0, .06))))

# ---------- cold overlay near the corner (shots 2-4) ----------
for i, (w, a) in enumerate([(.45, .45), (.9, .25), (1.4, .1)]):
    p1 = b3d.prim('plane', [cold_m[i]], size=1, location=(-.004 - i * .001, -w / 2, H / 2), rotation=(0, R(90), 0)); p1.scale = (H, w, 1)
    p2 = b3d.prim('plane', [cold_m[i]], size=1, location=(-w / 2, -.004 - i * .001, H / 2), rotation=(R(90), 0, 0)); p2.scale = (w, H, 1)
    b3d.key_input(cold_m[i], 'Alpha', [(0, 0), (s2, 0), (s2 + 15, a), (e4, a), (e4 + 10, 0)])

def label(txt, loc, m, size=.28):
    cu = bpy.data.curves.new('L', 'FONT'); cu.body = txt; cu.size = size; cu.align_x = 'CENTER'; cu.extrude = .01
    ob = b3d.link(bpy.data.objects.new('L', cu)); ob.data.materials.append(m); ob.location = loc
    ob.rotation_euler = (R(90), 0, R(-45)); return ob
cold_lbl = b3d.mat('ColdLbl', (.3, .6, 1), .4, emit=(.3, .6, 1), estr=4)
for o in (label('+10°', (-.45, -.45, 2.2), cold_lbl), label('+20°', (-2.1, -2.7, 1.2), warm_m)):
    b3d.visible(o, [(s2, e4)])

rnd = random.Random(7)
# warm air loop (shot 2): ellipse in the room centre, never reaching the corner
for k in range(16):
    bd = b3d.prim('uv_sphere', [warm_m], radius=.035, segments=12, ring_count=8)
    for f in range(s2, e2 + 1, 2):
        a = k / 16 * 2 * math.pi + (f - s2) * .05
        bd.location = (-2.2 + 1.1 * math.cos(a), -2.2 + 1.1 * math.sin(a), 1.3 + .6 * math.sin(a * 2)); bd.keyframe_insert('location', frame=f)
    b3d.visible(bd, [(s2, e2)])

# vapour: rises from the mug (shot 3), drifts to the corner (shot 4)
CORNER = []
for k in range(26):
    bd = b3d.prim('uv_sphere', [vap_m], radius=.022, segments=12, ring_count=8); bd.visible_shadow = False
    t0 = s3 + rnd.randint(0, max(1, (e3 - s3) // 2))
    end = Vector((-.05 - rnd.uniform(0, .5) * (k % 2), -.05 - rnd.uniform(0, .5) * ((k + 1) % 2), rnd.uniform(.4, 2.5)))
    if k % 2: end.y = -.05
    else: end.x = -.05
    up = MUG + Vector((rnd.uniform(-.25, .25), rnd.uniform(-.25, .25), rnd.uniform(.7, 1.3)))
    keys(bd, 'location', [(t0, MUG + Vector((0, 0, .12))), (e3, up), (s4 + rnd.randint(15, max(16, e4 - s4 - 5)), end)])
    keys(bd, 'scale', [(t0, (.3, .3, .3)), (t0 + 20, (1, 1, 1))])
    b3d.visible(bd, [(t0, e4)])
    CORNER.append(end)

# droplets on the cold corner (appear in shot 4, dry in shot 6)
DRY = s6 + int((e6 - s6) * .85)
for k in range(70):
    side = k % 2; d = abs(rnd.gauss(0, .28)); z = rnd.uniform(.15, 2.7); r = rnd.uniform(.008, .022)
    loc = (-.006, -d, z) if side == 0 else (-d, -.006, z)
    dr = b3d.smooth(b3d.prim('uv_sphere', [water_m], radius=r, segments=12, ring_count=8, location=loc))
    dr.scale = (.45, 1, 1.15) if side == 0 else (1, .45, 1.15)
    sc0 = dr.scale.copy(); t0 = s4 + int((e4 - s4) * (.35 + .6 * rnd.random()))
    keys(dr, 'scale', [(t0, (0, 0, 0)), (t0 + 8, sc0), (s6 + 10, sc0), (DRY, (0, 0, 0))])

# mould patches near the corner: full in shot 1, absent shots 2-4, grow in shot 5, stay
MS = []
for k in range(60):
    side = k % 2; d = abs(rnd.gauss(0, .2)); z = rnd.choice([rnd.uniform(2.2, 2.75), rnd.uniform(.1, .6), rnd.uniform(.6, 2.2)])
    if abs(z - 1.4) < .8 and d > .12: d *= .5
    loc = (-.003, -d, z) if side == 0 else (-d, -.003, z)
    rot = (0, R(90), 0) if side == 0 else (R(90), 0, 0)
    m = b3d.prim('cylinder', [mould_m], vertices=20, radius=rnd.uniform(.025, .1), depth=.004, location=loc, rotation=rot)
    m.visible_shadow = False; sx, sy = rnd.uniform(.7, 1.3), rnd.uniform(.7, 1.3)
    full = (sx, sy, 1); g0 = s5 + int((e5 - s5) * (.2 + .5 * rnd.random()))
    keys(m, 'scale', [(0, full), (s2 - 1, full), (s2, (0, 0, 1)), (g0, (0, 0, 1)), (min(g0 + 40, e5 - 1), full), (e7, full)])
    MS.append(Vector(loc))

# spores drift in and land on the mould spots (shot 5)
for k in range(30):
    sp = b3d.prim('uv_sphere', [spore_m], radius=.012, segments=8, ring_count=6); sp.visible_shadow = False
    tgt_ = MS[k % len(MS)]; st = Vector((rnd.uniform(-1.6, -.4), rnd.uniform(-1.6, -.4), rnd.uniform(.4, 2.6)))
    pts = []
    for j in range(6):
        t = j / 5; p = st.lerp(tgt_, t) + Vector((rnd.uniform(-.1, .1), rnd.uniform(-.1, .1), rnd.uniform(-.1, .1))) * (1 - t)
        pts.append((s5 + int((e5 - s5) * .55 * t), p))
    keys(sp, 'location', pts)
    b3d.visible(sp, [(s5, s5 + int((e5 - s5) * .6))])

# fresh air arrows through the open window (shot 6)
for i, z in enumerate((1.25, 1.55, 1.85)):
    a_in = b3d.arrow(f'In{i}', (-2.4, 1.6, z - .1), (-2.4 + .2, -.9, z - .25), fresh_m, r=.03)
    a_out = b3d.arrow(f'Out{i}', (-1.95, -.9, z + .15), (-2.0, 1.4, z + .25), warm_m, r=.022)
    for a_ in (a_in, a_out): b3d.visible(a_, [(OP, e6)])

b3d.light('AREA', 'Key', (-3.2, -3.4, 2.5), 90, (1, .88, .72), 2.0, rot=(60, 0, -45))
b3d.light('POINT', 'Lamp', (-2.4, -2.4, 2.2), 25, (1, .85, .65), .3)
b3d.light('AREA', 'Win', (-2.3, 1.5, 1.6), 60, (.55, .7, 1), 1.2, rot=(-90, 0, 0))
b3d.light('POINT', 'CornerFill', (-.8, -.8, 1.4), 15, (.9, .9, 1), .3)
b3d.light('SUN', 'Moon', (0, 6, 6), 1.2, (.6, .7, 1), .1, rot=(-50, 0, 180))

# ---------- camera ----------
cam, tgt = b3d.camera(22)
C = (0, 0, 1.45)
b3d.shot(cam, tgt, s1, e1, (-2.3, -2.3, 1.55), (-1.9, -1.9, 1.5), C, lens=22)
b3d.shot(cam, tgt, s2, e2, (-3.6, -3.6, 1.6), (-3.4, -3.8, 1.6), (-1.1, -1.1, 1.4), lens=20)
b3d.shot(cam, tgt, s3, e3, (-2.6, -2.7, 1.25), (-2.5, -2.55, 1.3), MUG + Vector((.3, .3, .6)), (MUG + Vector((.5, .5, .8))), lens=26)
b3d.shot(cam, tgt, s4, e4, (-1.5, -.45, 1.55), (-1.3, -.4, 1.5), (0, -.25, 1.4), lens=26)
b3d.shot(cam, tgt, s5, e5, (-1.3, -1.25, 1.6), (-1.1, -1.05, 1.7), (0, 0, 1.6), lens=24)
b3d.shot(cam, tgt, s6, e6, (-1.2, -3.2, 1.55), (-1.4, -3.0, 1.55), (-1.6, 0, 1.45), lens=22)
b3d.shot(cam, tgt, s7, e7, (-1.8, -1.8, 1.5), (-3.6, -3.6, 1.7), C, lens=22)

b3d.render(OUT, cfg.get('frames'))
