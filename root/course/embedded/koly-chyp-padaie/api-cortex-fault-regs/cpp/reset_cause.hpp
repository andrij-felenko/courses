// reset_cause.hpp — «липкі» прапорці причини скидання (RCC->CSR).
//
// Прапорці переживають перезапуск і накопичуються, доки їх не зітруть
// записом RMVF. Тому знімок робиться рівно один раз на старті й одразу
// з очищенням: клас навмисно не дає способу прочитати CSR, не стерши його.
#pragma once

#include <cstdint>

#include "stm32f4xx.h"  // CMSIS: RCC_CSR_*

// Старіші заголовки STM32 звуть прапорець піна NRST інакше.
#ifndef RCC_CSR_PINRSTF
#define RCC_CSR_PINRSTF RCC_CSR_PADRSTF
#endif

namespace reset {

enum class Cause : std::uint32_t {
    none          = 0,
    low_power     = RCC_CSR_LPWRRSTF,
    window_wdt    = RCC_CSR_WWDGRSTF,
    independent_wdt = RCC_CSR_IWDGRSTF,
    software      = RCC_CSR_SFTRSTF,
    power_on      = RCC_CSR_PORRSTF,
    nrst_pin      = RCC_CSR_PINRSTF,
    brown_out     = RCC_CSR_BORRSTF,
};

constexpr Cause operator|(Cause lhs, Cause rhs)
{
    return static_cast<Cause>(static_cast<std::uint32_t>(lhs) | static_cast<std::uint32_t>(rhs));
}

constexpr Cause operator&(Cause lhs, Cause rhs)
{
    return static_cast<Cause>(static_cast<std::uint32_t>(lhs) & static_cast<std::uint32_t>(rhs));
}

constexpr bool any(Cause value)
{
    return value != Cause::none;
}

class Status {
public:
    // Читає RCC->CSR і негайно стирає прапорці. Викликати першою дією main().
    static Status capture();

    Cause causes() const { return causes_; }
    std::uint32_t raw() const { return raw_; }

    // Прошивка зависла: підняв сторож.
    bool hung() const;
    // Живлення просідало: вміст RAM недійсний.
    bool cold() const;
    // Перезапуск замовила сама прошивка.
    bool requested() const;

    void report() const;

private:
    explicit Status(std::uint32_t raw);

    std::uint32_t raw_;
    Cause         causes_;
};

}  // namespace reset
