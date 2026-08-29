#include "compass_mot.h"

#include <math.h>

#define COMPASS_MOT_MIN_SAMPLES 30u
/* Нижче цієї дисперсії струму нахил ділиться на шум. */
#define COMPASS_MOT_MIN_DENOM   1.0e-3
/* Магнітне поле Землі — 25..65 мкТл; менше 5 — це не поле, це збій. */
#define COMPASS_MOT_MIN_FIELD   5.0f
/* M_PI не гарантований у C99 без розширень — тримаємо своє. */
#define COMPASS_MOT_TWO_PI      6.28318530718f

static bool vec3_finite(vec3_t v)
{
    return isfinite(v.x) && isfinite(v.y) && isfinite(v.z);
}

static float vec3_norm(vec3_t v)
{
    return sqrtf(v.x * v.x + v.y * v.y + v.z * v.z);
}

/* ---------------------------------------------------------------- */
/* Компенсатор                                                       */
/* ---------------------------------------------------------------- */

void compass_mot_init(compass_mot_t *cm, vec3_t k,
                      float dt_sec, float cutoff_hz, float max_current_a)
{
    cm->current_filtered = 0.0f;
    cm->max_current_a = (max_current_a > 0.0f) ? max_current_a : 250.0f;
    compass_mot_set_k(cm, k);

    /* Однополюсний ФНЧ: alpha = dt / (RC + dt), RC = 1 / (2π·fc).
     * Він вирівнює групову затримку шунта з дециматором магнітометра —
     * без нього на різкому газі в очищеному полі лишаються тонкі піки. */
    if (!(dt_sec > 0.0f) || !(cutoff_hz > 0.0f)) {
        cm->lpf_alpha = 1.0f;  /* без фільтра, але й без ділення на нуль */
        return;
    }
    const float rc = 1.0f / (COMPASS_MOT_TWO_PI * cutoff_hz);
    cm->lpf_alpha = dt_sec / (rc + dt_sec);
}

void compass_mot_set_k(compass_mot_t *cm, vec3_t k)
{
    if (!vec3_finite(k)) {
        k = (vec3_t){0.0f, 0.0f, 0.0f};
    }
    cm->k = k;
    cm->enabled = (vec3_norm(k) > 1.0e-5f);
}

void compass_mot_reset(compass_mot_t *cm)
{
    cm->current_filtered = 0.0f;
}

vec3_t compass_mot_apply(compass_mot_t *cm, vec3_t b_raw, float current_a)
{
    if (!cm->enabled || !vec3_finite(b_raw)) {
        return b_raw;
    }
    if (!isfinite(current_a) || current_a < 0.0f || current_a > cm->max_current_a) {
        /* Давач струму бреше. Компенсувати за брехнею гірше, ніж не
         * компенсувати: стан фільтра не чіпаємо, віддаємо сире поле. */
        return b_raw;
    }

    cm->current_filtered += cm->lpf_alpha * (current_a - cm->current_filtered);

    const float i = cm->current_filtered;
    return (vec3_t){
        b_raw.x - cm->k.x * i,
        b_raw.y - cm->k.y * i,
        b_raw.z - cm->k.z * i,
    };
}

/* ---------------------------------------------------------------- */
/* Регресія                                                          */
/* ---------------------------------------------------------------- */

void compass_mot_ols_reset(compass_mot_ols_t *ols, vec3_t baseline)
{
    const compass_mot_ols_t empty = {0};
    *ols = empty;
    ols->baseline = baseline;
}

void compass_mot_ols_feed(compass_mot_ols_t *ols, float current_a, vec3_t b_meas)
{
    if (!isfinite(current_a) || current_a < 0.0f || !vec3_finite(b_meas)) {
        ols->rejected++;
        return;
    }

    const double i = (double)current_a;
    const double d[3] = {
        (double)(b_meas.x - ols->baseline.x),
        (double)(b_meas.y - ols->baseline.y),
        (double)(b_meas.z - ols->baseline.z),
    };

    ols->sum_i  += i;
    ols->sum_i2 += i * i;
    for (int a = 0; a < 3; a++) {
        ols->sum_b[a]  += d[a];
        ols->sum_b2[a] += d[a] * d[a];
        ols->sum_ib[a] += i * d[a];
    }
    if (current_a > ols->i_max) {
        ols->i_max = current_a;
    }
    ols->n++;
}

compass_mot_err_t compass_mot_ols_solve(const compass_mot_ols_t *ols,
                                        compass_mot_fit_t *out)
{
    if (ols->n < COMPASS_MOT_MIN_SAMPLES) {
        return COMPASS_MOT_ERR_FEW_SAMPLES;
    }

    const double n = (double)ols->n;
    /* Спільний для трьох осей знаменник: N·∑I² − (∑I)². */
    const double denom = n * ols->sum_i2 - ols->sum_i * ols->sum_i;
    if (fabs(denom) < COMPASS_MOT_MIN_DENOM) {
        return COMPASS_MOT_ERR_NO_SPAN;
    }

    const float base_norm = vec3_norm(ols->baseline);
    if (!(base_norm > COMPASS_MOT_MIN_FIELD)) {
        return COMPASS_MOT_ERR_NO_FIELD;
    }

    float k[3];
    for (int a = 0; a < 3; a++) {
        const double num = n * ols->sum_ib[a] - ols->sum_i * ols->sum_b[a];
        k[a] = (float)(num / denom);

        /* R² для однієї змінної — це квадрат кореляції:
         * num² / (denom · (N·∑ΔB² − (∑ΔB)²)). */
        const double var_b = n * ols->sum_b2[a] - ols->sum_b[a] * ols->sum_b[a];
        out->r2[a] = (var_b > 1.0e-9) ? (float)((num * num) / (denom * var_b)) : 0.0f;
        if (out->r2[a] > 1.0f) {
            out->r2[a] = 1.0f;  /* округлення в double уміє дати 1.0000001 */
        }
    }

    out->k = (vec3_t){k[0], k[1], k[2]};
    out->i_max = ols->i_max;
    out->samples = ols->n;
    out->interference_pct = (vec3_norm(out->k) * ols->i_max / base_norm) * 100.0f;
    return COMPASS_MOT_OK;
}

const char *compass_mot_strerror(compass_mot_err_t err)
{
    switch (err) {
    case COMPASS_MOT_OK:                   return "гаразд";
    case COMPASS_MOT_ERR_FEW_SAMPLES:      return "замало вибірок: прогін обірвався";
    case COMPASS_MOT_ERR_NO_SPAN:          return "струм не змінювався: нахил не визначений";
    case COMPASS_MOT_ERR_NO_FIELD:         return "базове поле близьке до нуля: компас не читається";
    case COMPASS_MOT_ERR_SAVE:             return "збій запису параметрів";
    }
    return "невідома помилка";
}

const char *compass_mot_verdict(float interference_pct)
{
    if (!isfinite(interference_pct)) {
        return "оцінка недійсна";
    }
    if (interference_pct < 10.0f) {
        return "відмінна компоновка: залишкова похибка курсу < 0.5°";
    }
    if (interference_pct <= 30.0f) {
        return "помірна завада: типово для компактної рами, дрейф < 1.5°";
    }
    return "критично: компас надто близько до силових трас, підняти щоглу";
}
