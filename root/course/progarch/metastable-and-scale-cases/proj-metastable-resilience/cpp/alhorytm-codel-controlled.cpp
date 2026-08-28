// C++ Implementation: CoDel Queue Latency Shedder (std::chrono)
#include <chrono>
#include <cmath>

class CoDelShedder {
public:
    CoDelShedder(std::chrono::milliseconds target, std::chrono::milliseconds interval)
        : target_(target), interval_(interval), dropping_(false), count_(0) {}

    bool should_drop(std::chrono::milliseconds sojourn_time, std::chrono::steady_clock::time_point now) {
        bool ok_to_drop = false;

        if (sojourn_time < target_) {
            first_above_time_ = std::chrono::steady_clock::time_point{};
        } else {
            if (first_above_time_ == std::chrono::steady_clock::time_point{}) {
                first_above_time_ = now + interval_;
            } else if (now >= first_above_time_) {
                ok_to_drop = true;
            }
        }

        if (dropping_) {
            if (!ok_to_drop) {
                dropping_ = false;
            } else if (now >= drop_next_) {
                count_++;
                auto next_interval_count = static_cast<long long>(interval_.count() / std::sqrt(count_));
                drop_next_ = now + std::chrono::milliseconds(std::max(next_interval_count, 2LL));
                return true;
            }
        } else if (ok_to_drop) {
            dropping_ = true;
            count_ = 1;
            drop_next_ = now + interval_;
            return true;
        }

        return false;
    }

private:
    const std::chrono::milliseconds target_;
    const std::chrono::milliseconds interval_;
    std::chrono::steady_clock::time_point first_above_time_{};
    std::chrono::steady_clock::time_point drop_next_{};
    bool dropping_;
    int count_;
};
