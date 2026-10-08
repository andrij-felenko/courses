/**
 * @file mcu_power_exti.c
 * @brief Реалізація периферійного HAL для керування живленням та перериваннями МК.
 *
 * Налаштовує вхідний пін GPIO з підтяжкою до землі (Pull-Down), конфігурує тригер
 * EXTI за зростаючим фронтом (Rising Edge), реалізує апаратний обробник ISR та
 * низькорівневу інструкцію переведення ядра у глибокий сон (WFI).
 */

#include "mcu_power_exti.h"
#include <stdio.h>

static void (*exti_pir_callback)(void) = NULL;
static bool s_pir_pin_physical_state = false;
static bool s_mosfet_pin_physical_state = false;
static uint32_t s_system_tick_ms = 1000U;
static mcu_power_mode_t s_current_power_mode = MCU_POWER_MODE_RUN;

bool mcu_gpio_init_pir_input(void)
{
    /* Конфігурація піну PA0: режим Input, внутрішня підтяжка Pull-Down (0V),
       щоб запобігти хибним спрацьовуванням при висячому стані або ініціалізації давача */
    s_pir_pin_physical_state = false;
    return true;
}

bool mcu_gpio_init_mosfet_output(void)
{
    /* Конфігурація піну PA1: режим Output Push-Pull, початковий рівень LOW (0V).
       Це гарантує, що N-канальний MOSFET закритий при подачі живлення */
    s_mosfet_pin_physical_state = false;
    return true;
}

bool mcu_exti_init_pir_interrupt(void (*isr_callback)(void))
{
    if (isr_callback == NULL) {
        return false;
    }

    exti_pir_callback = isr_callback;

    /* Вмикаємо системне тактування EXTI модуля та конфігуруємо
       EXTI Line 0 на генерацію переривання за зростаючим фронтом (Rising Edge Trigger).
       Задаємо пріоритет переривання в NVIC. */
    return true;
}

bool mcu_gpio_read_pir_pin(void)
{
    return s_pir_pin_physical_state;
}

void mcu_gpio_write_mosfet_pin(bool level)
{
    s_mosfet_pin_physical_state = level;
}

void mcu_power_clear_exti_flag(void)
{
    /* Симуляція скидання біта у регістрі EXTI_PR (Pending Register) */
}

void mcu_power_enter_deep_sleep(void)
{
    s_current_power_mode = MCU_POWER_MODE_DEEP_SLEEP;

    /*
     * Апаратний алгоритм переходу у Deep Sleep / STOP Mode (Cortex-M):
     * 1. Встановлення біта SLEEPDEEP у регістрі System Control Register (SCB->SCR |= SCB_SCR_SLEEPDEEP_Msk).
     * 2. Вибір регулятора живлення в режимі низького споживання (PWR_CR_LPDS).
     * 3. Виконання інструкції __WFI() (Wait For Interrupt).
     * 4. Процесор зупиняє виконання інструкцій, струм споживання падає до ~2-5 мкА.
     */
    printf("   [HAL Power] МК переходить у DEEP SLEEP (струм споживання ~3.5 мкА). Очікування EXTI...\n");
}

uint32_t mcu_get_tick_ms(void)
{
    return s_system_tick_ms;
}

void mcu_delay_ms(uint32_t ms)
{
    s_system_tick_ms += ms;
}

void mcu_simulate_pir_hardware_event(bool high_level)
{
    bool previous_state = s_pir_pin_physical_state;
    s_pir_pin_physical_state = high_level;

    /* Виявлення зростаючого фронту (0 -> 1): тригерить апаратне переривання EXTI */
    if (!previous_state && high_level) {
        printf("\n>>> [Апаратна подія] HC-SR505 згенерував RISING EDGE (3.3V на PA0) <<<\n");
        mcu_power_clear_exti_flag();
        s_current_power_mode = MCU_POWER_MODE_RUN;

        /* Апаратне переривання прокидає МК із глибокого сну та викликає ISR */
        if (exti_pir_callback != NULL) {
            exti_pir_callback();
        }
    }
}
