#include <cstring>
#include <cstdint>
#include "esp_heap_caps.h"
#include "esp_log.h"

class DmaBuffer {
private:
    void *ptr = nullptr;
    size_t bytes = 0;

public:
    explicit DmaBuffer(size_t size) : bytes(size) {
        ptr = heap_caps_malloc(bytes, MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA);
        if (ptr) {
            std::memset(ptr, 0, bytes);
        }
    }

    ~DmaBuffer() {
        if (ptr) {
            heap_caps_free(ptr);
        }
    }

    void* data() const { return ptr; }
};
