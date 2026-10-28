#!/usr/bin/env python3
"""Демо-саундтрек для клипа «Я не в сети» (Грязный Гена) — 3:07 (187 c).
Тёмный эмбиент + глубокий бас. Это ВРЕМЕННАЯ дорожка (placeholder):
заменяется на оригинал одной командой ffmpeg (см. README).

Таймлайн секций (сек):
  0-20   Интро    — тёмный дрон, шёпот-атмосфера
  20-50  Куплет 1 — пульс баса, грув
  50-60  Пре-дроп — нарастание, райзер
  60-75  Дроп 1   — 808-бас, энергия
  75-105 Куплет 2 — грув + тёплый пэд
  105-120 Брейк   — почти тишина, тиканье (ирония)
  120-140 Билд-ап — шиммер, райзер, нарастание
  140-165 Финальный дроп — свет, мощь, широкий пэд
  165-187 Аутро   — тёплый пэд, затухание
"""
import numpy as np
import wave

SR = 44100
DUR = 187.0
N = int(SR * DUR)
L = np.zeros(N)
R = np.zeros(N)
rng = np.random.default_rng(42)

def add(sig, start, pan=0.0, gain=1.0):
    i0 = int(start * SR)
    n = min(len(sig), N - i0)
    if n <= 0:
        return
    gl = gain * (1 - max(0, pan))
    gr = gain * (1 - max(0, -pan))
    L[i0:i0+n] += sig[:n] * gl
    R[i0:i0+n] += sig[:n] * gr

def sine(f, dur, amp=1.0):
    t = np.arange(int(dur*SR)) / SR
    return amp * np.sin(2*np.pi*f*t)

def saw_bandlimited(f, dur, amp=0.5, n_harm=30):
    t = np.arange(int(dur*SR)) / SR
    out = np.zeros_like(t)
    for k in range(1, n_harm+1):
        if f*k >= SR/2*0.9: break
        out += np.sin(2*np.pi*f*k*t) / k
    return amp * out * (2/np.pi)

def env_adsr(n, a, d, s_level, r):
    e = np.ones(n) * s_level
    na, nd, nr = int(a*SR), int(d*SR), int(r*SR)
    na, nd, nr = min(na, n), min(nd, n), min(nr, n)
    if na > 0: e[:na] = np.linspace(0, 1, na)
    if nd > 0: e[na:na+nd] = np.linspace(1, s_level, nd)
    if nr > 0: e[-nr:] *= np.linspace(1, 0, nr)
    return e

def lowpass_fft(sig, cutoff):
    spec = np.fft.rfft(sig)
    freqs = np.fft.rfftfreq(len(sig), 1/SR)
    spec[freqs > cutoff] *= 0.05
    return np.fft.irfft(spec, len(sig))

def sub_hit(freq, dur=2.2, amp=1.0, glide=True):
    """808-удар: синус с глиссандо вниз + экспон. затухание."""
    n = int(dur*SR)
    t = np.arange(n)/SR
    f_t = np.full(n, freq)
    if glide:
        g = np.exp(-t/0.04)
        f_t = freq * (1 + 1.2*g)
    ph = 2*np.pi*np.cumsum(f_t)/SR
    body = np.sin(ph) * np.exp(-t/(dur/3.2))
    click = rng.normal(0, 1, n) * np.exp(-t/0.004) * 0.25
    click = lowpass_fft(click, 900)
    return amp * np.tanh((body + click) * 1.3) * 0.85

