#pragma once

#include <algorithm>
#include <chrono>

#include "hardware.hpp"

namespace cart {

// Монотонний час пристрою з плавним підтягуванням до еталона сервера.
// Хід прискорюють або сповільнюють щонайбільше на kSlewPercent, тому
// повернена мітка НІКОЛИ не йде назад — навіть коли сервер каже, що
// годинник поспішає на три секунди.
class SlewClock {
public:
    explicit SlewClock(Millis raw) noexcept : lastRaw_{raw} {}

    [[nodiscard]] Millis now(Millis raw) const noexcept { return raw + offset_; }

    void setReference(Millis raw, Millis server) noexcept {
        // Різницю не застосовуємо стрибком — лише ставимо в чергу.
        pending_ = server - now(raw);
    }

    void tick(Millis raw) noexcept {
        const auto dt = raw - lastRaw_;
        lastRaw_ = raw;
        if (dt <= Millis{0} || pending_ == Millis{0}) return;

        auto step = dt * kSlewPercent / 100;
        if (step == Millis{0}) step = Millis{1};

        if (pending_ > Millis{0}) {
            step = std::min(step, pending_);
            offset_ += step;
            pending_ -= step;
        } else {
            step = std::min(step, -pending_);
            offset_ -= step;
            pending_ += step;
        }
    }

    [[nodiscard]] Millis pending() const noexcept { return pending_; }
    [[nodiscard]] Millis offset() const noexcept { return offset_; }

private:
    static constexpr int kSlewPercent = 5;

    Millis offset_{0};
    Millis pending_{0};
    Millis lastRaw_{0};
};

}  // namespace cart
