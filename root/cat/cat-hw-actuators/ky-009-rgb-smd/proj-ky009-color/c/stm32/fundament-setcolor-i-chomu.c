// KY-009, спільний катод. STM32 + HAL, налаштування з CubeMX:
// TIM3 CH1 → R, CH2 → G, CH3 → B, усі три в режимі PWM Generation.
// Prescaler підібраний так, щоб при Period (ARR) = 255 вийшло ≈5 кГц;
// ARR = 255 дає шпаруватість 0…255 — рівно ті числа, з якими ми працюємо.
#include "main.h"

extern TIM_HandleTypeDef htim3;

static void leds_init(void) {
    HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);   // R
    HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_2);   // G
    HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_3);   // B
}

// Єдиний шлюз кольору. Запис у регістр порівняння каналу (CCR) — і є яскравість.
static void set_color(uint8_t r, uint8_t g, uint8_t b) {
    __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, r);
    __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_2, g);
    __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_3, b);
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_TIM3_Init();
    leds_init();

    while (1) {
        set_color(255,   0,   0); HAL_Delay(600);  // червоний
        set_color(  0, 255,   0); HAL_Delay(600);  // зелений
        set_color(  0,   0, 255); HAL_Delay(600);  // синій
        set_color(255, 255,   0); HAL_Delay(600);  // жовтий
        set_color(255, 255, 255); HAL_Delay(600);  // білий
    }
}
