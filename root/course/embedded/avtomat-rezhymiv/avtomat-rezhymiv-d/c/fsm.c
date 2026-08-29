#include "fsm.h"

#include <math.h>
#include <stdio.h>
#include <string.h>

#include "fm_time.h"
#include "throttle.h"

void fm_fsm_init(fm_fsm_t *fsm, const fm_params_t *params,
                 const fm_reporter_t *reporter, const fm_state_t *s)
{
    if (!fsm) {
        return;
    }
    memset(fsm, 0, sizeof(*fsm));

    if (params) {
        fsm->params = *params;
    } else {
        fm_params_default(&fsm->params);
    }
    if (reporter) {
        fsm->reporter = *reporter;
    }

    /* Стан за замовчуванням — найнижчий стабілізований: він потребує лише
       інерціального блока, тож у нього можна впасти з будь-якої відмови. */
    fsm->mode          = FM_MODE_STABILIZE;
    fsm->previous_mode = FM_MODE_STABILIZE;
    fsm->mode_priority = FM_PRIO_NONE;
    fsm->mode_since_ms = s ? s->now_ms : 0u;
    fsm->last_step_ms  = s ? s->now_ms : 0u;
    fsm->primed        = false;
    fsm->last_failsafe_reason = NULL;

    fm_arming_init(&fsm->arming, s ? s->armed : false);
    fm_land_init(&fsm->land);
    fm_ctl_init(&fsm->ctl, s);
    fm_debounce_init(&fsm->alt_guard_ok, false);
    fm_debounce_init(&fsm->pos_guard_ok, false);
    fsm->throttle_output = s ? s->motor_output : 0.0f;
}

/* ── службове ─────────────────────────────────────────────────────────────── */

static bool is_landing_mode(fm_mode_t mode)
{
    return mode == FM_MODE_LAND || mode == FM_MODE_EMERGENCY_LAND;
}

static void say(const fm_fsm_t *fsm, uint8_t severity, const char *text)
{
    fm_report_text(&fsm->reporter, severity, text);
}

static void say_denied(const fm_fsm_t *fsm, fm_mode_t target, fm_deny_t deny)
{
    char text[FM_STATUSTEXT_LEN + 1];

    fm_deny_text(target, deny, text, sizeof(text));
    say(fsm, MAV_SEVERITY_ERROR, text);
}

/* Єдине місце, де змінюється поточний режим. Усе, що мусить статися разом зі
   зміною — фіксація уставок, передустановка інтеграторів, скидання детектора
   посадки, латч апаратної відсічки, — стається тут, і ніде більше. */
static void apply_transition(fm_fsm_t *fsm, fm_mode_t target, fm_priority_t prio,
                             const fm_state_t *s, const char *reason, uint8_t severity)
{
    char text[FM_STATUSTEXT_LEN + 1];

    fsm->previous_mode = fsm->mode;
    fsm->mode          = target;
    fsm->mode_priority = prio;
    fsm->mode_since_ms = s->now_ms;

    if (target == FM_MODE_TERMINATE) {
        fm_arming_kill(&fsm->arming);
    }
    if (!is_landing_mode(target)) {
        fm_land_reset(&fsm->land);
    }

    fm_ctl_enter_mode(&fsm->ctl, target, s, &fsm->params);

    if (reason) {
        (void)snprintf(text, sizeof(text), "%s", reason);
    } else {
        (void)snprintf(text, sizeof(text), "Mode: %s -> %s",
                       fm_mode_name(fsm->previous_mode), fm_mode_name(target));
    }
    say(fsm, severity, text);
}

/* Витриманість охоронця: перехід УГОРУ ієрархією дозволено лише тоді, коли
   умова тримається guard_stable_ms. Падіння вниз витримки не потребує. */
static bool guard_is_stable(const fm_fsm_t *fsm, fm_mode_t target)
{
    if (fm_mode_needs_position(target) && !fm_debounce_state(&fsm->pos_guard_ok)) {
        return false;
    }
    if (fm_mode_needs_altitude(target) && !fm_debounce_state(&fsm->alt_guard_ok)) {
        return false;
    }
    return true;
}

/* ── штатний запит ────────────────────────────────────────────────────────── */

