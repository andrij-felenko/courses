#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "esp_cpu.h"
#include "esp_timer.h"
#include "esp_log.h"

static const char *TAG = "PROFILER_PIPELINE";

#define NUM_SAMPLES 100
#define PIPELINE_STAGES 3

typedef struct {
    uint32_t stage_cycles[PIPELINE_STAGES];
    uint32_t total_cycles;
} pipeline_sample_t;

// Порівняльна функція для qsort
static int compare_uint32(const void *a, const void *b)
{
    uint32_t val_a = *(const uint32_t *)a;
    uint32_t val_b = *(const uint32_t *)b;
    if (val_a < val_b) return -1;
    if (val_a > val_b) return 1;
    return 0;
}

// Заглушки етапів обробки даних для демонстрації профілювання
static void stage_acquire_data(uint8_t *buffer, size_t len)
{
    for (size_t i = 0; i < len; i++) {
        buffer[i] = (uint8_t)(i & 0xFF);
    }
}

static void stage_filter_data(uint8_t *buffer, size_t len)
{
    // Вузьке місце: неефективна обробка в циклі
    for (size_t i = 0; i < len; i++) {
        buffer[i] = (buffer[i] ^ 0xAA) + 1;
    }
}

static void stage_transmit_data(const uint8_t *buffer, size_t len)
{
    volatile uint32_t dummy = 0;
    for (size_t i = 0; i < len; i++) {
        dummy += buffer[i];
    }
    (void)dummy;
}

void profile_pipeline_execution(void)
{
    uint8_t data_buffer[256];
    pipeline_sample_t samples[NUM_SAMPLES];
    uint32_t total_stage_sum[PIPELINE_STAGES] = {0};

    ESP_LOGI(TAG, "Запуск статистичного профілювання конвеєра (%d прогонів)...", NUM_SAMPLES);

    for (int s = 0; s < NUM_SAMPLES; s++) {
        uint32_t t0 = esp_cpu_get_cycle_count();
        stage_acquire_data(data_buffer, sizeof(data_buffer));
        
        uint32_t t1 = esp_cpu_get_cycle_count();
        stage_filter_data(data_buffer, sizeof(data_buffer));
        
        uint32_t t2 = esp_cpu_get_cycle_count();
        stage_transmit_data(data_buffer, sizeof(data_buffer));
        
        uint32_t t3 = esp_cpu_get_cycle_count();

        samples[s].stage_cycles[0] = t1 - t0;
        samples[s].stage_cycles[1] = t2 - t1;
        samples[s].stage_cycles[2] = t3 - t2;
        samples[s].total_cycles = t3 - t0;

        total_stage_sum[0] += samples[s].stage_cycles[0];
        total_stage_sum[1] += samples[s].stage_cycles[1];
        total_stage_sum[2] += samples[s].stage_cycles[2];
    }

    // Збір та сортування загальних тактів для перцентилів
    uint32_t totals[NUM_SAMPLES];
    for (int i = 0; i < NUM_SAMPLES; i++) {
        totals[i] = samples[i].total_cycles;
    }
    qsort(totals, NUM_SAMPLES, sizeof(uint32_t), compare_uint32);

    uint32_t p50_cycles = totals[NUM_SAMPLES / 2];
    uint32_t p99_cycles = totals[(NUM_SAMPLES * 99) / 100];
    uint32_t max_cycles = totals[NUM_SAMPLES - 1];

    ESP_LOGI(TAG, "--- РЕЗУЛЬТАТИ ПРОФІЛЮВАННЯ КОНВЕЄРА ---");
    ESP_LOGI(TAG, "Етап 1 (Acquire)  - Середнє: %lu тактів", total_stage_sum[0] / NUM_SAMPLES);
    ESP_LOGI(TAG, "Етап 2 (Filter)   - Середнє: %lu тактів [ВУЗЬКЕ МІСЦЕ]", total_stage_sum[1] / NUM_SAMPLES);
    ESP_LOGI(TAG, "Етап 3 (Transmit) - Середнє: %lu тактів", total_stage_sum[2] / NUM_SAMPLES);
    ESP_LOGI(TAG, "Перцентиль p50 загального часу: %lu тактів", p50_cycles);
    ESP_LOGI(TAG, "Перцентиль p99 загального часу: %lu тактів", p99_cycles);
    ESP_LOGI(TAG, "Найгірший випадок (Max): %lu тактів", max_cycles);
}
