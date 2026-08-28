#include <memory>
#include <new>
#include <span>
#include "esp_heap_caps.h"
#include "esp_log.h"

namespace esp_memory {

template <uint32_t Caps>
struct CapsDeleter {
    void operator()(void* ptr) const noexcept {
        heap_caps_free(ptr);
    }
};

template <typename T, uint32_t Caps>
using CapsUniquePtr = std::unique_ptr<T, CapsDeleter<Caps>>;

template <typename T, uint32_t Caps, typename... Args>
[[nodiscard]] CapsUniquePtr<T, Caps> make_caps_unique(Args&&... args)
{
    void* raw = heap_caps_malloc(sizeof(T), Caps);
    if (!raw) {
        throw std::bad_alloc();
    }
    T* object = ::new (raw) T(std::forward<Args>(args)...);
    return CapsUniquePtr<T, Caps>{object};
}

template <typename T, uint32_t Caps>
[[nodiscard]] CapsUniquePtr<T[], Caps> make_caps_buffer(std::size_t element_count)
{
    void* raw = heap_caps_malloc(sizeof(T) * element_count, Caps);
    if (!raw) {
        throw std::bad_alloc();
    }
    return CapsUniquePtr<T[], Caps>{static_cast<T*>(raw)};
}

} // namespace esp_memory

void allocate_hardware_buffers_cpp()
{
    try {
        // Автоматичне виділення та RAII-очищення DMA-буфера
        auto dma_buf = esp_memory::make_caps_buffer<uint8_t, MALLOC_CAP_DMA | MALLOC_CAP_INTERNAL>(4096);

        // Виділення кадрового буфера у зовнішній PSRAM
        auto frame_buf = esp_memory::make_caps_buffer<uint8_t, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT>(640 * 480 * 2);

        ESP_LOGI("CPP_HEAP", "RAII буфери виділено: DMA @ %p, PSRAM @ %p",
                 dma_buf.get(), frame_buf.get());
    }
    catch (const std::bad_alloc&) {
        ESP_LOGE("CPP_HEAP", "Неможливо виділити запитаний обсяг пам'яті");
    }
}
