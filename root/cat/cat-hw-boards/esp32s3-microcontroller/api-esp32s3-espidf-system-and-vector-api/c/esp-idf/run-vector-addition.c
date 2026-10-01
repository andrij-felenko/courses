#include "esp_nn.h"
#include "esp_log.h"

static const char *TAG = "ESP_NN";

void run_vector_addition(void) {
    const int len = 16;
    int8_t vec_a[16] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16};
    int8_t vec_b[16] = {10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10};
    int8_t vec_out[16];

    esp_nn_add_elementwise_s8(vec_a, vec_b, vec_out, len);

    ESP_LOGI(TAG, "Результат другого елемента: %d", vec_out[1]);
}
