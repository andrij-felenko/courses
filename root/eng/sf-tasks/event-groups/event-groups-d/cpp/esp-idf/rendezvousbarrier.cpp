#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include "esp_log.h"

class RendezvousBarrier {
public:
    static constexpr EventBits_t kTaskABit = (1 << 0);
    static constexpr EventBits_t kTaskBBit = (1 << 1);
    static constexpr EventBits_t kTaskCBit = (1 << 2);
    static constexpr EventBits_t kAllBits = (kTaskABit | kTaskBBit | kTaskCBit);

    RendezvousBarrier() {
        handle_ = xEventGroupCreate();
    }

    ~RendezvousBarrier() {
        if (handle_ != nullptr) {
            vEventGroupDelete(handle_);
        }
    }

    EventBits_t sync(EventBits_t bit_to_set, TickType_t ticks_to_wait = portMAX_DELAY) {
        return xEventGroupSync(handle_, bit_to_set, kAllBits, ticks_to_wait);
    }

private:
    EventGroupHandle_t handle_;
};

static RendezvousBarrier s_barrier;
static const char *TAG = "CPP_BARRIER";

extern "C" void app_main(void) {
    xTaskCreate([](void *param) {
        while (true) {
            ESP_LOGI(TAG, "C++ Задача 1: Крок 1 completed");
            vTaskDelay(pdMS_TO_TICKS(80));
            s_barrier.sync(RendezvousBarrier::kTaskABit);
            ESP_LOGI(TAG, "C++ Задача 1: Синхронізовано");
        }
    }, "task1", 2048, nullptr, 5, nullptr);
}
