#include "fallback.h"

#include <math.h>

#include "platform.h"

static float clampf(float v, float lo, float hi) {
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

// Рампа з обмеженням і прискорення, і ривка: уставка не може ні стрибнути,
// ні різко змінити темп — саме це рятує шестерні під час повернення контролю.
static void ramp_throttle(fallback_t *fb, float target, float dt) {
    if (dt <= 0.0f) return;
    float err = target - fb->throttle;
    float want_rate = clampf(err / dt, -FB_MAX_ACCEL, FB_MAX_ACCEL);
    float d_rate = clampf(want_rate - fb->throttle_rate, -FB_MAX_JERK * dt, FB_MAX_JERK * dt);

    fb->throttle_rate += d_rate;
    fb->throttle += fb->throttle_rate * dt;

    if ((err > 0.0f && fb->throttle > target) || (err < 0.0f && fb->throttle < target)) {
        fb->throttle = target;          // ціль досягнуто, темп скидаємо
        fb->throttle_rate = 0.0f;
    }
    fb->throttle = clampf(fb->throttle, -1.0f, 1.0f);
}

static void ramp_steering(fallback_t *fb, float target, float dt) {
    float step = FB_STEER_RATE * dt;
    float err = target - fb->steering;
    if (err > step) fb->steering += step;
    else if (err < -step) fb->steering -= step;
    else fb->steering = target;
}

static void enter(fallback_t *fb, fallback_state_t st, uint32_t now, uint8_t ev, bool critical) {
    fb->state = st;
    fb->state_since_ms = now;
    logstore_event(&fb->log, now, ev, critical);

    switch (st) {
    case FALLBACK_AUTONOMOUS_PHASE2:
        // Тиша затягнулася: сесію анулюємо. Тепер жодна команда не діє,
        // поки пульт не пройде рукостискання наново.
        link_drop_session(&fb->link);
        break;
    case FALLBACK_SAFE_STATE_PHASE3:
        fb->throttle = 0.0f;
        fb->throttle_rate = 0.0f;
        fb->steering = 0.0f;
        plat_set_actuators(0.0f, 0.0f);
        plat_set_power_enable(false);
        plat_set_brake(true);
        plat_set_low_power(true);
        break;
    case FALLBACK_RECONNECTING:
        plat_set_power_enable(true);
        plat_set_low_power(false);
        plat_set_beacon(false);
        plat_set_brake(false);
        break;
    default:
        break;
    }
}

void fallback_init(fallback_t *fb, uint32_t raw_now, uint32_t key) {
    fb->state = FALLBACK_ONLINE;
    fb->state_since_ms = raw_now;
    fb->last_frame_ms = raw_now;
    fb->offline_since_ms = raw_now;

    fb->cached.type = LINK_TYPE_CMD;
    fb->cached.session_id = 0U;
    fb->cached.seq = 0U;
    fb->cached.t_ms = raw_now;
    fb->cached.throttle = 0.0f;
    fb->cached.steering = 0.0f;

    fb->throttle = 0.0f;
    fb->throttle_rate = 0.0f;
    fb->steering = 0.0f;
    fb->dr_pos_m = 0.0f;
    fb->dr_sigma_m = 0.0f;
    fb->beacon_phase_ms = 0U;
    fb->drain_credit = 0U;
    fb->raw_now = raw_now;

    timebase_init(&fb->tb, raw_now);
    deadman_init(&fb->dm, FB_DEADMAN_TIMEOUT_MS, FB_HEARTBEAT_MS, raw_now);
    link_init(&fb->link, key);
    logstore_init(&fb->log);

    plat_set_power_enable(true);
    plat_set_brake(false);
}

link_status_t fallback_on_frame(fallback_t *fb, const uint8_t *frame, size_t len, uint32_t raw_now) {
    uint32_t now = timebase_now(&fb->tb, raw_now);
    link_command_t cmd;

    link_status_t st = link_accept(&fb->link, frame, len, now, &cmd);
    if (st != LINK_OK) return st;   // не кадр — не дозвіл: мертва рука не годується

    fb->last_frame_ms = now;
    deadman_feed(&fb->dm, now);

    if (cmd.type == LINK_TYPE_HELLO) {
        // Крок 2 порядку відновлення: еталон часу лише ставимо в чергу на
        // підтягування. Стрибок годинника назад заборонений.
        timebase_set_reference(&fb->tb, raw_now, cmd.t_ms);
        if (fb->state == FALLBACK_AUTONOMOUS_PHASE2 || fb->state == FALLBACK_SAFE_STATE_PHASE3) {
            enter(fb, FALLBACK_RECONNECTING, now, FB_EV_RECONNECT, false);
        }
        return LINK_OK;
    }

    fb->cached = cmd;
    if (fb->state == FALLBACK_HOLD_PHASE1) {
        enter(fb, FALLBACK_ONLINE, now, FB_EV_ONLINE, false);
    }
    return LINK_OK;
}

void fallback_tick(fallback_t *fb, uint32_t raw_now, float sensor_value) {
    timebase_tick(&fb->tb, raw_now);
    uint32_t now = timebase_now(&fb->tb, raw_now);
    uint32_t dt_ms = raw_now - fb->raw_now;
    fb->raw_now = raw_now;
    float dt = (float)dt_ms / 1000.0f;

    deadman_service(&fb->dm, now);   // поки дозвіл живий — тактуємо ENABLE
    plat_interlock_service();        // а це вже реакція зовнішньої мікросхеми

    uint32_t silence = now - fb->last_frame_ms;

    switch (fb->state) {
    case FALLBACK_ONLINE:
        if (deadman_expired(&fb->dm, now)) {
            fb->offline_since_ms = now;
            fb->dr_pos_m = 0.0f;
            fb->dr_sigma_m = 0.0f;
            enter(fb, FALLBACK_HOLD_PHASE1, now, FB_EV_LINK_LOST, false);
        } else {
            ramp_throttle(fb, fb->cached.throttle, dt);
            ramp_steering(fb, fb->cached.steering, dt);
        }
        break;

    case FALLBACK_HOLD_PHASE1: {
        // Екстраполюємо рух за одометрією й одразу рахуємо, як росте похибка.
        fb->dr_pos_m += fabsf(fb->throttle) * FB_MAX_SPEED_MPS * dt;
        fb->dr_sigma_m += (FB_DR_SIGMA_BASE + FB_DR_SIGMA_GAIN * fabsf(fb->throttle)) * dt;

        if (fb->dr_sigma_m > FB_DR_SIGMA_LIMIT) {
            // Невизначеність вийшла за радіус безпеки — числення обриваємо
            // примусово, не чекаючи п'яти секунд.
            enter(fb, FALLBACK_AUTONOMOUS_PHASE2, now, FB_EV_DR_LIMIT, true);
            break;
        }
        if (silence > FB_PHASE1_MS) {
            enter(fb, FALLBACK_AUTONOMOUS_PHASE2, now, FB_EV_PHASE2, false);
            break;
        }
        // Утримання уставки: наростання заборонене, дозволене лише збереження
        // або згасання, тому ціль не більша за модулем від поточної тяги.
        float hold = (fabsf(fb->cached.throttle) < fabsf(fb->throttle)) ? fb->cached.throttle : fb->throttle;
        ramp_throttle(fb, hold, dt);
        ramp_steering(fb, fb->steering, dt);
        break;
    }

    case FALLBACK_AUTONOMOUS_PHASE2: {
        if (silence > FB_PHASE2_MS) {
            enter(fb, FALLBACK_SAFE_STATE_PHASE3, now, FB_EV_SAFE_STATE, true);
            break;
        }
        // Локальний регулятор: рівномірне сповільнення до нуля, кермо в центр,
        // а на зупинці — механічне гальмо.
        float step = FB_DECEL * dt;
        float target;
        if (fb->throttle > step) target = fb->throttle - step;
        else if (fb->throttle < -step) target = fb->throttle + step;
        else target = 0.0f;

        ramp_throttle(fb, target, dt);
        ramp_steering(fb, 0.0f, dt);

        if (fabsf(fb->throttle) < 0.01f) {
            fb->throttle = 0.0f;
            fb->throttle_rate = 0.0f;
            plat_set_brake(true);
        }
        break;
    }

    case FALLBACK_SAFE_STATE_PHASE3:
        // Енергію знято безумовно; рампи тут немає й бути не може.
        fb->throttle = 0.0f;
        fb->throttle_rate = 0.0f;
        fb->steering = 0.0f;
        fb->beacon_phase_ms = (fb->beacon_phase_ms + dt_ms) % FB_BEACON_PERIOD_MS;
        plat_set_beacon(fb->beacon_phase_ms < FB_BEACON_FLASH_MS);
        break;

    case FALLBACK_RECONNECTING:
        if (deadman_expired(&fb->dm, now)) {
            // Рукостискання було, а команди знову зникли — назад у фазу 1.
            fb->offline_since_ms = now;
            fb->dr_sigma_m = 0.0f;
            enter(fb, FALLBACK_HOLD_PHASE1, now, FB_EV_LINK_LOST, false);
            break;
        }
        ramp_throttle(fb, fb->cached.throttle, dt);
        ramp_steering(fb, fb->cached.steering, dt);
        if ((uint32_t)(now - fb->state_since_ms) >= FB_RECONNECT_MS &&
            fabsf(fb->cached.throttle - fb->throttle) < 0.02f) {
            enter(fb, FALLBACK_ONLINE, now, FB_EV_ONLINE, false);
        }
        break;
    }

    if (fb->state != FALLBACK_SAFE_STATE_PHASE3) {
        plat_set_actuators(fb->throttle, fb->steering);
        if (fabsf(fb->throttle) > 0.01f) plat_set_brake(false);
    }

    uint32_t offline_ms = (fb->state == FALLBACK_ONLINE) ? 0U : (uint32_t)(now - fb->offline_since_ms);
    logstore_sample(&fb->log, now, sensor_value, offline_ms);
    logstore_background(&fb->log);

    if (fb->state == FALLBACK_ONLINE || fb->state == FALLBACK_RECONNECTING) {
        fb->drain_credit += FB_DRAIN_CREDIT_TICK;
        if (fb->drain_credit > FB_DRAIN_CREDIT_MAX) fb->drain_credit = FB_DRAIN_CREDIT_MAX;
        fb->drain_credit -= logstore_drain(&fb->log, fb->drain_credit);
    }
}

uint32_t fallback_offline_ms(const fallback_t *fb) {
    if (fb->state == FALLBACK_ONLINE) return 0U;
    return (uint32_t)(timebase_now(&fb->tb, fb->raw_now) - fb->offline_since_ms);
}

const char *fallback_state_name(fallback_state_t st) {
    switch (st) {
    case FALLBACK_ONLINE:             return "ONLINE";
    case FALLBACK_HOLD_PHASE1:        return "HOLD (фаза 1)";
    case FALLBACK_AUTONOMOUS_PHASE2:  return "AUTONOMOUS (фаза 2)";
    case FALLBACK_SAFE_STATE_PHASE3:  return "SAFE STATE (фаза 3)";
    case FALLBACK_RECONNECTING:       return "RECONNECTING";
    default:                          return "?";
    }
}
