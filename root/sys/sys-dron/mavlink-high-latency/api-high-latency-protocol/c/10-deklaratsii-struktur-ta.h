#ifndef MAVLINK_HIGH_LATENCY2_H
#define MAVLINK_HIGH_LATENCY2_H

#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#define MAVLINK_MSG_ID_HIGH_LATENCY2 235
#define MAVLINK_MSG_ID_HIGH_LATENCY2_LEN 65
#define MAVLINK_MSG_ID_HIGH_LATENCY2_CRC 179

#pragma pack(push, 1)
typedef struct __mavlink_high_latency2_t {
    uint32_t timestamp;        // Час від старту (мс)
    int32_t  latitude;         // Широта (degE7)
    int32_t  longitude;        // Довгота (degE7)
    uint16_t custom_mode;      // Польотний режим
    int16_t  altitude;         // Висота AMSL (м)
    int16_t  target_altitude;  // Цільова висота (м)
    uint16_t target_distance;  // Відстань до цілі (декаметри, ×10 м)
    uint16_t wp_num;           // Номер точки маршруту
    uint16_t failure_flags;    // Маска відмов (HL_FAILURE_FLAG)
    int16_t  current_battery;  // Струм (0.1 А)
    uint8_t  type;             // MAV_TYPE
    uint8_t  autopilot;        // MAV_AUTOPILOT
    uint8_t  heading;          // Курс (deg / 2)
    uint8_t  target_heading;   // Цільовий курс (deg / 2)
    uint8_t  throttle;         // Газ (0..100%)
    uint8_t  airspeed;         // Приладова швидкість (м/с × 5)
    uint8_t  airspeed_sp;      // Задана швидкість (м/с × 5)
    uint8_t  groundspeed;      // Шляхова швидкість (м/с × 5)
    uint8_t  windspeed;        // Швидкість вітру (м/с × 5)
    uint8_t  wind_heading;     // Напрямок вітру (deg / 2)
    uint8_t  eph;              // Горизонтальна похибка GPS (0.1 м)
    uint8_t  epv;              // Вертикальна похибка GPS (0.1 м)
    int8_t   temperature_air;  // Температура повітря (°C)
    int8_t   climb_rate;       // Вертикальна швидкість (0.1 м/с)
    int8_t   battery;          // Залишок батареї (%)
    int8_t   custom0;          // Поле користувача 0
    int8_t   custom1;          // Поле користувача 1
    int8_t   custom2;          // Поле користувача 2
    int8_t   temperature;      // Температура автопілота (°C)
    uint8_t  failsafe;         // Прапорці захисту failsafe
} mavlink_high_latency2_t;
#pragma pack(pop)

static inline void mavlink_high_latency2_pack_fields(
    mavlink_high_latency2_t *msg,
    uint32_t time_boot_ms,
    double lat, double lon,
    float alt_amsl_m, float target_alt_m,
    float heading_deg, float target_heading_deg,
    float target_dist_m, uint16_t wp_idx,
    float airspeed_mps, float groundspeed_mps,
    float climb_rate_mps, int8_t battery_pct,
    float current_amps, uint16_t fail_flags
) {
    msg->timestamp = time_boot_ms;
    msg->latitude = (int32_t)round(lat * 1e7);
    msg->longitude = (int32_t)round(lon * 1e7);
    msg->altitude = (int16_t)round(alt_amsl_m);
    msg->target_altitude = (int16_t)round(target_alt_m);
    msg->heading = (uint8_t)(round(heading_deg / 2.0f)) % 180;
    msg->target_heading = (uint8_t)(round(target_heading_deg / 2.0f)) % 180;
    msg->target_distance = (uint16_t)fminf(roundf(target_dist_m / 10.0f), 65535.0f);
    msg->wp_num = wp_idx;
    msg->airspeed = (uint8_t)fminf(roundf(airspeed_mps * 5.0f), 255.0f);
    msg->groundspeed = (uint8_t)fminf(roundf(groundspeed_mps * 5.0f), 255.0f);
    msg->climb_rate = (int8_t)fminf(fmaxf(roundf(climb_rate_mps * 10.0f), -128.0f), 127.0f);
    msg->battery = battery_pct;
    msg->current_battery = (int16_t)round(current_amps * 10.0f);
    msg->failure_flags = fail_flags;
}

#endif // MAVLINK_HIGH_LATENCY2_H
