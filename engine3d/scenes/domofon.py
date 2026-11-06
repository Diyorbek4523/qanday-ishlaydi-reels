"""Domofon: an entrance door held shut by an electromagnet on its header, a call panel with a round reader beside it.
A key fob (no battery) comes in; its shell goes clear to show a copper coil and a chip; at the reader the field rings
wake the chip, its number floats into the panel; the magnet glows and holds the door; the screen turns green, the
magnet goes dark and the door swings open onto a warm hallway. 7 shots."""
import math, os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.03, .04, .09), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))

# ---------- materials ----------
wall_m = b3d.mat('Wall', (.42, .36, .32), .85, bump=.12)
ground = b3d.mat('Ground', (.16, .16, .19), .9, bump=.15)
frame_m = b3d.mat('Frame', (.12, .12, .14), .4, metal=.6)
door_m = b3d.mat('Door', (.36, .17, .1), .45, metal=.35)
alu = b3d.mat('Alu', (.72, .74, .78), .3, metal=.8)
btn_m = b3d.mat('Btn', (.2, .21, .25), .4, metal=.4)
screen_m = b3d.mat('Screen', (.1, .2, .5), .3, emit=(.15, .35, 1), estr=1.5)
rdr_m = b3d.mat('Reader', (.3, .8, 1), .3, emit=(.25, .75, 1), estr=2.0)
fob_m = b3d.mat('Fob', (.12, .35, .9), .35)
fob_clear = b3d.mat('FobClear', (.3, .5, 1), .1, emit=(.1, .2, .5), estr=.3)
b3d.bsdf(fob_clear).inputs['Alpha'].default_value = .22
copper = b3d.mat('Copper', (.95, .45, .2), .25, metal=.6, emit=(1, .45, .15), estr=.6)
chip_m = b3d.mat('Chip', (.05, .05, .06), .3, emit=(1, .85, .2), estr=0)
field_m = b3d.mat('Field', (.3, .9, 1), .4, emit=(.25, .85, 1), estr=2.5)
digit_m = b3d.mat('Digits', (1, .85, .2), .3, emit=(1, .8, .15), estr=4)
mag_m = b3d.mat('Magnet', (.5, .5, .55), .35, metal=.7, emit=(1, .1, .05), estr=0)
mfield = b3d.mat('MField', (1, .2, .1), .4, emit=(1, .15, .05), estr=3)
warm = b3d.mat('Hall', (.6, .45, .3), .8)
pulse_m = b3d.mat('Pulse', (.4, 1, .5), .3, emit=(.3, 1, .4), estr=4)
for m in (fob_clear,):
    try: m.surface_render_method = 'BLENDED'
    except (AttributeError, TypeError): pass
def box(m, c, s, bevel=0):
    b = b3d.prim('cube', [m], size=1, location=c); b.scale = s
    if bevel:
        bv = b.modifiers.new('Bv', 'BEVEL'); bv.width = bevel; bv.segments = 4; b3d.smooth(b)
    return b
def curve(name, pts, m, r=.03, cyclic=False):
    cv = bpy.data.curves.new(name, 'CURVE'); cv.dimensions = '3D'; cv.bevel_depth = r; cv.bevel_resolution = 3; cv.use_fill_caps = True
    sp = cv.splines.new('POLY'); sp.points.add(len(pts) - 1); sp.use_cyclic_u = cyclic
    for bp, p in zip(sp.points, pts): bp.co = (*p, 1)
    cv.materials.append(m); return b3d.link(bpy.data.objects.new(name, cv))
def ease(u): u = min(1, max(0, u)); return u * u * (3 - 2 * u)
def lerp(a, b, u): return tuple(x + (y - x) * u for x, y in zip(a, b))
X90 = (math.radians(90), 0, 0)

T_TOUCH = s4 + int((e4 - s4) * .3)
T_CHIP = T_TOUCH + 6
T_OK = s6 + int((e6 - s6) * .15)
T_OPEN = s6 + int((e6 - s6) * .42)

