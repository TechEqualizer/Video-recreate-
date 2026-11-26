#!/usr/bin/env python3
"""Temp score for the animatic: 126 BPM, warm piano + pad + soft pulse, a tick on every cut.
Usage: python3 score.py out.wav DURATION CUT1,CUT2,...  (replaced by a produced track at finish)"""
import sys, wave
import numpy as np

SR = 44100
out, dur = sys.argv[1], float(sys.argv[2])
cuts = [float(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 else []
B = 60 / 126
n = int(SR * (dur + 1.5))
t = np.arange(n) / SR
mix = np.zeros(n)

def note(f, start, length, amp, harm=(1, .5, .25, .12), decay=3.0):
    i0 = int(start * SR); m = int(length * SR)
    if i0 >= n: return
    m = min(m, n - i0); tt = np.arange(m) / SR
    env = np.exp(-decay * tt) * np.minimum(1, tt / 0.004)
    sig = sum(a * np.sin(2 * np.pi * f * (k + 1) * tt) for k, a in enumerate(harm))
    mix[i0:i0 + m] += amp * env * sig

def mtof(m): return 440 * 2 ** ((m - 69) / 12)

# progression (2 bars each): Am9 - Fmaj7 - C - G/B
prog = [[57, 60, 64, 67, 71], [53, 57, 60, 64, 69], [48, 55, 60, 64, 67], [47, 55, 59, 62, 67]]
bars = int(dur / (4 * B)) + 2
for bar in range(bars):
    ch = prog[(bar // 2) % 4]
    b0 = bar * 4 * B
    # pad: slow attack sustained chord, quiet
    for m_ in ch[:4]:
        i0 = int(b0 * SR); L = int(4 * B * SR)
        if i0 >= n: break
        L = min(L, n - i0); tt = np.arange(L) / SR
        env = np.minimum(1, tt / 0.6) * np.minimum(1, (L / SR - tt) / 0.4)
        f = mtof(m_)
        mix[i0:i0 + L] += 0.035 * env * (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * f * 1.003 * tt) + 0.2 * np.sin(2 * np.pi * 2 * f * tt))
    # piano arpeggio on 8ths from bar 1
    if bar >= 1:
        pat = [0, 2, 4, 3, 1, 3, 4, 2]
        for k, idx in enumerate(pat):
            note(mtof(ch[idx] + 12), b0 + k * B / 2, 1.2, 0.07 if k % 2 == 0 else 0.05, decay=4.5)
    # bass on beat 1 and 3
    note(mtof(ch[0] - 12), b0, 1.6, 0.16, harm=(1, .3), decay=1.6)
    note(mtof(ch[0] - 12), b0 + 2 * B, 1.2, 0.11, harm=(1, .3), decay=2.0)
    # soft kick + hat from bar 2
    if bar >= 2:
        for k in range(4):
            i0 = int((b0 + k * B) * SR); L = min(int(0.25 * SR), n - i0)
            if L <= 0: continue
            tt = np.arange(L) / SR
            mix[i0:i0 + L] += 0.30 * np.exp(-18 * tt) * np.sin(2 * np.pi * (48 + 60 * np.exp(-40 * tt)) * tt)
            j0 = int((b0 + k * B + B / 2) * SR); L2 = min(int(0.05 * SR), n - j0)
            if L2 > 0:
                rng = np.random.default_rng(bar * 4 + k)
                hat = rng.standard_normal(L2); hat = np.diff(np.concatenate([[0], hat]))
                mix[j0:j0 + L2] += 0.025 * hat * np.exp(-90 * np.arange(L2) / SR)

# a soft tick on every cut, a low swell into the wedge lock and the end
for c in cuts:
    i0 = int(c * SR); L = min(int(0.03 * SR), n - i0)
    if L > 0:
        tt = np.arange(L) / SR
        mix[i0:i0 + L] += 0.05 * np.sin(2 * np.pi * 2200 * tt) * np.exp(-160 * tt)
for hit in (0.62, dur - 1.3):
    i0 = int(hit * SR); L = min(int(1.4 * SR), n - i0)
    tt = np.arange(L) / SR
    mix[i0:i0 + L] += 0.22 * np.exp(-3 * tt) * np.sin(2 * np.pi * 41 * tt)

# fade tail, stereo widen slightly, write
fade = np.ones(n); tail = int(1.5 * SR); fade[-tail:] = np.linspace(1, 0, tail)
mix *= fade
mix = mix[: int(SR * dur)]
mix /= np.max(np.abs(mix)) + 1e-9
mix *= 0.8
L = mix; R = np.roll(mix, int(0.012 * SR)) * 0.96 + mix * 0.04
st = (np.stack([L, R], 1) * 32767).astype(np.int16)
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes())
print(out)
