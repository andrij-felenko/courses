#include <stdio.h>
#include "esp_nn.h"
#include "esp_log.h"

static const char *TAG = "ESP_NN_VECTOR";

void run_vector_acceleration_example(void) {
    #define VECTOR_LEN 16
    int8_t input_a[VECTOR_LEN] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16};
    int8_t input_b[VECTOR_LEN] = {10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10};
    int8_t output[VECTOR_LEN] = {0};

    // Параметри квантування
    int32_t mult = 1 << 30; // Масштаб 1.0
    int shift = 0;

    // Виклик прискореного векторного додавання із задіянням інструкцій PIE
    esp_nn_add_s8(input_a, input_b, 0, 0, mult, shift, 0, 0, output, VECTOR_LEN);

    ESP_LOGI(TAG, "Результат першого елемента вектора: %d", output[0]);
}
