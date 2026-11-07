"""Banka qopqog'i: a glass jar of hot jam on a kitchen table. The lid comes down and screws on while steam rises; as it
cools the steam (white) turns into droplets on the glass and only a few air molecules (blue) stay inside; outside air
(many molecules) presses the lid's safety button down (red arrows). Opening: the lid twists up, outside air rushes in,
the button pops back - "CHIRT!". Then a spoiled jar with a bulging lid and gas bubbles gets a red cross. 7 shots."""
import math, os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.03, .04, .09), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))

# ---------- materials ----------
table_m = b3d.mat('Table', (.36, .2, .1), .55, bump=.05)
wall_m = b3d.mat('Wall', (.55, .5, .42), .8)
tile_m = b3d.mat('Tile', (.75, .78, .8), .3)
glass = b3d.mat('Glass', (.75, .9, 1), .05)
b3d.bsdf(glass).inputs['Alpha'].default_value = .12
jam_m = b3d.mat('Jam', (.5, .04, .03), .2, emit=(1, .25, .05), estr=0)
lid_m = b3d.mat('Lid', (.95, .7, .25), .25, metal=1.0)
btn_m = b3d.mat('Button', (.95, .72, .3), .2, metal=1.0)
label_m = b3d.mat('Label', (.95, .9, .78), .7)
redl = b3d.mat('LabelRed', (.75, .12, .1), .6)
steam_m = b3d.mat('Steam', (1, 1, 1), .5, emit=(1, 1, 1), estr=1.2)
b3d.bsdf(steam_m).inputs['Alpha'].default_value = .6
drop_m = b3d.mat('Drop', (.6, .85, 1), .05, emit=(.4, .7, 1), estr=1.5)
air_m = b3d.mat('Air', (.1, .4, 1), .3, emit=(.1, .4, 1), estr=1.3)
push_m = b3d.mat('Push', (1, .3, .15), .4, emit=(1, .2, .05), estr=1.6)
pop_m = b3d.mat('Pop', (1, .8, .1), .3, emit=(1, .75, .1), estr=2.5)
bad_m = b3d.mat('Bad', (.9, .08, .05), .3, emit=(1, .05, .02), estr=2)
badjam = b3d.mat('BadJam', (.35, .3, .1), .4)
bub_m = b3d.mat('Bubble', (.8, .9, .6), .1, emit=(.6, .8, .4), estr=.8)
for m in (glass, steam_m):
    try: m.surface_render_method = 'BLENDED'
    except (AttributeError, TypeError): pass

def box(m, c, s, bevel=0):
    b = b3d.prim('cube', [m], size=1, location=c); b.scale = s
    if bevel:
        bv = b.modifiers.new('Bv', 'BEVEL'); bv.width = bevel; bv.segments = 4; b3d.smooth(b)
    return b
