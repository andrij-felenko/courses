/* load_pin.h — дискретний вихід під навантаження: реле, світлодіод, затвор
 * зовнішнього силового ключа.
 *
 * Дві речі, заради яких цей шар узагалі існує:
 *   1) пасивний рівень виставляється РАНІШЕ за напрямок виводу, тож навантаження
 *      не клацає на мілісекунду під час ініціалізації;
 *   2) швидкість фронту за замовчуванням найнижча — крутий фронт на такій лінії
 *      дає лише сплеск di/dt і просадку живлення, а користі не дає жодної. */
#ifndef LOAD_PIN_H
#define LOAD_PIN_H

#include "gpio_regs.h"

typedef struct {
    gpio_port_t  port;
    uint8_t      pin;
    bool         active_low; /* навантаження вмикається нулем (типова релейна плата) */
    gpio_speed_t speed;      /* GPIO_SPEED_LOW, якщо немає вагомої причини інакше */
} load_pin_t;

/* Тактування → пасивний рівень → конфігурація виходу. Саме в такому порядку. */
gpio_status_t load_pin_init(const load_pin_t *lp);

gpio_status_t load_pin_set(const load_pin_t *lp, bool on);
gpio_status_t load_pin_toggle(const load_pin_t *lp);

/* Чи ввімкнене навантаження за станом засувки ODR. */
gpio_status_t load_pin_is_on(const load_pin_t *lp, bool *on);

/* Вимкнути й лишити вивід АКТИВНО утримувати пасивний рівень.
 * Свідомо не переводимо в Hi-Z: підвішений затвор зовнішнього MOSFET —
 * саме той випадок, коли навантаження вмикається само від наводки. */
gpio_status_t load_pin_park(const load_pin_t *lp);

#endif /* LOAD_PIN_H */
