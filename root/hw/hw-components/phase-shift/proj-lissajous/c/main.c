#include <math.h>
#include <stddef.h>
#include <stdint.h>

// Пара одночасних відліків двох каналів АЦП.
typedef struct { int16_t x, y; } Sample;

// Кут між каналами у градусах (додатний — Y веде, від'ємний — Y відстає).
// Повертає NAN, якщо у вікні немає сигналу або висхідного перетину.
float phase_from_lissajous(const Sample *s, size_t n) {
    // 1. Прибрати постійні зміщення — центрувати кожен канал коло нуля.
    int32_t sx = 0, sy = 0;
    for (size_t i = 0; i < n; i++) { sx += s[i].x; sy += s[i].y; }
    const float mx = (float)sx / n, my = (float)sy / n;

    // 2. Амплітуда B — найбільше відхилення Y після центрування.
    float B = 0.0f;
    for (size_t i = 0; i < n; i++) {
        const float y = s[i].y - my;
        if (fabsf(y) > B) B = fabsf(y);
    }
    if (B == 0.0f) return NAN;                     // по Y немає сигналу

    // 3. Перший висхідний перетин нуля по X — і знаковий Y саме там.
    for (size_t i = 1; i < n; i++) {
        const float x0 = s[i - 1].x - mx, x1 = s[i].x - mx;
        if (x0 < 0.0f && x1 >= 0.0f) {             // перехід − → +
            const float t  = x0 / (x0 - x1);       // де саме між відліками X = 0
            const float y0 = (s[i - 1].y - my) + t * (s[i].y - s[i - 1].y);
            float sin_phi = y0 / B;                // = sin φ, уже зі знаком
            if (sin_phi >  1.0f) sin_phi =  1.0f;  // притиснути шум на межі
            if (sin_phi < -1.0f) sin_phi = -1.0f;
            return asinf(sin_phi) * 57.29578f;     // радіани → градуси
        }
    }
    return NAN;                                    // висхідного кросу не було — довше вікно
}
