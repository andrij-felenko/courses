#include "camera_psram_config.h"
#include "esp_log.h"
#include "esp_heap_caps.h"

static const char *TAG = "CAM_PSRAM_CFG";

esp_err_t check_psram_availability(size_t *free_psram, size_t *min_free_psram)
{
    // Опитування доступної оперативної пам'яті за допомогою маски MALLOC_CAP_SPIRAM
    size_t psram_free = heap_caps_get_free_size(MALLOC_CAP_SPIRAM);
    size_t psram_min_free = heap_caps_get_minimum_free_size(MALLOC_CAP_SPIRAM);

    if (free_psram) {
        *free_psram = psram_free;
    }
    if (min_free_psram) {
        *min_free_psram = psram_min_free;
    }

    if (psram_free == 0) {
        ESP_LOGW(TAG, "Octal PSRAM не виявлено або не ініціалізовано в sdkconfig");
        return ESP_ERR_NOT_FOUND;
    }

    ESP_LOGI(TAG, "Зовнішню Octal PSRAM успішно виявлено:");
    ESP_LOGI(TAG, "  Вільний обсяг: %u байт (%.2f МБ)", psram_free, (float)psram_free / (1024.0f * 1024.0f));
    ESP_LOGI(TAG, "  Мінімальний вільний залишок: %u байт", psram_min_free);

    return ESP_OK;
}

esp_err_t configure_camera_for_psram(camera_config_t *config, bool *uses_psram)
{
    if (!config) {
        return ESP_ERR_INVALID_ARG;
    }

    // Призначення виводів шини даних та синхронізації Waveshare ESP32-S3R2
    config->pin_pwdn  = CAM_PIN_PWDN;
    config->pin_reset = CAM_PIN_RESET;
    config->pin_xclk  = CAM_PIN_XCLK;
    config->pin_siod  = CAM_PIN_SIOD;
    config->pin_sioc  = CAM_PIN_SIOC;

    config->pin_d7    = CAM_PIN_D7;
    config->pin_d6    = CAM_PIN_D6;
    config->pin_d5    = CAM_PIN_D5;
    config->pin_d4    = CAM_PIN_D4;
    config->pin_d3    = CAM_PIN_D3;
    config->pin_d2    = CAM_PIN_D2;
    config->pin_d1    = CAM_PIN_D1;
    config->pin_d0    = CAM_PIN_D0;

    config->pin_vsync = CAM_PIN_VSYNC;
    config->pin_href  = CAM_PIN_HREF;
    config->pin_pclk  = CAM_PIN_PCLK;

    // Частота тактування генератора XCLK (20 МГц для стабільного захоплення)
    config->xclk_freq_hz = 20000000;
    config->ledc_timer   = LEDC_TIMER_0;
    config->ledc_channel = LEDC_CHANNEL_0;

    config->pixel_format = PIXFORMAT_JPEG;
    config->jpeg_quality = 10; // Діапазон 0-63 (чим менше значення, тим вища якість)

    // Перевірка обсягу PSRAM для вибору стратегії буферизації
    size_t free_psram = 0;
    esp_err_t err = check_psram_availability(&free_psram, NULL);

    if (err == ESP_OK && free_psram >= MIN_PSRAM_FOR_DOUBLE_BUFFER) {
        // Конфігурація для Octal PSRAM: висока роздільна здатність і подвійна буферизація
        config->frame_size = FRAMESIZE_UXGA; // 1600x1200
        config->fb_location = CAMERA_FB_IN_PSRAM;
        config->fb_count = 2; // Подвійний кадровий буфер у PSRAM
        config->grab_mode = CAMERA_GRAB_LATEST;

        if (uses_psram) {
            *uses_psram = true;
        }
        ESP_LOGI(TAG, "Конфігурація камери: UXGA (1600x1200), 2 буфери в Octal PSRAM");
    } else {
        // Режим сумісності без PSRAM: розміщення буфера у внутрішній SRAM
        config->frame_size = FRAMESIZE_QVGA; // 320x240
        config->fb_location = CAMERA_FB_IN_DRAM;
        config->fb_count = 1;
        config->grab_mode = CAMERA_GRAB_WHEN_EMPTY;

        if (uses_psram) {
            *uses_psram = false;
        }
        ESP_LOGW(TAG, "Конфігурація сумісності: QVGA (320x240), 1 буфер у внутрішній SRAM");
    }

    return ESP_OK;
}