fm_deny_t fm_fsm_request_mode(fm_fsm_t *fsm, fm_mode_t target,
                              fm_priority_t priority, const fm_state_t *s)
{
    if (!fsm || !s) {
        return FM_DENY_INVALID_MODE;
    }

    if (!fm_mode_valid(target)) {
        say_denied(fsm, target, FM_DENY_INVALID_MODE);
        fm_report_ack(&fsm->reporter, MAV_CMD_DO_SET_MODE, MAV_RESULT_UNSUPPORTED);
        fm_report_tone(&fsm->reporter, FM_TONE_MODE_REJECTED);
        return FM_DENY_INVALID_MODE;
    }

    /* Сходинка пріоритетів: критичний failsafe не поступається нікому, крім
       апаратної відсічки. */
    if (!fm_priority_overrides(priority, fsm->mode_priority)) {
        say_denied(fsm, target, FM_DENY_FAILSAFE_LOCK);
        fm_report_ack(&fsm->reporter, MAV_CMD_DO_SET_MODE, MAV_RESULT_DENIED);
        fm_report_tone(&fsm->reporter, FM_TONE_MODE_REJECTED);
        return FM_DENY_FAILSAFE_LOCK;
    }

    if (target == fsm->mode) {
        fm_report_ack(&fsm->reporter, MAV_CMD_DO_SET_MODE, MAV_RESULT_ACCEPTED);
        return FM_ALLOW;
    }

    const bool in_air = fm_arming_in_air(&fsm->arming);

    /* 1. Заслінка газу — перед охоронцями: навіть ідеально справні сенсори не
          виправдають стрибка тяги з 48% у нуль. */
    fm_deny_t deny = fm_throttle_interlock(fsm->mode, target, s, &fsm->params, in_air);

    if (deny != FM_ALLOW) {
        say_denied(fsm, target, deny);
        fm_report_ack(&fsm->reporter, MAV_CMD_DO_SET_MODE, fm_deny_mav_result(deny));
        fm_report_tone(&fsm->reporter, FM_TONE_THROTTLE_LOCK);
        return deny;
    }

    /* 2. Параметричні охоронці цільового режиму. */
    deny = fm_guard_check(target, s, &fsm->params);
    if (deny == FM_ALLOW && !guard_is_stable(fsm, target)) {
        deny = FM_DENY_GUARD_UNSTABLE;
    }

    if (deny != FM_ALLOW) {
        /* Відмова нічого не чіпає: ні режиму, ні контурів, ні виходу на мотори. */
        say_denied(fsm, target, deny);
        fm_report_ack(&fsm->reporter, MAV_CMD_DO_SET_MODE, fm_deny_mav_result(deny));
        fm_report_tone(&fsm->reporter, FM_TONE_MODE_REJECTED);
        return deny;
    }

    apply_transition(fsm, target, priority, s, NULL, MAV_SEVERITY_INFO);
    fm_report_ack(&fsm->reporter, MAV_CMD_DO_SET_MODE, MAV_RESULT_ACCEPTED);
    fm_report_tone(&fsm->reporter, FM_TONE_MODE_ACCEPTED);
    return FM_ALLOW;
}

fm_deny_t fm_fsm_request_arm(fm_fsm_t *fsm, const fm_state_t *s)
{
    if (!fsm || !s) {
        return FM_DENY_INVALID_MODE;
    }

    const fm_deny_t deny = fm_arming_request_arm(&fsm->arming, s, &fsm->params);

    if (deny != FM_ALLOW) {
        char text[FM_STATUSTEXT_LEN + 1];

        fm_deny_text(fsm->mode, deny, text, sizeof(text));
        say(fsm, MAV_SEVERITY_ERROR, text);
        fm_report_tone(&fsm->reporter, FM_TONE_MODE_REJECTED);
        return deny;
    }

    /* Озброєння скидає контури на поточні покази: тяга ще нульова, висота
       нульова, і саме від цих значень має початися перший політ. */
    fm_ctl_enter_mode(&fsm->ctl, fsm->mode, s, &fsm->params);
    say(fsm, MAV_SEVERITY_INFO, "Armed");
    fm_report_tone(&fsm->reporter, FM_TONE_MODE_ACCEPTED);
    return FM_ALLOW;
}

fm_deny_t fm_fsm_request_disarm(fm_fsm_t *fsm, const fm_state_t *s)
{
    if (!fsm || !s) {
        return FM_DENY_INVALID_MODE;
    }

    const fm_deny_t deny = fm_arming_request_disarm(&fsm->arming, s);

    if (deny != FM_ALLOW) {
        say(fsm, MAV_SEVERITY_WARNING, "Disarm refused: vehicle is airborne");
        fm_report_tone(&fsm->reporter, FM_TONE_MODE_REJECTED);
        return deny;
    }
    say(fsm, MAV_SEVERITY_INFO, "Disarmed");
    fm_report_tone(&fsm->reporter, FM_TONE_DISARM);
    return FM_ALLOW;
}

