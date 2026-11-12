"""Muzlatkich eshigi: a fridge whose door snaps shut by itself; close-up of the rubber gasket; a big top-down slice
(door + gasket with a glowing magnetic strip + steel cabinet wall) closing with pull arrows; warm air balls bounce off
the seal while cold ones stay inside; the door resists re-opening (air pushes it in). 7 shots."""
import math, os, sys, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy
from mathutils import Vector

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.03, .035, .08), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))
R = math.radians

wall_m = b3d.mat('Wall', (.33, .42, .48), .7, bump=.03)
floor_m = b3d.mat('Floor', (.6, .42, .28), .6, bump=.05)
wood = b3d.mat('Wood', (.62, .42, .26), .5, bump=.04)
body_m = b3d.mat('Body', (.68, .71, .76), .3, metal=.3)
in_m = b3d.mat('Inner', (.8, .9, 1), .5, emit=(.6, .8, 1), estr=.12)
shelf_m = b3d.mat('Shelf', (.7, .85, .95), .2)
gask_m = b3d.mat('Gasket', (.2, .21, .24), .8, emit=(1, .9, .6), estr=0)
hand_m = b3d.mat('Handle', (.6, .62, .66), .25, metal=.8)
mag_m = b3d.mat('Magnet', (.9, .15, .25), .4, emit=(1, .12, .25), estr=2)
steel_m = b3d.mat('Steel', (.55, .6, .68), .3, metal=.7)
door_m = b3d.mat('DoorCut', (.68, .71, .76), .5)
foam_m = b3d.mat('Foam', (.95, .82, .45), .9)
warm_m = b3d.mat('Warm', (1, .5, .15), .4, emit=(1, .4, .08), estr=3)
cold_m = b3d.mat('Cold', (.3, .7, 1), .4, emit=(.2, .6, 1), estr=3)
pull_m = b3d.mat('Pull', (1, .85, .2), .4, emit=(1, .8, .15), estr=2.2)
push_m = b3d.mat('Push', (.3, .7, 1), .4, emit=(.25, .65, 1), estr=2.2)
bg_m = b3d.mat('Bg', (.07, .09, .16), .8)
cin_m = b3d.mat('ColdFloor', (.12, .25, .45), .7)
wout_m = b3d.mat('WarmFloor', (.35, .16, .1), .7)
c1 = b3d.mat('It1', (.9, .3, .2), .5); c2 = b3d.mat('It2', (.95, .8, .2), .5); c3 = b3d.mat('It3', (.3, .7, .35), .5)

def box(m, c, s, bevel=0, parent=None):
    b = b3d.prim('cube', [m], size=1, location=c); b.scale = s
    if bevel: bv = b.modifiers.new('Bv', 'BEVEL'); bv.width = bevel; bv.segments = 3
    if parent: b.parent = parent
    return b
def keys(ob, attr, fv):
    for f, v in fv: setattr(ob, attr, v); ob.keyframe_insert(attr, frame=f)

# ---------- kitchen + fridge (front at y=0, facing -Y) ----------
box(floor_m, (0, 0, -.02), (8, 8, .04))
box(wall_m, (0, .78, 1.5), (8, .06, 3))
box(wood, (-1.05, .38, .45), (1.2, .65, .9), .01)
box(body_m, (-1.05, .38, .92), (1.26, .7, .04), .01)
box(body_m, (0, .64, .9), (.7, .02, 1.8)); box(body_m, (-.34, .325, .9), (.02, .65, 1.8)); box(body_m, (.34, .325, .9), (.02, .65, 1.8))
box(body_m, (0, .325, 1.79), (.7, .65, .02)); box(body_m, (0, .325, .01), (.7, .65, .02))
box(in_m, (0, .625, .9), (.66, .01, 1.76)); box(in_m, (-.327, .325, .9), (.006, .62, 1.76)); box(in_m, (.327, .325, .9), (.006, .62, 1.76))
for z in (.5, .95, 1.4): box(shelf_m, (0, .33, z), (.65, .58, .015))
for (x, z, m, k) in ((-.18, .5, c1, 0), (.1, .5, c2, 1), (-.05, .95, c3, 1), (.2, .95, c1, 0), (-.2, 1.4, c2, 1), (.12, 1.4, c3, 0)):
    if k: b3d.smooth(b3d.prim('cylinder', [m], vertices=24, radius=.055, depth=.2, location=(x, .3, z + .108)))
    else: box(m, (x, .3, z + .078), (.16, .12, .14), .01)
