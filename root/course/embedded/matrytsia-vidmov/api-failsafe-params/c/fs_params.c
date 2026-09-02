#include "fs_params.h"

#include <math.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>

/* Таблиця живе у Flash (const): у ОЗП лежать лише значення. */
const fs_param_desc_t fs_param_desc[FS_PARAM_COUNT] = {
    { "FS_THR_ENABLE",    FS_TYPE_INT8,     0.0f,      3.0f,     1.0f, 1 },
    { "FS_THR_VALUE",     FS_TYPE_INT16,  900.0f,   1000.0f,   950.0f, 1 },
    { "FS_RC_TIMEOUT",    FS_TYPE_FLOAT,    0.5f,     10.0f,     1.5f, 1 },
    { "FS_RC_RECOVER",    FS_TYPE_FLOAT,    1.0f,      5.0f,     2.0f, 2 },
    { "FS_GCS_TIMEOUT",   FS_TYPE_FLOAT,    2.0f,     60.0f,     5.0f, 1 },
    { "FS_GCS_ENABLE",    FS_TYPE_INT8,     0.0f,      2.0f,     1.0f, 1 },
    { "FS_EKF_THRESH",    FS_TYPE_FLOAT,    0.5f,      2.0f,     1.0f, 2 },
    { "FS_GNSS_HDOP_MAX", FS_TYPE_FLOAT,    1.2f,      5.0f,     2.5f, 2 },
    { "FS_GNSS_TIMEOUT",  FS_TYPE_FLOAT,    1.0f,     10.0f,     3.0f, 2 },
    { "FS_BATT_LOW_V",    FS_TYPE_FLOAT,    3.4f,      3.7f,    3.55f, 1 },
    { "FS_BATT_CRIT_V",   FS_TYPE_FLOAT,    3.1f,     3.45f,    3.30f, 1 },
    { "FS_BATT_HYST_MS",  FS_TYPE_INT16,  200.0f,   3000.0f,  1000.0f, 2 },
    { "FS_BATT_ACT",      FS_TYPE_INT8,     1.0f,      4.0f,     2.0f, 1 },
    { "FS_FENCE_ENABLE",  FS_TYPE_INT8,     0.0f,      1.0f,     1.0f, 1 },
    { "FS_FENCE_RADIUS",  FS_TYPE_FLOAT,   50.0f,  10000.0f,   500.0f, 1 },
    { "FS_FENCE_ALT_MAX", FS_TYPE_FLOAT,   10.0f,    500.0f,   120.0f, 1 },
    { "FS_FENCE_ACT",     FS_TYPE_INT8,     1.0f,      3.0f,     1.0f, 1 },
    { "FS_CRASH_DUMP",    FS_TYPE_INT8,     0.0f,      1.0f,     1.0f, 3 },
    { "FS_LAST_GASP_TX",  FS_TYPE_INT8,     0.0f,      1.0f,     1.0f, 3 },
};

static void store(fs_param_block_t *b, fs_param_id_t id, float value)
{
    switch (fs_param_desc[id].type) {
    case FS_TYPE_INT8:  b->v[id].i8  = (int8_t)lrintf(value);  break;
    case FS_TYPE_INT16: b->v[id].i16 = (int16_t)lrintf(value); break;
    default:            b->v[id].f32 = value;                  break;
    }
}

void fs_params_load_defaults(fs_param_block_t *b)
{
    for (int i = 0; i < FS_PARAM_COUNT; ++i)
        store(b, (fs_param_id_t)i, fs_param_desc[i].def);
}

int fs_params_find(const char *name)
{
    if (name == NULL)
        return -1;
    for (int i = 0; i < FS_PARAM_COUNT; ++i)
        if (strncmp(name, fs_param_desc[i].name, FS_PARAM_NAME_MAX) == 0)
            return i;
    return -1;
}

float fs_params_get(const fs_param_block_t *b, fs_param_id_t id)
{
    if (id >= FS_PARAM_COUNT)
        return 0.0f;
    switch (fs_param_desc[id].type) {
    case FS_TYPE_INT8:  return (float)b->v[id].i8;
    case FS_TYPE_INT16: return (float)b->v[id].i16;
    default:            return b->v[id].f32;
    }
}

fs_param_status_t fs_params_set(fs_param_block_t *b, fs_param_id_t id, float value)
{
    if (id >= FS_PARAM_COUNT)
        return FS_PARAM_ERR_ID;
    /* NaN не проходить жодного порівняння — саме тому перевіряємо через "не в межах". */
    if (!(value >= fs_param_desc[id].min && value <= fs_param_desc[id].max))
        return FS_PARAM_ERR_RANGE;
    store(b, id, value);
    return FS_PARAM_OK;
}

