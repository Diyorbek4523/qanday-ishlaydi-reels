"""Ekran: a phone on a table, its layers lifted apart. Under the glass a grid of wires holds a weak electric field; a fingertip draws
charge away at one crossing and only that crossing lights up. A thick glove changes nothing. 5 shots."""
import math, os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.05, .06, .13), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5) = list(zip(S[:-1], S[1:]))
T = (.2, -.45)  # touch point, on a grid crossing

# ---------- materials ----------
case = b3d.mat('Case', (.05, .05, .07), .3, metal=.6)
wood = b3d.mat('Table', (.36, .19, .09), .55, bump=.2)
wall = b3d.mat('Wall', (.12, .16, .28), .8)
wall_p = b3d.mat('Wallpaper', (.02, .03, .1), .3, emit=(.1, .17, .6), estr=.85)
glass = b3d.mat('Glass', (.75, .88, 1), .08, metal=.1)
b3d.bsdf(glass).inputs['Alpha'].default_value = .32
try: glass.surface_render_method = 'BLENDED'
except (AttributeError, TypeError): pass
wire_a = b3d.mat('WireA', (.05, .15, .3), .4, emit=(.2, .62, 1), estr=1.2)
wire_b = b3d.mat('WireB', (.03, .2, .18), .4, emit=(.1, .9, .75), estr=1.1)
node = b3d.mat('Node', (.06, .15, .3), .4, emit=(.35, .75, 1), estr=1.3)
hot = b3d.mat('Hot', (.06, .15, .3), .4, emit=(.35, .75, 1), estr=1.3)
spark = b3d.mat('Spark', (.2, .3, .4), .3, emit=(.7, .92, 1), estr=1.6)
charge = b3d.mat('Charge', (.4, .25, .03), .3, emit=(1, .72, .08), estr=1.7)
ring_m = b3d.mat('Ring', (.4, .3, .1), .3, emit=(1, .78, .2), estr=1.6)
skin = b3d.mat('Skin', (.82, .54, .4), .5)
nail = b3d.mat('Nail', (.95, .78, .72), .22)
wool = b3d.mat('Wool', (.13, .2, .42), .95, bump=.9)
wool2 = b3d.mat('Wool2', (.75, .2, .15), .95, bump=.9)
no_m = b3d.mat('No', (1, .12, .08), .4, emit=(1, .1, .06), estr=1.3)
cols = [(1, .35, .3), (.3, .85, .4), (1, .8, .2), (.4, .6, 1), (.85, .4, .95), (.3, .9, .9)]
icons = [b3d.mat(f'Ic{i}', tuple(x * .25 for x in c), .4, emit=c, estr=.95) for i, c in enumerate(cols)]

def box(m, c, s, bevel=0):
    b = b3d.prim('cube', [m], size=1, location=c); b.scale = s
    if bevel:
        bv = b.modifiers.new('Bv', 'BEVEL'); bv.width = bevel; bv.segments = 5; b3d.smooth(b)
    return b

# ---------- room and phone ----------
box(wood, (0, 2, -.5), (14, 14, 1))
b3d.prim('plane', [wall], size=30, location=(0, 8, 8), rotation=(math.radians(90), 0, 0))
box(case, (0, 0, .07), (1.62, 3.22, .14), bevel=.06)
box(wall_p, (0, 0, .145), (1.5, 3.08, .01))
for i in range(4):
    for j in range(5):
        box(icons[(i * 2 + j) % 6], (-.525 + .35 * i, 1.0 - .4 * j, .155), (.23, .23, .012), bevel=.04)
mug = b3d.lathe('Mug', [(.001, 0), (.42, 0), (.48, .08), (.48, 1.0), (.42, 1.0), (.42, .12), (.001, .12)]); mug.data.materials.append(b3d.mat('MugM', (.75, .22, .15), .35)); mug.location = (-2.1, 2.2, 0)

Gz = {'exp': .75, 'near': .36, 'flat': .19}; Lz = {'exp': 1.35, 'near': .62, 'flat': .17}
grid = b3d.empty('Grid', (0, 0, Gz['flat'])); hots = []
XS = [-.6 + .2 * i for i in range(7)]; YS = [-1.35 + .225 * j for j in range(13)]
for x in XS:
    w = b3d.prim('cylinder', [wire_b], vertices=8, radius=.011, depth=2.9, location=(x, 0, 0)); w.rotation_euler = (math.radians(90), 0, 0); w.parent = grid
