#include <stdint.h>
#include <stdlib.h>

/* Параметри конфігурації сервопривода MG90S */
#define SERVO_DEADBAND_US   4   /* Ширина зони нечутливості компаратора, мкс */
#define SERVO_MIN_PULSE_US  500 /* Мінімальна тривалість імпульсу (0°), мкс */
#define SERVO_MAX_PULSE_US  2500/* Максимальна тривалість імпульсу (180°), мкс */

typedef struct {
    uint16_t current_pulse_us;  /* Поточна зафіксована тривалість імпульсу */
    uint16_t deadband_us;       /* Захисний поріг гістерезису */
} servo_filter_t;

void servo_filter_init(servo_filter_t *filter, uint16_t initial_pulse_us) {
    if (initial_pulse_us < SERVO_MIN_PULSE_US) initial_pulse_us = SERVO_MIN_PULSE_US;
    if (initial_pulse_us > SERVO_MAX_PULSE_US) initial_pulse_us = SERVO_MAX_PULSE_US;
    filter->current_pulse_us = initial_pulse_us;
    filter->deadband_us = SERVO_DEADBAND_US;
}

/* Повертає 1, якщо значення оновлено, та 0, якщо зміна лежить у зоні нечутливості */
uint8_t servo_filter_update(servo_filter_t *filter, uint16_t target_pulse_us, uint16_t *filtered_pulse_us) {
    /* Програмне обмеження діапазону для запобігання заклинюванню */
    if (target_pulse_us < SERVO_MIN_PULSE_US) target_pulse_us = SERVO_MIN_PULSE_US;
    if (target_pulse_us > SERVO_MAX_PULSE_US) target_pulse_us = SERVO_MAX_PULSE_US;

    int32_t diff = (int32_t)target_pulse_us - (int32_t)filter->current_pulse_us;
    if (abs(diff) >= filter->deadband_us) {
        filter->current_pulse_us = target_pulse_us;
        *filtered_pulse_us = target_pulse_us;
        return 1; /* Потрібно записати нове значення в регістр CCR */
    }

    *filtered_pulse_us = filter->current_pulse_us;
    return 0; /* Зміна проігнорована для запобігання тремтінню */
}
