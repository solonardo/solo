"""Bande-son originale du spot Beaufort (30 s, 120 BPM) : musique + sound design.

Tout est synthétisé (numpy seul), donc libre de droits. Les repères temporels
sont alignés sur la timeline de index.html.
    python3 audio.py out/soundtrack.wav
"""
import sys, wave
import numpy as np

SR = 48000
DUR = 30.0
N = int(SR * DUR)
rng = np.random.default_rng(2026)
BEAT = 0.5  # 120 BPM

mus = np.zeros((N, 2))   # musique
sfx = np.zeros((N, 2))   # bruitages
send = np.zeros((N, 2))  # départ réverbération


def note(n):  # n = numéro MIDI
    return 440.0 * 2 ** ((n - 69) / 12)


def add(buf, t0, sig, gain=1.0, pan=0.0, rev=0.0):
    i = int(t0 * SR)
    if i >= N or i + len(sig) <= 0:
        return
    if i < 0:
        sig, i = sig[-i:], 0
    sig = sig[: N - i]
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[i:i + len(sig), 0] += sig * gain * l * 1.414
    buf[i:i + len(sig), 1] += sig * gain * r * 1.414
    if rev:
        send[i:i + len(sig), 0] += sig * gain * rev * l
        send[i:i + len(sig), 1] += sig * gain * rev * r


def tt(d):
    return np.arange(int(d * SR)) / SR


def fft_filter(x, lo=None, hi=None):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    m = np.ones_like(f)
    if lo:
        m *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4)
    if hi:
        m *= 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(X * m, len(x))


def noise(d):
    return rng.standard_normal(int(d * SR))


def adsr(n, a, d_, s, r, total):
    t = np.arange(n) / SR
    env = np.where(t < a, t / max(a, 1e-4), s + (1 - s) * np.exp(-(t - a) / max(d_, 1e-4)))
    rel = np.clip((total - t) / r, 0, 1)
    return env * rel


# ------------------------------------------------------------------ instruments
def pad(freqs, d, bright=1.0):
    t = tt(d)
    out = np.zeros_like(t)
    for f in freqs:
        for det in (-0.006, 0, 0.0065):
            ph = rng.random() * 6.28
            for h in range(1, 10):
                amp = (1 / h) * np.exp(-h / (2.2 * bright))
                out += amp * np.sin(2 * np.pi * f * (1 + det) * h * t + ph * h)
    env = np.clip(t / 1.2, 0, 1) * np.clip((d - t) / 1.0, 0, 1)
    return out * env / (len(freqs) * 3)


def pluck(f, d=0.6):
    t = tt(d)
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 4.01 * t) * np.exp(-t * 30) + 0.2 * np.sin(2 * np.pi * f * 2 * t)
    return s * np.exp(-t * 7) * np.clip(t / 0.003, 0, 1)


def bass(f, d):
    t = tt(d)
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2 * t)
    s = np.tanh(s * 1.6)
    return s * np.clip(t / 0.006, 0, 1) * np.exp(-t * 3) * np.clip((d - t) / 0.03, 0, 1)


def kick(g=1.0):
    t = tt(0.45)
    f = 45 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t * 7.5) + 0.25 * fft_filter(noise(0.45), 1500) * np.exp(-t * 200)
    return np.tanh(s * 1.4) * g


def clap():
    t = tt(0.3)
    n = fft_filter(noise(0.3), 900, 6000)
    env = sum(np.exp(-np.maximum(t - o, 0) * 120) * (t >= o) for o in (0, 0.011, 0.022)) + 0.6 * np.exp(-t * 18)
    return n * env * 0.35


def hat(open_=False):
    d = 0.25 if open_ else 0.06
    t = tt(d)
    return fft_filter(noise(d), 7000) * np.exp(-t * (14 if open_ else 70)) * 0.25


def shaker():
    t = tt(0.07)
    return fft_filter(noise(0.07), 5000, 12000) * np.sin(np.pi * t / 0.07) * 0.12


