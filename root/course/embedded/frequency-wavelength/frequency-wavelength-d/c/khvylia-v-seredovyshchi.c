#include <math.h>

// Затримка сигналу на доріжці плати (мікросмужка).
// len_m — довжина доріжки в метрах, eps_eff — ефективна проникність.
float trace_delay_ns(float len_m, float eps_eff) {
    const float c = 2.998e8f;                 // м/с
    float v = c / sqrtf(eps_eff);             // швидкість у середовищі
    return (len_m / v) * 1e9f;                // у наносекундах
}

// приклад: 10 см на FR-4 → ≈0.56 нс
// float d = trace_delay_ns(0.10f, 2.8f);
