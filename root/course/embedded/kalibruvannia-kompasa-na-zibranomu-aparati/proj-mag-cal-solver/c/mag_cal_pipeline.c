/* ==========================================================================
 *  mag_cal_pipeline.c — Вбудований конвеєр калібрування магнітометра (C99)
 * ========================================================================== */

#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define MAG_CAL_BINS_LAT        6
#define MAG_CAL_BINS_LON        12
#define MAG_CAL_TOTAL_BINS      (MAG_CAL_BINS_LAT * MAG_CAL_BINS_LON) /* 72 */
#define MAG_CAL_SAMPLES_PER_BIN 4
#define MAG_CAL_MAX_POINTS      (MAG_CAL_TOTAL_BINS * MAG_CAL_SAMPLES_PER_BIN) /* 288 */

#define MAG_CAL_MAX_ITERATIONS  20
#define MAG_CAL_DEFAULT_EARTH_B 45.0f /* мкТл */

typedef struct {
    float x, y, z;
} vec3_t;

typedef struct {
    float m[3][3];
} mat3_t;

typedef struct {
    vec3_t offset;          /* Hard Iron вектор V_0 (мкТл) */
    mat3_t soft_iron;       /* Soft Iron матриця W (безрозмірна) */
    float  earth_field;     /* Оцінений модуль поля Землі (мкТл) */
    float  rms_residual;    /* Середньоквадратична нев'язка (мкТл) */
    float  coverage_pct;    /* Відсоток заповнених секторів сфери (0..100) */
    float  condition_num;   /* Число зумовленості матриці W */
    uint32_t crc32;         /* Контрольна сума для збереження у Flash */
    bool   is_valid;        /* Прапорець успішності калібрування */
} mag_cal_result_t;

typedef struct {
    vec3_t samples[MAG_CAL_TOTAL_BINS][MAG_CAL_SAMPLES_PER_BIN];
    uint8_t sample_count[MAG_CAL_TOTAL_BINS];
    uint16_t total_points;
    float target_earth_field;
} mag_cal_collector_t;

/* --- Векторна та матрична алгебра --- */

static inline vec3_t vec3_sub(vec3_t a, vec3_t b) {
    return (vec3_t){ a.x - b.x, a.y - b.y, a.z - b.z };
}