for y in YS:
    w = b3d.prim('cylinder', [wire_a], vertices=8, radius=.011, depth=1.4, location=(0, y, 0)); w.rotation_euler = (0, math.radians(90), 0); w.parent = grid
for x in XS:
    for y in YS:
        close = math.hypot(x - T[0], y - T[1]) < .3
        n = b3d.smooth(b3d.prim('uv_sphere', [hot if close else node], segments=12, ring_count=8, radius=.028, location=(x, y, 0))); n.parent = grid
        if close: hots.append(n)
gl = box(glass, (0, 0, Lz['flat']), (1.6, 3.2, .05), bevel=.02)
try: gl.visible_shadow = False
except AttributeError: pass

def zkey(ob, pairs):
    for f, z in pairs:
        ob.location.z = z; ob.keyframe_insert('location', index=2, frame=f)
Fexp, Fcol = min(s2 + 22, e2 - 1), min(s5 + 18, e5 - 1)
zkey(grid, [(s1, Gz['flat']), (s2 + 4, Gz['flat']), (Fexp, Gz['exp']), (e2 - 1, Gz['exp']), (s3, Gz['near']), (s5, Gz['near']), (Fcol, Gz['flat'])])
zkey(gl, [(s1, Lz['flat']), (s2 + 4, Lz['flat']), (Fexp, Lz['exp']), (e2 - 1, Lz['exp']), (s3, Lz['near']), (s5, Lz['near']), (Fcol, Lz['flat'])])

