"""Kir mashina: front-loader with the door panel removed. Wet laundry lies in the slotted drum, the spin ramps up, laundry is pinned to
the wall, water flies off through the slots tangentially, lands in the outer tub and a pump sends it out of the hose. 7 shots."""
import bmesh, math, os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.05, .06, .12), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))
CZ = 1.6  # drum axis height; the axis runs along Y

# ---------- materials ----------
white = b3d.mat('White', (.78, .8, .84), .3)
inside = b3d.mat('Inside', (.13, .15, .2), .6)
steel = b3d.mat('Steel', (.66, .69, .73), .28, metal=.9)
tub_m = b3d.mat('Tub', (.2, .22, .27), .5, metal=.4)
back_m = b3d.mat('Back', (.32, .35, .4), .4, metal=.6)
dark = b3d.mat('Dark', (.05, .05, .07), .4)
chrome = b3d.mat('Chrome', (.75, .77, .8), .15, metal=1)
glass = b3d.mat('Glass', (.6, .75, .9), .05)
b3d.bsdf(glass).inputs['Alpha'].default_value = .22
try: glass.surface_render_method = 'BLENDED'
except (AttributeError, TypeError): pass
tile = b3d.mat('Tile', (.38, .42, .48), .4, bump=.1)
wall = b3d.mat('Wall', (.2, .3, .38), .8)
water = b3d.mat('Water', (.25, .6, 1), .15, emit=(.1, .45, 1), estr=2.2)
pool_m = b3d.mat('Pool', (.15, .45, .95), .12, emit=(.06, .32, .85), estr=1.3)
pump_m = b3d.mat('Pump', (1, .55, .1), .4, emit=(1, .42, .03), estr=.7)
hose_m = b3d.mat('Hose', (.7, .85, 1), .2)
b3d.bsdf(hose_m).inputs['Alpha'].default_value = .3
try: hose_m.surface_render_method = 'BLENDED'
except (AttributeError, TypeError): pass
screen = b3d.mat('Screen', (.05, .3, .3), .3, emit=(.15, .9, .75), estr=2)
point_m = b3d.mat('Point', (1, .8, .2), .4, emit=(1, .72, .08), estr=2.6)
hold_m = b3d.mat('Hold', (.55, .9, 1), .4, emit=(.5, .85, 1), estr=2.6)
bottle = b3d.mat('Bottle', (.15, .45, .9), .3)
cl_cols = [(.85, .14, .12), (.95, .75, .15), (.9, .9, .92), (.14, .4, .85), (.12, .65, .35), (.85, .35, .6), (.95, .5, .12), (.3, .25, .7)]
cloth = [b3d.mat(f'Cl{i}', c, .85, bump=.5) for i, c in enumerate(cl_cols)]

def box(m, c, s, bevel=0):
    b = b3d.prim('cube', [m], size=1, location=c); b.scale = s
    if bevel:
        bv = b.modifiers.new('Bv', 'BEVEL'); bv.width = bevel; bv.segments = 4; b3d.smooth(b)
    return b

def arc(name, m, r0, r1, a0, a1, y0, y1, steps=6, parent=None):
    """Curved block round the Y axis through (0, 0, 0): angles in radians measured in the XZ plane."""
    bm = bmesh.new(); rings = []
    for i in range(steps + 1):
        a = a0 + (a1 - a0) * i / steps; c, s = math.cos(a), math.sin(a)
        rings.append([bm.verts.new((r * c, y, r * s)) for r, y in ((r0, y0), (r1, y0), (r1, y1), (r0, y1))])
    for i in range(steps):
        p, q = rings[i], rings[i + 1]
        for k in range(4): bm.faces.new((p[k], p[(k + 1) % 4], q[(k + 1) % 4], q[k]))
    if abs(a1 - a0) < 6.28:
        bm.faces.new(rings[0]); bm.faces.new(rings[-1][::-1])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(m)
    ob = b3d.link(bpy.data.objects.new(name, me))
    if parent: ob.parent = parent
    return ob

