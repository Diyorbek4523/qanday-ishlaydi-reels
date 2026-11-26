"""Kir sakrash: why a front-loading washing machine shakes and walks. Shot 1 outside, machine shakes and hops (clothes clumped).
Shot 2 see-through cabinet: drum spins fast, water drops fly out of the drum. Shot 3 springs (top) and dampers (bottom) glow.
Shot 4 concrete counterweight glows. Shot 5 clothes clumped on one side, red arrow turns with the drum, whole machine shakes.
Shot 6 back: orange transport bolts glow + a foot is screwed level. Shot 7 pull back."""
import math, os, sys, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy
from mathutils import Vector

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.02, .02, .045), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))

def blend(m, a):
    b3d.bsdf(m).inputs['Alpha'].default_value = a
    try: m.surface_render_method = 'BLENDED'
    except Exception: pass
    return m

floor_m = b3d.mat('Tile', (.42, .33, .26), .5, bump=.01)
wall_m = b3d.mat('Wall', (.2, .25, .34), .85, bump=.02)
cab_m = b3d.mat('Cabinet', (.78, .8, .84), .3)
panel_m = b3d.mat('Panel', (.75, .77, .82), .35)
ring_m = b3d.mat('Ring', (.7, .72, .76), .2, metal=.8)
glass_m = blend(b3d.mat('Glass', (.3, .5, .7), .05), .12)
tub_m = blend(b3d.mat('Tub', (.45, .5, .58), .4), .25)
drum_m = blend(b3d.mat('Drum', (.6, .65, .72), .2, metal=.6), .3)
lift_m = b3d.mat('Lifter', (.7, .72, .76), .3, metal=.6)
spring_m = b3d.mat('Spring', (.75, .75, .78), .3, metal=.9, emit=(1, .8, .15), estr=0)
damp_m = b3d.mat('Damper', (.15, .15, .17), .5, emit=(1, .8, .15), estr=0)
conc_m = b3d.mat('Concrete', (.3, .3, .29), .95, emit=(1, .8, .15), estr=0, bump=.15)
bolt_m = b3d.mat('Bolt', (1, .45, .05), .4, emit=(1, .4, .05), estr=0)
foot_m = b3d.mat('Foot', (.12, .12, .13), .5)
water_m = b3d.mat('Water', (.3, .65, 1), .1, emit=(.2, .55, 1), estr=2.5)
red_m = b3d.mat('Red', (1, .15, .1), .3, emit=(1, .1, .05), estr=4)
yel_m = b3d.mat('Yel', (1, .85, .2), .3, emit=(1, .8, .15), estr=4)
knob_m = b3d.mat('Knob', (.2, .22, .26), .3)
led_m = b3d.mat('Led', (.2, 1, .4), .3, emit=(.2, 1, .4), estr=4)
cloth = [b3d.mat(f'Cloth{i}', c, .95, bump=.05) for i, c in enumerate(((.85, .15, .15), (.95, .75, .15), (.2, .4, .85), (.2, .65, .3)))]

def keys(ob, attr, fv):
    for f, v in fv: setattr(ob, attr, v); ob.keyframe_insert(attr, frame=f)

def box(name, m, loc, dims, bev=0, parent=None):
    ob = b3d.prim('cube', [m], size=1, location=loc); ob.scale = dims; ob.name = name
    if bev: ob.modifiers.new('bev', 'BEVEL').width = bev; ob.modifiers['bev'].segments = 3
    if parent: ob.parent = parent
    return ob

def cyl_y(name, m, loc, r, d, parent=None, verts=48):  # cylinder along Y (front-back)
    ob = b3d.smooth(b3d.prim('cylinder', [m], vertices=verts, radius=r, depth=d, location=loc)); ob.rotation_euler = (math.radians(90), 0, 0); ob.name = name
    if parent: ob.parent = parent
    return ob

def tube(name, pts, r, m, parent=None):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 4
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for p, c in zip(sp.points, pts): p.co = (*c, 1)
    ob = b3d.link(bpy.data.objects.new(name, cu)); ob.data.materials.append(m)
    if parent: ob.parent = parent
    return ob

# ---------- room ----------
b3d.prim('plane', [floor_m], size=10, location=(0, 0, 0))
b3d.prim('plane', [wall_m], size=10, location=(0, 1.9, 2), rotation=(math.radians(90), 0, 0))

M = b3d.empty('Machine', (0, 0, 0))   # whole machine (shakes)
TC = Vector((0, .02, .47))            # tub / drum centre

