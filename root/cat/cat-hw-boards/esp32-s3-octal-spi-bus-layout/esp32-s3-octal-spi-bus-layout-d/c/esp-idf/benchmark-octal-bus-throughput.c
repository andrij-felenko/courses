#include "esp_timer.h"
#include "esp_psram.h"
#include "esp_log.h"
#include "string.h"

static const char *TAG = "BUS_PERFORMANCE";

// Тест швидкодії та перевірка шини Octal SPI при роботі з масивами
void benchmark_octal_bus_throughput(void) {
    const size_t buffer_size = 1024 * 1024; // 1 МБ буфер
    uint32_t *spiram_buf = (uint32_t *)heap_caps_malloc(buffer_size, MALLOC_CAP_SPIRAM);
    
    if (spiram_buf == NULL) {
        ESP_LOGE(TAG, "Помилка виділення пам'яті у зоні SPIRAM");
        return;
    }

    int64_t start_time = esp_timer_get_time();

    // Запис 1 МБ блоку
    for (size_t i = 0; i < buffer_size / sizeof(uint32_t); i++) {
        spiram_buf[i] = (uint32_t)i;
    }

    int64_t write_time = esp_timer_get_time() - start_time;

    start_time = esp_timer_get_time();

    // Перевірка зчитування
    uint32_t checksum = 0;
    for (size_t i = 0; i < buffer_size / sizeof(uint32_t); i++) {
        checksum += spiram_buf[i];
    }

    int64_t read_time = esp_timer_get_time() - start_time;

    heap_caps_free(spiram_buf);

    double write_speed = (double)buffer_size / (write_time / 1000000.0) / (1024.0 * 1024.0);
    double read_speed = (double)buffer_size / (read_time / 1000000.0) / (1024.0 * 1024.0);

    ESP_LOGI(TAG, "Швидкість запису в Octal PSRAM: %.2f МБ/с", write_speed);
    ESP_LOGI(TAG, "Швидкість читання з Octal PSRAM: %.2f МБ/с", read_speed);
    ESP_LOGI(TAG, "Контрольна сума масиву: 0x%08X", (unsigned int)checksum);
}
