// hal/hal_gpio.h — контракт однієї цифрової ніжки. Потрібен службі живлення,
// щоб клацнути ключем MOSFET, нічого не знаючи про порт і номер виводу.
#ifndef HAL_GPIO_H
#define HAL_GPIO_H

#include <stdint.h>
#include <stdbool.h>

typedef enum {
    HAL_GPIO_LOW = 0,
    HAL_GPIO_HIGH = 1
} hal_gpio_level_t;

typedef enum {
    HAL_GPIO_OK = 0,
    HAL_GPIO_ERR_ARG,
    HAL_GPIO_ERR_HW
} hal_gpio_status_t;

typedef struct hal_gpio_pin_ops {
    hal_gpio_status_t (*write)(void* context, uint8_t pin, hal_gpio_level_t level);
    hal_gpio_status_t (*read)(void* context, uint8_t pin, hal_gpio_level_t* out_level);
} hal_gpio_pin_ops_t;

typedef struct hal_gpio_pin {
    const hal_gpio_pin_ops_t* ops;
    void* context;  // GPIO_TypeDef* на чипі, лічильник перемикань у заглушці
    uint8_t pin;    // Номер виводу всередині порту
} hal_gpio_pin_t;

static inline hal_gpio_status_t hal_gpio_write(const hal_gpio_pin_t* p, hal_gpio_level_t level)
{
    if (!p || !p->ops || !p->ops->write) return HAL_GPIO_ERR_ARG;
    return p->ops->write(p->context, p->pin, level);
}

static inline hal_gpio_status_t hal_gpio_read(const hal_gpio_pin_t* p, hal_gpio_level_t* out_level)
{
    if (!p || !p->ops || !p->ops->read || !out_level) return HAL_GPIO_ERR_ARG;
    return p->ops->read(p->context, p->pin, out_level);
}

#endif  // HAL_GPIO_H
