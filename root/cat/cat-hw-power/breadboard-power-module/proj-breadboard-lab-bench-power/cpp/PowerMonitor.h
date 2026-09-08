#ifndef POWER_MONITOR_H
#define POWER_MONITOR_H

#include <stdint.h>

enum class ProtectionState {
    Normal,
    Warning,
    TrippedOverCurrent,
    TrippedOverVoltage
};

struct PowerMetrics {
    float voltage_v{0.0f};
    float current_ma{0.0f};
    float power_mw{0.0f};
};

class PowerMonitor {
public:
    PowerMonitor(uint8_t alert_pin, uint8_t cutoff_pin, float max_current_ma = 400.0f, float max_voltage_v = 5.5f);
    ~PowerMonitor();

    bool begin();
    void update(uint32_t current_time_ms);
    void reset();

    ProtectionState getState() const no_except { return state_; }
    const PowerMetrics& getMetrics() const no_except { return metrics_; }
    bool isOutputEnabled() const no_except { return output_enabled_; }

private:
    uint8_t alert_pin_;
    uint8_t cutoff_pin_;
    float max_current_ma_;
    float max_voltage_v_;
    ProtectionState state_{ProtectionState::Normal};
    PowerMetrics metrics_{};
    bool output_enabled_{true};
    uint32_t last_sample_time_ms_{0};

    void pollSensors();
    void evaluateSafety();
    void tripProtection(ProtectionState reason);
};

#endif // POWER_MONITOR_H