def ball(m, r, loc=(0, 0, 0), seg=12):
    return b3d.smooth(b3d.prim('uv_sphere', [m], segments=seg, ring_count=seg // 2, radius=r, location=loc))
def ease(u): u = min(1, max(0, u)); return u * u * (3 - 2 * u)
X90 = (math.radians(90), 0, 0)
rnd = random.Random(3)

T_LID = s2 + int((e2 - s2) * .55)
T_OPEN = s5 + int((e5 - s5) * .25)
T_POP = s5 + int((e5 - s5) * .55)

# ---------- kitchen ----------
box(table_m, (0, -1, -2.5), (12, 9, 5), bevel=.04)
box(wall_m, (0, 3.2, 3), (20, .2, 8))
for i in range(-8, 9):
    for j in range(0, 6): box(tile_m, (i * .62, 3.08, .4 + j * .62), (.58, .04, .58))

# ---------- jar ----------
def jar(name, x, jam_mat, lid_z):
    g = b3d.lathe(name + 'Glass', [(0, 0), (.84, 0), (.92, .1), (.92, 1.75), (.8, 1.98), (.78, 2.3), (.74, 2.3)]); g.data.materials.append(glass); g.location = (x, 0, 0)
    j = b3d.lathe(name + 'Jam', [(0, .03), (.85, .03), (.89, .1), (.89, 1.5), (0, 1.5)]); j.data.materials.append(jam_mat); j.location = (x, 0, 0)
    lb = b3d.lathe(name + 'Label', [(.935, .35), (.935, 1.05)]); lb.data.materials.append(label_m); lb.location = (x, 0, 0)
    st = b3d.lathe(name + 'Stripe', [(.94, .55), (.94, .68)]); st.data.materials.append(redl); st.location = (x, 0, 0)
    lid = b3d.empty(name + 'Lid', (x, 0, lid_z))
    c = b3d.prim('cylinder', [lid_m], vertices=48, radius=.86, depth=.26); c.parent = lid; b3d.smooth(c)
    rim = b3d.prim('torus', [lid_m], major_radius=.86, minor_radius=.04, major_segments=48, minor_segments=8); rim.parent = lid; rim.location = (0, 0, -.12)
    for k in range(24):  # ribs
        a = 2 * math.pi * k / 24; r_ = box(lid_m, (0, 0, 0), (.04, .04, .22)); r_.parent = lid; r_.location = (.87 * math.cos(a), .87 * math.sin(a), 0)
    btn = ball(btn_m, .38, seg=32); btn.parent = lid; btn.location = (0, 0, .13); btn.scale = (1, 1, .18)
    return g, j, lid, btn, lb, st

g, jam, lid, btn, _, _ = jar('J', 0, jam_m, 2.38)
for f, z, r in ((0, 3.15, 0), (s2 + 4, 3.15, 0), (T_LID, 2.38, -200), (T_OPEN, 2.38, -200), (T_OPEN + 14, 2.62, -110), (N, 2.62, -110)):
    lid.location.z = z; lid.keyframe_insert('location', frame=f); lid.rotation_euler = (0, 0, math.radians(r)); lid.keyframe_insert('rotation_euler', frame=f)
for f, sz in ((0, .18), (s3 + 10, .18), (s4 + 6, .02), (T_POP - 1, .02), (T_POP + 3, .26), (T_POP + 7, .16), (N, .18)):
    btn.scale = (1, 1, sz); btn.keyframe_insert('scale', frame=f)
for f, z in ((0, .13), (s3 + 10, .13), (s4 + 6, .07), (T_POP - 1, .07), (T_POP + 3, .14), (N, .13)):
    btn.location.z = z; btn.keyframe_insert('location', frame=f)
b3d.key_input(jam_m, 'Emission Strength', [(0, .9), (s3, .9), (e3, 0.), (N, 0.)])

# steam: rises out of the open jar in shot 2, fills the headspace, then shrinks onto the glass as drops in shot 3
steam = []
for k in range(26):
    p = ball(steam_m, rnd.uniform(.07, .12)); steam.append(p)
    a = rnd.uniform(0, 2 * math.pi); r0 = rnd.uniform(0, .6)
    for f in range(s1, T_LID, 3):  # rising, looping
        u = ((f - s1) / 40 + k / 26) % 1
        p.location = (r0 * math.cos(a) + .1 * math.sin(f / 7 + k), r0 * math.sin(a), 1.55 + u * 2.2); p.keyframe_insert('location', frame=f)
    for f in range(T_LID, s3 + 12, 3):  # trapped
        p.location = (rnd.uniform(-.6, .6), rnd.uniform(-.6, .6), rnd.uniform(1.6, 2.2)); p.keyframe_insert('location', frame=f)
    wa = rnd.uniform(0, 2 * math.pi); wz = rnd.uniform(1.6, 2.0); W = (.86 * math.cos(wa), .86 * math.sin(wa), wz)
    for f, loc, sz in ((s3 + 12, p.location[:], 1), (s3 + 40 + k, W, .45), (N, (W[0], W[1], wz - .25), .45)):
        p.location = loc; p.keyframe_insert('location', frame=f); p.scale = (sz,) * 3; p.keyframe_insert('scale', frame=f)
    b3d.visible(p, [(s1, s3 + 40 + k)])
    d = ball(drop_m, .045, W); b3d.visible(d, [(s3 + 40 + k, s5)])
    for f, z in ((s3 + 40 + k, wz), (s5, wz - .2)):
        d.location.z = z; d.keyframe_insert('location', frame=f)

# air molecules inside (few) and outside (many)
def jitter(p, box_, f0, f1, every=4):
    (x0, x1), (y0, y1), (z0, z1) = box_
    for f in range(f0, f1 + 1, every):
        p.location = (rnd.uniform(x0, x1), rnd.uniform(y0, y1), rnd.uniform(z0, z1)); p.keyframe_insert('location', frame=f)
inside = []
for k in range(5):
    p = ball(air_m, .06); jitter(p, ((-.55, .55), (-.55, .55), (1.6, 2.15)), s3, N); b3d.visible(p, [(s3, N)]); inside.append(p)
outside = []
for k in range(36):
    p = ball(air_m, .06); outside.append(p)
    a = rnd.uniform(0, 2 * math.pi); r_ = rnd.uniform(.2, 1.4); h = rnd.uniform(2.75, 3.6)
    home = (r_ * math.cos(a), r_ * math.sin(a), h)
    for f in range(s4, T_OPEN + 1, 4):
        p.location = (home[0] + rnd.uniform(-.12, .12), home[1] + rnd.uniform(-.12, .12), home[2] + rnd.uniform(-.12, .12)); p.keyframe_insert('location', frame=f)
    if k < 18:  # rush in through the gap under the lifted lid
        e = (.84 * math.cos(a), .84 * math.sin(a), 2.42); fin = (rnd.uniform(-.5, .5), rnd.uniform(-.5, .5), rnd.uniform(1.65, 2.1))
        t0 = T_OPEN + 4 + k // 3
        for f, loc in ((t0, e), (t0 + 6, fin)):
            p.location = loc; p.keyframe_insert('location', frame=f)
        jitter(p, ((-.55, .55), (-.55, .55), (1.6, 2.15)), t0 + 10, N)
    b3d.visible(p, [(s4, N)])
arrows = []
for k in range(5):
    a = 2 * math.pi * k / 5 + .3; x, y = .5 * math.cos(a), .5 * math.sin(a)
    if k == 4: x, y = 0, 0
    arr = b3d.arrow(f'Push{k}', (x, y, 3.55), (x, y, 2.75), push_m, r=.035); arrows.append(arr)
    b3d.visible(arr, [(s4 + 6, T_OPEN)])
# pop
ring = b3d.prim('torus', [pop_m], major_radius=1, minor_radius=.02, major_segments=48, minor_segments=6, location=(0, 0, 2.8))
for f, s_ in ((T_POP, .3), (T_POP + 12, 2.0)):
    ring.scale = (s_, s_, s_); ring.keyframe_insert('scale', frame=f)
b3d.visible(ring, [(T_POP, T_POP + 12)])
bpy.ops.object.text_add(location=(0, 0, 0)); txt = bpy.context.object; txt.data.body = 'CHIRT!'; txt.data.size = .5
txt.data.align_x = 'CENTER'; txt.data.extrude = .04; txt.data.materials.append(pop_m); txt.rotation_euler = X90
for f, loc, s_ in ((T_POP, (.25, -.6, 3.0), .3), (T_POP + 5, (.25, -.7, 3.25), .9), (T_POP + 9, (.25, -.7, 3.3), .8), (e5, (.25, -.7, 3.4), .8)):
    txt.location = loc; txt.keyframe_insert('location', frame=f); txt.scale = (s_,) * 3; txt.keyframe_insert('scale', frame=f)
b3d.visible(txt, [(T_POP, e5)])

# ---------- spoiled jar ----------
BX = 2.6
g2, jam2, lid2, btn2, lb2, st2 = jar('B', BX, badjam, 2.38)
btn2.scale = (1, 1, .45); btn2.location.z = .2
for k in range(14):
    b = ball(bub_m, rnd.uniform(.04, .09), seg=10)
    x0, y0 = rnd.uniform(-.6, .6), rnd.uniform(-.75, -.3)
    for f in range(s6, N + 1, 3):
        u = ((f - s6) / 45 + k / 14) % 1; b.location = (BX + x0, y0, .2 + 1.25 * u); b.keyframe_insert('location', frame=f)
    b3d.visible(b, [(s6, N)])
for o in (g2, jam2, lid2, lb2, st2): b3d.visible(o, [(s6, N)])
for o in b3d.tree(lid2): pass
cross = b3d.empty('Cross', (BX, -.3, 3.55)); cross.rotation_euler = X90
for a in (45, -45):
    c = box(bad_m, (0, 0, 0), (.16, .9, .1)); c.parent = cross; c.rotation_euler = (0, 0, math.radians(a))
for f, s_ in ((s6 + 10, .01), (s6 + 18, 1.15), (s6 + 22, 1.0)):
    cross.scale = (s_,) * 3; cross.keyframe_insert('scale', frame=f)
b3d.visible(cross, [(s6 + 10, N)])
upar = b3d.arrow('Bulge', (BX, -.95, 2.4), (BX, -.95, 2.95), bad_m, r=.03); b3d.visible(upar, [(s6 + 4, N)])

# ---------- lights ----------
b3d.light('AREA', 'Key', (3, -5, 6), 280, (1, .95, .88), 5, rot=(45, 0, 30))
b3d.light('AREA', 'Fill', (-4, -4, 3), 180, (.62, .74, 1), 4, rot=(70, 0, -40))
b3d.light('AREA', 'Rim', (0, 2.5, 5), 90, (1, .85, .7), 3, rot=(-40, 0, 0))
b3d.light('POINT', 'JamGlow', (0, -.3, 1.0), 25, (1, .5, .2), .4)

# ---------- timeline ----------
cam, tgt = b3d.camera(30)
b3d.shot(cam, tgt, s1, e1, (1.6, -5.4, 3.6), (1.3, -4.8, 3.3), (.1, 0, 2.0), lens=30)
b3d.shot(cam, tgt, s2, e2, (1.2, -5.0, 3.0), (1.0, -4.6, 3.1), (0, 0, 2.1), lens=30)
b3d.shot(cam, tgt, s3, e3, (.7, -2.8, 2.3), (.5, -2.5, 2.2), (0, 0, 1.85), lens=30)
b3d.shot(cam, tgt, s4, e4, (1.0, -3.6, 3.3), (.8, -3.3, 3.2), (0, 0, 2.6), lens=30)
b3d.shot(cam, tgt, s5, e5, (1.2, -4.0, 3.1), (1.0, -3.7, 3.0), (.3, 0, 2.5), lens=30)
b3d.shot(cam, tgt, s6, e6, (BX + .8, -4.4, 2.9), (BX + .6, -4.0, 2.8), (BX, 0, 1.9), lens=30)
b3d.shot(cam, tgt, s7, e7, (1.6, -5.0, 3.0), (2.2, -8.0, 4.2), (1.3, 0, 1.7), lens=30)
b3d.render(OUT, cfg.get('frames'))
