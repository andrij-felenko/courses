// gateway_core.hpp - Ідіоматичне ядро шлюзу на сучасному C++ (C++20)
#pragma once

#include <cstdint>
#include <string>
#include <string_view>
#include <vector>
#include <deque>
#include <unordered_map>
#include <optional>
#include <chrono>
#include <functional>
#include <memory>
#include <span>

namespace edge {

enum class Priority : uint8_t {
    Telemetry = 0,
    Event     = 1,
    Alarm     = 2
};

enum class WanState {
    OnlineStreaming,
    OfflineBuffering,
    DrainingSync
};

struct QueueRecord {
    uint32_t id;
    std::chrono::milliseconds timestamp;
    Priority priority;
    std::string topic;
    std::string payload;
    bool in_flight{false};
};

struct MetricConfig {
    float deadband{0.2f};
    std::chrono::milliseconds max_heartbeat_interval{std::chrono::seconds(300)};
};

struct MetricState {
    float current_value{0.0f};
    float last_sent_value{0.0f};
    std::chrono::milliseconds last_sampled_time{0};
    std::chrono::milliseconds last_sent_time{0};
    bool is_valid{false};
};

class Gateway {
public:
    using OutputPublisher = std::function<bool(std::string_view topic, 
                                               std::string_view payload, 
                                               Priority prio)>;
    using EmergencyActuator = std::function<void(bool activate)>;

    explicit Gateway(float pressure_limit_bar,
                     OutputPublisher publisher,
                     EmergencyActuator actuator,
                     size_t max_queue_capacity = 10000);

    void register_metric(uint16_t metric_id, MetricConfig config);
    void ingest_modbus_reading(uint16_t metric_id, float value, 
                               std::chrono::milliseconds now);
    void ingest_lorawan_packet(uint32_t dev_addr, std::span<const uint8_t> payload, 
                               std::chrono::milliseconds now);

    void set_wan_connected(bool connected);
    void tick(std::chrono::milliseconds now);

    [[nodiscard]] size_t queue_size() const noexcept { return queue_.size(); }
    [[nodiscard]] WanState wan_state() const noexcept { return wan_state_; }
    [[nodiscard]] bool is_emergency_latched() const noexcept { return emergency_latched_; }

private:
    void enqueue_message(Priority prio, std::string topic, std::string payload, 
                         std::chrono::milliseconds now);
    void evaluate_fast_path_rules(uint16_t metric_id, float value, 
                                  std::chrono::milliseconds now);
    void drain_queue_batch();

    float pressure_limit_bar_;
    OutputPublisher publisher_;
    EmergencyActuator emergency_actuator_;
    size_t max_queue_capacity_;

    WanState wan_state_{WanState::OfflineBuffering};
    bool emergency_latched_{false};
    uint32_t next_id_{1};

    std::unordered_map<uint16_t, MetricConfig> metric_configs_;
    std::unordered_map<uint16_t, MetricState> metric_states_;
    std::deque<QueueRecord> queue_;
};

} // namespace edge
