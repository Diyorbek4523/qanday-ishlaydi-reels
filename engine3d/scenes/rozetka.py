"""Rozetka: a surface-mounted wall socket with a plug. Scorched socket (hook); cutaway: copper contacts grip the pins,
current beads flow; contacts loosen, only one tip touches; the tip glows hot; contacts darken (oxide) and glow red;
cover back, scorch ring grows with smoke; pull back. 7 shots."""
import math, os, sys, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy
from mathutils import Vector

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.02, .02, .04), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))

wall_m = b3d.mat('Wall', (.38, .3, .24), .85, bump=.02)
floor_m = b3d.mat('Floor', (.35, .22, .14), .7)
plast = b3d.mat('Plastic', (.85, .84, .8), .35)
base_m = b3d.mat('Base', (.7, .7, .68), .45)
hole_m = b3d.mat('Hole', (.03, .03, .03), .6)
plug_m = b3d.mat('Plug', (.12, .12, .14), .4)
pin_m = b3d.mat('Pin', (.75, .75, .78), .25, metal=.9)
cu_m = b3d.mat('Copper', (.85, .45, .22), .3, metal=.85, emit=(1, .25, .05), estr=0)
wire_m = b3d.mat('Wire', (.75, .35, .1), .5)
bead_m = b3d.mat('Bead', (1, .85, .2), .3, emit=(1, .8, .15), estr=5)
hot_m = b3d.mat('Hot', (1, .4, .1), .3, emit=(1, .35, .05), estr=0)
scorch = b3d.mat('Scorch', (.012, .008, .006), .95)
sb = b3d.bsdf(scorch); sb.inputs['Alpha'].default_value = 0
try: scorch.surface_render_method = 'BLENDED'
except Exception: pass
smoke_m = b3d.mat('Smoke', (.35, .35, .38), .9)
smb = b3d.bsdf(smoke_m); smb.inputs['Alpha'].default_value = .5
try: smoke_m.surface_render_method = 'BLENDED'
except Exception: pass

def keys(ob, attr, fv):
    for f, v in fv: setattr(ob, attr, v); ob.keyframe_insert(attr, frame=f)

Z = 1.0
# ---------- room ----------
b3d.prim('plane', [wall_m], size=12, location=(0, 0, 2), rotation=(math.radians(90), 0, 0))
b3d.prim('plane', [floor_m], size=12, location=(0, -6, 0))

# ---------- socket housing (hollow box in front of wall: y -0.3 .. 0) ----------
def box(name, m, loc, dims):
    ob = b3d.prim('cube', [m], size=1, location=loc); ob.scale = dims; ob.name = name; return ob
box('Back', base_m, (0, -.015, Z), (.8, .03, .8))
box('SideL', base_m, (-.385, -.15, Z), (.03, .27, .8))
box('SideR', base_m, (.385, -.15, Z), (.03, .27, .8))
box('Bot', base_m, (0, -.15, Z - .385), (.8, .27, .03))
top = box('Top', base_m, (0, -.15, Z + .385), (.8, .27, .03))
cover = box('Cover', plast, (0, -.29, Z), (.84, .04, .84))
cover.modifiers.new('bev', 'BEVEL').width = .03
PX = (-.1, .1)
holes = [b3d.prim('cylinder', [hole_m], vertices=24, radius=.032, depth=.01, location=(x, -.312, Z), rotation=(math.radians(90), 0, 0)) for x in PX]
sc_disc = b3d.prim('cylinder', [scorch], vertices=48, radius=.34, depth=.004, location=(-.04, -.315, Z + .02), rotation=(math.radians(90), 0, 0))
sc_disc.scale = (1, 1.25, 1); sc_disc.visible_shadow = False
for o in [cover, top, sc_disc] + holes: b3d.visible(o, [(0, s2), (s6, e7 + 1)])
b3d.key_input(scorch, 'Alpha', [(0, .97), (s2 - 1, .97), (s2, 0), (s6, 0), (s6 + int((e6 - s6) * .8), .97), (e7, .97)])

