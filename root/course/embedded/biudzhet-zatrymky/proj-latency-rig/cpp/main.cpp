#include <array>
#include <span>
#include <chrono>
#include <algorithm>
#include <numeric>
#include <optional>
#include <cstdint>

namespace latency {

using namespace std::chrono_literals;
using Microseconds = std::chrono::duration<uint32_t, std::micro>;

template <std::size_t MaxSamples = 256>
class MeasurementRig {
public:
    struct Statistics {
        std::size_t total_samples{0};
        std::size_t timeout_count{0};
        Microseconds min{0us};
        Microseconds max{0us};
        Microseconds mean{0us};
        Microseconds p50{0us};
        Microseconds p95{0us};
        Microseconds p99{0us};
        Microseconds jitter{0us};
    };

    enum class State {
        Idle,
        WaitingResponse,
        Cooldown
    };

    void on_optical_trigger_isr(Microseconds timestamp) noexcept {
        if (state_ == State::WaitingResponse) {
            last_latency_ = timestamp - trigger_start_;
            sample_ready_ = true;
            state_ = State::Cooldown;
        }
    }

    void start_trigger(Microseconds timestamp) noexcept {
        if (state_ != State::Idle) return;
        sample_ready_ = false;
        state_ = State::WaitingResponse;
        trigger_start_ = timestamp;
    }

    struct PollResult {
        bool completed{false};
        bool is_timeout{false};
        Microseconds latency{0us};
    };

    PollResult poll(Microseconds current_time, Microseconds timeout_limit = 250000us) noexcept {
        if (state_ == State::WaitingResponse) {
            if ((current_time - trigger_start_) >= timeout_limit) {
                state_ = State::Cooldown;
                ++timeouts_;
                return { .completed = true, .is_timeout = true, .latency = timeout_limit };
            }
        }

        if (sample_ready_) {
            sample_ready_ = false;
            if (sample_count_ < MaxSamples) {
                samples_[sample_count_++] = last_latency_;
            }
            return { .completed = true, .is_timeout = false, .latency = last_latency_ };
        }

        return { .completed = false, .is_timeout = false, .latency = 0us };
    }

    void reset_to_idle() noexcept {
        state_ = State::Idle;
    }

    [[nodiscard]] std::optional<Statistics> compute_statistics() const noexcept {
        if (sample_count_ == 0) {
            return std::nullopt;
        }

        std::array<Microseconds, MaxSamples> sorted_buf;
        std::copy_n(samples_.begin(), sample_count_, sorted_buf.begin());
        std::sort(sorted_buf.begin(), sorted_buf.begin() + sample_count_);

        Statistics stats;
        stats.total_samples = sample_count_;
        stats.timeout_count = timeouts_;
        stats.min = sorted_buf.front();
        stats.max = sorted_buf[sample_count_ - 1];

        const uint64_t total_us = std::accumulate(
            sorted_buf.begin(), sorted_buf.begin() + sample_count_, 0ULL,
            [](uint64_t acc, Microseconds val) { return acc + val.count(); }
        );
        stats.mean = Microseconds(static_cast<uint32_t>(total_us / sample_count_));

        stats.p50 = sorted_buf[(sample_count_ * 50) / 100];
        stats.p95 = sorted_buf[(sample_count_ * 95) / 100];
        stats.p99 = sorted_buf[(sample_count_ * 99) / 100];

        uint64_t dev_sum = 0;
        for (std::size_t i = 0; i < sample_count_; ++i) {
            const auto diff = static_cast<int64_t>(sorted_buf[i].count()) - 
                              static_cast<int64_t>(stats.mean.count());
            dev_sum += static_cast<uint64_t>(std::abs(diff));
        }
        stats.jitter = Microseconds(static_cast<uint32_t>(dev_sum / sample_count_));

        return stats;
    }

private:
    std::array<Microseconds, MaxSamples> samples_{};
    std::size_t sample_count_{0};
    std::size_t timeouts_{0};
    Microseconds trigger_start_{0us};
    Microseconds last_latency_{0us};
    volatile State state_{State::Idle};
    volatile bool sample_ready_{false};
};

} // namespace latency
