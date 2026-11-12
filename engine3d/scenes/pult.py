"""TV pulti: a remote on a coffee table aimed at a TV. The IR LED stays dark to the eye; cutaway shows the chip picking the
button's code (bits appear); a burst of long/short light pulses travels to the TV receiver, the channel number flips 7 -> 8;
a phone camera screen shows the LED glowing violet. 7 shots."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import b3d, bpy
from mathutils import Vector

cfg, OUT, S = b3d.args(); N = S[-1]; sc = b3d.setup(N, sky=(.03, .035, .08), preview=cfg.get('preview'))
(s1, e1), (s2, e2), (s3, e3), (s4, e4), (s5, e5), (s6, e6), (s7, e7) = list(zip(S[:-1], S[1:]))
R = math.radians

wall_m = b3d.mat('Wall', (.42, .5, .62), .7, bump=.03)
floor_m = b3d.mat('Floor', (.55, .38, .25), .6, bump=.05)
wood = b3d.mat('Wood', (.62, .42, .26), .5, bump=.04)
body_m = b3d.mat('Remote', (.13, .14, .17), .35)
btn_m = b3d.mat('Btn', (.55, .58, .64), .4)
red_m = b3d.mat('BtnRed', (.9, .2, .15), .35, emit=(1, .2, .1), estr=0)
led_m = b3d.mat('Led', (.25, .05, .08), .05, emit=(1, .15, .5), estr=0)
pcb_m = b3d.mat('PCB', (.1, .45, .2), .4)
chip_m = b3d.mat('Chip', (.03, .03, .04), .3)
bit_m = b3d.mat('Bits', (1, .8, .2), .4, emit=(1, .75, .15), estr=4)
pulse_m = b3d.mat('Pulse', (.9, .3, 1), .3, emit=(.75, .2, 1), estr=3)
tv_m = b3d.mat('TV', (.05, .05, .06), .3)
scr_m = b3d.mat('Screen', (.05, .1, .2), .3, emit=(.15, .35, .8), estr=.8)
num_m = b3d.mat('Num', (1, 1, 1), .4, emit=(1, 1, 1), estr=3)
rx_m = b3d.mat('Rx', (.1, .9, .3), .3, emit=(.1, 1, .3), estr=.3)
phone_m = b3d.mat('Phone', (.08, .08, .1), .25)
pscr_m = b3d.mat('PScreen', (.02, .02, .03), .3, emit=(.05, .05, .07), estr=1)
pglow_m = b3d.mat('PGlow', (.6, .2, 1), .3, emit=(.6, .15, 1), estr=3)
prem_m = b3d.mat('PRemote', (.25, .25, .3), .4, emit=(.2, .2, .25), estr=.6)

def box(m, c, s, bevel=0):
    b = b3d.prim('cube', [m], size=1, location=c); b.scale = s
    if bevel: bv = b.modifiers.new('Bv', 'BEVEL'); bv.width = bevel; bv.segments = 3
    return b
def keys(ob, attr, fv):
    for f, v in fv: setattr(ob, attr, v); ob.keyframe_insert(attr, frame=f)
def text(body, m, loc, size=.4, rot=(90, 0, 0)):
    cu = bpy.data.curves.new('T' + body, 'FONT'); cu.body = body; cu.size = size; cu.extrude = .004
    cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    ob = b3d.link(bpy.data.objects.new('T' + body, cu)); cu.materials.append(m); ob.location = loc; ob.rotation_euler = [R(a) for a in rot]
    return ob

# ---------- room ----------
box(floor_m, (0, 1, -.02), (6, 6, .04))
box(wall_m, (0, 2.9, 1.5), (6, .06, 3))
box(wood, (0, 0, .25), (1.0, .7, .5), .01)                    # coffee table, top z .5
box(wood, (0, 2.6, .3), (1.9, .45, .6), .01)                  # TV stand, top z .6
TVY = 2.5; TVZ = 1.02
box(tv_m, (0, TVY, TVZ), (1.3, .06, .78), .01)
box(tv_m, (0, TVY + .05, .63), (.3, .15, .04))
scr = box(scr_m, (0, TVY - .031, TVZ + .02), (1.2, .004, .66))
n7 = text('7', num_m, (0, TVY - .04, TVZ + .02), .45); n8 = text('8', num_m, (0, TVY - .04, TVZ + .02), .45)
RXP = Vector((.45, TVY - .035, TVZ - .36))
box(tv_m, RXP, (.06, .01, .03), .003)
rxl = b3d.smooth(b3d.prim('uv_sphere', [rx_m], radius=.008, location=RXP + Vector((0, -.008, 0))))

# ---------- remote (bottom shell, PCB, top shell with buttons) ----------
RZ = .5
bot = box(body_m, (0, 0, RZ + .007), (.055, .2, .014), .006)
pcb = box(pcb_m, (0, -.005, RZ + .015), (.045, .17, .002))
chip = box(chip_m, (0, -.03, RZ + .018), (.016, .016, .004), .001)
for k in range(6):
    box(btn_m, (-.012 + .024 * (k % 2), -.07 + .028 * (k // 2), RZ + .017), (.006, .006, .002))   # contact pads
top = b3d.empty('Top', (0, 0, 0))
ts = box(body_m, (0, 0, RZ + .021), (.055, .2, .014), .006); ts.parent = top
btns = []
for i in range(3):
    for j in range(2):
        b = b3d.prim('cylinder', [btn_m], vertices=20, radius=.0075, depth=.006, location=(-.012 + .024 * j, -.07 + .028 * i, RZ + .028)); b.parent = top
for i in range(2):
    b = b3d.prim('cylinder', [btn_m], vertices=20, radius=.006, depth=.006, location=(-.012 + .024 * i, .02, RZ + .028)); b.parent = top
chb = b3d.prim('cylinder', [red_m], vertices=24, radius=.009, depth=.007, location=(0, .05, RZ + .028)); chb.parent = top
LED = Vector((0, .103, RZ + .014))
led = b3d.smooth(b3d.prim('uv_sphere', [led_m], radius=.006, location=LED)); led.scale = (1, 1.3, 1)
# button presses: shot 1, shot 3, shot 4
PR = [s1 + int((e1 - s1) * .5), s3 + int((e3 - s3) * .35), s4 + 6, s6 + 8]
fv = [(0, (0, .05, RZ + .028))]
for p in PR: fv += [(p - 3, (0, .05, RZ + .028)), (p, (0, .05, RZ + .024)), (p + 10, (0, .05, RZ + .024)), (p + 14, (0, .05, RZ + .028))]
keys(chb, 'location', fv)
b3d.key_input(red_m, 'Emission Strength', [(0, 0)] + [x for p in PR for x in ((p - 1, 0), (p, 2), (p + 12, 2), (p + 14, 0))])
b3d.visible(top, [(0, s3), (e3, N)])
bits = '10110010'
for k, c in enumerate(bits):
    t = text(c, bit_m, (-.042 + .012 * k, -.03, RZ + .045), .014, rot=(60, 0, 0))
    b3d.visible(t, [(PR[1] + 4 + 3 * k, e3)])

# ---------- pulses: long = 1, short = 0, two bursts in shot 4 ----------
RX = RXP + Vector((0, -.02, 0)); TRAVEL = 34
d = (RX - LED).normalized()
emits = []
for burst in (s4 + 8, s4 + int((e4 - s4) * .36), s4 + int((e4 - s4) * .68)):
    for k, c in enumerate(bits):
        f0 = burst + 4 * k; emits.append((f0, c))
        p = b3d.smooth(b3d.prim('uv_sphere', [pulse_m], radius=.02, segments=16, ring_count=8, location=LED))
        p.rotation_mode = 'QUATERNION'; p.rotation_quaternion = Vector((0, 1, 0)).rotation_difference(d)
        p.scale = (1, 3.5 if c == '1' else 1.2, 1)
        keys(p, 'location', [(f0, LED), (f0 + TRAVEL, RX)])
        act = p.animation_data.action
        try: curves = act.fcurves
        except AttributeError: curves = [c for l in act.layers for st in l.strips for cb in st.channelbags for c in cb.fcurves]
        for fc in curves:
            for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
        b3d.visible(p, [(f0, f0 + TRAVEL)])
lk = [(0, 0), (s4, 0)]
for f0, c in emits: lk += [(f0, 6), (f0 + (3 if c == '1' else 1), 0)]
lk += [(s6, 0)] + [(s6 + 4 * k, 8 if k % 2 else 1) for k in range(1, max(2, (e6 - s6) // 4))] + [(e6, 0)]
b3d.key_input(led_m, 'Emission Strength', sorted(lk))
ARR = emits[7][0] + TRAVEL; ARR2 = emits[-1][0] + TRAVEL
b3d.key_input(rx_m, 'Emission Strength', [(0, .3), (emits[0][0] + TRAVEL - 1, .3), (emits[0][0] + TRAVEL, 6), (ARR2 + 2, 6), (ARR2 + 6, .3)])
SW = s5 + int((e5 - s5) * .4)
b3d.visible(n7, [(0, SW)]); b3d.visible(n8, [(SW + 3, N)])
b3d.key_input(scr_m, 'Emission Strength', [(0, .8), (SW - 1, .8), (SW + 1, 3), (SW + 5, .8)])

# ---------- phone (shot 6): stands in front of the LED, its screen shows the glow ----------
ph = b3d.empty('Phone', (0, 0, 0))
pb = box(phone_m, (0, .26, RZ + .081), (.075, .009, .16), .006); pb.parent = ph
psc = box(pscr_m, (0, .2655, RZ + .081), (.066, .002, .145)); psc.parent = ph
pr = box(prem_m, (0, .2675, RZ + .06), (.03, .001, .08)); pr.parent = ph
pg = b3d.smooth(b3d.prim('uv_sphere', [pglow_m], radius=.009, location=(0, .2685, RZ + .105))); pg.parent = ph; pg.scale = (1, .3, 1)
b3d.key_input(pglow_m, 'Emission Strength', [(0, 0), (s6, 0)] + [(s6 + 4 * k, 3.5 if k % 2 else .3) for k in range(1, max(2, (e6 - s6) // 4))] + [(e6, 0)])
b3d.visible(ph, [(s6, e6)])

# ---------- lights ----------
b3d.light('AREA', 'Key', (1.5, -1.5, 2.4), 160, (1, .93, .85), 2, rot=(50, 0, 40))
b3d.light('AREA', 'Fill', (-1.6, -1.2, 1.5), 60, (.62, .74, 1), 2, rot=(65, 0, -45))
b3d.light('POINT', 'TVGlow', (0, TVY - .5, TVZ), 15, (.4, .6, 1), .5)
b3d.light('POINT', 'Near', (.25, -.15, .75), 1.5, (1, .95, .9), .1)

# ---------- timeline ----------
cam, tgt = b3d.camera(30)
b3d.shot(cam, tgt, s1, e1, (.1, -.3, .66), (.085, -.26, .645), (-.01, .02, .5), lens=30)
b3d.shot(cam, tgt, s2, e2, (.09, .2, .56), (.075, .18, .55), (0, .1, RZ + .014), lens=40)
b3d.shot(cam, tgt, s3, e3, (.1, -.2, .66), (.08, -.17, .64), (0, -.01, RZ + .02), lens=35)
b3d.shot(cam, tgt, s4, e4, (.22, -.33, .74), (.2, -.2, .72), (.22, 1.4, .64), lens=30)
b3d.shot(cam, tgt, s5, e5, (.85, 1.35, .95), (.75, 1.5, .95), (.2, TVY, .8), lens=30)
b3d.shot(cam, tgt, s6, e6, (.08, .55, .66), (.06, .5, .64), (0, .26, RZ + .081), lens=35)
b3d.shot(cam, tgt, s7, e7, (.45, -.9, 1.0), (.75, -1.5, 1.2), (0, 1.2, .75), lens=30)
b3d.render(OUT, cfg.get('frames'))
