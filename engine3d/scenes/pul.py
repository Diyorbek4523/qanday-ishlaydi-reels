"""Pul: why banknotes survive the wash. Notes tumbling in a washer; in a water tank a paper sheet falls apart while a note stays whole;
cotton boll spins long fibres into a note; macro of tangled fibres with water passing through. 5 shots, one station per idea along X."""
import math, os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.05, .07, .13), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5) = list(zip(S[:-1], S[1:]))
BX, CX, DX = 20, 40, 60

# ---------- materials ----------
white = b3d.mat('White', (.78, .8, .84), .3)
dark = b3d.mat('Dark', (.05, .05, .07), .4)
steel = b3d.mat('Steel', (.6, .63, .68), .3, metal=.85)
drum_m = b3d.mat('DrumM', (.16, .18, .23), .5, metal=.5)
chrome = b3d.mat('Chrome', (.75, .77, .8), .15, metal=1)
screen = b3d.mat('Screen', (.05, .3, .3), .3, emit=(.15, .9, .75), estr=2)
tile = b3d.mat('Tile', (.3, .34, .4), .5, bump=.08)
wall = b3d.mat('Wall', (.12, .18, .27), .85)
water = b3d.mat('Water', (.2, .55, .95), .1, emit=(.05, .3, .75), estr=.5)
b3d.bsdf(water).inputs['Alpha'].default_value = .26
try: water.surface_render_method = 'BLENDED'
except (AttributeError, TypeError): pass
drop = b3d.mat('Drop', (.3, .65, 1), .1, emit=(.1, .45, 1), estr=2)
foam = b3d.mat('Foam', (.92, .95, 1), .6)
g1 = b3d.mat('Note', (.16, .46, .28), .55)
g2 = b3d.mat('NoteLight', (.5, .78, .55), .55)
g3 = b3d.mat('NoteGold', (.95, .78, .25), .4, emit=(.9, .65, .1), estr=.35)
paper = b3d.mat('Paper', (.86, .84, .76), .85)
fib = b3d.mat('Fibre', (.92, .9, .8), .7, emit=(.5, .48, .4), estr=.25)
fib2 = b3d.mat('Fibre2', (.55, .85, .6), .7, emit=(.2, .45, .25), estr=.25)
cot = b3d.mat('Cotton', (.95, .95, .93), .9, bump=.4)
stem = b3d.mat('Stem', (.2, .42, .15), .7)
husk = b3d.mat('Husk', (.28, .16, .08), .7)
pot = b3d.mat('Pot', (.5, .24, .12), .7)
gold_t = b3d.mat('GoldText', (1, .8, .2), .4, emit=(1, .72, .08), estr=2.4)
wh_t = b3d.mat('WhiteText', (1, 1, 1), .4, emit=(1, 1, 1), estr=1.6)
c_red = b3d.mat('ClothR', (.8, .15, .15), .85, bump=.5)
c_blu = b3d.mat('ClothB', (.15, .35, .8), .85, bump=.5)

def box(m, c, s, bevel=0):
    b = b3d.prim('cube', [m], size=1, location=c); b.scale = s
    if bevel:
        bv = b.modifiers.new('Bv', 'BEVEL'); bv.width = bevel; bv.segments = 4; b3d.smooth(b)
    return b

def note(name, loc, s=1.):
    """Made-up note facing -Y: 2.2 x 1 sheet, inset frame and a medallion. Not any real currency."""
    r = b3d.empty(name, loc); r.scale = (s, s, s)
    box(g1, (0, 0, 0), (2.2, .02, 1), bevel=.006).parent = r
    box(g2, (0, -.012, 0), (2.04, .006, .84)).parent = r
    box(g1, (0, -.017, 0), (1.92, .006, .72)).parent = r
    b3d.prim('cylinder', [g2], vertices=48, radius=.27, depth=.008, location=(0, -.024, 0), rotation=(math.pi / 2, 0, 0)).parent = r
    b3d.prim('cylinder', [g3], vertices=48, radius=.17, depth=.008, location=(0, -.03, 0), rotation=(math.pi / 2, 0, 0)).parent = r
    for x, z in ((-.78, .24), (.78, .24), (-.78, -.24), (.78, -.24)):
        b3d.prim('cylinder', [g2], vertices=24, radius=.09, depth=.008, location=(x, -.024, z), rotation=(math.pi / 2, 0, 0)).parent = r
    return r

