"""Uzaytirgich: power strip on the floor, kettle plugged in; heater plugged in too -> twice the current beads in the cord;
see-through cord: copper core glows red; the coiled part glows hottest and smokes; heater unplugged, glow fades; pull back. 7 shots."""
import math, os, sys, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy
from mathutils import Vector

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.02, .02, .045), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))

floor_m = b3d.mat('Floor', (.42, .28, .17), .6)
wall_m = b3d.mat('Wall', (.45, .42, .5), .85, bump=.02)
strip_m = b3d.mat('Strip', (.9, .9, .88), .35)
hole_m = b3d.mat('Hole', (.03, .03, .03), .6)
plug_m = b3d.mat('Plug', (.1, .1, .12), .4)
kettle_m = b3d.mat('Kettle', (.15, .45, .75), .25)
heat_m = b3d.mat('Heater', (.85, .85, .82), .3, metal=.3)
red_led = b3d.mat('Led', (1, .2, .1), .3, emit=(1, .15, .05), estr=4)
ins_m = b3d.mat('Insul', (.92, .92, .95), .2)
ib = b3d.bsdf(ins_m); ib.inputs['Alpha'].default_value = .28
try: ins_m.surface_render_method = 'BLENDED'
except Exception: pass
cu_m = b3d.mat('Copper', (.85, .45, .22), .3, metal=.8, emit=(1, .18, .03), estr=0)
coil_cu = b3d.mat('CoilCopper', (.85, .45, .22), .3, metal=.8, emit=(1, .15, .02), estr=0)
bead_m = b3d.mat('Bead', (1, .85, .2), .3, emit=(1, .8, .15), estr=5)
smoke_m = b3d.mat('Smoke', (.35, .35, .38), .9)
smb = b3d.bsdf(smoke_m); smb.inputs['Alpha'].default_value = .45
try: smoke_m.surface_render_method = 'BLENDED'
except Exception: pass

def keys(ob, attr, fv):
    for f, v in fv: setattr(ob, attr, v); ob.keyframe_insert(attr, frame=f)

def box(name, m, loc, dims, bev=0):
    ob = b3d.prim('cube', [m], size=1, location=loc); ob.scale = dims; ob.name = name
    if bev: ob.modifiers.new('bev', 'BEVEL').width = bev
    return ob

def tube(name, pts, r, m):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 4
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for p, c in zip(sp.points, pts): p.co = (*c, 1)
    ob = b3d.link(bpy.data.objects.new(name, cu)); ob.data.materials.append(m); return ob

# ---------- room ----------
b3d.prim('plane', [floor_m], size=14, location=(0, 0, 0))
b3d.prim('plane', [wall_m], size=14, location=(0, 3.0, 3), rotation=(math.radians(90), 0, 0))
box('WallSocket', strip_m, (-1.5, 2.97, .4), (.22, .06, .22), .02)

# ---------- power strip ----------
box('Strip', strip_m, (0, 0, .05), (1.0, .26, .1), .02)
SX = (-.28, 0, .28)
for x in SX: b3d.prim('cylinder', [hole_m], vertices=24, radius=.07, depth=.01, location=(x, 0, .101))
b3d.smooth(b3d.prim('uv_sphere', [red_led], radius=.02, location=(.44, -.08, .1)))

# kettle (socket 0) and oil heater (socket 2)
kettle = b3d.lathe('Kettle', [(0, 0), (.22, 0), (.24, .05), (.24, .32), (.19, .42), (.1, .46), (0, .47)])
kettle.data.materials.append(kettle_m); kettle.location = (-.95, -.3, 0)
heater = b3d.empty('HeaterRoot', (.75, -.55, 0))
for k in range(7):
    f_ = box(f'Fin{k}', heat_m, (0, 0, 0), (.07, .34, .62), .02); f_.parent = heater; f_.location = (-.27 + k * .09, 0, .36)
for z in (.08, .64):
    b = box(f'Bar{z}', heat_m, (0, 0, 0), (.62, .08, .05)); b.parent = heater; b.location = (0, 0, z)
box('Plug0', plug_m, (SX[0], 0, .16), (.13, .1, .12), .02)
hroot = b3d.empty('HPlug', (SX[2], 0, .16))
hp = box('Plug2', plug_m, (0, 0, 0), (.13, .1, .12), .02); hp.parent = hroot; hp.location = (0, 0, 0)
plugs = [None, hroot]
tube('KettleCord', [(SX[0], 0, .16), (SX[0] - .05, -.15, .05), (-.6, -.25, .02), (-.75, -.3, .05)], .018, plug_m)
hcord = tube('HeaterCord', [(0, 0, 0), (.08, -.12, -.11), (.3, -.35, -.14), (.4, -.5, -.11)], .018, plug_m)
hcord.parent = plugs[1]
# heater plug drops in at the start of shot 3, pulled out early in shot 6
P_IN = s3 + 12; P_OUT = s6 + int((e6 - s6) * .25)
keys(plugs[1], 'location', [(0, (SX[2], 0, .6)), (s3, (SX[2], 0, .6)), (P_IN, (SX[2], 0, .16)), (P_OUT, (SX[2], 0, .16)), (P_OUT + 10, (SX[2], 0, .6))])
b3d.visible(plugs[1], [(0, s2), (s3, P_OUT + 10), (s7, e7 + 1)])

