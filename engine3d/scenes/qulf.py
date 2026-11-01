"""Qulf (pin tumbler): cutaway of a cylinder lock. Spring-loaded pin stacks block the plug; a wrong key leaves them across the
shear line, the right key lifts every gap onto it and the plug turns. Shots 1, 6, 7 show the lock from outside (at x = 8). 7 shots."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy, bmesh
from mathutils import Vector

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.05, .06, .11), preview=cfg.get('preview'))
sh = list(zip(S[:-1], S[1:]))

# ---------- materials ----------
brass = b3d.mat('Brass', (.78, .58, .25), .35, metal=.7)
brass_cut = b3d.mat('BrassCut', (.62, .45, .2), .55, metal=.2)
hole = b3d.mat('Hole', (.12, .08, .04), .7, metal=.2)
plug_m = b3d.mat('Plug', (.85, .66, .30), .35, metal=.7)
plug_cut = b3d.mat('PlugCut', (.75, .33, .14), .55, metal=.2)
keypin = b3d.mat('KeyPin', (.95, .55, .12), .3, metal=.6)
driver = b3d.mat('Driver', (.62, .66, .72), .3, metal=.8)
spring_m = b3d.mat('Spring', (.75, .78, .82), .3, metal=.9)
key_m = b3d.mat('Key', (.72, .74, .78), .3, metal=.8)
bad_m = b3d.mat('BadKey', (.55, .58, .62), .35, metal=.8)
line_m = b3d.mat('Shear', (1, .1, .05), .5, emit=(1, .08, .03), estr=3)
wood = b3d.mat('Door', (.28, .15, .08), .7, bump=.15)
slot_m = b3d.mat('Slot', (.02, .02, .02), .9)

def cutter(name, loc, scale, m, kind='cube', rot=None):
    if kind == 'cube': c = b3d.prim('cube', [m], size=1, location=loc); c.scale = scale
    else: c = b3d.prim('cylinder', [m], vertices=32, radius=scale[0], depth=scale[1], location=loc)
    if rot: c.rotation_euler = rot
    c.hide_render = True; c.hide_viewport = True; c.name = name; return c
def boolean(ob, c):
    bo = ob.modifiers.new(c.name, 'BOOLEAN'); bo.operation = 'DIFFERENCE'; bo.object = c
    try: bo.material_mode = 'TRANSFER'
    except (AttributeError, TypeError): pass

PX = [-.6, -.3, 0., .3, .6]; R = .35; SHEAR = R; TOP = 1.1; CH = .085; PR = .075
LK = [.30, .42, .26, .38, .33]; LD = .30; REST = -.17
GOOD = [SHEAR - l for l in LK]                  # tooth height that puts each key pin's top on the shear line
BAD = [.05, .09, -.08, -.03, .12]               # pins 2, 3 and 5 end up wrong
Y90 = (0, math.radians(90), 0)

# ---------- housing (back half only, cut face at y = 0) ----------
hous = b3d.prim('cube', [brass], size=1, location=(0, 0, .3)); hous.scale = (2, 1.2, 1.8)
hous.data.materials.append(brass_cut); hous.data.materials.append(hole)
boolean(hous, cutter('HFront', (0, -.6, .3), (3, 1.2, 3), brass_cut))
boolean(hous, cutter('HPlug', (0, 0, 0), (R + .005, 2.4), hole, 'cyl', Y90))
for k, x in enumerate(PX): boolean(hous, cutter(f'HCh{k}', (x, 0, (SHEAR - .05 + TOP) / 2), (CH, TOP - SHEAR + .05), hole, 'cyl'))
plug = b3d.prim('cylinder', [plug_m], vertices=64, radius=R, depth=2.0, location=(0, 0, 0)); plug.rotation_euler = Y90; b3d.smooth(plug)
plug.data.materials.append(plug_cut); plug.data.materials.append(hole)
boolean(plug, cutter('PFront', (0, -.6, 0), (3, 1.2, 3), plug_cut))
boolean(plug, cutter('PWay', (0, 0, -.2), (2.4, .09, .2), hole))
for k, x in enumerate(PX): boolean(plug, cutter(f'PCh{k}', (x, 0, .15), (CH, .7), hole, 'cyl'))

# ---------- pins and springs ----------
def helix(name, coils=8, r=.058, wire=.011):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = wire; cu.bevel_resolution = 2
    sp = cu.splines.new('POLY'); n = coils * 16; sp.points.add(n)
    for i, p in enumerate(sp.points): t = i / n; p.co = (r * math.cos(t * coils * 2 * math.pi), r * math.sin(t * coils * 2 * math.pi), -t, 1)
    ob = b3d.link(bpy.data.objects.new(name, cu)); cu.materials.append(spring_m); return ob
kps, dps, sps = [], [], []
for k, x in enumerate(PX):
    kp = b3d.prim('cylinder', [keypin], vertices=32, radius=PR, depth=LK[k]); b3d.smooth(kp)
    bv = kp.modifiers.new('Bv', 'BEVEL'); bv.width = .03; bv.segments = 4; kps.append(kp)
    dp = b3d.prim('cylinder', [driver], vertices=32, radius=PR, depth=LD); b3d.smooth(dp)
    bv = dp.modifiers.new('Bv', 'BEVEL'); bv.width = .012; bv.segments = 3; dps.append(dp)
    s = helix(f'Spring{k}'); s.location = (x, 0, TOP); sps.append(s)
def place(k, bottom, f):
    kps[k].location = (PX[k], 0, bottom + LK[k] / 2); kps[k].keyframe_insert('location', frame=f)
    dt = bottom + LK[k]; dps[k].location = (PX[k], 0, dt + LD / 2); dps[k].keyframe_insert('location', frame=f)
    sps[k].scale = (1, 1, TOP - dt - LD); sps[k].keyframe_insert('scale', frame=f)

# ---------- keys: blade profile in XZ (x = position along the plug when fully in), extruded in Y ----------
def make_key(name, heights, m):
    def top(u):
        if u > .9: return None
        if u > .68: return -.12 - (u - .68) / .22 * .1
        pts = [(-1.05, .1)] + [(x + d, h) for x, h in zip(PX, heights) for d in (-.045, .045)] + [(.68, -.12)]
        for (a, ha), (b, hb) in zip(pts, pts[1:]):
            if a <= u <= b: return ha + (hb - ha) * (u - a) / max(1e-6, b - a)
        return .1
    us = [.9 - i * .01 for i in range(int((.9 + 1.05) / .01) + 1)]
    outline = [(-1.05, -.28), (.8, -.28), (.9, -.24)] + [(u, top(u)) for u in us]
    bm = bmesh.new(); vs = [bm.verts.new((x, -.03, z)) for x, z in outline]; f = bm.faces.new(vs)
    r = bmesh.ops.extrude_face_region(bm, geom=[f]); bmesh.ops.translate(bm, vec=(0, .06, 0), verts=[v for v in r['geom'] if isinstance(v, bmesh.types.BMVert)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    root = b3d.empty(name + 'Root'); blade = b3d.link(bpy.data.objects.new(name, me)); blade.data.materials.append(m); blade.parent = root
    neck = b3d.prim('cube', [m], size=1, location=(-1.2, 0, -.09)); neck.scale = (.32, .06, .38); neck.parent = root
    bow = b3d.prim('cylinder', [m], vertices=48, radius=.34, depth=.07, location=(-1.6, 0, -.09)); bow.rotation_euler = (math.radians(90), 0, 0); bow.parent = root
    holeb = b3d.prim('cylinder', [slot_m], vertices=32, radius=.08, depth=.08, location=(-1.75, 0, -.09)); holeb.rotation_euler = (math.radians(90), 0, 0); holeb.parent = root
    return root, top
good_key, good_top = make_key('GoodKey', GOOD, key_m)
bad_key, bad_top = make_key('BadKey', BAD, bad_m)
shear = b3d.prim('cube', [line_m], size=1, location=(0, -.1, SHEAR)); shear.scale = (2.05, .01, .014)

# ---------- outside view: door with the lock face; same key turning (at x = 8) ----------
X0 = 8.
door = b3d.prim('cube', [wood], size=1, location=(X0, .06, .2)); door.scale = (4, .12, 4.5)
ros = b3d.prim('cylinder', [brass], vertices=64, radius=.55, depth=.05, location=(X0, -.02, 0)); ros.rotation_euler = (math.radians(90), 0, 0); b3d.smooth(ros)
bv = ros.modifiers.new('Bv', 'BEVEL'); bv.width = .02; bv.segments = 4
turn = b3d.empty('Turn', (X0, 0, 0)); turn.rotation_mode = 'XYZ'
face = b3d.prim('cylinder', [plug_m], vertices=64, radius=.33, depth=.06, location=(X0, -.06, 0)); face.rotation_euler = (math.radians(90), 0, 0); b3d.smooth(face)
slot = b3d.prim('cube', [slot_m], size=1, location=(X0, -.092, -.09)); slot.scale = (.075, .01, .42)
face.parent = turn; face.location = (0, -.06, 0); slot.parent = turn; slot.location = (0, -.092, -.09)
ext_key, _ = make_key('ExtKey', GOOD, key_m)
ext_hold = b3d.empty('ExtHold', (0, 0, 0)); ext_hold.parent = turn; ext_hold.location = (0, 0, 0)
ext_key.parent = ext_hold; ext_key.rotation_euler = (0, 0, math.radians(90))  # blade along +Y into the door, bow toward the camera

# ---------- lights ----------
b3d.light('SUN', 'Sun', (0, 0, 5), 1.5, (1, .9, .75), .3, rot=(50, 0, -25))
b3d.light('AREA', 'Front', (0, -3.5, 1.5), 140, (1, .95, .9), 4, rot=(70, 0, 0))
b3d.light('AREA', 'Fill', (-3, -2, 2), 150, (.6, .7, 1), 3, rot=(55, 0, -55))
b3d.light('AREA', 'FrontX', (X0 + 1, -3, 1.5), 110, (1, .92, .85), 3, rot=(65, 0, 20))

# ---------- timeline ----------
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = sh
cam, tgt = b3d.camera(30)
b3d.shot(cam, tgt, s1, e1, (X0 + 1.4, -3.4, .6), (X0 + 1.0, -2.7, .4), (X0, -.4, 0), lens=32)       # hook: key comes to the lock
b3d.shot(cam, tgt, s2, e2, (.2, -3.0, .45), (0, -2.7, .4), (0, 0, .3), lens=30)                     # cutaway: five pin stacks
b3d.shot(cam, tgt, s3, e3, (-.15, -1.55, .7), (-.25, -1.3, .62), (-.3, 0, .55), lens=30)              # close-up: two halves + spring
b3d.shot(cam, tgt, s4, e4, (-.4, -3.5, .4), (-.25, -3.2, .38), (-.25, 0, .25), lens=30)              # wrong key
b3d.shot(cam, tgt, s5, e5, (-.05, -3.5, .4), (-.25, -3.2, .38), (-.25, 0, .25), lens=30)                # right key: gaps on the line
b3d.shot(cam, tgt, s6, e6, (X0 + .7, -2.0, .45), (X0 + .55, -1.7, .35), (X0, -.4, 0), lens=32)      # outside: key turns
b3d.shot(cam, tgt, s7, e7, (X0 + .6, -1.9, .4), (X0 + 1.3, -3.9, 1.1), (X0, -.2, .1), lens=30)      # end: pull back

def key_off(f, a, b):  # key slides in over the first 60% of the shot
    t = min(1, max(0, (f - a) / ((b - a) * .6))); t = t * t * (3 - 2 * t); return -2.2 * (1 - t)
for f in range(0, N + 1):
    if s4 <= f < e4: o, top = key_off(f, s4, e4), bad_top
    elif s5 <= f < e5: o, top = key_off(f, s5, e5), good_top
    else: o, top = None, None
    for k in range(5):
        h = top(PX[k] - o) if top else None
        b = max(REST, h) if h is not None else REST
        if k == 1 and s3 + 6 <= f < s3 + 36: b += .14 * math.sin((f - s3 - 6) / 30 * math.pi)  # pushed up, the spring presses it back
        place(k, b, f)
    if s4 <= f < e5: (bad_key if f < e4 else good_key).location = (o, 0, 0); (bad_key if f < e4 else good_key).keyframe_insert('location', frame=f)

for o in (hous, plug) + tuple(kps) + tuple(dps) + tuple(sps): b3d.visible(o, [(s2, e5)])
b3d.visible(shear, [(s3, e5)])
b3d.visible(bad_key, [(s4, e4)]); b3d.visible(good_key, [(s5, e5)])
for o in (door, ros, turn, face, slot, ext_hold): b3d.visible(o, [(s1, e1), (s6, e7)])
b3d.visible(ext_key, [(s1, e1), (s6, e7)])

# shear line: red while blocked, green once the right key has lined the gaps up
GREEN = (.1, 1, .25); RED = (1, .08, .03); ok = s5 + int((e5 - s5) * .6)
b3d.key_input(line_m, 'Emission Color', [(s3, RED), (ok - 1, RED), (ok + 3, GREEN)])
b3d.key_input(line_m, 'Base Color', [(s3, RED), (ok - 1, RED), (ok + 3, GREEN)])

# outside: key slides in (hook), turns a quarter in shot 6
ext_hold.location = (0, -2.1, 0); ext_hold.keyframe_insert('location', frame=s1)
ext_hold.location = (0, -2.1, 0); ext_hold.keyframe_insert('location', frame=s1 + 6)
ext_hold.location = (0, .98, 0); ext_hold.keyframe_insert('location', frame=s1 + int((e1 - s1) * .75))
turn.rotation_euler = (0, 0, 0); turn.keyframe_insert('rotation_euler', frame=s6 + 6)
turn.rotation_euler = (0, math.radians(90), 0); turn.keyframe_insert('rotation_euler', frame=s6 + int((e6 - s6) * .7))

b3d.render(OUT, cfg.get('frames'))
