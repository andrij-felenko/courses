#include <cstdint>
#include <cmath>

class JitterEstimator {
public:
    constexpr JitterEstimator() noexcept = default;

    void update(std::uint32_t send_time, std::uint32_t recv_time) noexcept {
        if (!initialized_) {
            last_s_ = send_time;
            last_r_ = recv_time;
            initialized_ = true;
            return;
        }

        const auto transit_curr = static_cast<std::int64_t>(recv_time) - static_cast<std::int64_t>(send_time);
        const auto transit_prev = static_cast<std::int64_t>(last_r_) - static_cast<std::int64_t>(last_s_);
        const double d = std::abs(static_cast<double>(transit_curr - transit_prev));

        last_s_ = send_time;
        last_r_ = recv_time;

        // RFC 3550 EWMA фільтр: J = J + (|D| - J) / 16
        jitter_ += (d - jitter_) / 16.0;
    }

    [[nodiscard]] double jitter() const noexcept {
        return jitter_;
    }

private:
    std::uint32_t last_s_{0};
    std::uint32_t last_r_{0};
    double jitter_{0.0};
    bool initialized_{false};
};
