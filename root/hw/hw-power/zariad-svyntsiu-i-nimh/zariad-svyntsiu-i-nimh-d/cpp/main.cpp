// Диспетчер станів універсального зарядного контролера на C++
#include <cstdint>
#include <algorithm>

namespace power {

enum class ChargeMode {
    LeadAcidIUoU,
    NiMHFast
};

enum class FsmState {
    Idle,
    BulkOrFastCC,
    AbsorptionOrTopOff,
    FloatOrTrickle,
    EmergencyStop
};

class ChargerCore {
public:
    explicit ChargerCore(ChargeMode mode) : mode_(mode) {}

    void process_1s(uint16_t v_mv, uint16_t i_ma, int16_t t_c, int16_t dt_mdeg_s) noexcept {
        ++timer_sec_;

        if (t_c > 55) {
            state_ = FsmState::EmergencyStop;
            v_target_mv_ = 0;
            i_target_ma_ = 0;
            return;
        }

        switch (state_) {
            case FsmState::Idle:
                if (v_mv > 1000) {
                    timer_sec_ = 0;
                    state_ = FsmState::BulkOrFastCC;
                    v_peak_mv_ = v_mv;
                }
                break;

            case FsmState::BulkOrFastCC:
                handle_bulk_or_fast(v_mv, t_c, dt_mdeg_s);
                break;

            case FsmState::AbsorptionOrTopOff:
                handle_absorption_or_topoff(i_ma);
                break;

            case FsmState::FloatOrTrickle:
                handle_float_or_trickle(t_c);
                break;

            case FsmState::EmergencyStop:
                v_target_mv_ = 0;
                i_target_ma_ = 0;
                break;
        }
    }

    [[nodiscard]] FsmState state() const noexcept { return state_; }
    [[nodiscard]] uint16_t target_v_mv() const noexcept { return v_target_mv_; }
    [[nodiscard]] uint16_t target_i_ma() const noexcept { return i_target_ma_; }

private:
    void handle_bulk_or_fast(uint16_t v_mv, int16_t t_c, int16_t dt_mdeg_s) noexcept {
        if (mode_ == ChargeMode::LeadAcidIUoU) {
            int32_t v_abs = 14400 - 24 * (t_c - 25);
            v_target_mv_ = static_cast<uint16_t>(std::clamp(v_abs, 12000, 16000));
            i_target_ma_ = 2000;
            if (v_mv >= v_target_mv_) {
                state_ = FsmState::AbsorptionOrTopOff;
                timer_sec_ = 0;
            }
        } else {
            v_peak_mv_ = std::max(v_peak_mv_, v_mv);
            i_target_ma_ = 1500;
            bool neg_dv = (v_peak_mv_ >= v_mv + 4);
            bool fast_t = (dt_mdeg_s >= 17 && timer_sec_ > 300);
            if (neg_dv || fast_t) {
                state_ = FsmState::AbsorptionOrTopOff;
                timer_sec_ = 0;
            }
        }
    }

    void handle_absorption_or_topoff(uint16_t i_ma) noexcept {
        if (mode_ == ChargeMode::LeadAcidIUoU) {
            if (i_ma < 200 || timer_sec_ > 4 * 3600) {
                state_ = FsmState::FloatOrTrickle;
                timer_sec_ = 0;
            }
        } else {
            i_target_ma_ = 200;
            if (timer_sec_ >= 1800) {
                state_ = FsmState::FloatOrTrickle;
                timer_sec_ = 0;
            }
        }
    }

    void handle_float_or_trickle(int16_t t_c) noexcept {
        if (mode_ == ChargeMode::LeadAcidIUoU) {
            int32_t v_flt = 13600 - 24 * (t_c - 25);
            v_target_mv_ = static_cast<uint16_t>(std::clamp(v_flt, 11500, 15000));
            i_target_ma_ = 500;
        } else {
            v_target_mv_ = 0;
            i_target_ma_ = 55;
        }
    }

    ChargeMode mode_;
    FsmState   state_{FsmState::Idle};
    uint32_t   timer_sec_{0};
    uint16_t   v_target_mv_{0};
    uint16_t   i_target_ma_{0};
    uint16_t   v_peak_mv_{0};
};

} // namespace power
