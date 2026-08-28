/* ESP-IDF / C99: Бенчмарк та верифікація бітової точності */
void run_fc_benchmark_and_verify(void) {
    const int NUM_IN = 256;   // 256 входів (кратно 16)
    const int NUM_OUT = 128;  // 128 вихідних нейронів

    // 1. Виділяємо пам'ять суворо у внутрішній 16-байтній SRAM
    int8_t *input = (int8_t *)heap_caps_aligned_alloc(16, NUM_IN * sizeof(int8_t), MALLOC_CAP_INTERNAL);
    int8_t *weights = (int8_t *)heap_caps_aligned_alloc(16, NUM_IN * NUM_OUT * sizeof(int8_t), MALLOC_CAP_INTERNAL);
    int32_t *bias = (int32_t *)heap_caps_aligned_alloc(16, NUM_OUT * sizeof(int32_t), MALLOC_CAP_INTERNAL);
    int8_t *out_scalar = (int8_t *)heap_caps_aligned_alloc(16, NUM_OUT * sizeof(int8_t), MALLOC_CAP_INTERNAL);
    int8_t *out_simd = (int8_t *)heap_caps_aligned_alloc(16, NUM_OUT * sizeof(int8_t), MALLOC_CAP_INTERNAL);

    if (!input || !weights || !bias || !out_scalar || !out_simd) {
        ESP_LOGE(TAG, "Помилка виділення пам'яті під тестові тензори!");
        return;
    }

    // 2. Ініціалізація тестовими даними
    for (int i = 0; i < NUM_IN; i++) input[i] = (int8_t)((i % 255) - 128);
    for (int i = 0; i < NUM_IN * NUM_OUT; i++) weights[i] = (int8_t)((i % 127) - 64);
    for (int i = 0; i < NUM_OUT; i++) bias[i] = (i * 10) - 500;

    fc_quant_params_t params = {
        .input_offset = 12,
        .output_offset = -5,
        .output_multiplier = 1073741824, // 0.5 у Q31
        .output_shift = 31,
        .quantized_activation_min = -128,
        .quantized_activation_max = 127
    };

    // 3. Тест скалярного виконання
    uint32_t t0 = esp_cpu_get_cycle_count();
    fc_layer_scalar(input, weights, bias, out_scalar, NUM_IN, NUM_OUT, &params);
    uint32_t t1 = esp_cpu_get_cycle_count();
    uint32_t scalar_cycles = t1 - t0;

    // 4. Тест векторного SIMD-виконання
    uint32_t t2 = esp_cpu_get_cycle_count();
    fc_layer_simd(input, weights, bias, out_simd, NUM_IN, NUM_OUT, &params);
    uint32_t t3 = esp_cpu_get_cycle_count();
    uint32_t simd_cycles = t3 - t2;

    // 5. Верифікація бітової точності
    bool bit_exact = true;
    for (int i = 0; i < NUM_OUT; i++) {
        if (out_scalar[i] != out_simd[i]) {
            ESP_LOGE(TAG, "Розбіжність на індексі %d: Scalar=%d, SIMD=%d",
                     i, out_scalar[i], out_simd[i]);
            bit_exact = false;
            break;
        }
    }

    // 6. Звіт про результати
    float speedup = (float)scalar_cycles / (float)simd_cycles;
    ESP_LOGI(TAG, "Результати бенчмарку [%d -> %d]:", NUM_IN, NUM_OUT);
    ESP_LOGI(TAG, "• Скалярний код: %lu тактів (%.2f мкс при 240 МГц)",
             (unsigned long)scalar_cycles, (float)scalar_cycles / 240.0f);
    ESP_LOGI(TAG, "• Векторний SIMD: %lu тактів (%.2f мкс при 240 МГц)",
             (unsigned long)simd_cycles, (float)simd_cycles / 240.0f);
    ESP_LOGI(TAG, "• Прискорення:   %.2fx", speedup);
    ESP_LOGI(TAG, "• Верифікація:  %s", bit_exact ? "УСПІШНО (біт-у-біт)" : "ПОМИЛКА");

    free(input); free(weights); free(bias); free(out_scalar); free(out_simd);
}
