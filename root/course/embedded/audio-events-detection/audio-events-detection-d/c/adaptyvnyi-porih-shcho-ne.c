#include <stdint.h>

// Асиметричне оновлення оцінки фону (усе в цілих, Q-нуль — просто MSE).
// UP > DOWN: зростання фону наздоганяємо агресивно, спад ведемо мляво.
static uint32_t noise = 400;              // оцінка фону, одиниці MSE
const int SHIFT_UP   = 3;                 // швидко: α_up   ≈ 1/8
const int SHIFT_DOWN = 7;                 // повільно: α_down ≈ 1/128

void noise_track(uint32_t mse) {
    if (mse > noise) {
        noise += (mse - noise) >> SHIFT_UP;    // фон росте — доганяємо жваво
    } else {
        noise -= (noise - mse) >> SHIFT_DOWN;  // фон падає — сповзаємо ліниво
    }
}
