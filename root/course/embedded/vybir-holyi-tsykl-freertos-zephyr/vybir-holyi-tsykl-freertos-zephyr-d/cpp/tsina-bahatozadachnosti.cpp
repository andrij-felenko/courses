#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"
#include <cstdint>
#include <optional>
#include <concepts>

namespace rtos {

template <typename T, size_t QueueLength>
class MessageQueue {
public:
    MessageQueue() : handle_(xQueueCreate(QueueLength, sizeof(T))) {}

    ~MessageQueue() {
        if (handle_ != nullptr) {
            vQueueDelete(handle_);
        }
    }

    // Заборона копіювання ресурсу ядра
    MessageQueue(const MessageQueue&) = delete;
    MessageQueue& operator=(const MessageQueue&) = delete;

    bool send(const T& item, TickType_t timeout_ticks) noexcept {
        if (handle_ == nullptr) return false;
        return xQueueSend(handle_, &item, timeout_ticks) == pdTRUE;
    }

    std::optional<T> receive(TickType_t timeout_ticks) noexcept {
        if (handle_ == nullptr) return std::nullopt;
        T item{};
        if (xQueueReceive(handle_, &item, timeout_ticks) == pdTRUE) {
            return item;
        }
        return std::nullopt;
    }

    [[nodiscard]] QueueHandle_t native_handle() const noexcept { return handle_; }

private:
    QueueHandle_t handle_{nullptr};
};

struct SensorReading {
    uint32_t timestamp_ms{0};
    float temperature{0.0F};
};

} // namespace rtos

static rtos::MessageQueue<rtos::SensorReading, 8> s_reading_queue;

extern "C" void vTaskSensorCpp(void* pvParameters) {
    (void)pvParameters;
    rtos::SensorReading reading{};

    while (true) {
        reading.timestamp_ms = xTaskGetTickCount() * portTICK_PERIOD_MS;
        reading.temperature = 24.5F;

        s_reading_queue.send(reading, pdMS_TO_TICKS(10));
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

extern "C" void vTaskDisplayCpp(void* pvParameters) {
    (void)pvParameters;

    while (true) {
        auto reading = s_reading_queue.receive(portMAX_DELAY);
        if (reading.has_value()) {
            // Безпечна робота з типізованими даними
            (void)reading->temperature;
        }
    }
}
