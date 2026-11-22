"""Muzlatkichda muz qotishi: upright freezer. Shot 1: door open, thick frost (no hook text, B variant); 2: frost thin, door
opens, warm humid air (orange) flows in, +25 / -18 labels; 3: vapour drifts to the cold back wall, frost grows; 4: side
cutaway, door closed, worn seal gap lets air stream in, frost thickens; 5: behind: compressor works hard (glow, shake);
6: No Frost heater glows, frost melts, drops run down to the drain; 7: pull back, door closes. 7 shots."""
import math, os, sys, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy
from mathutils import Vector

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.015, .025, .06), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))
R = math.radians
rnd = random.Random(11)

def keys(ob, attr, fv):
    for f, v in fv: setattr(ob, attr, v); ob.keyframe_insert(attr, frame=f)

def box(name, m, lo, hi):
    lo, hi = Vector(lo), Vector(hi)
    ob = b3d.prim('cube', [m], size=1, location=(lo + hi) / 2); ob.scale = hi - lo; ob.name = name; return ob

shell_m = b3d.mat('Shell', (.86, .88, .9), .3)
inner_m = b3d.mat('Inner', (.32, .42, .56), .4)
seal_m = b3d.mat('Seal', (.12, .12, .13), .8)
handle_m = b3d.mat('Handle', (.55, .57, .6), .2, metal=.8)
floor_m = b3d.mat('Floor', (.35, .3, .27), .7)
shelf_m = b3d.mat('Shelf', (.75, .85, .95), .1, emit=(.5, .7, 1), estr=.2)
frost_m = b3d.mat('Frost', (.93, .97, 1), .9, emit=(.7, .85, 1), estr=.35, bump=.6)
warm_m = b3d.mat('Warm', (1, .55, .15), .3, emit=(1, .5, .1), estr=4)
vap_m = b3d.mat('Vap', (.75, .9, 1), .3, emit=(.6, .85, 1), estr=3)
cold_m = b3d.mat('ColdLbl', (.3, .6, 1), .4, emit=(.3, .6, 1), estr=4)
water_m = b3d.mat('Water', (.75, .88, 1), .03, emit=(.6, .8, 1), estr=.8)
comp_m = b3d.mat('Comp', (.12, .13, .15), .5, metal=.4, emit=(1, .15, .05), estr=0)
coil_m = b3d.mat('Coil', (.1, .1, .1), .6)
heat_m = b3d.mat('Heat', (.3, .1, .08), .5, emit=(1, .2, .05), estr=0)
food = [b3d.mat(f'F{i}', c, .5) for i, c in enumerate([(.8, .2, .15), (.2, .55, .3), (.95, .75, .2), (.3, .4, .8)])]

# ---------- cabinet (outer x -.35..35, y -.3..35, z .08..1.6) ----------
X0, X1, Y0, Y1, Z0, Z1, T = -.35, .35, -.3, .35, .08, 1.6, .04
left = box('Left', shell_m, (X0, Y0, Z0), (X0 + T, Y1, Z1))
box('Right', shell_m, (X1 - T, Y0, Z0), (X1, Y1, Z1))
box('Back', shell_m, (X0, Y1 - T, Z0), (X1, Y1, Z1))
box('Top', shell_m, (X0, Y0, Z1 - T), (X1, Y1, Z1))
box('Bot', shell_m, (X0, Y0, Z0), (X1, Y1, Z0 + T))
for lo, hi in [((X0 + T, Y1 - T - .002, Z0 + T), (X1 - T, Y1 - T, Z1 - T)), ((X0 + T, Y0, Z1 - T - .002), (X1 - T, Y1 - T, Z1 - T)),
               ((X1 - T - .002, Y0, Z0 + T), (X1 - T, Y1 - T, Z1 - T)), ((X0 + T, Y0, Z0 + T), (X1 - T, Y1 - T, Z0 + T + .002))]:
    box('In', inner_m, lo, hi)
for x, y in [(-.3, -.25), (.3, -.25), (-.3, .3), (.3, .3)]:
    b3d.prim('cylinder', [seal_m], vertices=12, radius=.025, depth=.08, location=(x, y, .04))
