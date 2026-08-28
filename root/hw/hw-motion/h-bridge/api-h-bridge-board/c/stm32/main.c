#include "stm32f4xx_hal.h"
extern TIM_HandleTypeDef htim3;              // ARR = 255 → шпаруватість теж 0..255

// speed: -255..+255 (знак = напрямок, модуль = шпаруватість каналу EN).
void motor_drive(int speed) {
    if (speed >  255) speed =  255;          // обрізаємо до діапазону ШІМ
    if (speed < -255) speed = -255;
    int duty = speed < 0 ? -speed : speed;   // модуль = швидкість

    HAL_GPIO_WritePin(IN1_GPIO_Port, IN1_Pin,        // напрямок: вперед при speed >= 0
                      speed >= 0 ? GPIO_PIN_SET : GPIO_PIN_RESET);
    HAL_GPIO_WritePin(IN2_GPIO_Port, IN2_Pin,
                      speed <  0 ? GPIO_PIN_SET : GPIO_PIN_RESET);
    __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, speed == 0 ? 0 : duty);
}
