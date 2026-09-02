#ifndef TELEMETRY_H
#define TELEMETRY_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

/* Телеметричні параметри, зчитані з борту безпосередньо перед армінгом.
   Це саме зліпок: одне значення на поле, зняте в момент запиту дозволу. */
typedef struct {
    uint8_t  gps_fix_type;      /* 3 = 3D Fix, 4 = DGPS, 5 = RTK Float, 6 = RTK Fixed */
    uint8_t  gps_satellites;    /* Кількість супутників у навігаційному рішенні */
    float    gps_hdop;          /* Horizontal Dilution of Precision */

    float    ekf_pos_innov;     /* Нормована похибка інновації позиції EKF */
    float    ekf_vel_innov;     /* Нормована похибка інновації швидкості EKF */
    float    ekf_yaw_innov;     /* Нормована похибка інновації курсу EKF */

    float    battery_voltage;   /* Загальна напруга силового акумулятора (В) */
    float    cell_delta_v;      /* Максимальний перекіс між осередками (В) */
    float    battery_temp_c;    /* Температура акумулятора (°C) */

    bool     geofence_enabled;  /* Чи активовано жорстку геозону в параметрах */
    uint16_t geofence_points;   /* Кількість вершин завантаженого полігону */
    uint8_t  geofence_action;   /* 0 = немає, 1 = RTL, 2 = Land, 3 = Terminate */

    int16_t  rc_rssi_dbm;       /* Рівень сигналу пульта на стоянці (дБм) */
    uint16_t rc_kill_channel;   /* Значення ШІМ аварійного каналу (мкс) */

    float    acc_vibe_floor;    /* Фонова амплітуда шуму акселерометра (м/с²) */
} VehicleTelemetryState;

/* Розбирає текстовий зліпок телеметрії з потоку `in`.

   Формат — по одному «ключ=значення» на рядок, імена ключів збігаються з
   іменами полів структури; «#» починає коментар до кінця рядка; порожні
   рядки ігноруються. Такий дамп віддає GCS перед стартом:

       # знято 2026-08-30 09:41:12, борт 04
       gps_fix_type   = 3
       gps_satellites = 14
       geofence_enabled = true

   Зліпок мусить бути ПОВНИМ: бракує поля — це відмова читати думки автопілота,
   а не привід підставити нуль. Повертає 0 при успіху й -1 при помилці,
   поклавши пояснення (з номером рядка) у буфер `err` розміру `err_len`. */
int telemetry_parse(FILE *in, VehicleTelemetryState *out, char *err, size_t err_len);

#endif /* TELEMETRY_H */
