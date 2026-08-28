# Python implementation using NumPy for vectorized DSP
import numpy as np

def iq_modulate(i_bb, q_bb, fs, fc):
    """Up-conversion: низькочастотні I/Q -> смуговий RF сигнал s(t)"""
    t = np.arange(len(i_bb)) / fs
    carrier_i = np.cos(2 * np.pi * fc * t)
    carrier_q = np.sin(2 * np.pi * fc * t)
    s_passband = i_bb * carrier_i - q_bb * carrier_q
    return s_passband

def iq_demodulate(s_passband, fs, fc, filter_len=41):
    """Down-conversion: смуговий RF -> низькочастотні I/Q через ФНЧ"""
    t = np.arange(len(s_passband)) / fs
    # Множення на квадратурний гетеродин
    i_raw =  2.0 * s_passband * np.cos(2 * np.pi * fc * t)
    q_raw = -2.0 * s_passband * np.sin(2 * np.pi * fc * t)
    
    # ФНЧ (КІХ-фільтр ковзного середнього)
    kernel = np.ones(filter_len) / filter_len
    i_rec = np.convolve(i_raw, kernel, mode='same')
    q_rec = np.convolve(q_raw, kernel, mode='same')
    return i_rec, q_rec

# Перевірка симуляції
if __name__ == "__main__":
    fs, fc, N = 10000.0, 2000.0, 1000
    t = np.arange(N) / fs
    i_orig = np.cos(2 * np.pi * 100 * t)
    q_orig = np.sin(2 * np.pi * 50 * t)

    s_rf = iq_modulate(i_orig, q_orig, fs, fc)
    i_rec, q_rec = iq_demodulate(s_rf, fs, fc)

    print(f"Зразок [500]: I_orig={i_orig[500]:.4f} -> I_rec={i_rec[500]:.4f}")
    print(f"Зразок [500]: Q_orig={q_orig[500]:.4f} -> Q_rec={q_rec[500]:.4f}")
