#include <cstdint>
#include <array>
#include "esp_nn.h"
#include "esp_log.h"

class VectorAccelerator {
private:
    static constexpr const char *TAG = "ESP_NN_VECTOR";
    static constexpr size_t LEN = 16;
public:
    static void compute() {
        alignas(16) std::array<int8_t, LEN> src_a = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16};
        alignas(16) std::array<int8_t, LEN> src_b = {10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10};
        alignas(16) std::array<int8_t, LEN> dst = {0};

        int32_t mult = 1 << 30;
        int shift = 0;

        esp_nn_add_s8(src_a.data(), src_b.data(), 0, 0, mult, shift, 0, 0, dst.data(), LEN);

        ESP_LOGI(TAG, "Результат обчислення C++: %d", dst[0]);
    }
};
