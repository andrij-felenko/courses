/* gpio_strobe.h — стробування виводу для цифрового осцилографа (STM32F4/F7).
 *
 * Запис у BSRR атомарний і коштує 1-2 такти шини AHB: біти 0..15 ставлять
 * рівень у одиницю, біти 16..31 — у нуль. Ні читання-модифікації-запису,
 * ні глушіння переривань, на відміну від ODR ^= PIN.
 */
#ifndef GPIO_STROBE_H
#define GPIO_STROBE_H

#include <stdint.h>

#include "dwt_profiler.h"

#define GPIOB_BASE     0x40020400UL
#define STROBE_PORT    GPIOB_BASE
#define STROBE_PIN     5U

/* Зсуви регістрів порту (RM0090, «General-purpose I/Os») */
#define GPIO_MODER     0x00U
#define GPIO_OTYPER    0x04U
#define GPIO_OSPEEDR   0x08U
#define GPIO_PUPDR     0x0CU
#define GPIO_BSRR      0x18U

#define GPIO_REG(port, off) (*(volatile uint32_t *)((uintptr_t)(port) + (off)))

/** Налаштовує вивід стробування: вихід, push-pull, максимальна швидкість фронту. */
void gpio_strobe_init(void);

/** Статистика тривалості обробника EXTI0 — заповнює сам обробник. */
extern profiler_stats_t g_isr_stats;

/** Корисна робота обробника; визначає застосунок (див. main.c). */
void process_urgent_sensor_event(void);

static inline void gpio_strobe_high(void) {
    GPIO_REG(STROBE_PORT, GPIO_BSRR) = (1UL << STROBE_PIN);
}

static inline void gpio_strobe_low(void) {
    GPIO_REG(STROBE_PORT, GPIO_BSRR) = (1UL << (STROBE_PIN + 16U));
}

#endif /* GPIO_STROBE_H */
