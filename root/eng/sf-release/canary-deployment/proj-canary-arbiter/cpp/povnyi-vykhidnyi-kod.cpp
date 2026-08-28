#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <atomic>
#include <chrono>
#include <thread>
#include <mutex>
#include <algorithm>
#include <memory>
#include <functional>
#include <span>
#include <cstdint>

// ── Алгоритм швидкого некриптографічного гешування FNV-1a ───────────────────
[[nodiscard]] constexpr uint32_t fnv1a_hash(std::string_view key) noexcept {
    uint32_t hash = 2166136261u;
    for (char c : key) {
        hash ^= static_cast<uint8_t>(c);
        hash *= 16777619u;
    }
    return hash;
}

// ── Структура результату виконання одного запиту ─────────────────────────────
struct alignas(64) RequestMetrics {
    std::atomic<uint64_t> total_requests{0};
    std::atomic<uint64_t> failed_requests{0};
    std::atomic<uint64_t> total_latency_us{0};

    // Гістограма затримок: 0-10ms, 10-25ms, 25-50ms, 50-100ms, 100-250ms, 250ms+
    static constexpr size_t BUCKETS = 6;
    std::atomic<uint64_t> latency_buckets[BUCKETS]{};

    void record(uint64_t latency_us, bool is_error) noexcept {
        total_requests.fetch_add(1, std::memory_order_relaxed);
        if (is_error) {
            failed_requests.fetch_add(1, std::memory_order_relaxed);
        }
        total_latency_us.fetch_add(latency_us, std::memory_order_relaxed);

        size_t b = 0;
        if (latency_us < 10'000)      b = 0;
        else if (latency_us < 25'000) b = 1;
        else if (latency_us < 50'000) b = 2;
        else if (latency_us < 100'000) b = 3;
        else if (latency_us < 250'000) b = 4;
        else                           b = 5;

        latency_buckets[b].fetch_add(1, std::memory_order_relaxed);
    }

    void reset() noexcept {
        total_requests.store(0, std::memory_order_relaxed);
        failed_requests.store(0, std::memory_order_relaxed);
        total_latency_us.store(0, std::memory_order_relaxed);
        for (auto& b : latency_buckets) {
            b.store(0, std::memory_order_relaxed);
        }
    }
};

// ── Клас внутрішньопроцесного канаркового арбітра ───────────────────────────
class CanaryTrafficArbiter {
public:
    enum class TargetVariant : uint8_t {
        Baseline = 0,
        Canary = 1
    };

    struct Config {
        uint32_t initial_weight_pct = 2;         // Початкова вага канарки (0..100)
        double max_error_rate_delta = 0.005;     // Допустиме перевищення частки помилок (+0.5%)
        uint64_t max_p99_latency_us = 100'000;    // Максимальна затримка p99 (100 мс)
        std::chrono::milliseconds eval_interval{200}; // Період роботи арбітра
    };

    using AlertCallback = std::function<void(std::string_view reason, double canary_err, double base_err)>;

    explicit CanaryTrafficArbiter(Config config, AlertCallback alert_cb = nullptr)
        : config_(config),
          alert_callback_(std::move(alert_cb)),
          canary_weight_pct_(config.initial_weight_pct),
          is_running_(true) {
        arbiter_thread_ = std::thread(&CanaryTrafficArbiter::evaluation_loop, this);
    }

    ~CanaryTrafficArbiter() {
        is_running_.store(false, std::memory_order_release);
        if (arbiter_thread_.joinable()) {
            arbiter_thread_.join();
        }
    }

    // Заборона копіювання (RAII-ресурс потоку)
    CanaryTrafficArbiter(const CanaryTrafficArbiter&) = delete;
    CanaryTrafficArbiter& operator=(const CanaryTrafficArbiter&) = delete;

    // Консистентний вибір цільового пулу для вхідного користувача
    [[nodiscard]] TargetVariant route_request(std::string_view user_id) const noexcept {
        const uint32_t current_weight = canary_weight_pct_.load(std::memory_order_acquire);
        if (current_weight == 0) {
            return TargetVariant::Baseline;
        }

        const uint32_t bucket = fnv1a_hash(user_id) % 100;
        return (bucket < current_weight) ? TargetVariant::Canary : TargetVariant::Baseline;
    }

    // Реєстрація метрик запиту
    void record_outcome(TargetVariant variant, uint64_t latency_us, bool is_error) noexcept {
        if (variant == TargetVariant::Canary) {
            canary_metrics_.record(latency_us, is_error);
        } else {
            baseline_metrics_.record(latency_us, is_error);
        }
    }

    [[nodiscard]] uint32_t get_current_weight() const noexcept {
        return canary_weight_pct_.load(std::memory_order_relaxed);
    }

    void set_weight(uint32_t weight) noexcept {
        canary_weight_pct_.store(std::min(weight, 100u), std::memory_order_release);
    }

    void emergency_rollback(std::string_view reason) noexcept {
        canary_weight_pct_.store(0, std::memory_order_release);
        std::cerr << "[ROLLBACK TRIGGERED] " << reason << " -> Вага канарки скинута до 0%\n";
    }

private:
    void evaluation_loop() {
        while (is_running_.load(std::memory_order_acquire)) {
            std::this_thread::sleep_for(config_.eval_interval);

            const uint32_t weight = canary_weight_pct_.load(std::memory_order_acquire);
            if (weight == 0) continue;

            const uint64_t c_total = canary_metrics_.total_requests.load(std::memory_order_relaxed);
            const uint64_t b_total = baseline_metrics_.total_requests.load(std::memory_order_relaxed);

            // Захист від малого обсягу вибірки: вимагаємо мінімум 50 запитів
            if (c_total < 50 || b_total < 50) continue;

            const uint64_t c_err = canary_metrics_.failed_requests.load(std::memory_order_relaxed);
            const uint64_t b_err = baseline_metrics_.failed_requests.load(std::memory_order_relaxed);

            const double c_rate = static_cast<double>(c_err) / static_cast<double>(c_total);
            const double b_rate = static_cast<double>(b_err) / static_cast<double>(b_total);

            // 1. Перевірка перевищення частки помилок
            if (c_rate > b_rate + config_.max_error_rate_delta) {
                std::string msg = "Деградація частоти помилок: Canary=" +
                                  std::to_string(c_rate * 100.0) + "% vs Baseline=" +
                                  std::to_string(b_rate * 100.0) + "%";
                emergency_rollback(msg);
                if (alert_callback_) {
                    alert_callback_(msg, c_rate, b_rate);
                }
                continue;
            }

            // 2. Оцінка 99-го перцентиля затримки
            const uint64_t high_latency_count = canary_metrics_.latency_buckets[5].load(std::memory_order_relaxed);
            const double tail_ratio = static_cast<double>(high_latency_count) / static_cast<double>(c_total);
            if (tail_ratio > 0.01) { // Понад 1% запитів перевищують 250 мс
                std::string msg = "Деградація хвоста затримок p99: >250мс для " +
                                  std::to_string(tail_ratio * 100.0) + "% запитів";
                emergency_rollback(msg);
                if (alert_callback_) {
                    alert_callback_(msg, c_rate, b_rate);
                }
            }
        }
    }

    Config config_;
    AlertCallback alert_callback_;
    alignas(64) std::atomic<uint32_t> canary_weight_pct_{0};
    std::atomic<bool> is_running_{false};

    RequestMetrics baseline_metrics_;
    RequestMetrics canary_metrics_;

    std::thread arbiter_thread_;
};
