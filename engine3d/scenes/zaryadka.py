"""Zaryadka: charger plugged into a wall socket, cable to a phone on a nightstand.
Big yellow beads (220 V) come down the wall into the charger, small blue beads (5 V) go out to the phone;
see-through shell shows transformer + board; charger glows warm and heat rises; battery bar fills and the
beads stop; a pillow drops on the phone and it glows red; pull back. 7 shots."""
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

wood_m = b3d.mat('Wood', (.42, .26, .14), .55)
wall_m = b3d.mat('Wall', (.38, .42, .55), .85, bump=.02)
sock_m = b3d.mat('Socket', (.92, .92, .9), .35)
shell_m = b3d.mat('Shell', (.95, .95, .95), .3, emit=(1, .35, .05), estr=0)
chan_m = blend(b3d.mat('Channel', (.9, .9, .95), .2), .25)
core_m = b3d.mat('Ferrite', (.15, .15, .17), .5)
coil_m = b3d.mat('Coil', (.85, .45, .2), .3, metal=.8, emit=(1, .25, .03), estr=0)
pcb_m = b3d.mat('Pcb', (.05, .35, .15), .5)
chip_m = b3d.mat('Chip', (.05, .05, .06), .4)
cap_m = b3d.mat('Cap', (.15, .3, .7), .35)
cable_m = b3d.mat('Cable', (.92, .92, .92), .4)
phone_m = b3d.mat('Phone', (.08, .08, .1), .3, metal=.3)
screen_m = b3d.mat('Screen', (.02, .02, .03), .1, emit=(.05, .08, .15), estr=1.5)
bat_m = b3d.mat('Bat', (.1, .8, .2), .3, emit=(.1, .8, .2), estr=1.1)
frame_m = b3d.mat('BatFrame', (.8, .8, .85), .3, emit=(.8, .8, .9), estr=1.2)
yel_m = b3d.mat('Yel', (1, .85, .2), .3, emit=(1, .8, .15), estr=5)
blu_m = b3d.mat('Blu', (.3, .7, 1), .3, emit=(.25, .65, 1), estr=5)
heat_m = blend(b3d.mat('Heat', (1, .45, .1), .9, emit=(1, .4, .08), estr=1.5), .35)
pil_m = b3d.mat('Pillow', (.4, .45, .58), .95)

def keys(ob, attr, fv):
    for f, v in fv: setattr(ob, attr, v); ob.keyframe_insert(attr, frame=f)

def box(name, m, loc, dims, bev=0):
    ob = b3d.prim('cube', [m], size=1, location=loc); ob.scale = dims; ob.name = name
    if bev: ob.modifiers.new('bev', 'BEVEL').width = bev; ob.modifiers['bev'].segments = 3
    return ob

def tube(name, pts, r, m):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 4
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for p, c in zip(sp.points, pts): p.co = (*c, 1)
    ob = b3d.link(bpy.data.objects.new(name, cu)); ob.data.materials.append(m); return ob

def stream(pts, n, r, m, f0, f1, stop=None, step=.035):
    pts = [Vector(p) for p in pts]
    seg = [(pts[k + 1] - pts[k]).length for k in range(len(pts) - 1)]; tot = sum(seg)
    def at(d):
        d %= tot
        for k, s in enumerate(seg):
            if d <= s: return pts[k].lerp(pts[k + 1], d / s)
            d -= s
        return pts[-1]
    for k in range(n):
        bd = b3d.prim('uv_sphere', [m], radius=r, segments=10, ring_count=6, location=(0, 0, 0))
        d = k * tot / n
        for f in range(f0, f1, 2):
            d += step; bd.location = at(d); bd.keyframe_insert('location', frame=f)
        b3d.visible(bd, [(f0, stop or f1)])

# ---------- room: nightstand top + wall ----------
b3d.prim('plane', [wood_m], size=8, location=(0, 0, 0))
b3d.prim('plane', [wall_m], size=8, location=(0, 1.2, 2), rotation=(math.radians(90), 0, 0))