# cabinet (see-through in shots 2-5)
box('Cabinet', cab_m, (0, 0, .46), (.6, .6, .84), .025, M)
b3d.key_input(cab_m, 'Alpha', [(0, 1), (s2 - 1, 1), (s2, .12), (e5 - 1, .12), (e5, 1)])
try: cab_m.surface_render_method = 'BLENDED'
except Exception: pass
box('Panel', panel_m, (0, -.302, .82), (.58, .01, .09), .005, M)
box('Drawer', cab_m, (-.19, -.31, .82), (.16, .02, .07), .008, M)
cyl_y('Knob', knob_m, (.17, -.312, .82), .03, .02, M)
box('Led', led_m, (.05, -.309, .825), (.06, .004, .015), 0, M)
dr = b3d.smooth(b3d.prim('torus', [ring_m], major_radius=.17, minor_radius=.025, major_segments=48, minor_segments=12, location=(0, -.31, TC.z)))
dr.rotation_euler = (math.radians(90), 0, 0); dr.parent = M
cyl_y('DoorGlass', glass_m, (0, -.31, TC.z), .16, .015, M)
for x in (-.25, .25):
    for y in (-.25, .25):
        f = b3d.prim('cylinder', [foot_m], vertices=16, radius=.025, depth=.04, location=(x, y, .02)); f.parent = M; f.name = 'Foot'
FOOT = f  # last foot = back-right (seen in shot 6)

# tub (hangs on springs) and drum (spins)
cyl_y('Tub', tub_m, tuple(TC), .26, .42, M)
D = b3d.empty('Drum', tuple(TC)); D.parent = M
cyl_y('DrumShell', drum_m, (0, 0, 0), .22, .36, D)
for a in range(3):
    an = a * 2 * math.pi / 3
    lf = box('Lifter', lift_m, (.19 * math.cos(an), 0, .19 * math.sin(an)), (.05, .3, .05), .01, D)
    lf.rotation_euler = (0, -an, 0)

# clothes: even set and clumped set (both turn with the drum)
rnd = random.Random(3)
even, clump = [], []
for i in range(9):
    a = i * 2 * math.pi / 9
    ob = b3d.smooth(b3d.prim('uv_sphere', [cloth[i % 4]], radius=.055, segments=16, ring_count=8, location=(.15 * math.cos(a), rnd.uniform(-.1, .1), .15 * math.sin(a))))
    ob.scale = (1.2, 1, .7); ob.rotation_euler = (0, -a, 0); ob.parent = D; even.append(ob)
for i in range(9):
    a = -math.pi / 2 + rnd.uniform(-.45, .45)
    r = rnd.uniform(.1, .16)
    ob = b3d.smooth(b3d.prim('uv_sphere', [cloth[i % 4]], radius=.06, segments=16, ring_count=8, location=(r * math.cos(a), rnd.uniform(-.11, .11), r * math.sin(a))))
    ob.parent = D; clump.append(ob)
for ob in even: b3d.visible(ob, [(e1, s5), (e5, e7 + 1)])
for ob in clump: b3d.visible(ob, [(s1, e1), (s5, e5)])
arr = b3d.arrow('Pull', (0, -.21, 0), (0, -.21, -.26), red_m, .014); arr.parent = D; arr.location = (0, -.21, 0)
b3d.visible(arr, [(s5 + 8, e5)])

# drum rotation: speed per shot (visual rev/s)
spd = (1.6, 1.8, .45, .45, 1.3, .3, .8)
ang = 0.0
for f in range(0, N + 1, 2):
    si = max(i for i, s in enumerate(S[:-1]) if f >= s)
    D.rotation_euler = (0, -ang, 0); D.keyframe_insert('rotation_euler', frame=f)
    ang += spd[si] * 2 * math.pi * 2 / 30

# springs (tub top -> cabinet top) and dampers (tub bottom -> base)
def spring(x, y, z0, z1, r=.022, turns=7):
    n = turns * 21
    pts = [(x + r * math.cos(t * .3), y + r * math.sin(t * .3), z0 + (z1 - z0) * t / n) for t in range(n + 1)]
    return tube('Spring', pts, .0045, spring_m, M)
for x in (-.13, .13):
    spring(x, .06, TC.z + .25, .86)
    o = b3d.prim('cylinder', [damp_m], vertices=16, radius=.02, depth=.12, location=(x, .06, .1)); o.parent = M
    o = b3d.prim('cylinder', [spring_m], vertices=16, radius=.008, depth=.1, location=(x, .06, .2)); o.parent = M
b3d.key_input(spring_m, 'Emission Strength', [(0, 0), (s3, 0), (s3 + 6, 2.5), (e3 - 2, 2.5), (e3, 0)])
b3d.key_input(damp_m, 'Emission Strength', [(0, 0), (s3, 0), (s3 + 6, 2.5), (e3 - 2, 2.5), (e3, 0)])

# concrete counterweight on top-front of the tub
box('Concrete', conc_m, (0, -.14, TC.z + .27), (.32, .1, .09), .015, M)
b3d.key_input(conc_m, 'Emission Strength', [(0, 0), (s4, 0), (s4 + 8, 1.6), (e4 - 2, 1.6), (e4, 0)])
ca = b3d.arrow('ConcDown', (0, 0, 0), (0, 0, -.2), yel_m, .015); ca.parent = M; ca.location = (0, -.14, TC.z + .55)
b3d.visible(ca, [(s4 + 8, e4)])

