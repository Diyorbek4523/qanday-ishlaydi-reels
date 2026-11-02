"""Telefon qish: phone in the snow; inside the battery lithium ions swim fast through warm electrolyte and crawl through cold thick
electrolyte; the phone dies at 34%, then back on a warm table the 34% returns. 7 shots. Battery at x = 40, warm table at x = 80."""
import math, os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.03, .05, .12), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))
X_B, X_W = 40., 80.

# ---------- materials ----------
case = b3d.mat('Case', (.05, .05, .07), .3, metal=.6)
snow_m = b3d.mat('SnowG', (.8, .86, .97), .75, bump=.5)
flake = b3d.mat('Flake', (.9, .95, 1), .5, emit=(.85, .92, 1), estr=1.4)
wood = b3d.mat('Table', (.34, .18, .08), .9, bump=.2)
txt_m = b3d.mat('Txt', (1, 1, 1), .5, emit=(1, 1, 1), estr=3)
txt_w = b3d.mat('TxtW', (1, 1, 1), .5, emit=(1, 1, 1), estr=3)
shell = b3d.mat('Shell', (.32, .34, .38), .4, metal=.7)
anode = b3d.mat('Anode', (.1, .1, .12), .6, bump=.5)
cathode = b3d.mat('Cathode', (.1, .42, .5), .45, metal=.3, bump=.3)
elec = b3d.mat('Elec', (.75, .42, .1), .6, emit=(.85, .4, .06), estr=.45)
ion = b3d.mat('Ion', (1, .85, .2), .3, emit=(1, .75, .08), estr=2)
thick = b3d.mat('Thick', (.45, .68, .95), .35, emit=(.3, .55, .95), estr=.7)
frost = b3d.mat('Frost', (.9, .95, 1), .5, emit=(.7, .85, 1), estr=.5)
foil = b3d.mat('Foil', (.75, .55, .3), .35, metal=.8)
mug_m = b3d.mat('Mug', (.75, .25, .12), .35)
grain_a = b3d.mat('GrainA', (.2, .2, .23), .5)
grain_c = b3d.mat('GrainC', (.2, .65, .72), .4)

def box(m, c, s, name=None, bevel=0):
    b = b3d.prim('cube', [m], size=1, location=c); b.scale = s
    if name: b.name = name
    if bevel:
        bv = b.modifiers.new('Bv', 'BEVEL'); bv.width = bevel; bv.segments = 5; b3d.smooth(b)
    return b

def phone(x, z, tilt, name, tm):
    """Upright phone. Returns the black 'off' panel and the 34% UI parts, each toggled with visible()."""
    root = b3d.empty(name, (x, 0, z)); root.rotation_euler = (math.radians(tilt), 0, 0)
    screen = b3d.mat(name + 'Scr', (.02, .02, .04), .15, emit=(.08, .2, .55), estr=1.3)
    black = b3d.mat(name + 'Off', (.015, .015, .02), .08, metal=.2)
    fillm = b3d.mat(name + 'Fill', (1, .55, .05), .4, emit=(1, .5, .05), estr=3)
    box(case, (0, 0, 0), (1.05, .1, 2.15), bevel=.05).parent = root
    box(screen, (0, -.052, 0), (.97, .006, 2.07)).parent = root
    off = box(black, (0, -.056, 0), (.97, .006, 2.07)); off.parent = root
    fc = bpy.data.curves.new(name + 'Pct', 'FONT'); fc.body = '34%'; fc.size = .42; fc.align_x = 'CENTER'; fc.align_y = 'CENTER'; fc.extrude = .002
    t = b3d.link(bpy.data.objects.new(name + 'Pct', fc)); fc.materials.append(tm); t.rotation_euler = (math.radians(90), 0, 0); t.parent = root; t.location = (0, -.062, .1)
    icon = box(tm, (0, -.060, -.32), (.46, .002, .2)); icon.parent = root                       # white outline, dark inner, orange level
    inner = box(case, (0, -.062, -.32), (.42, .002, .16)); inner.parent = root
    fill = box(fillm, (-.21 + .42 * .17, -.064, -.32), (.42 * .34, .002, .16)); fill.parent = root
    tip = box(tm, (.26, -.060, -.32), (.04, .002, .09)); tip.parent = root
    return off, [t, icon, inner, fill, tip]

