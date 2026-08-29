/* hal/hal_gpio.h — абстракція окремого виводу.
 * Драйвер світлодіода не знає ні порту GPIOB, ні номера ніжки: він тримає
 * hal_gpio_pin_t, який плата заповнила за схемою. Перенесення лінії CS
 * з PA4 на PB12 стає правкою одного рядка в порті, а не полюванням на
 * магічні макроси в десятках файлів. */
#ifndef HAL_GPIO_H
#define HAL_GPIO_H

#include <stdbool.h>
#include <stdint.h>

typedef enum {
    HAL_GPIO_MODE_INPUT = 0,
    HAL_GPIO_MODE_INPUT_PULLUP,
    HAL_GPIO_MODE_OUTPUT_PP,   /* двотактний вихід */
    HAL_GPIO_MODE_OUTPUT_OD    /* відкритий стік */
} hal_gpio_mode_t;

typedef struct {
    void (*configure)(void *ctx, uint8_t pin, hal_gpio_mode_t mode);
    void (*set)(void *ctx, uint8_t pin, bool level);
    bool (*get)(void *ctx, uint8_t pin);
} hal_gpio_ops_t;

/* Опис конкретного виводу конкретної плати. Прапорець active_low знімає
 * з драйвера знання про те, що світлодіод підключений катодом до ніжки. */
typedef struct {
    const hal_gpio_ops_t *ops;
    void                 *ctx;
    uint8_t               pin;
    bool                  active_low;
} hal_gpio_pin_t;

static inline bool hal_gpio_pin_is_valid(const hal_gpio_pin_t *p)
{
    return p != 0 && p->ops != 0 && p->ops->set != 0;
}

static inline void hal_gpio_configure(const hal_gpio_pin_t *p, hal_gpio_mode_t mode)
{
    if (p != 0 && p->ops != 0 && p->ops->configure != 0) {
        p->ops->configure(p->ctx, p->pin, mode);
    }
}

/* on == true означає «активний стан», а не «висока напруга». */
static inline void hal_gpio_write(const hal_gpio_pin_t *p, bool on)
{
    if (hal_gpio_pin_is_valid(p)) {
        p->ops->set(p->ctx, p->pin, p->active_low ? !on : on);
    }
}

static inline bool hal_gpio_read(const hal_gpio_pin_t *p)
{
    if (p == 0 || p->ops == 0 || p->ops->get == 0) {
        return false;
    }
    const bool raw = p->ops->get(p->ctx, p->pin);
    return p->active_low ? !raw : raw;
}

#endif /* HAL_GPIO_H */
