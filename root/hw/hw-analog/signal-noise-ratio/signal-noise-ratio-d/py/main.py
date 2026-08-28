from math import log10
# Обидві величини множаться на те саме G — відношення не зрушується
Usig_in   = 2.0e-3      # сигнал на вході, В rms
Unoise_in = 1.82e-6     # тепловий шум опору джерела, В rms
G = 100.0               # підсилення

Usig_out   = G * Usig_in      # 0.200 В
Unoise_out = G * Unoise_in    # 1.82e-4 В

snr_in_db  = 20.0 * log10(Usig_in  / Unoise_in)    # ≈ 60.8 дБ
snr_out_db = 20.0 * log10(Usig_out / Unoise_out)   # ≈ 60.8 дБ — те саме!
