/* include/board.h — усе, що застосунок знає про плату: набір готових шин,
 * виводів і приймач телеметрії. Кожен порт (stm32f4, host_mock) реалізує
 * board_init() по-своєму, а main.c лишається байт-у-байт однаковим. */
#ifndef BOARD_H
#define BOARD_H

#include "hal/hal_gpio.h"
#include "hal/hal_i2c.h"
#include "include/telemetry_record.h"

struct event_queue;

typedef struct {
    const hal_i2c_bus_t *env_bus;    /* шина давача мікроклімату */
    const hal_i2c_bus_t *accel_bus;  /* шина акселерометра (може збігатися) */
    hal_gpio_pin_t       led_status;
    telemetry_sink_fn    report_record;
    void                *report_ctx;
} board_t;

/* Піднімає тактування, шини, таймер тіку. Повертає опис плати або NULL,
 * якщо залізо не піднялося — тоді запускати застосунок нема сенсу. */
const board_t *board_init(void);

/* Прив'язує чергу подій до порту: саме звідси її беруть обробники переривань
 * і генератор системного тіку. Виклик до board_init() безпечний. */
void board_bind_event_queue(struct event_queue *queue);

/* Черга, прив'язана board_bind_event_queue(), або NULL. Викликається з
 * контексту переривання, тому не робить нічого, крім читання покажчика. */
struct event_queue *board_event_queue(void);

#endif /* BOARD_H */
