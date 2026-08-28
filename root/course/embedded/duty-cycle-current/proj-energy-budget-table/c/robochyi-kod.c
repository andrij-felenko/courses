#include <stdint.h>
#include <stddef.h>

// Одна фаза циклу: струм у мікроамперах, тривалість у мікросекундах.
typedef struct {
    uint32_t current_uA;   // напр. 180000 = 180 мА
    uint32_t duration_us;  // напр. 300000 = 0.3 с
} phase_t;

// Підсумок розрахунку.
typedef struct {
    uint32_t avg_current_uA;   // середній струм за цикл, мкА
    uint32_t life_hours;       // оцінка часу життя, год
} budget_t;

// active[] — активні фази (boot, вимір, TX...). Решту періоду чіп спить.
// period_us  — повна тривалість циклу, мкс.
// sleep_uA   — струм глибокого сну, мкА.
// cap_mAh    — ємність батареї, мА·год.
budget_t energy_budget(const phase_t *active, size_t n,
                       uint64_t period_us, uint32_t sleep_uA,
                       uint32_t cap_mAh) {
    budget_t out = {0, 0};
    if (period_us == 0) return out;            // захист від ділення на нуль

    // Заряд активних фаз, накопичуємо в 64 бітах: мкА·мкс росте дуже швидко.
    uint64_t active_us = 0;
    uint64_t charge_uA_us = 0;                  // заряд в одиницях мкА·мкс
    for (size_t i = 0; i < n; i++) {
        charge_uA_us += (uint64_t)active[i].current_uA * active[i].duration_us;
        active_us    += active[i].duration_us;
    }

    // Сон займає решту періоду (якщо активні фази довші за період — сну нема).
    uint64_t sleep_us = (active_us < period_us) ? (period_us - active_us) : 0;
    charge_uA_us += (uint64_t)sleep_uA * sleep_us;

    // Середній струм = заряд / період (мкА·мкс / мкс = мкА). Округлення до найближчого.
    uint64_t avg_uA = (charge_uA_us + period_us / 2) / period_us;
    out.avg_current_uA = (uint32_t)avg_uA;

    if (avg_uA == 0) return out;                // нескінченне життя — лишаємо 0 як «дуже довго»

    // Час життя: ємність / середній струм. cap у мА·год = cap*1000 мкА·год.
    // life_h = cap_mAh * 1000 / avg_uA.  cap*1000 множимо в 64 бітах.
    out.life_hours = (uint32_t)(((uint64_t)cap_mAh * 1000u) / avg_uA);
    return out;
}