# ---------- room and case ----------
box(tile, (0, 2, -.25), (30, 30, .5))
b3d.prim('plane', [wall], size=40, location=(0, 1.6, 10), rotation=(math.radians(90), 0, 0))
H, W, D = 3.25, 1.34, 1.25
box(inside, (-W, 0, H / 2), (.06, 2 * D, H)); box(inside, (W, 0, H / 2), (.06, 2 * D, H))
box(white, (0, 0, H), (2 * W + .06, 2 * D, .06), bevel=.015); box(inside, (0, 0, .05), (2 * W, 2 * D, .1)); box(inside, (0, D, H / 2), (2 * W, .06, H))
ext = b3d.empty('Exterior')
for sgn in (-1, 1): box(white, (sgn * (W + .035), 0, H / 2), (.02, 2 * D, H)).parent = ext  # white skin outside the dark inner walls
panel = box(white, (0, -D, H / 2), (2 * W + .06, .06, H))
cutter = b3d.prim('cylinder', [], vertices=96, radius=.95, depth=1, location=(0, -D, CZ), rotation=(math.radians(90), 0, 0)); cutter.hide_render = True; cutter.hide_viewport = True
bl = panel.modifiers.new('Hole', 'BOOLEAN'); bl.operation = 'DIFFERENCE'; bl.object = cutter; panel.parent = ext
box(dark, (-.35, -D - .035, 2.98), (1.5, .02, .34)).parent = ext
box(screen, (-.55, -D - .05, 2.98), (.6, .012, .2)).parent = ext
kn = b3d.smooth(b3d.prim('cylinder', [chrome], vertices=40, radius=.17, depth=.1, location=(.86, -D - .08, 2.98), rotation=(math.radians(90), 0, 0))); kn.parent = ext
ring = b3d.smooth(b3d.prim('torus', [chrome], major_radius=1.0, minor_radius=.07, major_segments=96, minor_segments=16, location=(0, -D - .06, CZ), rotation=(math.radians(90), 0, 0))); ring.parent = ext
gd = b3d.prim('cylinder', [glass], vertices=96, radius=.98, depth=.04, location=(0, -D - .06, CZ), rotation=(math.radians(90), 0, 0)); gd.parent = ext
try: gd.visible_shadow = False
except AttributeError: pass
bt = b3d.lathe('Bottle', [(.001, 0), (.26, 0), (.3, .1), (.3, .62), (.14, .78), (.14, .95), (.001, .95)]); bt.data.materials.append(bottle); bt.location = (-.75, .1, H + .03)

# ---------- outer tub (fixed) and drum (spins about Y) ----------
AX = b3d.empty('TubRoot', (0, 0, CZ))
arc('TubWall', tub_m, 1.24, 1.3, 0, 2 * math.pi, -.86, .95, steps=96, parent=AX)
arc('TubLip', steel, 1.2, 1.3, 0, 2 * math.pi, -.9, -.86, steps=96, parent=AX)
bd = b3d.prim('cylinder', [dark], vertices=96, radius=1.27, depth=.04, location=(0, .93, 0), rotation=(math.radians(90), 0, 0)); bd.parent = AX
drum = b3d.empty('Drum', (0, 0, CZ))
SEG, ROWS = 26, 5
y = -.8; dy = 1.6 / ROWS; pitch = 2 * math.pi / SEG
for rw in range(ROWS):
    for k in range(SEG):
        a0 = (k + (.5 if rw % 2 else 0)) * pitch
        arc(f'D{rw}_{k}', steel, 1.0, 1.05, a0 + pitch * .13, a0 + pitch * .87, y, y + dy, steps=3, parent=drum)
    y += dy
for yy in (-.82, .8, -.02):
    arc(f'Hoop{yy}', steel, 1.0, 1.06, 0, 2 * math.pi, yy, yy + .035, steps=72, parent=drum)
dbk = b3d.prim('cylinder', [back_m], vertices=96, radius=1.03, depth=.04, location=(0, .82, 0), rotation=(math.radians(90), 0, 0)); dbk.parent = drum
hub = b3d.smooth(b3d.prim('uv_sphere', [steel], segments=32, ring_count=16, radius=.2, location=(0, .78, 0))); hub.scale = (1, .3, 1); hub.parent = drum
for k in range(3):
    a = k * 2 * math.pi / 3 + .4
    lf = box(steel, (.92 * math.cos(a), 0, .92 * math.sin(a)), (.09, 1.55, .16), bevel=.03); lf.rotation_euler = (0, math.pi / 2 - a, 0); lf.parent = drum

# angular speed per frame, with slow-motion for the explanation shot
def rate(f):
    if f < s2: return .012
    if f < s3: return .024
    if f < s3 + 24: return .024 + (f - s3) / 24 * .17
    if f < s4: return .194
    if f < s5: return .045          # slowed down so the eye can follow one piece
    if f < s7: return .13
    return max(.012, .13 * (1 - (f - s7) / 40))
PHI = [0.]
for f in range(N + 1): PHI.append(PHI[-1] + rate(f))
for f in range(N):
    drum.rotation_euler = (0, PHI[f], 0); drum.keyframe_insert('rotation_euler', index=1, frame=f)