hinge = b3d.empty('Hinge', (.35, 0, 0))
box(body_m, (-.35, -.045, .9), (.7, .05, 1.8), .008, hinge)
box(hand_m, (-.63, -.09, 1.0), (.03, .04, .45), .008, hinge)
box(in_m, (-.35, -.018, .9), (.6, .006, 1.66), 0, hinge)
for z in (.45, .9, 1.35): box(shelf_m, (-.35, .004, z), (.56, .05, .07), .005, hinge)
for c, s in (((-.665, -.008, .9), (.05, .026, 1.74)), ((-.035, -.008, .9), (.05, .026, 1.74)), ((-.35, -.01, 1.77), (.68, .02, .035)), ((-.35, -.01, .03), (.68, .02, .035))):
    box(gask_m, c, s, .006, hinge)
d6 = e6 - s6
ang = [(0, 40), (s1 + int((e1 - s1) * .45), 40), (s1 + int((e1 - s1) * .62), 0), (e1 - 1, 0), (s2, 75), (e2 - 1, 75), (s3, 0),
       (s6 + int(d6 * .2), 0), (s6 + int(d6 * .3), 5), (s6 + int(d6 * .42), 0), (s6 + int(d6 * .6), 0), (s6 + int(d6 * .7), 4), (s6 + int(d6 * .82), 0)]
for f, a in ang: hinge.rotation_euler = (0, 0, R(a)); hinge.keyframe_insert('rotation_euler', frame=f)
for i, z in enumerate((.6, 1.0, 1.4)):
    a = b3d.arrow('Push%d' % i, (-.15, -.6, z), (-.15, -.11, z), push_m, r=.03); b3d.visible(a, [(s6, e6)])

# ---------- big top-down slice (shots 3-5), at X0 ----------
X0 = 6.0
box(bg_m, (X0 + .2, 0, -.14), (4, 4, .04))
box(cin_m, (X0 + .47, .2, -.11), (.82, .52, .02)); box(wout_m, (X0 - .55, -.1, -.11), (1.0, 1.1, .02))
box(steel_m, (X0, .25, 0), (.12, .5, .2), .005)                       # cabinet wall, front face at y=0
box(steel_m, (X0 + .47, .47, 0), (.82, .06, .2), .005)                # back wall
dg = b3d.empty('DoorCut', (X0, 0, 0))
box(door_m, (.35, -.11, 0), (1.0, .1, .2), .008, dg)
box(foam_m, (.35, -.11, .003), (.94, .06, .2), 0, dg)
box(gask_m, (0, -.03, 0), (.1, .06, .2), .012, dg)
box(mag_m, (0, -.018, .004), (.07, .022, .2), 0, dg)
def label(body, loc, size=.07, parent=None):
    cu = bpy.data.curves.new('L' + body, 'FONT'); cu.body = body; cu.size = size; cu.extrude = .002; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    ob = b3d.link(bpy.data.objects.new('L' + body, cu)); cu.materials.append(lab_m); ob.location = loc; ob.parent = parent
    return ob
