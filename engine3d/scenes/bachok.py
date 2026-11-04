"""Bachok: toilet cistern cutaway. Button lifts the flap, water drops out, float falls and the lever opens the fill valve, water rises, float closes it.
Water level L(f) drives everything. Front wall and bowl show only in outside views. 7 shots."""
import math, os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.05, .07, .12), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))

# ---------- materials ----------
white = b3d.mat('White', (.82, .84, .87), .22)
inner = b3d.mat('Inner', (.42, .46, .52), .55)
tile = b3d.mat('Tile', (.2, .36, .42), .35, bump=.08)
floor_m = b3d.mat('Floor', (.34, .3, .28), .5, bump=.1)
chrome = b3d.mat('Chrome', (.75, .77, .8), .15, metal=1)
water = b3d.mat('Water', (.2, .55, .95), .1, emit=(.05, .3, .75), estr=.5)
b3d.bsdf(water).inputs['Alpha'].default_value = .5
try: water.surface_render_method = 'BLENDED'
except (AttributeError, TypeError): pass
glass = b3d.mat('PipeGlass', (.75, .85, .95), .15)
b3d.bsdf(glass).inputs['Alpha'].default_value = .28
try: glass.surface_render_method = 'BLENDED'
except (AttributeError, TypeError): pass
drop = b3d.mat('Drop', (.3, .65, 1), .1, emit=(.1, .45, 1), estr=2.2)
float_m = b3d.mat('Float', (1, .45, .08), .35, emit=(1, .35, .03), estr=.35)
rod_m = b3d.mat('Rod', (.8, .82, .86), .25, metal=.9)
brass = b3d.mat('Brass', (.85, .62, .2), .3, metal=.9)
flap_m = b3d.mat('Flap', (.8, .12, .12), .5)
point_m = b3d.mat('Point', (1, .8, .2), .4, emit=(1, .72, .08), estr=2.6)
lamp = b3d.mat('Lamp', (.9, .1, .1), .3, emit=(1, .1, .08), estr=1.1)
LO, HI = 3.65, 5.5        # water surface
FLOORZ = 3.1
def ease(u): u = min(1, max(0, u)); return u * u * (3 - 2 * u)
T_FALL0 = s3 + 14; T_FALL1 = s4 + int((e4 - s4) * .62)
T_OPEN = s4 + int((e4 - s4) * .42); T_RISE0 = T_FALL1; T_CLOSE = s6 + int((e6 - s6) * .6)
def level(f):
    if f < T_FALL0: return HI
    if f < T_FALL1: return HI + (LO - HI) * ease((f - T_FALL0) / (T_FALL1 - T_FALL0))
    if f < T_CLOSE: return LO + (HI - LO) * ((f - T_RISE0) / (T_CLOSE - T_RISE0))
    return HI

def box(m, c, s, bevel=0):
    b = b3d.prim('cube', [m], size=1, location=c); b.scale = s
    if bevel:
        bv = b.modifiers.new('Bv', 'BEVEL'); bv.width = bevel; bv.segments = 4; b3d.smooth(b)
    return b

# ---------- bathroom ----------
box(floor_m, (0, -2, -.25), (30, 30, .5))
b3d.prim('plane', [tile], size=40, location=(0, 1.0, 20), rotation=(math.radians(90), 0, 0))

# ---------- tank: everything but the front ----------
TW, TD, T0, T1 = 4.0, 1.5, 2.95, 6.6; TZ = (T0 + T1) / 2
box(inner, (0, TD / 2 - .04, TZ), (TW, .08, T1 - T0))
for sx in (-1, 1): box(white, (sx * (TW / 2 - .04), 0, TZ), (.08, TD, T1 - T0))
box(white, (0, 0, T0 + .07), (TW, TD, .14))
lid = box(white, (0, 0, T1 + .05), (TW + .1, TD + .1, .12), bevel=.03)
wat = box(water, (0, 0, 0), (TW - .16, TD - .12, 1))
for f in range(0, N, 2):
    L = level(f); wat.scale = (TW - .16, TD - .12, L - FLOORZ); wat.location = (0, 0, FLOORZ + (L - FLOORZ) / 2)
    wat.keyframe_insert('scale', frame=f); wat.keyframe_insert('location', frame=f)

