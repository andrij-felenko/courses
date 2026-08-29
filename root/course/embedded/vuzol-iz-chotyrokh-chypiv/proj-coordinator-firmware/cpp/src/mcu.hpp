#pragma once

// Тонкий шар над регістрами STM32L476: вивід, тактування, час, сторожовий
// таймер, вхід у Stop 2. Усе inline і без віртуальних функцій — компілятор
// зводить це до тих самих записів у регістри, що й у С.

#include <cstdint>

#include "stm32l4xx.h"

namespace mcu {

// ── Вивід ────────────────────────────────────────────────────────────────
class Pin {
public:
    enum class Mode : std::uint32_t { Input = 0, Output = 1, Alternate = 2, Analog = 3 };
    enum class Pull : std::uint32_t { None = 0, Up = 1, Down = 2 };

    constexpr Pin(GPIO_TypeDef* port, std::uint32_t number) noexcept
        : port_{port}, n_{number} {}

    void mode(Mode m) const noexcept {
        port_->MODER = (port_->MODER & ~(0b11u << (n_ * 2))) |
                       (static_cast<std::uint32_t>(m) << (n_ * 2));
    }
    void pull(Pull p) const noexcept {
        port_->PUPDR = (port_->PUPDR & ~(0b11u << (n_ * 2))) |
                       (static_cast<std::uint32_t>(p) << (n_ * 2));
    }
    void alternate(std::uint32_t af) const noexcept {
        const std::uint32_t idx = n_ >> 3;
        const std::uint32_t sh  = (n_ & 7u) * 4u;
        port_->AFR[idx] = (port_->AFR[idx] & ~(0xFu << sh)) | (af << sh);
        mode(Mode::Alternate);
    }
    void openDrain(bool on) const noexcept {
        if (on) { port_->OTYPER |= (1u << n_); } else { port_->OTYPER &= ~(1u << n_); }
    }
    void fast() const noexcept { port_->OSPEEDR |= (0b11u << (n_ * 2)); }

    void write(bool high) const noexcept {
        port_->BSRR = high ? (1u << n_) : (1u << (n_ + 16u));
    }
    [[nodiscard]] bool read() const noexcept { return (port_->IDR & (1u << n_)) != 0u; }

private:
    GPIO_TypeDef* port_;
    std::uint32_t n_;
};

// ── Заборона переривань на час критичної ділянки ─────────────────────────
// Той самий прийом, що й lock_guard: вихід із області — хоч через return,
// хоч через виняток — повертає PRIMASK як було.
class ScopedIrqLock {
public:
    ScopedIrqLock() noexcept : saved_{__get_PRIMASK()} { __disable_irq(); }
    ~ScopedIrqLock() { __set_PRIMASK(saved_); }

