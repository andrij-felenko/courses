#include <span>
#include <chrono>
#include <concepts>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

class HeapMonitor {
public:
    explicit constexpr HeapMonitor(size_t warning_threshold_bytes = 4096) noexcept
        : threshold_bytes_{warning_threshold_bytes} {}

    void inspect_and_log() const noexcept {
        const size_t free_bytes = xPortGetFreeHeapSize();
        const size_t min_ever_free = xPortGetMinimumEverFreeHeapSize();

        ESP_LOGI("HEAP_MON", "Поточна RAM: %zu Б, історичний мінімум: %zu Б",
                 free_bytes, min_ever_free);

        if (min_ever_free < threshold_bytes_) {
            ESP_LOGW("HEAP_MON", "Критичний запас пам'яті: %zu Б (поріг %zu Б)",
                     min_ever_free, threshold_bytes_);
        }
    }

private:
    size_t threshold_bytes_;
};

extern "C" void heap_monitor_task_cpp(void *pvParameters)
{
    (void)pvParameters;
    const HeapMonitor monitor{4096};

    while (true) {
        monitor.inspect_and_log();
        vTaskDelay(pdMS_TO_TICKS(5000));
    }
}
