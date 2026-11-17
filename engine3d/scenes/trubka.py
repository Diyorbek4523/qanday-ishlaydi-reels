"""Air-conditioner pipe pre-install before renovation (client sample for a split-system installer).
Shots 1-2: finished room, AC with an ugly white cable duct running across the wall (the bad way).
Shot 3: bare plaster wall, a groove (shtroba) is cut from the corner to the AC spot.
Shot 4: two copper pipes in insulation, the power cable and the drain hose drop into the groove one by one.
Shot 5: the groove is plastered over and the wall painted; only the pipe ends stick out where the AC will hang.
Shots 6-7: AC on a clean wall, cool air, camera pulls back over the room."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.03, .035, .07), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))
R = math.radians
def fr(a, b, u): return int(a + (b - a) * u)

PAINT, RAW = (.86, .78, .66), (.55, .54, .52)
wall_m = b3d.mat('Wall', PAINT, .7, bump=.03)
floor_m = b3d.mat('Floor', (.42, .28, .17), .5, bump=.06)
white_m = b3d.mat('White', (.93, .93, .92), .3)
glass_m = b3d.mat('Glass', (.05, .1, .22), .1, emit=(.1, .18, .45), estr=1.0)
dark_m = b3d.mat('Dark', (.06, .06, .07), .5)
groove_m = b3d.mat('Groove', (.32, .3, .29), .9, bump=.1)
copper_m = b3d.mat('Copper', (.85, .45, .25), .25, metal=1.0, emit=(1, .5, .2), estr=0)
foam_m = b3d.mat('Foam', (.12, .12, .13), .8, emit=(1, .8, .2), estr=0)
cable_m = b3d.mat('Cable', (.75, .75, .75), .5, emit=(1, .8, .2), estr=0)
hose_m = b3d.mat('Hose', (.92, .92, .95), .4, emit=(1, .8, .2), estr=0)
duct_m = b3d.mat('Duct', (.97, .97, .97), .25, emit=(1, .08, .04), estr=0)
air_m = b3d.mat('Air', (.5, .8, 1), .2, emit=(.35, .7, 1), estr=1.5)
leaf_m = b3d.mat('Leaf', (.18, .45, .2), .6, bump=.1); pot_m = b3d.mat('Pot', (.75, .4, .25), .5)
sofa_m = b3d.mat('Sofa', (.35, .42, .55), .8, bump=.05)
arrow_m = b3d.mat('Arrow', (1, .85, .1), .3, emit=(1, .8, .1), estr=4)

def box(m, c, s, bevel=0):
    b = b3d.prim('cube', [m], size=1, location=c); b.scale = s
    if bevel:
        bv = b.modifiers.new('Bv', 'BEVEL'); bv.width = bevel; bv.segments = 4; b3d.smooth(b)
    return b
def cyl(m, r, d, loc, rot=(0, 0, 0), v=24): return b3d.smooth(b3d.prim('cylinder', [m], vertices=v, radius=r, depth=d, location=loc, rotation=rot))
def ball(m, r, loc=(0, 0, 0)): return b3d.smooth(b3d.prim('uv_sphere', [m], segments=16, ring_count=8, radius=r, location=loc))
def keys(ob, attr, fv):
    for f, v in fv: setattr(ob, attr, v); ob.keyframe_insert(attr, frame=f)

AC_SHOTS = [(0, s3), (s6, N)]
GX0, GX1, GZ, GH, GD = -3.2, 1.12, 2.55, .22, .08     # groove: x range, centre height, height, depth
XL = GX1 - GX0; XC = (GX0 + GX1) / 2

# ---------- room ----------
wall = box(wall_m, (0, .15, 1.6), (7, .3, 3.2))
box(b3d.mat('Ceil', (.9, .9, .9), .6, emit=(1, .97, .93), estr=.35), (0, -3, 3.05), (7, 6.4, .1))  # ceiling
cut = box(dark_m, (XC, GD / 2 - .01, GZ), (XL, GD + .02, GH)); cut.hide_render = True; cut.display_type = 'BOUNDS'
bo = wall.modifiers.new('Groove', 'BOOLEAN'); bo.operation = 'DIFFERENCE'; bo.object = cut
try: bo.solver = 'EXACT'
except TypeError: pass
# the groove is cut right to left during shot 3 (before that it does not exist)
G0, G1 = fr(s3, e3, .2), fr(s3, e3, .85)
for f, u in ((0, .001), (G0, .001), (G1, 1.)):
    cut.scale = (XL * u, GD + .02, GH); cut.location = (GX1 - XL * u / 2, GD / 2 - .01, GZ)
    cut.keyframe_insert('scale', frame=f); cut.keyframe_insert('location', frame=f)
grv = box(groove_m, (XC, GD + .004, GZ), (XL, .008, GH))  # rough back of the groove
b3d.visible(grv, [(G0, N)])
box(floor_m, (0, -3, -.05), (7, 6.2, .1)); box(white_m, (0, -.02, .06), (7, .04, .12))
box(white_m, (0, -.03, 2.96), (7, .08, .08))
# window, plant, sofa
box(white_m, (-1.75, -.02, 1.25), (1.15, .06, 1.5), .02); box(glass_m, (-1.75, -.05, 1.25), (1.0, .02, 1.35))
box(white_m, (-1.75, -.06, 1.25), (.04, .02, 1.35)); box(white_m, (-1.75, -.12, .5), (1.3, .2, .05), .01)
cyl(pot_m, .17, .35, (-2.75, -.6, .17)); [ball(leaf_m, .2 - .03 * k, (-2.75 + .09 * math.sin(k * 2), -.6 + .08 * math.cos(k * 2), .45 + .15 * k)) for k in range(5)]
box(sofa_m, (.9, -.55, .25), (2.0, .8, .4), .06); box(sofa_m, (.9, -.2, .6), (2.0, .25, .6), .06)
box(sofa_m, (-.05, -.55, .45), (.2, .8, .5), .06); box(sofa_m, (1.85, -.55, .45), (.2, .8, .5), .06)

# ---------- the bad way: white duct on the wall ----------
duct = box(duct_m, (XC - .06, -.04, GZ), (XL - .12, .08, .13), .01); b3d.visible(duct, [(0, s3)])
b3d.key_input(duct_m, 'Emission Strength', [(s2, 0.), (fr(s2, e2, .3), 1.2), (fr(s2, e2, .5), .2), (fr(s2, e2, .7), 1.2), (e2, .3)])

# ---------- pipes in the groove ----------
# (z offset, radius, material, label) top to bottom: thick gas pipe, thin liquid pipe (both copper in black foam), cable, drain hose
LINES = [(.065, .03, foam_m, copper_m, .018), (.012, .025, foam_m, copper_m, .011), (-.035, .012, cable_m, None, 0), (-.07, .017, hose_m, None, 0)]
P0, P1 = fr(s4, e4, .05), fr(s4, e4, .9)
for k, (dz, r, m, core, cr) in enumerate(LINES):
    z = GZ + dz; y_in = GD / 2 + .004
    root = b3d.empty(f'Line{k}', (XC, -.6, z + .25))
    if core:  # copper pipe, insulation stops short so the copper shows near the AC end
        p = cyl(m, r, XL - .65, (-.31, 0, 0), (0, R(90), 0)); p.parent = root
        c = cyl(core, cr, XL - .04, (0, 0, 0), (0, R(90), 0)); c.parent = root
    else:
        p = cyl(m, r, XL - .04, (0, 0, 0), (0, R(90), 0)); p.parent = root
    t0 = P0 + k * (P1 - P0) // 4; t1 = t0 + 14
    keys(root, 'location', [(0, (XC, -.6, z + .25)), (t0, (XC, -.6, z + .25)), (t1, (XC, y_in, z))])
    b3d.visible(root, [(t0, N)])
    # stubs out of the wall at the AC end (seen after plastering)
    st = cyl(core or m, (cr or r), .1, (GX1 - .05, -.04, z), (R(90), 0, 0)); b3d.visible(st, [(fr(s5, e5, .1), N)])
# glow each line as it lands (one shared timing per material)
b3d.key_input(foam_m, 'Emission Strength', [(0, 0.), (P0 + 14, 0.), (P0 + 18, .6), (P0 + 34, .6), (P0 + 46, 0.)])
b3d.key_input(cable_m, 'Emission Strength', [(0, 0.), (P0 + 2 * (P1 - P0) // 4 + 14, 0.), (P0 + 2 * (P1 - P0) // 4 + 18, .7), (P0 + 2 * (P1 - P0) // 4 + 30, 0.)])
b3d.key_input(hose_m, 'Emission Strength', [(0, 0.), (P0 + 3 * (P1 - P0) // 4 + 14, 0.), (P0 + 3 * (P1 - P0) // 4 + 18, .7), (P0 + 3 * (P1 - P0) // 4 + 30, 0.)])

# ---------- plaster over the groove, then paint ----------
F0, F1 = fr(s5, e5, .1), fr(s5, e5, .5)
fill = box(wall_m, (GX0, GD / 2 - .005, GZ), (.001, GD, GH + .004))
for f, u in ((F0, .001), (F1, 1.)):
    fill.scale = (XL * u, GD, GH + .004); fill.location = (GX0 + XL * u / 2, GD / 2 - .005, GZ)
    fill.keyframe_insert('scale', frame=f); fill.keyframe_insert('location', frame=f)
b3d.visible(fill, [(F0, N)])
PA0, PA1 = fr(s5, e5, .6), fr(s5, e5, .92)
for n in ('Base Color',):
    b3d.key_input(wall_m, n, [(0, PAINT), (s3 - 1, PAINT), (s3, RAW), (PA0, RAW), (PA1, PAINT)])
ar = b3d.arrow('Arr', (GX1 + .45, -.6, GZ + .45), (GX1 + .02, -.12, GZ + .05), arrow_m, .02); b3d.visible(ar, [(fr(s5, e5, .7), e5)])

# ---------- the AC unit ----------
AX, AZ = 1.6, GZ + .03
ac = box(white_m, (AX, -.14, AZ), (1.05, .26, .34), .05)
for o in (box(dark_m, (AX, -.27, AZ - .13), (.8, .02, .04)), box(glass_m, (AX + .38, -.275, AZ + .05), (.06, .01, .03))):
    o.parent = ac; o.matrix_parent_inverse = ac.matrix_world.inverted()
b3d.visible(ac, AC_SHOTS)
# cool air: small glowing puffs drifting down and out of the slot
for k in range(40):
    b = ball(air_m, .015); t0 = s6 + (k * 7) % max(1, (N - s6 - 30)); t1 = t0 + 40
    x = AX - .35 + .7 * ((k * .37) % 1)
    keys(b, 'location', [(t0, (x, -.3, AZ - .15)), (t1, (x + .1 * math.sin(k), -1.2 - .2 * (k % 3), AZ - .9 - .1 * (k % 4)))])
    keys(b, 'scale', [(t0, (.6, .6, .6)), (t1, (1.6, 1.6, 1.6))])
    b3d.visible(b, [(t0, t1)])

# ---------- lights ----------
b3d.light('AREA', 'Key', (2.5, -4, 2.9), 160, (1, .94, .86), 6, rot=(55, 0, 30))
b3d.light('AREA', 'Fill', (-3, -4, 2), 70, (.65, .76, 1), 5, rot=(70, 0, -40))
b3d.light('POINT', 'Groove', (.3, -1.6, 2.3), 12, (1, .95, .9), .5)

# ---------- timeline ----------
cam, tgt = b3d.camera(30)
b3d.shot(cam, tgt, s1, e1, (.9, -3.8, 2.2), (.75, -3.4, 2.25), (.55, 0, 2.35), lens=24)
b3d.shot(cam, tgt, s2, e2, (-.2, -2.0, 2.3), (-.7, -1.7, 2.35), (-.6, 0, 2.5), lens=24)
b3d.shot(cam, tgt, s3, e3, (1.7, -2.4, 2.4), (1.3, -2.1, 2.45), (-.3, 0, 2.5), lens=30)
b3d.shot(cam, tgt, s4, e4, (1.3, -1.35, 2.5), (1.0, -1.1, 2.52), (.6, 0, 2.55))
b3d.shot(cam, tgt, s5, e5, (1.6, -2.4, 2.4), (1.3, -2.1, 2.45), (.8, 0, 2.5))
b3d.shot(cam, tgt, s6, e6, (1.9, -2.6, 2.3), (1.6, -3.2, 2.2), (1.3, 0, 2.3))
b3d.shot(cam, tgt, s7, e7, (.2, -4.6, 1.6), (.2, -5.6, 1.6), (0, 0, 1.6), lens=24)
b3d.render(OUT, cfg.get('frames'))