IX0, IX1, IY0, IY1, IZ0, IZ1 = X0 + T, X1 - T, Y0, Y1 - T, Z0 + T, Z1 - T
for z in (.55, 1.05):
    box('Shelf', shelf_m, (IX0, IY0 + .03, z), (IX1, IY1, z + .015))
for i, (lo, hi) in enumerate([((-.25, -.1, .135), (-.05, .12, .3)), ((.02, -.05, .135), (.24, .2, .24)),
                               ((-.22, -.05, .565), (-.02, .18, .72)), ((.05, -.08, .565), (.22, .1, .66)),
                               ((-.2, 0, 1.065), (.15, .22, 1.18))]):
    b3d.smooth(box('Food', food[i % 4], lo, hi))
b3d.prim('plane', [floor_m], size=10, location=(0, 0, 0))

# door: hinge at the right front edge, swings out toward -y
hinge = b3d.empty('Hinge', (X1, Y0, 0))
door = box('Door', shell_m, (-.7, -.06, Z0), (0, 0, Z1)); door.parent = hinge
for lo, hi in [((-.69, -.005, Z0 + .01), (-.64, .01, Z1 - .01)), ((-.06, -.005, Z0 + .01), (-.01, .01, Z1 - .01)),
               ((-.69, -.005, Z0 + .01), (-.01, .01, Z0 + .05)), ((-.69, -.005, Z1 - .05), (-.01, .01, Z1 - .01))]:
    box('Gasket', seal_m, lo, hi).parent = hinge
hd = box('Handle', handle_m, (-.64, -.1, .85), (-.62, -.06, 1.3)); hd.parent = hinge
OPEN = R(105)
o2a, o2b = s2 + int((e2 - s2) * .25), s2 + int((e2 - s2) * .45)
c4 = s4
o6 = s6 + 6
c7a, c7b = s7 + int((e7 - s7) * .35), s7 + int((e7 - s7) * .7)
keys(hinge, 'rotation_euler', [(0, (0, 0, OPEN)), (e1 - 1, (0, 0, OPEN)), (s2, (0, 0, 0)), (o2a, (0, 0, 0)), (o2b, (0, 0, OPEN)),
                               (e3 - 1, (0, 0, OPEN)), (c4, (0, 0, 0)), (e5 - 1, (0, 0, 0)), (o6, (0, 0, OPEN)), (c7a, (0, 0, OPEN)), (c7b, (0, 0, 0))])
b3d.visible(left, [(0, s4), (e4, N + 1)])

# ---------- frost layers: thickness keyed (origin on the wall surface) ----------
TH = [(0, .055), (e1 - 1, .055), (s2, .003), (e2, .004), (s3 + 10, .006), (e3, .02), (s4 + 10, .022), (e4, .045), (e5, .045),
      (s6 + int((e6 - s6) * .2), .045), (s6 + int((e6 - s6) * .85), 0), (N, 0)]

def frost(name, c, axis, sign, ext):
    ob = b3d.prim('cube', [frost_m], size=1); ob.name = name; ob.visible_shadow = False
    for f, t in TH:
        loc = Vector(c); loc[axis] += sign * t / 2; scl = Vector(ext); scl[axis] = max(t, .0001)
        ob.location = loc; ob.scale = scl; ob.keyframe_insert('location', frame=f); ob.keyframe_insert('scale', frame=f)
    return ob
