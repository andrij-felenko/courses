#include "driver/gpio.h"
#include "esp_log.h"
#include "esp_rom_sys.h"                   // esp_rom_delay_us()
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIN_DO  GPIO_NUM_4                 // вивід DO давача

static const char *TAG = "ky038";
static int idle_level;                     // рівень DO у тиші (визначимо самі)

// Прочитати рівень, що переважає в тиші: беремо більшість із багатьох відліків.
static int detect_idle_level(gpio_num_t pin, int samples) {
    int highs = 0;
    for (int i = 0; i < samples; i++) {
        if (gpio_get_level(pin)) highs++;
        esp_rom_delay_us(200);             // короткі паузи; загалом ~40 мс на всю оцінку
    }
    // Якщо більшість відліків були одиницями — спокій це 1, інакше 0.
    return (highs > samples / 2) ? 1 : 0;
}

void app_main(void) {
    gpio_config_t in = {
        .pin_bit_mask = 1ULL << PIN_DO,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,      // на платі вже є своя підтяжка
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&in));
    vTaskDelay(pdMS_TO_TICKS(300));        // дати мікрофону встановити зсув після ввімкнення
    idle_level = detect_idle_level(PIN_DO, 200);
    ESP_LOGI(TAG, "рівень спокою DO = %s",
             idle_level ? "1 (звук → 0)" : "0 (звук → 1)");
}
