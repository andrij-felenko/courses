// WakeupTimer.hpp — RTC Wakeup Timer на LSE як джерело пробудження за часом.
#pragma once

#include <chrono>
#include <cstdint>

namespace emb::hal {

class WakeupTimer {
public:
    // Стеля одного заходу: 65535 відліків по 1/2048 с.
    static constexpr std::chrono::milliseconds MaxTimeout{31'999};

    static void init() noexcept;

    // Повертає ФАКТИЧНИЙ горизонт: довший простій розбивається на кілька снів.
    [[nodiscard]] static std::chrono::milliseconds arm(std::chrono::milliseconds timeout) noexcept;

    static void disarm() noexcept;

    // Скільки минуло від програмування — рахуємо по календарю RTC,
    // бо лічильник WUT назовні не читається.
    [[nodiscard]] static std::chrono::milliseconds elapsedSinceArm() noexcept;

    [[nodiscard]] static bool expired() noexcept { return s_expired; }

private:
    [[nodiscard]] static std::chrono::milliseconds now() noexcept;

    static inline std::chrono::milliseconds s_armedAt{0};
    static inline volatile bool s_expired{false};

    friend void rtcWakeupIsr() noexcept;
};

void rtcWakeupIsr() noexcept;

} // namespace emb::hal
