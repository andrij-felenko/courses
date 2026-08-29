/* ==========================================================================
 *  mag_cal_collector.c — просторове квотування хмари вимірів
 * ========================================================================== */

#include <string.h>

#include "mag_cal_collector.h"
#include "mag_cal_linalg.h"

#define MAG_CAL_PI      3.14159265f
#define MAG_CAL_HALF_PI 1.57079633f
#define MAG_CAL_TWO_PI  6.28318531f

/* Ширина пояса за кутом місця й ширина сектора за азимутом */
#define MAG_CAL_LAT_STEP (MAG_CAL_PI / (float)MAG_CAL_BINS_LAT)
#define MAG_CAL_LON_STEP (MAG_CAL_TWO_PI / (float)MAG_CAL_BINS_LON)

int mag_cal_bin_index(vec3_t raw) {
    const float norm = vec3_norm(raw);
    if (!(norm > 1e-3f)) {          /* нульовий модуль або NaN у вимірі */
        return -1;
    }

    float sin_elev = raw.z / norm;
    if (sin_elev >  1.0f) sin_elev =  1.0f;   /* округлення float може вивести */
    if (sin_elev < -1.0f) sin_elev = -1.0f;   /* аргумент asinf за межі [-1,1] */

    const float elev = asinf(sin_elev);           /* кут місця,  [-π/2, +π/2] */
    const float azim = atan2f(raw.y, raw.x);      /* азимут,     [-π,   +π]   */

    int lat_idx = (int)((elev + MAG_CAL_HALF_PI) / MAG_CAL_LAT_STEP);
    if (lat_idx < 0) lat_idx = 0;
    if (lat_idx >= MAG_CAL_BINS_LAT) lat_idx = MAG_CAL_BINS_LAT - 1;

    int lon_idx = (int)((azim + MAG_CAL_PI) / MAG_CAL_LON_STEP);
    if (lon_idx < 0) lon_idx = 0;
    if (lon_idx >= MAG_CAL_BINS_LON) lon_idx = MAG_CAL_BINS_LON - 1;

    return lat_idx * MAG_CAL_BINS_LON + lon_idx;
}

/* Одиничний вектор у центр комірки — зворотне перетворення до індексації */
static vec3_t mag_cal_bin_center(int bin) {
    const int lat_idx = bin / MAG_CAL_BINS_LON;
    const int lon_idx = bin % MAG_CAL_BINS_LON;

    const float elev = -MAG_CAL_HALF_PI + ((float)lat_idx + 0.5f) * MAG_CAL_LAT_STEP;
    const float azim = -MAG_CAL_PI      + ((float)lon_idx + 0.5f) * MAG_CAL_LON_STEP;

    const float ce = cosf(elev);
    return (vec3_t){ ce * cosf(azim), ce * sinf(azim), sinf(elev) };
}

void mag_cal_collector_init(mag_cal_collector_t *col, float earth_field_ut) {
    memset(col, 0, sizeof(*col));
    col->target_earth_field = (earth_field_ut > 10.0f && earth_field_ut < 100.0f)
                            ? earth_field_ut
                            : MAG_CAL_DEFAULT_EARTH_UT;
}

bool mag_cal_collector_push(mag_cal_collector_t *col, vec3_t raw,
                            vec3_t gyro_rad_s, uint32_t now_ms) {
    /* Різкий рух: цифровий фільтр АЦП магнітометра відстає від гіроскопа,
     * і вимір лягає не в те положення, у якому апарат був насправді. */
    if (vec3_norm(gyro_rad_s) > MAG_CAL_GYRO_LIMIT_RAD_S) {
        col->rejected_gyro++;
        return false;
    }

    const int bin = mag_cal_bin_index(raw);
    if (bin < 0) {
        col->rejected_bad++;
        return false;
    }

    const uint8_t count = col->sample_count[bin];
    if (count >= MAG_CAL_SAMPLES_PER_BIN) {
        col->rejected_full++;       /* квота комірки вибрана — це норма */
        return false;
    }

    col->samples[bin][count] = raw;
    col->sample_count[bin]   = (uint8_t)(count + 1u);
    col->total_points++;
    col->last_accept_ms = now_ms;
    return true;
}

uint16_t mag_cal_collector_filled_bins(const mag_cal_collector_t *col) {
    uint16_t filled = 0;
    for (int i = 0; i < MAG_CAL_TOTAL_BINS; i++) {
        if (col->sample_count[i] > 0u) filled++;
    }
    return filled;
}

float mag_cal_collector_coverage(const mag_cal_collector_t *col) {
    return ((float)mag_cal_collector_filled_bins(col) / (float)MAG_CAL_TOTAL_BINS) * 100.0f;
}

void mag_cal_collector_completion_mask(const mag_cal_collector_t *col,
                                       uint8_t mask[MAG_CAL_MASK_BYTES]) {
    memset(mask, 0, MAG_CAL_MASK_BYTES);
    for (int i = 0; i < MAG_CAL_TOTAL_BINS; i++) {
        /* Сектор вважаємо зробленим, лише коли вибрано всю квоту: наземна
         * станція має малювати зеленим те, що більше чіпати не треба. */
        if (col->sample_count[i] >= MAG_CAL_SAMPLES_PER_BIN) {
            mask[i / 8] |= (uint8_t)(1u << (i % 8));
        }
    }
}

vec3_t mag_cal_collector_hint_direction(const mag_cal_collector_t *col) {
    int     worst_bin   = -1;
    uint8_t worst_count = MAG_CAL_SAMPLES_PER_BIN;

    for (int i = 0; i < MAG_CAL_TOTAL_BINS; i++) {
        if (col->sample_count[i] < worst_count) {
            worst_count = col->sample_count[i];
            worst_bin   = i;
        }
    }

    if (worst_bin < 0) {
        return (vec3_t){ 0.0f, 0.0f, 1.0f };    /* хмара повна */
    }
    return mag_cal_bin_center(worst_bin);
}

void mag_cal_collector_snapshot(const mag_cal_collector_t *src,
                                mag_cal_collector_t *dst) {
    memcpy(dst, src, sizeof(*dst));
}
