#include "driver/gpio.h"
#include "esp_rom_sys.h"        // esp_rom_delay_us() — пауза без віддачі керування

#define LOAD_PIN  GPIO_NUM_5    // MOSFET підмикає резистор-«гирю» до виходу
#define TRIG_PIN  GPIO_NUM_6    // зовнішній запуск осцилографа

void load_pins_init(void) {
    gpio_config_t cfg = {
        .pin_bit_mask = (1ULL << LOAD_PIN) | (1ULL << TRIG_PIN),
        .mode = GPIO_MODE_OUTPUT,
    };
    gpio_config(&cfg);
}

void load_step(void) {
    gpio_set_level(TRIG_PIN, 1);    // спершу армуємо запуск осцилографа
    gpio_set_level(LOAD_PIN, 1);    // тим самим тактом — різко даємо повне навантаження
    esp_rom_delay_us(500);          // тримаємо, поки контур відпрацює провал і дзвін
    gpio_set_level(LOAD_PIN, 0);    // знімаємо навантаження
    gpio_set_level(TRIG_PIN, 0);
}
