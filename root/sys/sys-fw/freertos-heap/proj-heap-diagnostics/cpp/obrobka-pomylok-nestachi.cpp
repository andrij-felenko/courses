#include "esp_heap_caps.h"
#include "esp_log.h"
#include <string_view>

namespace memory_protection {

class AllocationFailureHandler {
public:
    static void init() noexcept {
        heap_caps_register_failed_alloc_callback(&callback_bridge);
    }

private:
    static void callback_bridge(size_t size, uint32_t caps, const char *function_name) noexcept {
        const std::string_view fn = (function_name != nullptr) ? function_name : "anonymous";
        ESP_LOGE("CPP_HEAP", "Неможливо виділити %zu Б у %.*s (caps: 0x%08x)",
                 size, static_cast<int>(fn.size()), fn.data(), caps);
    }
};

} // namespace memory_protection

void init_diagnostics_cpp()
{
    memory_protection::AllocationFailureHandler::init();
}
