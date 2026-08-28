#include "driver/gpio.h"
#include "esp_rom_sys.h"          // esp_rom_delay_us()
#include "freertos/FreeRTOS.h"

#define WELD_GPIO  GPIO_NUM_12    // затвор силового MOSFET-ключа
#define PULSE1_US      1500       // «пробити»: 1.5 мс
#define GAP_US         3000       // пауза між імпульсами: 3 мс
#define PULSE2_US      5000       // «зварити»: 5 мс

static portMUX_TYPE weld_mux = portMUX_INITIALIZER_UNLOCKED;

void weld_init(void)
{
    gpio_config_t cfg = {
        .pin_bit_mask = 1ULL << WELD_GPIO,
        .mode         = GPIO_MODE_OUTPUT,
        .pull_down_en = GPIO_PULLDOWN_ENABLE,   // ключ закритий, поки МК не ожив
        .intr_type    = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&cfg));
    gpio_set_level(WELD_GPIO, 0);
}

void fire_weld(void)
{
    // критична секція: ані планувальник, ані Wi-Fi не влізуть посеред імпульсу
    portENTER_CRITICAL(&weld_mux);

    gpio_set_level(WELD_GPIO, 1);   // пробити оксид
    esp_rom_delay_us(PULSE1_US);
    gpio_set_level(WELD_GPIO, 0);

    esp_rom_delay_us(GAP_US);       // пауза

    gpio_set_level(WELD_GPIO, 1);   // сплавити ядро
    esp_rom_delay_us(PULSE2_US);
    gpio_set_level(WELD_GPIO, 0);

    portEXIT_CRITICAL(&weld_mux);
}
