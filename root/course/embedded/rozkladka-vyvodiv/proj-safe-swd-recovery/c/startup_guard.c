#include "startup_guard.h"

#include "stm32f4xx.h"

/* PA0 — кнопка відновлення: затиснута під час подачі живлення = «не стартуй». */
#define RECOVERY_PIN  0U

/*
 * Груба калібровка порожнього циклу для HSI 16 МГц: тіло займає близько
 * десятка тактів. Точність тут не потрібна — вікно має бути «не менше двох
 * секунд», а не «рівно дві». Систем-таймер на цьому етапі свідомо не чіпаємо:
 * дерево тактування ще не налаштоване й може виявитися збійним.
 */
#define LOOPS_PER_MS  1500U

static void spin_ms(uint32_t ms)
{
    while (ms-- > 0U) {
        for (volatile uint32_t i = 0; i < LOOPS_PER_MS; ++i) {
            __NOP();
        }
    }
}

void startup_guard_keep_debug_in_low_power(void)
{
    DBGMCU->CR |= DBGMCU_CR_DBG_SLEEP
                | DBGMCU_CR_DBG_STOP
                | DBGMCU_CR_DBG_STANDBY;
    __DSB();
}

bool startup_guard_debugger_attached(void)
{
    return (CoreDebug->DHCSR & CoreDebug_DHCSR_C_DEBUGEN_Msk) != 0U;
}

static void recovery_input_init(void)
{
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    (void)RCC->AHB1ENR;   /* зворотне читання: чекаємо, поки тактування дійде до порту */

    GPIOA->MODER &= ~(0x3U << (RECOVERY_PIN * 2U));   /* вхід */
    GPIOA->PUPDR &= ~(0x3U << (RECOVERY_PIN * 2U));
    GPIOA->PUPDR |=  (0x2U << (RECOVERY_PIN * 2U));   /* підтяжка вниз */

    spin_ms(1U);   /* ємність лінії має встигнути розрядитися до першого читання */
}

static bool recovery_pressed(void)
{
    return (GPIOA->IDR & (1U << RECOVERY_PIN)) != 0U;
}

/* Кнопку вважаємо натиснутою лише після GUARD_DEBOUNCE_MS підряд однакових вибірок. */
static bool recovery_held(uint32_t ms_budget)
{
    uint32_t stable = 0U;

    for (uint32_t ms = 0U; ms < ms_budget; ++ms) {
        if (recovery_pressed()) {
            if (++stable >= GUARD_DEBOUNCE_MS) {
                return true;
            }
        } else {
            stable = 0U;
        }
        spin_ms(1U);
    }
    return false;
}

guard_result_t startup_guard_run(void)
{
    startup_guard_keep_debug_in_low_power();
    recovery_input_init();

    /* Спершу — короткий опит кнопки: аварійний вихід має спрацьовувати завжди. */
    if (recovery_held(GUARD_DEBOUNCE_MS * 2U)) {
        return GUARD_HELD_BY_OPERATOR;
    }

    /*
     * Якщо налагоджувач уже перехопив ядро (наприклад, через connect under
     * reset), чекати нема на кого — вікно своє відпрацювало.
     */
    if (startup_guard_debugger_attached()) {
        return GUARD_PROCEED;
    }

    if (recovery_held(GUARD_WINDOW_MS)) {
        return GUARD_HELD_BY_OPERATOR;
    }
    return GUARD_PROCEED;
}

void startup_guard_park(void)
{
    /*
     * Переривання глушимо навмисно: єдиний таймер, що лишився увімкненим від
     * попереднього запуску, здатен приспати ядро просто з обробника.
     */
    __disable_irq();

    for (;;) {
        __NOP();
    }
}
