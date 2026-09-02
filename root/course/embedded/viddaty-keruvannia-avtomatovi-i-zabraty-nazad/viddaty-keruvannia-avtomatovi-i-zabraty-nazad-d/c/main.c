#include <math.h>
#include <stdio.h>

#include "annunciate.h"
#include "flight_types.h"
#include "nav_guard.h"
#include "rc_input.h"
#include "takeover.h"

/* Прогін сценарію зі статті: літак іде за маршрутом на 22 м/с і 45 м, збоку
   дме вітер, на 2-й секунді пілот смикає стік на себе і вправо, обходячи трос
   крана, а потім відпускає ручку. Модель планера тут навмисно проста — вона
   потрібна лише для того, щоб побачити роботу перехоплення. */

#define LOOP_HZ    200.0f
#define DT         (1.0f / LOOP_HZ)
#define RUN_SEC    9.0f
#define WIND_Y     6.0f   /* м/с, вітер зліва зносить апарат управо по +y */
#define DEG2RAD    0.01745329f
#define RAD2DEG    57.2957795f

#define PILOT_ROLL_LIMIT_DEG  45.0f
#define PILOT_PITCH_LIMIT_DEG 15.0f
#define PILOT_YAW_LIMIT_DPS   20.0f

typedef struct {
    vehicle_state_t st;
    float roll_deg;  /* фактичний крен: приводи й планер відстають від команди */
    float pitch_deg;
} plane_t;

typedef struct {
    const char *title;
    bool  anti_windup;
    float rc_loss_at; /* с; від'ємне — зв'язок не втрачається */
    float fence_at;   /* с; від'ємне — геозону не порушуємо */
} scenario_t;

static void plane_step(plane_t *pl, const control_command_t *u, float dt) {
    pl->roll_deg  += (u->roll  - pl->roll_deg)  * (dt / (0.25f + dt));
    pl->pitch_deg += (u->pitch - pl->pitch_deg) * (dt / (0.40f + dt));

    const float roll_rad = pl->roll_deg * DEG2RAD;
    const float pitch_rad = pl->pitch_deg * DEG2RAD;

    /* Координований розворот: правий крен веде ніс за годинниковою стрілкою,
       тобто курс у нашій системі координат спадає. */
    const float turn_rate = (9.81f / fmaxf(pl->st.airspeed, 8.0f)) * tanf(roll_rad) * RAD2DEG;
    pl->st.heading_deg = wrap180(pl->st.heading_deg - turn_rate * dt);

    const float hdg = pl->st.heading_deg * DEG2RAD;
    pl->st.x += (pl->st.airspeed * cosf(hdg)) * dt;
    pl->st.y += (pl->st.airspeed * sinf(hdg) + WIND_Y) * dt;
    pl->st.alt += pl->st.airspeed * sinf(pitch_rad) * dt;

    const float spd_eq = 12.0f + 15.0f * u->throttle - 20.0f * sinf(pitch_rad);
    pl->st.airspeed += (spd_eq - pl->st.airspeed) * (dt / (1.5f + dt));
    pl->st.airspeed = fmaxf(pl->st.airspeed, 8.0f);
}

/* Що робить пілот. Важіль газу весь політ лишається там, де його поклали:
   це і є неузгодженість газу з пастки номер два. */
static void pilot_script(float t, float *roll, float *pitch, float *thr, rc_mode_t *mode) {
    *roll = 0.0f;
    *pitch = 0.0f;
    *thr = 0.30f;
    *mode = RC_MODE_AUTO;
    if (t >= 2.0f && t < 3.6f) {
        *roll = 0.75f;  /* правий крен */
        *pitch = 0.90f; /* стік на себе — набір висоти */
    }
}

static uint16_t to_pwm_sym(float v) {
    return (uint16_t)(1500.0f + 500.0f * clampf(v, -1.0f, 1.0f) + 0.5f);
}

static uint16_t to_pwm_uni(float v) {
    return (uint16_t)(1000.0f + 1000.0f * clampf(v, 0.0f, 1.0f) + 0.5f);
}

static uint16_t mode_pwm(rc_mode_t m) {
    return (m == RC_MODE_AUTO) ? 1100u : (m == RC_MODE_POSHOLD) ? 1500u : 1900u;
}

