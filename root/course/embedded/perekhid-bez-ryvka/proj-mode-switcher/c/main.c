/* Стенд диспетчера режимів. Збірка: cc -std=c11 -O2 *.c -lm -o modes
   Три сценарії: перемикання режимів у польоті, підхоплення ручки і
   аварійний перехід при втраті зв'язку. */

#include <math.h>
#include <stdio.h>
#include <string.h>

#include "altitude.h"
#include "flight_manager.h"
#include "rc_input.h"

#define DT             0.02f   /* 50 Гц */
#define HOVER_THROTTLE 0.56f

/* Груба модель апарата: надлишок тяги над зависанням дає прискорення,
   опір повітря його з'їдає. Повертає вертикальне прискорення. */
static float plant_step(float *alt, float *climb, float throttle, float dt)
{
    const float acc = (throttle - HOVER_THROTTLE) * 20.0f - 0.8f * (*climb);
    *climb += acc * dt;
    *alt   += (*climb) * dt;
    return acc;
}

static uint16_t raw_from_unit(float unit)
{
    const float us = 988.0f + unit * 1024.0f;
    return (uint16_t)((us - 881.0f) / 0.62477f + 0.5f);
}

static void build_tx_frame(uint8_t frame[RC_FRAME_SIZE], float throttle,
                           uint16_t aux1_raw, bool override_on)
{
    rc_channels_t tx;
    for (int i = 0; i < RC_CHANNEL_COUNT; ++i) tx.ch[i] = 992;
    tx.ch[2] = raw_from_unit(throttle);            /* газ */
    tx.ch[4] = aux1_raw;                           /* AUX1 — режим */
    tx.ch[5] = override_on ? 1792 : 191;           /* AUX2 — силове перехоплення */
    rc_frame_build(&tx, frame);
}

/* ── Сценарій 1: два перемикання в польоті ───────────────────────────── */
static void scenario_mode_switch(void)
{
    printf("=== Сценарій 1: MANUAL -> ALT_HOLD -> AUTO_MISSION ===\n");
    printf("Час[с] | Режим        | Висота[м] | Вихід    | Стрибок dU | Інтегратор\n");
    printf("---------------------------------------------------------------------\n");

    float alt_true = 42.0f, climb_true = 0.0f, acc_up = 0.0f;

    flight_manager_t mgr;
    fm_init(&mgr, 42.0f, 210.0f);
    fm_set_armed(&mgr, true);
    fm_set_mission_target(&mgr, 80.0f);

    alt_filter_t fus;
    alt_filter_init(&fus, 1.2f, 0.6f);

    rc_link_t link;
    rc_link_init(&link, 0);

    int sw_pos = 0;
    float prev_out = HOVER_THROTTLE;

    for (int step = 0; step <= 750; ++step) {
        const uint32_t now_ms = (uint32_t)step * 20u;
        const float t = (float)step * DT;

        /* Пульт: газ 56 %, тумблер AUX1 переходить у середнє положення на
           5-й секунді і у верхнє — на 10-й. */
        uint16_t aux1 = 191;
        if (step >= 500)      aux1 = 1792;
        else if (step >= 250) aux1 = 992;

        uint8_t frame[RC_FRAME_SIZE];
        build_tx_frame(frame, HOVER_THROTTLE, aux1, false);
        rc_link_feed(&link, frame, sizeof frame, now_ms);
        rc_link_tick(&link, now_ms);

        /* Фузія висоти */
        alt_filter_update(&fus, alt_true, acc_up, DT);
        const vehicle_state_t st = {
            .alt_m = alt_filter_altitude(&fus),
            .climb_mps = alt_filter_climb(&fus),
            .heading_deg = 90.0f
        };

        /* Тумблер → бажаний режим */
        sw_pos = rc_switch_pos(rc_channel_us(link.ch.ch[4]), sw_pos);
        const flight_mode_t want = (flight_mode_t)sw_pos;
        if (want != mgr.mode) {
            const flight_mode_t from = mgr.mode;
            if (fm_request_mode(&mgr, want, &st))
                printf(">>> [t=%.1fs] ПЕРЕМИКАННЯ: %s -> %s <<<\n",
                       (double)t, fm_mode_name(from), fm_mode_name(want));
            else
                printf(">>> [t=%.1fs] ВІДМОВА: захоплення неможливе <<<\n", (double)t);
        }

        const pilot_input_t rc = {
            .throttle = rc_channel_unit(link.ch.ch[2]),
            .mode_pos = sw_pos,
            .force_override = rc_channel_us(link.ch.ch[5]) > 1700.0f,
            .valid = !link.failsafe
        };
        const fm_output_t out = fm_step(&mgr, &rc, &st, DT);
        const float du = fabsf(out.throttle - prev_out);

        if (step == 249 || step == 250 || step == 251 ||
            step == 499 || step == 500 || step == 501) {
            const pid_t *active = (mgr.mode == MODE_AUTO_MISSION) ? &mgr.mission_pid
                                                                  : &mgr.alt_pid;
            printf("%5.2f  | %-12s | %8.2f  | %8.6f | %10.6f | %9.6f\n",
                   (double)t, fm_mode_name(mgr.mode), (double)st.alt_m,
                   (double)out.throttle, (double)du,
                   (double)(mgr.mode == MODE_MANUAL ? 0.0f : pid_integral(active)));
        }

        acc_up = plant_step(&alt_true, &climb_true, out.throttle, DT);
        prev_out = out.throttle;
    }

    printf("Кадрів прийнято: %u, помилок CRC: %u, зауважень до захоплення: %u\n\n",
           link.frames_ok, link.crc_errors, mgr.handover_warnings);
}

