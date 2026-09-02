#pragma once

#include <algorithm>
#include <chrono>

#include "platform.hpp"

namespace bringup {

// Блокувати процесор на десятки мілісекунд не можна: за цей час не годується
// сторожовий таймер. Тому подачу живлення лише позначаємо міткою часу, а факт
// виходу на режим перевіряємо в головному циклі.
class PowerGuard {
public:
    PowerGuard(platform::PowerRail& rail, std::chrono::milliseconds boot_time) noexcept
        : rail_{rail}, boot_time_{boot_time} {}

    void power_on() noexcept {
        rail_.on();
        powered_at_ = platform::Clock::now();
        stable_ = false;
    }

    void power_off() noexcept {
        rail_.off();
        stable_ = false;
    }

    [[nodiscard]] bool ready() noexcept {
        if (!stable_ && platform::Clock::now() - powered_at_ >= boot_time_) {
            stable_ = true;  // один раз вийшли на режим — далі не перевіряємо
        }
        return stable_;
    }

    [[nodiscard]] std::chrono::milliseconds remaining() const noexcept {
        const auto elapsed = platform::Clock::now() - powered_at_;
        return std::max(std::chrono::milliseconds::zero(), boot_time_ - elapsed);
    }

private:
    platform::PowerRail& rail_;
    std::chrono::milliseconds boot_time_;
    platform::Clock::time_point powered_at_{};
    bool stable_{false};
};

}  // namespace bringup
