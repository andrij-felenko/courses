/* ============================================================================
 * Інструментація бізнес-операції на сучасному C++20 (RAII Scoped Timer)
 * ============================================================================ */
#include <iostream>
#include <chrono>
#include <atomic>
#include <string_view>

class ScopedLatencyTimer {
public:
    using Clock = std::chrono::steady_clock;

    explicit ScopedLatencyTimer(std::atomic<uint64_t>& request_counter,
                                std::atomic<uint64_t>& error_counter) noexcept
        : requests_(request_counter),
          errors_(error_counter),
          start_time_(Clock::now()),
          is_success_(true) {
        requests_.fetch_add(1, std::memory_order_relaxed);
    }

    void mark_failure() noexcept {
        is_success_ = false;
    }

    ~ScopedLatencyTimer() {
        if (!is_success_) {
            errors_.fetch_add(1, std::memory_order_relaxed);
        }
        auto duration = Clock::now() - start_time_;
        auto duration_ms = std::chrono::duration_cast<std::chrono::microseconds>(duration).count();
        // duration_ms передається у відповідний кошик гістограми
        (void)duration_ms;
    }

private:
    std::atomic<uint64_t>& requests_;
    std::atomic<uint64_t>& errors_;
    Clock::time_point start_time_;
    bool is_success_;
};

/* Приклад використання у бізнес-сервісі */
class PaymentService {
public:
    bool process_order(uint64_t order_id, double amount) {
        ScopedLatencyTimer timer(requests_total_, errors_total_);

        if (amount <= 0.0) {
            timer.mark_failure();
            return false;
        }

        if (order_id % 7 == 0) {
            timer.mark_failure();
            return false;
        }

        return true;
    }

private:
    std::atomic<uint64_t> requests_total_{0};
    std::atomic<uint64_t> errors_total_{0};
};
