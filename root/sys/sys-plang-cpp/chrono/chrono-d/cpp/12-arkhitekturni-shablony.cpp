// Шаблонний клас бізнес-логіки з можливістю підміни годинника в тестах
template <typename Clock = std::chrono::steady_clock>
class SessionTracker {
public:
    void touch() {
        last_activity_ = Clock::now();
    }

    bool is_expired(typename Clock::duration timeout) const {
        return (Clock::now() - last_activity_) > timeout;
    }
private:
    typename Clock::time_point last_activity_{Clock::now()};
};

// Мок-годинник для миттєвого підроблення часу в юніт-тестах без реальних затримок
struct MockClock {
    using rep = int64_t;
    using period = std::milli;
    using duration = std::chrono::duration<rep, period>;
    using time_point = std::chrono::time_point<MockClock, duration>;
    static inline time_point current_time{duration(0)};

    static time_point now() noexcept {
        return current_time;
    }

    static void advance(duration d) {
        current_time += d;
    }
};
