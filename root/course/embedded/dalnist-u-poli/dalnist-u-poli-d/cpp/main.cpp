#include <cstdint>
#include <algorithm>

class LinkMonitor {
public:
    explicit constexpr LinkMonitor(int16_t sensitivity_dbm) noexcept
        : sensitivity_limit_(sensitivity_dbm) {}

    void update(uint16_t seq, int16_t rssi_dbm, int8_t snr_db) noexcept {
        const int32_t rssi_in_q8 = static_cast<int32_t>(rssi_dbm) << 8;
        const int32_t snr_in_q8 = static_cast<int32_t>(snr_db) << 8;

        if (!initialized_) {
            rssi_ema_q8_ = rssi_in_q8;
            snr_ema_q8_ = snr_in_q8;
            last_seq_ = seq;
            total_received_ = 1;
            initialized_ = true;
            return;
        }

        /* EMA-фільтрація без операцій з рухомою комою */
        rssi_ema_q8_ += (rssi_in_q8 - rssi_ema_q8_) >> ALPHA_SHIFT;
        snr_ema_q8_  += (snr_in_q8 - snr_ema_q8_) >> ALPHA_SHIFT;

        /* Детекція втрачених номерів послідовності */
        const uint16_t expected_seq = last_seq_ + 1;
        if (seq != expected_seq) {
            const uint16_t lost = (seq > last_seq_)
                                ? (seq - expected_seq)
                                : static_cast<uint16_t>((0xFFFF - last_seq_) + seq);
            total_lost_ += lost;
        }

        last_seq_ = seq;
        ++total_received_;
    }

    [[nodiscard]] constexpr int16_t smoothed_rssi() const noexcept {
        return static_cast<int16_t>(rssi_ema_q8_ >> 8);
    }

    [[nodiscard]] constexpr int16_t smoothed_snr() const noexcept {
        return static_cast<int16_t>(snr_ema_q8_ >> 8);
    }

    [[nodiscard]] constexpr int16_t fade_margin() const noexcept {
        return smoothed_rssi() - sensitivity_limit_;
    }

    [[nodiscard]] float packet_error_rate() const noexcept {
        const uint32_t total = total_received_ + total_lost_;
        if (total == 0) return 0.0f;
        return (static_cast<float>(total_lost_) / static_cast<float>(total)) * 100.0f;
    }

    void reset() noexcept {
        rssi_ema_q8_ = 0;
        snr_ema_q8_ = 0;
        last_seq_ = 0;
        total_received_ = 0;
        total_lost_ = 0;
        initialized_ = false;
    }

private:
    static constexpr int32_t ALPHA_SHIFT = 3; /* Вага 1/8 для нового виміру */

    int32_t  rssi_ema_q8_{0};
    int32_t  snr_ema_q8_{0};
    uint32_t total_received_{0};
    uint32_t total_lost_{0};
    uint16_t last_seq_{0};
    int16_t  sensitivity_limit_{-120};
    bool     initialized_{false};
};