static inline float vec3_dot(vec3_t a, vec3_t b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

static inline float vec3_norm(vec3_t a) {
    return sqrtf(vec3_dot(a, a));
}

static inline vec3_t mat3_mul_vec(const mat3_t *m, vec3_t v) {
    return (vec3_t){
        m->m[0][0] * v.x + m->m[0][1] * v.y + m->m[0][2] * v.z,
        m->m[1][0] * v.x + m->m[1][1] * v.y + m->m[1][2] * v.z,
        m->m[2][0] * v.x + m->m[2][1] * v.y + m->m[2][2] * v.z
    };
}

/* Обчислення індексу сферичної комірки (Spatial Binning) */
static int mag_cal_get_bin_index(vec3_t raw) {
    float norm = vec3_norm(raw);
    if (norm < 1e-3f) return -1;

    /* Кут місця (Elevation/Pitch) від -pi/2 до +pi/2 */
    float elev = asinf(raw.z / norm);
    /* Азимут (Azimuth/Yaw) від -pi до +pi */
    float azim = atan2f(raw.y, raw.x);

    int lat_idx = (int)((elev + 1.5707963f) / (3.1415926f / MAG_CAL_BINS_LAT));
    if (lat_idx < 0) lat_idx = 0;
    if (lat_idx >= MAG_CAL_BINS_LAT) lat_idx = MAG_CAL_BINS_LAT - 1;

    int lon_idx = (int)((azim + 3.1415926f) / (6.2831853f / MAG_CAL_BINS_LON));
    if (lon_idx < 0) lon_idx = 0;
    if (lon_idx >= MAG_CAL_BINS_LON) lon_idx = MAG_CAL_BINS_LON - 1;

    return lat_idx * MAG_CAL_BINS_LON + lon_idx;
}

/* Ініціалізація збирача зразків */
void mag_cal_collector_init(mag_cal_collector_t *col, float earth_b) {
    memset(col, 0, sizeof(mag_cal_collector_t));
    col->target_earth_field = (earth_b > 10.0f) ? earth_b : MAG_CAL_DEFAULT_EARTH_B;
}

/* Додавання виміру з динамічним фільтром */
bool mag_cal_collector_push(mag_cal_collector_t *col, vec3_t raw, vec3_t gyro_rad_s) {
    /* Відхиляємо виміри при надто високій кутовій швидкості */
    if (vec3_norm(gyro_rad_s) > 1.745f) { /* > 100 град/с */
        return false;
    }

    int bin_idx = mag_cal_get_bin_index(raw);
    if (bin_idx < 0 || bin_idx >= MAG_CAL_TOTAL_BINS) return false;

    uint8_t count = col->sample_count[bin_idx];
    if (count < MAG_CAL_SAMPLES_PER_BIN) {
        col->samples[bin_idx][count] = raw;
        col->sample_count[bin_idx] = count + 1;
        col->total_points++;
        return true;
    }
    return false;
}

/* Оцінка відсотка покриття сфери */
float mag_cal_collector_coverage(const mag_cal_collector_t *col) {
    int filled = 0;
    for (int i = 0; i < MAG_CAL_TOTAL_BINS; i++) {
        if (col->sample_count[i] > 0) filled++;
    }
    return ((float)filled / (float)MAG_CAL_TOTAL_BINS) * 100.0f;
}

/* Розрахунок апроксимованого числа зумовленості для симетричної матриці 3x3 */
static float mat3_condition_number(const mat3_t *m) {
    /* Оцінка норми Фробеніуса та діагональних елементів */
    float trace = fabsf(m->m[0][0]) + fabsf(m->m[1][1]) + fabsf(m->m[2][2]);
    float min_diag = fminf(fabsf(m->m[0][0]), fminf(fabsf(m->m[1][1]), fabsf(m->m[2][2])));
    if (min_diag < 1e-4f) return 999.0f;
    return (trace / 3.0f) / min_diag;
}

/* Розв'язувач Levenberg-Marquardt (оптимізація 9 параметрів) */
bool mag_cal_run_solver(const mag_cal_collector_t *col, mag_cal_result_t *out) {
    memset(out, 0, sizeof(mag_cal_result_t));
    out->coverage_pct = mag_cal_collector_coverage(col);

    /* Необхідно мінімум 60% покриття та щонайменше 40 точок */
    if (out->coverage_pct < 60.0f || col->total_points < 40) {
        out->is_valid = false;
        return false;
    }

    /* Вектор параметрів p = [x0, y0, z0, W11, W12, W13, W22, W23, W33] */
    float p[9];
    /* Початкове наближення: центр у вибірковому середньому, W = I */
    float sum_x = 0, sum_y = 0, sum_z = 0;
    for (int b = 0; b < MAG_CAL_TOTAL_BINS; b++) {
        for (int s = 0; s < col->sample_count[b]; s++) {
            sum_x += col->samples[b][s].x;
            sum_y += col->samples[b][s].y;
            sum_z += col->samples[b][s].z;
        }
    }
    p[0] = sum_x / (float)col->total_points;
    p[1] = sum_y / (float)col->total_points;
    p[2] = sum_z / (float)col->total_points;
    p[3] = 1.0f; p[4] = 0.0f; p[5] = 0.0f;
    p[6] = 1.0f; p[7] = 0.0f; p[8] = 1.0f;

    float lambda = 1.0f;
    float earth_b = col->target_earth_field;

    for (int iter = 0; iter < MAG_CAL_MAX_ITERATIONS; iter++) {
        float H[9][9];
        float g[9];
        memset(H, 0, sizeof(H));
        memset(g, 0, sizeof(g));

        mat3_t W = {{
            { p[3], p[4], p[5] },
            { p[4], p[6], p[7] },
            { p[5], p[7], p[8] }
        }};
        vec3_t V0 = { p[0], p[1], p[2] };

        float total_residual_sq = 0.0f;

        /* Накопичення градієнта та матриці нормальних рівнянь */
        for (int b = 0; b < MAG_CAL_TOTAL_BINS; b++) {
            for (int s = 0; s < col->sample_count[b]; s++) {
                vec3_t raw = col->samples[b][s];
                vec3_t d = vec3_sub(raw, V0);
                vec3_t cal = mat3_mul_vec(&W, d);
                float cal_norm = vec3_norm(cal);
                if (cal_norm < 1e-4f) cal_norm = 1e-4f;

                float r = cal_norm - earth_b;
                total_residual_sq += r * r;

                vec3_t u = { cal.x / cal_norm, cal.y / cal_norm, cal.z / cal_norm };

                /* Рядок Якобіана J (1x9) */
                float J[9];
                /* Похідні по V0: -u^T * W */
                J[0] = -(u.x * W.m[0][0] + u.y * W.m[1][0] + u.z * W.m[2][0]);
                J[1] = -(u.x * W.m[0][1] + u.y * W.m[1][1] + u.z * W.m[2][1]);
                J[2] = -(u.x * W.m[0][2] + u.y * W.m[1][2] + u.z * W.m[2][2]);

                /* Похідні по W_ij */
                J[3] = u.x * d.x;                      /* W11 */
                J[4] = u.x * d.y + u.y * d.x;          /* W12 */
                J[5] = u.x * d.z + u.z * d.x;          /* W13 */
                J[6] = u.y * d.y;                      /* W22 */
                J[7] = u.y * d.z + u.z * d.y;          /* W23 */
                J[8] = u.z * d.z;                      /* W33 */

                /* H += J^T * J, g += J^T * r */
                for (int j = 0; j < 9; j++) {
                    g[j] += J[j] * r;
                    for (int k = 0; k < 9; k++) {
                        H[j][k] += J[j] * J[k];
                    }
                }
            }
        }

        /* Демпфування Левенберга: H[i][i] += lambda * H[i][i] + 1e-3 */
        for (int i = 0; i < 9; i++) {
            H[i][i] += lambda * (H[i][i] + 1e-3f);
        }

        /* Розв'язання лінійної системи H * dp = -g (метод Гаусса 9x9) */
        float dp[9];
        for (int i = 0; i < 9; i++) dp[i] = -g[i];

        /* Прямий хід Гаусса з вибором головного елемента */
        bool singular = false;
        for (int i = 0; i < 9; i++) {
            int max_r = i;
            float max_val = fabsf(H[i][i]);
            for (int k = i + 1; k < 9; k++) {
                if (fabsf(H[k][i]) > max_val) {
                    max_val = fabsf(H[k][i]);
                    max_r = k;
                }
            }
            if (max_val < 1e-8f) { singular = true; break; }

            if (max_r != i) {
                for (int k = 0; k < 9; k++) {
                    float tmp = H[i][k]; H[i][k] = H[max_r][k]; H[max_r][k] = tmp;
                }
                float tmp = dp[i]; dp[i] = dp[max_r]; dp[max_r] = tmp;
            }

            for (int k = i + 1; k < 9; k++) {
                float factor = H[k][i] / H[i][i];
                for (int j = i; j < 9; j++) {
                    H[k][j] -= factor * H[i][j];
                }
                dp[k] -= factor * dp[i];
            }
        }

        if (singular) {
            lambda *= 10.0f;
            continue;
        }

        /* Зворотний хід Гаусса */
        for (int i = 8; i >= 0; i--) {
            for (int j = i + 1; j < 9; j++) {
                dp[i] -= H[i][j] * dp[j];
            }
            dp[i] /= H[i][i];
        }

        /* Оновлення вектора параметрів */
        float dp_norm = 0.0f;
        for (int i = 0; i < 9; i++) {
            p[i] += dp[i];
            dp_norm += dp[i] * dp[i];
        }

        if (sqrtf(dp_norm) < 1e-4f) {
            /* Збіжність досягнута */
            break;
        }
        lambda = fmaxf(lambda * 0.2f, 1e-6f);
    }

    /* Запис підсумкових результатів */
    out->offset = (vec3_t){ p[0], p[1], p[2] };
    out->soft_iron = (mat3_t){{
        { p[3], p[4], p[5] },
        { p[4], p[6], p[7] },
        { p[5], p[7], p[8] }
    }};
    out->earth_field = earth_b;
    out->condition_num = mat3_condition_number(&out->soft_iron);

    /* Розрахунок RMS залишкової нев'язки */
    float sum_err_sq = 0.0f;
    for (int b = 0; b < MAG_CAL_TOTAL_BINS; b++) {
        for (int s = 0; s < col->sample_count[b]; s++) {
            vec3_t cal = mat3_mul_vec(&out->soft_iron, vec3_sub(col->samples[b][s], out->offset));
            float err = vec3_norm(cal) - earth_b;
            sum_err_sq += err * err;
        }
    }
    out->rms_residual = sqrtf(sum_err_sq / (float)col->total_points);

    /* Багаторівневий гейт якості: RMS < 3.0 мкТл та зумовленість < 2.5 */
    out->is_valid = (out->rms_residual < 3.0f) && (out->condition_num < 2.5f);
    return out->is_valid;
}

/* Застосування калібрувальної моделі в реальному часі */
vec3_t mag_cal_apply(vec3_t raw, const mag_cal_result_t *cal) {
    if (!cal->is_valid) return raw;
    vec3_t centered = vec3_sub(raw, cal->offset);
    return mat3_mul_vec(&cal->soft_iron, centered);
}
