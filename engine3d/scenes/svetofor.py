"""Svetofor: induction loop under the asphalt. A road slab lifts to reveal the wire loop, its magnetic field arcs over the lane,
a car's metal body squashes the field, a signal runs to the controller box and the light turns green. 7 shots."""
import math, os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.05, .06, .13), preview=cfg.get('preview'))
sh = list(zip(S[:-1], S[1:]))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = sh

# ---------- materials ----------
asphalt = b3d.mat('Asphalt', (.11, .115, .13), .85, bump=.25)
soil = b3d.mat('Soil', (.22, .14, .08), .9, bump=.3)
walk = b3d.mat('Walk', (.36, .36, .38), .8, bump=.1)
paint = b3d.mat('Paint', (.85, .85, .8), .6)
copper = b3d.mat('Copper', (.95, .5, .2), .35, metal=.6, emit=(1, .45, .12), estr=1.5)
xray = b3d.mat('Xray', (1, .55, .15), .5, emit=(1, .45, .05), estr=1.6)
field = b3d.mat('Field', (.2, .6, 1), .5, emit=(.15, .55, 1), estr=1.5)
sig = b3d.mat('Signal', (1, .9, .3), .4, emit=(1, .75, .1), estr=2.2)
wire_m = b3d.mat('Wire', (.5, .4, .1), .5, emit=(1, .8, .2), estr=.7)
car_m = b3d.mat('Car', (.8, .12, .1), .3, metal=.3)
glass = b3d.mat('Glass', (.08, .13, .2), .1, metal=.4)
tyre = b3d.mat('Tyre', (.03, .03, .03), .8)
hub = b3d.mat('Hub', (.6, .62, .65), .3, metal=.8)
head = b3d.mat('Head', (1, .95, .7), .3, emit=(1, .92, .6), estr=5)
tail = b3d.mat('Tail', (.8, .05, .03), .3, emit=(1, .05, .02), estr=3)
steel = b3d.mat('Steel', (.25, .27, .3), .45, metal=.7)
box_m = b3d.mat('Box', (.45, .5, .52), .5, metal=.3)
red_l = b3d.mat('Red', (.25, .02, .02), .3, emit=(1, .04, .02), estr=2.5)
yel_l = b3d.mat('Yel', (.25, .18, .02), .3, emit=(1, .7, .05), estr=0)
grn_l = b3d.mat('Grn', (.02, .2, .06), .3, emit=(.02, .95, .2), estr=0)
wall_ms = [b3d.mat(f'W{i}', c, .8) for i, c in enumerate(((.22, .2, .28), (.3, .22, .2), (.18, .24, .3)))]
win = b3d.mat('Win', (1, .8, .45), .5, emit=(1, .68, .3), estr=1.05)
leaf = b3d.mat('Leaf', (.08, .25, .14), .8)

def box(m, c, s, name=None):
    b = b3d.prim('cube', [m], size=1, location=c); b.scale = s
    if name: b.name = name
    return b
def curve(name, pts, m, bev, cyclic=False):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = bev; cu.bevel_resolution = 3
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1); sp.use_cyclic_u = cyclic
    for p, c in zip(sp.points, pts): p.co = (*c, 1)
    ob = b3d.link(bpy.data.objects.new(name, cu)); cu.materials.append(m); return ob
def rect(x, y0, y1, z): return [(-x, y0, z), (x, y0, z), (x, y1, z), (-x, y1, z)]

# ---------- road, junction, sidewalks ----------
LY, LX, LL = -2., 1.1, 1.0                     # loop centre y, half width, half length
road = box(asphalt, (0, 0, -.5), (5, 80, 1), 'Road'); road.data.materials.append(soil)
cut = box(soil, (0, LY, -.35), (2.5, 2.3, .7), 'PitCut'); cut.hide_render = cut.hide_viewport = True
bo = road.modifiers.new('Pit', 'BOOLEAN'); bo.operation = 'DIFFERENCE'; bo.object = cut
try: bo.material_mode = 'TRANSFER'
except (AttributeError, TypeError): pass
lid = box(asphalt, (0, LY, -.35), (2.49, 2.29, .7), 'Lid')
for sx in (-1, 1):
    box(asphalt, (sx * 22.5, 4.5, -.5), (40, 6, 1))
    box(walk, (sx * 5.5, -19.25, -.4), (6, 41.5, 1)); box(walk, (sx * 5.5, 27.75, -.4), (6, 40.5, 1))
    box(paint, (sx * 2.35, -19.25, .004), (.1, 41.5, .008))
box(paint, (0, .1, .004), (5, .45, .008))
for k in range(3):                              # wire turns in the pit
    curve(f'Turn{k}', rect(LX - k * .07, LY - LL + k * .07, LY + LL - k * .07, -.62), copper, .035, True)

