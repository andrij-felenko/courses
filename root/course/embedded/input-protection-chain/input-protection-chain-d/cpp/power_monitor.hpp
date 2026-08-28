// power_monitor.hpp - Ідіоматичний C++20 клас супервізора вхідного живлення
#pragma once

#include <cstdint>
#include <concepts>
#include <functional>
#include <optional>

namespace embedded::power {

enum class State : uint8_t {
    Off,
    Starting,
    Normal,
    FaultUvlo,
    FaultOvlo,
    FaultHardware
};

struct Thresholds {
    uint32_t uvlo_cutoff_mv{16500};    // 16.5 В
    uint32_t uvlo_recovery_mv{18000};  // 18.0 В (гістерезис 1.5 В)
    uint32_t ovlo_cutoff_mv{32000};    // 32.0 В
    uint32_t ovlo_recovery_mv{30500};  // 30.5 В (гістерезис 1.5 В)
    uint16_t adc_vref_mv{3300};
    uint16_t divider_top_k{110};
    uint16_t divider_bottom_k{10};
    uint8_t  filter_shift{3};          // Коефіцієнт згладжування 1/8
};

template <std::invocable<bool> SwitchDriver>
class InputProtectionChain {
public:
    explicit InputProtectionChain(SwitchDriver switch_ctrl, Thresholds thresholds = {})
        : switch_ctrl_{std::move(switch_ctrl)}
        , thresholds_{thresholds} {
        switch_ctrl_(false);
    }

    void process_adc_sample(uint16_t raw_adc) noexcept {
        update_filter(raw_adc);
        calculate_voltage();
        evaluate_state_machine();
    }

    void trigger_hardware_fault() noexcept {
        switch_ctrl_(false);
        state_ = State::FaultHardware;
        ++fault_count_;
    }

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] uint32_t voltage_mv() const noexcept { return voltage_mv_; }
    [[nodiscard]] uint32_t fault_count() const noexcept { return fault_count_; }
    [[nodiscard]] bool is_power_good() const noexcept { return state_ == State::Normal; }

private:
    void update_filter(uint16_t raw_adc) noexcept {
        const uint32_t sample_scaled = static_cast<uint32_t>(raw_adc) << 8;
        if (filtered_adc_raw_ == 0) {
            filtered_adc_raw_ = sample_scaled;
        } else {
            const auto diff = static_cast<int32_t>(sample_scaled) - static_cast<int32_t>(filtered_adc_raw_);
            filtered_adc_raw_ += (diff >> thresholds_.filter_shift);
        }
    }

    void calculate_voltage() noexcept {
        const uint32_t avg_adc = filtered_adc_raw_ >> 8;
        const uint32_t v_pin_mv = (avg_adc * thresholds_.adc_vref_mv) / 4095UL;
        const uint32_t div_sum = thresholds_.divider_top_k + thresholds_.divider_bottom_k;
        voltage_mv_ = (v_pin_mv * div_sum) / thresholds_.divider_bottom_k;
    }

    void evaluate_state_machine() noexcept {
        switch (state_) {
            case State::Off:
            case State::FaultUvlo:
                if (voltage_mv_ >= thresholds_.uvlo_recovery_mv &&
                    voltage_mv_ <= thresholds_.ovlo_recovery_mv) {
                    state_ = State::Starting;
                }
                break;

            case State::FaultOvlo:
                if (voltage_mv_ <= thresholds_.ovlo_recovery_mv &&
                    voltage_mv_ >= thresholds_.uvlo_recovery_mv) {
                    state_ = State::Starting;
                }
                break;

            case State::Starting:
                switch_ctrl_(true);
                state_ = State::Normal;
                break;

            case State::Normal:
                if (voltage_mv_ < thresholds_.uvlo_cutoff_mv) {
                    switch_ctrl_(false);
                    state_ = State::FaultUvlo;
                    ++fault_count_;
                } else if (voltage_mv_ > thresholds_.ovlo_cutoff_mv) {
                    switch_ctrl_(false);
                    state_ = State::FaultOvlo;
                    ++fault_count_;
                }
                break;

            case State::FaultHardware:
                break;
        }
    }

    SwitchDriver switch_ctrl_;
    Thresholds   thresholds_;
    State        state_{State::Off};
    uint32_t     filtered_adc_raw_{0};
    uint32_t     voltage_mv_{0};
    uint32_t     fault_count_{0};
};

} // namespace embedded::power
