#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include "esp_log.h"

class SystemHealthMonitor {
public:
    enum StateBits : EventBits_t {
        PowerReady   = (1 << 0),
        StorageReady = (1 << 1),
        SensorsReady = (1 << 2),
        NetworkReady = (1 << 3),
        AllReady     = (PowerReady | StorageReady | SensorsReady | NetworkReady)
    };

    SystemHealthMonitor() {
        handle_ = xEventGroupCreateStatic(&static_buffer_);
    }

    void set_subsystem_ready(StateBits bit) {
        xEventGroupSetBits(handle_, static_cast<EventBits_t>(bit));
    }

    bool await_full_system_ready(TickType_t timeout_ticks = portMAX_DELAY) {
        EventBits_t result = xEventGroupWaitBits(
            handle_,
            AllReady,
            pdFALSE,
            pdTRUE,
            timeout_ticks
        );
        return (result & AllReady) == AllReady;
    }

private:
    StaticEventGroup_t static_buffer_;
    EventGroupHandle_t handle_;
};

static SystemHealthMonitor s_health_monitor;
