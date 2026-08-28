// Тепловий захист комірки: спрацьовує за абсолютним рівнем АБО за крутизною.
// t_c10 — температура найгарячішої комірки в десятих градуса (372 = 37.2 °C),
// dt_ms — період між викликами в мілісекундах. Без float у гарячому шляху.
#include <stdint.h>
#include <stdbool.h>

#define T_TRIP_C10     600    // 60.0 °C — абсолютна аварія
#define RATE_TRIP      20     // 2.0 °C/с — крута втеча (десятих °C за секунду)

bool thermal_fault(int32_t t_c10, uint32_t dt_ms) {
    static int32_t prev = INT32_MIN;     // попередній замір
    bool fault = false;

    if (t_c10 >= T_TRIP_C10) {
        fault = true;                    // рубіж за рівнем
    }
    if (prev != INT32_MIN && dt_ms > 0) {
        // швидкість у десятих °C за секунду: (Δ десятих) * 1000 / Δмс
        int32_t rate = (t_c10 - prev) * 1000 / (int32_t)dt_ms;
        if (rate >= RATE_TRIP) {
            fault = true;                // рубіж за швидкістю — ловить раніше
        }
    }
    prev = t_c10;
    return fault;
}