# ---------- plug + pins + cord ----------
plug = b3d.smooth(b3d.prim('cylinder', [plug_m], vertices=48, radius=.22, depth=.26, location=(0, -.44, Z), rotation=(math.radians(90), 0, 0)))
plug.modifiers.new('bev', 'BEVEL').width = .03
for x in PX:
    b3d.smooth(b3d.prim('cylinder', [pin_m], vertices=24, radius=.02, depth=.22, location=(x, -.21, Z), rotation=(math.radians(90), 0, 0)))
cu = bpy.data.curves.new('Cord', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = .045; cu.bevel_resolution = 4
sp = cu.splines.new('BEZIER'); sp.bezier_points.add(2)
for p, c in zip(sp.bezier_points, [(0, -.58, Z), (.05, -.62, .45), (.15, -.4, .02)]):
    p.co = c; p.handle_left_type = p.handle_right_type = 'AUTO'
cord = b3d.link(bpy.data.objects.new('Cord', cu)); cord.data.materials.append(plug_m)
for o in (plug, cord): b3d.visible(o, [(0, s2), (s6, e7 + 1)])

# ---------- copper contacts: outer strip pivots at its front end, inner strip slides away ----------
L = .15; Y0 = -.25  # strips span y -0.25 .. -0.10
strips = []
for i, x in enumerate(PX):
    sgn = -1 if x < 0 else 1  # outward direction
    piv = b3d.empty(f'Piv{i}', (x + sgn * .02, Y0, Z))
    a = box(f'StripA{i}', cu_m, (0, 0, 0), (.02, L, .12)); a.parent = piv; a.location = (sgn * .01, L / 2, 0)
    b = box(f'StripB{i}', cu_m, (x - sgn * .03, Y0 + L / 2, Z), (.02, L, .12))
    strips.append((piv, b, sgn, x))
    # wire out the back
    w = bpy.data.curves.new(f'W{i}', 'CURVE'); w.dimensions = '3D'; w.bevel_depth = .014
    s_ = w.splines.new('POLY'); s_.points.add(2)
    for p, c in zip(s_.points, [(x, -.1, Z), (x, -.06, Z + .1), (x * 2.2, -.06, Z + .36)]): p.co = (*c, 1)
    b3d.link(bpy.data.objects.new(f'W{i}', w)).data.materials.append(wire_m)
LO = s3 + int((e3 - s3) * .25); LO2 = s3 + int((e3 - s3) * .75)
for piv, b, sgn, x in strips:
    keys(piv, 'rotation_euler', [(LO, (0, 0, 0)), (LO2, (0, 0, -sgn * math.radians(9)))])
    keys(b, 'location', [(LO, b.location.copy()), (LO2, b.location + Vector((-sgn * .03, 0, 0)))])
# oxide: copper darkens and glows
b3d.key_input(cu_m, 'Base Color', [(0, (.85, .45, .22)), (s5, (.85, .45, .22)), (s5 + int((e5 - s5) * .7), (.18, .09, .05))])
b3d.key_input(cu_m, 'Emission Strength', [(0, 0), (s5, 0), (e5 - 1, 2.5), (e6, 2.5)])

# hot spots at the touching tips
hots = []
for i, x in enumerate(PX):
    sgn = -1 if x < 0 else 1
    h = b3d.smooth(b3d.prim('uv_sphere', [hot_m], radius=.03, location=(x + sgn * .02, Y0 + .005, Z)))
    hots.append(h); b3d.visible(h, [(s4, e6)])
b3d.key_input(hot_m, 'Emission Strength', [(0, 0), (s4, 0), (s4 + int((e4 - s4) * .5), 5), (e5, 6), (e6, 6)])
HL = b3d.light('POINT', 'HotLight', (-.12, -.3, Z), 0, (1, .4, .1), .05)
for f, v in [(0, 0), (s4, 0), (s4 + int((e4 - s4) * .5), 6), (e5, 10), (s6, 0)]:
    HL.data.energy = v; HL.data.keyframe_insert('energy', frame=f)

# current beads: along each pin into the contact, then out the wire (shots 2-5)
rnd = random.Random(5)
for i, x in enumerate(PX):
    sgn = -1 if x < 0 else 1
    path = [Vector(p) for p in [(x, -.32, Z), (x, -.25, Z), (x + sgn * .02, -.24, Z), (x + sgn * .02, -.1, Z), (x, -.06, Z + .1), (x * 2.2, -.06, Z + .36)]]
    seg = [(path[k + 1] - path[k]).length for k in range(len(path) - 1)]; TOT = sum(seg)
    def at(d):
        d %= TOT
        for k, s in enumerate(seg):
            if d <= s: return path[k].lerp(path[k + 1], d / s)
            d -= s
        return path[-1]
    for k in range(8):
        bd = b3d.prim('uv_sphere', [bead_m], radius=.011, segments=12, ring_count=8, location=(0, 0, 0))
        dist = k * TOT / 8
        for f in range(s2, e5, 2):
            dist += .024 * (2.2 if f >= s5 else 1)
            bd.location = at(dist)
            bd.keyframe_insert('location', frame=f)
        b3d.visible(bd, [(s2, e5)])

# smoke from the cover top (shot 6-7)
for k in range(18):
    p = b3d.smooth(b3d.prim('uv_sphere', [smoke_m], radius=.04, segments=12, ring_count=8, location=(0, 0, 0)))
    x0 = rnd.uniform(-.25, .2); t0 = s6 + rnd.randint(0, max(1, e6 - s6 - 20)); p.visible_shadow = False
    keys(p, 'location', [(t0, (x0, -.33, Z + .1)), (t0 + 40, (x0 + rnd.uniform(-.1, .1), -.4, Z + .75))])
    keys(p, 'scale', [(t0, (.4, .4, .4)), (t0 + 40, (2.2, 2.2, 2.2))])
    b3d.visible(p, [(t0, min(t0 + 40, e7))])

b3d.light('AREA', 'Key', (-1.2, -2.2, 2.2), 45, (1, .85, .7), 1.5, rot=(55, 0, -30))
b3d.light('AREA', 'Fill', (1.6, -2.0, 1.0), 20, (.6, .7, 1), 2.0, rot=(70, 0, 40))
b3d.light('POINT', 'Inner', (0, -.6, Z + .5), 5, (1, .9, .8), .2)

# ---------- camera ----------
cam, tgt = b3d.camera(35)
TIP = (-.12, -.25, Z)
b3d.shot(cam, tgt, s1, e1, (.5, -2.5, 1.25), (.25, -2.0, 1.1), (0, -.3, Z), lens=35)
b3d.shot(cam, tgt, s2, e2, (.3, -.8, 1.4), (.2, -.72, 1.32), (0, -.18, Z), lens=35)
b3d.shot(cam, tgt, s3, e3, (-.02, -.6, 1.32), (-.05, -.55, 1.28), (-.1, -.18, Z), lens=40)
b3d.shot(cam, tgt, s4, e4, (-.32, -.52, 1.18), (-.28, -.48, 1.14), TIP, lens=50)
b3d.shot(cam, tgt, s5, e5, (.3, -.72, 1.38), (.36, -.68, 1.3), (0, -.18, Z), lens=35)
b3d.shot(cam, tgt, s6, e6, (.35, -1.95, 1.15), (.25, -1.7, 1.1), (0, -.3, Z + .1), lens=35)
b3d.shot(cam, tgt, s7, e7, (0, -1.7, 1.1), (0, -3.3, 1.25), (0, -.3, Z + .1), lens=35)

b3d.render(OUT, cfg.get('frames'))
