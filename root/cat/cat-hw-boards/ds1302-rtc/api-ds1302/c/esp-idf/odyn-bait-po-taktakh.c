#include "driver/gpio.h"
#include "esp_rom_sys.h"        // esp_rom_delay_us() — мікросекундна пауза без RTOS

// Виставити один байт у мікросхему (біти 0..7, молодший уперед).
// DAT уже переведений на ВИХІД (gpio_set_direction).
static void shift_out_byte(uint8_t v) {
  for (int i = 0; i < 8; i++) {
    gpio_set_level(PIN_DAT, (v >> i) & 0x01);  // виставили біт i
    gpio_set_level(PIN_CLK, 1);                // ↑ фронт: мікросхема зчитала
    esp_rom_delay_us(1);
    gpio_set_level(PIN_CLK, 0);                // ↓ готуємось до наступного біта
    esp_rom_delay_us(1);
  }
}

// Забрати один байт із мікросхеми. DAT уже переведений на ВХІД.
static uint8_t shift_in_byte(void) {
  uint8_t v = 0;
  for (int i = 0; i < 8; i++) {
    // Мікросхема міняє біт по спадному фронту; читаємо ПІСЛЯ нього.
    if (gpio_get_level(PIN_DAT)) v |= (1 << i);
    gpio_set_level(PIN_CLK, 1);                // такт для наступного біта
    esp_rom_delay_us(1);
    gpio_set_level(PIN_CLK, 0);                // ↓ фронт: новий біт на лінії
    esp_rom_delay_us(1);
  }
  return v;
}