# ---------- socket + charger ----------
CX, CZ = -.8, .38
box('Socket', sock_m, (CX, 1.18, CZ), (.34, .05, .34), .02)
CY = 1.155 - .13
shell = box('Charger', shell_m, (CX, CY, CZ), (.28, .26, .3), .03)
# internals (seen through the shell in shots 3-4)
inner = []
inner.append(box('Pcb', pcb_m, (CX, CY, CZ - .12), (.24, .2, .015)))
inner.append(box('Core', core_m, (CX - .04, CY, CZ - .03), (.06, .12, .14)))
for dx in (-.075, -.005):
    c = b3d.smooth(b3d.prim('cylinder', [coil_m], vertices=24, radius=.035, depth=.1, location=(CX + dx, CY, CZ - .03)))
    c.rotation_euler = (math.radians(90), 0, 0); inner.append(c)
for (x, y) in ((.06, -.05), (.07, .05)):
    inner.append(box('Chip', chip_m, (CX + x, CY + y, CZ - .1), (.06, .05, .025)))
cap = b3d.smooth(b3d.prim('cylinder', [cap_m], vertices=24, radius=.03, depth=.09, location=(CX + .08, CY, CZ - .015)))
inner.append(cap)
for ob in inner: b3d.visible(ob, [(s3, e4)])
b3d.key_input(shell_m, 'Alpha', [(0, 1), (s3 - 1, 1), (s3 + 6, .18), (e4 - 6, .18), (e4 + 1, 1)])
try: shell_m.surface_render_method = 'BLENDED'
except Exception: pass

# wall channel (220 V wire comes down to the socket)
chan = [(CX, 1.17, 1.6), (CX, 1.17, CZ + .17)]
tube('WallWire', chan, .03, chan_m)
stream([(CX, 1.17, 1.6), (CX, 1.17, CZ + .02), (CX, CY, CZ)], 14, .022, yel_m, s2, e5, stop=s5 + int((e5 - s5) * .6), step=.05)

# cable: charger bottom -> table -> phone port
PX, PY = .05, -.12
cable = [(CX, CY - .05, CZ - .15), (CX, CY - .12, .05), (CX + .05, .7, .02), (-.45, .5, .02), (PX - .05, .4, .02), (PX, PY + .38, .02)]
tube('Cable', cable, .012, cable_m)
FULL = s5 + int((e5 - s5) * .6)
stream(cable, 22, .011, blu_m, s2, e5, stop=FULL, step=.03)

# ---------- phone ----------
box('Phone', phone_m, (PX, PY, .025), (.34, .74, .04), .025)
box('Screen', screen_m, (PX, PY, .0455), (.3, .68, .002))
box('BatFrame', frame_m, (PX, PY, .047), (.15, .31, .001))
box('BatInner', screen_m, (PX, PY, .048), (.13, .29, .001))
bat = box('BatBar', bat_m, (PX, PY - .14, .0495), (.11, .01, .001))
def bat_at(f, frac):
    h = .27 * frac + .005
    bat.scale = (.11, h, .001); bat.location = (PX, PY - .14 + h / 2, .0495)
    bat.keyframe_insert('scale', frame=f); bat.keyframe_insert('location', frame=f)
bat_at(0, .15); bat_at(s2, .15); bat_at(s5, .6); bat_at(FULL, 1.0)
b3d.key_input(bat_m, 'Emission Strength', [(0, 1.1), (FULL, 1.1), (FULL + 6, 2), (FULL + 12, 1.1)])

