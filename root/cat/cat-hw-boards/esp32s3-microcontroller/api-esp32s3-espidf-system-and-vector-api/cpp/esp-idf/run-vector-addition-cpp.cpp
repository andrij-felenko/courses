#include "esp_nn.h"
#include "esp_log.h"
#include <array>

namespace {
    constexpr const char* TAG = "ESP_NN";
}

void run_vector_addition_cpp() {
    constexpr int len = 16;
    std::array<int8_t, len> vec_a = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16};
    std::array<int8_t, len> vec_b = {10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10};
    std::array<int8_t, len> vec_out{};

    esp_nn_add_elementwise_s8(vec_a.data(), vec_b.data(), vec_out.data(), len);

    ESP_LOGI(TAG, "Результат другого елемента (C++): %d", vec_out[1]);
}
