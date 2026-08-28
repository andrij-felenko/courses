#include <stdint.h>
#include <math.h>

// Обчислити код настройки M для бажаної частоти:
//   M = round( fout * 2^N / fclk )
uint32_t dds_tuning_word(double fout, double fclk) {
    double m = fout * 4294967296.0 / fclk;   // fout·2^32/fclk
    return (uint32_t)(m + 0.5);              // округлення до найближчого цілого
}

// Приклад:
//   dds_tuning_word(10000.0, 125e6)
//   = round(10000 · 4294967296 / 125e6)
//   = round(343597.38) = 343597
