// gateway_core.cpp - Реалізація ядра шлюзу на C++20
#include "gateway_core.hpp"
#include <cmath>
#include <format>
#include <algorithm>

namespace edge {

Gateway::Gateway(float pressure_limit_bar,
                 OutputPublisher publisher,
                 EmergencyActuator actuator,
                 size_t max_queue_capacity)
    : pressure_limit_bar_(pressure_limit_bar),
      publisher_(std::move(publisher)),
      emergency_actuator_(std::move(actuator)),
      max_queue_capacity_(max_queue_capacity) {}

void Gateway::register_metric(uint16_t metric_id, MetricConfig config) {
    metric_configs_[metric_id] = config;
    metric_states_[metric_id] = MetricState{};
}

void Gateway::enqueue_message(Priority prio, std::string topic, std::string payload, 
                              std::chrono::milliseconds now) {
    if (queue_.size() >= max_queue_capacity_) {
        // Витісняємо найстарішу телеметрію
        auto it = std::find_if(queue_.begin(), queue_.end(), [](const QueueRecord& r) {
            return r.priority == Priority::Telemetry;
        });

        if (it != queue_.end()) {
            queue_.erase(it);
        } else {
            // Якщо немає телеметрії, видаляємо звичайну подію
            auto it_ev = std::find_if(queue_.begin(), queue_.end(), [](const QueueRecord& r) {
                return r.priority == Priority::Event;
            });
            if (it_ev != queue_.end()) {
                queue_.erase(it_ev);
            } else {
                return; // Черга заповнена критичними аваріями
            }
        }
    }

    queue_.push_back(QueueRecord{
        .id = next_id_++,
        .timestamp = now,
        .priority = prio,
        .topic = std::move(topic),
        .payload = std::move(payload),
        .in_flight = false
    });
}

void Gateway::evaluate_fast_path_rules(uint16_t metric_id, float value, 
                                       std::chrono::milliseconds now) {
    // Контур контролю критичного тиску парового котла (ID 100)
    if (metric_id == 100) {
        if (value >= pressure_limit_bar_) {
            if (!emergency_latched_) {
                emergency_latched_ = true;
                if (emergency_actuator_) {
                    emergency_actuator_(true); // Негайне апаратне відсікання
                }

                std::string alarm_json = std::format(
                    "{{\"event\":\"CRITICAL_OVERPRESSURE\",\"val\":{:.2f},\"ts\":{}}}",
                    value, now.count()
                );
                enqueue_message(Priority::Alarm, "plant/boiler/alarm", std::move(alarm_json), now);
            }
        } else if (value < (pressure_limit_bar_ - 0.5f)) {
            // Гістерезис відновлення 0.5 bar
            if (emergency_latched_) {
                emergency_latched_ = false;
                if (emergency_actuator_) {
                    emergency_actuator_(false);
                }
            }
        }
    }
}

void Gateway::ingest_modbus_reading(uint16_t metric_id, float value, 
                                    std::chrono::milliseconds now) {
    auto& cfg = metric_configs_[metric_id];
    auto& state = metric_states_[metric_id];

    state.current_value = value;
    state.last_sampled_time = now;

    // 1. Виконання швидкого аварійного контуру (< 1 мс)
    evaluate_fast_path_rules(metric_id, value, now);

    // 2. Апертурна фільтрація
    bool should_send = false;
    if (!state.is_valid) {
        should_send = true;
        state.is_valid = true;
    } else {
        float delta = std::abs(value - state.last_sent_value);
        if (delta >= cfg.deadband) {
            should_send = true;
        } else if ((now - state.last_sent_time) >= cfg.max_heartbeat_interval) {
            should_send = true;
        }
    }

    if (should_send) {
        state.last_sent_value = value;
        state.last_sent_time = now;

        std::string topic = std::format("plant/sensor/{}/telemetry", metric_id);
        std::string payload = std::format("{{\"val\":{:.2f},\"ts\":{}}}", value, now.count());

        if (wan_state_ == WanState::OnlineStreaming && queue_.empty()) {
            if (!publisher_(topic, payload, Priority::Telemetry)) {
                wan_state_ = WanState::OfflineBuffering;
                enqueue_message(Priority::Telemetry, std::move(topic), std::move(payload), now);
            }
        } else {
            enqueue_message(Priority::Telemetry, std::move(topic), std::move(payload), now);
        }
    }
}

void Gateway::ingest_lorawan_packet(uint32_t dev_addr, std::span<const uint8_t> payload, 
                                    std::chrono::milliseconds now) {
    if (payload.size() < 4) return;

    size_t offset = 0;
    while (offset + 2 <= payload.size()) {
        uint8_t channel = payload[offset++];
        uint8_t type = payload[offset++];

        if (type == 0x67 && (offset + 2 <= payload.size())) { // Cayenne LPP Температура
            int16_t raw = static_cast<int16_t>((payload[offset] << 8) | payload[offset + 1]);
            offset += 2;
            float temp = raw * 0.1f;
            uint16_t synthetic_id = static_cast<uint16_t>((dev_addr & 0xFF) * 100 + channel);
            ingest_modbus_reading(synthetic_id, temp, now);
        } else {
            break;
        }
    }
}

void Gateway::set_wan_connected(bool connected) {
    if (connected) {
        if (wan_state_ == WanState::OfflineBuffering) {
            wan_state_ = queue_.empty() ? WanState::OnlineStreaming : WanState::DrainingSync;
        }
    } else {
        wan_state_ = WanState::OfflineBuffering;
    }
}

void Gateway::drain_queue_batch() {
    if (queue_.empty()) {
        wan_state_ = WanState::OnlineStreaming;
        return;
    }

    constexpr size_t BatchLimit = 16;
    size_t processed = 0;

    while (!queue_.empty() && processed < BatchLimit) {
        const auto& rec = queue_.front();
        if (publisher_(rec.topic, rec.payload, rec.priority)) {
            queue_.pop_front();
            processed++;
        } else {
            wan_state_ = WanState::OfflineBuffering;
            break;
        }
    }
}

void Gateway::tick(std::chrono::milliseconds now) {
    (void)now;
    if (wan_state_ == WanState::DrainingSync) {
        drain_queue_batch();
    }
}

} // namespace edge
