#include <stdint.h>

static volatile int32_t g_overflow_count = 0;

void TIMx_IRQHandler(void) {
    if (TIMx->SR & TIM_SR_UIF) {
        TIMx->SR = ~TIM_SR_UIF; // Скидання прапорця переривання оновлення
        if ((TIMx->CR1 & TIM_CR1_DIR) == 0) {
            g_overflow_count++; // Переповнення вгору (Upcounting)
        } else {
            g_overflow_count--; // Недоповнення вниз (Downcounting)
        }
    }
}