# ---------- heat: charger glows, warm blobs rise (shot 4), again in shot 6 at the phone ----------
H4 = s4 + int((e4 - s4) * .5)
b3d.key_input(shell_m, 'Emission Strength', [(0, 0), (s4, 0), (H4, 1.2), (e4, 1.2), (e4 + 10, 0)])
b3d.key_input(coil_m, 'Emission Strength', [(0, 0), (s4, 0), (H4, 2.5), (e4, 2.5), (e4 + 10, 0)])
rnd = random.Random(5)
def heat(x, y, z, f0, f1, n, spread):
    for k in range(n):
        p = b3d.smooth(b3d.prim('uv_sphere', [heat_m], radius=.03, segments=12, ring_count=8, location=(0, 0, 0))); p.visible_shadow = False
        x0 = x + rnd.uniform(-spread, spread); y0 = y + rnd.uniform(-spread * .5, spread * .5)
        t0 = f0 + rnd.randint(0, max(1, f1 - f0 - 30))
        keys(p, 'location', [(t0, (x0, y0, z)), (t0 + 40, (x0 + rnd.uniform(-.06, .06), y0, z + .55))])
        keys(p, 'scale', [(t0, (.5, .5, .5)), (t0 + 40, (2.2, 2.2, 2.2))])
        b3d.visible(p, [(t0, min(t0 + 40, f1 + 15))])
heat(CX, CY - .05, CZ + .16, s4 + 6, e4, 14, .1)

# ---------- pillow drops on the phone (shot 6) ----------
pil = b3d.smooth(b3d.prim('uv_sphere', [pil_m], radius=.42, segments=32, ring_count=16, location=(PX, PY, 1.2)))
pil.scale = (.95, 1.15, .38)
pil.modifiers.new('sub', 'SUBSURF').levels = 1
P6 = s6 + 14
keys(pil, 'location', [(0, (PX + .05, PY, 1.4)), (s6, (PX + .05, PY, 1.4)), (P6, (PX, PY, .17)), (P6 + 4, (PX, PY, .19)), (e7, (PX, PY, .19))])
b3d.visible(pil, [(s6, e7 + 1)])
RL = b3d.light('POINT', 'PhoneHot', (PX + .1, PY - .55, .06), 0, (1, .2, .05), .1)
for f, v in [(0, 0), (P6, 0), (P6 + 20, 25), (e6, 45), (e7, 45)]:
    RL.data.energy = v; RL.data.keyframe_insert('energy', frame=f)
heat(PX + .05, PY - .5, .12, P6 + 10, e6, 10, .25)

b3d.light('AREA', 'Key', (-1.2, -2.2, 2.6), 160, (1, .88, .75), 3, rot=(50, 0, -25))
b3d.light('AREA', 'Fill', (2.0, -1.8, 1.4), 60, (.6, .7, 1), 3, rot=(65, 0, 45))
b3d.light('POINT', 'Lamp', (-.2, -.2, 1.3), 60, (1, .75, .45), .3)

# ---------- camera ----------
cam, tgt = b3d.camera(35)
b3d.shot(cam, tgt, s1, e1, (.1, -2.4, 1.5), (0, -2.2, 1.4), (-.25, .35, .3), lens=35)
b3d.shot(cam, tgt, s2, e2, (-.15, -.55, .75), (-.25, -.45, .72), (-.7, 1.1, .55), lens=35)
b3d.shot(cam, tgt, s3, e3, (-.55, .35, .45), (-.62, .42, .43), (CX, CY, CZ - .04), lens=40)
b3d.shot(cam, tgt, s4, e4, (-1.15, .4, .6), (-1.08, .45, .58), (CX, CY, CZ + .05), lens=38)
b3d.shot(cam, tgt, s5, e5, (PX, -.95, .85), (PX, -.85, .75), (PX, PY + .02, 0), lens=38)
b3d.shot(cam, tgt, s6, e6, (1.25, -1.35, .85), (1.15, -1.25, .75), (PX, PY - .1, .12), lens=35)
b3d.shot(cam, tgt, s7, e7, (.2, -2.0, 1.3), (.2, -3.4, 2.1), (-.35, .3, .25), lens=35)

b3d.render(OUT, cfg.get('frames'))
