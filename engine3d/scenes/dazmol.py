"""Dazmol (iron) thermostat: an iron on an ironing board, its orange light blinking. The shell comes off: a heating
element in the soleplate glows, current (yellow beads) runs cord -> bimetal strip -> contact -> heater. Heat bends the
two-layer strip down, the contact opens (spark), heater and light go dark; it cools, the strip springs back, contact
closes. The temperature knob screws the fixed contact up or down. 8 shots."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy, bmesh

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.03, .035, .08), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7), (s8, e8) = list(zip(S[:-1], S[1:]))
R = math.radians

# ---------- materials ----------
board_m = b3d.mat('Board', (.18, .32, .55), .85, bump=.15)
leg_m = b3d.mat('Leg', (.55, .57, .6), .3, metal=.8)
sole_m = b3d.mat('Sole', (.82, .84, .88), .3, metal=.55, emit=(1, .35, .08), estr=0)
shell_m = b3d.mat('Shell', (.92, .93, .95), .35)
trim_m = b3d.mat('Trim', (.1, .55, .75), .35)
handle_m = b3d.mat('Handle', (.08, .4, .6), .4)
knob_m = b3d.mat('Knob', (.12, .12, .14), .4)
ceram_m = b3d.mat('Ceramic', (.93, .9, .82), .7)
heat_m = b3d.mat('Heater', (.5, .2, .1), .4, metal=.4, emit=(1, .3, .05), estr=0)
bim_a = b3d.mat('BimA', (.95, .5, .25), .3, metal=.7, emit=(1, .3, .05), estr=0)
bim_b = b3d.mat('BimB', (.62, .64, .68), .3, metal=.8, emit=(1, .3, .05), estr=0)
silver = b3d.mat('Silver', (.9, .9, .92), .15, metal=1.0)
copper = b3d.mat('Copper', (.95, .45, .2), .3, metal=.6)
cord_m = b3d.mat('Cord', (.1, .1, .12), .6)
lamp_m = b3d.mat('Lamp', (1, .55, .1), .3, emit=(1, .5, .08), estr=0)
cur_m = b3d.mat('Current', (1, .85, .2), .3, emit=(1, .8, .15), estr=4)
heatarr_m = b3d.mat('HeatArrow', (1, .4, .1), .4, emit=(1, .35, .05), estr=3)
spark_m = b3d.mat('Spark', (.7, .85, 1), .3, emit=(.7, .85, 1), estr=8)
txt_m = b3d.mat('Txt', (.95, .95, .95), .5)

def box(m, c, s, bevel=0):
    b = b3d.prim('cube', [m], size=1, location=c); b.scale = s
    if bevel:
        bv = b.modifiers.new('Bv', 'BEVEL'); bv.width = bevel; bv.segments = 4; b3d.smooth(b)
    return b
def curve(name, pts, m, r=.03, cyclic=False, smooth=False):
    cv = bpy.data.curves.new(name, 'CURVE'); cv.dimensions = '3D'; cv.bevel_depth = r; cv.bevel_resolution = 3; cv.use_fill_caps = True
    sp = cv.splines.new('POLY'); sp.points.add(len(pts) - 1); sp.use_cyclic_u = cyclic
    for bp, p in zip(sp.points, pts): bp.co = (*p, 1)
    cv.materials.append(m); return b3d.link(bpy.data.objects.new(name, cv))
def ball(m, r, loc=(0, 0, 0)): return b3d.smooth(b3d.prim('uv_sphere', [m], segments=12, ring_count=6, radius=r, location=loc))
def keys(ob, attr, fv):
    for f, v in fv: setattr(ob, attr, v); ob.keyframe_insert(attr, frame=f)
def lerp(a, b, u): return tuple(x + (y - x) * u for x, y in zip(a, b))

def outline(sc_=1.0, n=28):  # iron footprint, pointed toward +x
    pts = []
    for i in range(n + 1):
        x = -1.0 + 2.1 * i / n
        w = .55 if x < -.2 else .55 * math.cos((x + .2) / 1.3 * math.pi / 2)
        w = max(w, .015)
        if x < -.92: w *= math.sqrt(max(.0, 1 - ((x + .92) / .08) ** 2)) * .4 + .6
        pts.append((x * sc_, w * sc_))
    return [(x, -w) for x, w in pts] + [(x, w) for x, w in reversed(pts)]
def prism(name, pts, z0, z1, m, bevel=0):
    bm = bmesh.new(); vs = [bm.verts.new((x, y, z0)) for x, y in pts]
    f = bm.faces.new(vs); r = bmesh.ops.extrude_face_region(bm, geom=[f])
    for v in [g for g in r['geom'] if isinstance(g, bmesh.types.BMVert)]: v.co.z = z1
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); ob = b3d.link(bpy.data.objects.new(name, me)); me.materials.append(m)
    if bevel:
        bv = ob.modifiers.new('Bv', 'BEVEL'); bv.width = bevel; bv.segments = 3
    return ob

# ---------- timing ----------
T_off = s5 + int((e5 - s5) * .3)     # contact opens
T_on = s6 + int((e6 - s6) * .45)     # contact closes again
H0 = s1 + int((e1 - s1) * .55)       # hook: light goes off
closed = [(0, H0), (s2, T_off), (T_on, N)]

# ---------- ironing board ----------
box(board_m, (0, 0, -.07), (7, 2.6, .12), bevel=.05)
for x in (-2.5, 2.5): box(leg_m, (x, 0, -1.6), (.08, 2.0, .08))

# ---------- iron ----------
prism('Sole', outline(), 0, .1, sole_m, bevel=.02)
prism('SoleTop', outline(.95), .1, .14, sole_m)
shell = prism('Shell', outline(.9), .14, .48, shell_m, bevel=.05)
trim = prism('Trim', outline(.92), .14, .2, trim_m)
handle = curve('Handle', [(-.8, 0, .44), (-.72, 0, .98), (-.55, 0, 1.06), (.3, 0, 1.06), (.45, 0, .9), (.55, 0, .46)], handle_m, r=.09)
b3d.visible(shell, [(s1, s2), (s8, N)]); b3d.visible(trim, [(s1, s2), (s8, N)]); b3d.visible(handle, [(s1, s2), (s8, N)])
cap = box(trim_m, (-.45, 0, .5), (.5, .5, .04), bevel=.02); b3d.visible(cap, [(s1, s2), (s8, N)])
lamp = ball(lamp_m, .07, (-.45, -.18, .55))
lamp_l = b3d.light('POINT', 'LampL', (-.45, -.35, .7), 0, (1, .55, .15), .1)
cord = curve('Cord', [(-.95, 0, .3), (-1.4, 0, .45), (-2.0, .2, .5), (-2.8, .8, .3), (-3.4, 1.2, .1)], cord_m, r=.045)
lv = [(0, 1), (H0, 1), (H0 + 1, 0), (s2 - 1, 0), (s2, 1), (T_off, 1), (T_off + 1, 0), (T_on, 0), (T_on + 1, 1), (N, 1)]
b3d.key_input(lamp_m, 'Emission Strength', [(f, 5. * v) for f, v in lv])
keys(lamp_l.data, 'energy', [(f, 40. * v) for f, v in lv])

# heating element: U loop sunk in the soleplate
hp = [(-.75, -.3, .16), (.35, -.3, .16), (.62, -.12, .16), (.68, 0, .16), (.62, .12, .16), (.35, .3, .16), (-.75, .3, .16)]
heater = curve('Heater', hp, heat_m, r=.045)
hv = [(0, 1.5), (H0, 1.5), (s2, .3), (s3, .3), (e3, 2.5), (T_off, 3.), (T_on, .4), (T_on + 25, 1.8), (s7, 2.), (N, 2.)]
b3d.key_input(heat_m, 'Emission Strength', [(f, v) for f, v in hv])
b3d.key_input(sole_m, 'Emission Strength', [(f, v * .08) for f, v in hv])
for m in (bim_a, bim_b): b3d.key_input(m, 'Emission Strength', [(0, 0.), (s4, 0.), (T_off, .9), (T_on, .2), (s7, .4), (N, .4)])

# thermostat: ceramic block, bimetal strip on a pivot, fixed contact on a screw bracket under the knob
box(ceram_m, (-.38, 0, .21), (.18, .3, .14), bevel=.02)
bim = b3d.empty('BimPv', (-.32, 0, .3))
for dz, m in ((-.018, bim_a), (.018, bim_b)):
    b = box(m, (0, 0, 0), (.62, .16, .036)); b.parent = bim; b.location = (.31, 0, dz)
mc = b3d.smooth(b3d.prim('cylinder', [silver], vertices=20, radius=.05, depth=.04, location=(0, 0, 0))); mc.parent = bim; mc.location = (.56, 0, .04)
keys(bim, 'rotation_euler', [(f, (0, R(a), 0)) for f, a in ((0, 0), (s4, 0), (T_off - 3, 3), (T_off, 9), (T_on - 1, 7), (T_on, 0), (N, 0))])
post = box(ceram_m, (.42, .0, .3), (.12, .3, .32), bevel=.02)
rod = b3d.empty('RodPv', (0, 0, 0))
brk = box(copper, (.32, 0, .42), (.26, .14, .04)); brk.parent = rod
fc = b3d.smooth(b3d.prim('cylinder', [silver], vertices=20, radius=.05, depth=.05, location=(.24, 0, .375))); fc.parent = rod
screw = b3d.smooth(b3d.prim('cylinder', [silver], vertices=16, radius=.03, depth=.3, location=(.42, 0, .56))); screw.parent = rod
knob = b3d.smooth(b3d.prim('cylinder', [knob_m], vertices=32, radius=.17, depth=.09, location=(.42, 0, .74)))
grip = box(knob_m, (0, 0, 0), (.3, .06, .07), bevel=.02); grip.parent = knob; grip.location = (0, 0, .07)
mark = box(lamp_m, (0, 0, 0), (.025, .1, .02)); mark.parent = knob; mark.location = (0, -.12, .05)
keys(knob, 'rotation_euler', [(0, (0, 0, 0)), (s7, (0, 0, 0)), (e7 - 10, (0, 0, R(-140))), (N, (0, 0, R(-140)))])
keys(rod, 'location', [(0, (0, 0, 0)), (s7, (0, 0, 0)), (e7 - 10, (0, 0, -.035)), (N, (0, 0, -.035))])
for nm, a, b in (('Lo', (.85, -.2, .74), 'MIN'), ('Hi', (.85, .2, .74), 'MAX')):
    pass
# labels around the knob in shot 7
for t, x, y in (('MIN', .2, -.26), ('MAX', .64, -.26)):
    bpy.ops.object.text_add(location=(x, y, .78)); o = bpy.context.object; o.data.body = t; o.data.size = .065
    o.data.align_x = 'CENTER'; o.data.extrude = .006; o.data.materials.append(txt_m); o.rotation_euler = (R(60), 0, R(0))
    b3d.visible(o, [(s7, e7)])
# wires
curve('W1', [(-.95, 0, .3), (-.7, -.1, .3), (-.4, -.1, .3), (-.32, 0, .3)], copper, r=.02)
curve('W2', [(.54, 0, .42), (.62, .1, .38), (.65, .2, .2), (.62, .3, .17)], copper, r=.02)
# heat arrows (shot 4) and sparks
for k, x in enumerate((-.2, .0, .2)):
    a = b3d.arrow(f'Heat{k}', (x, -.3, .17), (x, -.12, .29), heatarr_m, r=.012); b3d.visible(a, [(s4, T_off)])
sp = ball(spark_m, .05, (.24, -.02, .33)); b3d.visible(sp, [(T_off, T_off + 6), (T_on, T_on + 5)])
b3d.flicker(sp, 'scale', T_off, T_off + 6, .5, 1.5, every=1, seed=3)
spl = b3d.light('POINT', 'SparkL', (.24, -.3, .4), 0, (.7, .85, 1), .05)
keys(spl.data, 'energy', [(T_off, 0), (T_off + 1, 150), (T_off + 5, 0), (T_on, 0), (T_on + 1, 120), (T_on + 4, 0)])

# current beads: cord -> strip -> contacts -> bracket -> heater
PATH = [(-.95, -.02, .3), (-.4, -.12, .3), (-.3, -.1, .32), (.24, -.1, .34), (.32, -.1, .43), (.54, -.1, .43), (.64, -.1, .3), (.62, -.32, .17),
        (.35, -.32, .17), (-.75, -.32, .17)]
seg = [math.dist(PATH[i], PATH[i + 1]) for i in range(len(PATH) - 1)]; TOT = sum(seg)
def along(u):
    d = (u % 1) * TOT
    for i, L in enumerate(seg):
        if d <= L: return lerp(PATH[i], PATH[i + 1], d / L)
        d -= L
    return PATH[-1]
for k in range(12):
    p = ball(cur_m, .028)
    for f in range(s2, N, 2): p.location = along((f - s2) / 75 + k / 12); p.keyframe_insert('location', frame=f)
    b3d.visible(p, [(s2, T_off), (T_on, s8)])

# ---------- lights ----------
b3d.light('AREA', 'Key', (2.5, -4, 4), 300, (1, .95, .88), 5, rot=(50, 0, 30))
b3d.light('AREA', 'Fill', (-3, -3.5, 2), 140, (.62, .74, 1), 4, rot=(70, 0, -40))
b3d.light('AREA', 'Top', (0, 0, 3), 80, (1, .95, .9), 3)

# ---------- timeline ----------
cam, tgt = b3d.camera(30)
b3d.shot(cam, tgt, s1, e1, (1.35, -2.6, 1.45), (1.15, -2.3, 1.35), (0, 0, .55))
b3d.shot(cam, tgt, s2, e2, (.5, -1.7, 1.3), (.35, -1.45, 1.15), (-.05, 0, .3))
b3d.shot(cam, tgt, s3, e3, (-.1, -1.5, 2.4), (.05, -1.3, 2.2), (0, 0, .15))
b3d.shot(cam, tgt, s4, e4, (.1, -1.25, .95), (.05, -1.1, .88), (0, 0, .27))
b3d.shot(cam, tgt, s5, e5, (.5, -1.2, .8), (.42, -1.05, .74), (.15, 0, .33))
b3d.shot(cam, tgt, s6, e6, (-.45, -1.25, .75), (-.35, -1.1, .7), (.05, 0, .3))
b3d.shot(cam, tgt, s7, e7, (.75, -1.05, 1.35), (.65, -.9, 1.25), (.35, 0, .5))
b3d.shot(cam, tgt, s8, e8, (1.0, -2.2, 1.3), (1.7, -3.4, 1.9), (0, 0, .55))
b3d.render(OUT, cfg.get('frames'))