# ---------- city backdrop ----------
r = random.Random(4)
for bx, by, w, d, h in ((-9.5, -14, 7, 16, 9), (9.5, -16, 7, 18, 7), (-9.5, 15, 7, 14, 12), (9.5, 14, 7, 12, 10), (0, 26, 22, 8, 14), (-22, 2, 12, 22, 11), (22, 4, 12, 20, 13)):
    box(wall_ms[r.randrange(3)], (bx, by, h / 2), (w, d, h))
    for wz in range(2, int(h), 2):
        for wn in range(int(w / 2)):
            if r.random() < .5: box(win, (bx - w / 2 + 1 + wn * 2, by - d / 2 - .01, wz), (.8, .02, 1))
        if bx:
            side = -1 if bx > 0 else 1
            for wn in range(int(d / 3)):
                if r.random() < .5: box(win, (bx + side * (w / 2 + .01), by - d / 2 + 1.5 + wn * 3, wz), (.02, 1.2, 1))
for tx, ty in ((-7, -7), (-7, -14), (4.6, -13), (4.6, -20), (-4.4, 11)):
    b3d.prim('cylinder', [steel], vertices=12, radius=.1, depth=1.2, location=(tx, ty, .7))
    b3d.smooth(b3d.prim('ico_sphere', [leaf], subdivisions=3, radius=.9, location=(tx, ty, 2)))

# ---------- traffic light and controller ----------
PX, PY = 3.4, 1.0
b3d.prim('cylinder', [steel], vertices=24, radius=.08, depth=3.8, location=(PX, PY, 2.0))
hd = box(steel, (PX, PY, 4.2), (.55, .3, 1.5))
hb = hd.modifiers.new('Bv', 'BEVEL'); hb.width = .06; hb.segments = 3
for m, z in ((red_l, 4.65), (yel_l, 4.2), (grn_l, 3.75)):
    b3d.smooth(b3d.prim('uv_sphere', [m], segments=24, ring_count=16, radius=.17, location=(PX, PY - .14, z)))
ctl = box(box_m, (PX, -.6, .65), (.7, .45, 1.1), 'Controller')
cb = ctl.modifiers.new('Bv', 'BEVEL'); cb.width = .04; cb.segments = 3
PATH = [(LX, LY, .02), (2.6, LY, .02), (3.0, LY, .13), (3.0, -.6, .13), (PX, -.6, .13), (PX, -.6, 1.22), (PX, PY, 1.22), (PX, PY, 3.45)]
wire = curve('SigWire', PATH, wire_m, .012)

# ---------- field (x-ray) over the loop ----------
xr = b3d.empty('XRay')
for k in range(3):
    c = curve(f'XTurn{k}', rect(LX - k * .08, LY - LL + k * .08, LY + LL - k * .08, .015), xray, .02, True); c.parent = xr
fr = b3d.empty('FieldRoot', (0, LY, 0))
for y in (-.8, -.4, 0, .4, .8):
    for a, h in ((LX - .3, .55), (LX, .95), (LX + .3, 1.4)):
        c = curve('Arc', [(a * math.cos(t / 24 * math.pi), y, h * math.sin(t / 24 * math.pi)) for t in range(25)], field, .016); c.parent = fr

# ---------- car (front +Y) ----------
car = b3d.empty('Car', (0, -10, 0))
def rounded(ob, w, seg=5):
    bv = ob.modifiers.new('Bv', 'BEVEL'); bv.width = w; bv.segments = seg; b3d.smooth(ob); ob.parent = car; return ob
rounded(box(car_m, (0, 0, .58), (1.75, 3.7, .55)), .2)
rounded(box(glass, (0, -.25, 1.07), (1.42, 1.9, .55)), .18)
rounded(box(car_m, (0, -.25, 1.35), (1.3, 1.5, .03)), .01)
for wx in (-.88, .88):
    for wy in (-1.15, 1.15):
        t = b3d.smooth(b3d.prim('cylinder', [tyre], vertices=32, radius=.33, depth=.24, location=(wx, wy, .33), rotation=(0, math.radians(90), 0))); t.parent = car
        h = b3d.smooth(b3d.prim('cylinder', [hub], vertices=24, radius=.15, depth=.26, location=(wx, wy, .33), rotation=(0, math.radians(90), 0))); h.parent = car
for sx in (-.6, .6):
    b3d.smooth(b3d.prim('uv_sphere', [head], segments=16, ring_count=10, radius=.12, location=(sx, 1.83, .62))).parent = car
    box(tail, (sx, -1.86, .68), (.34, .03, .12)).parent = car

# ---------- lights ----------
b3d.light('SUN', 'Sun', (0, 0, 10), 2.2, (1, .85, .7), .4, rot=(50, 0, -35))
b3d.light('SUN', 'SkyFill', (0, 0, 10), .9, (.55, .65, 1), .8, rot=(35, 0, 150))
b3d.light('POINT', 'LoopGlow', (0, LY, 1.8), 40, (1, .8, .6), .5)