# laundry: a heap at the bottom until the spin ramps up, then pinned to the wall
r = random.Random(5); pieces = []
for k in range(9):
    pc = b3d.smooth(b3d.prim('ico_sphere', [cloth[k % 8]], subdivisions=4, radius=1))
    d = pc.modifiers.new('Disp', 'DISPLACE'); tx = bpy.data.textures.new(f'Tx{k}', 'CLOUDS'); tx.noise_scale = .55; d.texture = tx; d.strength = .22
    off = k * 2 * math.pi / 9 + r.uniform(-.1, .1); y0 = r.uniform(-.48, .48); hp = (-math.pi / 2 + r.uniform(-.7, .7), r.uniform(.56, .8), r.uniform(-.5, .5))
    sca = (r.uniform(.28, .38), r.uniform(.26, .36), r.uniform(.11, .16))
    pieces.append((pc, off))
    for f in range(0, N, 2):
        bl_ = min(1, max(0, (f - s3) / 22)); bl_ = bl_ * bl_ * (3 - 2 * bl_)
        th_h = hp[0] + .05 * math.sin(f * .08 + k) * (1 - bl_); th_w = off - PHI[f]
        dth = (th_w - th_h + math.pi) % (2 * math.pi) - math.pi; th = th_h + bl_ * dth  # shortest arc from heap to wall
        rd = hp[1] + bl_ * (.86 - hp[1]); yy = hp[2] + bl_ * (y0 - hp[2])
        pc.location = (rd * math.cos(th), yy, CZ + rd * math.sin(th)); pc.rotation_euler = (0, math.pi / 2 - th, 0)
        pc.scale = (sca[0] * (1 + .22 * bl_), sca[1] * (1 + .12 * bl_), sca[2] * (1 - .25 * bl_))
        pc.keyframe_insert('location', frame=f); pc.keyframe_insert('rotation_euler', frame=f); pc.keyframe_insert('scale', frame=f)

# shot 4 arrows ride on one piece: yellow tangent (wants to fly straight), pale inward (the wall holds it)
rider = b3d.empty('Rider', (0, 0, CZ))
for f in range(s4, e4):
    rider.rotation_euler = (0, PHI[f], 0); rider.keyframe_insert('rotation_euler', index=1, frame=f)
a0 = pieces[0][1]; px, pz = .9 * math.cos(a0), .9 * math.sin(a0); tx_, tz_ = math.sin(a0), -math.cos(a0)  # velocity of Ry(+phi) at that spot
ar = b3d.arrow('Fly', (px, -.75, pz), (px + .85 * tx_, -.75, pz + .85 * tz_), point_m, r=.045); ar.parent = rider
ah = b3d.arrow('Hold', (1.06 * math.cos(a0 + .28), -.75, 1.06 * math.sin(a0 + .28)), (.72 * math.cos(a0 + .28), -.75, .72 * math.sin(a0 + .28)), hold_m, r=.04); ah.parent = rider
b3d.visible(ar, [(s4, e4)]); b3d.visible(ah, [(s4, e4)])

# water: drips off the heap in shot 2, flies off tangentially while spinning
for k in range(10):
    d = b3d.smooth(b3d.prim('uv_sphere', [water], segments=10, ring_count=6, radius=.028)); x0 = r.uniform(-.55, .55); y0 = r.uniform(-.45, .45); ph = k / 10
    for f in range(s2, e2, 2):
        u = (ph + (f - s2) / 26) % 1; d.location = (x0, y0, CZ - .6 - u * .58); d.keyframe_insert('location', frame=f)
    b3d.visible(d, [(s2, e2)])
SPIN = [(s3 + 14, e3), (s5, e5), (s6, e6)]
for k in range(70):
    d = b3d.smooth(b3d.prim('uv_sphere', [water], segments=10, ring_count=6, radius=.045)); y0 = random.Random(k).uniform(-.72, .72); per = 11; pk = k * 3 % per
    for a, b in SPIN:
        for f in range(a, b):
            cyc = (f + pk) // per; u = ((f + pk) % per) / per; th = random.Random(k * 977 + cyc).uniform(0, 2 * math.pi)
            st = (1.03 * math.cos(th), 1.03 * math.sin(th)); tn = (math.sin(th), -math.cos(th)); L = .69
            d.location = (st[0] + u * L * tn[0], y0, CZ + st[1] + u * L * tn[1]); d.keyframe_insert('location', frame=f)
    b3d.visible(d, SPIN)

# pool at the bottom of the tub during shots 5-6
pool = arc('Pool', pool_m, 1.14, 1.24, -math.pi / 2 - .75, -math.pi / 2 + .75, -.82, .9, steps=32); pool.location = (0, 0, CZ)
b3d.visible(pool, [(s5, e6)])

