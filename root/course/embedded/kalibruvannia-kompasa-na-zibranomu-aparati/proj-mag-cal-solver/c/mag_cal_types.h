/* ==========================================================================
 *  mag_cal_types.h — спільні типи, пороги й константи конвеєра калібрування
 *  магнітометра. Жодних викликів malloc: усі буфери статичні.
 * ========================================================================== */
#ifndef MAG_CAL_TYPES_H
#define MAG_CAL_TYPES_H

#include <stdbool.h>
#include <stdint.h>

/* --- Просторове розбиття сфери: 6 широтних поясів × 12 азимутних секторів --- */
#define MAG_CAL_BINS_LAT        6
#define MAG_CAL_BINS_LON        12
#define MAG_CAL_TOTAL_BINS      (MAG_CAL_BINS_LAT * MAG_CAL_BINS_LON)            /* 72 */
#define MAG_CAL_SAMPLES_PER_BIN 4
#define MAG_CAL_MAX_POINTS      (MAG_CAL_TOTAL_BINS * MAG_CAL_SAMPLES_PER_BIN)   /* 288 */

/* Байтів на бітову маску заповнених секторів у MAVLink (uint8_t[10] = 80 біт) */
#define MAG_CAL_MASK_BYTES      10

/* --- Пороги якості й керування конвеєром --- */
#define MAG_CAL_MIN_COVERAGE_PCT    60.0f    /* нижче — розв'язувач не запускаємо */
#define MAG_CAL_SOLVE_COVERAGE_PCT  80.0f    /* фоновий потік стартує розв'язувач */
#define MAG_CAL_MIN_POINTS          40
#define MAG_CAL_MAX_RMS_UT          3.0f     /* гейт нев'язки, мкТл */
#define MAG_CAL_MAX_CONDITION       2.5f     /* гейт зумовленості матриці W */
#define MAG_CAL_GYRO_LIMIT_RAD_S    1.745f   /* 100 °/с — відсів динамічних спотворень */
#define MAG_CAL_DEFAULT_EARTH_UT    45.0f
#define MAG_CAL_MAX_ITERATIONS      20
#define MAG_CAL_IDLE_TIMEOUT_MS     60000u   /* немає нових точок хвилину — скасування */

/* Розумні межі, за якими вміст Flash вважаємо сміттям навіть при збіжній CRC */
#define MAG_CAL_MAX_OFFSET_UT       1500.0f
#define MAG_CAL_MAX_GAIN            5.0f

typedef struct {
    float x, y, z;
} vec3_t;

typedef struct {
    float m[3][3];
} mat3_t;

/* Результат роботи розв'язувача — він же вміст запису у Flash */
typedef struct {
    vec3_t   offset;         /* Hard Iron, вектор V0 (мкТл) */
    mat3_t   soft_iron;      /* Soft Iron, симетрична матриця W (безрозмірна) */
    float    earth_field;    /* еталонний модуль поля Землі (мкТл) */
    float    rms_residual;   /* середньоквадратична нев'язка (мкТл) */
    float    coverage_pct;   /* відсоток заповнених секторів сфери на момент розв'язання */
    float    condition_num;  /* число зумовленості W = |λmax| / |λmin| */
    float    sphere_radius;  /* середній модуль скоригованого вектора (мкТл) */
    uint16_t points_used;    /* скільки точок пішло в підгонку */
    uint8_t  iterations;     /* прийнятих кроків Левенберга — Марквардта */
    uint8_t  compass_id;     /* номер компаса в системі (для MAVLink) */
    uint32_t crc32;          /* контрольна сума запису; 0 — ще не рахована */
    bool     is_valid;       /* пройдено обидва гейти якості */
} mag_cal_result_t;

/* Одиничне перетворення «сирий вектор → скоригований» без стану */
#define MAG_CAL_IDENTITY_RESULT                            \
    (mag_cal_result_t){                                    \
        .offset      = { 0.0f, 0.0f, 0.0f },               \
        .soft_iron   = {{ { 1.0f, 0.0f, 0.0f },            \
                          { 0.0f, 1.0f, 0.0f },            \
                          { 0.0f, 0.0f, 1.0f } }},         \
        .earth_field = MAG_CAL_DEFAULT_EARTH_UT,           \
        .is_valid    = false                               \
    }

#endif /* MAG_CAL_TYPES_H */
