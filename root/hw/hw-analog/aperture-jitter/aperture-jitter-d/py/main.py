import math

# Стеля SNR (дБ) від апертурного джиттера
# f_hz    — частота вхідного сигналу, Гц
# tj_sec  — RMS-джиттер такту, с
def jitter_snr_db(f_hz, tj_sec):
    x = 2.0 * math.pi * f_hz * tj_sec
    return -20.0 * math.log10(x)

# Скільки ефективних розрядів (ENOB) лишає ця стеля
def jitter_enob(f_hz, tj_sec):
    snr = jitter_snr_db(f_hz, tj_sec)
    return (snr - 1.76) / 6.02        # SNR ≈ 6.02·ENOB + 1.76

# приклад: jitter_snr_db(10e6, 1e-12) ≈ 84.0;  jitter_enob(...) ≈ 13.7