def bell(f, d=2.5):
    t = tt(d)
    s = sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t * k) for m, a, k in ((1, 1, 1.6), (2.76, .5, 3), (5.4, .25, 5), (8.93, .12, 8)))
    return s * np.clip(t / 0.002, 0, 1)


# ------------------------------------------------------------------ harmonie
# accords (MIDI) : La m9, Fa maj7, Do maj7, Sol 6
CH = {
    'Am': [57, 60, 64, 67, 71], 'F': [53, 57, 60, 64, 67], 'C': [48, 55, 59, 62, 64], 'G': [55, 59, 62, 64, 69],
    'Cmaj9': [48, 55, 59, 62, 64, 71],
}
ROOT = {'Am': 45, 'F': 41, 'C': 36, 'G': 43, 'Cmaj9': 36}
PROG = [(0, 4, 'Am'), (4, 8, 'F'), (8, 10, 'C'), (10, 12, 'G'), (12, 16, 'Am'), (16, 20, 'F'), (20, 22, 'C'), (22, 24, 'G'),
        (24, 26, 'Am'), (26, 27, 'F'), (27, 28, 'G'), (28, 30, 'Cmaj9')]

for a, b, c in PROG:
    d = b - a + 0.8
    g = 0.22 if a < 6 else 0.16
    if 11.0 <= a < 12:
        g = 0.08
    add(mus, a, pad([note(n) for n in CH[c]], d, bright=0.8 if a < 6 else 1.2), g, -0.15, rev=0.5)
    add(mus, a, pad([note(n + 12) for n in CH[c][2:]], d, bright=1.5), g * 0.35, 0.3, rev=0.7)

# drone sub d'intro
t = tt(6.2)
add(mus, 0, np.sin(2 * np.pi * 55 * t) * np.clip(t / 3, 0, 1) * np.clip((6.2 - t) / .4, 0, 1), 0.18)


def chord_at(x):
    for a, b, c in PROG:
        if a <= x < b:
            return c
    return 'Cmaj9'


# ------------------------------------------------------------------ rythmique
def grid(a, b, step):
    x = a
    while x < b - 1e-6:
        yield round(x, 4)
        x += step

# 6-11 : demi-temps
for x in grid(6.0, 11.0, 1.0):
    add(mus, x, kick(0.75), 0.6)
for x in grid(6.5, 11.0, 1.0):
    add(mus, x, hat(), 0.5, 0.3)
