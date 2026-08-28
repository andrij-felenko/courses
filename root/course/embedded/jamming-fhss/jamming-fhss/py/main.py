import math

# Виграш обробки в децибелах із відношення смуг (чип-рейт / швидкість даних).
def processing_gain_db(chip_rate_hz, data_rate_bps):
    ratio = chip_rate_hz / data_rate_bps    # у скільки разів ширше
    return 10.0 * math.log10(ratio)         # дБ


# GPS C/A: 1.023 МЧ/с проти 50 біт/с → ≈ 43 дБ
g = processing_gain_db(1023000.0, 50.0)     # g ≈ 43.1
