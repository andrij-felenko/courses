#include "driver/gpio.h"
#include "rom/ets_sys.h"

uint8_t read_74hc165(gpio_num_t pin_pl, gpio_num_t pin_cp, gpio_num_t pin_q7) {
    uint8_t data = 0;

    // Фіксація паралельних даних у внутрішній регістр (Parallel Load)
    gpio_set_level(pin_pl, 0);
    ets_delay_us(1); // Затримка для стабілізації
    gpio_set_level(pin_pl, 1);
    ets_delay_us(1);

    // Зчитування 8 біт
    for (int i = 0; i < 8; i++) {
        // Читаємо старший біт, який вже доступний на Q7
        int bit_val = gpio_get_level(pin_q7);
        data = (data << 1) | bit_val;

        // Генеруємо тактовий імпульс для зсуву наступного біта
        gpio_set_level(pin_cp, 1);
        ets_delay_us(1);
        gpio_set_level(pin_cp, 0);
        ets_delay_us(1);
    }

    return data;
}