lab_m = b3d.mat('Label', (1, 1, 1), .5, emit=(1, 1, 1), estr=1.2)
label('MAGNIT', (.0, -.235, -.09), .075, dg); pl = label("PO'LAT", (X0, .27, .102), .06); pl.rotation_euler = (0, 0, R(90))
b3d.key_input(gask_m, 'Emission Strength', [(0, 0), (s2, 0)] + [(s2 + 12 * k, .9 if k % 2 else .1) for k in range(1, max(2, (e2 - s2) // 12))] + [(e2, 0)]); label('SOVUQ', (X0 + .36, .22, -.09), .075)
GAP = .28; CL = s4 + int((e4 - s4) * .45)
keys(dg, 'location', [(0, (X0, -GAP, 0)), (CL - 8, (X0, -GAP, 0)), (CL, (X0, 0, 0)), (N, (X0, 0, 0))])
b3d.key_input(mag_m, 'Emission Strength', [(s3, 1)] + [(s3 + 10 * k, 5 if k % 2 else 1.5) for k in range(1, max(2, (e3 - s3) // 10))] + [(e3, 2), (CL, 5), (CL + 12, 2)])
for i, x in enumerate((-.03, .03)):
    a = b3d.arrow('Pull%d' % i, (X0 + x, -.2, .13), (X0 + x, -.02, .13), pull_m, r=.012); b3d.visible(a, [(s4, CL - 2)])
rnd = random.Random(4)
for i in range(6):                                                     # warm air: runs at the seam, bounces off the gasket
    y = -.03 + rnd.uniform(-.012, .012); ph = i * 9
    p = b3d.smooth(b3d.prim('uv_sphere', [warm_m], radius=.02, segments=16, ring_count=8, location=(X0 - .7, y, .13)))
    fv = []; f = s5 - 20 + ph
    while f < e5 + 30:
        fv += [(f, (X0 - .75, y - .12, .02)), (f + 22, (X0 - .085, y, .13)), (f + 40, (X0 - .6, y - .3 + rnd.uniform(-.1, .1), .13))]; f += 54
    keys(p, 'location', fv); b3d.visible(p, [(s5, e5)])
for i in range(8):                                                     # cold air stays inside
    x, y = X0 + rnd.uniform(.14, .8), rnd.uniform(-.02, .38)
    p = b3d.smooth(b3d.prim('uv_sphere', [cold_m], radius=.02, segments=16, ring_count=8, location=(x, y, .13)))
    keys(p, 'location', [(s5 + 14 * k, (x + rnd.uniform(-.05, .05), y + rnd.uniform(-.04, .04), .13)) for k in range(0, (e5 - s5) // 14 + 2)])
    b3d.visible(p, [(s5, e5)])

# ---------- lights ----------
b3d.light('AREA', 'Key', (-1.6, -2.4, 2.6), 120, (1, .94, .86), 2.5, rot=(52, 0, -35))
b3d.light('AREA', 'Fill', (1.6, -1.8, 1.4), 40, (.62, .74, 1), 2.5, rot=(68, 0, 42))
b3d.light('POINT', 'Inside', (0, .25, 1.2), 4, (.75, .88, 1), .1)
b3d.light('AREA', 'CutKey', (X0 + .6, -.9, 1.6), 40, (1, .95, .88), 2, rot=(30, 0, 25))
b3d.light('AREA', 'CutFill', (X0 - .8, -.4, 1.0), 14, (.62, .74, 1), 2, rot=(40, 0, -60))

# ---------- timeline ----------
cam, tgt = b3d.camera(30)
b3d.shot(cam, tgt, s1, e1, (-.9, -2.7, 1.3), (-.7, -2.4, 1.25), (0, 0, .95), lens=30)
b3d.shot(cam, tgt, s2, e2, (-.42, -1.15, 1.2), (-.34, -1.05, 1.15), (.17, -.66, 1.1), lens=30)
b3d.shot(cam, tgt, s3, e3, (X0 + .12, -.6, 1.25), (X0 + .08, -.52, 1.05), (X0 + .08, -.14, 0), lens=30)
b3d.shot(cam, tgt, s4, e4, (X0 + .2, -.55, 1.3), (X0 + .16, -.5, 1.15), (X0 + .12, -.08, 0), lens=30)
b3d.shot(cam, tgt, s5, e5, (X0 - .02, -.55, 1.45), (X0 + .02, -.5, 1.3), (X0 + .04, .04, 0), lens=30)
b3d.shot(cam, tgt, s6, e6, (-1.7, -1.5, 1.2), (-1.5, -1.35, 1.15), (-.05, -.15, 1.0), lens=30)
b3d.shot(cam, tgt, s7, e7, (-.7, -2.4, 1.25), (-1.1, -3.3, 1.5), (0, 0, .95), lens=30)
b3d.render(OUT, cfg.get('frames'))
