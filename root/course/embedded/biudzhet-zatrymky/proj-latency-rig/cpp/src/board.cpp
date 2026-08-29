#include "board.hpp"

extern "C" {
#include "stm32f4xx.h"
}

namespace board {
namespace {

constexpr std::uint32_t kLedPin = 5; // PA5
constexpr std::uint32_t kPdPin  = 0; // PA0
constexpr std::uint32_t kTxPin  = 2; // PA2

void led(bool on) noexcept
{
    // Запис у BSRR атомарний і триває один такт шини — read-modify-write над
    // ODR тут неприпустимий: обробник переривання гасить світлодіод посеред
    // головного циклу.
    GPIOA->BSRR = on ? (1u << kLedPin) : (1u << (kLedPin + 16));
}

void uart_put(char c) noexcept
{
    while ((USART2->SR & USART_SR_TXE) == 0u) {
    }
    USART2->DR = static_cast<std::uint8_t>(c);
}

void print_padded(std::uint32_t value, unsigned min_digits) noexcept
{
    char digits[10];
    unsigned n = 0;

    do {
        digits[n++] = static_cast<char>('0' + (value % 10u));
        value /= 10u;
    } while (value != 0u && n < sizeof(digits));

    while (n < min_digits) {
        digits[n++] = '0';
    }
    while (n > 0u) {
        uart_put(digits[--n]);
    }
}

} // namespace

void init() noexcept
{
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    RCC->APB1ENR |= RCC_APB1ENR_TIM2EN | RCC_APB1ENR_USART2EN;
    RCC->APB2ENR |= RCC_APB2ENR_SYSCFGEN;

    // PA5: вихід, двотактний, максимальна швидкість фронту — час наростання
    // на затворі прямо входить у похибку моменту старту.
    GPIOA->MODER   &= ~(3u << (kLedPin * 2));
    GPIOA->MODER   |=  (1u << (kLedPin * 2));
    GPIOA->OTYPER  &= ~(1u << kLedPin);
    GPIOA->OSPEEDR |=  (3u << (kLedPin * 2));
    led(false);

    // PA0: вхід без підтяжок, компаратор жене двотактний рівень.
    GPIOA->MODER &= ~(3u << (kPdPin * 2));
    GPIOA->PUPDR &= ~(3u << (kPdPin * 2));

    // PA2: AF7 = USART2_TX; PCLK1 = 16 МГц, 115200 бод -> BRR = 0x8B.
    GPIOA->MODER  &= ~(3u << (kTxPin * 2));
    GPIOA->MODER  |=  (2u << (kTxPin * 2));
    GPIOA->AFR[0] &= ~(0xFu << (kTxPin * 4));
    GPIOA->AFR[0] |=  (7u   << (kTxPin * 4));
    USART2->BRR = 0x8Bu;
    USART2->CR1 = USART_CR1_TE | USART_CR1_UE;

    // TIM2: 16 МГц / 16 = 1 МГц, вільний хід на всю 32-бітну шкалу.
    TIM2->PSC = 15u;
    TIM2->ARR = 0xFFFFFFFFu;
    TIM2->EGR = TIM_EGR_UG;
    TIM2->CR1 = TIM_CR1_CEN;

    // EXTI0 <- порт A, фронт наростання, найвищий пріоритет: час входу в
    // обробник цілком лягає у виміряну затримку.
    SYSCFG->EXTICR[0] &= ~SYSCFG_EXTICR1_EXTI0;
    EXTI->RTSR |=  EXTI_RTSR_TR0;
    EXTI->FTSR &= ~EXTI_FTSR_TR0;
    EXTI->IMR  &= ~EXTI_IMR_MR0;
    EXTI->PR    =  EXTI_PR_PR0;
    NVIC_SetPriority(EXTI0_IRQn, 0);
    NVIC_EnableIRQ(EXTI0_IRQn);
}

Microseconds now() noexcept
{
    return Microseconds{TIM2->CNT};
}

void wait(Microseconds duration) noexcept
{
    const auto start = now();
    while ((now() - start) < duration) {
        __NOP();
    }
}

LedFlash::LedFlash() noexcept
{
    led(true);
}

LedFlash::~LedFlash() noexcept
{
    led(false);
}

OpticalWindow::OpticalWindow() noexcept
{
    EXTI->PR = EXTI_PR_PR0; // скинути все, що набігло за паузу
    NVIC_ClearPendingIRQ(EXTI0_IRQn);
    EXTI->IMR |= EXTI_IMR_MR0;
    __DSB();
}

void OpticalWindow::close() noexcept
{
    if (open_) {
        EXTI->IMR &= ~EXTI_IMR_MR0;
        __DSB();
        open_ = false;
    }
}

OpticalWindow::~OpticalWindow() noexcept
{
    close();
}

void clear_optical_flag() noexcept
{
    EXTI->PR = EXTI_PR_PR0;
}

void print(std::string_view text) noexcept
{
    for (char c : text) {
        if (c == '\n') {
            uart_put('\r');
        }
        uart_put(c);
    }
}

void print(std::uint32_t value) noexcept
{
    print_padded(value, 1);
}

void print(Microseconds value) noexcept
{
    const std::uint32_t us = value.count();
    print_padded(us / 1000u, 1);
    uart_put('.');
    print_padded(us % 1000u, 3);
}

void halt() noexcept
{
    led(false);
    for (;;) {
        __WFI();
    }
}

} // namespace board
