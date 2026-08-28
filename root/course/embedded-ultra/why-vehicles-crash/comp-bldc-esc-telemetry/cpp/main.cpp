#include <cstdint>
#include <algorithm>

class EscHealthMonitor {
public:
    static constexpr float kMaxCurrentAmps = 45.0f;
    static constexpr float kDesyncRpmDropRatio = 0.40f;
    static constexpr uint32_t kZcpTimeoutMicros = 1500;
    static constexpr uint8_t kFaultThreshold = 6;

    struct Status {
        float filtered_current{0.0f};
        uint32_t measured_erpm{0};
        uint8_t desync_score{0};
        bool is_stalled{false};
    };

    constexpr EscHealthMonitor() noexcept = default;

    [[nodiscard]] bool update(float raw_current,
                             uint32_t target_erpm,
                             uint32_t current_erpm,
                             uint32_t now_us) noexcept {
        // 1. Фільтрація вимірювання шунта струму
        status_.filtered_current = 0.85f * status_.filtered_current + 0.15f * raw_current;

        // 2. Аналіз таймауту чергового перетину нуля
        const uint32_t dt = now_us - last_commutation_us_;
        if (dt > kZcpTimeoutMicros && target_erpm > 3000) {
            status_.desync_score = static_cast<uint8_t>(std::min<int>(status_.desync_score + 1, 10));
        } else if (status_.desync_score > 0) {
            --status_.desync_score;
        }

        // 3. Перевірка надструму при загальмованому роторі
        if (status_.filtered_current > kMaxCurrentAmps &&
            current_erpm < static_cast<uint32_t>(target_erpm * kDesyncRpmDropRatio)) {
            status_.desync_score = static_cast<uint8_t>(std::min<int>(status_.desync_score + 3, 10));
        }

        // 4. Фіксація аварійного стану
        if (status_.desync_score >= kFaultThreshold) {
            status_.is_stalled = true;
            return false; // Помилка: негайне зняття напруги з ключів
        }

        status_.measured_erpm = current_erpm;
        last_commutation_us_ = now_us;
        return true;
    }

    [[nodiscard]] const Status& get_status() const noexcept { return status_; }

private:
    Status status_{};
    uint32_t last_commutation_us_{0};
};
