import numpy as np
from scipy.signal import hilbert

fs = 44_100
t  = np.arange(int(fs * 1.0)) / fs
f1, f2 = 440.0, 443.0
x = np.sin(2*np.pi*f1*t) + np.sin(2*np.pi*f2*t)   # два майже однакові тони

env       = np.abs(hilbert(x))                    # обвідна = модуль аналітичного сигналу
env_theor = 2*np.abs(np.cos(np.pi*(f1 - f2)*t))   # те саме з тотожності «сума→добуток»
# env ≈ env_theor: повільна крива, що дихає з частотою |f1 − f2|
