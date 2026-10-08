#include "esp_psram.h"
#include "esp_log.h"
#include "esp_err.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "OCTAL_SPI_INIT";

// Ініціалізація та перевірка конфігурації Octal PSRAM DDR
esp_err_t check_octal_psram_status(void) {
    if (!esp_psram_is_initialized()) {
        ESP_LOGE(TAG, "Octal PSRAM не ініціалізована ROM-завантажником!");
        return ESP_FAIL;
    }

    size_t psram_size = esp_psram_get_size();
    ESP_LOGI(TAG, "Успішно виявлено Octal PSRAM об'ємом: %d МБ", (int)(psram_size / (1024 * 1024)));

    // Тестове виділення пам'яті у зовнішньому зоні PSRAM
    uint32_t *test_buffer = (uint32_t *)heap_caps_malloc(1024 * sizeof(uint32_t), MALLOC_CAP_SPIRAM);
    if (test_buffer == NULL) {
        ESP_LOGE(TAG, "Не вдалося виділити буфер у Octal PSRAM");
        return ESP_ERR_NO_MEM;
    }

    // Запис та перевірка даних по 8-бітній шині DDR
    for (int i = 0; i < 1024; i++) {
        test_buffer[i] = 0xAA55AA55 ^ i;
    }

    bool test_passed = true;
    for (int i = 0; i < 1024; i++) {
        if (test_buffer[i] != (0xAA55AA55 ^ i)) {
            test_passed = false;
            break;
        }
    }

    heap_caps_free(test_buffer);

    if (test_passed) {
        ESP_LOGI(TAG, "Тест цілісності даних Octal PSRAM DDR пройдено успішно");
        return ESP_OK;
    } else {
        ESP_LOGE(TAG, "Помилка цілісності даних на шині Octal SPI!");
        return ESP_FAIL;
    }
}
