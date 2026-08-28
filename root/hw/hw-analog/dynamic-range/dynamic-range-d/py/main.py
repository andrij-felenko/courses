import math

def adc_dynamic_range_db(bits):
    # ідеальний діапазон повношкальної синусоїди: 6.02·N + 1.76 дБ
    return 6.02 * bits + 1.76

def bits_for_range(ratio_max_to_min):
    # скільки бітів треба, щоб охопити заданий розмах сигналу (відношення разів)
    needed_db = 20.0 * math.log10(ratio_max_to_min)
    return math.ceil(needed_db / 6.02)          # округлюємо вгору — менше не вистачить

# bits_for_range(4000.0) → 12;  adc_dynamic_range_db(12) ≈ 74 дБ
