#pragma once

// Монотонний час пристрою. Тип std::chrono::milliseconds замість голого
// uint32_t — не косметика: він не дає відняти позицію від строку життя і
// прибирає цілий клас помилок «мілісекунди проти секунд».
//
// На МК тут був би лічильник SysTick; на занятті час рухає демонстрація,
// щоб сценарії не тривали реальних десяти секунд.

#include <chrono>

namespace cmdctl {

using Millis = std::chrono::milliseconds;
using namespace std::chrono_literals;

class SimClock {
public:
    [[nodiscard]] Millis now() const noexcept { return uptime_; }

    void advance(Millis dt) noexcept { uptime_ += dt; }

    // Скидання живлення: монотонний лічильник починається з нуля.
    void reset() noexcept { uptime_ = Millis{0}; }

private:
    Millis uptime_{0};
};

}  // namespace cmdctl
