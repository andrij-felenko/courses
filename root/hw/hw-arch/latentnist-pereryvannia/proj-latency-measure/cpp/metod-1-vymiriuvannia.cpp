#include <cstdint>
#include <span>
#include <concepts>

namespace mcu {

/* Типобезпечні структури апаратних регістрів */
struct GpioPort {
    volatile uint32_t MODER;
    volatile uint32_t OTYPER;
    volatile uint32_t OSPEEDR;
    volatile uint32_t PUPDR;
    volatile uint32_t IDR;
    volatile uint32_t ODR;
    volatile uint32_t BSRR;
    volatile uint32_t LCKR;
    volatile uint32_t AF[2];
};

struct ExtiController {
    volatile uint32_t IMR;
    volatile uint32_t EMR;
    volatile uint32_t RTSR;
    volatile uint32_t FTSR;
    volatile uint32_t SWIER;
    volatile uint32_t PR;
};

struct RccController {
    volatile uint32_t CR;
    volatile uint32_t PLLCFGR;
    volatile uint32_t CFGR;
    volatile uint32_t CIR;
    volatile uint32_t AHB1RSTR;
    volatile uint32_t AHB2RSTR;
    volatile uint32_t AHB3RSTR;
    uint32_t reserved0;
    volatile uint32_t APB1RSTR;
    volatile uint32_t APB2RSTR;
    uint32_t reserved1[2];
    volatile uint32_t AHB1ENR;
    volatile uint32_t AHB2ENR;
    volatile uint32_t AHB3ENR;
    uint32_t reserved2;
    volatile uint32_t APB1ENR;
    volatile uint32_t APB2ENR;
};

/* Апаратні адреси периферії STM32F4 */
inline auto& rcc   = *reinterpret_cast<RccController*>(0x40023800U);
inline auto& gpioa = *reinterpret_cast<GpioPort*>(0x40020000U);
inline auto& exti  = *reinterpret_cast<ExtiController*>(0x40013C00U);
inline auto& nvic_iser0 = *reinterpret_cast<volatile uint32_t*>(0xE000E100U);

/* RAII-контролер імпульсу вимірювання */
class LatencyBenchmark {
public:
    static void init() noexcept {
        /* Увімкнення тактування шин AHB1 (GPIOA) та APB2 (SYSCFG) */
        rcc.AHB1ENR |= (1U << 0);
        rcc.APB2ENR |= (1U << 14);

        /* Налаштування PA0 як входу */
        gpioa.MODER &= ~(3U << 0);

        /* Налаштування PA1 як швидкісного виходу */
        gpioa.MODER &= ~(3U << 2);
        gpioa.MODER |= (1U << 2);
        gpioa.OSPEEDR |= (3U << 2);

        /* Початковий низький рівень на PA1 */
        gpioa.BSRR = (1U << (1 + 16));

        /* Налаштування маски переривань EXTI */
        exti.IMR |= (1U << 0);
        exti.RTSR |= (1U << 0);

        /* Увімкнення переривання в NVIC */
        nvic_iser0 = (1U << 6);
    }

    [[gnu::always_inline]] static inline void trigger_high() noexcept {
        gpioa.BSRR = (1U << 1);
    }

    [[gnu::always_inline]] static inline void trigger_low() noexcept {
        gpioa.BSRR = (1U << (1 + 16));
    }

    [[gnu::always_inline]] static inline void clear_exti() noexcept {
        exti.PR = (1U << 0);
    }
};

} // namespace mcu

/* C++ обробник переривання */
extern "C" void EXTI0_IRQHandler() {
    /* Миттєвий строб без накладних витрат виклику функцій */
    mcu::LatencyBenchmark::trigger_high();
    mcu::LatencyBenchmark::clear_exti();
    mcu::LatencyBenchmark::trigger_low();
}
