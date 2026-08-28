#include <stdint.h>

int64_t get_encoder_position_atomic(void) {
    int32_t high1, high2;
    uint16_t low;
    do {
        high1 = g_overflow_count;
        low = (uint16_t)TIMx->CNT;
        high2 = g_overflow_count;
    } while (high1 != high2); // Повторюємо, якщо під час зчитування виникло переривання

    // Перевірка на випадок, коли переповнення сталось, але прапорець UIF ще не оброблений
    if ((TIMx->SR & TIM_SR_UIF) && (low < 32768)) {
        if ((TIMx->CR1 & TIM_CR1_DIR) == 0) {
            high1++;
        } else {
            high1--;
        }
    }
    return ((int64_t)high1 << 16) | low;
}
