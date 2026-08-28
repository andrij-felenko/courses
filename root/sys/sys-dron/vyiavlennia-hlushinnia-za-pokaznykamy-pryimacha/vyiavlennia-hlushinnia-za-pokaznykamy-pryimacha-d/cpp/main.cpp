#include <array>
#include <algorithm>
#include <cstdint>
#include <span>

namespace gnss::security {

enum class JammingState : uint8_t {
    Clean = 0,
    Warning,
    Critical,
    Recovery
};

struct SatelliteInfo {
    uint8_t gnss_id{0};
    uint8_t sv_id{0};
    uint8_t cno{0};          // dB-Hz
    int8_t  elevation{0};    // градуси (-90..+90)
    bool    used_in_fix{false};
};

struct UbxMonRfBlock {
    uint8_t  block_id{0};
    uint8_t  flags{0};
    uint8_t  ant_status{0};
    uint8_t  ant_power{0};
    uint32_t post_status{0};
    uint16_t noise_per_ms{0};
    uint16_t agc_cnt{0};      // 0..8191
    uint8_t  jam_ind{0};      // 0..255
    int8_t   ofs_i{0};
    uint8_t  mag_i{0};
    int8_t   ofs_q{0};
    uint8_t  mag_q{0};
};

class JammingDetector {
public:
    constexpr JammingDetector() = default;

    JammingState update(const UbxMonRfBlock& rf, std::span<const SatelliteInfo> satellites) noexcept {
        float cno_sum = 0.0F;
        uint8_t valid_sats = 0;

        for (const auto& sat : satellites) {
            if (sat.elevation >= 15 && sat.cno > 0) {
                cno_sum += static_cast<float>(sat.cno);
                valid_sats++;
            }
        }

        const float mean_cno = (valid_sats > 0) ? (cno_sum / static_cast<float>(valid_sats)) : 0.0F;

        if (!is_calibrated_) {
            calibrate_step(rf.agc_cnt, mean_cno, valid_sats);
            return JammingState::Clean;
        }

        // 1. Оцінка просідання підсилення AGC
        float delta_agc = 0.0F;
        if (agc_baseline_ > 0 && rf.agc_cnt < agc_baseline_) {
            delta_agc = static_cast<float>(agc_baseline_ - rf.agc_cnt) / static_cast<float>(agc_baseline_);
        }
        s_agc_ = std::clamp((delta_agc - 0.15F) / (0.60F - 0.15F), 0.0F, 1.0F);

        // 2. Оцінка деградації середнього C/N0
        const float delta_cno = cno_baseline_ - mean_cno;
        s_cno_ = std::clamp((delta_cno - 4.0F) / (18.0F - 4.0F), 0.0F, 1.0F);

        // 3. Оцінка за апаратним індикатором jamInd
        s_jam_ = std::clamp((static_cast<float>(rf.jam_ind) - 40.0F) / (180.0F - 40.0F), 0.0F, 1.0F);

        // 4. Оцінка за кількістю втрачених супутників
        float delta_sv = 0.0F;
        if (sv_count_baseline_ > 0 && valid_sats < sv_count_baseline_) {
            delta_sv = static_cast<float>(sv_count_baseline_ - valid_sats) / static_cast<float>(sv_count_baseline_);
        }
        s_sv_ = std::clamp((delta_sv - 0.20F) / (0.70F - 0.20F), 0.0F, 1.0F);

        const float raw_score = 0.35F * s_agc_ + 0.30F * s_cno_ + 0.25F * s_jam_ + 0.10F * s_sv_;
        filtered_score_ = kAlpha * raw_score + (1.0F - kAlpha) * filtered_score_;

        update_fsm();
        return state_;
    }

    [[nodiscard]] JammingState state() const noexcept { return state_; }
    [[nodiscard]] float threat_score() const noexcept { return filtered_score_; }
    [[nodiscard]] bool is_calibrated() const noexcept { return is_calibrated_; }

private:
    static constexpr float kAlpha{0.25F};
    static constexpr float kThreshWarning{0.35F};
    static constexpr float kThreshCritical{0.70F};
    static constexpr float kThreshRecovery{0.20F};
    static constexpr uint8_t kCriticalPersist{3};

    void calibrate_step(uint16_t agc_cnt, float mean_cno, uint8_t sv_count) noexcept {
        agc_accum_ += agc_cnt;
        cno_accum_ += mean_cno;
        calib_samples_++;

        if (calib_samples_ >= 50) {
            agc_baseline_ = static_cast<uint16_t>(agc_accum_ / calib_samples_);
            cno_baseline_ = cno_accum_ / static_cast<float>(calib_samples_);
            sv_count_baseline_ = sv_count;
            is_calibrated_ = true;
        }
    }

    void update_fsm() noexcept {
        switch (state_) {
        case JammingState::Clean:
            if (filtered_score_ >= kThreshWarning) {
                state_ = JammingState::Warning;
            }
            break;

        case JammingState::Warning:
            if (filtered_score_ >= kThreshCritical) {
                if (++critical_counter_ >= kCriticalPersist) {
                    state_ = JammingState::Critical;
                    critical_counter_ = 0;
                }
            } else if (filtered_score_ < kThreshRecovery) {
                state_ = JammingState::Clean;
                critical_counter_ = 0;
            } else {
                critical_counter_ = 0;
            }
            break;

        case JammingState::Critical:
            if (filtered_score_ < 0.40F) {
                state_ = JammingState::Recovery;
                recovery_ticks_ = 25; // 5 секунд затримки валідації при 5 Гц
            }
            break;

        case JammingState::Recovery:
            if (filtered_score_ >= kThreshWarning) {
                state_ = JammingState::Critical;
            } else if (recovery_ticks_ > 0) {
                --recovery_ticks_;
            } else {
                state_ = JammingState::Clean;
            }
            break;
        }
    }

    uint16_t agc_baseline_{7500};
    float    cno_baseline_{42.0F};
    uint8_t  sv_count_baseline_{12};
    bool     is_calibrated_{false};
    uint16_t calib_samples_{0};
    uint32_t agc_accum_{0};
    float    cno_accum_{0.0F};

    JammingState state_{JammingState::Clean};
    float        filtered_score_{0.0F};
    uint8_t      critical_counter_{0};
    uint16_t     recovery_ticks_{0};

    float s_agc_{0.0F};
    float s_cno_{0.0F};
    float s_jam_{0.0F};
    float s_sv_{0.0F};
};

} // namespace gnss::security
