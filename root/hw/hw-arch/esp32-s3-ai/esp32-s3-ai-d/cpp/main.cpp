// ESP-IDF / C++20: RAII-обгортка тензорної арени у швидкій внутрішній SRAM
#include <cstdint>
#include <cstddef>
#include <span>
#include <memory>
#include "esp_heap_caps.h"
#include "esp_log.h"

namespace ai {

static constexpr const char *TAG = "ESP32S3_AI_CPP";
static constexpr std::size_t AlignmentBytes = 16;

class AlignedTensorArena {
public:
    explicit AlignedTensorArena(std::size_t size)
        : requested_size_(size), raw_memory_(nullptr), aligned_span_{} {
        
        // Виділення строго у внутрішній SRAM з підтримкою DMA
        void *raw = heap_caps_malloc(
            size + AlignmentBytes,
            MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT | MALLOC_CAP_DMA
        );

        if (!raw) {
            ESP_LOGE(TAG, "Не вдалося виділити %zu байтів у внутрішній SRAM", size);
            return;
        }

        raw_memory_ = static_cast<std::uint8_t *>(raw);

        // Обчислення вирівняної адреси
        auto raw_addr = reinterpret_cast<std::uintptr_t>(raw_memory_);
        auto aligned_addr = (raw_addr + (AlignmentBytes - 1)) & ~(AlignmentBytes - 1);
        auto *aligned_ptr = reinterpret_cast<std::uint8_t *>(aligned_addr);

        aligned_span_ = std::span<std::uint8_t>(aligned_ptr, size);

        ESP_LOGI(TAG, "C++ Tensor Arena: %zu КБ виділено за адресою %p",
                 size / 1024, aligned_ptr);
    }

    ~AlignedTensorArena() noexcept {
        if (raw_memory_) {
            free(raw_memory_);
            raw_memory_ = nullptr;
        }
    }

    // Заборона копіювання для запобігання подвійному звільненню
    AlignedTensorArena(const AlignedTensorArena &) = delete;
    AlignedTensorArena &operator=(const AlignedTensorArena &) = delete;

    // Дозвіл переміщення
    AlignedTensorArena(AlignedTensorArena &&other) noexcept
        : requested_size_(other.requested_size_),
          raw_memory_(other.raw_memory_),
          aligned_span_(other.aligned_span_) {
        other.raw_memory_ = nullptr;
        other.aligned_span_ = {};
    }

    [[nodiscard]] bool is_valid() const noexcept { return !aligned_span_.empty(); }
    [[nodiscard]] std::span<std::uint8_t> span() noexcept { return aligned_span_; }
    [[nodiscard]] std::uint8_t *data() noexcept { return aligned_span_.data(); }
    [[nodiscard]] std::size_t size() const noexcept { return aligned_span_.size(); }

private:
    std::size_t requested_size_{0};
    std::uint8_t *raw_memory_{nullptr};
    std::span<std::uint8_t> aligned_span_{};
};

} // namespace ai
