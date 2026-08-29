#include "safe_state.h"

#include "crash_log.h"
#include "mcu.h"

/* Розкладка керування силовою частиною на GPIOA:
 *   PA8  — TIM1_CH1, верхнє плече мостового драйвера (альтернативна функція)
 *   PA7  — TIM1_CH1N, нижнє плече
 *   PA9  — ENABLE драйвера моста, активний високий
 *   PA10 — реле відсікання силового живлення, активне високе */
#define PIN_DRIVER_ENABLE 9U
#define PIN_MAIN_RELAY    10U

/* volatile: обидві змінні читає й пише обробник винятку. */
static volatile bool s_power_enabled = false;
static volatile bool s_latched = false;

static void gpio_make_output_low(uint32_t pin)
{
    /* Спершу рівень, потім напрямок: інакше між перемиканням у вихід
     * і записом нуля вивід на кілька тактів віддає невизначений рівень,
     * і драйвер моста встигає клацнути. */
    GPIOA_BSRR = (1UL << (pin + 16U)); /* скидання в нуль */

    GPIOA_OTYPER &= ~(1UL << pin);      /* двотактний вихід */
    GPIOA_PUPDR &= ~(3UL << (pin * 2U));
    GPIOA_PUPDR |= (2UL << (pin * 2U)); /* підтяжка до землі */
    GPIOA_OSPEEDR |= (1UL << (pin * 2U));

    uint32_t moder = GPIOA_MODER;
    moder &= ~(3UL << (pin * 2U));
    moder |= (1UL << (pin * 2U)); /* режим «вихід» */
    GPIOA_MODER = moder;

    GPIOA_BSRR = (1UL << (pin + 16U));
}

static void power_stages_off(void)
{
    /* Головний дозвіл виходів таймера. Один запис у BDTR миттєво
     * переводить усі канали в неактивний стан — це швидше за будь-яку
     * роботу з окремими ніжками. */
    TIM1_BDTR &= ~TIM1_BDTR_MOE;
    TIM1_CCER &= ~(TIM1_CCER_CC1E | TIM1_CCER_CC1NE);
    TIM1_CCR1 = 0U;
    TIM1_CR1 &= ~TIM1_CR1_CEN;

    /* Далі — окремі лінії дозволу драйвера й силового реле. */
    GPIOA_BSRR = (1UL << (PIN_DRIVER_ENABLE + 16U));
    GPIOA_BSRR = (1UL << (PIN_MAIN_RELAY + 16U));
    mcu_dsb();

    s_power_enabled = false;
}

void safe_state_arm_outputs(void)
{
    RCC_AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    RCC_APB2ENR |= RCC_APB2ENR_TIM1EN;
    mcu_dsb();

    /* Таймер міг лишитися ввімкненим від попереднього запуску: теплий
     * рестарт скидає ядро, але не завжди зупиняє периферію на тому самому
     * такті. Гасимо виходи ще до налаштування ніжок. */
    power_stages_off();

    gpio_make_output_low(PIN_DRIVER_ENABLE);
    gpio_make_output_low(PIN_MAIN_RELAY);

    /* Прапорець аварії живе в тій самій RAM, що й усе інше, і після
     * теплого рестарту міг лишитися виставленим. Старт — це нова спроба,
     * рішення про блокування ухвалює main() за журналом, а не за сміттям
     * у неініціалізованій змінній. */
    s_latched = false;
    s_power_enabled = false;
}

bool safe_state_enable_power(void)
{
    if (s_latched) {
        /* Один раз зафіксувавшись в аварії, ми з неї не виходимо без
         * рестарту: інакше прошивка, яка «полікувалася» сама, поверне
         * рух приводу, причини аварії так і не з'ясувавши. */
        return false;
    }

    GPIOA_BSRR = (1UL << PIN_MAIN_RELAY);
    GPIOA_BSRR = (1UL << PIN_DRIVER_ENABLE);

    TIM1_CCER |= TIM1_CCER_CC1E | TIM1_CCER_CC1NE;
    TIM1_BDTR |= TIM1_BDTR_MOE;
    TIM1_CR1 |= TIM1_CR1_CEN;

    s_power_enabled = true;
    return true;
}

void safe_state_disable_power(void)
{
    power_stages_off();
}

void safe_state_enter(void)
{
    const bool was_latched = s_latched;
    s_latched = true;

    power_stages_off();

    /* Лічильник рахує ПОДІЇ, а не виклики: обробник збою може зайти сюди
     * двічі, і другий раз — це та сама аварія. */
    if (!was_latched) {
        crash_log_note_safe_state();
    }
}

bool safe_state_is_active(void)
{
    return !s_power_enabled;
}

bool safe_state_is_latched(void)
{
    return s_latched;
}