def pad_chord(freqs, dur, amp=0.3, attack=1.2, release=2.0, detune=0.0015, cutoff=2200):
    n = int(dur*SR)
    out = np.zeros(n)
    for f in freqs:
        for dt in (1-detune, 1+detune):
            t = np.arange(n)/SR
            out += 0.5*np.sin(2*np.pi*f*dt*t) + 0.22*np.sin(2*np.pi*f*2*dt*t+0.5) + 0.1*np.sin(2*np.pi*f*3*dt*t+1.1)
    out /= len(freqs)
    out = lowpass_fft(out, cutoff)
    e = np.ones(n)
    na = min(int(attack*SR), n//2); e[:na] = np.linspace(0,1,na)
    nr = min(int(release*SR), n//2); e[-nr:] *= np.linspace(1,0,nr)
    return amp * out * e

def noise_sweep(dur, amp=0.5, cutoff_start=300, cutoff_end=6000, reverse=False):
    n = int(dur*SR)
    sig = rng.normal(0, 1, n)
    blocks = 64
    bs = n // blocks
    out = np.zeros(n)
    for b in range(blocks):
        frac = b/max(blocks-1,1)
        if reverse: frac = 1-frac
        cut = cutoff_start + (cutoff_end-cutoff_start)*frac
        seg = sig[b*bs:(b+1)*bs]
        out[b*bs:(b+1)*bs] = lowpass_fft(seg, cut)
    e = np.linspace(0.15, 1.0, n)**2
    return amp * out * e * 0.5

def riser(dur, amp=0.35, f0=70, f1=2400):
    n = int(dur*SR)
    t = np.arange(n)/SR
    f_t = f0 * (f1/f0)**(t/dur)
    ph = 2*np.pi*np.cumsum(f_t)/SR
    trem = 0.6 + 0.4*np.sin(2*np.pi*9*t)
    e = (t/dur)**2.2
    return amp * np.sin(ph) * trem * e

def tv_static(dur, amp=0.5):
    n = int(dur*SR)
    sig = rng.normal(0, 1, n)
    sig = np.tanh(sig*2.2)*0.8
    e = np.ones(n)
    ne = min(int(0.02*SR), n//2)
    e[:ne] = np.linspace(0,1,ne); e[-ne:] = np.linspace(1,0,ne)
    return amp * sig * e * 0.5

def crackle(dur, amp=0.06, density=18):
    n = int(dur*SR)
    out = np.zeros(n)
    ticks = rng.poisson(density*dur)
    for _ in range(ticks):
        i = rng.integers(0, max(1, n-1000))
        ln = rng.integers(40, 700)
        tk = rng.normal(0, 1, ln) * np.exp(-np.arange(ln)/(ln/4))
        end = min(ln, n-i)
        out[i:i+end] += tk[:end]
    return amp * lowpass_fft(out, 4800)

# ============================================================
# НОТЫ
A1, E2, A2, C3, E3, F2, G2, C2, G3, F3, D3 = 55.0, 82.41, 110.0, 130.81, 164.81, 87.31, 98.0, 65.41, 196.0, 174.61, 146.83
C1 = 32.7

# ---------- ИНТРО 0-20 ----------
dr = saw_bandlimited(A1, 21, amp=0.32, n_harm=14) + saw_bandlimited(E2, 21, amp=0.14, n_harm=8)
dr = lowpass_fft(dr, 500)
add(dr * env_adsr(len(dr), 3, 0, 1, 5), 0, pan=0, gain=0.9)
add(pad_chord([A1, E2, A2], 21, amp=0.16, attack=4, release=6, cutoff=700), 0)
add(crackle(20, amp=0.05, density=14), 0)
for st in (6.5, 13.2, 17.0):
    add(sub_hit(A1, 3.0, amp=0.5), st)
add(noise_sweep(2.2, amp=0.10, cutoff_start=200, cutoff_end=1600), 1.0)
add(noise_sweep(1.8, amp=0.08, cutoff_start=200, cutoff_end=1200), 9.0)
add(tv_static(0.5, amp=0.34), 14.0)

# ---------- КУПЛЕТ 1: 20-50 (85 BPM) ----------
beat = 60/85.0
pat = [1,0,0.6,0, 0,0.8,0,0.4]
for i in range(int(30/beat/2)):
    st = 20 + i*2*beat
    v = pat[i % 8]
    if v > 0:
        add(sub_hit(A1, 1.8, amp=0.42*v), st)
add(pad_chord([A2, C3, E3], 30, amp=0.13, attack=5, release=6, cutoff=1400), 20)
add(crackle(30, amp=0.035, density=20), 20)
for i in range(int(30/beat)):
    if i % 2 == 1:
        add(lowpass_fft(rng.normal(0,1,int(0.06*SR)), 8000)*0.05, 20+i*beat)

# ---------- ПРЕ-ДРОП 50-60 ----------
add(riser(9.5, amp=0.26), 50.2)
add(pad_chord([A2, C3, E3], 10, amp=0.12, attack=2, release=3, cutoff=2000), 50)
for i, st in enumerate(np.arange(50, 59.6, 1.0)):
    add(sub_hit(A1*(1+i*0.03), 0.9, amp=0.3+0.05*i), st)
add(noise_sweep(3.0, amp=0.14, cutoff_start=400, cutoff_end=8000), 57)

# ---------- ДРОП 1: 60-75 ----------
add(tv_static(0.45, amp=0.42), 60.0)
d1pat = [1,0,0,0.85, 0,0,1,0, 0,0.9,0,0, 1,0,0.5,0]
i = 0
tcur = 60.35
while tcur < 74.2:
    v = d1pat[i % len(d1pat)]
    if v > 0:
        add(sub_hit(A1, 2.0, amp=0.62*v), tcur)
    if i % 4 == 2:
        add(lowpass_fft(rng.normal(0,1,int(0.12*SR)), 6000)*0.09, tcur)
    i += 1
    tcur += beat
add(pad_chord([A2, C3, E3], 14.5, amp=0.20, attack=0.4, release=2, cutoff=2600), 60.35, pan=-0.2)
add(pad_chord([A2, E3, A2*2], 14.5, amp=0.10, attack=0.6, release=2, cutoff=3000), 60.35, pan=0.3)
add(noise_sweep(0.8, amp=0.16, cutoff_start=2000, cutoff_end=9000), 66.5)
add(noise_sweep(0.8, amp=0.16, cutoff_start=2000, cutoff_end=9000), 71.8)

# ---------- КУПЛЕТ 2: 75-105 ----------
pat2 = [1,0,0.55,0, 0,0.75,0,0.35]
i = 0
tcur = 75.3
while tcur < 104:
    v = pat2[i % 8]
    if v > 0:
        add(sub_hit(A1 if i % 16 < 12 else F2, 1.7, amp=0.4*v), tcur)
    i += 1
    tcur += 2*beat
add(pad_chord([F2, C3, F3], 15, amp=0.10, attack=6, release=5, cutoff=1600), 75, pan=0.15)
add(pad_chord([G2, D3, G3], 15, amp=0.08, attack=6, release=5, cutoff=1600), 90, pan=-0.15)
add(crackle(30, amp=0.03, density=16), 75)

# ---------- БРЕЙК 105-120 ----------
add(lowpass_fft(saw_bandlimited(A1, 15, amp=0.1, n_harm=6), 300) * env_adsr(int(15*SR), 2, 0, 1, 3), 105)
add(crackle(15, amp=0.06, density=10), 105)
for st in np.arange(106, 118, 1.0):
    add(lowpass_fft(rng.normal(0,1,int(0.015*SR)), 2500)*0.10, st)
    add(lowpass_fft(rng.normal(0,1,int(0.010*SR)), 2000)*0.06, st+0.5)
add(sine(880, 0.09, 0.06), 112.4); add(sine(660, 0.09, 0.05), 112.55)

# ---------- БИЛД-АП 120-140 ----------
add(riser(18, amp=0.30, f0=60, f1=3000), 120)
for k, st in enumerate(np.arange(120.5, 138, 2.4)):
    f = [C3, E3, G3, C3*2, E3*2, G3*2, C3*2, E3*2][k % 8]
    add(pad_chord([f], 3.2, amp=0.07+0.008*k, attack=0.5, release=1.5, cutoff=5200), st, pan=(-0.3+0.6*(k%2)))
for i, st in enumerate(np.arange(128, 139.6, 0.7059*2)):
    add(sub_hit(C2, 1.2, amp=0.28+0.05*i), st)
add(pad_chord([C3, E3, G3], 19, amp=0.14, attack=8, release=3, cutoff=2800), 120.5)
add(noise_sweep(4, amp=0.2, cutoff_start=500, cutoff_end=10000), 135.5)

# ---------- ФИНАЛЬНЫЙ ДРОП 140-165 ----------
add(tv_static(0.5, amp=0.5), 140.0)
fdpat = [1,0,0,0.9, 0,0,1,0.3, 0,0.95,0,0, 1,0,0.55,0]
i = 0
tcur = 140.4
while tcur < 163.5:
    v = fdpat[i % len(fdpat)]
    if v > 0:
        add(sub_hit(C1*2, 2.1, amp=0.66*v), tcur)
    if i % 4 == 2:
        add(lowpass_fft(rng.normal(0,1,int(0.12*SR)), 6500)*0.10, tcur)
    if i % 8 == 7:
        add(lowpass_fft(rng.normal(0,1,int(0.3*SR)), 9000)*0.08, tcur)
    i += 1
    tcur += beat
add(pad_chord([C3, E3, G3, C3*2], 24, amp=0.24, attack=0.5, release=3, cutoff=3400), 140.4, pan=-0.25)
add(pad_chord([G3, C3*2, E3*2], 24, amp=0.13, attack=0.8, release=3, cutoff=3800), 140.4, pan=0.3)
add(noise_sweep(1.0, amp=0.18, cutoff_start=3000, cutoff_end=9500), 147.0)
add(noise_sweep(1.0, amp=0.18, cutoff_start=3000, cutoff_end=9500), 153.5)
add(noise_sweep(1.2, amp=0.22, cutoff_start=2000, cutoff_end=10000), 160.0)

# ---------- АУТРО 165-187 ----------
add(pad_chord([F2, C3, F3, A2], 22, amp=0.22, attack=3, release=10, cutoff=2000), 165, pan=-0.1)
add(pad_chord([A2, E3, A2*2], 22, amp=0.12, attack=4, release=10, cutoff=2400), 165, pan=0.2)
add(sub_hit(C1*2, 4.0, amp=0.35), 167.5)
add(sub_hit(F2, 4.0, amp=0.3), 174)
add(crackle(20, amp=0.03, density=8), 165)

# ============================================================
# МАСТЕРИНГ
mix = np.stack([L, R])
mix = np.tanh(mix * 1.15)
peak = np.max(np.abs(mix))
mix = mix / peak * 0.88
nf = int(1.5*SR); mix[:, :nf] *= np.linspace(0, 1, nf)
nf = int(6*SR);   mix[:, -nf:] *= np.linspace(1, 0, nf)**1.5

out = (mix.T * 32767).astype(np.int16)
with wave.open("/home/z/my-project/dirtygen/audio/soundtrack_placeholder.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(out.tobytes())
print("SAVED soundtrack_placeholder.wav", out.shape[0]/SR, "sec")
