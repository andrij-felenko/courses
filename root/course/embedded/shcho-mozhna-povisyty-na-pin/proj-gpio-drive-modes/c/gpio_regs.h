/* gpio_regs.h — тонкий шар доступу до регістрів порту GPIO.
 *
 * Розкладка регістрів і адреси — STM32F4 (RM0090, розділ «General-purpose I/Os»).
 * Навмисно без вендорних бібліотек: у цій темі важливо бачити, який саме біт
 * якого регістра керує транзисторами вихідного каскаду. */
#ifndef GPIO_REGS_H
#define GPIO_REGS_H

#include <stdbool.h>
#include <stdint.h>

/* Блок регістрів одного порту. Зсуви — рівно ті, що в довіднику. */
typedef struct {
    volatile uint32_t moder;   /* 0x00 режим: вхід / вихід / альтернативна функція / аналог */
    volatile uint32_t otyper;  /* 0x04 тип каскаду: push-pull / open-drain */
    volatile uint32_t ospeedr; /* 0x08 струм керування затворами → швидкість фронту */
    volatile uint32_t pupdr;   /* 0x0C внутрішні підтяжки 30…50 кОм */
    volatile uint32_t idr;     /* 0x10 реальний рівень НА НІЖЦІ (після тригера Шмітта) */
    volatile uint32_t odr;     /* 0x14 засувка бажаного вихідного рівня */
    volatile uint32_t bsrr;    /* 0x18 атомарні set (біти 0..15) / reset (біти 16..31) */
    volatile uint32_t lckr;    /* 0x1C замок конфігурації */
    volatile uint32_t afr[2];  /* 0x20 вибір номера альтернативної функції */
} gpio_regs_t;

typedef enum {
    GPIO_PORT_A = 0,
    GPIO_PORT_B = 1,
    GPIO_PORT_C = 2,
    GPIO_PORT_D = 3,
    GPIO_PORT_E = 4,
    GPIO_PORT_COUNT
} gpio_port_t;

/* MODER, два біти на вивід */
typedef enum {
    GPIO_MODE_INPUT     = 0u, /* Hi-Z, обидва вихідні MOSFET закриті */
    GPIO_MODE_OUTPUT    = 1u,
    GPIO_MODE_ALTERNATE = 2u,
    GPIO_MODE_ANALOG    = 3u  /* вимикає вхідний тригер Шмітта — нема струмів витоку */
} gpio_mode_t;

/* OTYPER, один біт на вивід */
typedef enum {
    GPIO_TYPE_PUSH_PULL  = 0u, /* активні обидва транзистори */
    GPIO_TYPE_OPEN_DRAIN = 1u  /* верхній P-MOSFET вимкнено назавжди */
} gpio_otype_t;

/* OSPEEDR, два біти на вивід */
typedef enum {
    GPIO_SPEED_LOW       = 0u,
    GPIO_SPEED_MEDIUM    = 1u,
    GPIO_SPEED_HIGH      = 2u,
    GPIO_SPEED_VERY_HIGH = 3u
} gpio_speed_t;

/* PUPDR, два біти на вивід */
typedef enum {
    GPIO_PULL_NONE = 0u,
    GPIO_PULL_UP   = 1u,
    GPIO_PULL_DOWN = 2u
} gpio_pull_t;

typedef enum {
    GPIO_OK         =  0,
    GPIO_ERR_PORT   = -1, /* такого порту в цьому корпусі немає */
    GPIO_ERR_PIN    = -2, /* номер виводу поза 0…15 */
    GPIO_ERR_LOCKED = -3, /* конфігурацію замкнено через LCKR — запис не подіяв */
    GPIO_ERR_ARG    = -4
} gpio_status_t;

typedef struct {
    gpio_mode_t  mode;
    gpio_otype_t otype;
    gpio_speed_t speed;
    gpio_pull_t  pull;
} gpio_pin_cfg_t;

/* Вказівник на блок регістрів порту; NULL для невідомого порту. */
gpio_regs_t *gpio_port_regs(gpio_port_t port);

/* Тактування порту: без нього записи в регістри просто губляться. */
gpio_status_t gpio_clock_enable(gpio_port_t port);

/* Повна конфігурація одного виводу. Напрямок (MODER) пишеться ОСТАННІМ,
 * тому вивід стає виходом уже з готовими типом, швидкістю й підтяжкою. */
gpio_status_t gpio_pin_configure(gpio_port_t port, uint8_t pin, const gpio_pin_cfg_t *cfg);

/* Атомарний запис рівня через BSRR — без read-modify-write. */
gpio_status_t gpio_pin_write(gpio_port_t port, uint8_t pin, bool high);

/* Рівень, який реально стоїть на ніжці (IDR). */
gpio_status_t gpio_pin_read(gpio_port_t port, uint8_t pin, bool *level);

/* Рівень, який ми ЗАМОВИЛИ (ODR). Розбіжність з IDR = зовнішня проблема. */
gpio_status_t gpio_pin_latched(gpio_port_t port, uint8_t pin, bool *level);

/* Груба затримка на порожньому циклі. Це не таймер — лише щоб приклад
 * не потребував налаштованого SysTick. */
void gpio_spin(uint32_t loops);

const char *gpio_status_text(gpio_status_t st);

#endif /* GPIO_REGS_H */
