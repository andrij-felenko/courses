#include <iostream>
#include <vector>
#include <numeric>
#include <algorithm>
#include <cmath>
#include <chrono>
#include <format>
#include <string_view>

class BenchmarkRunner {
public:
    explicit BenchmarkRunner(size_t reserve_capacity) {
        samples_.reserve(reserve_capacity);
    }

    // RAII Таймер автоматичного вимірювання скоупу
    class ScopedTimer {
    public:
        ScopedTimer(BenchmarkRunner& runner)
            : runner_(runner), start_(std::chrono::steady_clock::now()) {}

        ~ScopedTimer() {
            auto end = std::chrono::steady_clock::now();
            runner_.add_sample(end - start_);
        }
    private:
        BenchmarkRunner& runner_;
        std::chrono::steady_clock::time_point start_;
    };

    void add_sample(std::chrono::nanoseconds elapsed) {
        samples_.push_back(elapsed);
    }

    [[nodiscard]] ScopedTimer measure_scope() {
        return ScopedTimer(*this);
    }

    void print_report(std::string_view label) {
        if (samples_.empty()) {
            std::cout << std::format("[{}] Немає замірів для аналізу.\n", label);
            return;
        }

        // Сортуємо заміри для точного обчислення медианы та перцентилів
        std::sort(samples_.begin(), samples_.end());

        auto min_duration = samples_.front();
        auto max_duration = samples_.back();

        double sum_ns = 0.0;
        for (const auto& s : samples_) {
            sum_ns += static_cast<double>(s.count());
        }
        double mean_ns = sum_ns / static_cast<double>(samples_.size());

        double variance_sum = 0.0;
        for (const auto& s : samples_) {
            double diff = static_cast<double>(s.count()) - mean_ns;
            variance_sum += diff * diff;
        }
        double stddev_ns = std::sqrt(variance_sum / static_cast<double>(samples_.size()));

        auto p50 = samples_[static_cast<size_t>(samples_.size() * 0.50)];
        auto p90 = samples_[static_cast<size_t>(samples_.size() * 0.90)];
        auto p99 = samples_[static_cast<size_t>(samples_.size() * 0.99)];

        std::cout << std::format("=== Звіт бенчмарка: {} (вибірка: {} вимірів) ===\n", label, samples_.size())
                  << std::format("  Мін:        {:8.3f} мкс\n", std::chrono::duration<double, std::micro>(min_duration).count())
                  << std::format("  Макс:       {:8.3f} мкс\n", std::chrono::duration<double, std::micro>(max_duration).count())
                  << std::format("  Середнє:    {:8.3f} мкс\n", mean_ns / 1000.0)
                  << std::format("  StdDev:     {:8.3f} мкс\n", stddev_ns / 1000.0)
                  << std::format("  P50 (Med):  {:8.3f} мкс\n", std::chrono::duration<double, std::micro>(p50).count())
                  << std::format("  P90:        {:8.3f} мкс\n", std::chrono::duration<double, std::micro>(p90).count())
                  << std::format("  P99:        {:8.3f} мкс\n", std::chrono::duration<double, std::micro>(p99).count());
    }

private:
    std::vector<std::chrono::nanoseconds> samples_;
};
