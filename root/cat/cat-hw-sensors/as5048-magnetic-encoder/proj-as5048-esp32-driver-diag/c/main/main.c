#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "driver/spi_master.h"
#include "driver/gpio.h"
#include "as5048.h"

static const char *TAG = "MAIN";

// Призначення виводів шини SPI2 (HSPI) для ESP32
#define PIN_NUM_MISO GPIO_NUM_19
#define PIN_NUM_MOSI GPIO_NUM_23
#define PIN_NUM_CLK  GPIO_NUM_18
#define PIN_NUM_CS   GPIO_NUM_5

void app_main(void)
{
    ESP_LOGI(TAG, "Старт системи зчитування кутового енкодера AS5048 (ESP-IDF C)");

    // Конфігурація апаратної шини SPI2 (HSPI)
    spi_bus_config_t buscfg = {
        .miso_io_num = PIN_NUM_MISO,
        .mosi_io_num = PIN_NUM_MOSI,
        .sclk_io_num = PIN_NUM_CLK,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1,
        .max_transfer_sz = 32
    };

    esp_err_t ret = spi_bus_initialize(SPI2_HOST, &buscfg, SPI_DMA_CH_AUTO);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації шини SPI: %s", esp_err_to_name(ret));
        return;
    }

    // Параметри підключення пристрою AS5048
    as5048_config_t dev_cfg = {
        .spi_host = SPI2_HOST,
        .cs_io_num = PIN_NUM_CS,
        .clock_speed_hz = 1000000, // 1 МГц
        .zero_offset = 0
    };

    as5048_handle_t encoder_handle = NULL;
    ret = as5048_init(&dev_cfg, &encoder_handle);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації пристрою AS5048: %s", esp_err_to_name(ret));
        return;
    }

    ESP_LOGI(TAG, "Давач AS5048 успішно ініціалізовано на шині SPI");

    // Затримка 50 мс для завершення стабілізації CORDIC після подачі живлення
    vTaskDelay(pdMS_TO_TICKS(50));

    // Початкова перевірка діагностичного стану магнітного поля
    as5048_diag_status_t diag;
    if (as5048_get_diagnostics(encoder_handle, &diag) == ESP_OK) {
        ESP_LOGI(TAG, "Діагностика AS5048: AGC=%d | OCF=%d | COF=%d | MAGH=%d | MAGL=%d",
                 diag.agc_val, diag.ocf, diag.cof, diag.magh, diag.magl);
        if (diag.magh) {
            ESP_LOGW(TAG, "Попередження: Магнітне поле занадто сильне (MAGH = 1)");
        } else if (diag.magl) {
            ESP_LOGW(TAG, "Попередження: Магнітне поле занадто слабке (MAGL = 1)");
        }
    }

    // Програмне калібрування: встановлюємо поточне положення ротора за 0.0°
    ESP_LOGI(TAG, "Виконується калібрування нульової позиції енкодера...");
    ret = as5048_calibrate_zero(encoder_handle);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Помилка виконання калібрування нуля");
    }

    // Основний цикл опитування кута та моніторингу
    int diag_counter = 0;
    while (1) {
        float degrees = 0.0f;
        uint16_t raw_angle = 0;

        esp_err_t err_raw = as5048_read_raw_angle(encoder_handle, &raw_angle);
        esp_err_t err_deg = as5048_read_angle(encoder_handle, &degrees);

        if (err_deg == ESP_OK && err_raw == ESP_OK) {
            ESP_LOGI(TAG, "Кут: %6.2f° | Відлік (Raw): %5u (0x%04X)", degrees, raw_angle, raw_angle);
        } else {
            ESP_LOGE(TAG, "Помилка зчитання даних кутового положення");
        }

        // Періодичне виведення AGC-телеметрії кожні 2 секунди (20 * 100 мс)
        if (++diag_counter >= 20) {
            diag_counter = 0;
            if (as5048_get_diagnostics(encoder_handle, &diag) == ESP_OK) {
                ESP_LOGI(TAG, "[Телеметрія AGC] Підсилення: %3d/255 | Стан: %s",
                         diag.agc_val,
                         (diag.magh ? "ПОЛЕ_СИЛЬНЕ" : (diag.magl ? "ПОЛЕ_СЛАБКЕ" : "НОРМА")));
            }
        }

        vTaskDelay(pdMS_TO_TICKS(100)); // Опитування з частотою 10 Гц
    }

    // Очищення ресурсів перед завершенням
    as5048_deinit(encoder_handle);
    spi_bus_free(SPI2_HOST);
}