# pump and drain hose: tub bottom -> pump -> out through the right wall -> up to the wall outlet
PATH = [(0, -.05, CZ - 1.3), (.1, -.05, .2), (.72, -.05, .22), (1.34, -.05, .3), (1.66, -.05, .7), (1.76, -.05, 1.6), (1.8, 1.3, 2.15)]
pu = b3d.smooth(b3d.prim('cylinder', [pump_m], vertices=40, radius=.24, depth=.3, location=(.72, -.05, .24), rotation=(math.radians(90), 0, 0)))
impel = b3d.empty('Impel', (.72, -.25, .24))
for k in range(4):
    bi = box(dark, (0, 0, 0), (.38, .03, .05)); bi.rotation_euler = (0, k * math.pi / 4, 0); bi.parent = impel
for f in range(s5, e6, 2):
    impel.rotation_euler = (0, f * .5, 0); impel.keyframe_insert('rotation_euler', index=1, frame=f)
cv = bpy.data.curves.new('HoseC', 'CURVE'); cv.dimensions = '3D'; cv.bevel_depth = .085; cv.bevel_resolution = 4
sp = cv.splines.new('BEZIER'); sp.bezier_points.add(len(PATH) - 1)
for bp, p in zip(sp.bezier_points, PATH): bp.co = p; bp.handle_left_type = bp.handle_right_type = 'AUTO'
cv.materials.append(hose_m); hose = b3d.link(bpy.data.objects.new('Hose', cv))
out = box(steel, (1.8, 1.45, 2.15), (.3, .22, .3), bevel=.04)

def at(u):  # Catmull-Rom through the hose points
    n = len(PATH) - 1; t = min(u, .9999) * n; i = int(t); k = t - i; P = lambda j: PATH[max(0, min(n, j))]
    a, b, c, d = P(i - 1), P(i), P(i + 1), P(i + 2)
    return tuple(.5 * ((2 * b[m]) + (c[m] - a[m]) * k + (2 * a[m] - 5 * b[m] + 4 * c[m] - d[m]) * k * k + (3 * b[m] - a[m] - 3 * c[m] + d[m]) * k ** 3) for m in range(3))
for k in range(26):
    d = b3d.smooth(b3d.prim('uv_sphere', [water], segments=10, ring_count=6, radius=.05)); ph = k / 26
    for f in range(s6, e6, 2):
        d.location = at((ph + (f - s6) / 60) % 1); d.keyframe_insert('location', frame=f)
    b3d.visible(d, [(s6, e6)])
b3d.visible(b3d.arrow('PumpPt', (.72, -.5, 1.0), (.72, -.5, .5), point_m, r=.034), [(s6, e6)])

# ---------- lights ----------
b3d.light('AREA', 'Key', (3, -6, 6), 650, (1, .94, .86), 6, rot=(45, 0, 25))
b3d.light('AREA', 'Fill', (-5, -5, 3), 320, (.62, .74, 1), 4, rot=(70, 0, -45))
b3d.light('POINT', 'DrumGlow', (0, -.3, CZ + .25), 42, (1, .95, .85), .6)

# ---------- timeline ----------
cam, tgt = b3d.camera(30)
b3d.shot(cam, tgt, s1, e1, (1.3, -6.9, 2.6), (.9, -6.1, 2.5), (0, 0, 2.3), lens=30)     # hook: machine in the room, drum turning behind the door
b3d.shot(cam, tgt, s2, e2, (-1.0, -5.4, 2.5), (-.6, -4.6, 2.3), (0, 0, 1.65), lens=30)    # panel gone: slotted drum, wet heap
b3d.shot(cam, tgt, s3, e3, (.7, -4.7, 1.9), (.3, -4.1, 1.75), (0, 0, 1.6), lens=30)       # spin ramps up
b3d.shot(cam, tgt, s4, e4, (-.5, -3.9, 2.0), (-.3, -3.5, 1.9), (0, 0, 1.6), lens=30)      # slow: arrows on one piece
b3d.shot(cam, tgt, s5, e5, (1.0, -3.5, 1.4), (.85, -3.1, 1.4), (.55, 0, 1.3), lens=30)  # close: drops shoot through the slots
b3d.shot(cam, tgt, s6, e6, (1.5, -5.4, 1.2), (1.1, -4.7, 1.15), (.8, 0, 1.05), lens=30)   # pump and hose
b3d.shot(cam, tgt, s7, e7, (.8, -6.2, 2.5), (1.5, -8.6, 2.8), (0, 0, 2.2), lens=30)      # end: outside again
b3d.visible(ext, [(s1, e1), (s7, e7)])
for o in (hose, out, pu, impel): b3d.visible(o, [(s6, e6)])

b3d.render(OUT, cfg.get('frames'))
