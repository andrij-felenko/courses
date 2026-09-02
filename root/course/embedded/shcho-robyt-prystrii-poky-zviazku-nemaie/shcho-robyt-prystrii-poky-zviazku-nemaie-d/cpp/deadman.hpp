#pragma once

#include <chrono>
#include <cstdint>

#include "hardware.hpp"

namespace cart {

// Таймер мертвої руки: дозвіл на енергію, що його поновлює ВИКЛЮЧНО
// декодований і автентифікований кадр. Поки дозвіл дійсний, service()
// тактує лінію ENABLE; щойно дедлайн минув — імпульси припиняються, і
// залізо гасить каскад саме, без участі цього коду.
//
// На відміну від C-версії тут немає танцю навколо переповнення лічильника:
// std::chrono::milliseconds — знаковий 64-бітний лічильник, порівняння чесне.
class Deadman {
public:
    Deadman(Board& board, Millis timeout, Millis heartbeat) noexcept
        : board_{board}, timeout_{timeout}, heartbeat_{heartbeat},
          deadline_{board.now() + timeout}, lastPulse_{board.now()} {
        board_.pulseInterlock();   // перший імпульс піднімає лінію ENABLE
    }

    void feed(Millis now) noexcept {
        deadline_ = now + timeout_;
        tripped_ = false;
    }

    [[nodiscard]] bool expired(Millis now) const noexcept { return now > deadline_; }

    [[nodiscard]] Millis remaining(Millis now) const noexcept {
        return now >= deadline_ ? Millis{0} : deadline_ - now;
    }

    void service(Millis now) noexcept {
        if (expired(now)) {
            if (!tripped_) {
                tripped_ = true;
                ++trips_;
            }
            return;   // мовчимо: за kInterlockHold супервізор сам зніме ENABLE
        }
        if (now - lastPulse_ >= heartbeat_) {
            board_.pulseInterlock();
            lastPulse_ = now;
        }
    }

    [[nodiscard]] std::uint32_t trips() const noexcept { return trips_; }

private:
    Board& board_;
    Millis timeout_;
    Millis heartbeat_;
    Millis deadline_;
    Millis lastPulse_;
    std::uint32_t trips_{0};
    bool tripped_{false};
};

}  // namespace cart
