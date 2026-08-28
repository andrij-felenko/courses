#include <math.h>

// Похибка на вході (В) від синфазної завади vcm (В)
// за паспортного cmrr_db (дБ).
float cm_error_input(float vcm, float cmrr_db) {
    float ratio = powf(10.0f, cmrr_db / 20.0f);  // дБ → у разах
    return vcm / ratio;                          // зведена до входу завада
}

// Приклад: 1 В синфазного, CMRR = 100 дБ
// cm_error_input(1.0f, 100.0f) -> 1.0e-5 В = 10 мкВ
