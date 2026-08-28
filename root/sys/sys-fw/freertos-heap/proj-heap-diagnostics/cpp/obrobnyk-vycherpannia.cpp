#include <string_view>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_system.h"

namespace diagnostics {

[[noreturn]] void handle_malloc_failure() noexcept
{
    const TaskHandle_t task = xTaskGetCurrentTaskHandle();
    const char * const raw_name = pcTaskGetName(task);
    const std::string_view task_name = (raw_name != nullptr) ? raw_name : "UNKNOWN";

    ESP_LOGE("CRITICAL", "Аварія алокації у задачі: %.*s",
             static_cast<int>(task_name.size()), task_name.data());
    ESP_LOGE("CRITICAL", "Залишок купи: %zu Б", xPortGetFreeHeapSize());

    esp_restart();
}

} // namespace diagnostics

extern "C" void vApplicationMallocFailedHook(void)
{
    diagnostics::handle_malloc_failure();
}