# ---------- snowy location at x = 0 ----------
b3d.prim('plane', [snow_m], size=60, location=(0, 10, 0))
r = random.Random(7)
for dx, dy, sx, sy, sz in ((-.95, -.25, .9, .7, .35), (.95, -.1, .8, .7, .28), (0, -.5, 1.1, .55, .24), (0, .7, 1.8, .9, .4), (-2.8, 2.5, 2.2, 1.8, .8), (3.2, 3.5, 2.8, 2, 1.1), (-5, 6, 3.5, 2, 1.6), (5.5, 8, 4, 2, 2)):
    d = b3d.smooth(b3d.prim('ico_sphere', [snow_m], subdivisions=4, radius=1, location=(dx, dy, 0))); d.scale = (sx, sy, sz)
pine = b3d.mat('Pine', (.08, .22, .2), .8)
for tx, ty in ((-4, 5), (4.5, 7), (-7, 9), (7.5, 10), (.5, 12)):
    for rad, zz in ((1.1, 1.2), (.85, 2.2), (.55, 3.1)):
        b3d.prim('cone', [pine], vertices=24, radius1=rad, depth=1.5, location=(tx, ty, zz))
for k in range(90):
    fl = b3d.prim('ico_sphere', [flake], subdivisions=1, radius=r.uniform(.012, .028))
    x0, y0, z0, v, ph = r.uniform(-3.5, 3.5), r.uniform(-2.5, 4), r.uniform(0, 5), r.uniform(.008, .016), r.uniform(0, 6)
    for f in range(0, N + 1, 12):
        fl.location = (x0 + .15 * math.sin(f * .04 + ph), y0, 5 - ((5 - z0) + f * v) % 5); fl.keyframe_insert('location', frame=f)
snow_off, snow_ui = phone(0, 1.18, 8, 'Snow', txt_m)

# ---------- battery cell at x = X_B ----------
W, H = 2.3, 3.2
box(elec, (X_B, .3, 0), (W, .05, H), 'ElecBack')
box(shell, (X_B, .4, 0), (W + .34, .15, H + .34), bevel=.08)
for sx in (-1, 1):
    box(shell, (X_B + sx * (W / 2 + .1), 0, 0), (.2, .8, H + .34), bevel=.05)
    box(anode if sx < 0 else cathode, (X_B + sx * .85, 0, 0), (.6, .55, H - .04), bevel=.03)
    box(foil, (X_B + sx * 1.08, 0, 0), (.08, .6, H), bevel=.01)
for sz in (-1, 1): box(shell, (X_B, 0, sz * (H / 2 + .1)), (W + .34, .8, .2), bevel=.05)
for k in range(9):    # grain lines on the electrodes
    zz = -1.4 + k * .35
    box(grain_a, (X_B - .85, -.277, zz), (.58, .004, .05)); box(grain_c, (X_B + .85, -.277, zz), (.58, .004, .05))

# frost and thick blobs grow in during the cold shot
cold_at = s4 + 8
for k in range(40):
    b = b3d.smooth(b3d.prim('ico_sphere', [thick], subdivisions=2, radius=r.uniform(.09, .16), location=(X_B + r.uniform(-.5, .5), r.uniform(-.1, .1), r.uniform(-1.45, 1.45))))
    for f, s in ((cold_at - 1, .001), (cold_at + 14, 1.)): b.scale = (s, s, s); b.keyframe_insert('scale', frame=f)
for k in range(70):
    side = r.choice(((-1, 0), (1, 0), (0, -1), (0, 1)))
    px = X_B + (side[0] * (W / 2 + .2) if side[0] else r.uniform(-W / 2 - .2, W / 2 + .2)); pz = side[1] * (H / 2 + .2) if side[1] else r.uniform(-H / 2 - .2, H / 2 + .2)
    b = b3d.prim('ico_sphere', [frost], subdivisions=1, radius=r.uniform(.04, .11), location=(px, -.38, pz)); b.rotation_euler = (r.random(), r.random(), r.random())
    for f, s in ((cold_at + 2, .001), (cold_at + 20, 1.)): b.scale = (s, s, s); b.keyframe_insert('scale', frame=f)

# ions: each lane shuttles from anode to cathode; speed is high in shot 3, near stop once cold
X0, X1 = X_B - .52, X_B + .52
for k in range(20):
    i = b3d.smooth(b3d.prim('uv_sphere', [ion], segments=16, ring_count=10, radius=.075))
    pos, z, y, wob = r.random(), r.uniform(-1.42, 1.42), r.uniform(-.22, -.14), r.uniform(0, 6)
    for f in range(s2, e4, 2):
        sp = .018 if f < s3 else (.05 if f < cold_at else (.005 if f > cold_at + 14 else .05 - .045 * (f - cold_at) / 14))
        pos = (pos + sp * 2) % 1
        i.location = (X0 + (X1 - X0) * pos, y, z + .05 * math.sin(f * .25 + wob)); i.keyframe_insert('location', frame=f)

