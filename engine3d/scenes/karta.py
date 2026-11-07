"""Karta to'lovi: a payment terminal on a shop counter; a bank card comes in, its shell goes clear to show the antenna
coil and the chip (no battery). At the terminal the field rings power the chip and a one-time code appears. The code
flies as a glowing packet along an arc to the processing centre, then on to the bank; the bank checks (coins glow),
a green tick appears, a green packet races back and the terminal screen turns green. 7 shots."""
import math, os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy
from mathutils import Vector, Euler

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.03, .04, .09), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))

# ---------- materials ----------
counter_m = b3d.mat('Counter', (.32, .18, .1), .55, bump=.05)
ground = b3d.mat('Ground', (.05, .06, .1), .9, bump=.15)
term_m = b3d.mat('Term', (.1, .1, .12), .35, metal=.3)
key_m = b3d.mat('Key', (.6, .62, .66), .4, metal=.3)
keyg = b3d.mat('KeyG', (.2, .7, .3), .4)
keyr = b3d.mat('KeyR', (.8, .2, .15), .4)
screen_m = b3d.mat('Screen', (.1, .2, .5), .3, emit=(.15, .35, 1), estr=1.6)
card_m = b3d.mat('Card', (.08, .3, .85), .3, metal=.2)
card_clear = b3d.mat('CardClear', (.3, .5, 1), .1, emit=(.1, .2, .5), estr=.3)
b3d.bsdf(card_clear).inputs['Alpha'].default_value = .2
stripe_m = b3d.mat('Stripe', (.95, .75, .25), .3, metal=.8)
gold = b3d.mat('Gold', (1, .78, .3), .25, metal=1.0)
copper = b3d.mat('Copper', (.95, .45, .2), .25, metal=.6, emit=(1, .45, .15), estr=0)
chip_m = b3d.mat('Chip', (.9, .7, .25), .25, metal=.9, emit=(1, .85, .2), estr=0)
field_m = b3d.mat('Field', (.3, .9, 1), .4, emit=(.25, .85, 1), estr=2.5)
code_m = b3d.mat('Code', (1, .85, .2), .3, emit=(1, .8, .15), estr=4)
packet_m = b3d.mat('Packet', (1, .85, .2), .3, emit=(1, .8, .15), estr=6)
greenp = b3d.mat('PacketG', (.3, 1, .4), .3, emit=(.3, 1, .4), estr=6)
arc_m = b3d.mat('Arc', (.2, .5, 1), .4, emit=(.2, .5, 1), estr=1.2)
proc_m = b3d.mat('Proc', (.12, .16, .3), .5, metal=.3)
win_m = b3d.mat('Win', (.2, .8, 1), .3, emit=(.2, .8, 1), estr=2.2)
bank_m = b3d.mat('Bank', (.85, .8, .7), .6)
bankwin = b3d.mat('BankWin', (1, .75, .3), .4, emit=(1, .7, .25), estr=0)
coin_m = b3d.mat('Coin', (1, .78, .3), .25, metal=1.0, emit=(1, .7, .2), estr=0)
tick_m = b3d.mat('Tick', (.3, 1, .4), .3, emit=(.3, 1, .4), estr=5)
city_m = b3d.mat('City', (.08, .09, .16), .7)
cwin = b3d.mat('CityWin', (1, .8, .45), .4, emit=(1, .75, .4), estr=1.5)
try: card_clear.surface_render_method = 'BLENDED'
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
def tick(name, loc, sz, m, rot=(90, 0, 0)):
    root = b3d.empty(name, loc); root.rotation_euler = [math.radians(r) for r in rot]
    a = box(m, (0, 0, 0), (.14 * sz, .35 * sz, .1 * sz)); a.parent = root; a.location = (-.13 * sz, -.06 * sz, 0); a.rotation_euler = (0, 0, math.radians(40))
    b = box(m, (0, 0, 0), (.14 * sz, .75 * sz, .1 * sz)); b.parent = root; b.location = (.14 * sz, .1 * sz, 0); b.rotation_euler = (0, 0, math.radians(-35))
    return root
X90 = (math.radians(90), 0, 0)
TILT = -15