/* ── Сценарій 2: підхоплення ручки при поверненні в ручний режим ─────── */
static void scenario_stick_matching(void)
{
    printf("=== Сценарій 2: Stick Matching при ALT_HOLD -> MANUAL ===\n");

    flight_manager_t mgr;
    fm_init(&mgr, 40.0f, 0.0f);
    fm_set_armed(&mgr, true);

    vehicle_state_t st = { .alt_m = 40.0f, .climb_mps = 0.0f, .heading_deg = 0.0f };
    pilot_input_t rc = { .throttle = HOVER_THROTTLE, .mode_pos = 0,
                         .force_override = false, .valid = true };

    /* Секунда ручного польоту, щоб на приводі стояло 56 % */
    for (int i = 0; i < 50; ++i) fm_step(&mgr, &rc, &st, DT);
    fm_request_mode(&mgr, MODE_ALT_HOLD, &st);
    for (int i = 0; i < 50; ++i) fm_step(&mgr, &rc, &st, DT);

    /* Пілот, поки летіли в автоматі, зсунув ручку майже до нуля */
    rc.throttle = 0.20f;
    fm_request_mode(&mgr, MODE_MANUAL, &st);
    printf("Ручка %.2f, тяга на приводі %.2f — керування утримано\n",
           (double)rc.throttle, (double)mgr.u_hold);

    printf("Крок | Ручка | Вихід | Підказка\n");
    for (int i = 0; i < 60; ++i) {
        if (i >= 5 && rc.throttle < 1.0f) rc.throttle += 0.01f;  /* пілот піднімає */
        const fm_output_t out = fm_step(&mgr, &rc, &st, DT);
        if (i % 5 == 0 || out.hint == HINT_STICK_MATCHED)
            printf("%4d | %5.2f | %5.2f | %s\n", i, (double)rc.throttle,
                   (double)out.throttle, fm_hint_text(out.hint));
        if (out.hint == HINT_STICK_MATCHED) break;
    }

    /* Те саме, але пілот тисне силове перехоплення — тяга падає одразу */
    fm_request_mode(&mgr, MODE_ALT_HOLD, &st);
    fm_step(&mgr, &rc, &st, DT);
    rc.throttle = 0.20f;
    fm_request_mode(&mgr, MODE_MANUAL, &st);
    rc.force_override = true;
    const fm_output_t forced = fm_step(&mgr, &rc, &st, DT);
    printf("Force Override: ручка %.2f -> вихід %.2f (%s)\n\n",
           (double)rc.throttle, (double)forced.throttle, fm_hint_text(forced.hint));
}

/* ── Сценарій 3: аварійний перехід при втраті зв'язку ────────────────── */
static void scenario_failsafe(void)
{
    printf("=== Сценарій 3: Failsafe -> повернення на базу ===\n");

    float alt_true = 60.0f, climb_true = 0.0f, acc_up = 0.0f;

    flight_manager_t mgr;
    fm_init(&mgr, 40.0f, 210.0f);   /* база: висота 40 м, азимут 210° */
    fm_set_armed(&mgr, true);

    alt_filter_t fus;
    alt_filter_init(&fus, 1.2f, 0.6f);

    rc_link_t link;
    rc_link_init(&link, 0);

    float heading = 30.0f;
    float prev_out = HOVER_THROTTLE;
    bool announced = false;

    for (int step = 0; step <= 600; ++step) {
        const uint32_t now_ms = (uint32_t)step * 20u;
        const float t = (float)step * DT;

        /* Після 6-ї секунди приймач мовчить: кадрів більше не подаємо. */
        if (step < 300) {
            uint8_t frame[RC_FRAME_SIZE];
            build_tx_frame(frame, HOVER_THROTTLE, 992, false);  /* AUX1 = ALT_HOLD */
            rc_link_feed(&link, frame, sizeof frame, now_ms);
        }
        const bool lost = rc_link_tick(&link, now_ms);

        /* На 2-й секунді барометр видає викид — фільтр мусить його відкинути. */
        const float baro = (step == 100) ? alt_true + 60.0f : alt_true;
        alt_filter_update(&fus, baro, acc_up, DT);

        const vehicle_state_t st = {
            .alt_m = alt_filter_altitude(&fus),
            .climb_mps = alt_filter_climb(&fus),
            .heading_deg = heading
        };

        if (step == 1) fm_request_mode(&mgr, MODE_ALT_HOLD, &st);

        if (lost && !mgr.failsafe) {
            fm_enter_failsafe(&mgr, &st);
            printf(">>> [t=%.2fs] FAILSAFE: %u мс без кадру -> повернення на базу\n",
                   (double)t, (unsigned)(now_ms - link.last_ok_ms));
        }

        const pilot_input_t rc = {
            .throttle = rc_channel_unit(link.ch.ch[2]),
            .mode_pos = 1,
            .force_override = false,
            .valid = !link.failsafe
        };
        const fm_output_t out = fm_step(&mgr, &rc, &st, DT);

        if (lost && !announced) {
            printf("Стрибок тяги на переході: dU = %.6f\n",
                   (double)fabsf(out.throttle - prev_out));
            announced = true;
        }
        if (step % 50 == 0 && step >= 300)
            printf("t=%5.2f | курс %6.1f° -> ціль %.0f° | висота %6.2f | тяга %.4f\n",
                   (double)t, (double)out.heading_cmd_deg, 210.0,
                   (double)st.alt_m, (double)out.throttle);

        heading = out.heading_cmd_deg;   /* борт іде за командою курсу */
        acc_up = plant_step(&alt_true, &climb_true, out.throttle, DT);
        prev_out = out.throttle;
    }

    printf("Відкинуто викидів барометра: %u\n", fus.rejected);
}

int main(void)
{
    scenario_mode_switch();
    scenario_stick_matching();
    scenario_failsafe();
    return 0;
}
