#include "arming.h"

#include <math.h>

/* Витримки детектора польоту. Вхід у політ визнаємо швидко (щоб заборона
   роззброєння встигла набути чинності на відриві), вихід — повільно: короткий
   дотик колесом до землі під час підскоку ще не означає посадки. */
#define FM_IN_AIR_RISE_MS  300u
#define FM_IN_AIR_FALL_MS 1000u

void fm_arming_init(fm_arming_t *a, bool armed)
{
    if (!a) {
        return;
    }
    a->armed        = armed;
    a->kill_latched = false;
    fm_debounce_init(&a->in_air, false);
}

static bool in_air_signature(const fm_state_t *s, const fm_params_t *p, bool armed)
{
    if (!armed) {
        return false;
    }
    if (isnan(s->altitude_rel_m)) {
        /* Висоти немає — лишаються силові й інерціальні ознаки. */
        return s->motor_output > p->in_air_motor_min &&
               s->accel_z_variance > p->in_air_accel_var_min;
    }

    const bool high_enough  = s->altitude_rel_m > p->in_air_alt_m;
    const bool motors_spun  = s->motor_output > p->in_air_motor_min;
    const bool moving       = s->accel_z_variance > p->in_air_accel_var_min ||
                              fabsf(s->vertical_velocity) > 0.5f;

    return high_enough || (motors_spun && moving);
}

bool fm_arming_update(fm_arming_t *a, const fm_state_t *s, const fm_params_t *p)
{
    if (!a || !s || !p) {
        return false;
    }
    /* Озброєння — стан САМОГО автомата, а не поле телеметрії: інакше наступний
       такт скасував би щойно виконане роззброєння, бо драйвер ще не встиг
       оновити свій прапорець. */
    if (a->kill_latched) {
        a->armed = false;
    }

    const bool raw = in_air_signature(s, p, a->armed);

    return fm_debounce_update(&a->in_air, raw, s->now_ms, FM_IN_AIR_RISE_MS, FM_IN_AIR_FALL_MS);
}

void fm_arming_notify_landed(fm_arming_t *a, const fm_state_t *s)
{
    if (!a) {
        return;
    }
    fm_debounce_init(&a->in_air, false);
    if (s) {
        (void)fm_debounce_update(&a->in_air, false, s->now_ms, FM_IN_AIR_RISE_MS, FM_IN_AIR_FALL_MS);
    }
}

bool fm_arming_in_air(const fm_arming_t *a)
{
    return a && fm_debounce_state(&a->in_air);
}

bool fm_arming_is_armed(const fm_arming_t *a)
{
    return a && a->armed;
}

fm_deny_t fm_arming_request_disarm(fm_arming_t *a, const fm_state_t *s)
{
    if (!a || !s) {
        return FM_DENY_INVALID_MODE;
    }
    if (!a->armed) {
        return FM_ALLOW;   /* уже роззброєні — запит нічого не змінює */
    }
    if (fm_arming_in_air(a)) {
        /* Комбінація стіків у польоті ігнорується завжди. Пілот, який справді
           хоче зупинити мотори в повітрі, має виділений апаратний тумблер. */
        return FM_DENY_IN_AIR;
    }
    a->armed = false;
    return FM_ALLOW;
}

void fm_arming_disarm_after_landing(fm_arming_t *a, const fm_state_t *s)
{
    if (!a) {
        return;
    }
    a->armed = false;
    fm_arming_notify_landed(a, s);
}

void fm_arming_kill(fm_arming_t *a)
{
    if (!a) {
        return;
    }
    a->kill_latched = true;
    a->armed        = false;
}

fm_deny_t fm_arming_request_arm(fm_arming_t *a, const fm_state_t *s, const fm_params_t *p)
{
    if (!a || !s || !p) {
        return FM_DENY_INVALID_MODE;
    }
    if (a->kill_latched) {
        /* Після апаратної відсічки озброєння дозволене лише повним циклом
           живлення: інакше причина відсічки поїхала б у політ разом з нами. */
        return FM_DENY_FAILSAFE_LOCK;
    }
    if (fm_arming_in_air(a)) {
        return FM_DENY_IN_AIR;
    }

    const fm_deny_t att = fm_guard_attitude(s);

    if (att != FM_ALLOW) {
        return att;
    }
    a->armed = true;
    return FM_ALLOW;
}
