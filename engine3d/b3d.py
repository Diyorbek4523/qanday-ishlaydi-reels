"""Blender helpers for 3D "Qanday ishlaydi?" reels (run inside Blender: blender -b --python scene.py -- cfg.json outdir).

A scene script builds its objects with these helpers, keys one camera shot per script scene (cfg["starts"] in seconds),
and calls render(). Shots cut hard: each shot keys its first and last frame, the next shot starts one frame later.
"""
import bpy, bmesh, json, math, os, random, sys
from mathutils import Vector

FPS = 30

def args():
    a = sys.argv[sys.argv.index('--') + 1:]
    cfg = json.load(open(a[0], encoding='utf-8'))
    return cfg, a[1], [round(s * FPS) for s in cfg['starts']]

def setup(frames, sky=(0.02, 0.025, 0.05), sky_str=1.0, preview=False):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    for e in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE'):
        try: sc.render.engine = e; break
        except TypeError: pass
    sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
    sc.render.resolution_percentage = 50 if preview else 100
    sc.render.fps = FPS; sc.frame_start = 0; sc.frame_end = frames - 1
    try: sc.eevee.taa_render_samples = 8 if preview else 24
    except AttributeError: pass
    for k, v in (('view_transform', 'Standard'), ('look', 'None')):  # AgX washes emissive colours (fire, glow) out to white
        try: setattr(sc.view_settings, k, v)
        except TypeError: pass
    w = bpy.data.worlds.new('W'); sc.world = w
    try: w.use_nodes = True
    except AttributeError: pass
    bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs[0].default_value = (*sky, 1); bg.inputs[1].default_value = sky_str
    sc.render.image_settings.file_format = 'PNG'
    return sc

def link(ob):
    bpy.context.scene.collection.objects.link(ob); return ob

def mat(name, color, rough=.6, metal=0., emit=None, estr=0., bump=0.):
    m = bpy.data.materials.new(name)
    try: m.use_nodes = True
    except AttributeError: pass
    nt = m.node_tree; b = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs['Base Color'].default_value = (*color, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if emit: b.inputs['Emission Color'].default_value = (*emit, 1); b.inputs['Emission Strength'].default_value = estr
    if bump:  # noisy surface (clay, dirt, dough)
        nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 40; bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = bump
        nt.links.new(nz.outputs['Fac'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    return m

def bsdf(m): return next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')

def key_input(m, name, frames_vals):  # keyframe a Principled input: [(frame, value)]
    inp = bsdf(m).inputs[name]
    for f, v in frames_vals:
        inp.default_value = (*v, 1) if isinstance(v, tuple) else v; inp.keyframe_insert('default_value', frame=f)

def smooth(ob):
    for p in ob.data.polygons: p.use_smooth = True
    return ob

def prim(kind, mats=(), **kw):
    getattr(bpy.ops.mesh, f'primitive_{kind}_add')(**kw); ob = bpy.context.object
    for m in mats: ob.data.materials.append(m)
    return ob

def lathe(name, prof, steps=72):  # spin an (r, z) profile round the Z axis
    bm = bmesh.new(); vs = [bm.verts.new((r, 0, z)) for r, z in prof]
    es = [bm.edges.new((vs[i], vs[i + 1])) for i in range(len(vs) - 1)]
    bmesh.ops.spin(bm, geom=vs + es, cent=(0, 0, 0), axis=(0, 0, 1), angle=2 * math.pi, steps=steps, use_merge=True)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    return smooth(link(bpy.data.objects.new(name, me)))

def empty(name, loc=(0, 0, 0)):
    e = link(bpy.data.objects.new(name, None)); e.location = loc; return e

def camera(lens=30):
    cd = bpy.data.cameras.new('Cam'); cd.lens = lens; cd.clip_start = .02
    cam = link(bpy.data.objects.new('Cam', cd)); bpy.context.scene.camera = cam
    tgt = empty('CamTarget')
    c = cam.constraints.new('TRACK_TO'); c.target = tgt; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
    return cam, tgt

def shot(cam, tgt, f0, f1, pa, pb, ta, tb=None, lens=None):
    """Camera move from pa->pb looking ta->tb over frames [f0, f1)."""
    tb = tb or ta
    for f, p, t in ((f0, pa, ta), (f1 - 1, pb, tb)):
        cam.location = p; cam.keyframe_insert('location', frame=f); tgt.location = t; tgt.keyframe_insert('location', frame=f)
        if lens: cam.data.lens = lens; cam.data.keyframe_insert('lens', frame=f)

def tree(ob): return [ob] + [c for ch in ob.children for c in tree(ch)]

def visible(ob, ranges):
    """Show ob (and children) only inside [f0, f1) ranges."""
    edges = sorted({0} | {a for a, _ in ranges} | {b for _, b in ranges})
    for o in tree(ob):
        for f in edges:
            o.hide_render = not any(a <= f < b for a, b in ranges); o.keyframe_insert('hide_render', frame=f)

def flicker(ob, what, f0, f1, lo, hi, every=3, seed=0, mul=None):
    """Random flicker of a light's energy or an object's scale (taller than wide, like a flame). mul(f) scales the range."""
    r = random.Random(seed)
    for f in range(f0, f1, every):
        v = (lo + (hi - lo) * r.random()) * (mul(f) if mul else 1)
        if what == 'energy': ob.data.energy = v; ob.data.keyframe_insert('energy', frame=f)
        else: ob.scale = (v, v, v * (1.2 + .5 * r.random())); ob.keyframe_insert('scale', frame=f)

def arrow(name, a, b, m, r=.022):  # cylinder shaft + cone head from a to b
    a, b = Vector(a), Vector(b); d = b - a; L = d.length
    root = empty(name, a); root.rotation_mode = 'QUATERNION'; root.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    sh = prim('cylinder', [m], vertices=16, radius=r, depth=L * .75, location=(0, 0, 0)); sh.parent = root; sh.location = (0, 0, L * .375)
    hd = prim('cone', [m], vertices=16, radius1=r * 2.6, depth=L * .25, location=(0, 0, 0)); hd.parent = root; hd.location = (0, 0, L * .875)
    return root

def light(kind, name, loc, energy, color=(1, 1, 1), size=.2, rot=None):
    ld = bpy.data.lights.new(name, kind); ld.energy = energy; ld.color = color
    if kind in ('POINT', 'SPOT'): ld.shadow_soft_size = size
    if kind == 'AREA': ld.size = size
    if kind == 'SUN': ld.angle = size
    ob = link(bpy.data.objects.new(name, ld)); ob.location = loc
    if rot: ob.rotation_euler = [math.radians(x) for x in rot]
    return ob

def render(out, frames=None):
    """Render all frames (or only the listed ones, for previews) to out/f_####.png."""
    sc = bpy.context.scene; os.makedirs(out, exist_ok=True)
    if frames is None:
        sc.render.filepath = os.path.join(out, 'f_'); bpy.ops.render.render(animation=True)
    else:
        for f in frames:
            sc.frame_set(f); sc.render.filepath = os.path.join(out, f'p_{f:04d}.png'); bpy.ops.render.render(write_still=True)