for x in grid(6.0, 11.0, 0.25):
    c = chord_at(x)
    i = int(round((x - 6) / 0.25))
    if i % 16 in (0, 3, 6, 10, 12):
        add(mus, x, pluck(note(CH[c][(i // 2) % len(CH[c])] + 12)), 0.12, -0.4 + 0.8 * ((i % 3) / 2), rev=0.6)
for x in grid(6.0, 11.0, 2.0):
    add(mus, x, bass(note(ROOT[chord_at(x)]), 1.9), 0.22)

# 12-28 : groove complet
for x in grid(12.0, 28.0, BEAT):
    add(mus, x, kick(), 0.85)
for x in grid(12.5, 28.0, 1.0):
    add(mus, x, clap(), 0.7, 0.05, rev=0.25)
for x in grid(12.25, 28.0, BEAT):
    add(mus, x, hat(open_=(int((x - 12) * 2) % 4 == 3)), 0.55, 0.35)
for x in grid(12.0, 28.0, 0.125):
    i = int(round((x - 12) / 0.125))
    add(mus, x, shaker(), 0.9 if i % 4 == 2 else 0.5, -0.45)
for x in grid(12.0, 28.0, 0.25):
    i = int(round((x - 12) / 0.25)) % 16
    if i in (2, 6, 7, 10, 14):
        c = chord_at(x)
        add(mus, x, bass(note(ROOT[c] + (12 if i == 7 else 0)), 0.22), 0.3)
    if i in (0, 3, 6, 8, 10, 13):
        c = chord_at(x)
        add(mus, x, pluck(note(CH[c][(i * 3 + int(x)) % len(CH[c])] + 12)), 0.13, -0.5 + (i % 5) / 4, rev=0.55)
# percussions afro (congas synthétiques)
for x in grid(12.0, 28.0, 0.25):
    i = int(round((x - 12) / 0.25)) % 16
    if i in (3, 5, 11, 13, 15):
        t = tt(0.18)
        f = 210 if i in (3, 11) else 290
        add(mus, x, np.sin(2 * np.pi * f * t * (1 + 0.3 * np.exp(-t * 40))) * np.exp(-t * 22), 0.16, 0.4)

# sidechain : la musique « respire » autour des kicks
env = np.ones(N)
for x in list(grid(12.0, 28.0, BEAT)) + list(grid(6.0, 11.0, 1.0)):
    i = int(x * SR)
    t = tt(0.3)
    seg_ = 1 - 0.55 * np.exp(-t * 14)
    env[i:i + len(seg_)] = np.minimum(env[i:i + len(seg_)], seg_[: N - i])

# ------------------------------------------------------------------ sound design
def riser(d, f0=300, f1=4000):
    t = tt(d)
    n = noise(d)
    out = np.zeros_like(t)
    k = 8
    for j in range(k):  # balayage par blocs filtrés
        a, b = int(j * len(t) / k), int((j + 1) * len(t) / k)
        fc = f0 * (f1 / f0) ** (j / k)
        out[a:b] = fft_filter(n, fc * .6, fc * 2)[a:b]
    sw = np.sin(2 * np.pi * np.cumsum(200 + 1200 * (t / d) ** 2) / SR) * 0.15
    return (out * 0.5 + sw) * (t / d) ** 2


def whoosh(d=0.45):
    t = tt(d)
    n = fft_filter(noise(d), 400, 5000)
    return n * np.sin(np.pi * t / d) ** 2 * 0.6


def boom(d=2.0):
    t = tt(d)
    f = 38 + 60 * np.exp(-t * 6)
    return np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2) * 2) * 0.9


def tink(f, d=0.6):
    t = tt(d)
    return sum(a * np.sin(2 * np.pi * f * m * t) for m, a in ((1, 1), (2.32, .5), (4.25, .3))) * np.exp(-t * 9) * np.clip(t / .001, 0, 1)


def clink():
    return sum(tink(f, 0.7) * g for f, g in ((2150, .5), (3420, .35), (5230, .25)))


# vent glacé + craquements de givre (0-5.8 s)
t = tt(6.0)
wind = fft_filter(noise(6.0), 200, 1800) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.23 * t)) * np.clip(t / 1.5, 0, 1) * np.clip((6.0 - t) / 0.3, 0, 1)
add(sfx, 0, wind, 0.1, -0.3, rev=0.3)
for _ in range(240):
    x = 0.3 + 5.4 * rng.random() ** 0.6
    c = fft_filter(noise(0.02), 3000) * np.exp(-tt(0.02) * 300)
    add(sfx, x, c, 0.12 + 0.2 * rng.random(), rng.uniform(-.8, .8), rev=0.3)
add(sfx, 3.8, riser(2.0, 400, 6000), 0.3, 0, rev=0.4)
# fissures
for k in range(9):
    add(sfx, 4.95 + k * 0.08, fft_filter(noise(0.08), 1500) * np.exp(-tt(.08) * 50), 0.35, rng.uniform(-.6, .6), rev=0.5)
# bris de glace (5.8)
add(sfx, 5.8, boom(2.2), 0.8)
add(sfx, 5.8, fft_filter(noise(1.2), 2500) * np.exp(-tt(1.2) * 5), 0.45, 0, rev=0.6)
for _ in range(45):
    add(sfx, 5.8 + rng.random() ** 2 * 0.9, tink(rng.uniform(2500, 7500), 0.5), 0.07, rng.uniform(-.9, .9), rev=0.6)
# riser avant décapsulage
add(sfx, 9.0, riser(2.0, 200, 3000), 0.25, rev=0.3)
# décapsulage : clic + pssht
add(sfx, 11.0, fft_filter(noise(0.03), 1000) * np.exp(-tt(.03) * 150), 0.9)
t = tt(1.1)
add(sfx, 11.01, fft_filter(noise(1.1), 2200, 9000) * np.exp(-t * 3.2) * np.clip(t / 0.01, 0, 1), 0.55, 0, rev=0.3)
add(sfx, 11.0, tink(1800, 0.8), 0.12, 0.5, rev=0.5)
# whooshs de transition
for c in (11.95, 20.0, 24.0, 28.0):
    add(sfx, c - 0.38, whoosh(0.45), 0.32, rev=0.2)
# service (glouglou + mousse)
for _ in range(70):
    x = 12.35 + rng.random() * 5.2
    t = tt(0.07)
    f = rng.uniform(180, 420)
    add(sfx, x, np.sin(2 * np.pi * f * t * (1 + 2 * t)) * np.sin(np.pi * t / .07), 0.06, rng.uniform(-.2, .2))
t = tt(5.5)
add(sfx, 12.3, fft_filter(noise(5.5), 600, 4000) * np.clip(t / .15, 0, 1) * np.clip((5.5 - t) / .3, 0, 1) * (0.7 + 0.3 * np.sin(2 * np.pi * 7 * t)), 0.08, 0.1)
for _ in range(500):  # pétillement
    x = 12.6 + 7.2 * rng.random()
    add(sfx, x, fft_filter(noise(0.006), 6000) * np.exp(-tt(.006) * 600), 0.05 + 0.05 * rng.random(), rng.uniform(-.9, .9))
# glaçons
for x in (20.25, 20.9, 21.6, 22.35, 23.05):
    add(sfx, x, clink(), 0.22, rng.uniform(-.6, .6), rev=0.6)
for k in range(8):
    add(sfx, 24.05 + k * 0.045 + rng.random() * 0.03, clink(), 0.12, rng.uniform(-.8, .8), rev=0.5)
# impacts
add(sfx, 23.0, riser(1.0, 400, 5000), 0.25, rev=0.3)
add(sfx, 24.0, boom(1.6), 0.6)
add(sfx, 28.0, boom(2.0), 0.7)
# carton final : accord de cloches cristallines
for k, n in enumerate([72, 76, 79, 83, 88]):
    add(mus, 28.05 + k * 0.06, bell(note(n), 2.0), 0.07, -0.6 + k * 0.3, rev=0.9)

# ------------------------------------------------------------------ mixage
mus *= env[:, None]
# réverbération par convolution (IR synthétique stéréo 2.2 s)
ir_t = tt(2.2)
rev = np.zeros_like(send)
for ch in range(2):
    ir = rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 3.0)
    ir = fft_filter(ir, 300, 7000)
    ir /= np.sqrt((ir ** 2).sum())
    L = len(send) + len(ir)
    rev[:, ch] = np.fft.irfft(np.fft.rfft(send[:, ch], L) * np.fft.rfft(ir, L), L)[: len(send)]
mix = mus + sfx * 1.1 + rev * 0.6
# coupure musicale nette juste après le pssht
dip = np.ones(N)
a, b = int(11.0 * SR), int(11.95 * SR)
dip[a:b] = np.linspace(0.45, 0.8, b - a)
mix *= dip[:, None]
# fondu final
fo = int(0.5 * SR)
mix[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 2
mix /= np.abs(mix).max()
mix = np.tanh(mix * 3.2) / np.tanh(3.2)
for ch in range(2):
    mix[:, ch] = fft_filter(mix[:, ch], 25, 16000)
# normalisation sur le pic réel (suréchantillonné x4) à -2.5 dBTP
true_peak = max(np.abs(np.fft.irfft(np.fft.rfft(mix[:, ch]), 4 * N)).max() * 4 for ch in range(2))
mix *= 10 ** (-2.5 / 20) / true_peak

out = sys.argv[1] if len(sys.argv) > 1 else 'soundtrack.wav'
with wave.open(out, 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('ok', out)
