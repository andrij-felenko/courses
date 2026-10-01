#include <cstddef>
#include <cstdint>
#include "esp_heap_caps.h"
#include "esp_cache.h"
#include "esp_log.h"

class PsramBufferManager {
private:
    static constexpr const char *TAG = "PsramCpp";

public:
    // Виділення та синхронізація вирівняного буфера PSRAM під C++
    static uint8_t* createAlignedBuffer(std::size_t size, std::size_t alignment) {
        void *raw_ptr = heap_caps_aligned_alloc(alignment, size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
        if (raw_ptr == nullptr) {
            ESP_LOGE(TAG, "Не вдалося виділити вирівняний буфер у PSRAM");
            return nullptr;
        }

        uint8_t *buffer = static_cast<uint8_t*>(raw_ptr);

        // Примусове скидання модифікованих даних з L1 кешу у фізичну PSRAM
        esp_err_t ret = esp_cache_msync(buffer, size, ESP_CACHE_MSYNC_FLAG_DIR_C2M | ESP_CACHE_MSYNC_FLAG_INVALIDATE);
        if (ret != ESP_OK) {
            ESP_LOGE(TAG, "Синхронізація esp_cache_msync завершилася з помилкою: %d", ret);
        }

        return buffer;
    }

    static void freeBuffer(uint8_t *buffer) {
        if (buffer != nullptr) {
            heap_caps_free(buffer);
        }
    }
};
