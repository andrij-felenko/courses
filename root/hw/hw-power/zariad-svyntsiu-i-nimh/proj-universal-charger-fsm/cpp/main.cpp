#include <cstdint>
#include <array>
#include <algorithm>
#include <numeric>

namespace power {

enum class BatteryChem {
    LeadAcid,
    NiMH
};

enum class ChargerState {
    Standby,
    LeadAcidBulkCC,
    LeadAcidAbsorptionCV,
    LeadAcidFloat,
    NiMHPrecharge,
    NiMHFastCC,
    NiMHTopOff,
    NiMHTrickle,
    Fault
};

enum class ChargerFault {
    None,
    OverVoltage,
    OverTemp,
    Timeout,
    ReversePolarity
};

class UniversalCharger {
public:
    static constexpr size_t kAdcFilterSize = 32;
    static constexpr size_t kDtWindowSec = 60;

    UniversalCharger(BatteryChem chem, uint16_t capacity_mah, uint8_t cell_count)
        : chem_(chem), capacity_mah_(capacity_mah), cell_count_(cell_count) {
        v_buffer_.fill(0);
        t_history_.fill(25);
    }

    void update_sensors(uint16_t raw_v_mv, int16_t raw_t_c) {
        v_buffer_[v_buf_idx_] = raw_v_mv;
        v_buf_idx_ = (v_buf_idx_ + 1) % kAdcFilterSize;

        uint32_t sum = std::accumulate(v_buffer_.begin(), v_buffer_.end(), 0u);
        v_filtered_mv_ = sum / kAdcFilterSize;

        t_current_c_ = raw_t_c;
        int16_t old_t = t_history_[t_hist_idx_];
        t_history_[t_hist_idx_] = raw_t_c;
        t_hist_idx_ = (t_hist_idx_ + 1) % kDtWindowSec;

        dt_dt_mdeg_per_sec_ = (static_cast<int32_t>(raw_t_c - old_t) * 1000) / static_cast<int32_t>(kDtWindowSec);
    }

    void tick_1s(uint16_t measured_i_ma) {
        ++state_time_sec_;
        ++total_charge_sec_;

        if (t_current_c_ > 55) {
            trigger_fault(ChargerFault::OverTemp);
            return;
        }

        switch (state_) {
            case ChargerState::Standby:
                handle_standby();
                break;
            case ChargerState::LeadAcidBulkCC:
                handle_la_bulk();
                break;
            case ChargerState::LeadAcidAbsorptionCV:
                handle_la_absorption(measured_i_ma);
                break;
            case ChargerState::LeadAcidFloat:
                handle_la_float();
                break;
            case ChargerState::NiMHPrecharge:
                handle_nimh_precharge();
                break;
            case ChargerState::NiMHFastCC:
                handle_nimh_fast();
                break;
            case ChargerState::NiMHTopOff:
                handle_nimh_top_off();
                break;
            case ChargerState::NiMHTrickle:
                target_i_ma_ = capacity_mah_ / 35;
                break;
            case ChargerState::Fault:
                target_v_mv_ = 0;
                target_i_ma_ = 0;
                break;
        }
    }

    [[nodiscard]] ChargerState state() const noexcept { return state_; }
    [[nodiscard]] ChargerFault fault() const noexcept { return fault_; }
    [[nodiscard]] uint16_t target_v_mv() const noexcept { return target_v_mv_; }
    [[nodiscard]] uint16_t target_i_ma() const noexcept { return target_i_ma_; }

private:
    uint16_t calc_la_compensated_v(uint16_t base_mv) const noexcept {
        int32_t delta_t = static_cast<int32_t>(t_current_c_) - 25;
        int32_t comp_mv = -4 * static_cast<int32_t>(cell_count_) * delta_t;
        int32_t result = static_cast<int32_t>(base_mv) + comp_mv;
        return static_cast<uint16_t>(std::clamp(result, 10000, 16500));
    }

    void trigger_fault(ChargerFault fault) noexcept {
        state_ = ChargerState::Fault;
        fault_ = fault;
        target_v_mv_ = 0;
        target_i_ma_ = 0;
    }

