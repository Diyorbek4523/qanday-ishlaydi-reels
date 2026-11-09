"""Lift: a cutaway building (front removed) with a 4-floor shaft, a cabin, ropes and the motor room on top. A metal plate
sits on the shaft wall at every floor; the cabin carries a sensor that flashes when it passes a plate, and the floor display
counts 1 -> 2 -> 3. Shot 6 shows the motor: the sheave turns and the encoder disk on its shaft spins and blinks. 7 shots."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy
from mathutils import Matrix

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.03, .035, .08), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))
R = math.radians

wall_m = b3d.mat('Wall', (.78, .72, .62), .7, bump=.05)
slab_m = b3d.mat('Slab', (.55, .5, .46), .7, bump=.08)
shaft_m = b3d.mat('Shaft', (.32, .35, .42), .7, bump=.05)
rail_m = b3d.mat('Rail', (.6, .62, .66), .3, metal=.8)
cab_m = b3d.mat('Cabin', (.85, .55, .2), .4, metal=.3)
cab_in = b3d.mat('CabinIn', (.95, .88, .72), .5)
plate_m = b3d.mat('Plate', (.25, .55, 1), .3, metal=.4, emit=(.2, .5, 1), estr=1.0)
sens_m = b3d.mat('Sensor', (.15, .9, .3), .3, emit=(.1, 1, .25), estr=.3)
disp_m = b3d.mat('Display', (.04, .04, .05), .4)
digit_m = b3d.mat('Digit', (1, .55, .1), .4, emit=(1, .5, .05), estr=5)
label_m = b3d.mat('Label', (.95, .95, .9), .5, emit=(1, 1, .9), estr=.8)
motor_m = b3d.mat('Motor', (.2, .45, .35), .4, metal=.5)
steel = b3d.mat('Steel', (.75, .77, .8), .25, metal=.9)
rope_m = b3d.mat('Rope', (.15, .15, .15), .6, metal=.5)
enc_m = b3d.mat('Enc', (.95, .95, .95), .3, emit=(1, .9, .4), estr=1.5)

def box(m, c, s, bevel=0):
    b = b3d.prim('cube', [m], size=1, location=c); b.scale = s
    if bevel: bv = b.modifiers.new('Bv', 'BEVEL'); bv.width = bevel; bv.segments = 3
    return b
def keys(ob, attr, fv, lin=False):
    for f, v in fv: setattr(ob, attr, v); ob.keyframe_insert(attr, frame=f)
def linear(ob):
    ad = ob.animation_data
    if not ad or not ad.action: return
    try: curves = ad.action.fcurves
    except AttributeError:
        curves = [c for l in ad.action.layers for st in l.strips for cb in st.channelbags for c in cb.fcurves]
    for c in curves:
        for k in c.keyframe_points: k.interpolation = 'LINEAR'
def parent(ob, p): ob.parent = p; ob.matrix_parent_inverse = Matrix.Translation(-p.location)
def text(body, m, loc, size=.4):
    cu = bpy.data.curves.new('T' + body, 'FONT'); cu.body = body; cu.size = size; cu.extrude = .015
    cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    ob = b3d.link(bpy.data.objects.new('T' + body, cu)); cu.materials.append(m); ob.location = loc; ob.rotation_euler = (R(90), 0, 0)
    return ob

FL = [0, 2.2, 4.4, 6.6]; TOP = 8.8
# ---------- building ----------
box(slab_m, (0, 0, -.15), (12, 6, .3))
box(shaft_m, (0, .95, TOP / 2), (1.9, .1, TOP))                          # shaft back wall
sw = [box(shaft_m, (x, .3, TOP / 2), (.1, 1.4, TOP)) for x in (-1.0, 1.0)]  # shaft side walls
for z in FL[1:] + [TOP]:
    for side in (-1, 1):
        sl = box(slab_m, (side * 2.6, .2, z - .1), (3.0, 2.0, .2))
        if side == 1 and z < TOP: b3d.visible(sl, [(0, s3), (e4, N)])
box(slab_m, (0, .2, TOP - .1), (2.1, 2.0, .2))                            # machine room floor
for side in (-1, 1): box(wall_m, (side * 2.6, 1.15, TOP / 2), (3.0, .1, TOP))
for i, z in enumerate(FL):
    lb = text(str(i + 1), label_m, (-1.0, -.42, z + 1.45), .35); lb.location.x = -1.0; lb.location.y = -.42
    box(shaft_m, (-1.6, .4, z + .9), (.06, 1.0, 1.8))                     # landing door frame
for x in (-.88, .88): box(rail_m, (x, .3, TOP / 2), (.06, .12, TOP))      # guide rails
plates = []
for i, z in enumerate(FL):
    p = box(plate_m, (.83, .05, z + 1.0), (.05, .2, .32), .01); plates.append(p)

# ---------- cabin ----------
cab = b3d.empty('Cabin', (0, .3, 0))
CW, CD, CH = 1.5, 1.3, 1.9
for c, s, m in (((0, .3, .05), (CW, CD, .1), cab_m), ((0, .3, CH), (CW, CD, .1), cab_m), ((0, .3 + CD / 2, CH / 2), (CW, .06, CH), cab_in),
                ((-CW / 2, .3, CH / 2), (.06, CD, CH), cab_in), ((CW / 2, .3, CH / 2), (.06, CD, CH), cab_in)):
    parent(box(m, c, s, .01), cab)
sens = box(sens_m, (.8, .05, 1.0), (.06, .1, .1), .01); parent(sens, cab)
arm = box(rail_m, (.77, .05, 1.0), (.06, .04, .04)); parent(arm, cab)
panel = box(disp_m, (0, .3 + CD / 2 - .05, 1.62), (.5, .04, .34), .02); parent(panel, cab)
digits = []
for i in range(3):
    d = text(str(i + 1), digit_m, (0, .3 + CD / 2 - .08, 1.62), .3); parent(d, cab); digits.append(d)
lamp = b3d.light('POINT', 'CabLamp', (0, 0, 1.6), 40, (1, .9, .75), .3); parent(lamp, cab)

# ---------- motion: rest on floor 1, pass floor 2 in shot 4, stop at floor 3 at the end of shot 5 ----------
P2 = s4 + int((e4 - s4) * .7); P3 = e5 - 6; P1 = s4 + 4
def zc(f): return 0 if f <= P1 else (FL[1] * (f - P1) / (P2 - P1) if f <= P2 else FL[1] + (FL[2] - FL[1]) * min(1, (f - P2) / (P3 - P2)))
KF = [0, P1, P2, P3, P3 + 6, P3 + 10, N]
ZK = [0, 0, FL[1], FL[2] + .06, FL[2] - .02, FL[2], FL[2]]
keys(cab, 'location', [(f, (0, .3, z)) for f, z in zip(KF, ZK)]); linear(cab)
for i, d in enumerate(digits): b3d.visible(d, [((0, P2, P3)[i], (P2, P3, N)[i])])
b3d.key_input(sens_m, 'Emission Strength', [(0, .3), (P1, 6), (P1 + 8, .3), (P2 - 4, .3), (P2, 7), (P2 + 8, .3), (P3 - 4, .3), (P3, 7), (P3 + 10, .3)])
b3d.key_input(plate_m, 'Emission Strength', [(0, 1.0), (s3, 1.0), (s3 + 10, 4), (e3, 4), (e3 + 1, 1.2)])

# ---------- ropes, motor, sheave, encoder ----------
SH = (0, .3, TOP + .7); SR = .45
ropes = []
for x in (-.08, .08):
    r_ = b3d.prim('cylinder', [rope_m], vertices=8, radius=.02, depth=1, location=(x, .3 + SR - .1, 0)); ropes.append(r_)
    r_.data.transform(Matrix.Translation((0, 0, -.5)))
    top = TOP + .7
    keys(r_, 'location', [(0, (x, .3, top))])
    keys(r_, 'scale', [(f, (1, 1, top - (z + CH))) for f, z in zip(KF, ZK)]); linear(r_)
mot = box(motor_m, (1.0, .3, TOP + .55), (.9, .7, .7), .05)
sheave = b3d.prim('cylinder', [steel], vertices=48, radius=SR, depth=.25, location=SH, rotation=(R(90), 0, 0))
groove = b3d.prim('torus', [rope_m], major_radius=SR, minor_radius=.04, location=SH, rotation=(R(90), 0, 0)); groove.parent = sheave; groove.location = (0, 0, 0); groove.rotation_euler = (0, 0, 0)
for k in range(4):
    sp = box(rope_m, (0, 0, 0), (.08, SR * 1.5, .02)); sp.parent = sheave; sp.location = (0, 0, .13); sp.rotation_euler = (0, 0, R(45 * k))
enc = b3d.prim('cylinder', [disp_m], vertices=48, radius=.24, depth=.05, location=(SH[0], SH[1] - .2, SH[2]), rotation=(R(90), 0, 0))
for k in range(12):
    st = box(enc_m, (0, 0, 0), (.07, .03, .02)); st.parent = enc; a_ = 2 * math.pi * k / 12
    st.location = (.17 * math.cos(a_), .17 * math.sin(a_), .03); st.rotation_euler = (0, 0, a_)
reader = box(sens_m, (SH[0] + .3, SH[1] - .22, SH[2] + .12), (.1, .1, .14), .01)
mshaft = b3d.prim('cylinder', [steel], vertices=24, radius=.07, depth=1.0, location=(.5, .3, SH[2]), rotation=(0, R(90), 0))
for ob in (sheave, enc):
    fv = [(f, (R(90), -z / SR * 2, 0)) for f, z in zip(KF, ZK)]
    fv.insert(-1, (e6 - 1, (R(90), -ZK[-1] / SR * 2 - 3.0, 0)))
    keys(ob, 'rotation_euler', sorted(fv)); linear(ob)
# extra spin in shot 6 so the motor visibly works (fine levelling)
b3d.key_input(sens_m, 'Emission Strength', [(P3 + 11, .3), (s6, .3)] + [(s6 + 4 * k, 6 if k % 2 else .3) for k in range(1, (e6 - s6) // 4)] + [(e6, .3)])

b3d.visible(sw[1], [(0, s3), (e4, N)])   # right shaft wall removed for the plate/sensor close-ups
# ---------- lights ----------
b3d.light('AREA', 'Key', (4, -7, 8), 1400, (1, .95, .88), 8, rot=(55, 0, 30))
b3d.light('AREA', 'Fill', (-4, -6, 4), 600, (.62, .74, 1), 7, rot=(70, 0, -40))
b3d.light('POINT', 'Machine', (0, -.8, TOP + 1.6), 120, (1, .95, .85), .4)

# ---------- timeline ----------
cam, tgt = b3d.camera(30)
b3d.shot(cam, tgt, s1, e1, (1.6, -9.0, 4.8), (1.3, -8.4, 4.7), (0, .3, 4.5))
b3d.shot(cam, tgt, s2, e2, (.6, -3.2, 1.7), (.4, -2.8, 1.65), (0, .6, 1.4))
b3d.shot(cam, tgt, s3, e3, (3.0, -3.2, 3.4), (2.7, -2.8, 3.6), (.8, .1, 3.3))
b3d.shot(cam, tgt, s4, e4, (2.0, -1.5, 2.4), (2.0, -1.5, 3.6), (.82, .05, 2.0), (.82, .05, 3.2))
b3d.shot(cam, tgt, s5, e5, (1.6, -5.6, 4.0), (1.4, -5.2, 5.2), (0, .3, 3.2), (0, .3, 4.9))
b3d.shot(cam, tgt, s6, e6, (1.1, -2.7, TOP + 1.3), (.9, -2.4, TOP + 1.25), (.3, .2, TOP + .65))
b3d.shot(cam, tgt, s7, e7, (1.3, -8.4, 4.7), (1.8, -10.4, 5.0), (0, .3, 4.5))
b3d.render(OUT, cfg.get('frames'))
