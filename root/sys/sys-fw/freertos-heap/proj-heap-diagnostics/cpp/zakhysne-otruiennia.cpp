#include "esp_heap_caps.h"
#include "esp_log.h"

struct HeapIntegrity {
    [[nodiscard]] static bool verify_all_regions(bool print_errors = true) noexcept {
        return heap_caps_check_integrity_all(print_errors);
    }
};

void run_diagnostics_cpp()
{
    if (HeapIntegrity::verify_all_regions()) {
        ESP_LOGI("HEAP_CHECK", "Купа неушкоджена.");
    } else {
        ESP_LOGE("HEAP_CHECK", "Аварія структури купи!");
    }
}
