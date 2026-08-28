#include <cstdint>
#include <algorithm>

namespace embedded {

enum class LoopStatus : uint8_t {
    Ok,
    WarningUnderRange,
    WarningOverRange,
    ErrorWireBreak,
    ErrorShortCircuit
};

struct LoopConfig {
    float r_shunt_ohms{100.0f};
    float v_ref_volts{3.30f};
    uint32_t adc_max_ticks{4095};
    float filter_alpha{0.10f};
    float phys_zero{0.0f};
    float phys_span{16.0f};
};

struct MeasurementResult {
    float current_ma;
    float physical_value;
    LoopStatus status;
};

class CurrentLoopReceiver {
public:
    explicit constexpr CurrentLoopReceiver(const LoopConfig& config) noexcept
        : config_{config}, filtered_voltage_{0.0f}, initialized_{false} {}

    [[nodiscard]] MeasurementResult update(uint16_t raw_adc) noexcept {
        const float raw_voltage = (static_cast<float>(raw_adc) / 
                                   static_cast<float>(config_.adc_max_ticks)) * config_.v_ref_volts;
        
        if (!initialized_) {
            filtered_voltage_ = raw_voltage;
            initialized_ = true;
        } else {
            filtered_voltage_ += config_.filter_alpha * (raw_voltage - filtered_voltage_);
        }

        const float current_ma = (filtered_voltage_ / config_.r_shunt_ohms) * 1000.0f;
        const auto status = evaluate_namur(current_ma);
        const float phys_val = scale_to_physics(current_ma);

        return MeasurementResult{
            .current_ma = current_ma,
            .physical_value = phys_val,
            .status = status
        };
    }

    void reset() noexcept {
        initialized_ = false;
        filtered_voltage_ = 0.0f;
    }

private:
    [[nodiscard]] static constexpr LoopStatus evaluate_namur(float current_ma) noexcept {
        if (current_ma < 3.60f) return LoopStatus::ErrorWireBreak;
        if (current_ma < 3.80f) return LoopStatus::WarningUnderRange;
        if (current_ma > 21.00f) return LoopStatus::ErrorShortCircuit;
        if (current_ma > 20.50f) return LoopStatus::WarningOverRange;
        return LoopStatus::Ok;
    }

    [[nodiscard]] constexpr float scale_to_physics(float current_ma) const noexcept {
        const float clamped_current = std::clamp(current_ma, 4.0f, 20.0f);
        const float normalized = (clamped_current - 4.0f) / 16.0f;
        return config_.phys_zero + normalized * (config_.phys_span - config_.phys_zero);
    }

    LoopConfig config_;
    float filtered_voltage_;
    bool initialized_;
};

} // namespace embedded
