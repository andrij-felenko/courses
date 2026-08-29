#include "land_detector.h"

#include <math.h>

#include "fm_time.h"

void fm_land_init(fm_land_detector_t *d)
{
    if (!d) {
        return;
    }
    d->phase        = FM_LAND_IDLE;
    d->contact_ms   = 0u;
    d->disarm_event = false;
    fm_debounce_init(&d->contact, false);
}

void fm_land_reset(fm_land_detector_t *d)
{
    if (!d) {
        return;
    }
    d->phase      = FM_LAND_IDLE;
    d->contact_ms = 0u;
    fm_debounce_init(&d->contact, false);
    /* Подію роззброєння не гасимо: якщо вона вже виникла, її мусить забрати
       автомат, а не з'їсти зміна режиму. */
}

/* Три незалежні ознаки торкання. Жодної з них поодинці не досить: зупинка
   зниження буває й у висінні, мала тяга — у падінні, тиха вертикаль — у
   вільному спуску над водою. */
static bool contact_signature(const fm_state_t *s, const fm_params_t *p)
{
    if (isnan(s->vertical_velocity) || isnan(s->accel_z_variance)) {
        return false;
    }

    const bool vz_stopped   = fabsf(s->vertical_velocity) < p->land_vz_epsilon;
    const float hover       = (s->hover_throttle > 0.05f) ? s->hover_throttle : 0.5f;
    const bool thrust_low   = s->motor_output < (p->land_thr_min * hover);
    const bool quiet_accel  = s->accel_z_variance < p->land_accel_var_max;

    return vz_stopped && thrust_low && quiet_accel;
}

void fm_land_update(fm_land_detector_t *d, const fm_state_t *s, const fm_params_t *p,
                    bool landing_mode, bool in_air)
{
    if (!d || !s || !p) {
        return;
    }

    if (!landing_mode || !s->armed) {
        fm_land_reset(d);
        return;
    }

    if (!in_air) {
        /* Режим посадки на землі — апарат уже стоїть (наприклад, Land увімкнули
           після невдалого зльоту). Гасити мотори можна одразу. */
        d->phase = FM_LAND_LANDED;
        if (!d->disarm_event) {
            d->disarm_event = true;
        }
        return;
    }

    const bool raw = contact_signature(s, p);
    /* Витримка потрібна лише на вхід: варто ознакам розсипатися — контакт
       знімається того ж такту, бо апарат, найімовірніше, відскочив від землі. */
    const bool stable = fm_debounce_update(&d->contact, raw, s->now_ms, p->land_contact_ms, 0u);

    if (!stable) {
        d->phase      = FM_LAND_DESCENT;
        d->contact_ms = 0u;
        return;
    }

    if (d->phase != FM_LAND_GROUND_CONTACT && d->phase != FM_LAND_LANDED) {
        d->phase      = FM_LAND_GROUND_CONTACT;
        d->contact_ms = s->now_ms;
        return;
    }

    if (d->phase == FM_LAND_GROUND_CONTACT &&
        fm_elapsed(s->now_ms, d->contact_ms, p->land_confirm_ms)) {
        d->phase        = FM_LAND_LANDED;
        d->disarm_event = true;
    }
}

bool fm_land_take_disarm_event(fm_land_detector_t *d)
{
    if (!d || !d->disarm_event) {
        return false;
    }
    d->disarm_event = false;
    return true;
}

float fm_land_target_vz(const fm_land_detector_t *d, const fm_params_t *p)
{
    if (!d || !p) {
        return 0.0f;
    }
    return (d->phase == FM_LAND_DESCENT) ? -p->land_speed : 0.0f;
}

const char *fm_land_phase_name(fm_land_phase_t phase)
{
    switch (phase) {
    case FM_LAND_IDLE:           return "idle";
    case FM_LAND_DESCENT:        return "descent";
    case FM_LAND_GROUND_CONTACT: return "ground contact";
    case FM_LAND_LANDED:         return "landed";
    default:                     return "unknown";
    }
}