# ---------- warm table at x = X_W ----------
box(wood, (X_W, 1, -.1), (14, 12, .2))
box(b3d.mat('Wall', (.6, .36, .18), .8), (X_W, 6, 4), (14, .2, 8.5))
warm_off, warm_ui = phone(X_W, 1.2, 12, 'Warm', txt_w)
box(case, (X_W, .42, .5), (.7, .06, 1.1)).rotation_euler = (math.radians(-22), 0, 0)   # stand
mug = b3d.lathe('Mug', [(.001, 0), (.42, 0), (.46, .05), (.46, .9), (.4, .9), (.38, .1), (.001, .1)]); mug.data.materials.append(mug_m); mug.location = (X_W + 1.35, 1.0, 0)
b3d.light('POINT', 'WarmLamp', (X_W + 1.8, -1.6, 2.6), 140, (1, .68, .36), 1.2)
b3d.light('POINT', 'WarmFill', (X_W - 1.8, -2, 1.8), 50, (1, .8, .6), 1)

# ---------- lights ----------
b3d.light('SUN', 'Moon', (0, 0, 8), 1.4, (.65, .75, 1), .5, rot=(55, 0, 25))
b3d.light('AREA', 'SnowKey', (-1.5, -3.5, 3), 110, (.85, .9, 1), 4, rot=(55, 0, -20))
b3d.light('AREA', 'BatKey', (X_B - .5, -4, 2), 260, (1, .96, .9), 5, rot=(65, 0, -8))
b3d.light('POINT', 'BatFill', (X_B + 2, -2, -1), 70, (.7, .8, 1), 1)

# ---------- timeline ----------
cam, tgt = b3d.camera(30)
b3d.shot(cam, tgt, s1, e1, (-.9, -4.5, 1.95), (-.5, -3.8, 1.8), (0, 0, 1.35), lens=30)             # hook: phone in the snow
b3d.shot(cam, tgt, s2, e2, (X_B - .5, -4.9, .4), (X_B - .15, -4.3, .3), (X_B, 0, .05), lens=30)      # cell opened, ions drift
b3d.shot(cam, tgt, s3, e3, (X_B + .5, -3.0, .35), (X_B + .1, -2.6, .3), (X_B, 0, .1), lens=30)      # ions zip across
b3d.shot(cam, tgt, s4, e4, (X_B - .3, -3.6, .3), (X_B + .2, -3.3, .3), (X_B, 0, .05), lens=30)      # cold: thick, frost, ions crawl
b3d.shot(cam, tgt, s5, e5, (.7, -3.8, 1.65), (.3, -3.1, 1.55), (0, 0, 1.3), lens=30)                # phone dies with charge left
b3d.shot(cam, tgt, s6, e6, (X_W - .7, -3.8, 1.7), (X_W - .3, -3.1, 1.6), (X_W, 0, 1.3), lens=30)    # warm: 34% back
b3d.shot(cam, tgt, s7, e7, (X_W - .4, -3.1, 1.6), (X_W - .8, -6.8, 2.4), (X_W + .2, 0, 1.35), lens=30)  # end: pull back

# phone screens
off_at = s5 + int((e5 - s5) * .68); on_at = s6 + int((e6 - s6) * .35)
b3d.visible(snow_off, [(off_at, N)])
for o in snow_ui: b3d.visible(o, [(0, off_at)])
b3d.visible(warm_off, [(s6, on_at)])
for o in warm_ui: b3d.visible(o, [(on_at, N)])
b3d.key_input(elec, 'Emission Color', [(s2, (.85, .42, .08)), (cold_at, (.85, .42, .08)), (cold_at + 16, (.12, .3, .75))])
b3d.key_input(elec, 'Base Color', [(s2, (.75, .42, .1)), (cold_at, (.75, .42, .1)), (cold_at + 16, (.15, .3, .7))])
b3d.key_input(txt_m, 'Emission Color', [(s5, (1, 1, 1)), (s5 + 10, (1, .25, .15))])
b3d.key_input(txt_m, 'Emission Strength', [(s5, 3.), (s5 + 10, 1.3)])

b3d.render(OUT, cfg.get('frames'))
