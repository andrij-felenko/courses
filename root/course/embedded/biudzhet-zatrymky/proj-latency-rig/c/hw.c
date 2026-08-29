#include "hw.h"

#include "stm32f4xx.h"

#define LED_PIN 5u // PA5 -> затвор MOSFET
#define PD_PIN  0u // PA0 <- вихід компаратора
#define TX_PIN  2u // PA2 -> USART2_TX

void hw_init(void)
{
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    RCC->APB1ENR |= RCC_APB1ENR_TIM2EN | RCC_APB1ENR_USART2EN;
    RCC->APB2ENR |= RCC_APB2ENR_SYSCFGEN;

    // PA5: вихід, двотактний, максимальна швидкість фронту. Час наростання
    // на затворі прямо входить у похибку моменту старту, тож не економимо.
    GPIOA->MODER   &= ~(3u << (LED_PIN * 2));
    GPIOA->MODER   |=  (1u << (LED_PIN * 2));
    GPIOA->OTYPER  &= ~(1u << LED_PIN);
    GPIOA->OSPEEDR |=  (3u << (LED_PIN * 2));
    GPIOA->BSRR     =  (1u << (LED_PIN + 16)); // світлодіод погашено

    // PA0: вхід без підтяжок — компаратор жене повноцінний двотактний рівень.
    GPIOA->MODER &= ~(3u << (PD_PIN * 2));
    GPIOA->PUPDR &= ~(3u << (PD_PIN * 2));

    // PA2: альтернативна функція AF7 = USART2_TX.
    GPIOA->MODER  &= ~(3u << (TX_PIN * 2));
    GPIOA->MODER  |=  (2u << (TX_PIN * 2));
    GPIOA->AFR[0] &= ~(0xFu << (TX_PIN * 4));
    GPIOA->AFR[0] |=  (7u   << (TX_PIN * 4));

    // PCLK1 = 16 МГц (HSI без PLL), 115200 бод -> USARTDIV = 8.6875 -> 0x8B.
    USART2->BRR = 0x8Bu;
    USART2->CR1 = USART_CR1_TE | USART_CR1_UE;

    // TIM2: 16 МГц / (15 + 1) = 1 МГц, вільний хід на всю 32-бітну шкалу.
    TIM2->PSC = 15u;
    TIM2->ARR = 0xFFFFFFFFu;
    TIM2->EGR = TIM_EGR_UG; // перезавантажити подільник негайно
    TIM2->CR1 = TIM_CR1_CEN;

    // EXTI0 <- порт A, фронт наростання. Пріоритет найвищий: час входу в
    // обробник цілком лягає у виміряну затримку, тож нічого не має його
    // випереджати.
    SYSCFG->EXTICR[0] &= ~SYSCFG_EXTICR1_EXTI0; // 0000 = PA
    EXTI->RTSR |=  EXTI_RTSR_TR0;
    EXTI->FTSR &= ~EXTI_FTSR_TR0;
    EXTI->IMR  &= ~EXTI_IMR_MR0; // вікно чутливості поки закрите
    EXTI->PR    =  EXTI_PR_PR0;
    NVIC_SetPriority(EXTI0_IRQn, 0);
    NVIC_EnableIRQ(EXTI0_IRQn);
}

uint32_t hw_now_us(void)
{
    return TIM2->CNT;
}

void hw_led(bool on)
{
    GPIOA->BSRR = on ? (1u << LED_PIN) : (1u << (LED_PIN + 16));
}

void hw_optical_window(bool open)
{
    if (open) {
        EXTI->PR   = EXTI_PR_PR0; // скинути все, що набігло за паузу
        NVIC_ClearPendingIRQ(EXTI0_IRQn);
        EXTI->IMR |= EXTI_IMR_MR0;
    } else {
        EXTI->IMR &= ~EXTI_IMR_MR0;
    }
    __DSB(); // маска має набути чинності до повернення з функції
}

void hw_delay_us(uint32_t us)
{
    const uint32_t start = hw_now_us();
    while ((hw_now_us() - start) < us) {
        __NOP();
    }
}

static void uart_put(char c)
{
    while ((USART2->SR & USART_SR_TXE) == 0u) {
        // чекаємо, поки звільниться регістр передавача
    }
    USART2->DR = (uint8_t)c;
}

void hw_print(const char *text)
{
    for (const char *p = text; *p != '\0'; ++p) {
        if (*p == '\n') {
            uart_put('\r');
        }
        uart_put(*p);
    }
}

// Друк без ділення на 10 у циклі по всій ширині: збираємо цифри у стек.
static void print_padded(uint32_t value, uint8_t min_digits)
{
    char digits[10];
    uint8_t n = 0;

    do {
        digits[n++] = (char)('0' + (value % 10u));
        value /= 10u;
    } while (value != 0u && n < sizeof(digits));

    while (n < min_digits) {
        digits[n++] = '0';
    }
    while (n > 0u) {
        uart_put(digits[--n]);
    }
}

void hw_print_u32(uint32_t value)
{
    print_padded(value, 1);
}

void hw_print_ms(uint32_t microseconds)
{
    print_padded(microseconds / 1000u, 1);
    uart_put('.');
    print_padded(microseconds % 1000u, 3);
}

void hw_print_nl(void)
{
    hw_print("\n");
}
