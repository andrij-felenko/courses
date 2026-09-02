#ifndef APP_H
#define APP_H

#include "FreeRTOS.h"
#include "queue.h"
#include "task.h"

#include <stdbool.h>
#include <stdint.h>

/* Стеки задаються у СЛОВАХ: StackType_t на Cortex-M — 4 байти. */
#define STACK_WORDS_SENSOR     192u /*  768 Б */
#define STACK_WORDS_DISPLAY    384u /* 1536 Б */
#define STACK_WORDS_SUPERVISOR 128u /*  512 Б */

#define PRIO_SUPERVISOR (tskIDLE_PRIORITY + 3)
#define PRIO_SENSOR     (tskIDLE_PRIORITY + 2)
#define PRIO_DISPLAY    (tskIDLE_PRIORITY + 1)

#define SAMPLE_QUEUE_LEN 4u

typedef struct {
    uint32_t stamp_ms;
    int32_t  temp_c100;
    uint16_t seq;
    uint16_t errors;
} sample_t;

/* Кожна робоча задача звітує супервізорові своїм бітом. */
#define ALIVE_SENSOR  (1u << 0)
#define ALIVE_DISPLAY (1u << 1)
#define ALIVE_ALL     (ALIVE_SENSOR | ALIVE_DISPLAY)

extern QueueHandle_t g_samples;
extern TaskHandle_t  g_sensor_task;
extern TaskHandle_t  g_display_task;
extern TaskHandle_t  g_supervisor_task;

void board_init(void);
void watchdog_start(void);
void watchdog_kick(void);

void task_sensor(void *arg);
void task_display(void *arg);
void task_supervisor(void *arg);

#endif /* APP_H */
