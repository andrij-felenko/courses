#include "opendrain.h"

#include <stddef.h>

/* Скільки чекати фронту, якщо в дескрипторі нічого не задано. Час підняття
 * задає RC: підтяжка помножена на ємність шини, тож для 4.7 кОм і 200 пФ
 * це одиниці мікросекунд. */
#define OD_DEFAULT_RISE_LOOPS 200u

static uint32_t rise_loops(const od_line_t *line)
{
    return line->rise_loops != 0u ? line->rise_loops : OD_DEFAULT_RISE_LOOPS;
}

gpio_status_t od_line_init(const od_line_t *line)
{
    if (line == NULL) {
        return GPIO_ERR_ARG;
    }

    gpio_status_t st = gpio_clock_enable(line->port);
    if (st != GPIO_OK) {
        return st;
    }

    /* Одиниця в ODR = верхній ключ і так вимкнено, нижній закритий → Hi-Z.
     * Ставимо її до конфігурації, щоб не смикнути шину під час ініціалізації. */
    st = gpio_pin_write(line->port, line->pin, true);
    if (st != GPIO_OK) {
        return st;
    }

    const gpio_pin_cfg_t cfg = {
        .mode  = GPIO_MODE_OUTPUT,
        .otype = GPIO_TYPE_OPEN_DRAIN,
        .speed = line->speed,
        /* Внутрішні 30…50 кОм для шини завеликі: вони не витягнуть фронт,
         * зате замаскують відсутній зовнішній резистор під час перевірки. */
        .pull  = GPIO_PULL_NONE
    };

    return gpio_pin_configure(line->port, line->pin, &cfg);
}

gpio_status_t od_line_drive_low(const od_line_t *line)
{
    if (line == NULL) {
        return GPIO_ERR_ARG;
    }
    return gpio_pin_write(line->port, line->pin, false);
}

gpio_status_t od_line_release(const od_line_t *line)
{
    if (line == NULL) {
        return GPIO_ERR_ARG;
    }
    return gpio_pin_write(line->port, line->pin, true);
}

gpio_status_t od_line_level(const od_line_t *line, bool *high)
{
    if (line == NULL || high == NULL) {
        return GPIO_ERR_ARG;
    }
    return gpio_pin_read(line->port, line->pin, high);
}

od_wiring_t od_line_check(const od_line_t *line)
{
    if (line == NULL) {
        return OD_WIRING_FAULT;
    }

    bool level = false;

    /* 1. Відпускаємо: підняти лінію мусить зовнішня підтяжка. */
    if (od_line_release(line) != GPIO_OK) {
        return OD_WIRING_FAULT;
    }
    gpio_spin(rise_loops(line));
    if (od_line_level(line, &level) != GPIO_OK) {
        return OD_WIRING_FAULT;
    }
    if (!level) {
        return OD_WIRING_STUCK_LOW;
    }

    /* 2. Притискаємо: наш нижній ключ мусить перемогти підтяжку. */
    if (od_line_drive_low(line) != GPIO_OK) {
        return OD_WIRING_FAULT;
    }
    gpio_spin(rise_loops(line));
    if (od_line_level(line, &level) != GPIO_OK) {
        return OD_WIRING_FAULT;
    }

    /* Хоч би що показала перевірка, шину лишаємо відпущеною. */
    if (od_line_release(line) != GPIO_OK) {
        return OD_WIRING_FAULT;
    }
    gpio_spin(rise_loops(line));

    return level ? OD_WIRING_STUCK_HIGH : OD_WIRING_OK;
}

const char *od_wiring_text(od_wiring_t w)
{
    switch (w) {
    case OD_WIRING_OK:         return "проводка шини в нормі";
    case OD_WIRING_STUCK_LOW:  return "лінія не піднімається: немає підтяжки або КЗ на землю";
    case OD_WIRING_STUCK_HIGH: return "лінія не притискається: обрив або перемичка на живлення";
    case OD_WIRING_FAULT:      return "помилка доступу до GPIO";
    default:                   return "невідомий результат перевірки";
    }
}
