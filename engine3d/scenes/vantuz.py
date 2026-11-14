"""Vantuz (plunger): the sifon set again - basin cut in half, drain pipe cut lengthwise - but the horizontal pipe is
blocked by a clog and the pipe and basin are full of standing water. A plunger seals the drain; each push/pull moves
the (incompressible) water column, the pulses shake the clog loose and it washes away into the stack. 7 shots."""
import math, os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy, bmesh
from mathutils import Vector

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.03, .035, .07), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))
R = math.radians; rnd = random.Random(4)

wall_m = b3d.mat('Wall', (.6, .66, .55), .5, bump=.05)
floor_m = b3d.mat('Floor', (.42, .36, .32), .7, bump=.1)
ceram = b3d.mat('Ceramic', (.95, .95, .96), .2)
chrome = b3d.mat('Chrome', (.85, .87, .9), .12, metal=1.0)
pipe_m = b3d.mat('Pipe', (.88, .88, .86), .4)
pipe_in = b3d.mat('PipeIn', (.55, .55, .54), .6)
stack_m = b3d.mat('Stack', (.45, .47, .5), .5, metal=.3)
water_m = b3d.mat('Water', (.15, .5, .95), .1, emit=(.1, .45, 1), estr=.8)
drop_m = b3d.mat('Drop', (.3, .65, 1), .1, emit=(.25, .6, 1), estr=2)
pulse_m = b3d.mat('Pulse', (.9, .97, 1), .2, emit=(.8, .95, 1), estr=3.5)
clog_m = b3d.mat('Clog', (.32, .2, .1), .9, bump=.6)
rubber = b3d.mat('Rubber', (.75, .16, .1), .5)
wood = b3d.mat('Wood', (.75, .55, .3), .6, bump=.1)
arrow_m = b3d.mat('Arrow', (1, .85, .1), .3, emit=(1, .8, .1), estr=4)

def box(m, c, s):
    b = b3d.prim('cube', [m], size=1, location=c); b.scale = s; return b
def ball(m, r, loc=(0, 0, 0)): return b3d.smooth(b3d.prim('uv_sphere', [m], segments=12, ring_count=6, radius=r, location=loc))
def keys(ob, attr, fv):
    for f, v in fv: setattr(ob, attr, v); ob.keyframe_insert(attr, frame=f)
def lerp(a, b, u): return tuple(x + (y - x) * u for x, y in zip(a, b))
def fr(a, b, u): return int(a + (b - a) * u)

def arc(cx, cz, r, a0, a1, n):
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / n), cz + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]
def line(a, b, n): return [lerp(a, b, i / n) for i in range(n + 1)]
U = line((0, 2.02), (0, 1.0), 12)[:-1] + arc(.3, 1.0, .3, math.pi, 2 * math.pi, 24)[:-1] + line((.6, 1.0), (.6, 1.5), 6)
PATH = U[:-1] + arc(.8, 1.5, .2, math.pi, math.pi / 2, 10)[:-1] + line((.8, 1.7), (2.42, 1.7), 16)
RP, RW, CLOG = .13, .108, 1.42

def sweep(name, pts, r, m, half=False, caps=False, seg=24):
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

def half_lathe(name, prof, m, steps=40):          # back half (y >= 0) of a spun profile: a cutaway
    bm = bmesh.new(); vs = [bm.verts.new((r, 0, z)) for r, z in prof]
    es = [bm.edges.new((vs[i], vs[i + 1])) for i in range(len(vs) - 1)]
    bmesh.ops.spin(bm, geom=vs + es, cent=(0, 0, 0), axis=(0, 0, 1), angle=math.pi, steps=steps, use_merge=False)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(m)
    return b3d.smooth(b3d.link(bpy.data.objects.new(name, me)))

# ---------- timing ----------
B = fr(s5, e5, .35)                 # the clog breaks
def active(f): return s3 + 8 <= f < e4 or s5 <= f < B or s6 <= f < e6
def pump(f):                        # 0 = cup relaxed, 1 = pushed down
    if not active(f): return 0.
    ph = (f - s3) % 14
    return ph / 5 if ph < 5 else 1 - (ph - 5) / 9
FULL = [(0, B + 12), (s6, e6)]      # standing water behind the clog
CLEAR = [(B + 12, s6), (s7, N)]

