#include <stdint.h>

#define DIV 10u                       // поділ: дія раз на DIV подій

volatile uint32_t revolutions = 0;    // усього обертів (лічильник подій)
volatile uint8_t  mod_cnt    = 0;     // лічильник за модулем (0..DIV-1)

// Викликається з переривання на фронті від давача Голла
void on_hall_pulse(void) {
    revolutions++;                    // лічильник подій: просто +1

    if (++mod_cnt >= DIV) {           // дорахували до межі —
        mod_cnt = 0;                  // скидаємось у 0 (mod-N по колу)
        LED_PIN ^= 1u;               // дія: перемкнути світлодіод (toggle у коді)
    }
}
