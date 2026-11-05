#include <cstdint>
#include "esp_heap_caps.h"

constexpr size_t kTensorArenaSize = 512 * 1024;

class TensorMemoryManager {
public:
    static uint8_t* allocate_arena() {
        return static_cast<uint8_t*>(heap_caps_aligned_alloc(
            32, 
            kTensorArenaSize, 
            MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA | MALLOC_CAP_8BIT
        ));
    }
};
