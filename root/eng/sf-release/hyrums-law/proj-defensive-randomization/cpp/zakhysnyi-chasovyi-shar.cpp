#include <chrono>
#include <random>
#include <thread>

/* Введення штучного мікросекундного джиттеру в C++ */
class LatencyJitterFilter {
public:
    LatencyJitterFilter(std::chrono::milliseconds min_delay,
                        std::chrono::milliseconds max_delay)
        : min_delay_{min_delay}, max_delay_{max_delay},
          dist_{static_cast<double>(min_delay.count()), static_cast<double>(max_delay.count())},
          rng_{std::random_device{}()} {}

    void inject_delay() {
        auto ms = static_cast<int64_t>(dist_(rng_));
        std::this_thread::sleep_for(std::chrono::milliseconds(ms));
    }

private:
    std::chrono::milliseconds min_delay_;
    std::chrono::milliseconds max_delay_;
    std::uniform_real_distribution<double> dist_;
    std::mt19937 rng_;
};
