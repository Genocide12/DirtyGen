#!/usr/bin/env python3
"""Анализ структуры трека: энергия по секундам для раскладки сцен клипа.
Использование: python3 analyze_track.py <mp3>
"""
import subprocess, sys
import numpy as np

path = sys.argv[1]
out = subprocess.run(
    ['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', '22050', '-'],
    capture_output=True).stdout
x = np.frombuffer(out, dtype=np.float32)
sr = 22050
dur = len(x) / sr
win = int(sr * 0.5)
n = len(x) // win
rms = np.sqrt(np.mean(x[:n*win].reshape(n, win)**2, axis=1))
# сглаживание
k = np.ones(3) / 3
rms_s = np.convolve(rms, k, mode='same')
peak = rms_s.max()

print(f"DURATION: {dur:.2f}s ({int(dur//60)}:{int(dur%60):02d})")
print("time  energy  bar")
for i in range(0, n, 4):  # каждые 2 секунды
    t = i * 0.5
    seg = rms_s[i:i+4].mean()
    bar = '#' * int(seg / peak * 55)
    print(f"{t:6.1f} {seg/peak:5.2f} {bar}")
