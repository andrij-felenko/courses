#include <cstdio>
#include "esp_heap_caps.h"
#include "esp_nn.h"
#include "esp_log.h"

static const char *TAG = "ESP_NN_DEMO_CPP";

class VectorMath {
public:
    static void ComputeMatrix() {
        const int rows = 16;
        const int cols = 16;
        std::size_t data_size = rows * cols * sizeof(int8_t);

        // Виділення 16-байтово вирівняних масивів
        auto *matrix_a = static_cast<int8_t *>(heap_caps_aligned_alloc(16, data_size, MALLOC_CAP_INTERNAL));
        auto *matrix_b = static_cast<int8_t *>(heap_caps_aligned_alloc(16, data_size, MALLOC_CAP_INTERNAL));
        auto *out_matrix = static_cast<int32_t *>(heap_caps_aligned_alloc(16, rows * cols * sizeof(int32_t), MALLOC_CAP_INTERNAL));

        if (!matrix_a || !matrix_b || !out_matrix) {
            ESP_LOGE(TAG, "Помилка виділення пам'яті");
            return;
        }

        for (int i = 0; i < rows * cols; i++) {
            matrix_a[i] = static_cast<int8_t>(i % 10);
            matrix_b[i] = static_cast<int8_t>(i % 5);
        }

        // Запуск векторно-прискореного множення
        esp_nn_matmul_s8(matrix_a, matrix_b, out_matrix, rows, cols, cols);
        ESP_LOGI(TAG, "Матричне множення виконано успішно");

        heap_caps_free(matrix_a);
        heap_caps_free(matrix_b);
        heap_caps_free(out_matrix);
    }
};
