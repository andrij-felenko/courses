// Двосмуговий планувальник на C++20: std::chrono, std::span, інкапсульований стан
#include <cstdint>
#include <chrono>
#include <span>
#include <string_view>

namespace transport {

using namespace std::chrono_literals;

class DualLaneMqttDrainer {
public:
    DualLaneMqttDrainer(std::chrono::milliseconds drain_interval = 200ms)
        : drain_interval_(drain_interval), last_drain_(std::chrono::steady_clock::now()) {}

    template<typename MqttClient, typename QueueStorage>
    void poll(MqttClient& mqtt, QueueStorage& flash_queue,
              std::span<const std::byte> live_telemetry) {
        
        // 1. Пріоритетна смуга: надсилаємо свіжі дані без затримок
        if (!live_telemetry.empty()) {
            mqtt.publish("nodes/01/state", live_telemetry, 1);
        }

        // 2. Обмежена смуга архіву (Token Bucket / Rate Limiter)
        const auto now = std::chrono::steady_clock::now();
        if (now - last_drain_ >= drain_interval_) {
            last_drain_ = now;

            if (!flash_queue.empty()) {
                auto record = flash_queue.pop_front();
                if (record.has_value()) {
                    mqtt.publish("nodes/01/replay", record->data_span(), 1);
                }
            }
        }
    }

private:
    std::chrono::milliseconds drain_interval_;
    std::chrono::steady_clock::time_point last_drain_;
};

} // namespace transport