void fm_fsm_set_position_target(fm_fsm_t *fsm, int32_t lat_1e7, int32_t lon_1e7,
                                float alt_rel_m)
{
    if (!fsm) {
        return;
    }
    fm_ctl_set_position_target(&fsm->ctl, fsm->mode, lat_1e7, lon_1e7, alt_rel_m);
}

/* ── такт автомата ───────────────────────────────────────────────────────── */

/* Перехоплення пілотом (рівень 2): рух стіків у автономному режимі скасовує
   автономію. Цілимося в найвищий режим, який дозволяють сенсори Й заслінка
   газу: скидати людину одразу в ручну тягу було б тим самим стрибком газу,
   від якого ми захищаємося. */
static void handle_pilot_override(fm_fsm_t *fsm, const fm_state_t *s)
{
    static const fm_mode_t ladder[] = { FM_MODE_POS_HOLD, FM_MODE_ALT_HOLD, FM_MODE_STABILIZE };

    if (!fm_mode_is_autonomous(fsm->mode)) {
        return;
    }
    if (fm_age_ms(s->now_ms, s->rc_last_frame_ms) > fsm->params.rc_loss_ms) {
        return;   /* стіки з мертвого лінка — не воля пілота, а шум */
    }

    const float dead = fsm->params.pilot_override_stick;

    if (fabsf(s->stick_roll) <= dead && fabsf(s->stick_pitch) <= dead &&
        fabsf(s->stick_yaw) <= dead) {
        return;
    }

    const bool in_air = fm_arming_in_air(&fsm->arming);

    for (size_t i = 0; i < sizeof(ladder) / sizeof(ladder[0]); ++i) {
        const fm_mode_t cand = ladder[i];

        if (fm_guard_check(cand, s, &fsm->params) != FM_ALLOW) {
            continue;
        }
        if (fm_throttle_interlock(fsm->mode, cand, s, &fsm->params, in_air) != FM_ALLOW) {
            continue;
        }
        apply_transition(fsm, cand, FM_PRIO_PILOT_OVERRIDE, s,
                         "Pilot override: mission cancelled", MAV_SEVERITY_NOTICE);
        fm_report_tone(&fsm->reporter, FM_TONE_MODE_ACCEPTED);
        return;
    }
}

/* Каскадна деградація: сенсорна база просіла під поточним режимом. Спускаємося
   рівно на одну сходинку — до того рівня, який ще забезпечений. */
static void handle_degradation(fm_fsm_t *fsm, const fm_state_t *s, bool in_air)
{
    if (!in_air) {
        return;
    }

    if (fm_mode_needs_position(fsm->mode) && !fm_debounce_state(&fsm->pos_guard_ok)) {
        const fm_mode_t next = fm_mode_degrade(fsm->mode);

        apply_transition(fsm, next, fsm->mode_priority, s,
                         "Degraded: position estimate lost", MAV_SEVERITY_ALERT);
        fm_report_tone(&fsm->reporter, FM_TONE_FAILSAFE);
    }

    if (fm_mode_needs_altitude(fsm->mode) && !fm_debounce_state(&fsm->alt_guard_ok)) {
        const fm_mode_t next = fm_mode_degrade(fsm->mode);

        apply_transition(fsm, next, fsm->mode_priority, s,
                         "Degraded: altitude estimate lost", MAV_SEVERITY_ALERT);
        fm_report_tone(&fsm->reporter, FM_TONE_FAILSAFE);
    }
}

/* Арбітр аварій (рівні 3–5). */
static void handle_failsafe(fm_fsm_t *fsm, const fm_state_t *s, bool in_air)
{
    const fm_preempt_t e = fm_failsafe_evaluate(s, &fsm->params, fsm->mode, in_air);

    if (!e.active) {
        /* Причина зникла: режим лишається, але замок знімається — пілот знову
           може перемикати. Апаратна відсічка з-під замка не виходить ніколи. */
        if (fsm->mode_priority >= FM_PRIO_NAV_FAILSAFE &&
            fsm->mode_priority < FM_PRIO_HARDWARE && fsm->mode != FM_MODE_TERMINATE) {
            fsm->mode_priority = FM_PRIO_ROUTINE;
        }
        fsm->last_failsafe_reason = NULL;
        return;
    }

    if (!fm_priority_overrides(e.priority, fsm->mode_priority)) {
        return;
    }

    if (fsm->mode == e.mode) {
        /* Уже там, куди веде аварія: піднімаємо замок і мовчимо, щоб не сипати
           той самий STATUSTEXT сто разів на секунду. */
        if (e.priority > fsm->mode_priority) {
            fsm->mode_priority = e.priority;
        }
        return;
    }

    if (fsm->last_failsafe_reason != e.reason) {
        fsm->last_failsafe_reason = e.reason;
    }
    apply_transition(fsm, e.mode, e.priority, s, e.reason, e.severity);
    fm_report_tone(&fsm->reporter, FM_TONE_FAILSAFE);
}

