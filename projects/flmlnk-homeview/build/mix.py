#!/usr/bin/env python3
"""Mix the produced score + designed SFX onto a picture-locked render.

Usage: python3 mix.py VIDEO CUTS_JSON OUT [--music-offset 0.023]
- music is trimmed by --music-offset so its beat grid lines up with the cuts
- whoosh leads (0.15 s pre-lap) into the shots with big camera moves
- tap lands on the wedge lock and on the 'Backed' title lighting up
- fades the music over the last 0.6 s, loudness-normalised to -14 LUFS (social)
"""
import json, subprocess, sys

video, cuts_json, out = sys.argv[1:4]
offset = float(sys.argv[sys.argv.index('--music-offset') + 1]) if '--music-offset' in sys.argv else 0.023
A = 'projects/flmlnk-homeview/audio/'
d = json.load(open(cuts_json)); cuts = d['cuts']; dur = d.get('duration', 30)
B = 60 / 126
# shot starts by beat index in v8 (see v8.html SHOTS): Stack 7, Wall 15, Handoff 43, Carousel 49; Tablet 29 (+0.95 s lit), End 60
whoosh = [7 * B, 15 * B, 43 * B, 49 * B]
taps = [0.62, 29 * B + 0.95, 60 * B + 0.25]
inputs = ['-i', video, '-ss', f'{offset}', '-i', A + 'music_v1.mp3']
filters, labels = [], []
filters.append(f"[1:a]atrim=0:{dur},afade=t=out:st={dur - 0.6}:d=0.6,volume=1.0[mus]")
n = 2
for i, t in enumerate(whoosh):
    inputs += ['-i', A + 'sfx_whoosh.mp3']; ms = int(max(0, t - 0.15) * 1000)
    filters.append(f"[{n}:a]volume=0.55,adelay={ms}|{ms}[w{i}]"); labels.append(f"[w{i}]"); n += 1
for i, t in enumerate(taps):
    inputs += ['-i', A + 'sfx_tap.mp3']; ms = int(t * 1000)
    filters.append(f"[{n}:a]volume=0.7,adelay={ms}|{ms}[t{i}]"); labels.append(f"[t{i}]"); n += 1
filters.append(f"[mus]{''.join(labels)}amix=inputs={1 + len(labels)}:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=9[a]")
filters.append("[0:v]noise=alls=3:allf=t,format=yuv420p[v]")
cmd = ['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', ';'.join(filters), '-map', '[v]', '-map', '[a]',
       '-c:v', 'libx264', '-crf', '17', '-maxrate', '35M', '-bufsize', '70M', '-preset', 'medium', '-g', '30', '-r', '60',
       '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-t', f'{dur}', '-movflags', '+faststart', out]
subprocess.run(cmd, check=True)
print(out)
