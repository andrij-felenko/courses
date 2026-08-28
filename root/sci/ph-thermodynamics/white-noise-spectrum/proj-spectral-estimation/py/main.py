# Python Reference Implementation using SciPy and NumPy
import numpy as np
from scipy import signal

# 1. Setup Parameters
fs = 10000.0               # Sampling frequency (10 kHz)
g0_target = 1e-4           # Target single-sided PSD (1e-4 V^2/Hz)
duration = 2.0             # 2 seconds
N = int(fs * duration)

# 2. Generate Discrete Gaussian White Noise
# Discrete variance sigma^2 = G0 * (fs / 2)
std_dev = np.sqrt(g0_target * (fs / 2.0))
noise_signal = np.random.normal(loc=0.0, scale=std_dev, size=N)

# 3. Estimate PSD via Welch's Method
frequencies, psd_estimated = signal.welch(
    noise_signal, 
    fs=fs, 
    window='hann', 
    nperseg=1024, 
    scaling='density'
)

print(f"Target PSD: {g0_target:.6e} V^2/Hz")
print(f"Mean Estimated PSD: {np.mean(psd_estimated):.6e} V^2/Hz")
