#include <iostream>
#include <chrono>
#include <optional>
#include <string_view>
#include <charconv>
#include <stop_token>
#include <cstdint>
#include <span>
#include <mutex>
#include <condition_variable>
#include <fcntl.h>
#include <poll.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>

class DeadlineContext {
public:
    using Clock = std::chrono::steady_clock;
    using TimePoint = Clock::time_point;
    using Milliseconds = std::chrono::milliseconds;

    /* Створення кореневого контексту з таймаутом і запасом */
    explicit DeadlineContext(Milliseconds timeout, Milliseconds margin = Milliseconds(10))
        : deadline_(Clock::now() + timeout), margin_(margin), stop_source_() {}

    /* Контекст із готовим абсолютним дедлайном */
    explicit DeadlineContext(TimePoint deadline, Milliseconds margin = Milliseconds(10))
        : deadline_(deadline), margin_(margin), stop_source_() {}

    /* Залишок часу до спливу дедлайну */
    [[nodiscard]] Milliseconds remaining() const noexcept {
        if (stop_source_.stop_requested()) {
            return Milliseconds::zero();
        }
        const auto now = Clock::now();
        if (now >= deadline_) {
            return Milliseconds::zero();
        }
        return std::chrono::duration_cast<Milliseconds>(deadline_ - now);
    }

    [[nodiscard]] bool is_expired() const noexcept {
        return remaining() <= Milliseconds::zero();
    }

    [[nodiscard]] TimePoint deadline() const noexcept { return deadline_; }
    [[nodiscard]] Milliseconds margin() const noexcept { return margin_; }
    [[nodiscard]] std::stop_token stop_token() const noexcept { return stop_source_.get_token(); }

    void cancel() noexcept {
        stop_source_.request_stop();
    }

private:
    TimePoint deadline_;
    Milliseconds margin_;
    std::stop_source stop_source_;
};
