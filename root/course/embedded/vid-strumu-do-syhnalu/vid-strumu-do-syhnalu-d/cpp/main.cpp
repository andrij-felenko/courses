#include <cstdint>
#include <algorithm>

namespace embedded {

enum class DiagnosticStatus : uint8_t {
    Normal,
    UnderRangeWarning,
    OverRangeWarning,
    FaultWireBreak,
    FaultShortCircuit
};

struct ChannelParameters {
    float shunt_resistance_ohms{100.0f};
    float adc_vref_volts{3.30f};
    uint32_t adc_max_count{4095};
    float smoothing_factor{0.10f};
    float scale_at_4ma{0.0f};
    float scale_at_20ma{16.0f};
};

struct ChannelOutput {
    float loop_current_ma;
    float scaled_physics;
    DiagnosticStatus diagnostics;
};

class CurrentLoopProcessor {
public:
    explicit constexpr CurrentLoopProcessor(const ChannelParameters& params) noexcept
        : params_{params}, filtered_voltage_{0.0f}, is_ready_{false} {}

    [[nodiscard]] ChannelOutput process_sample(uint16_t adc_code) noexcept {
        const float sample_voltage = (static_cast<float>(adc_code) / 
                                      static_cast<float>(params_.adc_max_count)) * params_.adc_vref_volts;
        
        if (!is_ready_) {
            filtered_voltage_ = sample_voltage;
            is_ready_ = true;
        } else {
            filtered_voltage_ += params_.smoothing_factor * (sample_voltage - filtered_voltage_);
        }

        const float current_ma = (filtered_voltage_ / params_.shunt_resistance_ohms) * 1000.0f;
        const auto diag = classify_namur(current_ma);
        const float physics = compute_scale(current_ma);

        return ChannelOutput{
            .loop_current_ma = current_ma,
            .scaled_physics = physics,
            .diagnostics = diag
        };
    }

    void reset() noexcept {
        is_ready_ = false;
        filtered_voltage_ = 0.0f;
    }

private:
    [[nodiscard]] static constexpr DiagnosticStatus classify_namur(float current_ma) noexcept {
        if (current_ma < 3.60f) return DiagnosticStatus::FaultWireBreak;
        if (current_ma < 3.80f) return DiagnosticStatus::UnderRangeWarning;
        if (current_ma > 21.00f) return DiagnosticStatus::FaultShortCircuit;
        if (current_ma > 20.50f) return DiagnosticStatus::OverRangeWarning;
        return DiagnosticStatus::Normal;
    }

    [[nodiscard]] constexpr float compute_scale(float current_ma) const noexcept {
        const float bounded_current = std::clamp(current_ma, 4.0f, 20.0f);
        const float normalized = (bounded_current - 4.0f) / 16.0f;
        return params_.scale_at_4ma + normalized * (params_.scale_at_20ma - params_.scale_at_4ma);
    }

    ChannelParameters params_;
    float filtered_voltage_;
    bool is_ready_;
};

} // namespace embedded
