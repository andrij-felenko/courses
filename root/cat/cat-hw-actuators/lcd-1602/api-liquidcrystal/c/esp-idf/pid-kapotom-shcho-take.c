#include "driver/gpio.h"
#include "esp_rom_sys.h"       // esp_rom_delay_us() — активне очікування в мікросекундах
                               // (vTaskDelay сюди не годиться: його крок — цілий тик)

// Виставити один напівбайт (молодші 4 біти value) на лінії D4–D7
static void put_nibble(uint8_t value) {
    for (int i = 0; i < 4; i++)
        gpio_set_level(LCD_DATA[i], (value >> i) & 1);
}

// Клацнути строб: підняти E, витримати, опустити — на спаді контролер читає лінії
static void pulse_e(void) {
    gpio_set_level(LCD_E, 1);
    esp_rom_delay_us(1);       // тримаємо E високим ≥ 0.45 мкс (беремо із запасом)
    gpio_set_level(LCD_E, 0);
    esp_rom_delay_us(50);      // даємо контролеру перетравити (звичайна команда ~37 мкс)
}
