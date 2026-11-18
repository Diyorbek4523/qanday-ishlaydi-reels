"""Kran tomchilashi: a sink with an old two-handle valve faucet dripping. Big cutaway of the valve: the stem screws down and
presses a rubber washer onto the brass seat; water pressure pushes from below; the washer ages (colour, crack, tilt) and
water seeps past it to the outlet. Then a ceramic disc cartridge with a scratch that leaks. A glass jar fills from the
drips; pull back. 7 shots."""
import math, os, sys, random
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
brass = b3d.mat('Brass', (.85, .6, .25), .3, metal=.8)
steel = b3d.mat('Steel', (.7, .72, .75), .25, metal=.9)
body_m = b3d.mat('Body', (.78, .8, .84), .3, metal=.5)
cut_m = b3d.mat('Cut', (.9, .45, .2), .5)
rub_m = b3d.mat('Rubber', (.05, .05, .06), .7)
water_m = b3d.mat('Water', (.25, .6, 1), .1, emit=(.2, .55, 1), estr=1.5)
drop_m = b3d.mat('Drop', (.4, .7, 1), .05, emit=(.2, .5, 1), estr=.8)
disc_m = b3d.mat('Disc', (.92, .9, .86), .2)
scr_m = b3d.mat('Scratch', (.15, .1, .08), .8)
arrow_m = b3d.mat('Arrow', (1, .35, .2), .3, emit=(1, .3, .15), estr=3)
jar_m = b3d.mat('Jar', (.7, .8, .9), .1)
b3d.bsdf(jar_m).inputs['Alpha'].default_value = .18
try: jar_m.surface_render_method = 'BLENDED'
except Exception: pass

def box(m, c, s):
    b = b3d.prim('cube', [m], size=1, location=c); b.scale = s; return b
def cyl(m, a, b, r, v=32):
    a, b = Vector(a), Vector(b); d = b - a
    c = b3d.prim('cylinder', [m], vertices=v, radius=r, depth=d.length, location=(a + b) / 2)
    c.rotation_mode = 'QUATERNION'; c.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized()); return b3d.smooth(c)
def keys(ob, attr, fv):
    for f, v in fv: setattr(ob, attr, v); ob.keyframe_insert(attr, frame=f)
def cutaway(ob, ext=3):
    k = b3d.prim('cube', size=1, location=(ob.location.x, -ext / 2, ob.location.z)); k.scale = (ext, ext, ext)
    bo = ob.modifiers.new('Cut', 'BOOLEAN'); bo.object = k; bo.operation = 'DIFFERENCE'; k.hide_render = True; k.hide_viewport = True
    if len(ob.data.materials) < 2: ob.data.materials.append(cut_m)
    return ob

TZ = .9
# ---------- sink ----------
box(tile_m, (0, .65, 1.4), (3.4, .05, 2.0))
box(tile_m, (0, 0, -.02), (3.4, 2.4, .04))
top = box(top_m, (0, .1, TZ - .025), (2.4, 1.1, .05))
hole = b3d.prim('cylinder', vertices=64, radius=.33, depth=.3, location=(0, 0, TZ))
bo = top.modifiers.new('Hole', 'BOOLEAN'); bo.object = hole; bo.operation = 'DIFFERENCE'; hole.hide_render = True; hole.hide_viewport = True
box(cab_m, (0, -.42, .43), (2.36, .04, .82))
basin = b3d.lathe('Basin', [(0, -.18), (.24, -.17), (.31, -.11), (.335, -.02), (.345, .004), (.37, .006)])
basin.location = (0, 0, TZ); basin.data.materials.append(cer_m)
basin.modifiers.new('Sol', 'SOLIDIFY').thickness = .012
b3d.prim('cylinder', [chrome], vertices=32, radius=.035, depth=.006, location=(0, 0, TZ - .177))
# faucet: column, spout, two cross handles
FY = .42
cyl(chrome, (0, FY, TZ), (0, FY, TZ + .26), .04)
cyl(chrome, (0, FY, TZ + .2), (0, .12, TZ + .2), .028)
b3d.smooth(b3d.prim('uv_sphere', [chrome], radius=.028, location=(0, .12, TZ + .2)))
cyl(chrome, (0, .12, TZ + .2), (0, .12, TZ + .16), .022)
OUTL = Vector((0, .12, TZ + .15))
for x in (-.16, .16):
    cyl(chrome, (x * .45, FY, TZ + .14), (x, FY, TZ + .14), .02)
    cyl(chrome, (x, FY, TZ + .14), (x, FY, TZ + .2), .028)
    for a in (0, 90):
        h = cyl(chrome, (x - .055, FY, TZ + .21), (x + .055, FY, TZ + .21), .011, 16); h.rotation_mode = 'XYZ'
        h.rotation_euler = (0, R(90), R(a)); h.location = (x, FY, TZ + .21)
