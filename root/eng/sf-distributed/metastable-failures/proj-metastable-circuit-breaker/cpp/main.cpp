#include <iostream>
#include <chrono>
#include <atomic>
#include <expected>
#include <algorithm>
#include <poll.h>
#include <sys/socket.h>
#include <unistd.h>

namespace resilience {

using MonotonicClock = std::chrono::steady_clock;
using TimePoint = MonotonicClock::time_point;
using Milliseconds = std::chrono::milliseconds;

/* =========================================================================
 * 1. Клієнтський рівень: Регулятор бюджету повторних спроб (Retry Budget)
 * ========================================================================= */

class RetryBudget {
public:
    explicit RetryBudget(int64_t max_tokens = 1000, double retry_fraction = 0.1)
        : total_tokens_(max_tokens),
          max_tokens_(max_tokens),
          retry_fraction_(retry_fraction) {}

    // Викликається після успішного первинного запиту для наповнення бюджету
    void record_success() noexcept {
        const int64_t add = static_cast<int64_t>(100.0 * retry_fraction_);
        int64_t cur = total_tokens_.load(std::memory_order_relaxed);
        while (cur < max_tokens_) {
            const int64_t next = std::min(max_tokens_, cur + add);
            if (total_tokens_.compare_exchange_weak(cur, next, 
                                                    std::memory_order_release, 
                                                    std::memory_order_relaxed)) {
                break;
            }
        }
    }

    // Спроба отримати дозвіл на повторний запит (списання 100 токенів)
    [[nodiscard]] bool try_acquire_retry() noexcept {
        constexpr int64_t kRetryCost = 100;
        int64_t cur = total_tokens_.load(std::memory_order_relaxed);
        while (cur >= kRetryCost) {
            if (total_tokens_.compare_exchange_weak(cur, cur - kRetryCost, 
                                                    std::memory_order_acq_rel, 
                                                    std::memory_order_relaxed)) {
                return true; // Дозвіл надано
            }
        }
        return false; // Бюджет вичерпано, блокуємо каскадне множення навантаження
    }

private:
    std::atomic<int64_t> total_tokens_;
    int64_t max_tokens_;
    double retry_fraction_;
};

/* =========================================================================
 * 2. Серверний рівень: RAII-вартовий дедлайну та стану з'єднання
 * ========================================================================= */

enum class ShedReason {
    DeadlineExceeded,
    ClientDisconnected
};

class RequestGuard {
public:
    RequestGuard(int socket_fd, Milliseconds timeout, Milliseconds min_exec_time)
        : socket_fd_(socket_fd),
          deadline_(MonotonicClock::now() + timeout),
          min_exec_time_(min_exec_time) {}

    // Перевірка 1: Чи достатньо часу залишається до закінчення дедлайну
    [[nodiscard]] bool is_viable() const noexcept {
        const auto now = MonotonicClock::now();
        if (now >= deadline_) {
            return false;
        }
        return (deadline_ - now) >= min_exec_time_;
    }

    // Перевірка 2: Неблокуюча діагностика відключення клієнта
    [[nodiscard]] bool is_client_connected() const noexcept {
        if (socket_fd_ < 0) {
            return false;
        }
        pollfd pfd{socket_fd_, POLLIN | POLLHUP | POLLERR, 0};
        int res = ::poll(&pfd, 1, 0);
        if (res < 0) return false;

        if (res > 0) {
            if (pfd.revents & (POLLHUP | POLLERR | POLLNVAL)) {
                return false;
            }
            char peek_byte;
            ssize_t n = ::recv(socket_fd_, &peek_byte, 1, MSG_PEEK | MSG_DONTWAIT);
            if (n == 0) {
                return false; // Отримано EOF (FIN-пакет)
            }
        }
        return true;
    }

    [[nodiscard]] Milliseconds remaining_time() const noexcept {
        const auto now = MonotonicClock::now();
        if (now >= deadline_) return Milliseconds{0};
        return std::chrono::duration_cast<Milliseconds>(deadline_ - now);
    }

private:
    int socket_fd_;
    TimePoint deadline_;
    Milliseconds min_exec_time_;
};

/* =========================================================================
 * 3. Серверний обробник з використанням std::expected
 * ========================================================================= */

struct ExecutionResult {
    uint64_t processed_items;
    Milliseconds time_taken;
};

std::expected<ExecutionResult, ShedReason> 
process_client_request(const RequestGuard& guard) {
    // 1. Бар'єр дедлайну на вході
    if (!guard.is_viable()) {
        return std::unexpected(ShedReason::DeadlineExceeded);
    }

    // 2. Бар'єр відключення перед зверненням до бази даних
    if (!guard.is_client_connected()) {
        return std::unexpected(ShedReason::ClientDisconnected);
    }

    // 3. Імітація корисної роботи
    const auto start = MonotonicClock::now();
    ::usleep(20000); // 20 ms
    const auto duration = std::chrono::duration_cast<Milliseconds>(MonotonicClock::now() - start);

    // 4. Повторна верифікація перед фіксацією стану
    if (!guard.is_client_connected()) {
        return std::unexpected(ShedReason::ClientDisconnected);
    }

    return ExecutionResult{
        .processed_items = 42,
        .time_taken = duration
    };
}

} // namespace resilience
