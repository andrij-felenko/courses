#include <array>
#include <cstdint>
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/task.h"

struct IsrFixedPacket {
    std::uint32_t length{0};
    std::array<std::uint8_t, 64> payload{};
};

class IsrBufferBridge {
public:
    explicit IsrBufferBridge(QueueHandle_t target_queue) noexcept
        : queue_{target_queue} {}

    void IRAM_ATTR handle_incoming_bytes_isr(const std::span<const uint8_t> rx_data) noexcept {
        BaseType_t higher_prio_woken = pdFALSE;
        IsrFixedPacket pkt{};
        pkt.length = static_cast<std::uint32_t>(rx_data.size());

        for (std::size_t i = 0; i < rx_data.size() && i < pkt.payload.size(); ++i) {
            pkt.payload[i] = rx_data[i];
        }

        xQueueSendFromISR(queue_, &pkt, &higher_prio_woken);

        if (higher_prio_woken == pdTRUE) {
            portYIELD_FROM_ISR();
        }
    }

private:
    QueueHandle_t queue_{nullptr};
};