# water drops flung from the drum (shot 2)
for i in range(36):
    p = b3d.prim('uv_sphere', [water_m], radius=.012, segments=8, ring_count=6, location=(0, 0, 0)); p.parent = M
    a = rnd.uniform(0, 2 * math.pi); y = TC.y + rnd.uniform(-.15, .15); t0 = s2 + rnd.randint(0, max(1, e2 - s2 - 12))
    p0 = (TC.x + .2 * math.cos(a), y, TC.z + .2 * math.sin(a)); p1 = (TC.x + .255 * math.cos(a - .5), y, TC.z + .255 * math.sin(a - .5))
    keys(p, 'location', [(t0, p0), (t0 + 10, p1)])
    b3d.visible(p, [(t0, t0 + 11)])

# transport bolts on the back panel (shot 6) + levelling foot
for (x, z) in ((-.2, .72), (.2, .72), (0, .22)):
    b = b3d.prim('cylinder', [bolt_m], vertices=6, radius=.03, depth=.03, location=(x, .315, z)); b.rotation_euler = (math.radians(90), 0, 0); b.parent = M
b3d.key_input(bolt_m, 'Emission Strength', [(0, 0), (s6, 0), (s6 + 8, 2.2), (e6 - 2, 2.2), (e6, 0)])
fa = b3d.arrow('FootArrow', (0, 0, 0), (-.17, -.17, -.17), yel_m, .012); fa.parent = M; fa.location = (.44, .44, .23)
b3d.visible(fa, [(s6 + 20, e6)])
keys(FOOT, 'rotation_euler', [(s6 + 20, (0, 0, 0)), (e6, (0, 0, math.radians(540)))])

# shaking: hop + sway (shots 1 and 5)
r2 = random.Random(9)
def shake(f0, f1, amp):
    for f in (f0 - 1, f1):
        M.location = (0, 0, 0); M.rotation_euler = (0, 0, 0)
        M.keyframe_insert('location', frame=f); M.keyframe_insert('rotation_euler', frame=f)
    for f in range(f0, f1, 2):
        t = (f - f0) / 30
        M.location = (amp * math.sin(t * 2 * math.pi * 5.5) + r2.uniform(-amp, amp) * .3, amp * .4 * math.sin(t * 2 * math.pi * 3.1), abs(amp * .8 * math.sin(t * 2 * math.pi * 5.5)))
        M.rotation_euler = (0, amp * 1.5 * math.sin(t * 2 * math.pi * 5.5 + 1), amp * 1.2 * math.sin(t * 2 * math.pi * 2.7))
        M.keyframe_insert('location', frame=f); M.keyframe_insert('rotation_euler', frame=f)
M.location = (0, 0, 0); M.keyframe_insert('location', frame=0); M.rotation_euler = (0, 0, 0); M.keyframe_insert('rotation_euler', frame=0)
shake(s1 + 1, e1 - 1, .018)
shake(s5 + 10, e5 - 1, .022)

b3d.light('AREA', 'Key', (-1.3, -2.0, 2.4), 90, (1, .88, .75), 3, rot=(50, 0, -30))
b3d.light('AREA', 'Fill', (1.8, -1.6, 1.4), 35, (.6, .7, 1), 3, rot=(65, 0, 45))
b3d.light('AREA', 'Back', (1.2, 1.5, 1.6), 40, (1, .9, .8), 2, rot=(-60, 0, 150))
b3d.light('POINT', 'Inner', (0, -.6, .55), 8, (.8, .9, 1), .3)
b3d.light('POINT', 'BackLamp', (.75, 1.15, 1.0), 45, (1, .88, .75), .3)

# ---------- camera ----------
cam, tgt = b3d.camera(35)
b3d.shot(cam, tgt, s1, e1, (.95, -1.75, 1.05), (.85, -1.55, .98), (0, 0, .42), lens=35)
b3d.shot(cam, tgt, s2, e2, (.18, -1.05, .6), (.12, -.95, .56), tuple(TC), lens=35)
b3d.shot(cam, tgt, s3, e3, (1.0, -.65, 1.05), (.95, -.55, 1.0), (0, .02, .55), lens=35)
b3d.shot(cam, tgt, s4, e4, (.4, -.7, 1.35), (.34, -.62, 1.3), (0, -.12, .74), lens=38)
b3d.shot(cam, tgt, s5, e5, (.55, -1.35, .8), (.48, -1.25, .75), tuple(TC), lens=35)
b3d.shot(cam, tgt, s6, e6, (.95, 1.3, .65), (.88, 1.2, .58), (.05, .3, .35), lens=35)
b3d.shot(cam, tgt, s7, e7, (.5, -1.6, 1.0), (.8, -2.8, 1.6), (0, 0, .45), lens=35)

b3d.render(OUT, cfg.get('frames'))