# ---------- signal balls ----------
def along(u):
    ds = [math.dist(a, b) for a, b in zip(PATH, PATH[1:])]; d = u * sum(ds)
    for a, b, l in zip(PATH, PATH[1:], ds):
        if d <= l: return tuple(p + (q - p) * d / max(l, 1e-6) for p, q in zip(a, b))
        d -= l
    return PATH[-1]
for k in range(5):
    bl = b3d.smooth(b3d.prim('uv_sphere', [sig], segments=16, ring_count=10, radius=.1))
    a, b = s5 + 8 + k * 7, e5 - 18 + k * 4
    for f in range(a, min(b, e5), 2):
        bl.location = along((f - a) / max(1, b - a)); bl.keyframe_insert('location', frame=f)
    bl.location = PATH[-1]; bl.keyframe_insert('location', frame=min(b, e5)); b3d.visible(bl, [(a, e5)])

# ---------- timeline ----------
cam, tgt = b3d.camera(30)
b3d.shot(cam, tgt, s1, e1, (-3.6, -9.5, 2.3), (-3.1, -8.2, 2.2), (1.2, 0, 1.6), lens=30)           # hook: car drives toward a red light
b3d.shot(cam, tgt, s2, e2, (-2.8, -6.6, 4.6), (-2.3, -5.8, 3.8), (.1, LY, .1), lens=30)            # slab lifts: wire loop in the pit
b3d.shot(cam, tgt, s3, e3, (-4.8, -6.6, 1.5), (-4.1, -6.0, 1.3), (0, LY, .75), lens=30)            # field over the loop
b3d.shot(cam, tgt, s4, e4, (-7.2, -5.6, 1.9), (-6.6, -5.1, 1.8), (0, LY - .4, .8), lens=30)        # car rolls in, field squashes and turns yellow
b3d.shot(cam, tgt, s5, e5, (5.0, -7.6, 3.4), (4.6, -6.9, 3.2), (2.3, -.9, 1.3), lens=30)           # signal to the box and up the pole
b3d.shot(cam, tgt, s6, e6, (1.4, -3.2, 1.0), (1.6, -2.6, 1.1), (PX, PY, 3.9), lens=32)             # light turns green
b3d.shot(cam, tgt, s7, e7, (-2.8, -7.5, 2.4), (-3.8, -11.5, 5.2), (.3, 1, 1.2), lens=30)           # end: car leaves

def ss(t): t = min(1, max(0, t)); return t * t * (3 - 2 * t)
for f, y in ((s1, -13), (e1 - 1, -6.5), (s4, -9.5), (s4 + int((e4 - s4) * .55), LY), (s7 + 6, LY), (e7 - 1, 11)):
    car.location = (0, y, 0); car.keyframe_insert('location', frame=f)
b3d.visible(car, [(s1, e1), (s4, e7)])

# lid lifts away in shot 2 only (flush everywhere else)
LOW = (0, LY, -.35); HIGH = (2.0, LY - .1, 1.35)
for f, p, rot in ((s2 - 1, LOW, 0), (s2 + 4, LOW, 0), (s2 + int((e2 - s2) * .45), HIGH, -18), (e2 - 1, HIGH, -18), (e2, LOW, 0)):
    lid.location = p; lid.rotation_euler = (0, math.radians(rot), 0); lid.keyframe_insert('location', frame=f); lid.keyframe_insert('rotation_euler', frame=f)

b3d.visible(xr, [(s3, e5)]); b3d.visible(fr, [(s3, e5)]); b3d.visible(wire, [(s5, e5)])
squash = s4 + int((e4 - s4) * .5)
for f in range(s3, e5, 3):
    pulse = 1 + .1 * math.sin((f - s3) / 30 * 2 * math.pi * 1.4); fall = 1 - .42 * ss((f - (squash - 12)) / 22)
    fr.scale = (1, 1, pulse * fall); fr.keyframe_insert('scale', frame=f)
b3d.key_input(field, 'Emission Color', [(s3, (.2, .65, 1)), (squash - 6, (.2, .65, 1)), (squash + 8, (1, .8, .15))])
b3d.key_input(field, 'Base Color', [(s3, (.2, .6, 1)), (squash - 6, (.2, .6, 1)), (squash + 8, (1, .8, .15))])

# light change near the middle of shot 6 (red -> yellow -> green); stays green in shot 7
a = s6 + int((e6 - s6) * .22); b = a + 18
b3d.key_input(red_l, 'Emission Strength', [(s1, 2.5), (a - 1, 2.5), (a + 2, 0.)])
b3d.key_input(yel_l, 'Emission Strength', [(a - 1, 0.), (a + 2, 2.5), (b - 1, 2.5), (b + 2, 0.)])
b3d.key_input(grn_l, 'Emission Strength', [(b - 1, 0.), (b + 2, 2.5)])

b3d.render(OUT, cfg.get('frames'))