b3d.bsdf(frost_m).inputs['Alpha'].default_value = 1
try: frost_m.surface_render_method = 'BLENDED'
except Exception: pass
b3d.key_input(frost_m, 'Alpha', [(f, min(1., .15 + t / .025)) for f, t in TH])
W, D, Hh = IX1 - IX0, IY1 - IY0, IZ1 - IZ0
frost('FBack', (0, IY1, (IZ0 + IZ1) / 2), 1, -1, (W, 0, Hh))
frost('FLeft', (IX0, (IY0 + IY1) / 2 + .02, (IZ0 + IZ1) / 2), 0, 1, (0, D - .04, Hh))
frost('FRight', (IX1, (IY0 + IY1) / 2 + .02, (IZ0 + IZ1) / 2), 0, -1, (0, D - .04, Hh))
frost('FTop', (0, (IY0 + IY1) / 2 + .02, IZ1), 2, -1, (W, D - .04, 0))
# frost lumps on the back wall and ceiling grow with the layer
for k in range(55):
    on_top = k % 3 == 0
    loc = (rnd.uniform(IX0 + .03, IX1 - .03), rnd.uniform(IY0 + .08, IY1 - .03), IZ1) if on_top else \
          (rnd.uniform(IX0 + .03, IX1 - .03), IY1, rnd.uniform(IZ0 + .05, IZ1 - .03))
    lm = b3d.smooth(b3d.prim('uv_sphere', [frost_m], radius=rnd.uniform(.02, .045), segments=12, ring_count=8, location=loc))
    lm.visible_shadow = False
    for f, t in TH:
        k_ = t / .055; lm.scale = (k_, k_ * (1 if on_top else .6), k_ * (.6 if on_top else 1)); lm.keyframe_insert('scale', frame=f)

def label(txt, loc, m, size=.16):
    cu = bpy.data.curves.new('L', 'FONT'); cu.body = txt; cu.size = size; cu.align_x = 'CENTER'; cu.extrude = .01
    ob = b3d.link(bpy.data.objects.new('L', cu)); ob.data.materials.append(m); ob.location = loc
    ob.rotation_euler = (R(90), 0, 0); return ob
for o, rg in ((label('+25°', (-.7, -.6, 1.25), warm_m), [(o2b, e3)]), (label('-18°', (0, .05, 1.3), cold_m, .12), [(o2b, e3)])):
    b3d.visible(o, rg)