def label(txt, loc, m, size=.34):
    cu = bpy.data.curves.new(txt, 'FONT'); cu.body = txt; cu.align_x = 'CENTER'; cu.size = size; cu.extrude = .015
    fp = os.path.join(os.environ.get('REEL_FONT_DIR', ''), 'Inter-Black.otf')
    if os.path.exists(fp): cu.font = bpy.data.fonts.load(fp)
    cu.materials.append(m)
    ob = b3d.link(bpy.data.objects.new(txt, cu)); ob.location = loc; ob.rotation_euler = (math.pi / 2, 0, 0)
    try: ob.visible_shadow = False
    except AttributeError: pass
    return ob

def tube(name, pts, m, r=.03, parent=None):
    cv = bpy.data.curves.new(name, 'CURVE'); cv.dimensions = '3D'; cv.bevel_depth = r; cv.bevel_resolution = 3; cv.use_fill_caps = True
    sp = cv.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts): bp.co = p; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    cv.materials.append(m); ob = b3d.link(bpy.data.objects.new(name, cv))
    if parent: ob.parent = parent
    return ob

# ---------- world ----------
box(tile, (40, 0, -.25), (140, 40, .5))
b3d.prim('plane', [wall], size=200, location=(40, 3.5, 20), rotation=(math.radians(90), 0, 0))

# ---------- A: washer ----------
H, W = 3.25, 2.7; CZ = 1.6
panel = box(white, (0, 0, H / 2), (W, .3, H))
cut = b3d.prim('cylinder', [], vertices=96, radius=.95, depth=1.2, location=(0, 0, CZ), rotation=(math.radians(90), 0, 0)); cut.hide_render = True; cut.hide_viewport = True
bl = panel.modifiers.new('Hole', 'BOOLEAN'); bl.operation = 'DIFFERENCE'; bl.object = cut
box(white, (-W / 2 + .03, .9, H / 2), (.06, 1.8, H)); box(white, (W / 2 - .03, .9, H / 2), (.06, 1.8, H)); box(white, (0, .9, H - .03), (W, 1.8, .06))
box(dark, (-.35, -.16, 2.98), (1.5, .02, .34)); box(screen, (-.55, -.175, 2.98), (.6, .012, .2))
b3d.smooth(b3d.prim('cylinder', [chrome], vertices=40, radius=.17, depth=.1, location=(.86, -.2, 2.98), rotation=(math.radians(90), 0, 0)))
b3d.smooth(b3d.prim('torus', [chrome], major_radius=1.0, minor_radius=.08, major_segments=96, minor_segments=16, location=(0, -.17, CZ), rotation=(math.radians(90), 0, 0)))
shell = b3d.lathe('Drum', [(.98, 0), (1.08, 0), (1.08, 1.5), (.98, 1.5), (.98, 0)], steps=96); shell.data.materials.append(drum_m); shell.location = (0, .1, CZ); shell.rotation_euler = (math.radians(-90), 0, 0)
b3d.prim('cylinder', [drum_m], vertices=64, radius=1.05, depth=.05, location=(0, 1.55, CZ), rotation=(math.radians(90), 0, 0))
wbox = box(water, (0, .8, CZ - .55), (2.1, 1.4, .95))
for f in range(0, e1 + 2, 3):
    wbox.rotation_euler = (0, .09 * math.sin(f * .16), 0); wbox.keyframe_insert('rotation_euler', index=1, frame=f)
r = random.Random(3)
for k in range(22):
    b3d.smooth(b3d.prim('uv_sphere', [foam], segments=12, ring_count=8, radius=r.uniform(.06, .14), location=(r.uniform(-.85, .85), r.uniform(.25, 1.3), CZ - .08 + r.uniform(-.04, .05))))
# things tumbling in the drum, in the first shot only (the last shot sees the note on the lid)
for k, (mk, rad, ph) in enumerate(((None, .55, 0), (c_red, .6, 2.2), (c_blu, .5, 4.2), (None, .35, 1.1))):
    if mk is None: o = note(f'Tumble{k}', (0, 0, 0), .46)
    else:
        o = b3d.smooth(b3d.prim('ico_sphere', [mk], subdivisions=4, radius=1)); o.scale = (.34, .28, .16)
        d = o.modifiers.new('Disp', 'DISPLACE'); tx = bpy.data.textures.new(f'TxC{k}', 'CLOUDS'); tx.noise_scale = .5; d.texture = tx; d.strength = .22
    for f in range(0, e1 + 2, 2):
        a = ph - f * .085
        o.location = (rad * math.cos(a), .55 + .25 * math.sin(a * .7 + k), CZ + rad * math.sin(a))
        o.rotation_euler = (f * .05 + k, 0, f * .1 + k * 2)
        o.keyframe_insert('location', frame=f); o.keyframe_insert('rotation_euler', frame=f)
    b3d.visible(o, [(s1, e1)])
