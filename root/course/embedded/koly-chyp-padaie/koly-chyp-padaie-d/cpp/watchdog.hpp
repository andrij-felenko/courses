#pragma once

#include <cstdint>

#include "stm32f4xx.h"

namespace watchdog {

// Незалежний сторож тактується власним LSI (~32 кГц) і працює навіть тоді,
// коли основний резонатор зірвався. Запущений раз — вимкнути вже не можна.
class Independent {
public:
    // Дільник 64 дає 500 тактів на секунду; перезавантаження 1000 ≈ 2 с.
    void start(std::uint32_t reload = 1000U, std::uint32_t prescaler = 4U) noexcept
    {
        IWDG->KR  = kWriteAccess;
        IWDG->PR  = prescaler;
        IWDG->RLR = reload;
        while (IWDG->SR != 0U) {
            // чекаємо, доки значення перепишуться в тактовий домен LSI
        }
        IWDG->KR = kFeed;
        IWDG->KR = kStart;
    }

    void kick() const noexcept { IWDG->KR = kFeed; }

private:
    static constexpr std::uint32_t kWriteAccess = 0x0000'5555U;
    static constexpr std::uint32_t kFeed        = 0x0000'AAAAU;
    static constexpr std::uint32_t kStart       = 0x0000'CCCCU;
};

} // namespace watchdog