# weak field: the grid pulses gently; sparks run along the wires
for f in range(s1, N, 15):
    b3d.key_input(node, 'Emission Strength', [(f, 1.9 + .9 * (f // 15 % 2))])
r = random.Random(4)
for k in range(16):
    d = b3d.smooth(b3d.prim('uv_sphere', [spark], segments=10, ring_count=6, radius=.022)); d.parent = grid; ph = r.random(); sp = r.uniform(.012, .022)
    alongx = k % 2 == 0; fix = r.choice(YS) if alongx else r.choice(XS); L = .7 if alongx else 1.45
    for f in range(s2, e4, 2):
        u = -L + 2 * L * ((ph + (f - s2) * sp) % 1)
        d.location = (u, fix, 0) if alongx else (fix, u, 0); d.keyframe_insert('location', frame=f)
    b3d.visible(d, [(s2, e4)])

# ---------- finger and glove ----------
def digit(name, m, rad, tip=None):
    root = b3d.empty(name); root.rotation_euler = (math.radians(-18), math.radians(38), 0)
    a = b3d.smooth(b3d.prim('uv_sphere', [m], segments=32, ring_count=20, radius=rad)); a.parent = root
    c = b3d.smooth(b3d.prim('cylinder', [m], vertices=32, radius=rad, depth=7, location=(0, 0, 3.5))); c.parent = root
    if tip:
        nl = b3d.smooth(b3d.prim('uv_sphere', [tip], segments=24, ring_count=16, radius=1)); nl.parent = root; nl.scale = (rad * .9, rad * .85, rad * 1.1); nl.location = (-rad * .2, 0, rad * .75)
    return root
fing = digit('Finger', skin, .24, nail)
glove = digit('Glove', wool, .36)
for z in (.7, .95, 1.2):  # knitted stripes
    st = b3d.smooth(b3d.prim('torus', [wool2], major_radius=.36, minor_radius=.05, major_segments=48, minor_segments=10, location=(0, 0, z))); st.parent = glove
Ft1 = s1 + int((e1 - s1) * .4); Ft3 = s3 + int((e3 - s3) * .22); Ft4 = s4 + int((e4 - s4) * .3)
def loc(ob, f, x, y, z): ob.location = (x, y, z); ob.keyframe_insert('location', frame=f)
top1, top3 = Lz['flat'] + .025, Lz['near'] + .025
for f, h in ((s1, 1.5), (Ft1, .0), (e1 - 1, .0)): loc(fing, f, T[0], T[1], top1 + .24 + h)
for f, h in ((s3, .9), (Ft3, 0), (e3 - 1, 0)): loc(fing, f, T[0], T[1], top3 + .24 + h)
for f, h in ((s4, .9), (Ft4, 0), (e4 - 1, 0)): loc(glove, f, T[0], T[1], top3 + .36 + h)
b3d.visible(fing, [(s1, e1), (s3, e3)]); b3d.visible(glove, [(s4, e4)])

# the crossing lights up only under the bare finger
b3d.key_input(hot, 'Emission Color', [(s1, (.35, .75, 1)), (Ft3 - 1, (.35, .75, 1)), (Ft3 + 3, (1, .62, .04)), (e3 - 1, (1, .62, .04)), (s4, (.35, .75, 1))])
b3d.key_input(hot, 'Emission Strength', [(s1, 1.3), (Ft3 - 1, 1.3), (Ft3 + 3, 2), (e3 - 1, 2), (s4, 1.3)])
for n in hots:
    n.scale = (1, 1, 1); n.keyframe_insert('scale', frame=Ft3 - 1); n.scale = (2.3, 2.3, 2.3); n.keyframe_insert('scale', frame=Ft3 + 4); n.keyframe_insert('scale', frame=e3 - 1); n.scale = (1, 1, 1); n.keyframe_insert('scale', frame=s4)
glow = b3d.light('POINT', 'TouchGlow', (T[0], T[1], .46), 0, (1, .75, .3), .2)
for f, v in ((Ft3 - 1, 0), (Ft3 + 3, 16), (e3 - 1, 16), (e3, 0)): glow.data.energy = v; glow.data.keyframe_insert('energy', frame=f)

# charge leaves the wire towards the fingertip
for k in range(14):
    d = b3d.smooth(b3d.prim('uv_sphere', [charge], segments=10, ring_count=6, radius=.02)); ph = k / 14; ang = k * 2.4; rd = .1 + .14 * (k % 3) / 2
    for f in range(Ft3, e3, 2):
        u = (ph + (f - Ft3) / 22) % 1
        d.location = (T[0] + rd * math.cos(ang) * (1 - u), T[1] + rd * math.sin(ang) * (1 - u), Gz['near'] + u * (Lz['near'] + .03 - Gz['near'])); d.keyframe_insert('location', frame=f)
    b3d.visible(d, [(Ft3, e3)])

# tap ripples on the screen in the hook shot
for ph in (0, .5):
    t = b3d.smooth(b3d.prim('torus', [ring_m], major_radius=1, minor_radius=.05, major_segments=48, minor_segments=8, location=(T[0], T[1], top1 + .01)))
    for f in range(Ft1, e1, 2):
        u = ((f - Ft1) / 24 + ph) % 1; v = .04 + .55 * u; t.scale = (v, v, 1 - u * .8 + .05); t.keyframe_insert('scale', frame=f)
    b3d.visible(t, [(Ft1, e1)])

# red cross beside the glove: nothing registered
cross = b3d.empty('Cross', (T[0] - .68, T[1] - .1, Lz['near'] + .5)); cross.rotation_euler = (math.radians(-25), 0, math.radians(-30))
for a in (45, -45):
    c = box(no_m, (0, 0, 0), (.42, .02, .08), bevel=.015); c.rotation_euler = (0, math.radians(a), 0); c.parent = cross
b3d.visible(cross, [(Ft4 + 6, e4)])

# ---------- lights ----------
b3d.light('AREA', 'Key', (2.5, -4, 6), 230, (1, .93, .84), 5, rot=(35, 0, 25))
b3d.light('AREA', 'Fill', (-5, -3, 3), 110, (.6, .72, 1), 4, rot=(65, 0, -55))
b3d.light('POINT', 'Rim', (1.5, 5, 4), 150, (.75, .82, 1), 1.5)

# ---------- timeline ----------
cam, tgt = b3d.camera(30)
b3d.shot(cam, tgt, s1, e1, (.5, -4.1, 4.6), (.25, -3.3, 3.9), (.05, -.15, .1), lens=30)             # hook: finger taps the phone
b3d.shot(cam, tgt, s2, e2, (-2.5, -4.6, 2.7), (-1.8, -3.9, 2.25), (0, -.1, .75), lens=30)           # layers lift apart: glass, wire grid, picture
b3d.shot(cam, tgt, s3, e3, (-.95, -2.15, 1.55), (-.7, -1.85, 1.35), (T[0], T[1], .5), lens=30)      # close: the crossing under the finger lights up
b3d.shot(cam, tgt, s4, e4, (-1.25, -2.4, 1.6), (-1.0, -2.1, 1.45), (T[0] - .1, T[1], .55), lens=30) # glove: grid stays blue
b3d.shot(cam, tgt, s5, e5, (.4, -3.4, 3.9), (.7, -5.6, 6.2), (0, -.1, .1), lens=30)                 # end: pull back from the phone

b3d.visible(grid, [(s2, e4)])  # invisible in normal use: only the lifted layers show it

b3d.render(OUT, cfg.get('frames'))
