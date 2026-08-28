#include <iostream>
#include <cstdint>
#include <chrono>
#include <concepts>
#include <cassert>

using namespace std::chrono_literals;

/* Типізований монотонний макет часу */
class MockClock {
public:
    using duration = std::chrono::milliseconds;
    using rep = uint16_t;

    static void setTime(rep ticks) noexcept {
        ticks_ = ticks;
    }

    static void advance(duration delta) noexcept {
        ticks_ = static_cast<rep>(ticks_ + delta.count());
    }

    static rep now() noexcept {
        return ticks_;
    }

private:
    static inline rep ticks_{0};
};

/* Надійний сторожовий модуль на шаблоні джерела часу */
template <typename Clock, uint16_t TimeoutMs = 100>
class SafeWatchdog {
public:
    enum class State { Ok, Tripped };

    explicit SafeWatchdog(typename Clock::rep now) noexcept
        : lastHeartbeat_{now}, state_{State::Ok}, tripCount_{0} {}

    void feed(typename Clock::rep now) noexcept {
        lastHeartbeat_ = now;
        state_ = State::Ok;
    }

    State check(typename Clock::rep now) noexcept {
        // Явне модульне віднімання у просторі uint16_t
        const uint16_t elapsed = static_cast<uint16_t>(now - lastHeartbeat_);
        if (elapsed > TimeoutMs) {
            state_ = State::Tripped;
            ++tripCount_;
        } else {
            state_ = State::Ok;
        }
        return state_;
    }

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] uint32_t tripCount() const noexcept { return tripCount_; }

private:
    typename Clock::rep lastHeartbeat_;
    State state_;
    uint32_t tripCount_;
};

int main() {
    std::cout << "=== Запуск C++20 регресійного стенду Time-Warp ===\n";

    // Тест 1: Штатний режим
    MockClock::setTime(1000);
    SafeWatchdog<MockClock, 100> wd(MockClock::now());

    for (int i = 0; i < 5; ++i) {
        MockClock::advance(20ms);
        assert(wd.check(MockClock::now()) == SafeWatchdog<MockClock, 100>::State::Ok);
        wd.feed(MockClock::now());
    }
    std::cout << "[TEST] 1. Штатна робота... PASSED\n";

    // Тест 2: Стрибок 65530 -> 10 (Rollover)
    MockClock::setTime(65530);
    wd.feed(MockClock::now());

    MockClock::advance(16ms); // Новий час: 10
    assert(MockClock::now() == 10);
    assert(wd.check(MockClock::now()) == SafeWatchdog<MockClock, 100>::State::Ok);
    std::cout << "[TEST] 2. Переповнення без втрати пакетів... PASSED\n";

    // Тест 3: Справжній таймаут через границю
    MockClock::setTime(65500);
    wd.feed(MockClock::now());

    MockClock::advance(105ms); // Новий час: 69
    assert(MockClock::now() == 69);
    assert(wd.check(MockClock::now()) == SafeWatchdog<MockClock, 100>::State::Tripped);
    assert(wd.tripCount() == 1);
    std::cout << "[TEST] 3. Справжній таймаут на межі... PASSED\n";

    // Тест 4: Псевдовипадковий фазинг
    MockClock::setTime(65450);
    wd.feed(MockClock::now());
    uint32_t rnd = 0xCAFEBABE;
    for (int i = 0; i < 1000; ++i) {
        rnd = rnd * 1664525U + 1013904223U;
        uint32_t step = 5 + (rnd % 25);
        MockClock::advance(std::chrono::milliseconds(step));
        assert(wd.check(MockClock::now()) == SafeWatchdog<MockClock, 100>::State::Ok);
        wd.feed(MockClock::now());
    }
    std::cout << "[TEST] 4. C++20 фазинг навколо межі... PASSED (1000 ітерацій)\n";

    std::cout << "=== Усі тести C++20 завершено успішно ===\n";
    return 0;
}