fs_param_status_t fs_params_set_by_name(fs_param_block_t *b, const char *name, float value)
{
    int idx = fs_params_find(name);
    if (idx < 0)
        return FS_PARAM_ERR_ID;
    return fs_params_set(b, (fs_param_id_t)idx, value);
}

static void report(char *out, uint32_t sz, uint32_t *off, const char *fmt, ...)
{
    va_list ap;
    int n;

    if (out == NULL || *off + 1 >= sz)
        return;
    va_start(ap, fmt);
    n = vsnprintf(out + *off, sz - *off, fmt, ap);
    va_end(ap);
    if (n > 0)
        *off += (uint32_t)n < (sz - *off) ? (uint32_t)n : (sz - *off - 1);
}

int fs_params_validate(const fs_param_block_t *b, float rtl_alt_m, char *out, uint32_t out_sz)
{
    uint32_t off = 0;
    int bad = 0;
    float low, crit, recover, thr_value, fence_alt;

    if (out != NULL && out_sz > 0)
        out[0] = '\0';

    /* 0. Значення, зчитані зі старої конфігурації, могли вийти за нові межі. */
    for (int i = 0; i < FS_PARAM_COUNT; ++i) {
        float v = fs_params_get(b, (fs_param_id_t)i);
        if (!(v >= fs_param_desc[i].min && v <= fs_param_desc[i].max)) {
            report(out, out_sz, &off, "%s=%.2f поза [%.2f..%.2f]\n",
                   fs_param_desc[i].name, (double)v,
                   (double)fs_param_desc[i].min, (double)fs_param_desc[i].max);
            ++bad;
        }
    }

    low       = fs_params_get(b, FS_P_BATT_LOW_V);
    crit      = fs_params_get(b, FS_P_BATT_CRIT_V);
    recover   = fs_params_get(b, FS_P_RC_RECOVER);
    thr_value = fs_params_get(b, FS_P_THR_VALUE);
    fence_alt = fs_params_get(b, FS_P_FENCE_ALT_MAX);

    /* 1. Інверсія порогів батареї: між попередженням і посадкою треба лишити запас. */
    if (low - crit < 0.15f) {
        report(out, out_sz, &off,
               "FS_BATT_LOW_V(%.2f) - FS_BATT_CRIT_V(%.2f) < 0.15 В/комірка\n",
               (double)low, (double)crit);
        ++bad;
    }

    /* 2. Програмний failsafe безсилий, якщо поріг газу не нижчий за робочий мінімум:
     *    приймач у режимі Hold Last State просто повторює останній кадр. */
    if (fs_params_get(b, FS_P_THR_ENABLE) != 0.0f && thr_value >= 1000.0f) {
        report(out, out_sz, &off,
               "FS_THR_VALUE(%.0f) не нижчий за мінімум газу 1000 мкс\n", (double)thr_value);
        ++bad;
    }

    /* 3. Захист від брязкоту на межі зони радіовидимості. */
    if (recover < 1.0f) {
        report(out, out_sz, &off, "FS_RC_RECOVER(%.2f) < 1.0 с\n", (double)recover);
        ++bad;
    }

    /* 4. Стеля геозони мусить бути вищою за висоту повернення щонайменше на 20 м,
     *    інакше сам RTL пробиває власний бар'єр. */
    if (fence_alt < rtl_alt_m + 20.0f) {
        report(out, out_sz, &off,
               "FS_FENCE_ALT_MAX(%.0f) < RTL_ALT(%.0f) + 20 м\n",
               (double)fence_alt, (double)rtl_alt_m);
        ++bad;
    }

    /* 5. Зведення з вимкненим батарейним чи канальним захистом заборонене. */
    if (fs_params_get(b, FS_P_BATT_ACT) < 1.0f) {
        report(out, out_sz, &off, "батарейний захист вимкнено (FS_BATT_ACT=0)\n");
        ++bad;
    }
    if (fs_params_get(b, FS_P_THR_ENABLE) == 0.0f) {
        report(out, out_sz, &off, "канальний failsafe вимкнено (FS_THR_ENABLE=0)\n");
        ++bad;
    }

    return bad;
}

const char *fs_param_status_str(fs_param_status_t s)
{
    switch (s) {
    case FS_PARAM_OK:        return "OK";
    case FS_PARAM_ERR_ID:    return "UNKNOWN_PARAM";
    case FS_PARAM_ERR_RANGE: return "OUT_OF_RANGE";
    default:                 return "?";
    }
}
