#include <cstdint>
#include <concepts>
#include <atomic>
#include "stm32f4xx.h"

namespace mcu::hw {

enum class pwm_mode : uint32_t {
    mode1 = 6U,
    mode2 = 7U
};

template <uint32_t BaseAddr>
class advanced_timer {
public:
    static constexpr auto* tim = reinterpret_cast<TIM_TypeDef*>(BaseAddr);

    struct config {
        uint32_t timer_clk_hz;
        uint32_t pwm_freq_hz;
        uint32_t duty_percent;
    };

    static void init(const config& cfg) noexcept {
        enable_bus_clock();

        // Налаштування пінів PA8 (CH1) та PA9 (CH2)
        RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
        GPIOA->MODER  = (GPIOA->MODER  & ~0x000F0000U) | 0x000A0000U;
        GPIOA->AFR[1] = (GPIOA->AFR[1] & ~0x000000FFU) | 0x00000011U;
        GPIOA->OSPEEDR |= 0x000F0000U;

        const uint32_t period_ticks = cfg.timer_clk_hz / cfg.pwm_freq_hz;
        const uint32_t duty_ticks   = (period_ticks * cfg.duty_percent) / 100U;

        tim->PSC = 0;
        tim->ARR = period_ticks - 1U;
        tim->CR1 = TIM_CR1_ARPE;

        // Канал 1: PWM
        tim->CCR1 = duty_ticks;
        tim->CCMR1 = (tim->CCMR1 & ~TIM_CCMR1_OC1M_Msk) |
                     (static_cast<uint32_t>(pwm_mode::mode1) << TIM_CCMR1_OC1M_Pos) |
                     TIM_CCMR1_OC1PE;
        tim->CCER |= TIM_CCER_CC1E;

        // Канал 2: Input Capture
        tim->CCMR1 = (tim->CCMR1 & ~TIM_CCMR1_CC2S_Msk) |
                     (1U << TIM_CCMR1_CC2S_Pos) |
                     (4U << TIM_CCMR1_IC2F_Pos);
        tim->CCER &= ~(TIM_CCER_CC2P | TIM_CCER_CC2NP);
        tim->CCER |= TIM_CCER_CC2E;

        // Дозвіл переривань
        tim->DIER |= TIM_DIER_CC2IE | TIM_DIER_UIE;
        NVIC_SetPriority(TIM1_CC_IRQn, 2);
        NVIC_EnableIRQ(TIM1_CC_IRQn);

        // Головний дозвіл виходів і пуск
        tim->BDTR |= TIM_BDTR_MOE;
        tim->EGR   = TIM_EGR_UG;
        tim->SR    = 0;
        tim->CR1  |= TIM_CR1_CEN;
    }

    static void set_duty_cycle(uint32_t duty_ticks) noexcept {
        tim->CCR1 = duty_ticks;
    }
};

using timer1 = advanced_timer<TIM1_BASE>;

} // namespace mcu::hw

// Дані захоплення, доступні системі
inline std::atomic<uint32_t> g_captured_period{0};
inline std::atomic<bool>     g_new_capture_ready{false};

extern "C" void TIM1_CC_IRQHandler() {
    if (TIM1->SR & TIM_SR_CC2IF) {
        TIM1->SR = ~TIM_SR_CC2IF;
        g_captured_period.store(TIM1->CCR2, std::memory_order_relaxed);
        g_new_capture_ready.store(true, std::memory_order_release);
    }
}
