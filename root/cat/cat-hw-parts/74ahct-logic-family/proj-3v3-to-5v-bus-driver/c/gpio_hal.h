#ifndef GPIO_HAL_H
#define GPIO_HAL_H

#include <stdint.h>
#include <stdbool.h>

/* Умовні адреси регістрів мікроконтролера для демонстрації */
#define GPIO_PORT_BASE   0x40020000UL
#define GPIO_MODER       (*(volatile uint32_t *)(GPIO_PORT_BASE + 0x00))
#define GPIO_ODR         (*(volatile uint32_t *)(GPIO_PORT_BASE + 0x14))
#define GPIO_BSRR        (*(volatile uint32_t *)(GPIO_PORT_BASE + 0x18))

/* Піни */
#define PIN_OE           (1U << 2)  /* PA2 - Output Enable для 74AHCT (Active Low) */
#define PIN_SIGNAL       (1U << 3)  /* PA3 - Лінія даних для генерації імпульсів */

static inline void gpio_hal_init(void) {
    /* Налаштування пінів на вихід: очищення та встановлення бітів конфігурації */
    GPIO_MODER &= ~((3U << (2 * 2)) | (3U << (2 * 3)));
    GPIO_MODER |=  ((1U << (2 * 2)) | (1U << (2 * 3)));

    /* 
     * Безпечний стан під час завантаження: 
     * OE встановлюємо у високий рівень (1), щоб буфер 74AHCT був у високоімпедансному стані (Z),
     * захищаючи шину від неконфігурованих переходів.
     */
    GPIO_BSRR = PIN_OE;
}

static inline void gpio_set_oe(bool enable) {
    if (enable) {
        /* Активний рівень OE для 74AHCT — низький (0) */
        GPIO_BSRR = (PIN_OE << 16);
    } else {
        /* Неактивний рівень OE — високий (1), виходи у Z-стані */
        GPIO_BSRR = PIN_OE;
    }
}

static inline void gpio_pulse_signal(void) {
    /* Генерація короткого імпульсу на лінії даних */
    GPIO_BSRR = PIN_SIGNAL;
    GPIO_BSRR = (PIN_SIGNAL << 16);
}

#endif /* GPIO_HAL_H */
