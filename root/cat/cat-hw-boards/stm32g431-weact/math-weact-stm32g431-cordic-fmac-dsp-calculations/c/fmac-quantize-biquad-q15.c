// C-функція квантування та масштабування коефіцієнтів фільтра у формат Q15
#include <stdint.h>
#include <math.h>

typedef struct {
    int16_t b_q15[3];
    int16_t a_q15[2]; // a0 завжди 1.0, зберігаємо a1 та a2
    uint8_t scale_shift;
} fmac_biquad_q15_t;

void fmac_quantize_biquad_q15(const double b[3], const double a[3], fmac_biquad_q15_t *out) {
    // Знаходимо максимальний за модулем коефіцієнт
    double max_val = fabs(b[0]);
    for (int i = 1; i < 3; i++) {
        if (fabs(b[i]) > max_val) max_val = fabs(b[i]);
        if (fabs(a[i]) > max_val) max_val = fabs(a[i]);
    }
    
    // Розраховуємо масштабний зсув m = ceil(log2(max_val))
    uint8_t shift = 0;
    if (max_val >= 1.0) {
        shift = (uint8_t)ceil(log2(max_val));
    }
    double scale = (double)(1 << shift);
    
    // Квантування у Q15 із врахуванням масштабу
    for (int i = 0; i < 3; i++) {
        out->b_q15[i] = (int16_t)round((b[i] / scale) * 32767.0);
    }
    out->a_q15[0] = (int16_t)round((a[1] / scale) * 32767.0);
    out->a_q15[1] = (int16_t)round((a[2] / scale) * 32767.0);
    out->scale_shift = shift;
}
