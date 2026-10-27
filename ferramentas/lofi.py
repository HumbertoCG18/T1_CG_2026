# Sintetiza uma trilha lofi ambiente (video/lofi.wav), gerada do zero: sem
# amostras externas e, portanto, sem direitos autorais de terceiros.
# Acordes Fmaj7-Em7-Dm7-Cmaj7, baixo, bateria leve com swing, chiado de vinil,
# tudo filtrado e com volume baixo para ficar de fundo.
# Uso: python ferramentas/lofi.py && python ferramentas/video.py --audio video/lofi.wav

import pathlib

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR, DURACAO, BPM = 44100, 120.0, 72
BATIDA = 60 / BPM
COMPASSO = 4 * BATIDA
ACORDES = [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [48, 52, 55, 59]]
SAIDA = pathlib.Path(__file__).resolve().parent.parent / "video" / "lofi.wav"

rng = np.random.default_rng(7)
n = int(SR * DURACAO)
mix = np.zeros(n)


def hz(midi):
    return 440 * 2 ** ((midi - 69) / 12)


def soma(sinal, inicio):
    i = int(inicio * SR)
    if i < n:
        mix[i:i + len(sinal)] += sinal[:n - i]


def piano(notas, dur, vol):
    t = np.arange(int(dur * SR)) / SR
    env = np.minimum(t / 0.015, 1) * np.exp(-t * 1.6)
    s = sum(np.sin(2 * np.pi * hz(m) * 1.002 * t) + 0.25 * np.sin(4 * np.pi * hz(m) * t) for m in notas)
    return vol * env * s / len(notas)


def baixo(m, dur):
    t = np.arange(int(dur * SR)) / SR
    return 0.35 * np.minimum(t / 0.01, 1) * np.exp(-t * 2.5) * np.sin(2 * np.pi * hz(m - 12) * t)


def bumbo():
    t = np.arange(int(0.35 * SR)) / SR
    freq = 50 + 70 * np.exp(-t * 30)
    return 0.5 * np.exp(-t * 12) * np.sin(2 * np.pi * np.cumsum(freq) / SR)


def ruido(dur, vol, corte, tipo):
    t = np.arange(int(dur * SR)) / SR
    return vol * np.exp(-t * 40) * sosfilt(butter(2, corte, tipo, fs=SR, output="sos"), rng.standard_normal(len(t)))


swing = 0.12 * BATIDA
compasso = 0
while compasso * COMPASSO < DURACAO:
    c0 = compasso * COMPASSO
    acorde = ACORDES[compasso % 4]
    soma(piano(acorde, COMPASSO, 0.30), c0)
    soma(piano(acorde[1:], 1.5 * BATIDA, 0.18), c0 + 2.5 * BATIDA + swing)
    soma(baixo(acorde[0], 1.5 * BATIDA), c0)
    soma(baixo(acorde[0], BATIDA), c0 + 2.5 * BATIDA)
    for b in (0, 2.5):
        soma(bumbo(), c0 + b * BATIDA)
    for b in (1, 3):
        soma(ruido(0.25, 0.20, 1800, "lowpass"), c0 + b * BATIDA)
    for k in range(8):
        soma(ruido(0.06, 0.06, 7000, "highpass"), c0 + k * BATIDA / 2 + (swing if k % 2 else 0))
    compasso += 1

# Chiado de vinil: ruido continuo baixo e estalos esparsos
mix += 0.004 * sosfilt(butter(1, 3000, "lowpass", fs=SR, output="sos"), rng.standard_normal(n))
estalos = rng.random(n) < 3 / SR
mix += 0.08 * estalos * rng.standard_normal(n)

mix = sosfilt(butter(2, 2500, "lowpass", fs=SR, output="sos"), mix)
fade = np.ones(n)
fade[:3 * SR] = np.linspace(0, 1, 3 * SR)
fade[-4 * SR:] = np.linspace(1, 0, 4 * SR)
mix *= fade

# Volume de fundo: RMS em -30 dBFS, com pico limitado a -12 dBFS
mix *= 10 ** (-30 / 20) / np.sqrt(np.mean(mix ** 2))
mix *= min(1, 10 ** (-12 / 20) / np.max(np.abs(mix)))
assert np.isfinite(mix).all() and np.max(np.abs(mix)) <= 0.26

SAIDA.parent.mkdir(exist_ok=True)
wavfile.write(SAIDA, SR, (mix * 32767).astype(np.int16))
print("Gerado:", SAIDA, "RMS %.1f dBFS, pico %.1f dBFS" % (20 * np.log10(np.sqrt(np.mean(mix ** 2))),
                                                          20 * np.log10(np.max(np.abs(mix)))))
