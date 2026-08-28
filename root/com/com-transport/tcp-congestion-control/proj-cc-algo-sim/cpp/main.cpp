#include <iostream>
#include <vector>
#include <string_view>
#include <algorithm>
#include <cstdint>
#include <iomanip>

namespace tcp {

constexpr uint32_t kMss = 1460;
constexpr uint32_t kInitialSsthresh = 65535;

enum class State {
    SlowStart,
    CongestionAvoidance,
    FastRecovery
};

enum class Algorithm {
    Tahoe,
    Reno
};

class CongestionControlSimulator {
public:
    explicit CongestionControlSimulator(Algorithm algo)
        : algo_(algo),
          state_(State::SlowStart),
          cwnd_(1 * kMss),
          ssthresh_(kInitialSsthresh),
          dup_ack_count_(0),
          bytes_acked_in_rtt_(0) {}

    void on_new_ack(uint32_t acked_bytes) noexcept {
        dup_ack_count_ = 0;

        switch (state_) {
        case State::SlowStart:
            cwnd_ += acked_bytes;
            if (cwnd_ >= ssthresh_) {
                state_ = State::CongestionAvoidance;
            }
            break;

        case State::CongestionAvoidance:
            bytes_acked_in_rtt_ += acked_bytes;
            if (bytes_acked_in_rtt_ >= cwnd_) {
                cwnd_ += kMss;
                bytes_acked_in_rtt_ -= cwnd_;
            }
            break;

        case State::FastRecovery:
            cwnd_ = ssthresh_;
            bytes_acked_in_rtt_ = 0;
            state_ = State::CongestionAvoidance;
            break;
        }
    }

    void on_dup_ack() noexcept {
        dup_ack_count_++;

        if (dup_ack_count_ == 3) {
            ssthresh_ = std::max(cwnd_ / 2, 2 * kMss);

            if (algo_ == Algorithm::Tahoe) {
                cwnd_ = 1 * kMss;
                state_ = State::SlowStart;
            } else {
                cwnd_ = ssthresh_ + 3 * kMss;
                state_ = State::FastRecovery;
            }
        } else if (state_ == State::FastRecovery) {
            cwnd_ += kMss;
        }
    }

    void on_timeout() noexcept {
        ssthresh_ = std::max(cwnd_ / 2, 2 * kMss);
        cwnd_ = 1 * kMss;
        dup_ack_count_ = 0;
        bytes_acked_in_rtt_ = 0;
        state_ = State::SlowStart;
    }

    [[nodiscard]] uint32_t cwnd() const noexcept { return cwnd_; }
    [[nodiscard]] uint32_t ssthresh() const noexcept { return ssthresh_; }
    [[nodiscard]] State state() const noexcept { return state_; }

    [[nodiscard]] std::string_view state_name() const noexcept {
        switch (state_) {
        case State::SlowStart:           return "SlowStart";
        case State::CongestionAvoidance: return "CongestionAvoidance";
        case State::FastRecovery:        return "FastRecovery";
        }
        return "Unknown";
    }

private:
    Algorithm algo_;
    State state_;
    uint32_t cwnd_;
    uint32_t ssthresh_;
    uint32_t dup_ack_count_;
    uint32_t bytes_acked_in_rtt_;
};

} // namespace tcp

int main() {
    tcp::CongestionControlSimulator sim(tcp::Algorithm::Reno);

    std::cout << "=== Симуляція TCP Reno (C++20 RAII та Strong Enums) ===\n";
    std::cout << std::left << std::setw(6)  << "Крок"
              << std::setw(22) << "Стан"
              << std::setw(15) << "cwnd (байти)"
              << std::setw(12) << "cwnd (MSS)"
              << "ssthresh\n";
    std::cout << std::string(65, '-') << "\n";

    for (int step = 1; step <= 15; ++step) {
        std::cout << std::left << std::setw(6)  << step
                  << std::setw(22) << sim.state_name()
                  << std::setw(15) << sim.cwnd()
                  << std::setw(12) << (sim.cwnd() / tcp::kMss)
                  << sim.ssthresh() << "\n";

        if (step == 7) {
            std::cout << " ---> [ПОДІЯ] Потрійний dupACK!\n";
            sim.on_dup_ack();
            sim.on_dup_ack();
            sim.on_dup_ack();
        } else if (step == 8) {
            sim.on_new_ack(sim.cwnd());
        } else {
            sim.on_new_ack(sim.cwnd());
        }
    }

    return 0;
}
