#include "vigilance_control.h"

void VigilanceControl_Init(VigilanceTimer_t *vt, uint32_t warning_ms, uint32_t trip_ms) {
    if (!vt) return;
    vt->warning_timeout_ms = warning_ms;
    vt->trip_timeout_ms = trip_ms;
    vt->inactivity_timer = 0;
    vt->state = VIGILANCE_OK;
    vt->warning_buzzer = false;
    vt->warning_lamp = false;
}

void VigilanceControl_Reset(VigilanceTimer_t *vt) {
    if (!vt) return;
    vt->inactivity_timer = 0;
    vt->state = VIGILANCE_OK;
    vt->warning_buzzer = false;
    vt->warning_lamp = false;
}

VigilanceState_t VigilanceControl_Update(VigilanceTimer_t *vt, bool is_enabled, uint32_t delta_ms) {
    if (!vt) return VIGILANCE_TRIPPED;

    // Якщо пристрій дозволу розімкнений (OFF), таймер скидається в безпечний стан
    if (!is_enabled) {
        VigilanceControl_Reset(vt);
        return VIGILANCE_OK;
    }

    // При перебуванні в стані ENABLE відраховуємо час безперервного утримання
    vt->inactivity_timer += delta_ms;

    if (vt->inactivity_timer >= (vt->warning_timeout_ms + vt->trip_timeout_ms)) {
        // Час підтвердження вичерпано — спрацьовує аварійне зупинення
        vt->state = VIGILANCE_TRIPPED;
        vt->warning_buzzer = true;
        vt->warning_lamp = true;
    } else if (vt->inactivity_timer >= vt->warning_timeout_ms) {
        // Фаза попередження: вмикаємо світлову та звукову сигналізацію
        vt->state = VIGILANCE_WARNING;
        vt->warning_lamp = true;
        vt->warning_buzzer = true;
    } else {
        vt->state = VIGILANCE_OK;
        vt->warning_lamp = false;
        vt->warning_buzzer = false;
    }

    return vt->state;
}
