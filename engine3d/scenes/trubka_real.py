"""Photoreal version of trubka.py (client asked for "real, not cartoon"): Cycles on the GPU, AgX, textured
materials (paint, raw plaster, parquet, foam, corrugated hose), daylight window, depth of field and a light handheld
camera shake. Same story and timing: duct on the wall (bad way) -> groove cut -> pipes laid -> plastered and painted ->
AC on a clean wall."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy

cfg, OUT, S = b3d.args(); N = S[-1]; PRE = cfg.get('preview')
sc = b3d.setup(N, sky=(.55, .62, .75), sky_str=.35, preview=PRE)
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))
R = math.radians
def fr(a, b, u): return int(a + (b - a) * u)

# ---------- renderer: Cycles on the GPU ----------
sc.render.engine = 'CYCLES'
try:
    cp = bpy.context.preferences.addons['cycles'].preferences
    for t in ('OPTIX', 'CUDA'):
        try:
            cp.compute_device_type = t; cp.get_devices()
            if any(d.type == t for d in cp.devices): break
        except TypeError: pass
    for d in cp.devices: d.use = d.type != 'CPU'
    sc.cycles.device = 'GPU'
except Exception as ex: print('GPU setup failed', ex)
sc.cycles.samples = 12 if PRE else int(os.environ.get('REAL_SAMPLES', 40))
sc.cycles.use_denoising = True
sc.cycles.max_bounces = 6; sc.cycles.diffuse_bounces = 3; sc.cycles.glossy_bounces = 3; sc.cycles.transparent_max_bounces = 4
try: sc.render.use_persistent_data = True
except AttributeError: pass
sc.view_settings.exposure = -.8
for k, v in (('view_transform', 'AgX'), ('look', 'AgX - Medium High Contrast')):
    try: setattr(sc.view_settings, k, v)
    except TypeError: pass

# ---------- materials ----------
def pmat(name, color, rough=.5, metal=0.):
    m = b3d.mat(name, color, rough, metal); return m, m.node_tree, b3d.bsdf(m)
def noise(nt, scale, detail=6, vec=None):
    n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = scale; n.inputs['Detail'].default_value = detail
    if vec is not None: nt.links.new(vec, n.inputs['Vector'])
    return n
def ramp(nt, fac, c0, c1):
    r = nt.nodes.new('ShaderNodeValToRGB'); r.color_ramp.elements[0].color = (*c0, 1); r.color_ramp.elements[1].color = (*c1, 1)
    nt.links.new(fac, r.inputs['Fac']); return r.outputs['Color']
def bump(nt, b, height, strength, dist=.002):
    bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = strength; bp.inputs['Distance'].default_value = dist
    nt.links.new(height, bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal']); return bp
def mapping(nt, scale):
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = scale
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); return mp.outputs['Vector']

PAINT0, PAINT1 = (.80, .74, .64), (.84, .78, .69)
RAW0, RAW1 = (.42, .41, .39), (.58, .57, .54)
# wall: painted surface <-> raw plaster, blended by one keyed factor
wall_m, nt, b = pmat('Wall', PAINT0, .85)
fine = noise(nt, 300, 4); coarse = noise(nt, 6, 3); spot = noise(nt, 60, 8)
paint_c = ramp(nt, coarse.outputs['Fac'], PAINT0, PAINT1); raw_c = ramp(nt, spot.outputs['Fac'], RAW0, RAW1)
mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'
nt.links.new(paint_c, mix.inputs[6]); nt.links.new(raw_c, mix.inputs[7]); nt.links.new(mix.outputs[2], b.inputs['Base Color'])
hmix = nt.nodes.new('ShaderNodeMix'); hmix.data_type = 'FLOAT'
nt.links.new(fine.outputs['Fac'], hmix.inputs[2]); nt.links.new(spot.outputs['Fac'], hmix.inputs[3])
bump(nt, b, hmix.outputs[0], .12)
WALL_RAW = [mix.inputs[0], hmix.inputs[0]]
def wall_raw(fv):
    for inp in WALL_RAW:
        for f, v in fv: inp.default_value = v; inp.keyframe_insert('default_value', frame=f)

def plain(name, color, rough, scale=200, strength=.05, metal=0.):
    m, nt, b = pmat(name, color, rough, metal); bump(nt, b, noise(nt, scale, 4).outputs['Fac'], strength); return m
white_m = plain('White', (.86, .86, .85), .35, 120, .02)
plastic_m = plain('Plastic', (.9, .9, .89), .22, 80, .01)
dark_m = plain('Dark', (.02, .02, .022), .4)
groove_m, nt, b = pmat('Groove', (.35, .33, .31), .95)
g = noise(nt, 40, 10); nt.links.new(ramp(nt, g.outputs['Fac'], (.22, .21, .2), (.45, .43, .4)), b.inputs['Base Color']); bump(nt, b, g.outputs['Fac'], .6, .01)
copper_m = plain('Copper', (.93, .55, .38), .28, 400, .02, metal=1.)
foam_m = plain('Foam', (.03, .03, .03), .85, 500, .25)
cable_m = plain('Cable', (.82, .82, .8), .38, 300, .02)
hose_m, nt, b = pmat('Hose', (.9, .9, .9), .45)  # corrugated drain hose: rings along its length
wv = nt.nodes.new('ShaderNodeTexWave'); wv.wave_type = 'RINGS'; wv.inputs['Scale'].default_value = 140
nt.links.new(mapping(nt, (1, 1, 1)), wv.inputs['Vector']); bump(nt, b, wv.outputs['Fac'], .5, .003)
duct_m = plain('Duct', (.92, .92, .91), .3, 150, .015)
sofa_m = plain('Sofa', (.42, .4, .37), .95, 700, .35)
rug_m = plain('Rug', (.42, .36, .3), 1., 900, .5)
frame_m = plain('Frame', (.12, .09, .07), .5, 200, .05)
art_m, nt, b = pmat('Art', (.5, .5, .5), .6)
nt.links.new(ramp(nt, noise(nt, 2.5, 2).outputs['Fac'], (.2, .32, .38), (.85, .7, .5)), b.inputs['Base Color'])
# parquet: planks from a brick texture, grain from stretched noise
floor_m, nt, b = pmat('Floor', (.4, .26, .16), .45)
vec = mapping(nt, (1, 1, 1))
br = nt.nodes.new('ShaderNodeTexBrick'); br.inputs['Scale'].default_value = 5; br.inputs['Mortar Size'].default_value = .004
br.inputs['Color1'].default_value = (.36, .22, .12, 1); br.inputs['Color2'].default_value = (.5, .33, .19, 1); br.inputs['Mortar'].default_value = (.12, .07, .04, 1)
br.inputs['Brick Width'].default_value = 1.6; br.inputs['Row Height'].default_value = .18
nt.links.new(vec, br.inputs['Vector'])
mp2 = nt.nodes.new('ShaderNodeMapping'); mp2.inputs['Scale'].default_value = (2, 60, 1); nt.links.new(vec, mp2.inputs['Vector'])
grain = noise(nt, 3, 8, mp2.outputs['Vector'])
fm = nt.nodes.new('ShaderNodeMix'); fm.data_type = 'RGBA'; fm.blend_type = 'MULTIPLY'; fm.inputs[0].default_value = .5
nt.links.new(br.outputs['Color'], fm.inputs[6]); nt.links.new(grain.outputs['Color'], fm.inputs[7]); nt.links.new(fm.outputs[2], b.inputs['Base Color'])
bump(nt, b, br.outputs['Fac'], .25)
# window: bright overcast daylight behind frosted glass
sky_m, nt, b = pmat('Sky', (1, 1, 1), .5)
b.inputs['Emission Color'].default_value = (.85, .92, 1, 1); b.inputs['Emission Strength'].default_value = 6
glass_m, nt, b = pmat('Glass', (.95, .97, 1), .05)
b.inputs['Transmission Weight'].default_value = 1.; b.inputs['IOR'].default_value = 1.45
disp_m, nt, b = pmat('Display', (.1, .2, .3), .3)
b.inputs['Emission Color'].default_value = (.5, .8, 1, 1); b.inputs['Emission Strength'].default_value = 3

def box(m, c, s, bevel=0):
    o = b3d.prim('cube', [m], size=1, location=c); o.scale = s
    if bevel:
        bv = o.modifiers.new('Bv', 'BEVEL'); bv.width = bevel; bv.segments = 4; b3d.smooth(o)
    return o
def cyl(m, r, d, loc, rot=(0, 0, 0), v=32): return b3d.smooth(b3d.prim('cylinder', [m], vertices=v, radius=r, depth=d, location=loc, rotation=rot))
def keys(ob, attr, fv):
    for f, v in fv: setattr(ob, attr, v); ob.keyframe_insert(attr, frame=f)

FINISHED = [(0, s3), (s6, N)]
GX0, GX1, GZ, GH, GD = -3.2, 1.12, 2.55, .22, .08
XL = GX1 - GX0; XC = (GX0 + GX1) / 2

# ---------- room ----------
wall = box(wall_m, (0, .15, 1.6), (7, .3, 3.2))
box(white_m, (0, -3, 3.05), (7, 6.4, .1))
box(wall_m, (-3.5, -3, 1.6), (.1, 6.4, 3.2))  # side wall closes the room on the left
cut = box(dark_m, (XC, GD / 2 - .01, GZ), (XL, GD + .02, GH)); cut.hide_render = True; cut.display_type = 'BOUNDS'
bo = wall.modifiers.new('Groove', 'BOOLEAN'); bo.operation = 'DIFFERENCE'; bo.object = cut
try: bo.solver = 'EXACT'
except TypeError: pass
G0, G1 = fr(s3, e3, .2), fr(s3, e3, .85)
for f, u in ((0, .001), (G0, .001), (G1, 1.)):
    cut.scale = (XL * u, GD + .02, GH); cut.location = (GX1 - XL * u / 2, GD / 2 - .01, GZ)
    cut.keyframe_insert('scale', frame=f); cut.keyframe_insert('location', frame=f)
grv = box(groove_m, (XC, GD + .004, GZ), (XL, .008, GH)); b3d.visible(grv, [(G0, N)])
# dust falling while the groove is cut
dust_m = plain('Dust', (.6, .58, .55), .9)
for k in range(24):
    d = b3d.smooth(b3d.prim('ico_sphere', [dust_m], subdivisions=1, radius=.006 + .004 * (k % 3), location=(0, 0, 0)))
    x = GX1 - XL * ((k * .041) % .8); t0 = G0 + (k * 3) % max(1, G1 - G0 - 10); t1 = t0 + 20
    keys(d, 'location', [(t0, (x, -.02, GZ - .1)), (t1, (x + .05 * math.sin(k), -.15 - .05 * (k % 3), GZ - 1.4))])
    b3d.visible(d, [(t0, t1)])
box(floor_m, (0, -3, -.05), (7, 6.2, .1)); box(white_m, (0, -.02, .05), (7, .03, .1)); box(white_m, (0, -.04, 2.97), (7, .08, .06))
box(rug_m, (.9, -1.6, .005), (2.6, 1.8, .01), .005)
# window with daylight
WX, WZ = -1.75, 1.35
for c, s in (((WX, -.02, WZ + .76), (1.2, .1, .06)), ((WX, -.02, WZ - .76), (1.2, .1, .06)), ((WX - .58, -.02, WZ), (.06, .1, 1.58)),
             ((WX + .58, -.02, WZ), (.06, .1, 1.58)), ((WX, -.02, WZ), (.04, .08, 1.5))):
    box(white_m, c, s, .005)
box(glass_m, (WX, .0, WZ), (1.12, .01, 1.48)); box(sky_m, (WX, .5, WZ), (1.3, .02, 1.7))
wcut = box(dark_m, (WX, .15, WZ), (1.12, .5, 1.48)); wcut.hide_render = True; wcut.display_type = 'BOUNDS'
wb = wall.modifiers.new('Win', 'BOOLEAN'); wb.operation = 'DIFFERENCE'; wb.object = wcut
box(white_m, (WX, -.1, WZ - .8), (1.4, .22, .04), .01)
# sofa
box(sofa_m, (.9, -.6, .23), (2.1, .85, .36), .08); box(sofa_m, (.9, -.22, .62), (2.1, .26, .6), .1)
box(sofa_m, (-.12, -.6, .42), (.22, .85, .46), .08); box(sofa_m, (1.92, -.6, .42), (.22, .85, .46), .08)
for x in (.45, 1.3): box(sofa_m, (x, -.55, .5), (.8, .7, .16), .07)
pic = box(frame_m, (.9, -.02, 1.55), (1.0, .03, .6), .005); art = box(art_m, (.9, -.04, 1.55), (.92, .01, .52))
for o in (pic, art): b3d.visible(o, FINISHED)

# ---------- duct on the wall (the bad way) ----------
duct = box(duct_m, (XC - .06, -.04, GZ), (XL - .12, .07, .11), .008); b3d.visible(duct, [(0, s3)])

# ---------- pipes ----------
LINES = [(.065, .03, foam_m, copper_m, .018), (.012, .025, foam_m, copper_m, .011), (-.035, .012, cable_m, None, 0), (-.07, .017, hose_m, None, 0)]
P0, P1 = fr(s4, e4, .05), fr(s4, e4, .9)
for k, (dz, r, m, core, cr) in enumerate(LINES):
    z = GZ + dz; y_in = GD / 2 + .004
    root = b3d.empty(f'Line{k}', (XC, -.6, z + .25))
    if core:
        p = cyl(m, r, XL - .65, (-.31, 0, 0), (0, R(90), 0)); p.parent = root
        c = cyl(core, cr, XL - .04, (0, 0, 0), (0, R(90), 0)); c.parent = root
    else:
        p = cyl(m, r, XL - .04, (0, 0, 0), (0, R(90), 0)); p.parent = root
    t0 = P0 + k * (P1 - P0) // 4; t1 = t0 + 16
    keys(root, 'location', [(0, (XC, -.6, z + .25)), (t0, (XC, -.6, z + .25)), (t1, (XC, y_in, z))])
    b3d.visible(root, [(t0, N)])
    st = cyl(core or m, (cr or r), .1, (GX1 - .05, -.04, z), (R(90), 0, 0)); b3d.visible(st, [(fr(s5, e5, .1), N)])

# ---------- plaster, then paint ----------
F0, F1 = fr(s5, e5, .1), fr(s5, e5, .5)
fill = box(wall_m, (GX0, GD / 2 - .005, GZ), (.001, GD, GH + .004))
for f, u in ((F0, .001), (F1, 1.)):
    fill.scale = (XL * u, GD, GH + .004); fill.location = (GX0 + XL * u / 2, GD / 2 - .005, GZ)
    fill.keyframe_insert('scale', frame=f); fill.keyframe_insert('location', frame=f)
b3d.visible(fill, [(F0, N)])
PA0, PA1 = fr(s5, e5, .6), fr(s5, e5, .92)
wall_raw([(0, 0.), (s3 - 1, 0.), (s3, 1.), (PA0, 1.), (PA1, 0.)])

# ---------- AC unit ----------
AX, AZ = 1.6, GZ + .03
ac = box(plastic_m, (AX, -.14, AZ), (1.05, .26, .32), .06)
parts = [box(dark_m, (AX, -.255, AZ - .125), (.86, .04, .035), .005), box(disp_m, (AX + .38, -.272, AZ + .04), (.05, .004, .02))]
flap = box(plastic_m, (AX, -.27, AZ - .13), (.88, .012, .05), .004); parts.append(flap)
for o in parts: o.parent = ac; o.matrix_parent_inverse = ac.matrix_world.inverted()
b3d.visible(ac, FINISHED)
keys(flap, 'rotation_euler', [(s6, (0, 0, 0)), (fr(s6, e6, .3), (R(-35), 0, 0))])

# ---------- lights ----------
b3d.light('AREA', 'Window', (WX, -.3, WZ), 120, (.85, .92, 1), 1.4, rot=(-90, 0, 0))
b3d.light('AREA', 'Room', (1.5, -3.5, 2.9), 260, (1, .9, .78), 3, rot=(60, 0, 20))
b3d.light('AREA', 'Groove', (.2, -1.2, 2.0), 25, (1, .95, .9), .8, rot=(60, 0, 0))
b3d.light('AREA', 'Bounce', (-1, -4, 1.4), 90, (.9, .93, 1), 4, rot=(80, 0, -20))

# ---------- camera: depth of field + a slight handheld drift ----------
cam, tgt = b3d.camera(30)
cam.data.dof.use_dof = True; cam.data.dof.focus_object = tgt; cam.data.dof.aperture_fstop = 3.2
b3d.shot(cam, tgt, s1, e1, (.9, -3.8, 2.2), (.75, -3.4, 2.25), (.55, 0, 2.35), lens=24)
b3d.shot(cam, tgt, s2, e2, (-.2, -2.0, 2.3), (-.7, -1.7, 2.35), (-.6, 0, 2.5), lens=24)
b3d.shot(cam, tgt, s3, e3, (1.7, -2.4, 2.4), (1.3, -2.1, 2.45), (-.3, 0, 2.5), lens=30)
b3d.shot(cam, tgt, s4, e4, (1.3, -1.35, 2.5), (1.0, -1.1, 2.52), (.6, 0, 2.55))
b3d.shot(cam, tgt, s5, e5, (1.6, -2.4, 2.4), (1.3, -2.1, 2.45), (.8, 0, 2.5))
b3d.shot(cam, tgt, s6, e6, (1.9, -2.6, 2.3), (1.6, -3.2, 2.2), (1.3, 0, 2.3))
b3d.shot(cam, tgt, s7, e7, (.2, -4.6, 1.6), (.2, -5.6, 1.6), (0, 0, 1.6), lens=24)
def fcurves(ob):
    ad = ob.animation_data; act = ad.action
    try: return list(act.fcurves)
    except AttributeError:
        out = []
        for ly in act.layers:
            for st in ly.strips: out += list(st.channelbag(ad.action_slot).fcurves)
        return out
try:
    for fc in fcurves(cam):
        if fc.data_path == 'location':
            nz = fc.modifiers.new('NOISE'); nz.scale = 25; nz.strength = .012; nz.phase = fc.array_index * 7
except Exception as ex: print('shake skipped', ex)
b3d.render(OUT, cfg.get('frames'))
