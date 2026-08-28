#include <iostream>
#include <chrono>
#include <thread>
#include <cstdint>
#include <format>

namespace truetime {

using namespace std::chrono_literals;

struct Interval {
    std::int64_t earliest_us{0};
    std::int64_t latest_us{0};
};

class ClockService {
public:
    explicit ClockService(std::chrono::microseconds base_eps, double drift_ppm)
        : base_eps_(base_eps), drift_ppm_(drift_ppm), sync_point_(std::chrono::steady_clock::now()) {}

    [[nodiscard]] Interval now() const {
        const auto current_tp = std::chrono::steady_clock::now();
        const auto now_us = std::chrono::duration_cast<std::chrono::microseconds>(
            current_tp.time_since_epoch()).count();
        const auto elapsed_us = std::chrono::duration_cast<std::chrono::microseconds>(
            current_tp - sync_point_).count();

        const auto dynamic_drift_us = static_cast<std::int64_t>(
            static_cast<double>(elapsed_us) * (drift_ppm_ / 1'000'000.0));
        const auto total_eps = base_eps_.count() + dynamic_drift_us;

        return Interval{
            .earliest_us = now_us - total_eps,
            .latest_us = now_us + total_eps
        };
    }

    void commit_wait(std::int64_t commit_ts) const {
        while (true) {
            const auto current = now();
            if (current.earliest_us > commit_ts) {
                return; // Умова лінеаризовності виконана
            }
            const auto sleep_us = commit_ts - current.earliest_us + 50;
            if (sleep_us > 0) {
                std::this_thread::sleep_for(std::chrono::microseconds(sleep_us));
            }
        }
    }

private:
    std::chrono::microseconds base_eps_;
    double drift_ppm_;
    std::chrono::steady_clock::time_point sync_point_;
};

class Transaction {
public:
    explicit Transaction(const ClockService& clock) : clock_(clock) {}

    [[nodiscard]] std::int64_t commit() {
        // Крок 1: вибір мітки s = latest
        const auto interval = clock_.now();
        const auto commit_ts = interval.latest_us;

        // Крок 2: очікування вичерпання невизначеності
        clock_.commit_wait(commit_ts);

        // Крок 3: безпечне повернення результату
        return commit_ts;
    }

private:
    const ClockService& clock_;
};

} // namespace truetime

int main() {
    truetime::ClockService clock(1000us, 200.0);
    truetime::Transaction tx(clock);

    std::cout << "Початок виконання транзакції...\n";
    const auto commit_ts = tx.commit();
    std::cout << std::format("Транзакцію зафіксовано з лінеаризовною міткою s = {} мкс\n", commit_ts);
    return 0;
}