static void run_scenario(const scenario_t *sc) {
    plane_t pl;
    pl.st.x = 0.0f;
    pl.st.y = 0.0f;
    pl.st.alt = 45.0f;
    pl.st.heading_deg = 0.0f;
    pl.st.airspeed = 22.0f;
    pl.roll_deg = 0.0f;
    pl.pitch_deg = 0.0f;

    nav_setpoint_t sp;
    sp.leg_x = 0.0f;
    sp.leg_y = 0.0f;
    sp.wp_x = 3000.0f;
    sp.wp_y = 0.0f;
    sp.alt_target = 45.0f;
    sp.airspeed_target = 22.0f;

    nav_guard_t nav;
    nav_guard_init(&nav, &sp);
    nav.anti_windup = sc->anti_windup;

    rc_input_t rc_in;
    rc_input_init(&rc_in);

    takeover_t tk;
    takeover_init(&tk);

    annunciator_t an;
    annunciate_init(&an);

    control_command_t prev_out = { 0.0f, 0.0f, 0.0f, 0.0f };
    control_command_t prev_mux = { 0.0f, 0.0f, 0.0f, 0.0f };
    bool have_prev = false;

    float max_rate_blend = 0.0f; /* °/с на виході змішувача */
    float max_rate_mux = 0.0f;   /* °/с, якби стояв простий мультиплексор */
    float max_abs_i = 0.0f;
    float max_xte_after = 0.0f;  /* найбільший відхід від лінії після віддачі */
    float next_print = 0.0f;

    printf("\n=== %s ===\n", sc->title);
    printf("   t    стан           alpha  thr    xte      I     roll    alt   thr\n");

    const int steps = (int)(RUN_SEC * LOOP_HZ);
    for (int i = 0; i <= steps; ++i) {
        const float t = (float)i * DT;
        const uint32_t now_ms = (uint32_t)(t * 1000.0f);

        float sr, spitch, sthr;
        rc_mode_t smode;
        pilot_script(t, &sr, &spitch, &sthr, &smode);

        const bool link_alive = (sc->rc_loss_at < 0.0f) || (t < sc->rc_loss_at);
        if (link_alive) {
            rc_frame_t frame;
            for (unsigned c = 0; c < RC_CHANNELS; ++c) frame.pwm_us[c] = 1500u;
            frame.pwm_us[0] = to_pwm_sym(sr);
            frame.pwm_us[1] = to_pwm_sym(spitch);
            frame.pwm_us[2] = to_pwm_uni(sthr);
            frame.pwm_us[3] = to_pwm_sym(0.0f);
            frame.pwm_us[4] = mode_pwm(smode);
            frame.timestamp_ms = now_ms;
            (void)rc_input_push(&rc_in, &frame);
        }

        const rc_command_t rc = rc_input_poll(&rc_in, now_ms);
        const bool fence = (sc->fence_at >= 0.0f) && (t >= sc->fence_at);

        const takeover_status_t st = takeover_update(&tk, &rc, fence, DT);

        const control_command_t u_auto = nav_guard_step(&nav, &pl.st, st.freeze_nav, DT);

        control_command_t u_pilot;
        u_pilot.roll = rc.roll * PILOT_ROLL_LIMIT_DEG;
        u_pilot.pitch = rc.pitch * PILOT_PITCH_LIMIT_DEG;
        u_pilot.yaw = rc.yaw * PILOT_YAW_LIMIT_DPS;
        u_pilot.throttle = rc.throttle;

        const control_command_t u_out = takeover_blend(&st, &u_auto, &u_pilot);

        /* Той самий момент, але з наївним мультиплексором: жодного змішування,
           перемикання за α > 0.5. Порівняння швидкостей — нижче в підсумку. */
        const control_command_t u_mux = (st.alpha > 0.5f) ? u_pilot : u_auto;

        if (have_prev) {
            const float r1 = fabsf(u_out.roll - prev_out.roll) / DT;
            const float r2 = fabsf(u_mux.roll - prev_mux.roll) / DT;
            if (r1 > max_rate_blend) max_rate_blend = r1;
            if (r2 > max_rate_mux) max_rate_mux = r2;
        }
        prev_out = u_out;
        prev_mux = u_mux;
        have_prev = true;

        if (fabsf(nav.integral) > max_abs_i) max_abs_i = fabsf(nav.integral);

        plane_step(&pl, &u_out, DT);

        if (t >= 3.6f) {
            const float xte_now = fabsf(nav_guard_crosstrack(&nav, &pl.st));
            if (xte_now > max_xte_after) max_xte_after = xte_now;
        }

        annunciate_events(&an, &tk, now_ms);
        annunciate_stream(&an, &st, now_ms);

        if (t + 1e-4f >= next_print) {
            next_print += 0.25f;
            printf("%5.2f  %-13s %.2f  %.2f %+7.1f %+6.1f %+7.1f %6.1f  %.2f\n",
                   (double)t, takeover_state_name(st.state),
                   (double)st.alpha, (double)st.alpha_throttle,
                   (double)nav_guard_crosstrack(&nav, &pl.st),
                   (double)nav.integral, (double)u_out.roll,
                   (double)pl.st.alt, (double)u_out.throttle);
        }
    }

    printf("  підсумок: |I|max=%.1f°  найбільший відхід після віддачі=%.1f м\n",
           (double)max_abs_i, (double)max_xte_after);
    printf("  швидкість зміни команди крену: змішувач %.0f °/с, "
           "наївний мультиплексор %.0f °/с\n",
           (double)max_rate_blend, (double)max_rate_mux);
}

int main(void) {
    const scenario_t scenarios[] = {
        { "Обхід троса: захисти увімкнено",        true,  -1.0f, -1.0f },
        { "Те саме без анти-віндапу й синхронізації уставки", false, -1.0f, -1.0f },
        { "Втрата RC посеред ручного маневру",     true,   2.8f, -1.0f },
        { "Геозона забирає керування в пілота",    true,  -1.0f,  2.8f }
    };

    for (unsigned i = 0; i < sizeof(scenarios) / sizeof(scenarios[0]); ++i) {
        run_scenario(&scenarios[i]);
    }
    return 0;
}
