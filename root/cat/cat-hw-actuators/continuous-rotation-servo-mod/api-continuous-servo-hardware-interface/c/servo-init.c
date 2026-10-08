/* Генерація ШІМ-сигналу керування сервоприводом на мові C */
#include <stdint.h>

#define SERVO_PIN 5
#define PWM_PERIOD_US 20000
#define NEUTRAL_PULSE_US 1500

/* Структура для опису стану привода */
typedef struct {
    uint16_t pulse_width_us;
} continuous_servo_t;

void servo_init(continuous_servo_t *servo) {
    servo->pulse_width_us = NEUTRAL_PULSE_US;
}

/* Встановлення швидкості: від -100 (макс. CCW) до +100 (макс. CW) */
void servo_set_speed(continuous_servo_t *servo, int8_t speed_pct) {
    if (speed_pct > 100) speed_pct = 100;
    if (speed_pct < -100) speed_pct = -100;

    /* Перетворення відсотків у тривалість імпульсу 1000-2000 мкс */
    servo->pulse_width_us = NEUTRAL_PULSE_US + (speed_pct * 5);
}
