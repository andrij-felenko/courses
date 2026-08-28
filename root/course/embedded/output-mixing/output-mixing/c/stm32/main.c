#include "stm32f4xx_hal.h"

#define SERVO_PORT  GPIOB
#define SERVO_PIN   GPIO_PIN_6
#define FRAME_US    20000                   // кадр 20 мс = 50 Гц

// кут 0..180°  →  ширина 1000..2000 мкс (лінійна підстановка)
static int angle_to_us(int deg) {
    if (deg < 0)   deg = 0;
    if (deg > 180) deg = 180;
    return 1000 + (int)((long)deg * 1000 / 180);  // 0°→1000, 90°→1500, 180°→2000
}

// HAL_Delay() рахує лише мілісекунди, тож мікросекунди беремо
// з вільного лічильника таймера, налаштованого на тік 1 мкс
extern TIM_HandleTypeDef htim2;
static void delay_us(uint32_t us) {
    uint32_t t0 = __HAL_TIM_GET_COUNTER(&htim2);
    while ((uint32_t)(__HAL_TIM_GET_COUNTER(&htim2) - t0) < us) { }
}

// один кадр: імпульс заданої ширини + добивання паузи до 20 мс
static void servo_frame(uint32_t width_us) {
    HAL_GPIO_WritePin(SERVO_PORT, SERVO_PIN, GPIO_PIN_SET);
    delay_us(width_us);                           // ширина = кут
    HAL_GPIO_WritePin(SERVO_PORT, SERVO_PIN, GPIO_PIN_RESET);
    delay_us(FRAME_US - width_us);                // решта кадру — пауза
}
