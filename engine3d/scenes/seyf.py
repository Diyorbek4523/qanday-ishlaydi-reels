"""Seyf (mechanical combination lock): a steel safe with a dial. Shots 3-6 the door has a cutaway window: behind the dial
three notched wheels sit on the spindle. Shot 4 the dial turns back and forth and the wheels stop one by one; shot 5 the
last wheel lines up and the three notches glow; shot 6 the fence bar drops into the notches, the bolts pull back and the
door swings open (gold inside). 7 shots."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy
from mathutils import Matrix, Vector

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.03, .035, .07), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))
R = math.radians

steel = b3d.mat('Steel', (.18, .3, .28), .35, metal=.6)
steel_d = b3d.mat('SteelDoor', (.22, .36, .33), .3, metal=.6)
inner_m = b3d.mat('Inner', (.08, .09, .1), .8)
cut_m = b3d.mat('Cut', (.9, .45, .15), .5, metal=.2)
chrome = b3d.mat('Chrome', (.85, .87, .9), .15, metal=1.)
dial_m = b3d.mat('Dial', (.12, .12, .13), .3, metal=.5)
tick_m = b3d.mat('Tick', (.95, .95, .9), .4, emit=(1, 1, .9), estr=1.5)
brass = b3d.mat('Brass', (.8, .6, .25), .3, metal=.8)
wheel_m = b3d.mat('Wheel', (.75, .77, .8), .25, metal=.9)
glow = b3d.mat('Glow', (1, .85, .2), .3, emit=(1, .8, .1), estr=5)
red = b3d.mat('Red', (1, .2, .1), .3, emit=(1, .15, .05), estr=4)
gold = b3d.mat('Gold', (1, .75, .2), .2, metal=1., emit=(.6, .4, .05), estr=.3)
floor_m = b3d.mat('Floor', (.35, .25, .2), .7, bump=.1)
wall_m = b3d.mat('Wall', (.3, .27, .35), .7, bump=.05)

def box(m, c, s, bevel=0, extra=()):
    b = b3d.prim('cube', [m, *extra], size=1, location=c); b.scale = s
    if bevel:
        bv = b.modifiers.new('Bv', 'BEVEL'); bv.width = bevel; bv.segments = 3
    return b
def cutter(name, loc, scale, m):
    c = b3d.prim('cube', [m], size=1, location=loc); c.scale = scale; c.hide_render = True; c.hide_viewport = True; c.name = name; return c
def boolean(ob, c):
    bo = ob.modifiers.new(c.name, 'BOOLEAN'); bo.operation = 'DIFFERENCE'; bo.object = c
    try: bo.material_mode = 'TRANSFER'
    except (AttributeError, TypeError): pass
def keys(ob, attr, fv):
    for f, v in fv: setattr(ob, attr, v); ob.keyframe_insert(attr, frame=f)
def parent(ob, p):
    ob.parent = p; ob.matrix_parent_inverse = Matrix.Translation(-p.location)

# ---------- room + safe body ----------
box(floor_m, (0, 0, -.05), (10, 8, .1)); box(wall_m, (0, 2.2, 3), (10, .2, 6))
body = box(steel, (0, 0, 1.2), (2.2, 2.0, 2.4), .04, (inner_m,))
boolean(body, cutter('Hollow', (0, -.1, 1.25), (1.9, 2.0, 2.1), inner_m))
for k, (x, z) in enumerate(((-.45, .35), (0, .35), (.45, .35), (-.22, .5), (.22, .5))):
    box(gold, (x, .3, z), (.4, .7, .14), .02)
# ---------- door (pivot on the left hinge) ----------
piv = b3d.empty('Hinge', (-1.0, -1.06, 1.2))
DOOR = ((0, -1.06, 1.2), (2.0, .12, 2.2))
door_full = box(steel_d, *DOOR, .03); parent(door_full, piv)
door_cut = box(steel_d, *DOOR, .03, (cut_m,)); parent(door_cut, piv)
boolean(door_cut, cutter('Window', (.25, -1.06, 1.5), (1.3, .5, 1.3), cut_m))
handle = b3d.smooth(b3d.prim('cylinder', [chrome], vertices=24, radius=.05, depth=.5, location=(.7, -1.25, .75), rotation=(0, R(90), 0))); parent(handle, piv)
hbase = b3d.smooth(b3d.prim('cylinder', [chrome], vertices=24, radius=.09, depth=.12, location=(.7, -1.15, .75), rotation=(R(90), 0, 0))); parent(hbase, piv)
for z in (.4, 2.0):
    h = b3d.smooth(b3d.prim('cylinder', [chrome], vertices=16, radius=.06, depth=.3, location=(-1.05, -1.06, z))); parent(h, piv)
OUT_SH = [(0, s3), (s7, N)]; IN_SH = [(s3, s7)]
b3d.visible(door_full, OUT_SH); b3d.visible(door_cut, IN_SH)

# ---------- dial on the spindle ----------
DZ = 1.4
dial = (b3d.prim('cylinder', [dial_m], vertices=64, radius=.3, depth=.08, location=(0, -1.18, DZ)))
dial.rotation_euler = (R(90), 0, 0); parent(dial, piv)
for k in range(20):
    a = 2 * math.pi * k / 20; t = box(tick_m, (0, 0, 0), (.015, .02, .07 if k % 5 == 0 else .04))
    t.parent = dial; t.location = (.24 * math.sin(a), .24 * math.cos(a), .041); t.rotation_euler = (0, 0, -a)
knob = (b3d.prim('cylinder', [chrome], vertices=32, radius=.1, depth=.1, location=(0, 0, 0))); knob.parent = dial; knob.location = (0, 0, .08)
ptr = b3d.prim('cone', [red], vertices=3, radius1=.04, depth=.06, location=(0, -1.13, DZ + .36), rotation=(R(180), 0, 0)); parent(ptr, piv)
spindle = b3d.smooth(b3d.prim('cylinder', [chrome], vertices=24, radius=.035, depth=.6, location=(0, -.85, DZ), rotation=(R(90), 0, 0))); parent(spindle, piv)

# ---------- wheel pack ----------
WY = [-.92, -.78, -.64]; WR = .32
hubs = []
for k, y in enumerate(WY):
    hub = b3d.empty(f'Hub{k}', (0, y, DZ)); parent(hub, piv); hubs.append(hub)
    w = (b3d.prim('cylinder', [wheel_m, cut_m], vertices=64, radius=WR, depth=.06, location=(0, y, DZ), rotation=(R(90), 0, 0)))
    parent(w, hub)
    c = cutter(f'Notch{k}', (0, y, DZ + WR), (.1, .2, .24), cut_m); parent(c, hub); boolean(w, c)
    mk = box(glow, (0, y, DZ + WR - .11), (.09, .075, .02)); parent(mk, hub); b3d.visible(mk, [(s5, s7)])
    pin = box(brass, (.1, y - .045, DZ - .12), (.05, .03, .05)); parent(pin, hub)
# dial turns: right, left, right (codes like 30-10-25); wheels stop one by one
T = [s4, s4 + int((e4 - s4) * .4), e4 - 2, s5 + int((e5 - s5) * .5)]
keys(dial, 'rotation_euler', [(0, (R(90), 0, 0)), (T[0], (R(90), 0, 0)), (T[1], (R(90), R(560), 0)), (T[2], (R(90), R(250), 0)), (T[3], (R(90), R(400), 0))])
STARTS = [R(150), R(-120), R(70)]   # notch angle of each wheel before dialing
keys(hubs[2], 'rotation_euler', [(0, (0, STARTS[2], 0)), (T[0], (0, STARTS[2], 0)), (T[1], (0, 0, 0))])                         # back wheel
keys(hubs[1], 'rotation_euler', [(0, (0, STARTS[1], 0)), (T[1], (0, STARTS[1], 0)), (T[2], (0, 0, 0))])
keys(hubs[0], 'rotation_euler', [(0, (0, STARTS[0], 0)), (T[2], (0, STARTS[0], 0)), (T[3], (0, 0, 0))])                         # front wheel last
line = box(red, (0, -.78, DZ + WR + .005), (.012, .44, .012)); parent(line, piv); b3d.visible(line, [(T[3] + 3, e5)])

# ---------- fence + bolt assembly ----------
bolt = b3d.empty('BoltRig', (0, 0, 0)); parent(bolt, piv)
FZ = DZ + WR + .045
parts = [box(brass, (0, -.78, FZ), (.08, .4, .08), .01), box(brass, (.45, -.8, FZ + .04), (.9, .06, .06)),
         box(brass, (.9, -.92, 1.2), (.1, .1, 1.7), .01)]
for z in (.55, 1.2, 1.85):
    parts.append(b3d.smooth(b3d.prim('cylinder', [chrome], vertices=24, radius=.07, depth=.42, location=(1.1, -.92, z), rotation=(0, R(90), 0))))
for p in parts: parent(p, bolt)
D0 = s6 + int((e6 - s6) * .12); D1 = s6 + int((e6 - s6) * .25); B1 = s6 + int((e6 - s6) * .5); O1 = e6 - 2
keys(bolt, 'location', [(0, (0, 0, 0)), (D0, (0, 0, 0)), (D1, (0, 0, -.1)), (B1, (-.4, 0, -.1)), (s7 - 1, (-.4, 0, -.1)), (s7, (-.4, 0, -.1))])
keys(piv, 'rotation_euler', [(0, (0, 0, 0)), (B1 + 2, (0, 0, 0)), (O1, (0, 0, R(-95))), (N, (0, 0, R(-100)))])

# ---------- lights ----------
b3d.light('AREA', 'Key', (3, -4.5, 4), 450, (1, .95, .88), 5, rot=(50, 0, 35))
b3d.light('AREA', 'Fill', (-3, -4, 2), 200, (.62, .74, 1), 4, rot=(70, 0, -40))
b3d.light('POINT', 'Inside', (.3, -.4, 1.7), 60, (1, .9, .75), .3)

# ---------- timeline ----------
cam, tgt = b3d.camera(30)
b3d.shot(cam, tgt, s1, e1, (2.2, -5.4, 2.3), (1.8, -4.9, 2.2), (0, -.5, 1.2))
b3d.shot(cam, tgt, s2, e2, (.5, -2.4, 1.7), (.35, -2.1, 1.6), (0, -1.1, 1.4))
b3d.shot(cam, tgt, s3, e3, (1.9, -3.1, 2.0), (1.7, -2.8, 1.95), (.1, -.85, 1.4))
b3d.shot(cam, tgt, s4, e4, (1.55, -1.8, 1.95), (1.45, -1.7, 1.9), (0, -.78, 1.45))
b3d.shot(cam, tgt, s5, e5, (1.3, -1.55, 2.3), (1.2, -1.45, 2.25), (0, -.78, 1.62))
b3d.shot(cam, tgt, s6, e6, (2.0, -3.6, 2.2), (2.2, -4.2, 2.3), (.3, -.8, 1.3))
b3d.shot(cam, tgt, s7, e7, (1.8, -4.4, 2.2), (2.4, -6.2, 2.8), (0, -.3, 1.2))
b3d.render(OUT, cfg.get('frames'))
