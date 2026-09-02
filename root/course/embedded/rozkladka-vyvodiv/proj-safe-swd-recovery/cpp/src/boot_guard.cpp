#include "mcu/boot_guard.hpp"

#include "stm32f4xx.h"

#include <cstdint>

namespace mcu::boot {
namespace {

constexpr std::uint32_t kRecoveryPin = 0;   // PA0

// Груба калібровка порожнього циклу для HSI 16 МГц. Систем-таймер тут не
// вживаємо навмисно: дерево тактування ще не налаштоване й може бути збійним.
constexpr std::uint32_t kLoopsPerMs = 1500;

void spin(std::chrono::milliseconds d) noexcept
{
    for (auto ms = d.count(); ms > 0; --ms) {
        for (volatile std::uint32_t i = 0; i < kLoopsPerMs; ++i) {
            __NOP();
        }
    }
}

void recovery_input_init() noexcept
{
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    static_cast<void>(RCC->AHB1ENR);   // зворотне читання: чекаємо тактування порту

    constexpr std::uint32_t shift = kRecoveryPin * 2;
    GPIOA->MODER &= ~(0x3U << shift);          // вхід
    GPIOA->PUPDR &= ~(0x3U << shift);
    GPIOA->PUPDR |= (0x2U << shift);           // підтяжка вниз

    spin(std::chrono::milliseconds{1});        // хай ємність лінії розрядиться
}

[[nodiscard]] bool pressed() noexcept
{
    return (GPIOA->IDR & (1U << kRecoveryPin)) != 0U;
}

// Натиснуто = kDebounce підряд однакових вибірок.
[[nodiscard]] bool held(std::chrono::milliseconds budget) noexcept
{
    std::chrono::milliseconds stable{0};

    for (auto ms = budget.count(); ms > 0; --ms) {
        if (pressed()) {
            stable += std::chrono::milliseconds{1};
            if (stable >= kDebounce) {
                return true;
            }
        } else {
            stable = std::chrono::milliseconds{0};
        }
        spin(std::chrono::milliseconds{1});
    }
    return false;
}

}  // namespace

void keep_debug_in_low_power() noexcept
{
    DBGMCU->CR |= DBGMCU_CR_DBG_SLEEP | DBGMCU_CR_DBG_STOP | DBGMCU_CR_DBG_STANDBY;
    __DSB();
}

bool debugger_attached() noexcept
{
    return (CoreDebug->DHCSR & CoreDebug_DHCSR_C_DEBUGEN_Msk) != 0U;
}

GuardResult guard(std::chrono::milliseconds window) noexcept
{
    keep_debug_in_low_power();
    recovery_input_init();

    // Аварійний вихід опитуємо першим: він мусить працювати завжди.
    if (held(kDebounce * 2)) {
        return GuardResult::HeldByOperator;
    }

    // Налагоджувач уже на шині — чекати нема на кого.
    if (debugger_attached()) {
        return GuardResult::Proceed;
    }

    return held(window) ? GuardResult::HeldByOperator : GuardResult::Proceed;
}

void park() noexcept
{
    // Переривання глушимо: чужий таймер здатен приспати ядро з обробника.
    __disable_irq();

    for (;;) {
        __NOP();
    }
}

}  // namespace mcu::boot