# ---------- wall with a door opening (x -1.1..1.1, z 0..4.4) ----------
box(ground, (0, -5, -.25), (40, 20, .5))
box(wall_m, (-4.05, 0, 4), (5.9, .3, 8)); box(wall_m, (4.05, 0, 4), (5.9, .3, 8)); box(wall_m, (0, 0, 6.2), (2.2, .3, 3.6))
box(frame_m, (-1.13, -.05, 2.2), (.08, .42, 4.45)); box(frame_m, (1.13, -.05, 2.2), (.08, .42, 4.45)); box(frame_m, (0, -.05, 4.44), (2.34, .42, .08))
box(warm, (0, 4, -.2), (6, 8, .4)); box(warm, (0, 8, 3), (6, .2, 6)); box(warm, (-3, 4, 3), (.2, 8, 6)); box(warm, (3, 4, 3), (.2, 8, 6))
box(warm, (0, 4, 5.2), (6, 8, .2))
# ---------- door on a hinge ----------
hinge = b3d.empty('Hinge', (-1.06, 0, 0))
def child(ob, loc): ob.parent = hinge; ob.location = loc; return ob
door = child(box(door_m, (0, 0, 0), (2.08, .1, 4.32), bevel=.02), (1.05, 0, 2.17))
child(box(alu, (0, 0, 0), (.08, .14, .55), bevel=.03), (1.82, -.1, 1.9))
for z in (1.2, 3.0): child(box(door_m, (0, 0, 0), (1.6, .03, 1.2), bevel=.02), (1.05, -.06, z))
plate = child(box(alu, (0, 0, 0), (.6, .18, .07), bevel=.01), (1.91, -.2, 4.3))
child(box(alu, (0, 0, 0), (.6, .06, .2), bevel=.01), (1.91, -.09, 4.24))
for f, r in ((0, 0), (T_OPEN, 0), (T_OPEN + 32, 72), (N, 72)):
    hinge.rotation_euler = (0, 0, math.radians(r)); hinge.keyframe_insert('rotation_euler', frame=f)
# ---------- magnet on the header ----------
mag = box(mag_m, (.85, -.2, 4.42), (.72, .24, .11), bevel=.02)
b3d.key_input(mag_m, 'Emission Strength', [(0, 0.), (s5, 0.), (s5 + 8, 1.6), (T_OPEN - 1, 1.6), (T_OPEN, 0.)])
mlines = []
for k in range(5):
    x = .6 + .12 * k
    L = curve(f'ML{k}', [(x + .08 * math.cos(t), -.33, 4.36 + .05 * math.sin(t)) for t in [2 * math.pi * i / 24 for i in range(24)]], mfield, r=.012, cyclic=True)
    mlines.append(L); b3d.visible(L, [(s5 + 8, e5), (s6, T_OPEN)])
b3d.visible(b3d.arrow('HoldDown', (.85, -.45, 3.75), (.85, -.45, 4.2), mfield, r=.02), [(s5 + 14, e5)])
# ---------- call panel ----------
PX = 2.1
box(alu, (PX, -.18, 2.35), (.62, .08, 1.3), bevel=.03)
scr = box(screen_m, (PX, -.225, 2.78), (.42, .02, .24))
b3d.key_input(screen_m, 'Emission Color', [(0, (.15, .35, 1)), (T_OK - 1, (.15, .35, 1)), (T_OK, (.2, 1, .35))])
b3d.key_input(screen_m, 'Base Color', [(0, (.1, .2, .5)), (T_OK - 1, (.1, .2, .5)), (T_OK, (.1, .6, .2))])
for i in range(3):
    for j in range(3): box(btn_m, (PX - .14 + .14 * i, -.23, 2.5 - .12 * j), (.1, .03, .08), bevel=.01)
RD = (PX, -.225, 1.92)
b3d.prim('torus', [rdr_m], major_radius=.13, minor_radius=.018, major_segments=48, minor_segments=8, location=RD, rotation=X90)
b3d.prim('cylinder', [btn_m], vertices=32, radius=.12, depth=.02, location=RD, rotation=X90)
wire = curve('Wire', [(PX, -.17, 3.0), (PX, -.17, 4.62), (1.3, -.17, 4.62), (1.3, -.2, 4.5)], frame_m, r=.025)
for k in range(5):
    pl = b3d.smooth(b3d.prim('uv_sphere', [pulse_m], segments=10, ring_count=6, radius=.05))
    path = [(PX, -.25, 3.0), (PX, -.25, 4.62), (1.3, -.25, 4.62)]
    for f in range(T_OK, T_OPEN + 2, 2):
        u = ((f - T_OK) / 22 + k / 5) % 1
        p = lerp(path[0], path[1], u / .6) if u < .6 else lerp(path[1], path[2], (u - .6) / .4)
        pl.location = p; pl.keyframe_insert('location', frame=f)
    b3d.visible(pl, [(T_OK, T_OPEN)])
# field rings from the reader (shot 4)
for k in range(4):
    rg = b3d.prim('torus', [field_m], major_radius=1, minor_radius=.012, major_segments=64, minor_segments=6, location=(RD[0], RD[1] - .02, RD[2]), rotation=X90)
    for f in range(s4, e4 + 2, 2):
        u = ((f - s4) / 26 + k / 4) % 1; s_ = .15 + .55 * u
        rg.scale = (s_, s_, 1); rg.location = (RD[0], RD[1] - .02 - .35 * u, RD[2]); rg.keyframe_insert('scale', frame=f); rg.keyframe_insert('location', frame=f)
    b3d.visible(rg, [(s4, e4)])
