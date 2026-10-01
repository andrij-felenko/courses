#include "esp_nn.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include <cstdint>

class VectorMathEngine {
private:
    static constexpr const char *TAG = "ESP_NN_CPP";

public:
    static int32_t dotProduct(const int8_t *vecA, const int8_t *vecB, size_t size) {
        int32_t result = 0;
        esp_nn_dot_product_s8(vecA, vecB, size, &result);
        return result;
    }

    static void execute() {
        constexpr size_t vecSize = 64;
        
        // Виділення вирівняних буферів за допомогою heap_caps_aligned_alloc
        auto *srcA = static_cast<int8_t *>(heap_caps_aligned_alloc(16, vecSize, MALLOC_CAP_INTERNAL));
        auto *srcB = static_cast<int8_t *>(heap_caps_aligned_alloc(16, vecSize, MALLOC_CAP_INTERNAL));

        if (srcA && srcB) {
            for (size_t i = 0; i < vecSize; ++i) {
                srcA[i] = static_cast<int8_t>(i);
                srcB[i] = 1;
            }

            int32_t res = dotProduct(srcA, srcB, vecSize);
            ESP_LOGI(TAG, "Векторний скалярний добуток (C++): %" PRIi32, res);

            heap_caps_free(srcA);
            heap_caps_free(srcB);
        }
    }
};
