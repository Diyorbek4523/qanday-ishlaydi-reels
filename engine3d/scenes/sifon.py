"""Sifon (P/U-trap): a wash basin on a tiled wall, the drain pipe below cut in half lengthwise so we see inside. Water
runs down through the U bend; the last of it stays in the bend as a plug. Green sewer gas comes out of the big stack
pipe, travels back along the pipe and stops at the water. Later the water evaporates (level drops), the gas gets
through and puffs out of the sink. 7 shots."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy, bmesh
from mathutils import Vector

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.03, .035, .07), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))
R = math.radians

# ---------- materials ----------
wall_m = b3d.mat('Wall', (.55, .68, .72), .5, bump=.05)
floor_m = b3d.mat('Floor', (.42, .36, .32), .7, bump=.1)
ceram = b3d.mat('Ceramic', (.95, .95, .96), .2)
chrome = b3d.mat('Chrome', (.85, .87, .9), .12, metal=1.0)
pipe_m = b3d.mat('Pipe', (.88, .88, .86), .4)
pipe_in = b3d.mat('PipeIn', (.55, .55, .54), .6)
stack_m = b3d.mat('Stack', (.45, .47, .5), .5, metal=.3)
water_m = b3d.mat('Water', (.15, .5, .95), .1, emit=(.1, .45, 1), estr=.8)
drop_m = b3d.mat('Drop', (.3, .65, 1), .1, emit=(.25, .6, 1), estr=2)
gas_m = b3d.mat('Gas', (.2, .85, .2), .5, emit=(.15, .9, .15), estr=2.0)
vap_m = b3d.mat('Vapor', (.9, .95, 1), .5, emit=(.9, .95, 1), estr=1.2)
stop_m = b3d.mat('Stop', (1, .2, .12), .3, emit=(1, .15, .08), estr=4)

def box(m, c, s, bevel=0):
    b = b3d.prim('cube', [m], size=1, location=c); b.scale = s
    if bevel:
        bv = b.modifiers.new('Bv', 'BEVEL'); bv.width = bevel; bv.segments = 4; b3d.smooth(b)
    return b
def ball(m, r, loc=(0, 0, 0)): return b3d.smooth(b3d.prim('uv_sphere', [m], segments=12, ring_count=6, radius=r, location=loc))
def keys(ob, attr, fv):
    for f, v in fv: setattr(ob, attr, v); ob.keyframe_insert(attr, frame=f)
def lerp(a, b, u): return tuple(x + (y - x) * u for x, y in zip(a, b))

# ---------- pipe path (x, z) in the y = 0 plane ----------
def arc(cx, cz, r, a0, a1, n):
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / n), cz + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]
def line(a, b, n): return [lerp(a, b, i / n) for i in range(n + 1)]
U = line((0, 2.02), (0, 1.0), 12)[:-1] + arc(.3, 1.0, .3, math.pi, 2 * math.pi, 24)[:-1] + line((.6, 1.0), (.6, 1.5), 6)
PATH = U[:-1] + arc(.8, 1.5, .2, math.pi, math.pi / 2, 10)[:-1] + line((.8, 1.7), (2.42, 1.7), 16)
RP, RW = .13, .108          # pipe outer radius, water radius
WEIR = 1.7 - .11

def sweep(name, pts, r, m, half=False, caps=False, seg=24):
    """Tube along (x, z) points; half=True keeps only the back half (y >= 0) - a cutaway."""
    bm = bmesh.new(); rings = []
    P = [Vector((x, 0, z)) for x, z in pts]
    for i, p in enumerate(P):
        t = (P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)]).normalized()
        nrm = Vector((t.z, 0, -t.x)); Y = Vector((0, 1, 0))
        ang = [math.pi * k / seg for k in range(seg + 1)] if half else [2 * math.pi * k / seg for k in range(seg)]
        rings.append([bm.verts.new(p + r * (math.cos(a) * nrm + math.sin(a) * Y)) for a in ang])
    for a, b in zip(rings[:-1], rings[1:]):
        n = len(a)
        for k in range(n if not half else n - 1):
            bm.faces.new((a[k], a[(k + 1) % n], b[(k + 1) % n], b[k]))
    if caps and not half:
        bm.faces.new(rings[0]); bm.faces.new(list(reversed(rings[-1])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = b3d.smooth(b3d.link(bpy.data.objects.new(name, me))); me.materials.append(m)
    return ob

pipe = sweep('Pipe', PATH, RP, pipe_m, half=True)
so = pipe.modifiers.new('Sol', 'SOLIDIFY'); so.thickness = .025; so.offset = 1; so.material_offset = 1
pipe.data.materials.append(pipe_in)
# cut-face rims so the half-pipe reads as a pipe wall
def water(level, name):
    pts = [p for p in U if p[1] <= level]
    return sweep(name, pts, RW, water_m, caps=True)
LEVELS = [1.49, 1.28, 1.08, .9]
wobs = [water(l, f'Water{i}') for i, l in enumerate(LEVELS)]

# ---------- timing ----------
F0 = s3 + 4                                  # tap opens
F1 = s4 + int((e4 - s4) * .45)               # tap closed, flow ends
G0 = s5                                      # gas crawls back
EV = [s6, s6 + int((e6 - s6) * .22), s6 + int((e6 - s6) * .4), s6 + int((e6 - s6) * .55)]   # evaporation steps
LEAK = EV[-1] + 4                            # gas gets through
for i, w in enumerate(wobs):
    a = EV[i] if i else 0
    b = EV[i + 1] if i + 1 < len(EV) else s7
    b3d.visible(w, [(a, b)] if i else [(0, EV[1]), (s7, N)])

# ---------- room ----------
box(wall_m, (1, .75, 2), (8, .2, 6))
for z in (.6, 1.2, 1.8, 2.4, 3.0, 3.6):
    box(wall_m, (1, .64, z), (8, .02, .02))
box(floor_m, (1, -1, -.05), (8, 4, .1))
stack = b3d.smooth(b3d.prim('cylinder', [stack_m], vertices=40, radius=.24, depth=4.2, location=(2.62, .25, 2.0)))
b3d.smooth(b3d.prim('cylinder', [stack_m], vertices=40, radius=.28, depth=.3, location=(2.62, .25, 1.7)))
# basin (lathe) + tap
prof = [(.07, 2.02), (.07, 2.08), (.3, 2.1), (.52, 2.2), (.66, 2.36), (.72, 2.5), (.8, 2.52), (.82, 2.47), (.74, 2.3), (.58, 2.1), (.35, 2.0), (.13, 1.98)]
basin = b3d.lathe('Basin', prof, 64); basin.data.materials.append(ceram)
b3d.smooth(b3d.prim('cylinder', [chrome], vertices=24, radius=.08, depth=.04, location=(0, 0, 2.09)))
tap = b3d.smooth(b3d.prim('cylinder', [chrome], vertices=24, radius=.06, depth=.45, location=(0, .62, 2.7)))
spout = b3d.smooth(b3d.prim('cylinder', [chrome], vertices=24, radius=.045, depth=.5, location=(0, .4, 2.9), rotation=(R(90), 0, 0)))
b3d.smooth(b3d.prim('cylinder', [chrome], vertices=24, radius=.05, depth=.12, location=(0, .17, 2.84)))
nut = b3d.smooth(b3d.prim('torus', [chrome], major_radius=.15, minor_radius=.03, location=(.6, 0, 1.25)))
# stop marker at the water surface (shot 5)
stopbar = box(stop_m, (.6, -.16, 1.6), (.34, .02, .03)); b3d.visible(stopbar, [])

# ---------- running water (shots 3-4) ----------
FLOW = [(0, .17, 2.8), (0, .05, 2.1)] + [(x, .02, z) for x, z in PATH] + [(2.6, .02, 1.7)]
seg = [math.dist(FLOW[i], FLOW[i + 1]) for i in range(len(FLOW) - 1)]; TOT = sum(seg)
def along(path, segl, tot, u):
    d = max(0., min(1., u)) * tot
    for i, L in enumerate(segl):
        if d <= L: return lerp(path[i], path[i + 1], d / L)
        d -= L
    return path[-1]
for k in range(22):
    d = ball(drop_m, .05)
    for f in range(F0 - 40, F1 + 41, 2):
        u = ((f - F0) / 40 + k / 22) % 1 if f < F1 else ((F1 - F0) / 40 + k / 22) % 1 + (f - F1) / 40
        d.location = along(FLOW, seg, TOT, u); d.keyframe_insert('location', frame=f)
    vis_end = F1 + int((1 - (((F1 - F0) / 40 + k / 22) % 1)) * 40)
    b3d.visible(d, [(F0 + int(k / 22 * 0), min(vis_end, e4))])
stream = sweep('Stream', [(0, 2.8), (0, 2.1)], .035, drop_m, caps=True)
stream.location = (0, .17, 0)
b3d.visible(stream, [(F0, F1)])

# ---------- sewer gas ----------
GAS = [(2.5, .02, 1.7)] + [(x, .02, z) for x, z in reversed(PATH)]
gseg = [math.dist(GAS[i], GAS[i + 1]) for i in range(len(GAS) - 1)]; GT = sum(gseg)
stop_u = 0
acc = 0
for i, L in enumerate(gseg):            # gas stops where the pipe reaches the water surface
    if GAS[i + 1][2] < WEIR + .05 and GAS[i + 1][0] < .7: stop_u = (acc + L * .2) / GT; break
    acc += L
full_u = 1.0
for k in range(10):
    g = ball(gas_m, .06 + .015 * (k % 3))
    lag = k * 5
    kf = [(0, 0.)]
    for f in range(s1, N, 3):
        if f < G0 + lag: u = 0
        elif f < LEAK: u = min(stop_u - .01 * (k % 4), (f - G0 - lag) / 70 * stop_u * 1.6)
        else: u = min(full_u, stop_u + (f - LEAK - lag * .5) / 50)
        p = along(GAS, gseg, GT, u)
        if u <= 0: p = (2.62 + .08 * math.sin(f * .2 + k), .25 + .1 * math.cos(f * .17 + k), 1.2 + ((f * .01 + k * .23) % 1) * 1.4)
        if f >= LEAK and u >= full_u - .001:
            t = (f - LEAK) / 30.; p = (.15 * math.sin(k * 2.1) * (1 + t), .1, 2.1 + .6 * min(t, 2))
        g.location = p; g.keyframe_insert('location', frame=f)
    b3d.visible(g, [(G0, s7)])
# gas inside the (open-topped) stack in shot 1, then everywhere from shot 5
puff = []
for k in range(6):
    p = ball(gas_m, .1, (0, 0, 2.3)); puff.append(p)
    keys(p, 'location', [(LEAK + 12, (0, .05, 2.15)), (LEAK + 50, (.4 * math.sin(k), -.2 * math.cos(k), 2.7 + .1 * k))])
    keys(p, 'scale', [(LEAK + 12, (.4, .4, .4)), (LEAK + 50, (1.8, 1.8, 1.8))])
    b3d.visible(p, [(LEAK + 12, s7)])
# vapour leaving the drying plug
for k in range(10):
    v = ball(vap_m, .03)
    x = 0 if k % 2 else .6
    a = EV[0] + k * 4
    keys(v, 'location', [(a, (x, .02, 1.45)), (a + 30, (x, .02, 2.0 if x == 0 else 1.7))])
    b3d.visible(v, [(a, a + 30)])

# ---------- lights ----------
b3d.light('AREA', 'Key', (3, -4, 4), 380, (1, .95, .88), 6, rot=(50, 0, 30))
b3d.light('AREA', 'Fill', (-3, -4, 2), 180, (.62, .74, 1), 5, rot=(70, 0, -40))
b3d.light('POINT', 'Inner', (.4, -.6, 1.3), 40, (1, .95, .9), .3)

# ---------- timeline ----------
cam, tgt = b3d.camera(30)
b3d.shot(cam, tgt, s1, e1, (1.4, -5.2, 2.4), (1.2, -4.7, 2.3), (1.0, 0, 1.6))
b3d.shot(cam, tgt, s2, e2, (.6, -2.1, 1.35), (.5, -1.8, 1.3), (.3, 0, 1.15))
b3d.shot(cam, tgt, s3, e3, (.5, -3.1, 2.0), (.4, -2.8, 1.95), (.3, 0, 1.65))
b3d.shot(cam, tgt, s4, e4, (.35, -2.0, 1.15), (.3, -1.8, 1.12), (.3, 0, 1.15))
b3d.shot(cam, tgt, s5, e5, (1.4, -2.4, 1.95), (1.25, -2.15, 1.9), (1.0, 0, 1.55))
b3d.shot(cam, tgt, s6, e6, (.5, -3.0, 1.9), (.45, -2.7, 1.9), (.3, 0, 1.7))
b3d.shot(cam, tgt, s7, e7, (1.2, -4.8, 2.3), (1.4, -6.6, 2.8), (1.0, 0, 1.6))
b3d.render(OUT, cfg.get('frames'))
