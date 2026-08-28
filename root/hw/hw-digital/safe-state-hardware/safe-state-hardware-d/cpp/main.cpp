#include <stdint.h>

#define HEATER_ON   1
#define HEATER_OFF  0

/* Викликати НАЙПЕРШИМ у старті — до будь-якої логіки нагріву.
 * Поки виконуються ці рядки, зовнішня підтяжка-вниз уже тримає
 * лінію в 0 (нагрівач холодний), тож небезпечного вікна нема. */
void heater_init_safe(void) {
    gpio_set_level(PIN_HEATER, HEATER_OFF);  /* спершу задаємо безпечний рівень */
    gpio_set_direction(PIN_HEATER, GPIO_OUTPUT);  /* аж тоді вмикаємо драйвер */
}

/* Єдина точка ввімкнення — лише коли САМІ переконалися, що можна. */
void heater_set(int on, int sensor_ok) {
    if (on && sensor_ok)
        gpio_set_level(PIN_HEATER, HEATER_ON);
    else
        gpio_set_level(PIN_HEATER, HEATER_OFF);  /* сумнів → знеструмлюємо */
}
