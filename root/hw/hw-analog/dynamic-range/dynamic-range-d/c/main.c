// Скільки рівнів і який діапазон дає N-бітний АЦП — швидка оцінка для вибору деталі.
#include <math.h>

float adc_dynamic_range_db(int bits) {
    // ідеальний діапазон повношкальної синусоїди: 6.02·N + 1.76 дБ
    return 6.02f * bits + 1.76f;
}

int bits_for_range(float ratio_max_to_min) {
    // скільки бітів треба, щоб охопити заданий розмах сигналу (відношення разів)
    float needed_db = 20.0f * log10f(ratio_max_to_min);
    int bits = (int)ceilf(needed_db / 6.02f);   // округлюємо вгору — менше не вистачить
    return bits;
}
// bits_for_range(4000.0f) → 12;  adc_dynamic_range_db(12) ≈ 74 дБ
