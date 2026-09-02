/* opendrain.h — лінія з відкритим стоком: I2C, «wired-AND», сигнал у бік
 * пристрою з іншою напругою живлення.
 *
 * Вивід має рівно два стани: притиснути до землі — або відпустити. Високий
 * рівень формує зовнішній резистор підтяжки, і саме тому тут з'являється
 * перевірка проводки: без підтяжки код працює «нормально», а лінія просто
 * ніколи не піднімається. */
#ifndef OPENDRAIN_H
#define OPENDRAIN_H

#include "gpio_regs.h"

typedef struct {
    gpio_port_t  port;
    uint8_t      pin;
    gpio_speed_t speed;       /* для I2C 100/400 кГц вистачає MEDIUM */
    uint32_t     rise_loops;  /* скільки чекати підняття лінії підтяжкою */
} od_line_t;

typedef enum {
    OD_WIRING_OK = 0,
    OD_WIRING_STUCK_LOW,  /* відпустили, а лінія лишилась у нулі: немає підтяжки,
                           * КЗ на землю або ведений тримає шину */
    OD_WIRING_STUCK_HIGH, /* притиснули, а лінія лишилась в одиниці: обрив між
                           * ніжкою й шиною або жорстка перемичка на живлення */
    OD_WIRING_FAULT       /* помилка доступу до самого GPIO */
} od_wiring_t;

/* Конфігурація відкритого стоку. Вивід одразу лишається відпущеним. */
gpio_status_t od_line_init(const od_line_t *line);

gpio_status_t od_line_drive_low(const od_line_t *line);
gpio_status_t od_line_release(const od_line_t *line);

/* Реальний рівень на шині (IDR), а не наш намір. */
gpio_status_t od_line_level(const od_line_t *line, bool *high);

/* Відпустити → лінія має піднятись; притиснути → має впасти.
 * Викликати ДО першого обміну: інакше збій проводки виглядатиме як
 * загадковий NACK від веденого. */
od_wiring_t od_line_check(const od_line_t *line);

const char *od_wiring_text(od_wiring_t w);

#endif /* OPENDRAIN_H */
