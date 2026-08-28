# Обчислити код настройки M для бажаної частоти:
#   M = round( fout * 2^N / fclk )
def dds_tuning_word(fout, fclk):
    m = fout * 2**32 / fclk        # fout·2^32/fclk
    return round(m)                # округлення до найближчого цілого

# Приклад:
#   dds_tuning_word(10000.0, 125e6)
#   = round(10000 · 4294967296 / 125e6)
#   = round(343597.38) = 343597