# ---------- flush: button, rod, flap, outlet pipe, overflow ----------
OX = .95
outlet = b3d.lathe('OutletSeat', [(.38, FLOORZ - .02), (.5, FLOORZ - .02), (.5, FLOORZ + .1), (.38, FLOORZ + .1), (.38, FLOORZ - .02)]); outlet.data.materials.append(chrome); outlet.location = (OX, 0, 0)
pipe = b3d.lathe('Pipe', [(.3, 0), (.36, 0), (.36, T0 + .1), (.3, T0 + .1), (.3, 0)]); pipe.data.materials.append(glass); pipe.location = (OX, 0, 0)
overflow = b3d.lathe('Overflow', [(.09, FLOORZ + .05), (.13, FLOORZ + .05), (.13, HI + .45), (.09, HI + .45), (.09, FLOORZ + .05)]); overflow.data.materials.append(rod_m); overflow.location = (OX + .55, -.05, 0)
FL0 = FLOORZ + .16; FLUP = FLOORZ + .92
T_CLOSEFLAP = T_FALL1
flap = b3d.smooth(b3d.prim('cylinder', [flap_m], vertices=48, radius=.45, depth=.1))
rod = box(rod_m, (0, 0, 0), (.05, .05, 1))
btn = b3d.smooth(b3d.prim('cylinder', [chrome], vertices=40, radius=.3, depth=.14))
def flap_z(f):
    if f < s3 + 6: return FL0
    if f < T_CLOSEFLAP - 14: return FL0 + (FLUP - FL0) * ease((f - s3 - 6) / 12)
    return FL0 + (FLUP - FL0) * (1 - ease((f - T_CLOSEFLAP + 14) / 14))
for f in range(0, N, 1):
    z = flap_z(f); flap.location = (OX, 0, z); flap.keyframe_insert('location', frame=f)
    top = T1 + .14; rod.scale = (.05, .05, top - z); rod.location = (OX, 0, (top + z) / 2); rod.keyframe_insert('scale', frame=f); rod.keyframe_insert('location', frame=f)
    bz = T1 + .17 - .1 * min(1, (z - FL0) / (FLUP - FL0) * 1.5); btn.location = (OX, 0, bz); btn.keyframe_insert('location', frame=f)
# water leaving through the pipe
for k in range(26):
    d = b3d.smooth(b3d.prim('uv_sphere', [drop], segments=10, ring_count=6, radius=.075)); rr = random.Random(k); ph = rr.random(); x0 = rr.uniform(-.17, .17); y0 = rr.uniform(-.1, .1)
    for f in range(T_FALL0, T_CLOSEFLAP, 2):
        u = (ph + (f - T_FALL0) / 15) % 1; d.location = (OX + x0, y0, FLOORZ + .2 - u * 2.8); d.keyframe_insert('location', frame=f)
    b3d.visible(d, [(T_FALL0, T_CLOSEFLAP)])

# ---------- fill valve, lever, float ----------
VX, PIVZ = -1.4, 5.88
ARM = 1.45; BALL = .36
inlet = b3d.lathe('Inlet', [(.1, 0), (.15, 0), (.15, 5.6), (.1, 5.6), (.1, 0)]); inlet.data.materials.append(brass); inlet.location = (VX, 0, 0)
box(brass, (VX, 0, 5.7), (.42, .42, .36), bevel=.04)
lp = b3d.smooth(b3d.prim('uv_sphere', [lamp], segments=20, ring_count=12, radius=.1, location=(VX, -.26, 5.74)))
def leverang(f):
    zb = level(f) + .08
    return max(0, min(1.25, math.asin(max(-1, min(1, (PIVZ - zb) / ARM)))))
arm = b3d.empty('Lever', (VX, -.1, PIVZ))
rd = box(rod_m, (ARM / 2, 0, 0), (ARM, .05, .05)); rd.parent = arm
ball = b3d.smooth(b3d.prim('uv_sphere', [float_m], segments=40, ring_count=24, radius=BALL, location=(ARM, 0, 0))); ball.parent = arm
for f in range(0, N, 2):
    arm.rotation_euler = (0, leverang(f), 0); arm.keyframe_insert('rotation_euler', index=1, frame=f)
