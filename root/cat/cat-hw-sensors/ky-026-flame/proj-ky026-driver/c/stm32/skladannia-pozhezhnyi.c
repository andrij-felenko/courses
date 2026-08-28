/* ── Пожежний робот на STM32 HAL: напрямок — GPIO, швидкість — канали TIM2 ──
   AO лівого давача — ADC1_IN0 (PA0), правого — ADC1_IN1 (PA1).
   TIM2 зведений у CubeMX на PWM, Period = 255 → duty теж 0..255. */
#include <stdlib.h>

#define L_DIR_PORT GPIOB
#define L_DIR_PIN  GPIO_PIN_4
#define R_DIR_PORT GPIOB
#define R_DIR_PIN  GPIO_PIN_5
#define FAN_PORT   GPIOB
#define FAN_PIN    GPIO_PIN_6          /* ключ вентилятора-гасія */

extern TIM_HandleTypeDef htim2;

static void motors_init(void) {
    HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_1);   /* лівий борт */
    HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_2);   /* правий борт */
}

static void drive(int left, int right) {   /* швидкості −255..+255 (знак = напрямок) */
    HAL_GPIO_WritePin(L_DIR_PORT, L_DIR_PIN, left  >= 0 ? GPIO_PIN_SET : GPIO_PIN_RESET);
    HAL_GPIO_WritePin(R_DIR_PORT, R_DIR_PIN, right >= 0 ? GPIO_PIN_SET : GPIO_PIN_RESET);
    int dl = abs(left),  dr = abs(right);
    if (dl > 255) dl = 255;
    if (dr > 255) dr = 255;
    __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_1, dl);
    __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_2, dr);
}
