#include <stdio.h>
#include "esp_heap_caps.h"
#include "esp_nn.h"
#include "esp_log.h"

static const char *TAG = "ESP_NN_DEMO";

void run_vector_matrix_multiplication(void)
{
    const int rows = 16;
    const int cols = 16;
    size_t data_size = rows * cols * sizeof(int8_t);

    // Виділення 16-байтово вирівняних буферів у внутрішній SRAM
    int8_t *matrix_a = (int8_t *)heap_caps_aligned_alloc(16, data_size, MALLOC_CAP_INTERNAL);
    int8_t *matrix_b = (int8_t *)heap_caps_aligned_alloc(16, data_size, MALLOC_CAP_INTERNAL);
    int32_t *out_matrix = (int32_t *)heap_caps_aligned_alloc(16, rows * cols * sizeof(int32_t), MALLOC_CAP_INTERNAL);

    if (!matrix_a || !matrix_b || !out_matrix) {
        ESP_LOGE(TAG, "Помилка виділення вирівняної пам'яті");
        return;
    }

    // Ініціалізація тестових даних
    for (int i = 0; i < rows * cols; i++) {
        matrix_a[i] = (int8_t)(i % 10);
        matrix_b[i] = (int8_t)(i % 5);
    }

    // Виклик оптимізованого векторного матричного множення з ESP-NN
    esp_nn_matmul_s8(matrix_a, matrix_b, out_matrix, rows, cols, cols);
    ESP_LOGI(TAG, "Векторне матричне множення успішно виконано через PIE");

    heap_caps_free(matrix_a);
    heap_caps_free(matrix_b);
    heap_caps_free(out_matrix);
}
