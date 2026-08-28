#include <math.h>

// Усе в одиницях СІ: оми, фаради, герци, ампери, вольти.
typedef struct {
    float Rf;       // резистор перетворення, Ом
    float Cin;      // повна вхідна ємність (діод + ОП + монтаж), Ф
    float f_gbw;    // добуток підсилення на смугу ОП, Гц
} TiaSpec;

// Cf, потрібний для заданої смуги −3 дБ
static float cf_for_bandwidth(float Rf, float bw_hz) {
    return 1.0f / (2.0f * (float)M_PI * Rf * bw_hz);
}

// Cf-орієнтир для максимально плаского (баттервортівського) відгуку — нижня межа стійкості
static float cf_for_stability(const TiaSpec *s) {
    return sqrtf(s->Cin / (2.0f * (float)M_PI * s->Rf * s->f_gbw));
}

// Реальна смуга −3 дБ при обраному Cf
static float bandwidth_of(float Rf, float Cf) {
    return 1.0f / (2.0f * (float)M_PI * Rf * Cf);
}

void choose_tia(const TiaSpec *s, float want_bw_hz) {
    float cf_bw  = cf_for_bandwidth(s->Rf, want_bw_hz);  // ≈ 1.6 пФ
    float cf_min = cf_for_stability(s);                  // ≈ 1.0 пФ
    // беремо більший: він і смугу обмежить, і стійкість забезпечить
    float Cf = (cf_bw > cf_min) ? cf_bw : cf_min;
    float real_bw = bandwidth_of(s->Rf, Cf);             // фактична смуга
    // Rf = 1 МОм, Cf ≈ 1.6 пФ, реальна смуга ≈ 100 кГц
    (void)real_bw;
}
