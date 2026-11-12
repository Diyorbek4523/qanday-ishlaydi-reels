"""Sensorli kran: a sink with a touchless faucet. A dark window at the faucet base hides an IR LED (red) and a receiver
(green); the pulsing beam goes out, bounces back from a cup into the receiver. Cutaway under the counter: control box,
solenoid valve (plunger lifts) and water beads running up the hose; stream flows; cup leaves -> valve closes. 7 shots."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy
from mathutils import Vector

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.03, .035, .08), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))
R = math.radians

tile_m = b3d.mat('Tile', (.55, .72, .78), .5, bump=.03)
top_m = b3d.mat('Top', (.32, .3, .34), .35, bump=.02)
cab_m = b3d.mat('Cab', (.85, .62, .38), .6, bump=.03)
cer_m = b3d.mat('Ceramic', (.95, .95, .93), .15)
chrome = b3d.mat('Chrome', (.7, .74, .8), .22, metal=.55)
glass_m = b3d.mat('Window', (.02, .02, .03), .05)
led_m = b3d.mat('IR', (1, .1, .05), .3, emit=(1, .08, .03), estr=3)
rx_m = b3d.mat('Rx', (.1, .9, .3), .3, emit=(.1, 1, .3), estr=.4)
beam_m = b3d.mat('Beam', (1, .1, .05), .3, emit=(1, .1, .04), estr=3)
back_m = b3d.mat('BeamBack', (.2, 1, .35), .3, emit=(.15, 1, .3), estr=4)
cup_m = b3d.mat('Cup', (.95, .55, .2), .35)
brass = b3d.mat('Brass', (.85, .6, .25), .3, metal=.8)
coil_m = b3d.mat('Coil', (.85, .4, .15), .3, metal=.7, emit=(1, .45, .1), estr=0)
steel = b3d.mat('Steel', (.7, .72, .75), .25, metal=.9)
box_m = b3d.mat('Ctrl', (.25, .3, .38), .4)
cled_m = b3d.mat('CtrlLed', (.1, .9, .3), .3, emit=(.1, 1, .3), estr=.3)
wire_m = b3d.mat('Wire', (.9, .2, .15), .5)
hose_m = b3d.mat('Hose', (.6, .62, .66), .4, metal=.6)
water_m = b3d.mat('Water', (.25, .6, 1), .1, emit=(.2, .55, 1), estr=1.5)

def box(m, c, s, bevel=0):
    b = b3d.prim('cube', [m], size=1, location=c); b.scale = s
    if bevel: bv = b.modifiers.new('Bv', 'BEVEL'); bv.width = bevel; bv.segments = 3
    return b
def cyl(m, a, b, r, v=24):
    a, b = Vector(a), Vector(b); d = b - a
    c = b3d.prim('cylinder', [m], vertices=v, radius=r, depth=d.length, location=(a + b) / 2)
    c.rotation_mode = 'QUATERNION'; c.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized()); return b3d.smooth(c)
def keys(ob, attr, fv):
    for f, v in fv: setattr(ob, attr, v); ob.keyframe_insert(attr, frame=f)

TZ = .9
# ---------- room ----------
box(tile_m, (0, .65, 1.4), (3.4, .05, 2.0))
box(tile_m, (0, 0, -.02), (3.4, 2.4, .04))
top = box(top_m, (0, .1, TZ - .025), (2.4, 1.1, .05), .005)
hole = b3d.prim('cylinder', vertices=64, radius=.33, depth=.3, location=(0, 0, TZ))
bo = top.modifiers.new('Hole', 'BOOLEAN'); bo.object = hole; bo.operation = 'DIFFERENCE'; hole.hide_render = True; hole.hide_viewport = True
front = box(cab_m, (0, -.42, .43), (2.36, .04, .82), .01)
for x in (-1.17, 1.17): box(cab_m, (x, .1, .43), (.04, 1.0, .82))
box(cab_m, (0, .1, .03), (2.36, 1.0, .04))
basin = b3d.lathe('Basin', [(0, -.18), (.24, -.17), (.31, -.11), (.335, -.02), (.345, .004), (.37, .006)])
basin.location = (0, 0, TZ); basin.data.materials.append(cer_m)
so = basin.modifiers.new('Sol', 'SOLIDIFY'); so.thickness = .012
drain = b3d.prim('cylinder', [chrome], vertices=32, radius=.035, depth=.006, location=(0, 0, TZ - .177))

# ---------- faucet ----------
FY = .4
cyl(chrome, (0, FY, TZ), (0, FY, TZ + .3), .045, 40)
b3d.smooth(b3d.prim('uv_sphere', [chrome], radius=.045, location=(0, FY, TZ + .3)))
cyl(chrome, (0, FY, TZ + .29), (0, .2, TZ + .29), .033, 32)
b3d.smooth(b3d.prim('uv_sphere', [chrome], radius=.033, location=(0, .2, TZ + .29)))
cyl(chrome, (0, .2, TZ + .29), (0, .2, TZ + .25), .028, 32)
cyl(chrome, (0, FY, TZ), (0, FY, TZ + .012), .07, 48)
box(glass_m, (0, FY - .043, TZ + .13), (.06, .012, .042), .004)
led = b3d.smooth(b3d.prim('uv_sphere', [led_m], radius=.008, location=(-.014, FY - .05, TZ + .13)))
rx = b3d.smooth(b3d.prim('uv_sphere', [rx_m], radius=.008, location=(.014, FY - .05, TZ + .13)))
LED = Vector((-.014, FY - .055, TZ + .13)); RX = Vector((.014, FY - .055, TZ + .13))

# ---------- cup ----------
cup = b3d.lathe('Cup', [(0, 0), (.045, 0), (.05, .01), (.058, .14), (.05, .14), (.04, .012), (0, .012)])
cup.data.materials.append(cup_m)
CUP = Vector((0, .19, TZ - .17))
CA = s4 + int((e4 - s4) * .45)            # cup arrives
CL = s6 + int((e6 - s6) * .35)                               # cup starts leaving
keys(cup, 'location', [(0, (0, -.9, TZ + .12)), (s4 + 2, (0, -.9, TZ + .12)), (s4 + int((e4 - s4) * .3), (0, .02, TZ + .1)),
                       (CA, CUP), (CL, CUP), (CL + 22, (0, .02, TZ + .1)), (CL + 40, (0, -.9, TZ + .15))])

b3d.visible(cup, [(s4, CL + 40)])
# ---------- beams ----------
far = Vector((0, .08, TZ - .14)); hit = Vector((0, .19 - .05, TZ - .04))
out_free = b3d.arrow('BeamOut', LED, far, beam_m, r=.0035)
out_hit = b3d.arrow('BeamHit', LED, hit, beam_m, r=.0035)
back = b3d.arrow('BeamBack', hit + Vector((.004, 0, 0)), RX, back_m, r=.0035)
b3d.visible(out_free, [(s2, CA), (CL + 10, e7)])
b3d.visible(out_hit, [(CA, CL + 10)])
b3d.visible(back, [(CA + 3, CL + 10)])
b3d.key_input(beam_m, 'Emission Strength', [(f, 4 if (f // 5) % 2 == 0 else .4) for f in range(0, N, 5)])
b3d.key_input(led_m, 'Emission Strength', [(f, 4 if (f // 5) % 2 == 0 else .6) for f in range(0, N, 5)])
b3d.key_input(rx_m, 'Emission Strength', [(0, .4), (CA + 2, .4), (CA + 6, 5), (CL + 10, 5), (CL + 14, .4)])

# ---------- under the counter: valve, controller, hose ----------
VZ = .45; VY = .4
cyl(hose_m, (0, .63, VZ), (0, VY + .05, VZ), .016)                       # supply from the wall
box(brass, (0, VY, VZ), (.13, .1, .1), .01)                             # valve body
cyl(coil_m, (0, VY, VZ + .05), (0, VY, VZ + .14), .045, 32)             # coil
plunger = cyl(steel, (0, VY, VZ + .12), (0, VY, VZ + .18), .016)
OPEN = s5 + int((e5 - s5) * .55); CLOSE = min(CL + 45, e6 - 10)
keys(plunger, 'location', [(0, (0, VY, VZ + .15)), (OPEN - 3, (0, VY, VZ + .15)), (OPEN + 3, (0, VY, VZ + .185)),
                           (CLOSE - 3, (0, VY, VZ + .185)), (CLOSE + 3, (0, VY, VZ + .15))])
b3d.key_input(coil_m, 'Emission Strength', [(0, 0), (OPEN - 4, 0), (OPEN, 1.2), (CLOSE, 1.2), (CLOSE + 4, 0)])
P = [Vector(p) for p in ((0, .62, VZ), (0, VY, VZ), (.11, VY, VZ), (.11, VY, TZ - .06), (0, VY, TZ - .06))]
cyl(hose_m, (.065, VY, VZ), (.11, VY, VZ), .014); cyl(hose_m, (.11, VY, VZ), (.11, VY, TZ - .06), .014); cyl(hose_m, (.11, VY, TZ - .06), (0, VY, TZ - .06), .014)
cyl(hose_m, (0, VY, TZ - .06), (0, VY, TZ), .02)
ctrl = box(box_m, (-.3, .5, .55), (.18, .08, .14), .01)
cled = b3d.smooth(b3d.prim('uv_sphere', [cled_m], radius=.012, location=(-.25, .459, .58)))
b3d.key_input(cled_m, 'Emission Strength', [(0, .3), (CA + 4, .3), (CA + 8, 6), (CL + 10, 6), (CL + 14, .3)])
cyl(wire_m, (-.21, .5, .52), (-.04, VY, VZ + .1), .005, 8)
cyl(wire_m, (-.3, .5, .62), (-.3, .5, TZ - .03), .005, 8)
cyl(wire_m, (-.3, .5, TZ - .03), (-.02, VY, TZ - .03), .005, 8)
b3d.light('POINT', 'CabLamp', (.3, -.35, .5), 2.2, (1, .92, .8), .2)

# water beads along the hose while open
L = [(P[i + 1] - P[i]).length for i in range(len(P) - 1)]; T = sum(L)
def along(t):
    t = t % T
    for i, l in enumerate(L):
        if t <= l: return P[i] + (P[i + 1] - P[i]) * (t / l)
        t -= l
    return P[-1]
for k in range(12):
    bd = b3d.smooth(b3d.prim('uv_sphere', [water_m], radius=.011, location=(0, 0, 0), segments=12, ring_count=8))
    for f in range(OPEN, CLOSE + 1, 2): bd.location = along(k * T / 12 + (f - OPEN) * .025); bd.keyframe_insert('location', frame=f)
    b3d.visible(bd, [(OPEN, CLOSE)])
stream = cyl(water_m, (0, .2, TZ + .25), (0, .2, TZ - .17), .011, 16)
b3d.visible(stream, [(OPEN + 4, CLOSE)])
splash = b3d.smooth(b3d.prim('uv_sphere', [water_m], radius=.03, location=(0, .2, TZ - .04), segments=16, ring_count=8)); splash.scale = (1, 1, .25)
b3d.visible(splash, [(OPEN + 6, CL)])
b3d.visible(front, [(0, s5), (e5, N)])

# ---------- lights ----------
b3d.light('AREA', 'Key', (1.6, -2.2, 2.6), 55, (1, .95, .88), 2.5, rot=(50, 0, 35))
b3d.light('AREA', 'Fill', (-1.6, -1.8, 1.6), 25, (.62, .74, 1), 2.5, rot=(65, 0, -40))
b3d.light('POINT', 'Faucet', (.15, -.1, TZ + .35), 1.5, (1, .95, .9), .1)

# ---------- timeline ----------
cam, tgt = b3d.camera(30)
b3d.shot(cam, tgt, s1, e1, (.85, -1.6, 1.55), (.7, -1.4, 1.5), (0, .22, .95), lens=30)
b3d.shot(cam, tgt, s2, e2, (.32, -.5, 1.2), (.26, -.42, 1.17), (0, .3, 1.02), lens=30)
b3d.shot(cam, tgt, s3, e3, (.17, -.02, 1.13), (.14, .03, 1.11), (0, FY - .05, TZ + .13), lens=40)
b3d.shot(cam, tgt, s4, e4, (.62, -.45, 1.2), (.55, -.38, 1.16), (0, .22, .9), lens=30)
b3d.shot(cam, tgt, s5, e5, (.42, -.62, .56), (.34, -.52, .6), (-.05, VY, .55), (-.05, VY, .6), lens=30)
b3d.shot(cam, tgt, s6, e6, (.62, -.5, 1.22), (.55, -.42, 1.18), (0, .18, .9), lens=30)
b3d.shot(cam, tgt, s7, e7, (.7, -1.4, 1.5), (1.05, -2.1, 1.75), (0, .22, .95), lens=30)
b3d.render(OUT, cfg.get('frames'))