# ---------- main cord: strip -> coil (helix) -> wall ----------
path = [(-.5, 0, .05), (-.75, .08, .035), (-1.05, .3, .035)]
CX, CY, CR, TURNS = -1.45, .6, .32, 5
a0 = math.atan2(.3 - CY, -1.05 - CX)
for i in range(TURNS * 24 + 1):
    a = a0 + 2 * math.pi * i / 24
    path.append((CX + CR * math.cos(a), CY + CR * math.sin(a), .035 + .055 * i / 24))
path += [(-1.5, 1.2, .04), (-1.5, 2.6, .035), (-1.5, 2.92, .4)]
NC = 3 + TURNS * 24 + 1  # index where the coil ends
straight = path[:3] + path[NC:]
tube('CordIns', path, .045, ins_m)
tube('CoreA', path[:4], .016, cu_m)
tube('CoreCoil', path[2:NC + 1], .016, coil_cu)
tube('CoreB', path[NC - 1:], .016, cu_m)

H4 = s4 + int((e4 - s4) * .7)
b3d.key_input(cu_m, 'Emission Strength', [(0, 0), (s4, 0), (H4, 2.2), (s6, 2.2), (s6 + int((e6 - s6) * .7), 0)])
b3d.key_input(cu_m, 'Base Color', [(0, (.85, .45, .22)), (s4, (.85, .45, .22)), (H4, (.9, .25, .08)), (s6, (.9, .25, .08)), (s6 + int((e6 - s6) * .7), (.85, .45, .22))])
b3d.key_input(coil_cu, 'Emission Strength', [(0, 0), (s4, 0), (H4, 3), (s5 + int((e5 - s5) * .5), 6), (s6, 6), (s6 + int((e6 - s6) * .7), 0)])
CL = b3d.light('POINT', 'CoilGlow', (CX, CY, .3), 0, (1, .3, .05), .2)
for f, v in [(0, 0), (s4, 0), (H4, 15), (s5 + int((e5 - s5) * .5), 40), (s6, 40), (s6 + int((e6 - s6) * .7), 0)]:
    CL.data.energy = v; CL.data.keyframe_insert('energy', frame=f)

# ---------- current beads: wall -> strip, doubled while the heater is plugged in ----------
pts = [Vector(p) for p in reversed(path)]
seg = [(pts[k + 1] - pts[k]).length for k in range(len(pts) - 1)]; TOT = sum(seg)
def at(d):
    d %= TOT
    for k, s in enumerate(seg):
        if d <= s: return pts[k].lerp(pts[k + 1], d / s)
        d -= s
    return pts[-1]
def speed(f): return 2.0 if P_IN <= f < P_OUT else 1.0
NB = 26
for k in range(2 * NB):
    bd = b3d.prim('uv_sphere', [bead_m], radius=.013, segments=10, ring_count=6, location=(0, 0, 0))
    dist = (k % NB) * TOT / NB + (TOT / NB / 2 if k >= NB else 0)
    for f in range(s2, e6, 2):
        dist += .045 * speed(f)
        bd.location = at(dist); bd.keyframe_insert('location', frame=f)
    b3d.visible(bd, [(s2, e6)] if k < NB else [(P_IN, P_OUT)])

# ---------- smoke over the coil (shot 5) ----------
rnd = random.Random(3)
for k in range(16):
    p = b3d.smooth(b3d.prim('uv_sphere', [smoke_m], radius=.05, segments=12, ring_count=8, location=(0, 0, 0))); p.visible_shadow = False
    a = rnd.uniform(0, 2 * math.pi); x0, y0 = CX + CR * math.cos(a), CY + CR * math.sin(a)
    t0 = s5 + rnd.randint(0, max(1, e5 - s5 - 25))
    keys(p, 'location', [(t0, (x0, y0, .15)), (t0 + 45, (x0 + rnd.uniform(-.15, .15), y0, .95))])
    keys(p, 'scale', [(t0, (.4, .4, .4)), (t0 + 45, (2.4, 2.4, 2.4))])
    b3d.visible(p, [(t0, min(t0 + 45, s6 + 20))])

b3d.light('AREA', 'Key', (-1.5, -2.5, 3.0), 180, (1, .88, .75), 3, rot=(50, 0, -25))
b3d.light('AREA', 'Fill', (2.2, -2.0, 1.5), 70, (.6, .7, 1), 3, rot=(65, 0, 45))

# ---------- camera ----------
cam, tgt = b3d.camera(35)
b3d.shot(cam, tgt, s1, e1, (.1, -3.4, 2.4), (0, -3.0, 2.1), (-.35, .45, .2), lens=35)
b3d.shot(cam, tgt, s2, e2, (-.35, -1.7, 1.0), (-.3, -1.5, .9), (-.3, 0, .15), lens=35)
b3d.shot(cam, tgt, s3, e3, (.5, -1.7, 1.0), (.45, -1.5, .9), (.25, -.1, .15), lens=35)
b3d.shot(cam, tgt, s4, e4, (-.5, -.22, .36), (-.56, -.16, .32), (-.82, .13, .04), lens=45)
b3d.shot(cam, tgt, s5, e5, (-1.15, -.65, 1.15), (-1.25, -.55, 1.05), (CX, CY, .15), lens=38)
b3d.shot(cam, tgt, s6, e6, (-.1, -2.3, 1.35), (-.15, -2.1, 1.25), (-.45, .35, .2), lens=35)
b3d.shot(cam, tgt, s7, e7, (-.3, -2.5, 1.5), (-.3, -4.8, 2.7), (-.4, .6, .2), lens=35)

b3d.render(OUT, cfg.get('frames'))
