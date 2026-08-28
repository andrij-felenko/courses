#include <stdint.h>

// Стеля частоти в мегагерцах. Затримки — у наносекундах.
// Синхронний: критичний шлях НЕ залежить від n (перенос паралельний).
double fmax_sync_MHz(double t_pd, double t_carry, double t_setup) {
    double path_ns = t_pd + t_carry + t_setup;   // n тут не бере участі
    return 1000.0 / path_ns;                      // 1/нс = ГГц → ×1000 = МГц
}

// Ланцюговий: затримки складаються вздовж усіх n розрядів (естафета).
double fmax_ripple_MHz(double t_pd, uint32_t n) {
    double path_ns = (double)n * t_pd;            // ось воно, N біля затримки
    return 1000.0 / path_ns;
}
