/*
 * Точки входу демонстрацій цього прикладу. Механізми (маска, вартові,
 * атомарні операції) лежать у cortexm.h, critical_section.h і atomic_arm.h;
 * тут — лише те, що показує стаття.
 */
#ifndef DEMOS_H
#define DEMOS_H

#include <stddef.h>
#include <stdint.h>

/* race_demo.c — незахищений спільний стан */
void process_data(void);

/* naive_trap.c — зламана вкладеність у драйвері */
int telemetry_send_packet(const uint8_t *payload, size_t len);

/* event_log.c — шаблон збереження PRIMASK */
int event_log_push(uint8_t code);
int event_log_pop(uint8_t *code);
uint32_t event_log_dropped(void);

/* rtos_section.c — селективне маскування через BASEPRI */
typedef struct {
    uint16_t id;
    int16_t arg;
} rtos_cmd_t;

int rtos_queue_push(uint16_t id, int16_t arg);
int rtos_queue_pop(rtos_cmd_t *out);

/* sensor_frame.c / sensor_frame_leak.c — витік маски й той самий код без нього */
#define SENSOR_OK 0
#define SENSOR_ERR_ARG (-1)
#define SENSOR_ERR_CRC (-2)

extern volatile uint16_t g_last_sample;

int sensor_frame_decode(const uint8_t *frame, size_t len, uint16_t *sample);
int sensor_frame_handle_leaky(const uint8_t *frame, size_t len);
int sensor_frame_handle(const uint8_t *frame, size_t len);

/* dualcore.c — друге ядро й апаратний спінлок */
int mailbox_publish(int32_t setpoint_ma, int32_t measured_ma);
int mailbox_read(int32_t *setpoint_ma);

#endif /* DEMOS_H */
