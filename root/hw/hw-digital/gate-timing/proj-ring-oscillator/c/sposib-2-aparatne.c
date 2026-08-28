// STM32 (HAL). Вихід кільця поділений апаратним лічильником на M=256,
// поділений сигнал заведено на канал input-capture таймера TIM2.
// Таймер тактується від системної шини (тут APB1 timer clock = 84 МГц).

#include "stm32f4xx_hal.h"

#define N            5U         // інверторів у кільці (непарне)
#define DIV_M        256U       // на скільки поділили частоту кільця перед захопленням
#define TIMER_HZ     84000000.0 // такт таймера TIM2, Гц

extern TIM_HandleTypeDef htim2; // TIM2, канал 1 у режимі input capture (CubeMX)

// Захопити два послідовні фронти, повернути період поділеного сигналу в секундах.
double capture_divided_period(void) {
    // Чекаємо перший фронт і фіксуємо значення таймера в мить фронту.
    __HAL_TIM_CLEAR_FLAG(&htim2, TIM_FLAG_CC1);
    while (!__HAL_TIM_GET_FLAG(&htim2, TIM_FLAG_CC1)) { }
    uint32_t c1 = HAL_TIM_ReadCapturedValue(&htim2, TIM_CHANNEL_1);

    // Чекаємо наступний фронт.
    __HAL_TIM_CLEAR_FLAG(&htim2, TIM_FLAG_CC1);
    while (!__HAL_TIM_GET_FLAG(&htim2, TIM_FLAG_CC1)) { }
    uint32_t c2 = HAL_TIM_ReadCapturedValue(&htim2, TIM_CHANNEL_1);

    // Різниця з урахуванням можливого перекоту 32-бітного таймера.
    uint32_t ticks = c2 - c1;              // беззнакове віднімання само коректне при перекоті
    return ticks / TIMER_HZ;               // період ПОДІЛЕНОГО сигналу, с
}

double measure_gate_delay(void) {
    // Усереднимо кілька захоплень — приберемо тремтіння (jitter) одиничного виміру.
    const int K = 64;
    double sum = 0.0;
    for (int i = 0; i < K; i++) sum += capture_divided_period();
    double T_div = sum / K;                // середній період поділеного сигналу

    // Повертаємо поділ назад: справжній період кільця у M разів коротший.
    double T_ring = T_div / DIV_M;         // T = 2·N·tpd
    double tpd    = T_ring / (2.0 * N);    // затримка одного вентиля
    return tpd;                            // с
}
