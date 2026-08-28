#include <stdint.h>
#include <stdbool.h>

#define DUTY_PERMILLE  10u      // 1% = 10 проміле (EU868)

// Скільки разів на годину дозволено слати пакет із даним airtime (мкс).
uint32_t sends_per_hour(uint32_t airtime_us) {
    // 1% від години = 3600 с · 1% = 36 с = 36 000 000 мкс.
    const uint64_t budget_us_per_hour = 3600000000ULL * DUTY_PERMILLE / 1000ULL;
    return (uint32_t)(budget_us_per_hour / airtime_us);
}

// Мінімальний проміжок між початками посилок, мкс (рівномірне розкладання 1%).
// airtime — це DUTY_PERMILLE‰ від періоду, тож період = airtime · 1000 / DUTY_PERMILLE.
uint32_t min_interval_us(uint32_t airtime_us) {
    return (uint32_t)((uint64_t)airtime_us * 1000ULL / DUTY_PERMILLE);
}

// Практичний планувальник: чи МОЖНА слати зараз, тримаючись 1% рівномірно.
// Викликати перед кожною передачею; після успішної — оновити last_tx_us.
static uint32_t last_tx_us = 0;
static bool     have_sent  = false;

bool may_send_now(uint32_t now_us, uint32_t airtime_us) {
    if (!have_sent) return true;                  // перша посилка — можна
    uint32_t need = min_interval_us(airtime_us);  // скільки треба було мовчати
    return (now_us - last_tx_us) >= need;
}

void note_sent(uint32_t now_us) {
    last_tx_us = now_us;
    have_sent  = true;
}
