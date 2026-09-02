#include "mcu/system_clock.hpp"

#include "stm32f4xx.h"

namespace mcu {
namespace {

constexpr std::uint32_t kHseHz = 8'000'000;
constexpr std::uint32_t kHsiHz = 16'000'000;

// Скільки порожніх обертів чекаємо на кожен апаратний прапорець готовності.
constexpr std::uint32_t kWaitLoops = 200'000;

// Обидва набори дають 1 МГц на вході VCO і 168 МГц на виході.
constexpr PllConfig kFromHse{8, 336, 2, 7};
constexpr PllConfig kFromHsi{16, 336, 2, 7};

// Коефіцієнти судить компілятор — на плату помилковий набір не доїде взагалі.
static_assert(kFromHse.valid(kHseHz), "PLL від HSE поза межами документації");
static_assert(kFromHsi.valid(kHsiHz), "PLL від HSI поза межами документації");
static_assert(kFromHse.sysclk(kHseHz) == 168'000'000);

ClockState s_state{ClockSource::Hsi, kHsiHz};

[[nodiscard]] bool wait_flag(const volatile std::uint32_t& reg, std::uint32_t mask,
                             bool expect_set) noexcept
{
    for (std::uint32_t i = 0; i < kWaitLoops; ++i) {
        if (((reg & mask) != 0U) == expect_set) {
            return true;
        }
    }
    return false;
}

[[nodiscard]] bool set_flash_latency(std::uint32_t wait_states) noexcept
{
    std::uint32_t acr = FLASH->ACR;
    acr &= ~FLASH_ACR_LATENCY;
    acr |= (wait_states & FLASH_ACR_LATENCY) | FLASH_ACR_PRFTEN | FLASH_ACR_ICEN
         | FLASH_ACR_DCEN;
    FLASH->ACR = acr;

    // Затримку читання підтверджуємо зворотним читанням: інакше ядро зависне
    // на першій же вибірці інструкції з Flash.
    return (FLASH->ACR & FLASH_ACR_LATENCY) == (wait_states & FLASH_ACR_LATENCY);
}

// Гарантований відкат: HSI 16 МГц, нульова затримка Flash, PLL вимкнено.
std::unexpected<ClockError> fallback(ClockError error) noexcept
{
    RCC->CR |= RCC_CR_HSION;
    static_cast<void>(wait_flag(RCC->CR, RCC_CR_HSIRDY, true));

    RCC->CFGR &= ~RCC_CFGR_SW;
    static_cast<void>(wait_flag(RCC->CFGR, RCC_CFGR_SWS, false));

    RCC->CR &= ~RCC_CR_PLLON;
    static_cast<void>(wait_flag(RCC->CR, RCC_CR_PLLRDY, false));

    RCC->CFGR &= ~(RCC_CFGR_HPRE | RCC_CFGR_PPRE1 | RCC_CFGR_PPRE2);
    static_cast<void>(set_flash_latency(0));

    s_state = ClockState{ClockSource::Hsi, kHsiHz};
    SystemCoreClock = kHsiHz;
    return std::unexpected(error);
}

}  // namespace

std::expected<ClockState, ClockError> SystemClock::configure() noexcept
{
    // 1. Відомий стан: сідаємо на HSI, PLL вимикаємо.
    RCC->CR |= RCC_CR_HSION;
    if (!wait_flag(RCC->CR, RCC_CR_HSIRDY, true)) {
        return std::unexpected(ClockError::HsiDead);
    }
    RCC->CFGR &= ~RCC_CFGR_SW;
    static_cast<void>(wait_flag(RCC->CFGR, RCC_CFGR_SWS, false));

    RCC->CR &= ~RCC_CR_PLLON;
    static_cast<void>(wait_flag(RCC->CR, RCC_CR_PLLRDY, false));

    // 2. Пробуємо кварц. Не завівся — це не привід зависати назавжди.
    RCC->CR |= RCC_CR_HSEON;
    const bool from_hse = wait_flag(RCC->CR, RCC_CR_HSERDY, true);
    if (!from_hse) {
        RCC->CR &= ~RCC_CR_HSEON;
    }

    const PllConfig& pll = from_hse ? kFromHse : kFromHsi;
    const std::uint32_t src_hz = from_hse ? kHseHz : kHsiHz;
    if (!pll.valid(src_hz)) {
        return fallback(ClockError::InvalidPll);
    }

    // 3. Живлення й затримка Flash — до підняття частоти, а не після.
    RCC->APB1ENR |= RCC_APB1ENR_PWREN;
    static_cast<void>(RCC->APB1ENR);
    PWR->CR |= PWR_CR_VOS;   // режим напруги 1: дозволяє 168 МГц

    if (!set_flash_latency(FLASH_ACR_LATENCY_5WS)) {
        return fallback(ClockError::SwitchTimeout);
    }

    // 4. Дільники шин: AHB 168, APB1 42, APB2 84 МГц.
    RCC->CFGR &= ~(RCC_CFGR_HPRE | RCC_CFGR_PPRE1 | RCC_CFGR_PPRE2);
    RCC->CFGR |= RCC_CFGR_HPRE_DIV1 | RCC_CFGR_PPRE1_DIV4 | RCC_CFGR_PPRE2_DIV2;

    RCC->PLLCFGR = (pll.m << 0U) | (pll.n << 6U) | (((pll.p / 2U) - 1U) << 16U)
                 | (pll.q << 24U) | (from_hse ? RCC_PLLCFGR_PLLSRC_HSE : 0U);

    // 5. Захоплення PLL з обмеженим очікуванням.
    RCC->CR |= RCC_CR_PLLON;
    if (!wait_flag(RCC->CR, RCC_CR_PLLRDY, true)) {
        return fallback(ClockError::PllTimeout);
    }

    // 6. Перемикання SYSCLK: поле SWS має підтвердити перехід.
    RCC->CFGR = (RCC->CFGR & ~RCC_CFGR_SW) | RCC_CFGR_SW_PLL;
    for (std::uint32_t i = 0; i < kWaitLoops; ++i) {
        if ((RCC->CFGR & RCC_CFGR_SWS) == RCC_CFGR_SWS_PLL) {
            s_state = ClockState{from_hse ? ClockSource::HsePll : ClockSource::HsiPll,
                                 pll.sysclk(src_hz)};
            SystemCoreClock = s_state.sysclk_hz;
            return s_state;
        }
    }
    return fallback(ClockError::SwitchTimeout);
}

ClockState SystemClock::state() noexcept
{
    return s_state;
}

void SystemClock::delay(std::chrono::milliseconds d) noexcept
{
    const std::uint32_t ticks = s_state.sysclk_hz / 1000U;
    if (ticks == 0U || ticks > SysTick_LOAD_RELOAD_Msk) {
        return;   // частота поза межами лічильника: краще нічого, ніж вічний цикл
    }

    SysTick->LOAD = ticks - 1U;
    SysTick->VAL = 0U;
    SysTick->CTRL = SysTick_CTRL_CLKSOURCE_Msk | SysTick_CTRL_ENABLE_Msk;

    for (auto ms = d.count(); ms > 0; --ms) {
        while ((SysTick->CTRL & SysTick_CTRL_COUNTFLAG_Msk) == 0U) {
        }
    }
    SysTick->CTRL = 0U;
}

std::string_view to_string(ClockError error) noexcept
{
    switch (error) {
        case ClockError::PllTimeout:    return "PLL не захопився";
        case ClockError::SwitchTimeout: return "перемикач SYSCLK не відповів";
        case ClockError::InvalidPll:    return "коефіцієнти PLL поза межами";
        case ClockError::HsiDead:       return "внутрішній генератор не завівся";
    }
    return "невідомий стан";
}

}  // namespace mcu