lid_note = note('LidNote', (.1, -.02, H + .012), .62); lid_note.rotation_euler = (math.radians(90), 0, math.radians(14))
b3d.visible(lid_note, [(s5, e5)])

# ---------- B: tank, paper falls apart, note stays ----------
TW, TH, TD = 5.2, 3.4, 1.7; TZ = TH / 2 + .05
for sx in (-1, 1):
    for sy in (-1, 1): box(steel, (BX + sx * TW / 2, sy * TD / 2, TZ), (.09, .09, TH))
for sy in (-1, 1):
    for z in (.05, TH + .05): box(steel, (BX, sy * TD / 2, z), (TW, .09, .09))
for sx in (-1, 1):
    for z in (.05, TH + .05): box(steel, (BX + sx * TW / 2, 0, z), (.09, TD, .09))
box(water, (BX, 0, TZ - .15), (TW - .06, TD - .06, TH - .3))
label("QOG'OZ", (BX - 1.28, -.95, 3.72), wh_t); label('PUL', (BX + 1.28, -.95, 3.72), gold_t)
NX, NZ = 8, 6; PW, PH = 1.95, 1.3
for i in range(NX):
    for j in range(NZ):
        tl = box(paper, (0, 0, 0), (PW / NX * 1.01, .012, PH / NZ * 1.01)); rr = random.Random(i * 31 + j)
        home = (BX - 1.28 + (i - (NX - 1) / 2) * PW / NX, 0, 1.9 + (j - (NZ - 1) / 2) * PH / NZ)
        drift = (rr.uniform(-.75, .75) + (i - NX / 2) * .1, rr.uniform(-.45, .45), rr.uniform(-1.45, -.15) + (j - NZ / 2) * .1)
        spin = (rr.uniform(-2.6, 2.6), rr.uniform(-2.6, 2.6), rr.uniform(-2.6, 2.6)); start = rr.uniform(0, .3)
        for f in range(s2, e2 + 1, 4):
            t = min(1, max(0, ((f - s2) / max(1, e2 - s2) - start) / (1 - start))); t = t * t * (3 - 2 * t)
            tl.location = tuple(h + t * d for h, d in zip(home, drift)); tl.rotation_euler = tuple(t * a for a in spin)
            tl.keyframe_insert('location', frame=f); tl.keyframe_insert('rotation_euler', frame=f)
sway = note('TankNote', (BX + 1.28, 0, 1.9), .88)
for f in range(s2, e2 + 1, 6):
    sway.rotation_euler = (.05 * math.sin(f * .07), .04 * math.sin(f * .05), .1 * math.sin(f * .06)); sway.location = (BX + 1.28, 0, 1.9 + .04 * math.sin(f * .08))
    sway.keyframe_insert('rotation_euler', frame=f); sway.keyframe_insert('location', frame=f)

# ---------- C: cotton boll -> note ----------
PX, PZ = CX - 1.1, 2.5  # boll centre
box(pot, (PX, 0, .3), (.9, .9, .6), bevel=.05)
tube('Stem', [(PX, 0, .55), (PX + .05, 0, 1.3), (PX - .03, 0, 2.05)], stem, r=.05)
for a in range(5):
    t = a * 2 * math.pi / 5
    h = b3d.prim('cone', [husk], vertices=16, radius1=.2, depth=.62, location=(PX + .3 * math.cos(t), .3 * math.sin(t), PZ - .36)); h.rotation_euler = (-math.sin(t) * .95, math.cos(t) * .95, 0)
r = random.Random(11)
for k in range(6):
    t = k * 2 * math.pi / 6
    c = b3d.smooth(b3d.prim('ico_sphere', [cot], subdivisions=4, radius=.34, location=(PX + .25 * math.cos(t), .25 * math.sin(t), PZ + r.uniform(-.08, .14))))
    d = c.modifiers.new('Disp', 'DISPLACE'); tx = bpy.data.textures.new(f'TxB{k}', 'CLOUDS'); tx.noise_scale = .12; d.texture = tx; d.strength = .1