    ScopedIrqLock(const ScopedIrqLock&) = delete;
    ScopedIrqLock& operator=(const ScopedIrqLock&) = delete;

private:
    std::uint32_t saved_;
};

// ── Тактування ───────────────────────────────────────────────────────────
namespace clock {

inline constexpr std::uint32_t kSysClkHz = 80'000'000u;
inline constexpr std::uint32_t kHsi16Hz  = 16'000'000u;

// Викликається на старті й після кожного виходу зі Stop 2: ядро прокидається
// на MSI, а нам потрібні 80 МГц від HSE через PLL.
inline void configure() noexcept {
    RCC->APB1ENR1 |= RCC_APB1ENR1_PWREN;
    FLASH->ACR = FLASH_ACR_PRFTEN | FLASH_ACR_ICEN | FLASH_ACR_DCEN |
                 FLASH_ACR_LATENCY_4WS;

    RCC->CR |= RCC_CR_HSEON;
    for (std::uint32_t guard = 0; (RCC->CR & RCC_CR_HSERDY) == 0u; ++guard) {
        if (guard > 1'000'000u) {
            return;   // кварц не завівся — лишаємось на MSI, але живі
        }
    }

    RCC->CR &= ~RCC_CR_PLLON;
    while ((RCC->CR & RCC_CR_PLLRDY) != 0u) { }

    // HSE 8 МГц → /1 → ×20 = 160 МГц у VCO → /2 = 80 МГц.
    RCC->PLLCFGR = (3u << RCC_PLLCFGR_PLLSRC_Pos) |
                   (0u << RCC_PLLCFGR_PLLM_Pos) |
                   (20u << RCC_PLLCFGR_PLLN_Pos) |
                   (0u << RCC_PLLCFGR_PLLR_Pos) |
                   RCC_PLLCFGR_PLLREN;
    RCC->CR |= RCC_CR_PLLON;
    while ((RCC->CR & RCC_CR_PLLRDY) == 0u) { }

    RCC->CFGR = (RCC->CFGR & ~RCC_CFGR_SW) | RCC_CFGR_SW_PLL;
    while ((RCC->CFGR & RCC_CFGR_SWS) != RCC_CFGR_SWS_PLL) { }
}

}  // namespace clock

// ── Час ──────────────────────────────────────────────────────────────────
namespace time {

inline volatile std::uint32_t g_ms{0};
inline std::uint32_t g_cyclesPerUs{80};

inline void init(std::uint32_t hclkHz) noexcept {
    g_cyclesPerUs = hclkHz / 1'000'000u;

    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CYCCNT = 0;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;

    SysTick->LOAD = (hclkHz / 1000u) - 1u;
    SysTick->VAL  = 0;
    SysTick->CTRL = SysTick_CTRL_CLKSOURCE_Msk | SysTick_CTRL_TICKINT_Msk |
                    SysTick_CTRL_ENABLE_Msk;
}

[[nodiscard]] inline std::uint32_t millis() noexcept { return g_ms; }

// Мікросекундні паузи беремо з лічильника тактів ядра: під час ручного
// тактування шини I2C таймера під рукою може й не бути.
inline void delayUs(std::uint32_t us) noexcept {
    const std::uint32_t start = DWT->CYCCNT;
    const std::uint32_t ticks = us * g_cyclesPerUs;
    while ((DWT->CYCCNT - start) < ticks) { }
}

// Різниця беззнакова, тож переповнення лічильника нічого не ламає.
[[nodiscard]] inline bool elapsed(std::uint32_t since, std::uint32_t ms) noexcept {
    return (millis() - since) > ms;
}

}  // namespace time

// ── Сторожовий таймер ────────────────────────────────────────────────────
class Watchdog {
public:
    // LSI ≈ 32 кГц, дільник 32 → тик 1 мс, 2000 тиків → 2.0 с. IWDG живиться
    // від LSI й тікає навіть у Stop 2, тому зависання уві сні теж карається.
    static void start() noexcept {
        RCC->CSR |= RCC_CSR_LSION;
        while ((RCC->CSR & RCC_CSR_LSIRDY) == 0u) { }

        IWDG->KR  = 0x5555u;
        IWDG->PR  = 3u;
        IWDG->RLR = 2000u - 1u;
        while (IWDG->SR != 0u) { }
        IWDG->KR = 0xAAAAu;
        IWDG->KR = 0xCCCCu;   // запущений сторож не вимикається до скидання
    }

    static void kick() noexcept { IWDG->KR = 0xAAAAu; }
};

// ── Сон ──────────────────────────────────────────────────────────────────
// У Stop 2 гасне все високочастотне: HSE, PLL, SysTick. Лишаються LSI зі
// сторожем, приймач USART на HSI16 і входи EXTI.
inline void enterStop2() noexcept {
    PWR->CR1 = (PWR->CR1 & ~PWR_CR1_LPMS) | PWR_CR1_LPMS_STOP2;
    SCB->SCR |= SCB_SCR_SLEEPDEEP_Msk;

    __DSB();
    __WFI();

    SCB->SCR &= ~SCB_SCR_SLEEPDEEP_Msk;
    clock::configure();
}

}  // namespace mcu
