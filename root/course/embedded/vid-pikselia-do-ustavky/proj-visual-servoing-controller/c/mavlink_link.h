#ifndef MAVLINK_LINK_H
#define MAVLINK_LINK_H

#include <stdbool.h>
#include <stdint.h>

#include "guidance.h"

/* Послідовний канал до автопілота: читаємо HIGHRES_IMU (гіроскопи),
 * пишемо SET_ATTITUDE_TARGET (кутові швидкості й тягу).
 * Заголовки MAVLink v2 підключає лише .c — щоб генерований мегазаголовок
 * не тягнувся в кожен модуль проєкту. */
typedef struct {
    int      fd;
    uint8_t  sysid;          /* наш ідентифікатор (супутній комп'ютер) */
    uint8_t  compid;
    uint8_t  target_sysid;
    uint8_t  target_compid;
    float    gyro_yaw;       /* zgyro, рад/с */
    float    gyro_pitch;     /* ygyro, рад/с */
    uint64_t gyro_time_us;   /* час останнього HIGHRES_IMU */
    /* Стан парсера MAVLink живе в бібліотеці, тут — лише лічильники. */
    unsigned imu_msgs;
    unsigned parse_errors;
} MavlinkLink;

int  mavlink_link_open(MavlinkLink *link, const char *device, int baud);
void mavlink_link_close(MavlinkLink *link);

/* Вичитує все, що прийшло, не блокуючись; повертає кількість оброблених
 * повідомлень HIGHRES_IMU або -1 на помилці читання. */
int  mavlink_link_poll(MavlinkLink *link);

/* Кутові швидкості з уставок плюс нормована вертикальна тяга [0..1]. */
int  mavlink_link_send_rates(MavlinkLink *link, const GuidanceSetpoints *sp,
                             float thrust, uint32_t boot_ms);

#endif /* MAVLINK_LINK_H */
