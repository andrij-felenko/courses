#include <stdint.h>
#include <stddef.h>

// Накопичувач заряду поточного вікна.
// Працює в пікокулонах (мкА·мкс) — найдрібніша одиниця, що випадає з добутку.
typedef struct {
    uint64_t window_pC;   // заряд поточного вікна, пікокулони (мкА·мкс)
    uint32_t window_us;   // скільки часу вже триває поточне вікно, мкс
} accumulator_t;

// Одна вибірка: додати порцію заряду за інтервал dt_us при струмі i_uA.
static inline void acc_add_sample(accumulator_t *a, uint32_t i_uA, uint32_t dt_us) {
    // КЛЮЧОВЕ приведення: добуток рахуємо в 64 бітах, інакше тихе обрізання.
    a->window_pC  += (uint64_t)i_uA * dt_us;
    a->window_us  += dt_us;
}