# ---------- room, pipe, basin ----------
box(wall_m, (1, .75, 2), (8, .2, 6))
for z in (.6, 1.2, 1.8, 2.4, 3.0, 3.6): box(wall_m, (1, .64, z), (8, .02, .02))
box(floor_m, (1, -1, -.05), (8, 4, .1))
b3d.smooth(b3d.prim('cylinder', [stack_m], vertices=40, radius=.24, depth=4.2, location=(2.62, .25, 2.0)))
b3d.smooth(b3d.prim('cylinder', [stack_m], vertices=40, radius=.28, depth=.3, location=(2.62, .25, 1.7)))
pipe = sweep('Pipe', PATH, RP, pipe_m, half=True)
so = pipe.modifiers.new('Sol', 'SOLIDIFY'); so.thickness = .025; so.offset = 1; so.material_offset = 1
pipe.data.materials.append(pipe_in)
prof = [(.07, 2.02), (.07, 2.08), (.3, 2.1), (.52, 2.2), (.66, 2.36), (.72, 2.5), (.8, 2.52), (.82, 2.47), (.74, 2.3), (.58, 2.1), (.35, 2.0), (.13, 1.98), (.07, 2.02)]
half_lathe('Basin', prof, ceram)
tap = b3d.smooth(b3d.prim('cylinder', [chrome], vertices=24, radius=.06, depth=.45, location=(.45, .5, 2.7)))
b3d.smooth(b3d.prim('cylinder', [chrome], vertices=24, radius=.045, depth=.4, location=(.45, .32, 2.9), rotation=(R(90), 0, 0)))
b3d.smooth(b3d.prim('torus', [chrome], major_radius=.15, minor_radius=.03, location=(.6, 0, 1.25)))

bw = half_lathe('BasinWater', [(0, 2.085), (.065, 2.085), (.29, 2.105), (.5, 2.2), (.585, 2.3), (0, 2.3)], water_m)
b3d.visible(bw, FULL)
wfull = sweep('WFull', [p for p in PATH if p[0] <= CLOG - .1], RW, water_m, caps=True); b3d.visible(wfull, FULL)
wplug = sweep('WPlug', [p for p in U if p[1] <= 1.49], RW, water_m, caps=True); b3d.visible(wplug, CLEAR)

# ---------- plunger ----------
pl = b3d.empty('Plunger', (0, 0, 2.09))
cup = b3d.lathe('Cup', [(.0, .2), (.05, .2), (.13, .16), (.19, .07), (.21, 0), (.19, 0), (.17, .06), (.11, .13), (.04, .16), (0, .16)], 40)
cup.data.materials.append(rubber); cup.parent = pl
handle = b3d.smooth(b3d.prim('cylinder', [wood], vertices=20, radius=.028, depth=1.0, location=(0, 0, .7))); handle.parent = pl
keys(pl, 'location', [(s1, (0, 0, 3.2)), (fr(s1, e1, .8), (0, 0, 2.09))])
for f in range(s3, e6):
    u = pump(f)
    cup.scale = (1 + .12 * u, 1 + .12 * u, 1 - .5 * u); cup.keyframe_insert('scale', frame=f)
    handle.location = (0, 0, .2 * (1 - .5 * u) + .5); handle.keyframe_insert('location', frame=f)
b3d.visible(pl, [(0, s7)])
b3d.key_input(water_m, 'Emission Strength', [(f, .8 + 1.3 * pump(f)) for f in range(s3, e6, 2)] + [(e6, .8)])

# ---------- pressure pulses: bright beads in the water column move with every stroke ----------
COL = [(0, -.1, 2.05)] + [(x, -.1, z) for x, z in PATH if x <= CLOG - .12]
cseg = [math.dist(COL[i], COL[i + 1]) for i in range(len(COL) - 1)]; CT = sum(cseg)
def along(path, segl, tot, u):
    d = max(0., min(1., u)) * tot
    for i, L in enumerate(segl):
        if d <= L: return lerp(path[i], path[i + 1], d / L)
        d -= L
    return path[-1]
for k in range(11):
    b = ball(pulse_m, .032)
    for f in range(s3, e6):
        b.location = along(COL, cseg, CT, (k + .5) / 11.5 + .045 * (pump(f) - .3)); b.keyframe_insert('location', frame=f)
    b3d.visible(b, [(s3 + 8, e4), (s5, B), (s6, e6)])

