#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define VIB_WINDOW_SIZE      128
#define VIB_RMS_WARN_G       2.5f    // Поріг попередження RMS (g)
#define VIB_RMS_ALARM_G      5.0f    // Критичний поріг RMS (g)
#define VIB_CREST_IMPACT_TH  4.5f    // Поріг крест-фактора для детекції ударів

typedef enum {
    VIB_HEALTH_OK = 0,
    VIB_HEALTH_WARNING,
    VIB_HEALTH_ALARM,
    VIB_HEALTH_IMPACT_LOOSE
} vib_health_status_t;

typedef struct {
    float x;
    float y;
    float z;
} accel_sample_t;

typedef struct {
    float sum_sq_mag;
    float peak_mag;
    uint16_t sample_count;
    vib_health_status_t last_status;
} vib_monitor_t;

void vib_monitor_init(vib_monitor_t *mon) {
    if (!mon) return;
    mon->sum_sq_mag = 0.0f;
    mon->peak_mag = 0.0f;
    mon->sample_count = 0;
    mon->last_status = VIB_HEALTH_OK;
}

// Обробка одного відліку з тривісного акселерометра (значення в одиницях g)
bool vib_monitor_push_sample(vib_monitor_t *mon, const accel_sample_t *s, 
                             float *out_rms, float *out_crest, vib_health_status_t *out_status) {
    if (!mon || !s) return false;

    // Векторна магнітуда прискорення без статичної гравітації (приблизно):
    // Для змінного аналізу віднімаємо постійну складову або беремо модуль вектора:
    float mag = sqrtf(s->x * s->x + s->y * s->y + s->z * s->z);
    
    // Фільтруємо статичну гравітацію 1.0g для аналізу суто вібрації
    float dynamic_accel = fabsf(mag - 1.0f);

    mon->sum_sq_mag += dynamic_accel * dynamic_accel;
    if (dynamic_accel > mon->peak_mag) {
        mon->peak_mag = dynamic_accel;
    }
    mon->sample_count++;

    // Коли вікно заповнене — обчислюємо метрики
    if (mon->sample_count >= VIB_WINDOW_SIZE) {
        float rms = sqrtf(mon->sum_sq_mag / (float)VIB_WINDOW_SIZE);
        float crest = (rms > 0.05f) ? (mon->peak_mag / rms) : 1.0f;

        vib_health_status_t status = VIB_HEALTH_OK;

        if (crest > VIB_CREST_IMPACT_TH && mon->peak_mag > 2.0f) {
            // Високий крест-фактор: характерна ознака люфту або розкрученого гвинта
            status = VIB_HEALTH_IMPACT_LOOSE;
        } else if (rms >= VIB_RMS_ALARM_G) {
            status = VIB_HEALTH_ALARM;
        } else if (rms >= VIB_RMS_WARN_G) {
            status = VIB_HEALTH_WARNING;
        }

        if (out_rms) *out_rms = rms;
        if (out_crest) *out_crest = crest;
        if (out_status) *out_status = status;

        mon->last_status = status;
        mon->sum_sq_mag = 0.0f;
        mon->peak_mag = 0.0f;
        mon->sample_count = 0;
        return true;
    }

    return false;
}
