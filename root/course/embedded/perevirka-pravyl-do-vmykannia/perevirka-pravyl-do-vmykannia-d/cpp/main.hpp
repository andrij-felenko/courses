#include <cstdint>
#include <atomic>
#include <array>
#include <optional>

struct SensorSnapshot {
    float temperature_c{0.0f};
    float pressure_bar{0.0f};
    bool flow_ok{false};
    bool level_low{false};
    bool level_high{false};
    bool e_stop_pressed{false};
    uint32_t timestamp_ms{0};
};

struct ActuatorCommands {
    bool pump_enable{false};
    bool heater_enable{false};
    bool valve_open{false};
    bool alarm_siren{false};
};

class SnapshotDoubleBuffer {
public:
    void commit(const SensorSnapshot& fresh) noexcept {
        const uint8_t write_idx = 1 - active_idx_.load(std::memory_order_relaxed);
        buffers_[write_idx] = fresh;
        active_idx_.store(write_idx, std::memory_order_release);
    }

    [[nodiscard]] SensorSnapshot read_latest() const noexcept {
        const uint8_t read_idx = active_idx_.load(std::memory_order_acquire);
        return buffers_[read_idx];
    }

private:
    std::array<SensorSnapshot, 2> buffers_{};
    std::atomic<uint8_t> active_idx_{0};
};

class IRuleEngine {
public:
    virtual ~IRuleEngine() = default;
    [[nodiscard]] virtual ActuatorCommands evaluate(const SensorSnapshot& snapshot) = 0;
};
