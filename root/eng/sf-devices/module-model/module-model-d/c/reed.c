/* reed.c — реалізація: деталі сховано (information hiding) */
#include "reed.h"
#include "driver/gpio.h"          /* GPIO ESP-IDF */

#define REED_PIN   GPIO_NUM_4     /* до якого піна припаяно — деталь модуля */
static const int ACTIVE_LEVEL = 0; /* геркон active-low: 0 = замкнено */

/* static → символ не видно поза цим файлом: інкапсуляція */
static int read_raw(void) {
    return gpio_get_level(REED_PIN);
}

void reed_init(void) {
    gpio_set_direction(REED_PIN, GPIO_MODE_INPUT);
    gpio_set_pull_mode(REED_PIN, GPIO_PULLUP_ONLY);  /* підтяжка тримає HIGH */
}

bool reed_is_closed(void) {
    return read_raw() == ACTIVE_LEVEL;   /* ховаємо «0 vs 1» від світу */
}