void fm_fsm_update(fm_fsm_t *fsm, const fm_state_t *s)
{
    if (!fsm || !s) {
        return;
    }

    float dt_s = 0.0f;

    if (fsm->primed) {
        dt_s = (float)fm_age_ms(s->now_ms, fsm->last_step_ms) * 0.001f;
    } else {
        fsm->primed = true;
        dt_s        = 0.01f;
    }
    fsm->last_step_ms = s->now_ms;

    /* 1. Детектор польоту — від нього залежать і заслінка газу, і заборона
          роззброєння, і те, які аварії взагалі мають сенс. */
    const bool in_air = fm_arming_update(&fsm->arming, s, &fsm->params);

    /* 2. Витриманість охоронців. Рахуємо ЩОТАКТУ, незалежно від того, чи хтось
          просить зміни режиму: інакше витримка почала б відлік з моменту
          запиту, а не з моменту, коли сенсори справді вичистилися. */
    const bool alt_raw = (fm_guard_altitude(s, &fsm->params) == FM_ALLOW);
    const bool pos_raw = (fm_guard_position(s, &fsm->params) == FM_ALLOW);

    (void)fm_debounce_update(&fsm->alt_guard_ok, alt_raw, s->now_ms,
                             fsm->params.guard_stable_ms, 0u);
    (void)fm_debounce_update(&fsm->pos_guard_ok, pos_raw, s->now_ms,
                             fsm->params.guard_stable_ms, 0u);

    /* 3. Аварії — до всього іншого: вони мають право перебити й місію, і пілота. */
    handle_failsafe(fsm, s, in_air);

    /* 4. Перехоплення стіками (рівень 2) — лише якщо аварія не тримає замок. */
    if (fsm->mode_priority <= FM_PRIO_PILOT_OVERRIDE) {
        handle_pilot_override(fsm, s);
    }

    /* 5. Каскадна деградація за наявними оцінювачами. */
    handle_degradation(fsm, s, in_air);

    /* 6. Комбінація стіків роззброєння — у повітрі ігнорується. */
    if (s->stick_disarm_combo && fm_arming_is_armed(&fsm->arming)) {
        (void)fm_fsm_request_disarm(fsm, s);
    }

    /* 7. Детектор посадки й завершення циклу. */
    fm_land_update(&fsm->land, s, &fsm->params, is_landing_mode(fsm->mode), in_air);

    if (fm_land_take_disarm_event(&fsm->land)) {
        fm_arming_disarm_after_landing(&fsm->arming, s);
        say(fsm, MAV_SEVERITY_INFO, "Landing detected: disarmed");
        fm_report_tone(&fsm->reporter, FM_TONE_DISARM);
        apply_transition(fsm, FM_MODE_STABILIZE, FM_PRIO_NONE, s,
                         "Safe state: on ground, disarmed", MAV_SEVERITY_INFO);
    }

    /* 8. Контури. Автомат уже вирішив, що активне; тут це просто рахується. */
    fsm->throttle_output = fm_ctl_step(&fsm->ctl, fsm->mode, s, &fsm->params,
                                       &fsm->land, dt_s);

    if (!fm_arming_is_armed(&fsm->arming)) {
        fsm->throttle_output = 0.0f;
        fm_slew_reset(&fsm->ctl.throttle_slew, 0.0f);
        fsm->ctl.output = 0.0f;
    }
}

/* ── доступ до стану ─────────────────────────────────────────────────────── */

fm_mode_t fm_fsm_mode(const fm_fsm_t *fsm)
{
    return fsm ? fsm->mode : FM_MODE_STABILIZE;
}

fm_priority_t fm_fsm_priority(const fm_fsm_t *fsm)
{
    return fsm ? fsm->mode_priority : FM_PRIO_NONE;
}

float fm_fsm_throttle(const fm_fsm_t *fsm)
{
    return fsm ? fsm->throttle_output : 0.0f;
}

bool fm_fsm_in_air(const fm_fsm_t *fsm)
{
    return fsm && fm_arming_in_air(&fsm->arming);
}

bool fm_fsm_armed(const fm_fsm_t *fsm)
{
    return fsm && fm_arming_is_armed(&fsm->arming);
}

fm_land_phase_t fm_fsm_land_phase(const fm_fsm_t *fsm)
{
    return fsm ? fsm->land.phase : FM_LAND_IDLE;
}
