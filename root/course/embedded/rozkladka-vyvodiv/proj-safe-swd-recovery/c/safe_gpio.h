#ifndef SAFE_GPIO_H
#define SAFE_GPIO_H

/*
 * Обгортка над портами вводу-виводу, яка знає про системні виводи.
 * Головна властивість: PA13 (SWDIO) і PA14 (SWCLK) не можна перепризначити
 * випадково — тільки свідомо, з ключем, і з обов'язковим поверненням назад.
 */

#include <stdbool.h>
#include <stdint.h>

typedef enum {
    GPIO_PORT_A = 0,
    GPIO_PORT_B,
    GPIO_PORT_C,
    GPIO_PORT_D,
    GPIO_PORT_E,
    GPIO_PORT_COUNT
} gpio_port_t;

typedef enum {
    GPIO_MODE_INPUT  = 0U,
    GPIO_MODE_OUTPUT = 1U,
    GPIO_MODE_ALT    = 2U,
    GPIO_MODE_ANALOG = 3U
} gpio_mode_t;

typedef enum {
    GPIO_PULL_NONE = 0U,
    GPIO_PULL_UP   = 1U,
    GPIO_PULL_DOWN = 2U
} gpio_pull_t;

typedef enum {
    GPIO_SPEED_LOW    = 0U,
    GPIO_SPEED_MEDIUM = 1U,
    GPIO_SPEED_HIGH   = 2U,
    GPIO_SPEED_VERY_HIGH = 3U
} gpio_speed_t;

typedef enum {
    GPIO_PUSH_PULL  = 0U,
    GPIO_OPEN_DRAIN = 1U
} gpio_otype_t;

typedef struct {
    gpio_port_t  port;
    uint8_t      pin;        /* 0..15 */
    gpio_mode_t  mode;
    gpio_pull_t  pull;
    gpio_speed_t speed;
    gpio_otype_t otype;
    uint8_t      alt;        /* AF0..AF15, значуще лише для GPIO_MODE_ALT */
} gpio_cfg_t;

typedef enum {
    GPIO_OK = 0,
    GPIO_ERR_PORT,        /* немає такого порту                    */
    GPIO_ERR_PIN,         /* номер виводу поза 0..15               */
    GPIO_ERR_ALT,         /* номер альтернативної функції поза 0..15 */
    GPIO_ERR_SWD_LOCKED   /* спроба зайняти PA13/PA14 без ключа    */
} gpio_status_t;

/* Ключ свідомого перепризначення виводів SWD. */
#define GPIO_SWD_UNLOCK_KEY  0x5EAF00DUL

/* Чи є цей вивід лінією SWD (PA13 або PA14). */
bool gpio_is_swd_pin(gpio_port_t port, uint8_t pin);

/*
 * Налаштовує вивід. Виводи SWD відхиляє, доки не викликано
 * gpio_unlock_swd_pins() з правильним ключем.
 */
gpio_status_t gpio_configure(const gpio_cfg_t *cfg);

/* Свідомо дозволяє чіпати PA13/PA14. Хибний ключ нічого не змінює. */
bool gpio_unlock_swd_pins(uint32_t key);

/* Повертає PA13/PA14 у режим AF0 (шина налагодження) і знову замикає їх. */
void gpio_restore_swd_pins(void);

/* Скільки разів обгортка врятувала шину налагодження від захоплення. */
uint32_t gpio_rejected_count(void);

void gpio_write(gpio_port_t port, uint8_t pin, bool level);
bool gpio_read(gpio_port_t port, uint8_t pin);
void gpio_toggle(gpio_port_t port, uint8_t pin);

const char *gpio_status_str(gpio_status_t status);

#endif /* SAFE_GPIO_H */
