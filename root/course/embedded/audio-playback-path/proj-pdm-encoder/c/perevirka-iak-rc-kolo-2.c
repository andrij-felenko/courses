#include <math.h>        // sin() лише для згенерувати тестовий синус

// Демонстрація повного тракту: PCM-синус → PDM-біти → RC → назад у рівень.
void demo_roundtrip(void) {
    pdm_state  mod = { .accum = 0 };
    int32_t    rc  = 0;                    // стан RC-фільтра

    const int FREQ_STEPS = 64;            // відліків на період синуса
    for (int n = 0; n < FREQ_STEPS * 8; n++) {   // вісім періодів
        // згенерувати вхідний відлік синуса на чверть шкали
        int16_t sample = (int16_t)(8000.0 * sin(2.0 * 3.14159 * n / FREQ_STEPS));

        int32_t restored = 0;
        for (int k = 0; k < OSR; k++) {   // OSR бітів на відлік
            bool bit = pdm_step(&mod, sample);
            restored = rc_average(&rc, bit);   // усереднюємо кожен біт
        }
        // restored тепер ≈ sample (той самий синус, трохи зашумлений і
        // зсунутий по фазі — RC завжди трохи запізнюється). Роздрукуй пари
        // (sample, restored) — і побачиш, як однобітний потік відтворив хвилю.
    }
}
