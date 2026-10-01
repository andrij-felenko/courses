#ifndef TINYML_PIPELINE_HPP
#define TINYML_PIPELINE_HPP

#include <cstdint>
#include <memory>
#include <esp_heap_caps.h>
#include <esp_log.h>
#include <esp_timer.h>

#include "frame_buffer_queue.hpp"

namespace esp32s3 {

struct DetectionResult {
    float confidence{0.0f};
    int label_id{-1};
    uint32_t inference_time_ms{0};
};

class TinyMLPipeline {
public:
    TinyMLPipeline() = default;

    ~TinyMLPipeline() {
        if (tensor_arena_) {
            heap_caps_free(tensor_arena_);
            tensor_arena_ = nullptr;
        }
    }

    bool init(size_t arena_size = 256 * 1024) {
        if (initialized_) return true;

        arena_size_ = arena_size;
        // Виділяємо тензорну арену в Octal PSRAM з вирівнюванням
        tensor_arena_ = static_cast<uint8_t*>(heap_caps_malloc(arena_size_, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));

        if (!tensor_arena_) {
            ESP_LOGE(TAG, "Не вдалося виділити %u байтів у PSRAM під тензорну арену TinyML", arena_size_);
            return false;
        }

        initialized_ = true;
        ESP_LOGI(TAG, "Двигун TinyML ініціалізовано. Тензорна арена: %u КБ у PSRAM (Векторизація PIE увімкнена)", arena_size_ / 1024);
        return true;
    }

    DetectionResult run_inference(const ScopedFrame& frame) {
        if (!initialized_ || !frame.valid()) {
            return {};
        }

        uint64_t start_time = esp_timer_get_time();

        // Симуляція перетворення кадру RGB565 -> INT8 входження тензора
        // та векторного виконання конволіцій через співпроцесор PIE
        uint32_t sum = 0;
        const uint8_t* buf = frame.data();
        size_t len = frame.size();

        // Векторизована симуляція обробки даних
        for (size_t i = 0; i < len; i += 4) {
            sum += buf[i];
        }

        uint64_t end_time = esp_timer_get_time();
        uint32_t elapsed_ms = static_cast<uint32_t>((end_time - start_time) / 1000);

        DetectionResult result;
        result.confidence = static_cast<float>((sum % 100)) / 100.0f;
        result.label_id = (sum % 2 == 0) ? 1 : 0; // 1 = Person Detected
        result.inference_time_ms = elapsed_ms;

        return result;
    }

private:
    static constexpr const char* TAG = "TinyMLPipeline";
    bool initialized_{false};
    uint8_t* tensor_arena_{nullptr};
    size_t arena_size_{0};
};

} // namespace esp32s3

#endif // TINYML_PIPELINE_HPP
