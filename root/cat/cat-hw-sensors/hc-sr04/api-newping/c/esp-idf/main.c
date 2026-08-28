// ESP-IDF 5.x. ECHO — ТІЛЬКИ через подільник 1к/2к (5 В → ~3.3 В), VCC модуля — 5 В.
#include "driver/gpio.h"
#include "esp_timer.h"
#include "esp_rom_sys.h"          // esp_rom_delay_us()
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define TRIG_GPIO        GPIO_NUM_5
#define ECHO_GPIO        GPIO_NUM_18      // сюди приходить середина подільника
#define ECHO_TIMEOUT_US  40000            // трохи більше за апаратні ~38 мс модуля

static const char *TAG = "hc-sr04";

static void hcsr04_init(void)
{
    gpio_config_t trig = {
        .pin_bit_mask = 1ULL << TRIG_GPIO,
        .mode         = GPIO_MODE_OUTPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&trig));

    gpio_config_t echo = trig;
    echo.pin_bit_mask  = 1ULL << ECHO_GPIO;
    echo.mode          = GPIO_MODE_INPUT;
    ESP_ERROR_CHECK(gpio_config(&echo));

    gpio_set_level(TRIG_GPIO, 0);
}

// Повертає відстань у см, або 0 — якщо луни не було (порожньо / поза межами).
static unsigned hcsr04_measure_cm(void)
{
    // Такт 1: чистий поштовх 10 мкс (esp_rom_delay_us не віддає процесор — тут це й треба).
    gpio_set_level(TRIG_GPIO, 0); esp_rom_delay_us(2);
    gpio_set_level(TRIG_GPIO, 1); esp_rom_delay_us(10);
    gpio_set_level(TRIG_GPIO, 0);

    // Такт 2: чекаємо фронту ECHO — але не довше за тайм-аут, інакше зависнемо.
    int64_t t0 = esp_timer_get_time();            // мікросекунди від старту
    while (gpio_get_level(ECHO_GPIO) == 0)
        if (esp_timer_get_time() - t0 > ECHO_TIMEOUT_US) return 0;

    // Такт 3: ширина високого рівня = час польоту t, мкс.
    int64_t rise = esp_timer_get_time();
    while (gpio_get_level(ECHO_GPIO) == 1)
        if (esp_timer_get_time() - rise > ECHO_TIMEOUT_US) return 0;

    return (unsigned)((esp_timer_get_time() - rise) / 58);   // Такт 4: мкс → см
}

void app_main(void)
{
    hcsr04_init();
    for (;;) {
        unsigned cm = hcsr04_measure_cm();
        if (cm == 0) ESP_LOGI(TAG, "out of range");   // не плутати з «0 см»!
        else         ESP_LOGI(TAG, "%u cm", cm);
        vTaskDelay(pdMS_TO_TICKS(60));                // пауза між вимірами ≥ 60 мс
    }
}
