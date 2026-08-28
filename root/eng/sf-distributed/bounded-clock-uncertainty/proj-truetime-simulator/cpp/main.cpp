#include <iostream>
#include <chrono>
#include <thread>
#include <mutex>
#include <algorithm>
#include <cstdint>
#include <format>

namespace truetime {

using Microseconds = std::chrono::microseconds;
using SteadyClock = std::chrono::steady_clock;
using TimePoint = std::chrono::time_point<SteadyClock>;

struct TimeInterval {
    std::int64_t earliest_us{0};
    std::int64_t latest_us{0};

    [[nodiscard]] bool contains(std::int64_t t) const noexcept {
        return earliest_us <= t && t <= latest_us;
    }

    [[nodiscard]] bool precedes(const TimeInterval& other) const noexcept {
        return latest_us < other.earliest_us;
    }

    [[nodiscard]] bool overlaps(const TimeInterval& other) const noexcept {
        return !(precedes(other) || other.precedes(*this));
    }
};

class ClockNode {
public:
    ClockNode(Microseconds base_uncertainty, double drift_ppm, Microseconds offset_bias)
        : base_uncertainty_(base_uncertainty),
          drift_ppm_(drift_ppm),
          offset_bias_(offset_bias),
          sync_point_(SteadyClock::now()) {}

    [[nodiscard]] TimeInterval now() const {
        const auto current_tp = SteadyClock::now();
        std::lock_guard<std::mutex> lock(mutex_);

        const auto elapsed_us = std::chrono::duration_cast<Microseconds>(current_tp - sync_point_).count();
        const auto raw_now_us = std::chrono::duration_cast<Microseconds>(current_tp.time_since_epoch()).count() + offset_bias_.count();

        const auto dynamic_drift_us = static_cast<std::int64_t>(static_cast<double>(elapsed_us) * (drift_ppm_ / 1'000'000.0));
        const auto total_uncertainty_us = base_uncertainty_.count() + dynamic_drift_us;

        return TimeInterval{
            .earliest_us = raw_now_us - total_uncertainty_us,
            .latest_us = raw_now_us + total_uncertainty_us
        };
    }

    [[nodiscard]] bool after(std::int64_t target_time_us) const {
        return now().earliest_us > target_time_us;
    }

    [[nodiscard]] bool before(std::int64_t target_time_us) const {
        return now().latest_us < target_time_us;
    }

    void commit_wait(std::int64_t commit_timestamp_us) const {
        while (!after(commit_timestamp_us)) {
            const auto current_interval = now();
            const auto remaining_us = commit_timestamp_us - current_interval.earliest_us + 50;
            if (remaining_us > 0) {
                std::this_thread::sleep_for(std::chrono::microseconds(remaining_us));
            }
        }
    }

    void resync(Microseconds new_base_uncertainty) {
        std::lock_guard<std::mutex> lock(mutex_);
        sync_point_ = SteadyClock::now();
        base_uncertainty_ = new_base_uncertainty;
    }

private:
    Microseconds base_uncertainty_;
    double drift_ppm_;
    Microseconds offset_bias_;
    TimePoint sync_point_;
    mutable std::mutex mutex_;
};

class TransactionCoordinator {
public:
    explicit TransactionCoordinator(ClockNode& clock) : clock_(clock) {}

    [[nodiscard]] std::int64_t execute_commit() {
        // Крок 1: Отримання інтервалу та вибір мітки коміту: s = latest
        const auto interval = clock_.now();
        const std::int64_t commit_ts = interval.latest_us;

        // Крок 2: Очікування закінчення невизначеності (Commit Wait)
        clock_.commit_wait(commit_ts);

        // Крок 3: Після виходу з Commit Wait мітка commit_ts гарантовано в минулому
        return commit_ts;
    }

private:
    ClockNode& clock_;
};

} // namespace truetime

int main() {
    // Вузол А: похибка 2 мс (2000 мкс), забігає вперед на +1 мс
    truetime::ClockNode node_a(std::chrono::microseconds(2000), 200.0, std::chrono::microseconds(1000));

    // Вузол В: похибка 2 мс (2000 мкс), суттєво відстає (-4 мс)
    truetime::ClockNode node_b(std::chrono::microseconds(2000), 200.0, std::chrono::microseconds(-4000));

    truetime::TransactionCoordinator coord_a(node_a);
    truetime::TransactionCoordinator coord_b(node_b);

    std::cout << "Початок транзакції T1 на Вузлі A...\n";
    const auto s1 = coord_a.execute_commit();
    std::cout << std::format("T1 зафіксовано з міткою s1 = {} мкс. Результат передано клієнту.\n", s1);

    // Зовнішня причинна затримка (клієнт надсилає запит на інший вузол)
    std::this_thread::sleep_for(std::chrono::milliseconds(5));

    std::cout << "Початок транзакції T2 на Вузлі B (з відстаючим локальним годинником)...\n";
    const auto s2 = coord_b.execute_commit();
    std::cout << std::format("T2 зафіксовано з міткою s2 = {} мкс.\n", s2);

    if (s2 > s1) {
        std::cout << std::format("УСПІХ: Зовнішню узгодженість дотримано: s1 ({}) < s2 ({}) [Різниця: {} мкс]\n",
                                 s1, s2, s2 - s1);
        return 0;
    } else {
        std::cerr << std::format("КРИТИЧНИЙ ЗБІЙ: Інверсія порядку! s2 ({}) <= s1 ({})\n", s2, s1);
        return 1;
    }
}
