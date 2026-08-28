#include "driver/gpio.h"
#include "driver/ledc.h"                     // канал ШІМ, таймер на 8 біт → duty 0..255

// speed: -255..+255 (знак = напрямок, модуль = шпаруватість каналу EN).
void motor_drive(int speed) {
    if (speed >  255) speed =  255;          // обрізаємо до діапазону ШІМ
    if (speed < -255) speed = -255;
    int duty = speed < 0 ? -speed : speed;   // модуль = швидкість

    gpio_set_level(PIN_IN1, speed >= 0);     // напрямок: вперед при speed >= 0
    gpio_set_level(PIN_IN2, speed <  0);
    ledc_set_duty(LEDC_LOW_SPEED_MODE, EN_CH, speed == 0 ? 0 : duty);
    ledc_update_duty(LEDC_LOW_SPEED_MODE, EN_CH);   // нове значення набирає чинності
}
