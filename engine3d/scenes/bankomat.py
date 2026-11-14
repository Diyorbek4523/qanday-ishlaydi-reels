"""Bankomat: how a cash-in ATM spots a fake note. Exterior ATM (shots 1, 2, 7) and, far to the side (x = 20), the
validator inside: a belt carrying the note under three stations - size lasers, UV lamp (hidden marks glow), magnetic
head (security thread). Shot 6: a pale fake glows all over under UV, the lamp goes red and the belt sends it back."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.03, .035, .07), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))
R = math.radians
def fr(a, b, u): return int(a + (b - a) * u)

body_m = b3d.mat('Body', (.13, .2, .42), .35)
trim_m = b3d.mat('Trim', (.75, .78, .82), .25, metal=.8)
screen_m = b3d.mat('Screen', (.1, .3, .6), .2, emit=(.2, .55, 1), estr=2.5)
sign_m = b3d.mat('Sign', (1, .6, .1), .4, emit=(1, .55, .08), estr=3)
key_m = b3d.mat('Key', (.8, .82, .85), .4)
black_m = b3d.mat('Black', (.02, .02, .025), .5)
slot_m = b3d.mat('SlotGlow', (.1, .9, .3), .4, emit=(.1, 1, .3), estr=3)
floor_m = b3d.mat('Floor', (.3, .3, .34), .7, bump=.08)
wall_m = b3d.mat('Wall', (.34, .38, .5), .6, bump=.04)
in_wall = b3d.mat('InWall', (.1, .14, .22), .6)
in_base = b3d.mat('InBase', (.16, .19, .26), .5, metal=.3)
belt_m = b3d.mat('Belt', (.05, .05, .06), .8)
stripe_m = b3d.mat('Stripe', (.2, .2, .22), .8)
steel = b3d.mat('Steel', (.6, .63, .68), .3, metal=.9)
note_m = b3d.mat('Note', (.3, .68, .4), .75)
note_dk = b3d.mat('NoteDark', (.1, .36, .2), .75)
hid_m = b3d.mat('Hidden', (.3, .68, .4), .75, emit=(.9, 1, .2), estr=0)
thr_m = b3d.mat('Thread', (.12, .2, .16), .5, emit=(1, .55, .1), estr=0)
fake_m = b3d.mat('Fake', (.62, .82, .68), .75, emit=(.55, .7, 1), estr=0)
fake_dk = b3d.mat('FakeDark', (.32, .55, .4), .75)
laser_m = b3d.mat('Laser', (1, .1, .1), .3, emit=(1, .08, .05), estr=6)
uv_m = b3d.mat('UV', (.5, .2, 1), .3, emit=(.55, .15, 1), estr=5)
ray_m = b3d.mat('UVRay', (.5, .2, 1), .3, emit=(.6, .25, 1), estr=2.5)
red_m = b3d.mat('PoleN', (.9, .12, .1), .4)
blue_m = b3d.mat('PoleS', (.12, .3, .9), .4)
mag_m = b3d.mat('MagDot', (1, .6, .1), .3, emit=(1, .55, .1), estr=4)
lamps = [b3d.mat(f'Lamp{i}', (.03, .03, .03), .3, emit=(.03, .03, .03), estr=4) for i in range(3)]

def box(m, c, s, bevel=0):
    b = b3d.prim('cube', [m], size=1, location=c); b.scale = s
    if bevel:
        bv = b.modifiers.new('Bv', 'BEVEL'); bv.width = bevel; bv.segments = 4; b3d.smooth(b)
    return b
def cyl(m, r, d, loc, rot=(0, 0, 0)): return b3d.smooth(b3d.prim('cylinder', [m], vertices=24, radius=r, depth=d, location=loc, rotation=rot))
def ball(m, r, loc=(0, 0, 0)): return b3d.smooth(b3d.prim('uv_sphere', [m], segments=16, ring_count=8, radius=r, location=loc))
def keys(ob, attr, fv):
    for f, v in fv: setattr(ob, attr, v); ob.keyframe_insert(attr, frame=f)

# ---------- exterior ----------
box(floor_m, (0, -2, -.05), (12, 10, .1)); box(wall_m, (0, .95, 2.5), (12, .2, 7))
box(body_m, (0, .4, 1.3), (1.4, .8, 2.6), .06)
box(sign_m, (0, -.01, 2.38), (1.1, .04, .2), .02)
box(trim_m, (0, -.01, 1.78), (1.0, .03, .7), .02); box(screen_m, (0, -.03, 1.78), (.86, .02, .56))
for i in range(3):
    for j in range(4): box(key_m, (-.3 + .1 * i, -.02, 1.27 - .075 * j), (.08, .04, .055), .01)
box(black_m, (.3, -.01, 1.22), (.34, .03, .03)); box(slot_m, (.3, -.012, 1.27), (.34, .02, .012))
box(trim_m, (0, -.01, .86), (.96, .03, .2), .02); box(black_m, (0, -.03, .86), (.8, .02, .07))
box(slot_m, (0, -.032, .915), (.8, .02, .014)); box(slot_m, (0, -.032, .805), (.8, .02, .014))

def make_note(fake=False):
    a, d = (fake_m, fake_dk) if fake else (note_m, note_dk)
    root = b3d.empty('NoteF' if fake else 'Note')
    def part(m, c, s):
        p = box(m, c, s); p.parent = root; return p
    part(a, (0, 0, 0), (.62, .3, .012))
    for y in (-.135, .135): part(d, (0, y, .004), (.6, .012, .008))
    for x in (-.3, .3): part(d, (x, 0, .004), (.012, .28, .008))
    o = cyl(d, .085, .008, (-.14, 0, .004)); o.scale = (.8, 1, 1); o.parent = root
    part(d, (.2, .085, .004), (.12, .05, .008)); part(d, (-.26, -.1, .004), (.05, .04, .008))
    if not fake:
        for c, s in (((.2, -.02, .0045), (.13, .03, .009)), ((.2, -.08, .0045), (.09, .03, .009)), ((-.14, 0, .0045), (.05, .05, .011))):
            part(hid_m, c, s)
        part(thr_m, (.04, 0, .0045), (.016, .3, .0095))
    return root

noteE = make_note(); real = make_note(); fake = make_note(True)
keys(noteE, 'location', [(s1, (0, -1.35, .98)), (e1 - 1, (0, -.8, .88)), (s2, (0, -.72, .86)), (fr(s2, e2, .95), (0, .1, .86))])
b3d.visible(noteE, [(0, e2)])

# ---------- inside: belt and three stations ----------
X1, X2, X3, ZB = 18.8, 20.0, 21.2, 1.04
box(in_wall, (20, .75, 1.5), (9, .2, 6)); box(in_base, (20, .1, .5), (6, .95, .96), .03)
box(belt_m, (20, 0, 1.0), (5.2, .5, .06))
for i in range(26): box(stripe_m, (17.5 + i * .2, 0, 1.031), (.02, .5, .002))
for i in range(9): cyl(steel, .06, .62, (17.6 + i * .6, 0, .98), (R(90), 0, 0))
for i, x in enumerate((X1, X2, X3)):
    box(in_base, (x, .28, 1.52), (.56, .76, .12), .02); ball(lamps[i], .06, (x, -.13, 1.6))
for dx, dy in ((-.31, 0), (.31, 0), (0, -.15), (0, .15)):
    box(steel, (X1 + dx, dy, 1.43), (.06, .06, .06), .01); cyl(laser_m, .007, .37, (X1 + dx, dy, 1.22))
box(uv_m, (X2, 0, 1.44), (.46, .3, .04), .01)
for i in range(5): cyl(ray_m, .006, .36, (X2 - .2 + i * .1, .02 * (i % 2), 1.24))
b3d.light('POINT', 'UVL', (X2, -.1, 1.35), 25, (.6, .2, 1), .2)
box(steel, (X3, 0, 1.36), (.34, .3, .2), .02); box(red_m, (X3 - .07, 0, 1.22), (.1, .26, .08), .01); box(blue_m, (X3 + .11, 0, 1.22), (.1, .26, .08), .01)

a3, b3_, c3 = fr(s3, e3, .45), fr(s3, e3, .75), e3 - 1
a4 = fr(s4, e4, .4); a5 = fr(s5, e5, .4)
keys(real, 'location', [(0, (17.9, 0, ZB)), (s3, (17.9, 0, ZB)), (a3, (X1, 0, ZB)), (b3_, (X1, 0, ZB)), (c3, (19.2, 0, ZB)),
                        (s4, (19.3, 0, ZB)), (a4, (X2, 0, ZB)), (e4 - 1, (X2, 0, ZB)),
                        (s5, (20.5, 0, ZB)), (a5, (X3 - .04, 0, ZB)), (e5 - 1, (X3 - .04, 0, ZB))])
b3d.visible(real, [(s3, e5)])
b3d.key_input(hid_m, 'Emission Strength', [(0, 0.), (a4 - 6, 0.), (a4 + 4, 5.), (e4, 5.), (e4 + 1, 0.)])
b3d.key_input(thr_m, 'Emission Strength', [(0, 0.), (a5 - 4, 0.), (a5 + 6, 5.), (e5, 5.)])
for k in range(6):                       # magnetic particles jumping between thread and head
    d = ball(mag_m, .016)
    for f in range(a5, e5, 3):
        d.location = (X3 + .005 * math.sin(k), -.12 + k * .048, 1.07 + .09 * abs(math.sin(f * .35 + k * 1.3))); d.keyframe_insert('location', frame=f)
    b3d.visible(d, [(a5 + 4, e5)])

a6, b6 = fr(s6, e6, .3), fr(s6, e6, .6)
keys(fake, 'location', [(0, (19.0, 0, ZB)), (s6, (19.0, 0, ZB)), (a6, (X2, 0, ZB)), (b6, (X2, 0, ZB)), (e6 - 1, (18.75, 0, ZB))])
b3d.visible(fake, [(s6, e6)])
b3d.key_input(fake_m, 'Emission Strength', [(0, 0.), (a6 - 6, 0.), (a6 + 3, 3.2), (b6 + 2, 3.2), (b6 + 12, 0.)])

G, GR, RD = (.08, 1, .2), (.03, .03, .03), (1, .06, .04)
def lamp(i, fv):
    for n in ('Emission Color', 'Base Color'): b3d.key_input(lamps[i], n, fv)
lamp(0, [(0, GR), (b3_ - 12, GR), (b3_ - 6, G), (e7, G)])
lamp(1, [(0, GR), (a4 + 14, GR), (a4 + 20, G), (e5 - 1, G), (s6, GR), (a6 + 8, GR), (a6 + 12, RD), (e6, RD)])
lamp(2, [(0, GR), (a5 + 22, GR), (a5 + 28, G), (e5 - 1, G), (s6, GR)])
b3d.key_input(screen_m, 'Emission Color', [(0, (.2, .55, 1)), (s7 + 8, (.2, .55, 1)), (s7 + 20, (.1, 1, .3))])

# ---------- lights ----------
b3d.light('AREA', 'Key', (2.5, -4, 4.5), 420, (1, .95, .88), 6, rot=(50, 0, 30))
b3d.light('AREA', 'Fill', (-3, -4, 2), 160, (.62, .74, 1), 5, rot=(70, 0, -40))
b3d.light('AREA', 'InKey', (21, -3.5, 4.5), 420, (1, .96, .9), 6, rot=(45, 0, 15))
b3d.light('AREA', 'InFill', (17.5, -3, 2.2), 150, (.62, .74, 1), 5, rot=(70, 0, -40))

# ---------- timeline ----------
cam, tgt = b3d.camera(30)
b3d.shot(cam, tgt, s1, e1, (.5, -4.0, 1.7), (.35, -3.5, 1.6), (0, 0, 1.45))
b3d.shot(cam, tgt, s2, e2, (.55, -1.7, 1.75), (.4, -1.4, 1.65), (0, -.25, .9))
b3d.shot(cam, tgt, s3, e3, (18.4, -2.7, 2.3), (18.7, -2.3, 2.15), (X1, 0, 1.3))
b3d.shot(cam, tgt, s4, e4, (19.6, -2.3, 2.2), (19.9, -1.8, 2.05), (X2, 0, 1.3))
b3d.shot(cam, tgt, s5, e5, (21.6, -2.3, 2.2), (21.3, -1.8, 2.05), (X3, 0, 1.3))
b3d.shot(cam, tgt, s6, e6, (19.5, -2.9, 2.35), (19.4, -2.6, 2.25), (19.45, 0, 1.3))
b3d.shot(cam, tgt, s7, e7, (.3, -3.6, 1.6), (.6, -4.9, 1.9), (0, 0, 1.45))
b3d.render(OUT, cfg.get('frames'))
