#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_system.h"
#include "usb_console.h"
#include "psram_benchmark.h"

static const char *TAG = "MAIN";

// Розмір тестового буфера кадрового масиву (2 МБ)
#define BENCHMARK_BUFFER_SIZE (2 * 1024 * 1024)

void app_main(void)
{
    // 1. Ініціалізація нативної консолі USB CDC/JTAG ESP32-S3
    esp_err_t ret = usb_console_init();
    if (ret != ESP_OK) {
        // У разі помилки даємо невелику затримку та виводимо повідомлення у стандартний UART
        vTaskDelay(pdMS_TO_TICKS(100));
    }

    // Пауза 1 секунда для стабілізації підключення USB CDC термінала після скидання чипа
    vTaskDelay(pdMS_TO_TICKS(1000));

    ESP_LOGI(TAG, "==================================================");
    ESP_LOGI(TAG, "  ESP32-S3 PSRAM BANDWIDTH BENCHMARK & USB CONSOLE");
    ESP_LOGI(TAG, "==================================================");

    // 2. Перевірка наявності зовнішньої оперативної пам'яті PSRAM
    if (!psram_is_available()) {
        ESP_LOGE(TAG, "Помилка: Зовнішня PSRAM не виявлена!");
        ESP_LOGE(TAG, "Переконайтеся, що в sdkconfig включено CONFIG_SPIRAM=y.");
        return;
    }

    psram_print_info();

    // 3. Запуск вимірювання швидкості читання/запису
    psram_benchmark_result_t results;
    ret = psram_run_benchmark(BENCHMARK_BUFFER_SIZE, &results);

    if (ret == ESP_OK) {
        ESP_LOGI(TAG, "--------------------------------------------------");
        ESP_LOGI(TAG, "    РЕЗУЛЬТАТИ ТЕСТУВАННЯ ПРОПУСКНОЇ ЗДАТНОСТІ    ");
        ESP_LOGI(TAG, "--------------------------------------------------");
        ESP_LOGI(TAG, "Обсяг тестового буфера : %u байт (%.2f МБ)",
                 (unsigned int)results.buffer_size_bytes,
                 (double)results.buffer_size_bytes / (1024.0 * 1024.0));
        ESP_LOGI(TAG, "Послідовний запис      : %.2f МБ/с", results.seq_write_speed_mbps);
        ESP_LOGI(TAG, "Послідовне зчитування  : %.2f МБ/с", results.seq_read_speed_mbps);
        ESP_LOGI(TAG, "Довільний запис        : %.2f МБ/с", results.rand_write_speed_mbps);
        ESP_LOGI(TAG, "Довільне зчитування    : %.2f МБ/с", results.rand_read_speed_mbps);
        ESP_LOGI(TAG, "--------------------------------------------------");
        ESP_LOGI(TAG, "[Порівняння архітектур шини пам'яті]");
        ESP_LOGI(TAG, "  Octal SPI (8-біт, 80 МГц) : теор. пропускна здатність до 80 МБ/с");
        ESP_LOGI(TAG, "  Quad SPI  (4-біт, 80 МГц) : теор. пропускна здатність до 40 МБ/с");
        ESP_LOGI(TAG, "--------------------------------------------------");
    } else {
        ESP_LOGE(TAG, "Виконання бенчмарка перервано через помилку: %s", esp_err_to_name(ret));
    }
}