NCX = CX + 1.15; NCZ = 2.5
cnote = note('CottonNote', (NCX, 0, NCZ), .86); cnote.rotation_euler = (0, 0, math.radians(-14))
for k in range(16):
    rr = random.Random(k + 50); z0 = PZ + rr.uniform(-.2, .3); z1 = NCZ + rr.uniform(-.34, .34)
    pts = [(PX + .3, rr.uniform(-.2, .2) - .12, z0)]
    for u in (.3, .6): pts.append((PX + .3 + u * (NCX - .92 - PX - .3), rr.uniform(-.22, .1) - .1, z0 + u * (z1 - z0) + rr.uniform(-.28, .28)))
    pts.append((NCX - .92, -.05, z1))
    fb = tube(f'Spin{k}', pts, fib, r=.016)
    fb.data.bevel_factor_end = 0; fb.data.keyframe_insert('bevel_factor_end', frame=s3 + k)
    fb.data.bevel_factor_end = 1; fb.data.keyframe_insert('bevel_factor_end', frame=s3 + 36 + k)
pct = label('75% PAXTA', (NCX, -.2, NCZ + .85), gold_t, size=.36); b3d.visible(pct, [(s3 + int((e3 - s3) * .5), e3)])

# ---------- D: macro tangle, water runs through, fibres hold ----------
tangle = b3d.empty('Tangle', (DX, 0, 2.2))
for k in range(58):
    rr = random.Random(k * 7 + 1); y0 = rr.uniform(-.9, .9); z0 = rr.uniform(-1.8, 1.8); pts = []
    for i in range(7):
        pts.append((-3.2 + 6.4 * i / 6, y0 + rr.uniform(-.65, .65), z0 + rr.uniform(-.8, .8)))
    tube(f'Tn{k}', pts, fib if k % 3 else fib2, r=.042, parent=tangle)
for f in range(s4, e4 + 1, 4):
    u = (f - s4) / max(1, e4 - s4)
    tangle.scale = (1 + .03 * math.sin(u * 10), 1, 1 - .02 * math.sin(u * 10)); tangle.keyframe_insert('scale', frame=f)
for k in range(38):
    rr = random.Random(k + 300); d = b3d.smooth(b3d.prim('uv_sphere', [drop], segments=14, ring_count=8, radius=rr.uniform(.05, .1)))
    x0 = DX + rr.uniform(-2.1, 2.1); y0 = rr.uniform(-1, .9); ph = rr.random(); wob = rr.uniform(0, 6)
    for f in range(s4, e4 + 1, 2):
        u = (ph + (f - s4) / 46) % 1
        d.location = (x0 + .12 * math.sin(f * .2 + wob), y0, 4.6 - u * 4.2); d.keyframe_insert('location', frame=f)
    b3d.visible(d, [(s4, e4)])

# ---------- lights ----------
b3d.light('SUN', 'Key', (0, -20, 20), 2.1, (1, .95, .88), .05, rot=(55, 0, 18))
b3d.light('SUN', 'Fill', (0, -20, 5), .7, (.6, .72, 1), .1, rot=(80, 0, -40))
b3d.light('POINT', 'DrumGlow', (0, .4, CZ + .3), 22, (1, .95, .85), .6)
b3d.light('POINT', 'TankGlow', (BX, -.2, 3.0), 60, (.75, .9, 1), 1)

# ---------- timeline ----------
cam, tgt = b3d.camera(30)
b3d.shot(cam, tgt, s1, e1, (.9, -6.4, 2.3), (.3, -5.0, 2.0), (0, 0, 1.75), lens=30)
b3d.shot(cam, tgt, s2, e2, (BX - .5, -7.6, 2.5), (BX + .3, -6.9, 2.4), (BX, 0, 2.1), lens=30)
b3d.shot(cam, tgt, s3, e3, (CX - .1, -7.6, 2.8), (CX + .6, -7.1, 2.8), (CX + .15, 0, 2.5), (CX + .5, 0, 2.5), lens=30)
b3d.shot(cam, tgt, s4, e4, (DX - .8, -5.4, 2.4), (DX + .6, -4.2, 2.2), (DX, 0, 2.2), lens=30)
b3d.shot(cam, tgt, s5, e5, (.8, -6.6, 2.6), (1.3, -9.2, 2.9), (0, 0, 2.2), lens=30)
b3d.render(OUT, cfg.get('frames'))
