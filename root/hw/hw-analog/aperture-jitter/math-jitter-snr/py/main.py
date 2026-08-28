import math


# Максимально допустимий RMS-джиттер такту (с),
# щоб на частоті f_hz отримати задану кількість ефективних розрядів.
def max_jitter_for_bits(f_hz, bits):
    snr_db = 6.02 * bits + 1.76            # цільовий SNR
    ratio = 10.0 ** (snr_db / 20.0)        # SNR у разах (амплітудно)
    return 1.0 / (2.0 * math.pi * f_hz * ratio)


# приклад: max_jitter_for_bits(10e6, 14.0) ≈ 0.79e-12 с (з урахуванням 1.76 дБ)
