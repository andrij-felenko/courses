#include "FrameBuffer.hpp"
#include "esp_log.h"
#include "esp_timer.h"
#include <cstring>

static const char* TAG = "FrameBuffer";

namespace camera {

FrameBuffer::Ptr FrameBuffer::create(size_t capacity, uint32_t width, uint32_t height, PixelFormat format) {
    if (capacity == 0) {
        ESP_LOGE(TAG, "Помилка: Спроба виділити кадровий буфер нулевої ємності");
        return nullptr;
    }

    // Використовуємо std::nothrow для безпечного створення об'єкта
    auto frame = Ptr(new (std::nothrow) FrameBuffer(capacity, width, height, format));
    if (!frame || frame->data_ == nullptr) {
        ESP_LOGE(TAG, "Помилка виділення буфера кадру у PSRAM розміром %zu байт", capacity);
        return nullptr;
    }

    return frame;
}

FrameBuffer::FrameBuffer(size_t capacity, uint32_t width, uint32_t height, PixelFormat format)
    : capacity_(capacity) {
    metadata_.width = width;
    metadata_.height = height;
    metadata_.format = format;
    metadata_.dataSize = 0;
    metadata_.sequenceNumber = 0;
    metadata_.timestampUs = esp_timer_get_time();

    // Виділяємо пам'ять суворо у зовнішній PSRAM із вирівнюванням під 32-бітну DMA шину
    data_ = static_cast<uint8_t*>(heap_caps_aligned_alloc(32, capacity, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
    if (!data_) {
        // Запасний варіант: звичайна алокація в PSRAM
        data_ = static_cast<uint8_t*>(heap_caps_malloc(capacity, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
    }

    if (data_) {
        std::memset(data_, 0, capacity);
    }
}

FrameBuffer::~FrameBuffer() {
    if (data_) {
        heap_caps_free(data_);
        data_ = nullptr;
    }
}

FrameBuffer::FrameBuffer(FrameBuffer&& other) noexcept
    : data_(other.data_),
      capacity_(other.capacity_),
      metadata_(other.metadata_),
      refCount_(other.refCount_.load()) {
    other.data_ = nullptr;
    other.capacity_ = 0;
    other.metadata_ = {};
}

FrameBuffer& FrameBuffer::operator=(FrameBuffer&& other) noexcept {
    if (this != &other) {
        if (data_) {
            heap_caps_free(data_);
        }
        data_ = other.data_;
        capacity_ = other.capacity_;
        metadata_ = other.metadata_;
        refCount_.store(other.refCount_.load());

        other.data_ = nullptr;
        other.capacity_ = 0;
        other.metadata_ = {};
    }
    return *this;
}

void FrameBuffer::setActualSize(size_t size) {
    if (size <= capacity_) {
        metadata_.dataSize = size;
    } else {
        ESP_LOGW(TAG, "Розмір кадру (%zu) перевищує ємність буфера (%zu), обрізаємо", size, capacity_);
        metadata_.dataSize = capacity_;
    }
}

void FrameBuffer::retain() {
    refCount_.fetch_add(1, std::memory_order_relaxed);
}

bool FrameBuffer::release() {
    if (refCount_.fetch_sub(1, std::memory_order_acq_rel) == 1) {
        return true;
    }
    return false;
}

} // namespace camera
