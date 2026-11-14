"""Batareya (radiator) with an air lock. Outside (shots 1, 5, 7): a sectional radiator under a window sill, top half
cold-blue, bottom half warm. Inside (shots 2, 3, 4, 6; front covers hidden): hot water circulating, air bubbles
collecting at the top, the pale air pocket growing, then the Mayevskiy bleed valve at the top corner lets it out."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.03, .035, .07), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))
R = math.radians
def fr(a, b, u): return int(a + (b - a) * u)

wall_m = b3d.mat('Wall', (.62, .5, .4), .6, bump=.05)
floor_m = b3d.mat('Floor', (.36, .25, .17), .6, bump=.08)
sill_m = b3d.mat('Sill', (.92, .92, .9), .3)
glass_m = b3d.mat('Glass', (.05, .08, .2), .1, emit=(.08, .14, .4), estr=1.2)
shell_m = b3d.mat('Shell', (.9, .9, .88), .35)
COLD, WARM = (.55, .72, 1.), (1., .5, .36)
top_m = b3d.mat('CoverTop', COLD, .35, emit=COLD, estr=.5)
bot_m = b3d.mat('CoverBot', WARM, .35, emit=(1, .3, .15), estr=.5)
dark_m = b3d.mat('Inner', (.1, .1, .13), .6)
hot_m = b3d.mat('HotWater', (1, .35, .1), .2, emit=(1, .3, .06), estr=2.2)
air_m = b3d.mat('Air', (.8, .9, 1), .3, emit=(.6, .8, 1), estr=.9)
bub_m = b3d.mat('Bubble', (1, 1, 1), .1, emit=(.9, .97, 1), estr=3)
flow_m = b3d.mat('Flow', (1, .85, .3), .2, emit=(1, .8, .2), estr=4)
pipe_m = b3d.mat('PipeW', (.85, .85, .83), .35)
chrome = b3d.mat('Chrome', (.85, .87, .9), .15, metal=1.0)
drop_m = b3d.mat('Drop', (.3, .65, 1), .1, emit=(.25, .6, 1), estr=2.5)
arrow_m = b3d.mat('Arrow', (1, .85, .1), .3, emit=(1, .8, .1), estr=4)

def box(m, c, s, bevel=0):
    b = b3d.prim('cube', [m], size=1, location=c); b.scale = s
    if bevel:
        bv = b.modifiers.new('Bv', 'BEVEL'); bv.width = bevel; bv.segments = 4; b3d.smooth(b)
    return b
def cyl(m, r, d, loc, rot=(0, 0, 0)): return b3d.smooth(b3d.prim('cylinder', [m], vertices=24, radius=r, depth=d, location=loc, rotation=rot))
def ball(m, r, loc=(0, 0, 0)): return b3d.smooth(b3d.prim('uv_sphere', [m], segments=12, ring_count=6, radius=r, location=loc))
def keys(ob, attr, fv):
    for f, v in fv: setattr(ob, attr, v); ob.keyframe_insert(attr, frame=f)
def lerp(a, b, u): return tuple(x + (y - x) * u for x, y in zip(a, b))

OUTSIDE = [(s1, e1), (s5, e5), (s7, N)]
NS, PITCH, ZB, ZT = 8, .2, .55, 1.85; H = ZT - ZB
XS = [(i - (NS - 1) / 2) * PITCH for i in range(NS)]

# ---------- room ----------
box(wall_m, (0, .4, 2.5), (10, .2, 7)); box(floor_m, (0, -2, -.05), (10, 6, .1))
box(sill_m, (0, .05, 2.25), (2.6, .6, .07), .02)
box(sill_m, (0, .3, 3.5), (2.3, .1, 2.4), .02); box(glass_m, (0, .26, 3.5), (2.05, .06, 2.15))
box(sill_m, (0, .22, 3.5), (.06, .06, 2.15)); box(sill_m, (0, .22, 3.5), (2.05, .06, .06))

# ---------- radiator ----------
for x in XS:
    box(shell_m, (x, .1, 1.2), (.175, .18, H + .16), .03)
    box(dark_m, (x, .005, 1.2), (.135, .02, H + .06))
    c = box(top_m, (x, -.03, 1.56), (.175, .07, .74), .03); b3d.visible(c, OUTSIDE)
    c = box(bot_m, (x, -.03, .84), (.175, .07, .74), .03); b3d.visible(c, OUTSIDE)
for z in (ZB, ZT):
    box(dark_m, (0, .0, z), (NS * PITCH - .05, .02, .13))
    cyl(pipe_m, .05, .8, (-1.15, .1, z), (0, R(90), 0))
cyl(pipe_m, .06, 3.6, (-1.55, .1, 1.8)); cyl(pipe_m, .06, 3.6, (-1.3, .22, 1.8))
# Mayevskiy valve at the top right corner
VX = XS[-1] + .12
cyl(chrome, .055, .1, (VX, .1, ZT), (0, R(90), 0))
vh = cyl(chrome, .035, .06, (VX + .07, .1, ZT), (0, R(90), 0))
slot = box(dark_m, (VX + .101, .1, ZT), (.004, .05, .012)); slot.parent = vh; slot.matrix_parent_inverse = vh.matrix_world.inverted()
keys(vh, 'rotation_euler', [(0, (0, R(90), 0)), (fr(s6, e6, .12), (0, R(90), 0)), (fr(s6, e6, .28), (R(200), R(90), 0)),
                            (fr(s6, e6, .78), (R(200), R(90), 0)), (fr(s6, e6, .9), (0, R(90), 0))])

# ---------- inside: water column and air pocket per section ----------
A0, A1 = fr(s3, e3, .25), e3 - 1                     # air collects
A2, A3 = fr(s6, e6, .28), fr(s6, e6, .72)            # air let out
def air_keys(k): return [(0, 0.), (A0 + k * 2, 0.), (A1, .42 - .02 * (k % 3)), (A2, .42 - .02 * (k % 3)), (A3, 0.), (N, 0.)]
for k, x in enumerate(XS):
    w = box(hot_m, (x, -.01, 1.2), (.115, .03, H)); a = box(air_m, (x, -.012, ZT), (.115, .03, .001))
    for f, v in air_keys(k):
        h = max(.001, v * H)
        keys(w, 'scale', [(f, (.115, .03, H - h))]); keys(w, 'location', [(f, (x, -.01, ZB + (H - h) / 2))])
        keys(a, 'scale', [(f, (.115, .03, h))]); keys(a, 'location', [(f, (x, -.012, ZT - h / 2))])
box(hot_m, (0, -.01, ZB), (NS * PITCH - .08, .03, .1))
tw = box(hot_m, (0, -.01, ZT), (NS * PITCH - .08, .03, .1)); ta = box(air_m, (0, -.014, ZT), (NS * PITCH - .08, .03, .1))
b3d.visible(ta, [(fr(A0, A1, .3), fr(A2, A3, .8))])
for z in (ZB, ZT): box(hot_m, (-1.0, -.01, z), (.5, .03, .07))

# hot water circulating (shot 2): in at the top, down every section, out at the bottom
for k in range(32):
    x = XS[k % NS]; d = ball(flow_m, .028)
    pts = [(-1.3, -.05, ZT), (x, -.05, ZT), (x, -.05, ZB), (-1.3, -.05, ZB)]
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(3)]; T = sum(seg)
    for f in range(s2, e2, 2):
        dd = (((f - s2) / 75 + k * .137) % 1) * T
        for i, L in enumerate(seg):
            if dd <= L: p = lerp(pts[i], pts[i + 1], dd / L); break
            dd -= L
        d.location = p; d.keyframe_insert('location', frame=f)
    b3d.visible(d, [(s2, e2)])
# air bubbles (shot 3): come in with the water along the bottom, rise up a section and stay at the top
for k in range(20):
    x = XS[(k * 3) % NS] + .03 * math.sin(k); b = ball(bub_m, .028 + .008 * (k % 3))
    t0 = s3 + k * 3; t1 = t0 + 22; t2 = t1 + 30
    keys(b, 'location', [(t0, (-1.25, -.05, ZB)), (t1, (x, -.05, ZB)), (t2, (x, -.05, ZT - .06 - .02 * (k % 4)))])
    b3d.visible(b, [(t0, e3)])
# air hissing out of the valve (shot 6), then a few drops of water
for k in range(16):
    b = ball(bub_m, .03)
    t0 = A2 + k * 4
    keys(b, 'location', [(t0, (VX + .1, .05, ZT)), (t0 + 22, (VX + .55 + .05 * (k % 3), -.1 - .04 * (k % 4), ZT + .12 + .07 * (k % 5)))])
    keys(b, 'scale', [(t0, (.5, .5, .5)), (t0 + 22, (1.8, 1.8, 1.8))])
    b3d.visible(b, [(t0, min(t0 + 22, A3 + 6))])
for k in range(3):
    d = ball(drop_m, .03); t0 = A3 + 4 + k * 7
    keys(d, 'location', [(t0, (VX + .1, .08, ZT - .03)), (t0 + 16, (VX + .1, .08, ZT - .9))]); b3d.visible(d, [(t0, t0 + 16)])
ar = b3d.arrow('Arr', (VX + .5, -.25, ZT + .45), (VX + .14, -.02, ZT + .08), arrow_m, .026); b3d.visible(ar, [(fr(s5, e5, .15), e5)])
# outside: after the fix the cold top warms up
for n, a, b in (('Base Color', COLD, WARM), ('Emission Color', COLD, (1, .3, .15))):
    b3d.key_input(top_m, n, [(0, a), (s7 + 6, a), (s7 + 40, b)])

# ---------- lights ----------
b3d.light('AREA', 'Key', (2.5, -4, 4), 380, (1, .93, .84), 6, rot=(50, 0, 30))
b3d.light('AREA', 'Fill', (-3, -4, 2), 170, (.62, .74, 1), 5, rot=(70, 0, -40))

# ---------- timeline ----------
cam, tgt = b3d.camera(30)
b3d.shot(cam, tgt, s1, e1, (.5, -4.2, 1.7), (.35, -3.7, 1.6), (0, 0, 1.45))
b3d.shot(cam, tgt, s2, e2, (-.5, -3.5, 1.5), (-.35, -3.1, 1.45), (-.2, 0, 1.35))
b3d.shot(cam, tgt, s3, e3, (.2, -3.3, 1.2), (.1, -2.9, 1.45), (-.1, 0, 1.35))
b3d.shot(cam, tgt, s4, e4, (.35, -2.7, 1.95), (.2, -2.4, 1.85), (0, 0, 1.5))
b3d.shot(cam, tgt, s5, e5, (1.35, -1.9, 2.1), (1.2, -1.5, 2.0), (VX - .05, 0, 1.75))
b3d.shot(cam, tgt, s6, e6, (.75, -3.0, 1.75), (.65, -2.7, 1.7), (.4, 0, 1.5))
b3d.shot(cam, tgt, s7, e7, (.3, -3.9, 1.55), (.5, -5.4, 1.95), (0, 0, 1.45))
b3d.render(OUT, cfg.get('frames'))
