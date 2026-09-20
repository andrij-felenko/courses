#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "bissc_encoder.h"

static const char *TAG = "MAIN_APP";

/**
 * @brief Фонова задача FreeRTOS для зчитування кутового положення з енкодера BiSS-C
 */
static void vBisscEncoderTask(void *pvParameters)
{
    bissc_frame_t frame;

    while (1) {
        esp_err_t err = bissc_encoder_read_frame(&frame);
        if (err == ESP_OK) {
            if (!frame.crc_valid) {
                ESP_LOGE(TAG, "Помилка контрольної суми CRC-6! Отримано: 0x%02X, Розраховано: 0x%02X",
                         frame.crc_received, frame.crc_calculated);
            } else if (frame.error_flag) {
                ESP_LOGW(TAG, "Апаратна помилка енкодера BiSS-C (Error Flag E)");
            } else {
                ESP_LOGI(TAG, "Кут: %6.2f deg | Позиція: %8lu | E: %d | W: %d | CRC: OK",
                         frame.angle_degrees,
                         (unsigned long)frame.position,
                         frame.error_flag ? 1 : 0,
                         frame.warning_flag ? 1 : 0);
            }
        } else {
            ESP_LOGE(TAG, "Помилка зчитування кадру BiSS-C: %s", esp_err_to_name(err));
        }

        // Частота оцифрування 100 Гц (10 мс)
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

void app_main(void)
{
    ESP_LOGI(TAG, "Запуск системи зчитування абсолютного енкодера BiSS-C");

    // Конфігурація 18-бітного оптичного абсолютного енкодера BiSS-C
    bissc_config_t config = {
        .spi_host = SPI2_HOST,
        .pin_ma = GPIO_NUM_18,        // Вивід тактування MA (Master Clock)
        .pin_slo = GPIO_NUM_19,       // Вивід даних SLO (Slave Out)
        .clock_speed_hz = 2000000,    // Частота тактування 2 МГц
        .data_bits = 18,              // 18-бітний диск (262144 дискрет/об)
        .is_gray_code = true          // Кодування маски в коді Ґрея
    };

    esp_err_t err = bissc_encoder_init(&config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Сбій ініціалізації драйвера BiSS-C енкодера");
        return;
    }

    // Створення фонової задачі зчитування кута з високим пріоритетом (10)
    xTaskCreate(vBisscEncoderTask, "bissc_encoder_task", 4096, NULL, 10, NULL);
}
