/* gpio_strobe.c — конфігурація виводу стробування й обробник переривання. */
#include "gpio_strobe.h"

#define RCC_AHB1ENR   (*(volatile uint32_t *)0x40023830U)
#define RCC_GPIOBEN   (1UL << 1)
#define EXTI_PR       (*(volatile uint32_t *)0x40013C14U)
#define EXTI_LINE0    (1UL << 0)

profiler_stats_t g_isr_stats;

void gpio_strobe_init(void) {
    RCC_AHB1ENR |= RCC_GPIOBEN;
    /* Тактування вмикається не миттєво: перший запис у регістр порту одразу
       після RCC губиться. Читання-назад дає потрібну затримку в два такти. */
    (void)RCC_AHB1ENR;

    const uint32_t pin2 = STROBE_PIN * 2U;

    uint32_t moder = GPIO_REG(STROBE_PORT, GPIO_MODER);
    moder &= ~(3UL << pin2);
    moder |= (1UL << pin2); /* 01 — цифровий вихід */
    GPIO_REG(STROBE_PORT, GPIO_MODER) = moder;

    GPIO_REG(STROBE_PORT, GPIO_OTYPER) &= ~(1UL << STROBE_PIN); /* push-pull */

    /* 11 — Very High Speed. Найкрутіший фронт, який дає каскад: із щупом на
       10-15 пФ навіть він розтягує наростання на десяток наносекунд. */
    uint32_t ospeedr = GPIO_REG(STROBE_PORT, GPIO_OSPEEDR);
    ospeedr |= (3UL << pin2);
    GPIO_REG(STROBE_PORT, GPIO_OSPEEDR) = ospeedr;

    GPIO_REG(STROBE_PORT, GPIO_PUPDR) &= ~(3UL << pin2); /* без підтяжок */

    gpio_strobe_low();
    profiler_stats_reset(&g_isr_stats);
}

/* Обробник зовнішнього переривання: осцилограф бачить ширину імпульсу,
   а DWT рахує ту саму ділянку в тактах — два незалежні свідки одного числа. */
void EXTI0_IRQHandler(void) {
    gpio_strobe_high();
    const uint32_t start = dwt_get_cycles();

    /* Прапорець гасимо на початку: якщо лишити наприкінці, подія, що прийшла
       під час обробки, загубиться разом із ним. */
    EXTI_PR = EXTI_LINE0;

    process_urgent_sensor_event();

    profiler_stats_update(&g_isr_stats, dwt_elapsed_cycles(start));
    gpio_strobe_low();
}
