#include <math.h>

// Виграш обробки в децибелах із відношення смуг (чип-рейт / швидкість даних).
float processing_gain_db(float chip_rate_hz, float data_rate_bps) {
    float ratio = chip_rate_hz / data_rate_bps;   // у скільки разів ширше
    return 10.0f * log10f(ratio);                 // дБ
}

// GPS C/A: 1.023 МЧ/с проти 50 біт/с → ≈ 43 дБ
float g = processing_gain_db(1023000.0f, 50.0f);  // g ≈ 43.1