# ---------- counter + ground + city ----------
box(counter_m, (0, .3, -.5), (4.2, 3.2, 1.0), bevel=.04)
box(ground, (0, 10, -1.05), (60, 40, .1))
rnd = random.Random(7)
for i in range(16):
    x = -16 + i * 2.2 + rnd.uniform(-.4, .4); y = 24 + rnd.uniform(0, 6); h = rnd.uniform(3, 9)
    if abs(x) < 7 and y < 26: continue
    box(city_m, (x, y, -1 + h / 2), (1.6, 1.6, h))
    for k in range(int(h // 1.2)):
        if rnd.random() < .6: box(cwin, (x + rnd.uniform(-.4, .4), y - .82, -.4 + k * 1.2), (.3, .02, .35))

# ---------- terminal ----------
T = b3d.empty('Terminal', (0, 0, 0)); T.rotation_euler = (math.radians(TILT), 0, 0)
def tch(ob, loc): ob.parent = T; ob.location = loc; return ob
tch(box(term_m, (0, 0, 0), (1.0, .42, 2.0), bevel=.08), (0, 0, 1.0))
scr = tch(box(screen_m, (0, 0, 0), (.78, .02, .56), bevel=.01), (0, -.215, 1.45))
for i in range(3):
    for j in range(4): tch(box(key_m, (0, 0, 0), (.2, .04, .12), bevel=.02), (-.26 + .26 * i, -.22, .95 - .17 * j))
tch(box(keyr, (0, 0, 0), (.2, .04, .12), bevel=.02), (-.26, -.22, .27)); tch(box(keyg, (0, 0, 0), (.2, .04, .12), bevel=.02), (.26, -.22, .27))
for k in range(3):  # contactless sign above the screen
    a = tch(b3d.prim('torus', [field_m], major_radius=.06 + .05 * k, minor_radius=.008, major_segments=32, minor_segments=6, rotation=X90), (.0, -.215, 1.84))
screen_tick = tick('ScreenTick', (0, 0, 0), .55, tick_m); screen_tick.parent = T; screen_tick.location = (0, -.24, 1.45); screen_tick.rotation_euler = X90

R = Euler((math.radians(TILT), 0, 0))
def tw(p): v = Vector(p); v.rotate(R); return tuple(v)
SCR = tw((0, -.215, 1.45)); NRM = Vector((0, -1, 0)); NRM.rotate(R)
TAP = tuple(Vector(SCR) + NRM * .32)

# ---------- card ----------
card = b3d.empty('Card', (0, 0, 0)); card.rotation_mode = 'XYZ'
def cch(ob, loc): ob.parent = card; ob.location = loc; return ob
body = cch(box(card_m, (0, 0, 0), (.86, .02, .54), bevel=.04), (0, 0, 0))
cch(box(stripe_m, (0, 0, 0), (.3, .005, .05)), (.2, -.012, -.17))
cch(box(stripe_m, (0, 0, 0), (.5, .005, .04)), (-.1, -.012, -.08))
chip_out = cch(box(gold, (0, 0, 0), (.13, .006, .1), bevel=.01), (-.24, -.012, .06))
shell = cch(box(card_clear, (0, 0, 0), (.86, .02, .54), bevel=.04), (0, 0, 0))
loops = []
for k in range(4):
    w, h = .37 - .025 * k, .22 - .025 * k
    pts = [(-w, 0, -h), (w, 0, -h), (w, 0, h), (-w, 0, h)]
    loops.append(cch(curve(f'Ant{k}', pts, copper, r=.006, cyclic=True), (0, 0, 0)))
chip_in = cch(box(chip_m, (0, 0, 0), (.13, .02, .1), bevel=.01), (-.24, 0, .06))
HOLD = (1.1, -1.7, 1.55)
for f, p, r in ((s1, (1.7, -2.6, 1.0), (0, 0, 40)), (e1 - 1, (1.2, -1.2, 1.55), (TILT, 0, 10)), (s2, HOLD, (0, 0, 0)), (e2 - 1, HOLD, (0, 0, 0)),
                (s3, HOLD, (0, 0, 0)), (s3 + int((e3 - s3) * .35), TAP, (TILT, 0, 0)), (N, TAP, (TILT, 0, 0))):
    card.location = p; card.keyframe_insert('location', frame=f)
    card.rotation_euler = [math.radians(x) for x in r]; card.keyframe_insert('rotation_euler', frame=f)
T_TAP = s3 + int((e3 - s3) * .35)
b3d.visible(body, [(s1, s2 + 10), (s4, N)]); b3d.visible(shell, [(s2 + 10, s4)])
for L in loops: b3d.visible(L, [(s2 + 10, s4)])
b3d.visible(chip_in, [(s2 + 10, s4)]); b3d.visible(chip_out, [(s1, s2 + 10), (s4, N)])
b3d.key_input(copper, 'Emission Strength', [(0, 0.), (T_TAP, 0.), (T_TAP + 6, 2.5), (N, 2.5)])
b3d.key_input(chip_m, 'Emission Strength', [(0, 0.), (T_TAP + 4, 0.), (T_TAP + 10, 4.), (N, 4.)])
# field rings from the screen
for k in range(4):
    rg = b3d.prim('torus', [field_m], major_radius=1, minor_radius=.01, major_segments=64, minor_segments=6)
    rg.rotation_euler = (math.radians(90 + TILT), 0, 0)
    for f in range(T_TAP - 10, e3 + 2, 2):
        u = ((f - T_TAP) / 24 + k / 4) % 1; s_ = .15 + .5 * u
        rg.scale = (s_, s_, 1); rg.location = tuple(Vector(SCR) + NRM * (.05 + .3 * u)); rg.keyframe_insert('scale', frame=f); rg.keyframe_insert('location', frame=f)
    b3d.visible(rg, [(T_TAP - 10, e3)])
# one-time code
bpy.ops.object.text_add(location=(0, 0, 0)); code = bpy.context.object; code.data.body = '8F 2C 7A 91'; code.data.size = .14
code.data.align_x = 'CENTER'; code.data.extrude = .008; code.data.materials.append(code_m); code.rotation_euler = X90
for f, p in ((T_TAP + 10, (TAP[0] + .2, TAP[1] - .2, TAP[2] + .55)), (e3 - 1, (TAP[0] + .3, TAP[1] - .3, TAP[2] + .85))):
    code.location = p; code.keyframe_insert('location', frame=f)
b3d.visible(code, [(T_TAP + 10, e3)])

# ---------- processing centre and bank ----------
PROC = (-5, 12, -1)
box(proc_m, (PROC[0], PROC[1], PROC[2] + 3), (3, 3, 6), bevel=.05)
for k in range(5):
    for j in range(3): box(win_m, (PROC[0] - .9 + .9 * j, PROC[1] - 1.52, PROC[2] + .9 + 1.0 * k), (.55, .02, .14))
for k in range(3):  # antenna dish on the roof
    pass
b3d.prim('cylinder', [key_m], vertices=16, radius=.06, depth=1.6, location=(PROC[0] + .8, PROC[1], PROC[2] + 6.8))
b3d.smooth(b3d.prim('uv_sphere', [packet_m], segments=16, ring_count=8, radius=.14, location=(PROC[0] + .8, PROC[1], PROC[2] + 7.65)))
BANK = (5, 18, -1)
box(bank_m, (BANK[0], BANK[1], BANK[2] + .3), (5.2, 3.6, .6))
box(bank_m, (BANK[0], BANK[1], BANK[2] + 2.7), (4.4, 2.8, 4.2))
for i in range(6): b3d.smooth(b3d.prim('cylinder', [bank_m], vertices=24, radius=.22, depth=3.6, location=(BANK[0] - 1.9 + .76 * i, BANK[1] - 1.6, BANK[2] + 2.4)))
box(bank_m, (BANK[0], BANK[1] - .1, BANK[2] + 4.4), (5.0, 3.6, .5))
ped = b3d.prim('cone', [bank_m], vertices=4, radius1=3.6, depth=1.6, location=(BANK[0], BANK[1] - .1, BANK[2] + 5.45)); ped.scale = (1, .55, 1); ped.rotation_euler = (0, 0, math.radians(45))
for i in range(5): box(bankwin, (BANK[0] - 1.52 + .76 * i, BANK[1] - 1.42, BANK[2] + 2.4), (.4, .02, 2.2))
b3d.key_input(bankwin, 'Emission Strength', [(0, 0.), (s5 + 10, 0.), (s5 + 20, 2.5), (N, 2.5)])
coins = []
for c in range(3):
    for k in range(4 + c * 2):
        coins.append(b3d.prim('cylinder', [coin_m], vertices=32, radius=.32, depth=.09, location=(BANK[0] - 3.4 + c * .75, BANK[1] - 2.6, BANK[2] + .05 + .1 * k)))
b3d.key_input(coin_m, 'Emission Strength', [(0, 0.), (s5 + 22, 0.), (s5 + 32, 1.5), (N, 1.5)])
bank_tick = tick('BankTick', (BANK[0], BANK[1] - 2.2, BANK[2] + 7.6), 2.4, tick_m)
for f, s_ in ((s6, .01), (s6 + 8, 1.15), (s6 + 12, 1.0)):
    bank_tick.scale = (s_, s_, s_); bank_tick.keyframe_insert('scale', frame=f)
b3d.visible(bank_tick, [(s6, N)])

# ---------- arcs and packets ----------
def arc_pts(a, b, h, n=40):
    a, b = Vector(a), Vector(b)
    return [tuple(a + (b - a) * (i / n) + Vector((0, 0, h * 4 * (i / n) * (1 - i / n)))) for i in range(n + 1)]
A0 = tw((0, 0, 2.05)); A1 = (PROC[0], PROC[1], PROC[2] + 6.1); A2 = (BANK[0], BANK[1], BANK[2] + 6.4)
arcA = arc_pts(A0, A1, 3.0); arcB = arc_pts(A1, A2, 2.5)
ca = curve('ArcA', arcA, arc_m, r=.025); cb = curve('ArcB', arcB, arc_m, r=.025)
b3d.visible(ca, [(s4, N)]); b3d.visible(cb, [(s4, N)])
def along(pts, u):
    u = min(1, max(0, u)) * (len(pts) - 1); i = min(int(u), len(pts) - 2); return lerp(pts[i], pts[i + 1], u - i)
def packet(m, path, f0, f1, name):
    p = b3d.smooth(b3d.prim('uv_sphere', [m], segments=16, ring_count=8, radius=.28)); p.name = name
    tr = []
    for f in range(f0, f1 + 1):
        p.location = along(path, ease((f - f0) / max(1, f1 - f0))); p.keyframe_insert('location', frame=f)
    b3d.visible(p, [(f0, f1 + 1)])
    for k in range(5):  # trail
        t = b3d.smooth(b3d.prim('uv_sphere', [m], segments=10, ring_count=6, radius=.2 - .03 * k))
        for f in range(f0, f1 + 1):
            t.location = along(path, ease((f - f0 - 2 * (k + 1)) / max(1, f1 - f0))); t.keyframe_insert('location', frame=f)
        b3d.visible(t, [(f0 + 2 * (k + 1), f1 + 1)])
    return p
packet(packet_m, arcA, s4 + 6, e4 - 6, 'P1')
packet(packet_m, arcB, s5 - 2, s5 + 14, 'P2')
back = list(reversed(arcB)) + list(reversed(arcA))[1:]
T_OK = s6 + int((e6 - s6) * .72)
packet(greenp, back, s6 + 10, T_OK, 'P3')
b3d.key_input(screen_m, 'Emission Color', [(0, (.15, .35, 1)), (T_OK - 1, (.15, .35, 1)), (T_OK, (.2, 1, .35))])
b3d.key_input(screen_m, 'Base Color', [(0, (.1, .2, .5)), (T_OK - 1, (.1, .2, .5)), (T_OK, (.1, .6, .2))])
b3d.visible(screen_tick, [(T_OK, N)])

# ---------- lights ----------
b3d.light('AREA', 'Key', (4, -6, 6), 500, (1, .95, .88), 6, rot=(50, 0, 35))
b3d.light('AREA', 'Fill', (-5, -5, 3), 200, (.62, .74, 1), 5, rot=(70, 0, -40))
b3d.light('SUN', 'Moon', (0, 0, 20), 1.2, (.6, .7, 1), .2, rot=(40, 0, 20))
b3d.light('POINT', 'BankL', (BANK[0], BANK[1] - 5, BANK[2] + 3), 300, (1, .85, .6), 1)
b3d.light('POINT', 'ProcL', (PROC[0] + 1, PROC[1] - 4, PROC[2] + 3), 250, (.5, .8, 1), 1)

# ---------- timeline ----------
cam, tgt = b3d.camera(30)
b3d.shot(cam, tgt, s1, e1, (2.6, -4.6, 2.4), (2.0, -4.0, 2.2), (.4, -.2, 1.3), lens=30)
b3d.shot(cam, tgt, s2, e2, (1.3, -3.45, 1.8), (1.25, -3.15, 1.75), HOLD, lens=30)
b3d.shot(cam, tgt, s3, e3, (1.9, -2.6, 2.1), (1.6, -2.3, 2.0), (.2, -.3, 1.5), lens=30)
b3d.shot(cam, tgt, s4, e4, (9.5, -1.0, 5.0), (9.0, .5, 6.0), (-2.5, 6, 3.2), lens=30)
b3d.shot(cam, tgt, s5, e5, (-1, 6, 4.5), (0, 7, 4.8), (BANK[0], BANK[1], BANK[2] + 3.2), lens=30)
b3d.shot(cam, tgt, s6, e6, (2, -6.5, 5.0), (1.5, -3.9, 2.5), (3, 12, 4.5), (0, 0, 1.4), lens=30)
b3d.shot(cam, tgt, s7, e7, (1.5, -3.4, 2.3), (3.0, -8.5, 4.2), (0, .5, 1.3), (0, 4, 2.0), lens=30)
b3d.render(OUT, cfg.get('frames'))
