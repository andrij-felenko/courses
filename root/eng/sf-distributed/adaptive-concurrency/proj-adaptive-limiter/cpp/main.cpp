#include <iostream>
#include <chrono>
#include <atomic>
#include <mutex>
#include <optional>
#include <algorithm>
#include <memory>

class AdaptiveVegasLimiter {
public:
    struct Config {
        double min_limit = 5.0;
        double max_limit = 1000.0;
        double initial_limit = 20.0;
        double headroom = 10.0;                // Запас черги h для пошуку максимуму
        double smoothing = 0.2;                // Коефіцієнт згладжування σ
        uint32_t sample_window = 50;           // Кількість запитів на вікно
        std::chrono::seconds min_rtt_ttl{300}; // 5 хвилин до старіння minRTT
    };

    // RAII-токен допуску: автоматично звільняє ресурс і фіксує час у деструкторі
    class Token {
    public:
        Token(AdaptiveVegasLimiter& parent)
            : parent_(parent), start_time_(std::chrono::steady_clock::now()), active_(true) {}

        ~Token() {
            if (active_) {
                release(true);
            }
        }

        Token(const Token&) = delete;
        Token& operator=(const Token&) = delete;

        Token(Token&& other) noexcept
            : parent_(other.parent_), start_time_(other.start_time_), active_(other.active_) {
            other.active_ = false;
        }

        void release(bool success = true) {
            if (active_) {
                auto end_time = std::chrono::steady_clock::now();
                auto duration_ms = std::chrono::duration<double, std::milli>(end_time - start_time_).count();
                parent_.on_request_completed(duration_ms, success);
                active_ = false;
            }
        }

    private:
        AdaptiveVegasLimiter& parent_;
        std::chrono::steady_clock::time_point start_time_;
        bool active_;
    };

    explicit AdaptiveVegasLimiter(Config cfg = {})
        : cfg_(cfg), current_limit_(cfg.initial_limit), in_flight_(0) {}

    // Спроба отримати допуск до виконання
    [[nodiscard]] std::optional<Token> try_acquire() {
        int current = in_flight_.load(std::memory_order_relaxed);
        if (static_cast<double>(current) >= current_limit_.load(std::memory_order_relaxed)) {
            return std::nullopt; // Швидке скидання навантаження (HTTP 429)
        }

        in_flight_.fetch_add(1, std::memory_order_acq_rel);
        return Token(*this);
    }

    [[nodiscard]] double current_limit() const noexcept {
        return current_limit_.load(std::memory_order_relaxed);
    }

    [[nodiscard]] int in_flight() const noexcept {
        return in_flight_.load(std::memory_order_relaxed);
    }

private:
    void on_request_completed(double duration_ms, bool success) {
        in_flight_.fetch_sub(1, std::memory_order_acq_rel);

        if (!success || duration_ms <= 0.0) {
            return;
        }

        std::lock_guard<std::mutex> lock(metrics_mutex_);
        auto now = std::chrono::steady_clock::now();

        // Скидання або оновлення базису minRTT
        if (!min_rtt_ms_ || (now - min_rtt_timestamp_) > cfg_.min_rtt_ttl) {
            min_rtt_ms_ = duration_ms;
            min_rtt_timestamp_ = now;
        } else {
            min_rtt_ms_ = std::min(*min_rtt_ms_, duration_ms);
        }

        sample_rtt_sum_ms_ += duration_ms;
        sample_count_++;

        if (sample_count_ >= cfg_.sample_window) {
            recalculate_limit();
        }
    }

    void recalculate_limit() {
        double sample_rtt = sample_rtt_sum_ms_ / static_cast<double>(sample_count_);
        double min_rtt = min_rtt_ms_.value_or(sample_rtt);

        if (sample_rtt > 0.0 && min_rtt > 0.0) {
            double gradient = min_rtt / sample_rtt;
            double current = current_limit_.load(std::memory_order_relaxed);

            double target = current * gradient + cfg_.headroom;
            double next = (1.0 - cfg_.smoothing) * current + cfg_.smoothing * target;

            next = std::clamp(next, cfg_.min_limit, cfg_.max_limit);
            current_limit_.store(next, std::memory_order_relaxed);
        }

        sample_count_ = 0;
        sample_rtt_sum_ms_ = 0.0;
    }

    const Config cfg_;
    std::atomic<double> current_limit_;
    std::atomic<int> in_flight_;

    std::mutex metrics_mutex_;
    std::optional<double> min_rtt_ms_;
    std::chrono::steady_clock::time_point min_rtt_timestamp_{};
    uint32_t sample_count_ = 0;
    double sample_rtt_sum_ms_ = 0.0;
};
