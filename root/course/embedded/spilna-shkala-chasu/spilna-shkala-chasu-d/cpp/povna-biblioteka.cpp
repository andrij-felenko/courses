#include <array>
#include <chrono>
#include <cstdint>
#include <limits>
#include <optional>
#include <algorithm>

namespace embedded::time {

using namespace std::chrono_literals;

struct TimesyncSample {
    std::chrono::microseconds t1_client{0};
    std::chrono::microseconds t2_server{0};
    std::chrono::microseconds t3_server{0};
    std::chrono::microseconds t4_client{0};
    std::chrono::microseconds offset{0};
    std::chrono::microseconds rtt{0};
    bool valid{false};
};

template <std::size_t WindowSize = 16>
class TimesyncFilter {
public:
    static constexpr std::chrono::microseconds MAX_VALID_RTT = 200ms;
    static constexpr double ALPHA = 0.10;

    constexpr TimesyncFilter() noexcept {
        reset();
    }

    void reset() noexcept {
        head_ = 0;
        count_ = 0;
        filtered_offset_ = std::chrono::microseconds{0};
        last_sync_local_ = std::chrono::microseconds{0};
        min_rtt_ = std::chrono::microseconds::max();
        synchronized_ = false;
        samples_.fill(TimesyncSample{});
    }

    [[nodiscard]] bool update(std::chrono::microseconds t1,
                              std::chrono::microseconds t2,
                              std::chrono::microseconds t3,
                              std::chrono::microseconds t4) noexcept {
        if (t4 < t1) {
            return false;
        }

        const auto proc_time = (t3 >= t2) ? (t3 - t2) : std::chrono::microseconds{0};
        const auto total_roundtrip = t4 - t1;

        if (total_roundtrip < proc_time) {
            return false;
        }

        const auto rtt = total_roundtrip - proc_time;
        if (rtt > MAX_VALID_RTT) {
            return false;
        }

        const auto diff1 = t2 - t1;
        const auto diff2 = t3 - t4;
        const auto raw_offset = (diff1 + diff2) / 2;

        samples_[head_] = TimesyncSample{
            .t1_client = t1,
            .t2_server = t2,
            .t3_server = t3,
            .t4_client = t4,
            .offset = raw_offset,
            .rtt = rtt,
            .valid = true
        };

        head_ = (head_ + 1) % WindowSize;
        if (count_ < WindowSize) {
            count_++;
        }

        // Пошук вибірки з мінімальним RTT
        auto best_rtt = std::chrono::microseconds::max();
        auto best_offset = std::chrono::microseconds{0};

        for (const auto& s : samples_) {
            if (s.valid && s.rtt < best_rtt) {
                best_rtt = s.rtt;
                best_offset = s.offset;
            }
        }

        min_rtt_ = best_rtt;

        if (!synchronized_) {
            filtered_offset_ = best_offset;
            synchronized_ = true;
        } else {
            const auto delta = best_offset - filtered_offset_;
            filtered_offset_ += std::chrono::duration_cast<std::chrono::microseconds>(delta * ALPHA);
        }

        last_sync_local_ = t4;
        return true;
    }

    [[nodiscard]] std::chrono::microseconds to_server_time(std::chrono::microseconds local_now) const noexcept {
        if (!synchronized_) {
            return local_now;
        }
        return local_now + filtered_offset_;
    }

    [[nodiscard]] std::chrono::microseconds to_local_time(std::chrono::microseconds server_now) const noexcept {
        if (!synchronized_) {
            return server_now;
        }
        return server_now - filtered_offset_;
    }

    [[nodiscard]] bool is_synchronized() const noexcept {
        return synchronized_;
    }

    [[nodiscard]] std::chrono::microseconds filtered_offset() const noexcept {
        return filtered_offset_;
    }

    [[nodiscard]] std::chrono::microseconds min_rtt() const noexcept {
        return min_rtt_;
    }

private:
    std::array<TimesyncSample, WindowSize> samples_{};
    std::size_t head_{0};
    std::size_t count_{0};
    std::chrono::microseconds filtered_offset_{0};
    std::chrono::microseconds last_sync_local_{0};
    std::chrono::microseconds min_rtt_{std::chrono::microseconds::max()};
    bool synchronized_{false};
};

} // namespace embedded::time
