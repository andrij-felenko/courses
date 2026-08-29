#ifndef GEO_H
#define GEO_H

#include <stdint.h>

/* Точка так, як її несе MAVLink: градуси, помножені на 1e7 (цілі),
   і висота в метрах над точкою зльоту. Цілі координати навмисні —
   у float повна широта (до 9e8) втратила б метри на молодших розрядах. */
typedef struct {
    int32_t lat_e7;
    int32_t lon_e7;
    float   alt_m;
} geo_point_t;

/* Зміщення в локальній дотичній площині: схід і північ, метри. */
typedef struct {
    float east_m;
    float north_m;
} geo_offset_t;

/* Проєкція на пласку дотичну площину. Придатна на плечах до кількох
   кілометрів — саме такі відрізки й бувають між вейпойнтами. */
geo_offset_t geo_offset(geo_point_t from, geo_point_t to);

/* КВАДРАТ відстані в метрах². Кореня немає навмисно: усі порівняння
   в диспетчері робляться з квадратом порога. */
float geo_dist_sq_m2(geo_point_t a, geo_point_t b);

/* Курс на ціль, [0, 360). */
float geo_bearing_deg(geo_point_t from, geo_point_t to);

/* Кутова похибка → [-180, +180). Без цього перехід 359° → 1°
   дає хибний розворот на 358° у зворотний бік. */
float geo_wrap_deg(float angle_deg);

/* Курс → [0, 360). */
float geo_norm_heading_deg(float angle_deg);

/* Точка, зміщена на схід/північ від базової. Симулятор рухає апарат
   саме так: тримає зміщення у float і щоразу перераховує від бази,
   тому похибка не накопичується. */
geo_point_t geo_shift(geo_point_t base, float east_m, float north_m);

#endif /* GEO_H */
