/* ==========================================================================
 *  mag_cal_collector.h — накопичувач вимірів із просторовим квотуванням.
 *  Сфера ділиться на 72 комірки, у кожну беремо рівно 4 виміри: інакше
 *  хмара перекошується в бік положення, у якому апарат просто полежав.
 * ========================================================================== */
#ifndef MAG_CAL_COLLECTOR_H
#define MAG_CAL_COLLECTOR_H

#include "mag_cal_types.h"

typedef struct {
    vec3_t   samples[MAG_CAL_TOTAL_BINS][MAG_CAL_SAMPLES_PER_BIN];
    uint8_t  sample_count[MAG_CAL_TOTAL_BINS];
    uint16_t total_points;
    float    target_earth_field;

    /* Лічильники відсіву — їх видно в журналі й вони пояснюють оператору,
     * чому хмара не росте, хоч апарат крутять. */
    uint32_t rejected_gyro;      /* різкий рух: |ω| > 100 °/с */
    uint32_t rejected_full;      /* комірка вже має свою квоту */
    uint32_t rejected_bad;       /* нульовий модуль або NaN у вимірі */
    uint32_t last_accept_ms;     /* мітка часу останньої прийнятої точки */
} mag_cal_collector_t;

void mag_cal_collector_init(mag_cal_collector_t *col, float earth_field_ut);

/* Швидкий шлях сенсорного потоку: без ділення на нуль, без блокувань.
 * true — вимір ліг у комірку. gyro_rad_s — модуль кутової швидкості. */
bool mag_cal_collector_push(mag_cal_collector_t *col, vec3_t raw,
                            vec3_t gyro_rad_s, uint32_t now_ms);

float    mag_cal_collector_coverage(const mag_cal_collector_t *col);
uint16_t mag_cal_collector_filled_bins(const mag_cal_collector_t *col);

/* Бітова маска заповнених секторів у форматі поля completion_mask MAVLink:
 * біт n маски = сектор n, молодший біт у молодшому байті. */
void mag_cal_collector_completion_mask(const mag_cal_collector_t *col,
                                       uint8_t mask[MAG_CAL_MASK_BYTES]);

/* Одиничний вектор у центр найбіднішої комірки — саме туди наземна станція
 * просить оператора довернути апарат. Хмара повна → {0,0,1}. */
vec3_t mag_cal_collector_hint_direction(const mag_cal_collector_t *col);

/* Копія накопичувача під м'ютексом: розв'язувач далі працює з нею 2–4 мс,
 * не тримаючи сенсорний потік. */
void mag_cal_collector_snapshot(const mag_cal_collector_t *src,
                                mag_cal_collector_t *dst);

/* Індекс комірки для вектора; -1 — вимір непридатний */
int mag_cal_bin_index(vec3_t raw);

#endif /* MAG_CAL_COLLECTOR_H */
