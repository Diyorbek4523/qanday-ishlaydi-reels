#!/usr/bin/env python3
"""Render a 3D "Qanday ishlaydi?" reel: ElevenLabs voice -> shot timing -> Blender (engine3d/scenes/<scene>.py) -> word-by-word captions.

    python engine3d/make3d.py scripts/NNN-slug.json out/NNN-slug.mp4 [--preview]

Script: {"title", "scene": "<scenes/*.py name>", "key", "voice": {..., "settings": {...}}, "scenes": [{"dur", "say", "text"?}]}
"say" may carry ElevenLabs v4 tags ([curious], [excited], [whispers] ...); they steer the read and are left out of the captions.
Scene 1 "text" is the hook title on top; the last scene's "text" is the end card (its words are not captioned).
--preview renders one half-size still from the middle of every shot into out/<name>_preview.png instead of the video.
"""
import json, os, re, shutil, subprocess, sys, wave
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'engine'))
import reel
from PIL import Image

BLENDER = os.environ.get('BLENDER', r'C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe')
FPS = 30; YEL = r'{\c&H33CCFF&}'  # ASS colours are BGR: accent (255, 204, 51)

def words(meta):
    """(word, start, end) from the ElevenLabs character alignment, skipping [tags]."""
    al = meta['alignment']; out, cur, t0, t1, tag = [], '', 0, 0, False
    for c, a, b in zip(al['characters'], al['character_start_times_seconds'], al['character_end_times_seconds']):
        if c == '[': tag = True; continue
        if tag: tag = c != ']'; continue
        if c.isspace():
            if cur: out.append((cur, t0, t1)); cur = ''
            continue
        if not cur: t0 = a
        cur += c; t1 = b
    if cur: out.append((cur, t0, t1))
    return out

def ts(t): t = max(0, t); return f'{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}'
def styled(s): return re.sub(r'\*([^*]+)\*', lambda m: YEL + m.group(1) + r'{\c&HFFFFFF&}', s).replace('|', r'\N')

def captions(ws, starts, S, path):
    font = 'Inter Black'
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{font},84,&H00FFFFFF,&H00FFFFFF,&H00141414,&H96000000,0,0,0,0,100,100,0,0,1,8,4,2,50,50,470,1
Style: Hook,{font},88,&H00FFFFFF,&H00FFFFFF,&H00141414,&H96000000,0,0,0,0,100,100,0,0,1,8,4,8,60,60,210,1
Style: End,{font},96,&H00FFFFFF,&H00FFFFFF,&H00141414,&H96000000,0,0,0,0,100,100,0,0,1,8,4,5,60,60,0,1
Style: Tag,{font},40,&H00D0D0D0,&H00FFFFFF,&H00141414,&H96000000,0,0,0,0,100,100,2,0,1,4,2,8,60,60,110,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev, sc = [], S['scenes']; end_t = starts[-2]
    ev.append(f'Dialogue: 1,{ts(0)},{ts(starts[-1])},Tag,,0,0,0,,QANDAY ISHLAYDI?')
    if sc[0].get('text'): ev.append(f'Dialogue: 1,{ts(0)},{ts(starts[1])},Hook,,0,0,0,,{{\\fad(120,0)}}{styled(sc[0]["text"])}')
    if sc[-1].get('text'): ev.append(f'Dialogue: 1,{ts(end_t)},{ts(starts[-1])},End,,0,0,0,,{{\\fad(150,0)}}{styled(sc[-1]["text"])}\\N{{\\fs44\\c&HD0D0D0&}}@qanday_ishlaydi.uz')
    ws = [(w.upper(), a + reel.LEAD, b + reel.LEAD) for w, a, b in ws if a + reel.LEAD < end_t - .05]
    chunks, cur = [], []
    for w in ws:  # 1-3 words, at most ~16 letters per chunk (fits one line), break after punctuation
        if cur and sum(len(x[0]) + 1 for x in cur) + len(w[0]) > 16: chunks.append(cur); cur = []
        cur.append(w)
        if len(cur) == 3 or w[0][-1] in '.,!?:;': chunks.append(cur); cur = []
    if cur: chunks.append(cur)
    for ci, ch in enumerate(chunks):
        c_end = min(chunks[ci + 1][0][1] if ci + 1 < len(chunks) else ch[-1][2] + .4, end_t)
        for wi, (w, a, b) in enumerate(ch):
            e = ch[wi + 1][1] if wi + 1 < len(ch) else c_end
            txt = ' '.join((YEL + r'{\fscx112\fscy112}' + x + r'{\r}') if j == wi else x for j, (x, _, _) in enumerate(ch))
            ev.append(f'Dialogue: 0,{ts(a)},{ts(e)},Cap,,0,0,0,,{txt}')
    open(path, 'w', encoding='utf-8').write(head + '\n'.join(ev) + '\n')

def main(script_path, out, preview=False):
    S = json.load(open(script_path, encoding='utf-8')); scenes = S['scenes']; base = os.path.splitext(os.path.abspath(script_path))[0]
    vo, marks, vend = reel.voice_take(S, base); starts = reel.fit_scenes(scenes, marks, vend); dur = float(starts[-1])
    work = os.path.abspath(out.rsplit('.', 1)[0] + '_work'); os.makedirs(work, exist_ok=True)
    cfg = {'starts': [float(x) for x in starts], 'preview': preview}
    if preview: cfg['frames'] = [int((a + b) / 2 * FPS) for a, b in zip(starts[:-1], starts[1:])]
    json.dump(cfg, open(os.path.join(work, 'cfg.json'), 'w'))
    scene_py = os.path.join(HERE, 'scenes', S['scene'] + '.py')
    with open(os.path.join(work, 'blender.log'), 'w') as lg:
        r = subprocess.run([BLENDER, '-b', '--factory-startup', '--python-exit-code', '1', '--python', scene_py, '--', os.path.join(work, 'cfg.json'), work], stdout=lg, stderr=subprocess.STDOUT)
    if r.returncode: sys.exit(f'Blender failed, see {work}\\blender.log')
    if preview:
        ims = [Image.open(os.path.join(work, f'p_{f:04d}.png')).convert('RGB').resize((270, 480)) for f in cfg['frames']]
        sheet = Image.new('RGB', (270 * len(ims), 480))
        for i, im in enumerate(ims): sheet.paste(im, (270 * i, 0))
        p = out.rsplit('.', 1)[0] + '_preview.png'; sheet.save(p); print(p, round(dur, 2), 's'); return
    pcm, sr = reel.music(dur, list(starts[1:-1]), S.get('key', 'A'))
    pcm = (reel.mix_voice(pcm / 32767, vo, sr) * 32767).astype(np.int16)
    with wave.open(os.path.join(work, 'audio.wav'), 'wb') as w_: w_.setnchannels(1); w_.setsampwidth(2); w_.setframerate(sr); w_.writeframes(pcm.tobytes())
    captions(words(json.load(open(base + '.voice.json', encoding='utf-8'))), starts, S, os.path.join(work, 'caps.ass'))
    fonts = os.path.join(work, 'fonts'); os.makedirs(fonts, exist_ok=True); shutil.copy(os.path.join(reel.FD, 'Inter-Black.otf'), fonts)
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-framerate', str(FPS), '-i', 'f_%04d.png', '-i', 'audio.wav', '-vf', 'subtitles=caps.ass:fontsdir=fonts',
                    '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '44100',
                    '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', os.path.abspath(out)], cwd=work, check=True)
    shutil.rmtree(work); print(out, round(dur, 2), 's')

if __name__ == '__main__': main(*sys.argv[1:3], preview='--preview' in sys.argv)
