#include "rc_input.h"
#include "flight_types.h"

/* Порядок каналів AETR — так їх кладе більшість апаратур. */
enum { CH_ROLL = 0, CH_PITCH = 1, CH_THROTTLE = 2, CH_YAW = 3, CH_MODE = 4 };

#define RC_MIN_US 800u
#define RC_MAX_US 2200u

void rc_input_init(rc_input_t *in) {
    if (!in) return;
    for (unsigned i = 0; i < RC_CHANNELS; ++i) in->last.pwm_us[i] = 1500u;
    in->last.pwm_us[CH_THROTTLE] = 1000u;
    in->last.timestamp_ms = 0u;
    in->last_frame_ms = 0u;
    in->have_frame = false;
    in->mode = RC_MODE_AUTO;
    in->candidate = RC_MODE_AUTO;
    in->candidate_count = 0u;
}

/* CRSF передає 11-бітні відліки 172…1811, що відповідають 988…2012 мкс.
   Коефіцієнт узятий з опису протоколу, а не підібраний на око. */
uint16_t rc_crsf_ticks_to_us(uint16_t ticks) {
    float us = 0.62477120195241f * (float)ticks + 881.0f;
    us = clampf(us, (float)RC_MIN_US, (float)RC_MAX_US);
    return (uint16_t)(us + 0.5f);
}

static rc_mode_t mode_from_us(uint16_t us) {
    if (us < 1300u) return RC_MODE_AUTO;
    if (us < 1700u) return RC_MODE_POSHOLD;
    return RC_MODE_MANUAL;
}

/* Симетрична вісь: центр 1500, повний хід ±500 мкс. */
static float norm_sym(uint16_t us) {
    return clampf(((float)us - 1500.0f) / 500.0f, -1.0f, 1.0f);
}

/* Газ: 1000 мкс — нуль, 2000 мкс — повний. */
static float norm_uni(uint16_t us) {
    return clampf(((float)us - 1000.0f) / 1000.0f, 0.0f, 1.0f);
}

bool rc_input_push(rc_input_t *in, const rc_frame_t *frame) {
    if (!in || !frame) return false;

    /* Побитий кадр не має права зрушити ані стіки, ані таймер зв'язку:
       інакше одна помилка CRC виглядатиме як команда пілота. */
    for (unsigned i = 0; i < RC_CHANNELS; ++i) {
        if (frame->pwm_us[i] < RC_MIN_US || frame->pwm_us[i] > RC_MAX_US) return false;
    }

    in->last = *frame;
    in->last_frame_ms = frame->timestamp_ms;
    in->have_frame = true;

    /* Антибрязкіт тумблера: нова позиція мусить протриматися RC_MODE_DEBOUNCE_FRAMES
       кадрів поспіль, інакше джитер радіоканалу зриватиме місію. */
    const rc_mode_t raw = mode_from_us(frame->pwm_us[CH_MODE]);
    if (raw == in->mode) {
        in->candidate = raw;
        in->candidate_count = 0u;
    } else if (raw == in->candidate) {
        if (++in->candidate_count >= RC_MODE_DEBOUNCE_FRAMES) {
            in->mode = raw;
            in->candidate_count = 0u;
        }
    } else {
        in->candidate = raw;
        in->candidate_count = 1u;
    }
    return true;
}

rc_command_t rc_input_poll(const rc_input_t *in, uint32_t now_ms) {
    rc_command_t out = { 0.0f, 0.0f, 0.0f, 0.0f, RC_MODE_AUTO, false };
    if (!in || !in->have_frame) return out;

    out.mode = in->mode;

    /* Різниця беззнакових коректно переживає переповнення лічильника мілісекунд. */
    if ((uint32_t)(now_ms - in->last_frame_ms) > RC_FRAME_TIMEOUT_MS) {
        /* Зв'язку немає. Віддаємо нейтраль і знятий прапорець, а не останні
           прийняті значення: заморожений стік — це найгірше, що можна зробити. */
        return out;
    }

    out.roll     = norm_sym(in->last.pwm_us[CH_ROLL]);
    out.pitch    = norm_sym(in->last.pwm_us[CH_PITCH]);
    out.yaw      = norm_sym(in->last.pwm_us[CH_YAW]);
    out.throttle = norm_uni(in->last.pwm_us[CH_THROTTLE]);
    out.link_ok  = true;
    return out;
}