# ---------- key fob ----------
fob = b3d.empty('Fob', (0, 0, 0))
def fchild(ob, loc): ob.parent = fob; ob.location = loc; return ob
shell = fchild(b3d.smooth(b3d.prim('uv_sphere', [fob_m], segments=32, ring_count=16, radius=1)), (0, 0, 0)); shell.scale = (.2, .06, .26)
shell2 = fchild(b3d.smooth(b3d.prim('uv_sphere', [fob_clear], segments=32, ring_count=16, radius=1)), (0, 0, 0)); shell2.scale = (.2, .06, .26)
fchild(b3d.prim('torus', [alu], major_radius=.07, minor_radius=.012, major_segments=32, minor_segments=8, rotation=X90), (0, 0, .3))
cpts = []
for i in range(5 * 40 + 1):
    t = i / 40; r = .08 + .065 * t / 5; a = 2 * math.pi * t; cpts.append((r * math.cos(a), 0, r * math.sin(a) * 1.25 - .02))
coil = curve('FobCoil', cpts, copper, r=.006); coil.parent = fob
chip = fchild(box(chip_m, (0, 0, 0), (.06, .02, .06)), (0, 0, -.02))
FOBP = (2.35, -1.5, 1.95)
TOUCH = (RD[0], RD[1] - .1, RD[2])
for f, p in ((s1, (3.6, -3.4, 1.3)), (e1 - 1, FOBP), (s4, FOBP), (T_TOUCH, TOUCH), (N, TOUCH)):
    fob.location = p; fob.keyframe_insert('location', frame=f)
for f, r in ((s1, 35), (e1 - 1, 0), (N, 0)):
    fob.rotation_euler = (0, 0, math.radians(r)); fob.keyframe_insert('rotation_euler', frame=f)
b3d.key_input(chip_m, 'Emission Strength', [(0, 0.), (T_CHIP - 1, 0.), (T_CHIP + 4, 4.), (N, 4.)])
b3d.visible(shell, [(s1, e2), (s5, N)]); b3d.visible(shell2, [(s3, e4)])
b3d.visible(coil, [(s3, e4)]); b3d.visible(chip, [(s3, e4)])
# chip number floating into the panel
bpy.ops.object.text_add(location=(0, 0, 0)); txt = bpy.context.object; txt.data.body = '7A 3F 91'; txt.data.size = .13
txt.data.align_x = 'CENTER'; txt.data.extrude = .008; txt.data.materials.append(digit_m); txt.rotation_euler = X90
for f, p in ((T_CHIP + 4, (RD[0] + .45, RD[1] - .45, RD[2] + .05)), (e4 - 4, (RD[0] + .05, RD[1] - .3, RD[2] + .5))):
    txt.location = p; txt.keyframe_insert('location', frame=f)
b3d.visible(txt, [(T_CHIP + 4, e4)])

# ---------- lights ----------
b3d.light('AREA', 'Key', (5, -8, 8), 700, (1, .95, .88), 8, rot=(45, 0, 30))
b3d.light('AREA', 'Fill', (-6, -7, 4), 280, (.62, .74, 1), 6, rot=(70, 0, -40))
b3d.light('POINT', 'Lamp', (0, -1.4, 5.0), 80, (1, .85, .6), .6)
b3d.light('POINT', 'HallLamp', (0, 3, 4.4), 260, (1, .78, .5), 1)

# ---------- timeline ----------
cam, tgt = b3d.camera(30)
b3d.shot(cam, tgt, s1, e1, (4.2, -7.4, 3.0), (3.7, -6.6, 2.8), (1.0, 0, 2.3), lens=30)
b3d.shot(cam, tgt, s2, e2, (2.75, -3.2, 2.15), (2.6, -2.8, 2.1), FOBP, lens=30)
b3d.shot(cam, tgt, s3, e3, (2.05, -2.5, 2.05), (2.2, -2.2, 2.0), FOBP, lens=30)
b3d.shot(cam, tgt, s4, e4, (3.9, -2.9, 2.5), (3.5, -2.5, 2.4), (2.05, -.4, 2.0), lens=30)
b3d.shot(cam, tgt, s5, e5, (1.9, -2.6, 3.9), (1.6, -2.2, 4.0), (.85, -.2, 4.3), lens=30)
b3d.shot(cam, tgt, s6, e6, (2.6, -5.6, 3.1), (2.3, -5.0, 3.0), (.6, 0, 2.5), lens=30)
b3d.shot(cam, tgt, s7, e7, (2.3, -5.0, 3.0), (3.6, -9.6, 4.2), (.6, 0, 2.3), lens=30)
b3d.render(OUT, cfg.get('frames'))
