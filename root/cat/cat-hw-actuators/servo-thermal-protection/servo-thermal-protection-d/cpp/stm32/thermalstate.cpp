#include <algorithm>

enum class ThermalState {
    Normal,
    Throttling,
    Shutdown
};

struct ThermalConfig {
    float t_warn{85.0f};   // °C
    float t_crit{110.0f};  // °C
    float t_hyst{5.0f};    // °C
    float i_max{10.0f};    // A
    float i_min{1.0f};     // A
};

class ThermalProtector {
public:
    explicit ThermalProtector(const ThermalConfig& config) : cfg_(config) {}

    void update(float winding_temperature) {
        switch (state_) {
            case ThermalState::Normal:
                if (winding_temperature >= cfg_.t_crit) {
                    state_ = ThermalState::Shutdown;
                } else if (winding_temperature >= cfg_.t_warn) {
                    state_ = ThermalState::Throttling;
                }
                break;

            case ThermalState::Throttling:
                if (winding_temperature >= cfg_.t_crit) {
                    state_ = ThermalState::Shutdown;
                } else if (winding_temperature < (cfg_.t_warn - cfg_.t_hyst)) {
                    state_ = ThermalState::Normal;
                }
                break;

            case ThermalState::Shutdown:
                if (winding_temperature < (cfg_.t_crit - cfg_.t_hyst)) {
                    state_ = ThermalState::Throttling;
                }
                break;
        }

        updateOutputs(winding_temperature);
    }

    [[nodiscard]] float currentLimit() const { return current_limit_; }
    [[nodiscard]] bool isBridgeEnabled() const { return bridge_enabled_; }
    [[nodiscard]] ThermalState state() const { return state_; }

private:
    void updateOutputs(float t_w) {
        if (state_ == ThermalState::Shutdown) {
            bridge_enabled_ = false;
            current_limit_ = 0.0f;
        } else if (state_ == ThermalState::Throttling) {
            bridge_enabled_ = true;
            float ratio = (t_w - cfg_.t_warn) / (cfg_.t_crit - cfg_.t_warn);
            ratio = std::clamp(ratio, 0.0f, 1.0f);
            current_limit_ = cfg_.i_max - ratio * (cfg_.i_max - cfg_.i_min);
        } else {
            bridge_enabled_ = true;
            current_limit_ = cfg_.i_max;
        }
    }

    ThermalConfig cfg_;
    ThermalState state_{ThermalState::Normal};
    float current_limit_{10.0f};
    bool bridge_enabled_{true};
};
