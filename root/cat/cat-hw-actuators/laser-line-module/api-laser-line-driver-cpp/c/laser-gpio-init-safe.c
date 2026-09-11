#include <stdint.h>
#include <stdbool.h>

/* Базові структури регістрів GPIO та RCC для мікроконтролера ARM Cortex-M */
typedef struct {
    volatile uint32_t MODER;    /* Регістр вибору режиму роботи виводів */
    volatile uint32_t OTYPER;   /* Регістр типу вихідного каскаду (push-pull / open-drain) */
    volatile uint32_t OSPEEDR;  /* Регістр швидкодії вихідного каскаду */
    volatile uint32_t PUPDR;    /* Регістр конфігурації підтягувальних резисторів */
    volatile uint32_t IDR;      /* Регістр вхідних даних */
    volatile uint32_t ODR;      /* Регістр вихідних даних */
    volatile uint32_t BSRR;     /* Регістр атомарного встановлення та скидання бітів */
    volatile uint32_t LCKR;     /* Регістр блокування конфігурації */
    volatile uint32_t AFR[2];   /* Регістри вибору альтернативних функцій */
} gpio_registers_t;

typedef struct {
    gpio_registers_t *port;     /* Вказівник на базову адресу порту (наприклад, GPIOA) */
    uint32_t pin_index;         /* Номер піна (0 - 15) */
    bool active_level_high;     /* true для N-MOSFET (активна 1), false для P-MOSFET (активний 0) */
} laser_gpio_config_t;

/**
 * @brief Безглітчева ініціалізація лінії керування лазером.
 * @param cfg Конфігураційні параметри виводу.
 */
void laser_gpio_init_safe(const laser_gpio_config_t *cfg) {
    if (!cfg || !cfg->port || cfg->pin_index > 15) {
        return;
    }

    gpio_registers_t *gpio = cfg->port;
    uint32_t pin = cfg->pin_index;

    /* Крок 1: Встановлення внутрішньої підтяжки у відповідність до пасивного стану */
    gpio->PUPDR &= ~(0x3U << (pin * 2));
    if (cfg->active_level_high) {
        /* Для активного високого рівня пасивний стан — 0 В (стягування pull-down, біти 10b) */
        gpio->PUPDR |= (0x2U << (pin * 2));
    } else {
        /* Для активного низького рівня пасивний стан — VDD (підтяжка pull-up, біти 01b) */
        gpio->PUPDR |= (0x1U << (pin * 2));
    }

    /* Крок 2: Запис пасивного стану у вихідний регістр ДО активації режиму виводу.
       Використовуємо атомарний регістр BSRR:
       - біти 0..15 встановлюють логічну одиницю;
       - біти 16..31 скидають вивід у логічний нуль. */
    if (cfg->active_level_high) {
        /* Скидаємо вихідний тригер у нуль (запис у старшу половину BSRR) */
        gpio->BSRR = (1U << (pin + 16));
    } else {
        /* Встановлюємо вихідний тригер в одиницю (запис у молодшу половину BSRR) */
        gpio->BSRR = (1U << pin);
    }

    /* Крок 3: Вибір типу виходу — двотактний вихід (push-pull, біт = 0) */
    gpio->OTYPER &= ~(1U << pin);

    /* Крок 4: Встановлення високої швидкості перемикання (high speed, біти 10b) */
    gpio->OSPEEDR &= ~(0x3U << (pin * 2));
    gpio->OSPEEDR |= (0x2U << (pin * 2));

    /* Крок 5: Лише тепер перемикаємо режим піна з входу (00b) на вихід (01b).
       Оскільки вихідний буфер уже налаштований на пасивний рівень, лінія
       залишається в безпечному стані без імпульсних сплесків напруги. */
    gpio->MODER &= ~(0x3U << (pin * 2));
    gpio->MODER |= (0x1U << (pin * 2));
}

/**
 * @brief Безпечне керування живленням лазера на рівні GPIO.
 */
void laser_gpio_set_emission(const laser_gpio_config_t *cfg, bool enable) {
    if (!cfg || !cfg->port) {
        return;
    }

    bool set_pin_high = (cfg->active_level_high) ? enable : !enable;

    if (set_pin_high) {
        cfg->port->BSRR = (1U << cfg->pin_index);
    } else {
        cfg->port->BSRR = (1U << (cfg->pin_index + 16));
    }
}
