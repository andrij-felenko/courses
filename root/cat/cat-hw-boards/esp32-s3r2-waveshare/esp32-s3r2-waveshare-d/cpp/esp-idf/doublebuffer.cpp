#include <cstdio>
#include <cstdint>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "DOUBLE_BUF_CPP";

class DoubleBuffer {
private:
    uint16_t *buf_a{nullptr};
    uint16_t *buf_b{nullptr};
    uint16_t *current{nullptr};
    size_t buffer_bytes{0};

public:
    bool init(size_t width, size_t height) {
        buffer_bytes = width * height * sizeof(uint16_t);
        buf_a = static_cast<uint16_t*>(heap_caps_malloc(buffer_bytes, MALLOC_CAP_SPIRAM));
        buf_b = static_cast<uint16_t*>(heap_caps_malloc(buffer_bytes, MALLOC_CAP_SPIRAM));

        if (!buf_a || !buf_b) {
            ESP_LOGE(TAG, "Помилка виділення буферів у PSRAM");
            free_resources();
            return false;
        }
        current = buf_a;
        return true;
    }

    void swap() {
        current = (current == buf_a) ? buf_b : buf_a;
    }

    uint16_t* get_active() const { return current; }

    void free_resources() {
        if (buf_a) heap_caps_free(buf_a);
        if (buf_b) heap_caps_free(buf_b);
        buf_a = buf_b = current = nullptr;
    }

    ~DoubleBuffer() { free_resources(); }
};