# drips through the whole video
BOT = TZ - .16
drop = b3d.smooth(b3d.prim('uv_sphere', [drop_m], radius=.012, location=OUTL))
CYC = 26
for c in range(0, N, CYC):
    keys(drop, 'location', [(c, OUTL), (c + 16, OUTL - Vector((0, 0, .008))), (c + 24, Vector((0, .12, BOT)))])
    keys(drop, 'scale', [(c, (.3, .3, .3)), (c + 16, (1, 1, 1.3)), (c + 23, (.9, .9, 1.4)), (c + 24, (0, 0, 0)), (c + 25, (0, 0, 0))])
# jar filling (shot 6)
JX = .62
jar = b3d.lathe('Jar', [(0, 0), (.11, 0), (.12, .02), (.12, .34), (.1, .38)]); jar.location = (JX, .15, TZ); jar.data.materials.append(jar_m)
wat = b3d.lathe('JarWater', [(0, 0), (.112, 0), (.112, .32), (0, .32)]); wat.location = (JX, .15, TZ + .01); wat.data.materials.append(water_m)
keys(wat, 'scale', [(0, (1, 1, .02)), (s6, (1, 1, .02)), (e6 - 5, (1, 1, 1)), (N, (1, 1, 1))])
b3d.visible(jar, [(s6, N)]); b3d.visible(wat, [(s6, N)])

# ---------- big valve cutaway ----------
X0 = 4.0
body = b3d.lathe('VBody', [(.17, 0), (.25, 0), (.25, 1.0), (.17, 1.0), (.17, 0)]); body.location = (X0, 0, 0); body.data.materials.append(body_m); cutaway(body)
seat = b3d.lathe('Seat', [(.07, .36), (.17, .36), (.17, .42), (.07, .42), (.07, .36)]); seat.location = (X0, 0, 0); seat.data.materials.append(brass); cutaway(seat)
inlet = b3d.lathe('Inlet', [(.07, -.5), (.11, -.5), (.11, .36), (.07, .36), (.07, -.5)]); inlet.location = (X0, 0, 0); inlet.data.materials.append(body_m); cutaway(inlet)
outl = cyl(body_m, (X0 + .24, 0, .62), (X0 + .75, 0, .62), .08); outl.modifiers.new('Sol', 'SOLIDIFY').thickness = .025; cutaway(outl)
cap = b3d.lathe('Cap', [(.06, 1.0), (.27, 1.0), (.27, 1.08), (.06, 1.08), (.06, 1.0)]); cap.location = (X0, 0, 0); cap.data.materials.append(body_m); cutaway(cap)
stem = b3d.empty('Stem', (X0, 0, 0))
def sp(o): o.parent = stem; return o
sp(cyl(steel, (0, 0, .47), (0, 0, 1.35), .05))
for i in range(12): sp(b3d.smooth(b3d.prim('torus', [steel], major_radius=.052, minor_radius=.012, location=(0, 0, .62 + i * .035))))
for a in (0, 90):
    h = sp(cyl(chrome, (-.22, 0, 1.38), (.22, 0, 1.38), .035)); h.rotation_mode = 'XYZ'; h.rotation_euler = (0, R(90), R(a)); h.location = (0, 0, 1.38)
washer = sp(b3d.smooth(b3d.prim('cylinder', [rub_m], vertices=48, radius=.11, depth=.05, location=(0, 0, .445))))
crack = sp(box(scr_m, (.07, -.08, .445), (.06, .012, .055))); crack.rotation_euler = (0, 0, R(-40))
UP = .14
SD = s2 + int((e2 - s2) * .75)
keys(stem, 'location', [(0, (X0, 0, UP)), (s2 + 4, (X0, 0, UP)), (SD, (X0, 0, 0)), (N, (X0, 0, 0))])
keys(stem, 'rotation_euler', [(0, (0, 0, 0)), (s2 + 4, (0, 0, 0)), (SD, (0, 0, R(-720))), (s4, (0, 0, R(-720))),
                              (s4 + 20, (R(4), R(-5), R(-720))), (N, (R(4), R(-5), R(-720)))])
