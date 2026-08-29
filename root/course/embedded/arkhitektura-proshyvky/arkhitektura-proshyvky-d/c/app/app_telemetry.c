/* app/app_telemetry.c — арифметика вікна телеметрії.
 * Файл не знає ні про шину, ні про давач: на вхід приходять числа,
 * на вихід іде запис. Через це його тестують таблицею значень. */
#include "app/app_telemetry.h"

#include <math.h>
#include <string.h>

static void reset_window(app_telemetry_t *t, uint32_t now_ms)
{
    t->window_start_ms   = now_ms;
    t->sample_count      = 0u;
    t->fault_count       = 0u;
    t->temp_sum_c        = 0.0f;
    t->temp_min_c        = 0.0f;
    t->temp_max_c        = 0.0f;
    t->humidity_sum_rh   = 0.0f;
    t->pressure_sum_hpa  = 0.0f;
    t->vibration_sq_sum  = 0.0f;
    t->vibration_peak_g  = 0.0f;
}

void app_telemetry_init(app_telemetry_t *t, uint32_t window_ms, uint32_t now_ms)
{
    if (t == 0) {
        return;
    }
    memset(t, 0, sizeof *t);
    t->window_ms = (window_ms == 0u) ? 1000u : window_ms;
    reset_window(t, now_ms);
}

void app_telemetry_add_sample(app_telemetry_t *t, uint32_t now_ms,
                              float temp_c, float humidity_rh,
                              float pressure_hpa, float vibration_g)
{
    if (t == 0) {
        return;
    }
    (void)now_ms;

    if (t->sample_count == 0u) {
        t->temp_min_c = temp_c;
        t->temp_max_c = temp_c;
    } else if (temp_c < t->temp_min_c) {
        t->temp_min_c = temp_c;
    } else if (temp_c > t->temp_max_c) {
        t->temp_max_c = temp_c;
    }

    t->temp_sum_c       += temp_c;
    t->humidity_sum_rh  += humidity_rh;
    t->pressure_sum_hpa += pressure_hpa;
    t->vibration_sq_sum += vibration_g * vibration_g;

    if (vibration_g > t->vibration_peak_g) {
        t->vibration_peak_g = vibration_g;
    }
    t->sample_count++;
}

void app_telemetry_add_fault(app_telemetry_t *t)
{
    if (t != 0) {
        t->fault_count++;
    }
}

bool app_telemetry_window_elapsed(const app_telemetry_t *t, uint32_t now_ms)
{
    return t != 0 && (now_ms - t->window_start_ms) >= t->window_ms;
}

bool app_telemetry_close_window(app_telemetry_t *t, uint32_t now_ms,
                                telemetry_record_t *out_record)
{
    if (t == 0 || out_record == 0) {
        return false;
    }

    if (t->sample_count == 0u) {
        /* Вікно без жодного виміру: запис не складаємо, але вікно зсуваємо,
         * інакше наступне закриття підбере чужий інтервал часу. */
        const uint32_t faults = t->fault_count;
        reset_window(t, now_ms);
        t->fault_count = faults; /* невдачі переносимо у наступне вікно */
        return false;
    }

    const float n = (float)t->sample_count;

    out_record->window_start_ms  = t->window_start_ms;
    out_record->window_end_ms    = now_ms;
    out_record->sample_count     = t->sample_count;
    out_record->temp_avg_c       = t->temp_sum_c / n;
    out_record->temp_min_c       = t->temp_min_c;
    out_record->temp_max_c       = t->temp_max_c;
    out_record->humidity_avg_rh  = t->humidity_sum_rh / n;
    out_record->pressure_avg_hpa = t->pressure_sum_hpa / n;
    out_record->vibration_rms_g  = sqrtf(t->vibration_sq_sum / n);
    out_record->vibration_peak_g = t->vibration_peak_g;
    out_record->fault_count      = t->fault_count;

    reset_window(t, now_ms);
    return true;
}
