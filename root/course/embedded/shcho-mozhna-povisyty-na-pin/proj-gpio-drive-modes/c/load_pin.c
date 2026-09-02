#include "load_pin.h"

#include <stddef.h>

/* Який фізичний рівень на ніжці означає «навантаження ввімкнене». */
static bool level_for(const load_pin_t *lp, bool on)
{
    return lp->active_low ? !on : on;
}

gpio_status_t load_pin_init(const load_pin_t *lp)
{
    if (lp == NULL) {
        return GPIO_ERR_ARG;
    }

    gpio_status_t st = gpio_clock_enable(lp->port);
    if (st != GPIO_OK) {
        return st;
    }

    /* Крок, який найчастіше пропускають. Поки MODER тримає вивід входом,
     * запис у BSRR лише заряджає засувку ODR — на ніжку він не виходить.
     * Зате в мить перемикання на вихід каскад одразу видасть готовий
     * пасивний рівень, а не те, що лежало в ODR після скидання. */
    st = gpio_pin_write(lp->port, lp->pin, level_for(lp, false));
    if (st != GPIO_OK) {
        return st;
    }

    const gpio_pin_cfg_t cfg = {
        .mode  = GPIO_MODE_OUTPUT,
        .otype = GPIO_TYPE_PUSH_PULL,
        .speed = lp->speed,
        .pull  = GPIO_PULL_NONE /* каскад push-pull сам тримає обидва рівні */
    };

    st = gpio_pin_configure(lp->port, lp->pin, &cfg);
    if (st != GPIO_OK) {
        return st;
    }

    /* Ще раз, уже «по-справжньому»: між записом ODR і вмиканням каскаду
     * міг втрутитися чужий код, який чіпав той самий порт. */
    return gpio_pin_write(lp->port, lp->pin, level_for(lp, false));
}

gpio_status_t load_pin_set(const load_pin_t *lp, bool on)
{
    if (lp == NULL) {
        return GPIO_ERR_ARG;
    }
    return gpio_pin_write(lp->port, lp->pin, level_for(lp, on));
}

gpio_status_t load_pin_toggle(const load_pin_t *lp)
{
    bool on = false;
    const gpio_status_t st = load_pin_is_on(lp, &on);
    if (st != GPIO_OK) {
        return st;
    }
    return load_pin_set(lp, !on);
}

gpio_status_t load_pin_is_on(const load_pin_t *lp, bool *on)
{
    if (lp == NULL || on == NULL) {
        return GPIO_ERR_ARG;
    }

    bool level = false;
    const gpio_status_t st = gpio_pin_latched(lp->port, lp->pin, &level);
    if (st != GPIO_OK) {
        return st;
    }

    *on = lp->active_low ? !level : level;
    return GPIO_OK;
}

gpio_status_t load_pin_park(const load_pin_t *lp)
{
    if (lp == NULL) {
        return GPIO_ERR_ARG;
    }

    const gpio_status_t st = load_pin_set(lp, false);
    if (st != GPIO_OK) {
        return st;
    }

    /* Каскад лишається ввімкненим і активно тримає пасивний рівень.
     * Це не заміна зовнішньому стягувальному резистору на затворі —
     * під час скидання процесора вивід усе одно стане входом. */
    return GPIO_OK;
}
