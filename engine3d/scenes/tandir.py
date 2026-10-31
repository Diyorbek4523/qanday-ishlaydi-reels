"""Tandir: clay oven, fire heats the walls, dough slapped on the wall sticks and bakes. 7 shots (one per script scene)."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d
from mathutils import Vector

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.05, .06, .11), preview=cfg.get('preview'))
sh = list(zip(S[:-1], S[1:]))  # (f0, f1) per scene

# ---------- materials ----------
clay = b3d.mat('Clay', (.50, .29, .17), .95, bump=.25)
inner = b3d.mat('ClayIn', (.20, .10, .06), .9, emit=(1., .32, .07), estr=0., bump=.3)
cut = b3d.mat('ClayCut', (.62, .40, .26), 1.)
dirt = b3d.mat('Dirt', (.16, .11, .08), 1., bump=.4)
fire = b3d.mat('Fire', (1, .3, .03), .5, emit=(1., .3, .02), estr=2.2)
coal = b3d.mat('Coal', (.05, .01, 0), .8, emit=(1., .2, .02), estr=6)
dough = b3d.mat('Dough', (.95, .8, .55), .65, bump=.15)
crust = b3d.mat('Crust', (.86, .74, .55), .6, bump=.1)
heat = b3d.mat('Heat', (1, .3, .05), .5, emit=(1., .3, .03), estr=3)

# ---------- tandir: lathe profile, solidified inward, plus a cutaway copy ----------
PROF = [(.78, 0), (.84, .25), (.85, .5), (.78, .8), (.6, 1.05), (.42, 1.2), (.4, 1.26)]; TH = .09
def r_in(z):
    for (r0, z0), (r1, z1) in zip(PROF, PROF[1:]):
        if z0 <= z <= z1: return r0 + (r1 - r0) * (z - z0) / (z1 - z0) - TH
    return PROF[-1][0] - TH
def tandir(name, cutaway):
    ob = b3d.lathe(name, PROF); ob.data.materials.append(clay); ob.data.materials.append(inner); ob.data.materials.append(cut)
    so = ob.modifiers.new('Th', 'SOLIDIFY'); so.thickness = TH; so.offset = -1; so.use_even_offset = True; so.material_offset = 1
    if cutaway:
        cutter = b3d.prim('cube', [cut], size=1, location=(0, -1.0, .6)); cutter.scale = (3, 2, 3); cutter.hide_render = True; cutter.hide_viewport = True
        bo = ob.modifiers.new('Cut', 'BOOLEAN'); bo.operation = 'DIFFERENCE'; bo.object = cutter
        try: bo.material_mode = 'TRANSFER'
        except (AttributeError, TypeError): pass
    return ob
full, half = tandir('Tandir', False), tandir('TandirCut', True)
ground = b3d.prim('plane', [dirt], size=40)
brick = b3d.mat('Brick', (.42, .22, .13), .95, bump=.3)
for k in range(28):  # ring of mud bricks round the base
    a = k * 2 * math.pi / 28; br = b3d.prim('cube', [brick], size=1, location=(.98 * math.cos(a), .98 * math.sin(a), .07)); br.scale = (.12, .2, .14); br.rotation_euler = (0, 0, a)

# ---------- fire and coals ----------
flames = []
for i, (x, y, rr, hh) in enumerate([(0, 0, .17, .55), (.17, .1, .12, .4), (-.16, .08, .13, .42), (.05, -.15, .11, .35), (-.08, .17, .1, .32), (.12, -.05, .09, .3)]):
    f = b3d.prim('cone', [fire], vertices=24, radius1=rr, depth=hh, location=(x, y, hh / 2 + .02)); b3d.smooth(f); flames.append(f)
coals = [b3d.prim('uv_sphere', [coal], segments=12, ring_count=8, radius=.045, location=(.4 * math.cos(a), .4 * math.sin(a) * .9, .03)) for a in [k * .62 for k in range(10)]]
for i in range(10): coals[i].location = (.42 * math.cos(i * .63) * (.4 + .6 * (i % 3) / 2), .42 * math.sin(i * .63) * (.4 + .6 * (i % 3) / 2), .03)
glow = b3d.light('POINT', 'FireLight', (0, 0, .35), 300, (1, .45, .15), .25)
b3d.light('AREA', 'InFill', (0, -.55, .75), 12, (1, .7, .45), .6, rot=(90, 0, 0))
b3d.light('POINT', 'MouthGlow', (0, 0, 1.45), 25, (1, .5, .2), .3)

# ---------- bread (non): disc + rim + stamped centre ----------
def non(name, m_body, m_mid):
    root = b3d.empty(name); root.rotation_mode = 'QUATERNION'
    d = b3d.prim('cylinder', [m_body], vertices=48, radius=.155, depth=.03); b3d.smooth(d); d.parent = root
    t = b3d.prim('torus', [m_body], major_radius=.145, minor_radius=.03, major_segments=48, minor_segments=12); b3d.smooth(t); t.parent = root; t.location = (0, 0, .012)
    c = b3d.prim('cylinder', [m_mid], vertices=32, radius=.075, depth=.012); c.parent = root; c.location = (0, 0, .018)
    for k in range(6):
        a = k * math.pi / 3; p = b3d.prim('uv_sphere', [m_mid], segments=8, ring_count=6, radius=.008); p.parent = root; p.location = (.04 * math.cos(a), .04 * math.sin(a), .025)
    return root
def on_wall(root, ang, z, gap=.045):  # flat against the (sloping) inner wall, facing the centre
    d = Vector((math.cos(ang), math.sin(ang), 0)); slope = (r_in(z + .01) - r_in(z - .01)) / .02
    inward = Vector((-d.x, -d.y, slope)).normalized(); p = d * r_in(z) + inward * gap; p.z += z
    root.location = p; root.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(inward)
    return p
breads = []  # (root, on the back half = still there in the cutaway)
for k, deg in enumerate([30, 90, 150, 210, 270, 330]): b = non(f'Non_a{k}', dough, crust); on_wall(b, math.radians(deg), .38); breads.append((b, deg < 180))
for k, deg in enumerate([18, 162, 234, 306]): b = non(f'Non_b{k}', dough, crust); on_wall(b, math.radians(deg), .74); breads.append((b, deg < 180))
thrown = non('NonThrown', dough, crust); target = on_wall(thrown, math.radians(90), .74)

# ---------- heat rays (shot 6): from the wall toward the breads / centre ----------
rays = []
for k, deg in enumerate([40, 75, 105, 140, 60, 120]):
    z = .3 if k < 4 else .62; d = Vector((math.cos(math.radians(deg)), math.sin(math.radians(deg)), 0))
    a = d * (r_in(z) - .06); a.z = z; b = d * (r_in(z) - .42); b.z = z + .05
    rays.append(b3d.arrow(f'Ray{k}', a, b, heat, r=.035))

# ---------- lights ----------
b3d.light('SUN', 'Sun', (0, 0, 5), 2.2, (1, .78, .55), .3, rot=(62, 0, -35))
b3d.light('AREA', 'Fill', (-2.5, -2.5, 2.5), 120, (.6, .7, 1), 3, rot=(55, 0, -45))

# ---------- timeline ----------
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = sh
cam, tgt = b3d.camera(28)
b3d.shot(cam, tgt, s1, e1, (1.7, -2.5, 1.35), (1.15, -2.0, 1.15), (0, .2, .55), lens=28)  # hook: cutaway, fire and bread on the glowing wall
b3d.shot(cam, tgt, s2, e2, (2.7, -2.9, 1.5), (1.3, -3.3, 1.2), (0, 0, .7), lens=30)       # outside, slow orbit
b3d.shot(cam, tgt, s3, e3, (0, -3.1, .95), (0, -2.6, .85), (0, .2, .5), lens=30)          # cutaway: fire lights, walls heat up
b3d.shot(cam, tgt, s4, e4, (.7, -2.3, 1.05), (.5, -2.1, 1.0), (0, .35, .7), lens=30)       # cutaway: dough flies onto the wall
b3d.shot(cam, tgt, s5, e5, (.35, -.55, .95), (.25, -.35, .85), (0, target.y, .74), lens=35) # close-up: dough on hot clay
b3d.shot(cam, tgt, s6, e6, (0, -3.3, 1.05), (.3, -2.9, 1.0), (0, .25, .5), lens=30)        # cutaway: heat rays, bread browns
b3d.shot(cam, tgt, s7, e7, (-.8, -2.2, 1.0), (-1.4, -3.8, 1.9), (0, 0, .7), lens=30)       # end: pull back from the tandir at dusk

b3d.visible(full, [(s2, e2), (s7, e7)]); b3d.visible(half, [(s1, e1), (s3, e6)])
for b, back in breads: b3d.visible(b, [(s1, e1), (s4, e6)] if back else [])
b3d.visible(thrown, [(s4, e6)])
for r in rays: b3d.visible(r, [(s6 + 10, e6)])

# wall glow: hot in the hook, cold at the start of shot 3, heats through it
b3d.key_input(inner, 'Emission Strength', [(s1, .45), (s3 - 1, .45), (s3, 0.), (s3 + int((e3 - s3) * .8), .6)])
b3d.key_input(inner, 'Base Color', [(s1, (.2, .1, .06)), (s3 - 1, (.2, .1, .06)), (s3, (.35, .2, .12)), (s3 + int((e3 - s3) * .8), (.2, .1, .06))])
fire_mul = lambda f: .35 + .65 * min(1, max(0, (f - s3) / max(1, (e3 - s3) * .6))) if s3 <= f < e3 else 1.
for i, fl in enumerate(flames): b3d.flicker(fl, 'scale', 0, N, .8, 1.25, every=3, seed=i, mul=fire_mul)
b3d.flicker(glow, 'energy', 0, N, 90, 150, every=2, seed=9, mul=fire_mul)

# dough: pale until shot 6, then browns; the hook and the end show baked bread
golden, pale, dark = (.85, .5, .18), (.95, .8, .55), (.55, .28, .1)
b3d.key_input(dough, 'Base Color', [(s1, golden), (s4 - 1, golden), (s4, pale), (s6 + 5, pale), (e6 - 5, golden)])
b3d.key_input(crust, 'Base Color', [(s1, dark), (s4 - 1, dark), (s4, (.86, .74, .55)), (s6 + 5, (.86, .74, .55)), (e6 - 5, dark)])

# the throw: from above the mouth down onto the back wall, squash on impact
hit = s4 + int((e4 - s4) * .55); start = Vector((0, -.2, 1.9))
thrown.location = start; thrown.keyframe_insert('location', frame=s4 + 4)
thrown.location = target; thrown.keyframe_insert('location', frame=hit)
for f, sx, sz in ((hit - 1, 1, 1), (hit + 2, 1.15, .55), (hit + 7, 1, 1)):
    thrown.scale = (sx, sx, sz); thrown.keyframe_insert('scale', frame=f)

b3d.render(OUT, cfg.get('frames'))