box(brass, (VX, -.1, PIVZ), (.12, .12, .22))
GREEN, RED = (.1, 1, .25), (1, .1, .08)
for f, c in ((0, RED), (T_OPEN - 1, RED), (T_OPEN, GREEN), (T_CLOSE - 1, GREEN), (T_CLOSE, RED)):
    b3d.key_input(lamp, 'Emission Color', [(f, c)]); b3d.key_input(lamp, 'Base Color', [(f, c)])
for k in range(34):
    d = b3d.smooth(b3d.prim('uv_sphere', [drop], segments=10, ring_count=6, radius=.055)); rr = random.Random(k + 90); ph = rr.random(); dx = rr.uniform(-.06, .06); y0 = rr.uniform(-.1, .1)
    for f in range(T_OPEN, T_CLOSE, 2):
        u = (ph + (f - T_OPEN) / 14) % 1; sz = 5.45; end = min(level(f), sz - .15)
        d.location = (VX - .28 + dx - u * .1, y0, sz + u * (end - sz)); d.keyframe_insert('location', frame=f)
    b3d.visible(d, [(T_OPEN, T_CLOSE)])
b3d.visible(b3d.arrow('DownPt', (.35, -.55, 5.65), (.35, -.55, 4.95), point_m, r=.04), [(s4 + 10, T_OPEN + 20)])
b3d.visible(b3d.arrow('UpPt', (.35, -.75, 4.3), (.35, -.75, 5.1), point_m, r=.04), [(s5, e5)])

# ---------- outside: front wall, pedestal, bowl ----------
ext = b3d.empty('Exterior')
box(white, (0, -TD / 2 - .03, TZ), (TW + .02, .1, T1 - T0)).parent = ext
box(white, (0, 0, 1.47), (1.5, 1.45, 2.95), bevel=.08).parent = ext
bowl = b3d.lathe('Bowl', [(.001, .0), (.75, .0), (.72, .35), (.8, .9), (1.15, 1.55), (1.3, 2.05), (1.24, 2.1), (1.05, 1.75), (.5, 1.25), (.001, 1.2)]); bowl.data.materials.append(white); bowl.location = (0, -2.35, 0); bowl.scale = (1.2, 1.2, 1.25); bowl.parent = ext
b3d.smooth(b3d.prim('torus', [white], major_radius=1.4, minor_radius=.16, major_segments=64, minor_segments=14, location=(0, -2.35, 2.72))).parent = ext
b3d.visible(ext, [(s1, e1), (s7, e7)])
b3d.visible(inlet, [(s2, e6)]); b3d.visible(pipe, [(s2, e6)])

# ---------- lights ----------
b3d.light('AREA', 'Key', (4, -9, 10), 1100, (1, .95, .88), 8, rot=(40, 0, 22))
b3d.light('AREA', 'Fill', (-6, -8, 5), 420, (.62, .74, 1), 6, rot=(70, 0, -40))
b3d.light('POINT', 'Inside', (0, -.5, 6.0), 70, (1, 1, 1), 1)

# ---------- timeline ----------
cam, tgt = b3d.camera(30)
b3d.shot(cam, tgt, s1, e1, (3.4, -13.4, 4.9), (2.6, -12, 4.7), (0, -.6, 4.0), lens=30)
b3d.shot(cam, tgt, s2, e2, (-1.3, -7.8, 5.2), (-.6, -7.2, 5.0), (-.2, 0, 4.7), lens=30)
b3d.shot(cam, tgt, s3, e3, (1.5, -7.4, 3.8), (1.1, -6.6, 3.5), (.6, 0, 3.5), lens=30)
b3d.shot(cam, tgt, s4, e4, (-1.2, -5.5, 5.0), (-.9, -5.0, 4.9), (-.55, 0, 4.85), lens=30)
b3d.shot(cam, tgt, s5, e5, (.6, -7.4, 4.9), (.2, -6.8, 4.8), (-.2, 0, 4.6), lens=30)
b3d.shot(cam, tgt, s6, e6, (-1.8, -4.4, 5.8), (-1.5, -3.9, 5.8), (-.9, 0, 5.55), lens=30)
b3d.shot(cam, tgt, s7, e7, (2.6, -12, 4.7), (3.6, -15.4, 5.2), (0, -.6, 3.8), lens=30)
b3d.render(OUT, cfg.get('frames'))