    void handle_standby() noexcept {
        if (v_filtered_mv_ > 500) {
            state_time_sec_ = 0;
            if (chem_ == BatteryChem::LeadAcid) {
                state_ = ChargerState::LeadAcidBulkCC;
                target_i_ma_ = capacity_mah_ / 10;
                target_v_mv_ = calc_la_compensated_v(2400 * cell_count_);
            } else {
                if (v_filtered_mv_ < 1000u * cell_count_) {
                    state_ = ChargerState::NiMHPrecharge;
                    target_i_ma_ = capacity_mah_ / 10;
                } else {
                    state_ = ChargerState::NiMHFastCC;
                    target_i_ma_ = (capacity_mah_ * 7) / 10;
                }
                v_peak_mv_ = v_filtered_mv_;
            }
        }
    }

    void handle_la_bulk() noexcept {
        uint16_t v_abs = calc_la_compensated_v(2400 * cell_count_);
        target_v_mv_ = v_abs;
        target_i_ma_ = capacity_mah_ / 10;

        if (v_filtered_mv_ >= v_abs) {
            state_ = ChargerState::LeadAcidAbsorptionCV;
            state_time_sec_ = 0;
        }
        if (state_time_sec_ > 14 * 3600) {
            trigger_fault(ChargerFault::Timeout);
        }
    }

    void handle_la_absorption(uint16_t measured_i_ma) noexcept {
        target_v_mv_ = calc_la_compensated_v(2400 * cell_count_);
        if (measured_i_ma < (capacity_mah_ / 50) || state_time_sec_ > 4 * 3600) {
            state_ = ChargerState::LeadAcidFloat;
            state_time_sec_ = 0;
        }
    }

    void handle_la_float() noexcept {
        target_v_mv_ = calc_la_compensated_v(2260 * cell_count_);
        target_i_ma_ = capacity_mah_ / 20;
    }

    void handle_nimh_precharge() noexcept {
        if (v_filtered_mv_ >= 1000u * cell_count_) {
            state_ = ChargerState::NiMHFastCC;
            state_time_sec_ = 0;
            target_i_ma_ = (capacity_mah_ * 7) / 10;
            v_peak_mv_ = v_filtered_mv_;
        }
        if (state_time_sec_ > 1800) {
            trigger_fault(ChargerFault::Timeout);
        }
    }

    void handle_nimh_fast() noexcept {
        if (v_filtered_mv_ > v_peak_mv_) {
            v_peak_mv_ = v_filtered_mv_;
        }

        uint32_t dv_thresh = 4u * cell_count_;
        bool neg_dv = (v_peak_mv_ >= v_filtered_mv_ + dv_thresh);
        bool temp_slope = (dt_dt_mdeg_per_sec_ >= 17 && state_time_sec_ > 300);

        if (neg_dv || temp_slope) {
            state_ = ChargerState::NiMHTopOff;
            state_time_sec_ = 0;
            target_i_ma_ = capacity_mah_ / 10;
        }
        if (state_time_sec_ > 7200) {
            trigger_fault(ChargerFault::Timeout);
        }
    }

    void handle_nimh_top_off() noexcept {
        if (state_time_sec_ >= 1800) {
            state_ = ChargerState::NiMHTrickle;
            state_time_sec_ = 0;
            target_i_ma_ = capacity_mah_ / 35;
        }
    }

    BatteryChem chem_;
    ChargerState state_{ChargerState::Standby};
    ChargerFault fault_{ChargerFault::None};

    uint16_t capacity_mah_;
    uint8_t cell_count_;

    std::array<uint32_t, kAdcFilterSize> v_buffer_{};
    size_t v_buf_idx_{0};
    uint32_t v_filtered_mv_{0};
    uint32_t v_peak_mv_{0};

    std::array<int16_t, kDtWindowSec> t_history_{};
    size_t t_hist_idx_{0};
    int16_t t_current_c_{25};
    int16_t dt_dt_mdeg_per_sec_{0};

    uint32_t state_time_sec_{0};
    uint32_t total_charge_sec_{0};

    uint16_t target_v_mv_{0};
    uint16_t target_i_ma_{0};
};

} // namespace power