# ---------- the clog ----------
OUTP = [(x, 0, 1.7) for x in (CLOG, 1.9, 2.42)] + [(2.6, .1, 1.5), (2.62, .2, .9)]
oseg = [math.dist(OUTP[i], OUTP[i + 1]) for i in range(len(OUTP) - 1)]; OT = sum(oseg)
for k in range(12):
    r = rnd.uniform(.05, .085); c = ball(clog_m, r)
    base = (CLOG + rnd.uniform(-.1, .14), rnd.uniform(-.06, .03), 1.7 + rnd.uniform(-.06, .06))
    c.scale = (1, 1, rnd.uniform(.7, 1.1)); lag = rnd.randint(0, 22)
    for f in range(0, B + 70):
        if f < B:
            loose = 0 if f < s4 else min(1., (f - s4) / max(1, e4 - s4))
            p = (base[0] + .045 * (pump(f) - .3) + loose * .02 * math.sin(f * .9 + k), base[1], base[2] + loose * .015 * math.cos(f * .7 + k * 2))
        else:
            u = max(0., (f - B - lag) / 42.); q = along(OUTP, oseg, OT, u)
            p = (q[0] + (base[0] - CLOG) * (1 - min(1, u)), q[1] + base[1], q[2] + (base[2] - 1.7))
        if f < s3 and f % 10: continue
        c.location = p; c.keyframe_insert('location', frame=f)
    b3d.visible(c, [(0, B + lag + 44)])

# ---------- water rushing out once the pipe is clear ----------
FLOW = [(0, .02, 2.1)] + [(x, .02, z) for x, z in PATH] + [(2.6, .02, 1.6)]
fseg = [math.dist(FLOW[i], FLOW[i + 1]) for i in range(len(FLOW) - 1)]; FT = sum(fseg)
for k in range(24):
    d = ball(drop_m, .05)
    for f in range(B, e5, 2):
        d.location = along(FLOW, fseg, FT, ((f - B) / 44 + k / 24) % 1); d.keyframe_insert('location', frame=f)
    b3d.visible(d, [(B + 12 + k, e5)])

# ---------- arrows: force goes straight down the water (shot 6) ----------
for a, b in (((-.32, -.25, 2.0), (-.32, -.25, 1.35)), ((.02, -.25, .55), (.55, -.25, .55))):
    ar = b3d.arrow('Arr', a, b, arrow_m, .028); b3d.visible(ar, [(fr(s6, e6, .25), e6)])

# ---------- lights ----------
b3d.light('AREA', 'Key', (3, -4, 4), 380, (1, .95, .88), 6, rot=(50, 0, 30))
b3d.light('AREA', 'Fill', (-3, -4, 2), 180, (.62, .74, 1), 5, rot=(70, 0, -40))
b3d.light('POINT', 'Inner', (.9, -.6, 1.5), 40, (1, .95, .9), .3)

# ---------- timeline ----------
cam, tgt = b3d.camera(30)
b3d.shot(cam, tgt, s1, e1, (1.3, -5.0, 2.5), (1.1, -4.5, 2.4), (.9, 0, 1.9))
b3d.shot(cam, tgt, s2, e2, (1.25, -2.5, 1.85), (1.15, -2.1, 1.8), (1.05, 0, 1.65))
b3d.shot(cam, tgt, s3, e3, (.75, -3.5, 2.05), (.7, -3.2, 2.0), (.65, 0, 1.75))
b3d.shot(cam, tgt, s4, e4, (1.2, -2.0, 1.85), (1.3, -1.7, 1.8), (1.3, 0, 1.68))
b3d.shot(cam, tgt, s5, e5, (1.7, -2.9, 1.95), (1.6, -2.6, 1.9), (1.55, 0, 1.6))
b3d.shot(cam, tgt, s6, e6, (.25, -3.1, 2.0), (.2, -2.8, 1.95), (.15, 0, 1.6))
b3d.shot(cam, tgt, s7, e7, (1.1, -4.6, 2.3), (1.3, -6.4, 2.8), (.9, 0, 1.7))
b3d.render(OUT, cfg.get('frames'))
