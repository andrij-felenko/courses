#include "psram_benchmark.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "esp_log.h"
#include "esp_heap_caps.h"
#include "esp_timer.h"

static const char *TAG = "PSRAM_BENCH";

bool psram_is_available(void)
{
    size_t total_psram = heap_caps_get_total_size(MALLOC_CAP_SPIRAM);
    return (total_psram > 0);
}

void psram_print_info(void)
{
    size_t total_psram = heap_caps_get_total_size(MALLOC_CAP_SPIRAM);
    size_t free_psram = heap_caps_get_free_size(MALLOC_CAP_SPIRAM);

    ESP_LOGI(TAG, "--- Параметри зовнішньої пам'яті PSRAM ---");
    ESP_LOGI(TAG, "Загальний обсяг PSRAM : %u байт (%.2f МБ)",
             (unsigned int)total_psram, (double)total_psram / (1024.0 * 1024.0));
    ESP_LOGI(TAG, "Вільний обсяг PSRAM   : %u байт (%.2f МБ)",
             (unsigned int)free_psram, (double)free_psram / (1024.0 * 1024.0));
}

void *psram_allocate_buffer(size_t size)
{
    // Явне виділення пам'яті у зовнішній PSRAM з можливістю побайтового доступу
    void *ptr = heap_caps_malloc(size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    if (ptr == NULL) {
        ESP_LOGE(TAG, "Помилка аллокації: не вдалося виділити %u байт у PSRAM!", (unsigned int)size);
    } else {
        ESP_LOGI(TAG, "Успішно виділено %u байт у PSRAM за адресою %p",
                 (unsigned int)size, ptr);
    }
    return ptr;
}

void psram_free_buffer(void *ptr)
{
    if (ptr != NULL) {
        heap_caps_free(ptr);
        ESP_LOGI(TAG, "Звільнено буфер PSRAM за адресою %p", ptr);
    }
}

esp_err_t psram_run_benchmark(size_t buffer_size, psram_benchmark_result_t *result)
{
    if (result == NULL || buffer_size == 0) {
        return ESP_ERR_INVALID_ARG;
    }

    if (!psram_is_available()) {
        ESP_LOGE(TAG, "Тестування скасовано: PSRAM відсутня або не ініціалізована.");
        return ESP_FAIL;
    }

    // Виділення буфера 32-бітних слів у PSRAM
    uint32_t *buf = (uint32_t *)psram_allocate_buffer(buffer_size);
    if (buf == NULL) {
        return ESP_ERR_NO_MEM;
    }

    size_t num_words = buffer_size / sizeof(uint32_t);
    result->buffer_size_bytes = buffer_size;

    ESP_LOGI(TAG, "Старт тестування пропускної здатності для буфера %u байт...", (unsigned int)buffer_size);

    // 1. Послідовний запис (Sequential Write)
    int64_t start_time = esp_timer_get_time();
    for (size_t i = 0; i < num_words; i++) {
        buf[i] = (uint32_t)(i ^ 0x5A5A5A5A);
    }
    int64_t end_time = esp_timer_get_time();
    int64_t seq_write_dur = end_time - start_time;
    result->seq_write_speed_mbps = ((double)buffer_size / (1024.0 * 1024.0)) / ((double)seq_write_dur / 1000000.0);

    // 2. Послідовне зчитування (Sequential Read)
    // Використання volatile запобігає вилученню циклу оптимізатором компілятора
    volatile uint32_t accumulator = 0;
    start_time = esp_timer_get_time();
    for (size_t i = 0; i < num_words; i++) {
        accumulator += buf[i];
    }
    end_time = esp_timer_get_time();
    int64_t seq_read_dur = end_time - start_time;
    result->seq_read_speed_mbps = ((double)buffer_size / (1024.0 * 1024.0)) / ((double)seq_read_dur / 1000000.0);

    (void)accumulator; // Запобігання ложному попередженню невикористаної змінної

    // Фіксоване зерно генератора для одинакової послідовності псевдовипадкових індексів
    const uint32_t seed = 0x12345678;

    // 3. Довільний запис (Random Write)
    uint32_t state = seed;
    start_time = esp_timer_get_time();
    for (size_t i = 0; i < num_words; i++) {
        state = state * 1664525u + 1013904223u; // Linear Congruential Generator (LCG)
        size_t idx = state % num_words;
        buf[idx] = (uint32_t)(i + state);
    }
    end_time = esp_timer_get_time();
    int64_t rand_write_dur = end_time - start_time;
    result->rand_write_speed_mbps = ((double)buffer_size / (1024.0 * 1024.0)) / ((double)rand_write_dur / 1000000.0);

    // 4. Довільне зчитування (Random Read)
    state = seed;
    accumulator = 0;
    start_time = esp_timer_get_time();
    for (size_t i = 0; i < num_words; i++) {
        state = state * 1664525u + 1013904223u;
        size_t idx = state % num_words;
        accumulator += buf[idx];
    }
    end_time = esp_timer_get_time();
    int64_t rand_read_dur = end_time - start_time;
    result->rand_read_speed_mbps = ((double)buffer_size / (1024.0 * 1024.0)) / ((double)rand_read_dur / 1000000.0);

    (void)accumulator;

    // Звільнення ресурсу
    psram_free_buffer(buf);

    return ESP_OK;
}