b3d.key_input(rub_m, 'Base Color', [(0, (.05, .05, .06)), (s3 + 10, (.05, .05, .06)), (e3 - 5, (.35, .28, .2))])
b3d.visible(crack, [(s3 + int((e3 - s3) * .6), N)])
# pressure arrows under the seat (shot 3)
arrs = [b3d.arrow(f'P{i}', (X0 + x, .02, .05), (X0 + x, .02, .3), arrow_m, .012) for i, x in enumerate((-.04, 0, .04))]
for a in arrs: b3d.visible(a, [(s3, e3)])
# water beads
rnd = random.Random(5)
inlet_p = [Vector((X0, .02, -.45)), Vector((X0, .02, .38))]
leak_p = [Vector((X0, .02, -.45)), Vector((X0, .02, .4)), Vector((X0 + .13, .02, .47)), Vector((X0 + .2, .02, .6)), Vector((X0 + .72, .02, .62))]
def along(path, t):
    seg = [(path[i + 1] - path[i]).length for i in range(len(path) - 1)]; d = t * sum(seg)
    for i, s in enumerate(seg):
        if d <= s: return path[i].lerp(path[i + 1], d / s)
        d -= s
    return path[-1]
for k in range(16):
    b = b3d.prim('uv_sphere', [water_m], radius=.022, segments=12, ring_count=8, location=(0, 0, 0))
    ph = k / 16
    for f in range(s2, e4, 2):
        if f < s4:  # pressed against the closed seat
            t = min(1, ph + (f - s2) * .02); p = along(inlet_p, t) + Vector((rnd.uniform(-.006, .006), 0, 0))
        else:       # seeping past the tilted washer
            t = (ph + (f - s4) * .012) % 1; p = along(leak_p, t)
        b.location = p; b.keyframe_insert('location', frame=f)
    b3d.visible(b, [(s2, e4)])

# ---------- ceramic cartridge ----------
X1 = 8.0
def disc(z, name):
    d = b3d.smooth(b3d.prim('cylinder', [disc_m], vertices=64, radius=.3, depth=.06, location=(X1, 0, z)))
    h = b3d.prim('cylinder', vertices=32, radius=.08, depth=.2, location=(X1 + .15, 0, z))
    bo = d.modifiers.new('H', 'BOOLEAN'); bo.object = h; bo.operation = 'DIFFERENCE'; h.hide_render = True; h.hide_viewport = True
    h.parent = d; h.matrix_parent_inverse = d.matrix_world.inverted(); return d
low = disc(0, 'Low'); upd = disc(.2, 'Up')
keys(upd, 'rotation_euler', [(s5, (0, 0, R(160))), (s5 + 20, (0, 0, R(160))), (e5, (0, 0, R(130)))])
scr = box(scr_m, (X1 - .05, -.02, .032), (.4, .03, .006)); scr.rotation_euler = (0, 0, R(15))
b3d.visible(scr, [(s5 + 15, N)])
for k in range(8):
    b = b3d.prim('uv_sphere', [water_m], radius=.014, segments=10, ring_count=6, location=(0, 0, 0))
    a = Vector((X1 - .22, -.07, .045)); c = Vector((X1 + .12, .02, .045))
    for f in range(s5 + 20, e5, 2):
        t = (k / 8 + (f - s5) * .012) % 1; b.location = a.lerp(c, t); b.keyframe_insert('location', frame=f)
    b3d.visible(b, [(s5 + 20, e5)])

b3d.light('AREA', 'Key', (1.5, -2.5, 3), 110, (1, .95, .88), 3, rot=(45, 0, 30))
b3d.light('AREA', 'KeyV', (X0 + 1.5, -3, 2.5), 140, (1, .95, .88), 3, rot=(50, 0, 25))
b3d.light('AREA', 'KeyC', (X1 + 1.2, -2.2, 2.2), 90, (1, .95, .88), 2.5, rot=(50, 0, 25))

cam, tgt = b3d.camera(35)
b3d.shot(cam, tgt, s1, e1, (.12, -.8, 1.3), (.05, -.62, 1.25), (0, .22, 1.02), lens=35)
b3d.shot(cam, tgt, s2, e2, (X0 + .2, -3.0, .8), (X0 + .1, -2.6, .7), (X0, 0, .55), lens=35)
b3d.shot(cam, tgt, s3, e3, (X0 + .15, -1.5, .35), (X0 + .08, -1.3, .38), (X0, 0, .3), lens=35)
b3d.shot(cam, tgt, s4, e4, (X0 + .45, -2.0, .65), (X0 + .38, -1.75, .6), (X0 + .22, 0, .5), lens=35)
b3d.shot(cam, tgt, s5, e5, (X1 + .3, -1.2, .4), (X1 + .2, -1.0, .32), (X1, 0, .07), lens=35)
b3d.shot(cam, tgt, s6, e6, (.5, -1.0, 1.3), (.48, -.85, 1.25), (.42, .15, 1.0), lens=35)
b3d.shot(cam, tgt, s7, e7, (.1, -1.4, 1.5), (.1, -2.4, 1.8), (.1, .2, 1.0), lens=35)
b3d.render(OUT, cfg.get('frames'))
