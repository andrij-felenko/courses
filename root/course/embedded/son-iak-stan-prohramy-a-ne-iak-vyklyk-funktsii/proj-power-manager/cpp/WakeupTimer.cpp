#include "WakeupTimer.hpp"
#include "stm32l4xx.h"

namespace emb::hal {
namespace {

using std::chrono::milliseconds;

// LSE 32768 Гц: PREDIV_A=31, PREDIV_S=1023 дають ck_spre 1 Гц і крок SSR ≈ 1 мс.
constexpr std::uint32_t kPredivA = 31;
constexpr std::uint32_t kPredivS = 1023;
// Джерело WUT — RTCCLK/16 = 2048 Гц (WUCKSEL = 000).
constexpr std::uint32_t kWutHz = 2048;
constexpr std::uint32_t kSpins = 100'000;
constexpr milliseconds  kHour{3'600'000};

// Розблокування регістрів RTC теж ресурс: замикаємо назад у деструкторі.
class WriteProtection {
public:
    WriteProtection() noexcept
    {
        RTC->WPR = 0xCAu;
        RTC->WPR = 0x53u;
    }
    ~WriteProtection() { RTC->WPR = 0xFFu; }

    WriteProtection(const WriteProtection&) = delete;
    WriteProtection& operator=(const WriteProtection&) = delete;
};

[[nodiscard]] bool spinUntilSet(volatile std::uint32_t& reg, std::uint32_t mask) noexcept
{
    for (std::uint32_t i = 0; i < kSpins; ++i) {
        if ((reg & mask) != 0u) {
            return true;
        }
    }
    return false;
}

[[nodiscard]] constexpr std::uint32_t fromBcd(std::uint32_t bcd) noexcept
{
    return ((bcd >> 4) & 0xFu) * 10u + (bcd & 0xFu);
}

} // namespace

milliseconds WakeupTimer::now() noexcept
{
    std::uint32_t ssr = 0, tr = 0, again = 0;
    do {
        ssr   = RTC->SSR;
        tr    = RTC->TR;
        again = RTC->SSR;
    } while (ssr != again); // захист від зміни секунди між читаннями

    const std::uint32_t sec = fromBcd((tr & (RTC_TR_ST | RTC_TR_SU)) >> RTC_TR_SU_Pos);
    const std::uint32_t min = fromBcd((tr & (RTC_TR_MNT | RTC_TR_MNU)) >> RTC_TR_MNU_Pos);
    const std::uint32_t frac = ((kPredivS - ssr) * 1000u) / (kPredivS + 1u); // SSR рахує вниз
    return milliseconds{(min * 60u + sec) * 1000u + frac};
}

void WakeupTimer::init() noexcept
{
    RCC->APB1ENR1 |= RCC_APB1ENR1_PWREN | RCC_APB1ENR1_RTCAPBEN;
    PWR->CR1 |= PWR_CR1_DBP; // домен резервного живлення відкрито на запис

    if ((RCC->BDCR & RCC_BDCR_RTCEN) == 0u) {
        RCC->BDCR |= RCC_BDCR_LSEON;
        if (!spinUntilSet(RCC->BDCR, RCC_BDCR_LSERDY)) {
            return; // без годинникового кварцу спимо тільки до події периферії
        }
        RCC->BDCR = (RCC->BDCR & ~RCC_BDCR_RTCSEL) | RCC_BDCR_RTCSEL_0;
        RCC->BDCR |= RCC_BDCR_RTCEN;

        WriteProtection unlocked;
        RTC->ISR = RTC_ISR_INIT;
        static_cast<void>(spinUntilSet(RTC->ISR, RTC_ISR_INITF));
        RTC->PRER = (kPredivA << RTC_PRER_PREDIV_A_Pos) | kPredivS;
        RTC->CR  |= RTC_CR_BYPSHAD; // читаємо лічильники напряму, без тіней
        RTC->ISR &= ~RTC_ISR_INIT;
    }

    EXTI->IMR1  |= EXTI_IMR1_IM20; // пробудження ядра йде лінією подій 20
    EXTI->RTSR1 |= EXTI_RTSR1_RT20;
    NVIC_SetPriority(RTC_WKUP_IRQn, 3);
    NVIC_EnableIRQ(RTC_WKUP_IRQn);
}

milliseconds WakeupTimer::arm(milliseconds timeout) noexcept
{
    if (timeout > MaxTimeout) {
        timeout = MaxTimeout;
    }
    std::uint32_t counts = static_cast<std::uint32_t>(timeout.count()) * kWutHz / 1000u;
    if (counts == 0u) {
        counts = 1u;
    }

    {
        WriteProtection unlocked;
        RTC->CR &= ~(RTC_CR_WUTE | RTC_CR_WUTIE);
        if (!spinUntilSet(RTC->ISR, RTC_ISR_WUTWF)) {
            return milliseconds{0}; // таймер не дався на перезапис
        }
        RTC->CR  &= ~RTC_CR_WUCKSEL;  // RTCCLK/16
        RTC->WUTR = counts - 1u;      // вистрелює на переході через нуль
        RTC->ISR &= ~RTC_ISR_WUTF;
        EXTI->PR1 = EXTI_PR1_PIF20;
        RTC->CR  |= RTC_CR_WUTE | RTC_CR_WUTIE;
    }

    s_expired = false;
    s_armedAt = now();
    return milliseconds{counts * 1000u / kWutHz};
}

void WakeupTimer::disarm() noexcept
{
    {
        WriteProtection unlocked;
        RTC->CR  &= ~(RTC_CR_WUTE | RTC_CR_WUTIE);
        RTC->ISR &= ~RTC_ISR_WUTF;
    }
    EXTI->PR1 = EXTI_PR1_PIF20;
}

milliseconds WakeupTimer::elapsedSinceArm() noexcept
{
    return (now() + kHour - s_armedAt) % kHour;
}

void rtcWakeupIsr() noexcept
{
    if ((RTC->ISR & RTC_ISR_WUTF) != 0u) {
        RTC->ISR &= ~RTC_ISR_WUTF; // прапорці RTC скидаються записом нуля
        WakeupTimer::s_expired = true;
    }
    EXTI->PR1 = EXTI_PR1_PIF20;
}

} // namespace emb::hal

extern "C" void RTC_WKUP_IRQHandler(void)
{
    emb::hal::rtcWakeupIsr();
}