# ---------- warm humid air (shot 2) -> vapour to the back wall (shot 3) ----------
for k in range(34):
    bd = b3d.prim('uv_sphere', [warm_m], radius=.02, segments=12, ring_count=8); bd.visible_shadow = False
    t0 = o2b - 8 + rnd.randint(0, max(1, (e2 - o2b) // 2))
    st = Vector((rnd.uniform(-.6, .2), rnd.uniform(-1.4, -.9), rnd.uniform(.3, 1.4)))
    mid = Vector((rnd.uniform(-.25, .25), rnd.uniform(-.25, .05), rnd.uniform(.25, 1.45)))
    keys(bd, 'location', [(t0, st), (e2, mid)]); b3d.visible(bd, [(t0, e2 + 1)])
    vp = b3d.prim('uv_sphere', [vap_m], radius=.016, segments=12, ring_count=8); vp.visible_shadow = False
    end = Vector((mid.x * .9, IY1 - .02, mid.z))
    keys(vp, 'location', [(s3, mid), (s3 + rnd.randint(25, max(26, e3 - s3 - 8)), end)])
    keys(vp, 'scale', [(s3, (1, 1, 1)), (e3 - 3, (.4, .4, .4))])
    b3d.visible(vp, [(s3, e3)])

# ---------- shot 4: air sneaks in through the worn seal at the free door edge ----------
for i, z in enumerate((.45, .8, 1.15)):
    a = b3d.arrow(f'Leak{i}', (X0 - .35, Y0 - .25, z), (X0 + .12, Y0 + .18, z + .03), warm_m, r=.014)
    b3d.visible(a, [(s4 + 12, e4)])
for k in range(24):
    bd = b3d.prim('uv_sphere', [warm_m], radius=.014, segments=10, ring_count=6); bd.visible_shadow = False
    t0 = s4 + 10 + (k * 7) % max(1, (e4 - s4 - 40)); z = rnd.uniform(.3, 1.4)
    keys(bd, 'location', [(t0, (X0 - .4, Y0 - .3, z)), (t0 + 25, (X0 + .05, Y0 + .02, z)), (t0 + 45, (rnd.uniform(-.2, .2), IY1 - .03, z))])
    b3d.visible(bd, [(t0, min(t0 + 46, e4))])

# ---------- shot 5: compressor behind ----------
comp = b3d.smooth(b3d.prim('cylinder', [comp_m], vertices=32, radius=.1, depth=.18, location=(.12, .5, .18)))
b3d.smooth(b3d.prim('uv_sphere', [comp_m], radius=.1, segments=24, ring_count=12, location=(.12, .5, .27))).parent = None
b3d.key_input(comp_m, 'Emission Strength', [(s5, 0), (s5 + 15, 2.5), (e5 - 5, 3), (e5, 0)])
for f in range(s5, e5, 2):
    comp.location = (.12 + rnd.uniform(-.006, .006), .5 + rnd.uniform(-.006, .006), .18); comp.keyframe_insert('location', frame=f)
for k in range(8):  # condenser zigzag on the back
    box('Coil', coil_m, (-.3, Y1 + .02, .45 + k * .13), (.3, Y1 + .035, .46 + k * .13))
for x in (-.28, .28):
    box('CoilV', coil_m, (x, Y1 + .02, .45), (x + .015, Y1 + .035, 1.37))
tok = label('TOK ↑', (.12, .55, .62), warm_m, .12); tok.rotation_euler = (R(90), 0, R(180))
b3d.visible(tok, [(s5 + 15, e5)])

# ---------- shot 6: No Frost heater, melt drops to the drain ----------
for z in (.3, .75, 1.25):
    hr = b3d.prim('cylinder', [heat_m], vertices=12, radius=.012, depth=W - .06, location=(0, IY1 - .015, z), rotation=(0, R(90), 0))
b3d.key_input(heat_m, 'Emission Strength', [(0, 0), (s6 + 8, 0), (s6 + 25, 5), (e6 - 5, 5), (e6, 0)])
for k in range(26):
    x = rnd.uniform(IX0 + .04, IX1 - .04); z = rnd.uniform(.5, 1.45); t0 = s6 + int((e6 - s6) * rnd.uniform(.25, .65))
    dr = b3d.smooth(b3d.prim('uv_sphere', [water_m], radius=.012, segments=12, ring_count=8)); dr.scale = (1, .6, 1.3)
    keys(dr, 'location', [(t0, (x, IY1 - .015, z)), (t0 + 30, (x, IY1 - .015, IZ0 + .01)), (t0 + 42, (0, IY1 - .02, IZ0 - .02))])
    b3d.visible(dr, [(t0, min(t0 + 42, e6))])
box('Drain', seal_m, (-.03, IY1 - .04, IZ0 - .001), (.03, IY1 - .005, IZ0 + .002))

b3d.light('AREA', 'Key', (-1.4, -1.8, 2.4), 180, (1, .9, .78), 2.0, rot=(55, 0, -35))
b3d.light('POINT', 'Inside', (0, .05, 1.4), 18, (.75, .85, 1), .2)
b3d.light('AREA', 'Fill', (1.6, -1.2, 1.2), 60, (.6, .7, 1), 1.5, rot=(70, 0, 50))
b3d.light('AREA', 'Rim', (0, 2.2, 1.8), 90, (.6, .7, 1), 1.5, rot=(-60, 0, 0))

# ---------- camera ----------
cam, tgt = b3d.camera(24)
b3d.shot(cam, tgt, s1, e1, (-.5, -1.6, 1.05), (-.38, -1.38, 1.0), (0, .1, .85), lens=24)
b3d.shot(cam, tgt, s2, e2, (-.9, -2.3, 1.1), (-.8, -2.1, 1.05), (0, -.2, .85), lens=24)
b3d.shot(cam, tgt, s3, e3, (-.3, -1.25, 1.0), (-.2, -1.05, .95), (0, .3, .85), lens=22)
b3d.shot(cam, tgt, s4, e4, (-1.5, -.45, 1.0), (-1.4, -.25, .95), (0, 0, .85), lens=22)
b3d.shot(cam, tgt, s5, e5, (.95, 1.5, .75), (.8, 1.35, .7), (.05, .4, .45), lens=24)
b3d.shot(cam, tgt, s6, e6, (-.3, -1.4, .95), (-.25, -1.2, .9), (0, .3, .8), lens=22)
b3d.shot(cam, tgt, s7, e7, (-.4, -1.6, 1.0), (-.9, -2.8, 1.2), (0, 0, .85), lens=24)

b3d.render(OUT, cfg.get('frames'))
