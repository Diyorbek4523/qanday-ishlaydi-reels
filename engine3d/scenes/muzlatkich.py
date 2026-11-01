"""Muzlatkich: the fridge makes no cold, it carries heat out. Refrigerant loop: evaporator (inside, cold, blue) -> compressor
(hot, red) -> condenser grid on the back (gives heat to the room) -> capillary -> back to the evaporator. 7 shots."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy
from mathutils import Vector

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.04, .05, .10), preview=cfg.get('preview'))
sh = list(zip(S[:-1], S[1:]))

# ---------- materials ----------
white = b3d.mat('Enamel', (.88, .9, .93), .35)
liner = b3d.mat('Liner', (.82, .9, .97), .5)
floor = b3d.mat('Floor', (.30, .22, .16), .8, bump=.1)
glass = b3d.mat('Shelf', (.6, .8, .9), .1)
handle = b3d.mat('Handle', (.5, .52, .56), .3, metal=.6)
black = b3d.mat('Comp', (.08, .08, .09), .45, metal=.4)
cond = b3d.mat('Cond', (.12, .1, .1), .5, metal=.3, emit=(1., .22, .03), estr=.3)
hotp = b3d.mat('HotPipe', (.3, .12, .08), .4, metal=.4, emit=(1., .18, .03), estr=1.2)
copper = b3d.mat('Copper', (.75, .4, .2), .35, metal=.8)
evap = b3d.mat('Evap', (.6, .85, 1.), .3, emit=(.1, .5, 1.), estr=.9)
retp = b3d.mat('RetPipe', (.45, .55, .65), .4, metal=.5)
heat = b3d.mat('Heat', (1, .2, .03), .5, emit=(1., .16, .02), estr=1.8)
foods = [b3d.mat(n, c, .5) for n, c in (('Tomato', (.8, .12, .08)), ('Bottle', (.15, .55, .25)), ('Juice', (.95, .55, .1)),
                                         ('Cheese', (.95, .8, .25)), ('Milk', (.92, .93, .95)), ('Ice', (.7, .85, .95)), ('Meat', (.7, .25, .25)))]

def box(name, x0, x1, y0, y1, z0, z1, m):
    ob = b3d.prim('cube', [m], size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)); ob.scale = (x1 - x0, y1 - y0, z1 - z0); ob.name = name
    bv = ob.modifiers.new('Bv', 'BEVEL'); bv.width = min(.012, (min(x1 - x0, y1 - y0, z1 - z0)) * .3); bv.segments = 3
    return ob

def tube(name, pts, r, m):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 3; cu.use_fill_caps = True
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for p, v in zip(sp.points, pts): p.co = (*v, 1)
    ob = b3d.link(bpy.data.objects.new(name, cu)); cu.materials.append(m); return ob

def serpentine(xa, xb, y, zs):
    """Rows at heights zs, from xa to xb then back, joined by half-circle bends outside [xa, xb]."""
    pts = []
    for k, z in enumerate(zs):
        a, b = (xa, xb) if k % 2 == 0 else (xb, xa); pts += [(a, y, z), (b, y, z)]
        if k + 1 < len(zs):
            r = (z - zs[k + 1]) / 2; c = z - r; s = 1 if b > a else -1
            pts += [(b + s * r * math.sin(t * math.pi / 8), y, c + r * math.cos(t * math.pi / 8)) for t in range(1, 8)]
    return pts

# ---------- fridge body (front is -Y). freezer above the divider ----------
X, Y0, Y1, Z0, Z1, T = .36, -.32, .34, .06, 1.85, .05
box('Back', -X, X, Y1 - T, Y1, Z0, Z1, white); box('Left', -X, -X + T, Y0, Y1, Z0, Z1, white)
right = box('Right', X - T, X, Y0, Y1, Z0, Z1, white)
box('Top', -X, X, Y0, Y1, Z1 - T, Z1, white); box('Bottom', -X, X, Y0, Y1, Z0, Z0 + T, white); box('Divider', -X, X, Y0, Y1, 1.22, 1.27, white)
box('LinerBack', -X + T, X - T, Y1 - T - .01, Y1 - T, Z0 + T, Z1 - T, liner)
for z in (.47, .84): box(f'Shelf{z}', -X + T, X - T, Y0 + .03, Y1 - T - .01, z, z + .015, glass)
for x in (-.3, .3):
    for y in (-.26, .28): b3d.prim('cylinder', [black], vertices=12, radius=.025, depth=.06, location=(x, y, .03))
doors = [box('DoorF', -X, X, Y0 - .05, Y0, 1.275, Z1, white), box('DoorR', -X, X, Y0 - .05, Y0, Z0, 1.245, white)]
for z0, z1 in ((1.33, 1.6), (.75, 1.15)): doors.append(box(f'Handle{z0}', -.31, -.28, Y0 - .11, Y0 - .05, z0, z1, handle))
ground = b3d.prim('plane', [floor], size=30)

# food on shelves
def food(kind, m, loc, s):
    if kind == 'bottle': ob = b3d.prim('cylinder', [m], vertices=24, radius=s, depth=s * 6, location=(loc[0], loc[1], loc[2] + s * 3))
    elif kind == 'ball': ob = b3d.prim('uv_sphere', [m], segments=24, ring_count=12, radius=s, location=(loc[0], loc[1], loc[2] + s))
    else: ob = box('Food', loc[0] - s, loc[0] + s, loc[1] - s * .8, loc[1] + s * .8, loc[2], loc[2] + s * 1.2, m)
    return b3d.smooth(ob) if kind != 'box' else ob
items = [food('bottle', foods[1], (-.2, .05, .115), .04), food('bottle', foods[2], (-.08, .1, .115), .045), food('box', foods[4], (.15, 0, .115), .09),
         food('ball', foods[0], (-.15, -.1, .485), .05), food('ball', foods[0], (-.04, -.12, .485), .045), food('box', foods[3], (.17, .02, .485), .08),
         food('bottle', foods[2], (.2, .05, .855), .035), food('box', foods[6], (-.1, 0, .855), .1),
         food('box', foods[5], (-.15, -.05, 1.27), .08), food('box', foods[6], (.13, -.08, 1.27), .07), food('box', foods[5], (.12, -.05, 1.37), .06)]

# ---------- refrigerant loop ----------
comp = b3d.lathe('Compressor', [(0, -.11), (.1, -.11), (.12, -.08), (.12, .04), (.11, .08), (.07, .11), (0, .115)]); comp.data.materials.append(black); comp.location = (.12, .5, .16)
box('CompBase', -.06, .3, .36, .64, .03, .05, handle)
b3d.prim('cylinder', [copper], vertices=12, radius=.012, depth=.06, location=(.12, .5, .29))
hot_pts = [(.12, .5, .28), (.12, .5, .32), (.33, .44, .34), (.33, .41, 1.67), (.30, .40, 1.67)]
cond_pts = serpentine(.28, -.28, .40, [1.67 - k * .1625 for k in range(9)])  # 9 rows -> ends on the left (x = -.28) at z .37
cap_pts = [(-.34, .40, .37), (-.34, .40, 1.74), (-.28, .27, 1.74)]
evap_pts = serpentine(-.26, .26, .27, [1.74, 1.61, 1.48, 1.35])  # 4 rows -> ends on the left
ret_pts = [(-.30, .27, 1.35), (-.22, .45, 1.35), (-.22, .47, .30), (.0, .5, .24), (.06, .5, .2)]
tube('HotTube', hot_pts, .014, hotp); tube('CondTube', cond_pts, .012, cond); tube('Capillary', cap_pts, .006, copper)
tube('EvapTube', evap_pts, .014, evap); tube('RetTube', ret_pts, .014, retp)
for z in (.5, 1.1, 1.55):  # condenser grid wires
    for x in (-.2, 0, .2): box(f'Wire{x}{z}', x - .004, x + .004, .395, .405, .3, 1.7, cond)

loop = hot_pts + cond_pts + cap_pts + evap_pts + ret_pts
L = [0.]
for a, b in zip(loop, loop[1:]): L.append(L[-1] + (Vector(b) - Vector(a)).length)
TOT = L[-1]; HOT_END = L[len(hot_pts) - 1]; COND_END = L[len(hot_pts) + len(cond_pts) - 1]; EVAP_END = L[len(loop) - len(ret_pts)]
def at(s):
    s %= TOT
    for i in range(len(L) - 1):
        if L[i] <= s <= L[i + 1]:
            t = (s - L[i]) / max(1e-6, L[i + 1] - L[i]); return Vector(loop[i]).lerp(Vector(loop[i + 1]), t)
    return Vector(loop[-1])
RED, BLUE = Vector((1., .08, .02)), Vector((.02, .35, 1.))
def col(s):
    s %= TOT
    if s < HOT_END: c = RED
    elif s < COND_END: c = RED.lerp(BLUE, (s - HOT_END) / (COND_END - HOT_END))
    elif s < EVAP_END: c = BLUE
    else: c = BLUE.lerp(Vector((.7, .5, 1.)), (s - EVAP_END) / (TOT - EVAP_END))
    return tuple(c)

NP, SPEED = 26, TOT / (8 * b3d.FPS)  # one loop every 8 s
dots = []
for k in range(NP):
    m = b3d.mat(f'Dot{k}', (1, 1, 1), .4, emit=(1, 1, 1), estr=2.2)
    d = b3d.prim('uv_sphere', [m], segments=12, ring_count=8, radius=.024); b3d.smooth(d); dots.append(d)
    for f in range(0, N + 1, 2):
        s = k * TOT / NP + f * SPEED; d.location = at(s); d.keyframe_insert('location', frame=f)
        c = col(s); b3d.bsdf(m).inputs['Emission Color'].default_value = (*c, 1); b3d.bsdf(m).inputs['Emission Color'].keyframe_insert('default_value', frame=f)
        b3d.bsdf(m).inputs['Base Color'].default_value = (*c, 1); b3d.bsdf(m).inputs['Base Color'].keyframe_insert('default_value', frame=f)

# ---------- heat arrows ----------
heat_in = [b3d.arrow(f'In{k}', a, b, heat, r=.016) for k, (a, b) in enumerate([((-.15, -.12, 1.42), (-.12, .18, 1.58)), ((.13, -.15, 1.45), (.1, .18, 1.62)),
                                                                                ((0, -.2, 1.33), (0, .16, 1.45))])]
heat_out = [b3d.arrow(f'Out{k}', (x, .46, z), (x * 1.3, .9, z + .12), heat, r=.022) for k, (x, z) in enumerate([(-.2, .55), (.2, .7), (0, 1.0), (-.2, 1.3), (.2, 1.5)])]

# ---------- lights ----------
b3d.light('SUN', 'Sun', (0, 0, 5), 2.0, (1, .85, .7), .3, rot=(55, 0, -30))
b3d.light('AREA', 'Fill', (-2.5, -2.5, 2.5), 150, (.6, .7, 1), 3, rot=(55, 0, -45))
b3d.light('AREA', 'Back', (1.5, 2.5, 2.2), 120, (.8, .8, 1), 2.5, rot=(-55, 0, 150))
b3d.light('POINT', 'InFridge', (0, -.05, .7), 18, (.85, .93, 1), .2)
b3d.light('POINT', 'InFreezer', (0, -.1, 1.55), 8, (.8, .9, 1), .15)
cglow = b3d.light('POINT', 'CondGlow', (0, .7, 1.0), 0, (1, .45, .15), .5)

# ---------- timeline ----------
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = sh
cam, tgt = b3d.camera(30)
C = (0, 0, .95)
b3d.shot(cam, tgt, s1, e1, (1.2, -2.6, 1.45), (.9, -2.15, 1.35), C, lens=30)             # hook: open fridge, food, cool light
b3d.shot(cam, tgt, s2, e2, (-1.5, -2.3, 1.2), (-.7, -2.6, 1.1), C, lens=30)              # closed, orbit
b3d.shot(cam, tgt, s3, e3, (2.7, 1.9, 1.35), (2.4, 1.2, 1.25), (0, .15, .95), lens=30)   # side-back cutaway: the whole loop
b3d.shot(cam, tgt, s4, e4, (.3, -1.15, 1.58), (.15, -.9, 1.55), (0, .15, 1.52), lens=30)  # freezer: evaporator takes the heat
b3d.shot(cam, tgt, s5, e5, (.95, 1.3, .42), (.72, 1.08, .36), (.08, .48, .3), lens=30)    # compressor squeezes, gets hot
b3d.shot(cam, tgt, s6, e6, (.5, 2.7, 1.15), (.2, 2.3, 1.05), (0, .4, .95), lens=30)      # back grid gives heat to the room
b3d.shot(cam, tgt, s7, e7, (.9, -2.0, 1.2), (1.6, -3.8, 1.7), C, lens=30)                # end: pull back

for d in doors: b3d.visible(d, [(s2, e2), (s3, e3), (s5, e7)])
b3d.visible(right, [(0, s3), (e3, N + 1)])
for d in dots: b3d.visible(d, [(s1, e1), (s3, e6)])
for a in heat_in: b3d.visible(a, [(s3 + 15, e3), (s4 + 10, e4)])
for a in heat_out: b3d.visible(a, [(s3 + 15, e3), (s6 + 10, e6)])

b3d.key_input(cond, 'Emission Strength', [(s1, .3), (s6, .3), (s6 + 20, 1.4), (e6, 1.4), (e6 + 1, .3)])
b3d.key_input(hotp, 'Emission Strength', [(s1, 1.2), (s5, 1.2), (s5 + 25, 2.5), (e6, 2.5), (e6 + 1, 1.2)])
for f, v in ((s1, 0), (s6, 0), (s6 + 20, 60), (e6, 60), (e6 + 1, 0)): cglow.data.energy = v; cglow.data.keyframe_insert('energy', frame=f)
import random
rr = random.Random(3)
for f in range(s5, e5, 2): comp.location = (.12 + rr.uniform(-.004, .004), .5 + rr.uniform(-.004, .004), .16); comp.keyframe_insert('location', frame=f)  # hum/vibrate
comp.location = (.12, .5, .16); comp.keyframe_insert('location', frame=e5)

b3d.render(OUT, cfg.get('frames'))
