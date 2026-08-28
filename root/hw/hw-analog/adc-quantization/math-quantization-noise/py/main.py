from math import sqrt, log10

N   = 12          # розрядність
Vfs = 3.3         # повна шкала, В
levels = 1 << N   # 2^N = 4096 рівнів

# 1) крок квантування
q = Vfs / levels                       # 3.3/4096 ≈ 0.806 мВ

# 2) RMS шуму квантування з рівномірного розподілу: q/√12
e_rms = q / sqrt(12)                    # ≈ 0.233 мВ

# 3) RMS повношкального синуса: амплітуда/√2, амплітуда = Vfs/2
sig_rms = (Vfs / 2) / sqrt(2)          # ≈ 1.167 В

# 4) SNR як відношення RMS у децибелах (за напругою → 20·log10)
snr_built = 20 * log10(sig_rms / e_rms)

# 5) та сама величина з готової формули
snr_formula = 6.02 * N + 1.76

print(f"крок q          = {q * 1e3:.4f} мВ")
print(f"шум  e_rms      = {e_rms * 1e3:.4f} мВ  (= q/sqrt(12))")
print(f"сигнал sig_rms  = {sig_rms:.4f} В   (= (Vfs/2)/sqrt(2))")
print(f"SNR зібраний    = {snr_built:.2f} дБ")
print(f"SNR за формулою = {snr_formula:.2f} дБ")
