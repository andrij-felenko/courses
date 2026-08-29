/* Стенд автомата польотних режимів: замість борту — найпростіша модель
   вертикальної та горизонтальної динаміки, замість пульта й наземної станції —
   сценарій. Автомат при цьому справжній: той самий код, що йде в прошивку.

   Збірка: cc -std=c11 -O2 -o fsm *.c -lm   */

#include <math.h>
#include <stdio.h>
#include <string.h>

#include "fsm.h"

#define SIM_TICK_MS 20u
#define SIM_DT_S    0.02f

typedef struct {
    fm_state_t   st;
    fm_fsm_t     fsm;
    fm_params_t  params;
    fm_mission_t mission;

    bool  rc_alive;
    bool  gcs_alive;
    bool  guided_alive;
    float hover;          /* справжня тяга висіння моделі */
} sim_t;

/* ── вихідний канал: те, що на борту пішло б у телеметрію ─────────────────── */

static void on_ack(void *ctx, uint16_t command, uint8_t result)
{
    const fm_state_t *st = (const fm_state_t *)ctx;
    static const char *const names[] = {
        "ACCEPTED", "TEMPORARILY_REJECTED", "DENIED", "UNSUPPORTED", "FAILED"
    };
    const char *name = (result < (sizeof(names) / sizeof(names[0]))) ? names[result] : "?";

    printf("  [%6.2f] COMMAND_ACK cmd=%u -> %s\n",
           (double)st->now_ms / 1000.0, (unsigned)command, name);
}

static void on_text(void *ctx, uint8_t severity, const char *text)
{
    const fm_state_t *st = (const fm_state_t *)ctx;

    printf("  [%6.2f] STATUSTEXT(sev=%u): %s\n",
           (double)st->now_ms / 1000.0, (unsigned)severity, text);
}

static void on_tone(void *ctx, fm_tone_t tone)
{
    const fm_state_t *st = (const fm_state_t *)ctx;
    static const char *const names[] = {
        "-", "accepted", "rejected", "throttle lock", "failsafe", "disarm"
    };

    if (tone == FM_TONE_NONE) {
        return;
    }
    printf("  [%6.2f] BUZZER: %s\n", (double)st->now_ms / 1000.0, names[tone]);
}

/* ── модель апарата ──────────────────────────────────────────────────────── */

static void plant_step(sim_t *sim, float throttle, float dt)
{
    fm_state_t *st = &sim->st;

    const bool grounded = (st->altitude_rel_m <= 0.001f) && (throttle < sim->hover);

    /* Вертикаль: різниця тяги й висіння дає прискорення, опір гасить швидкість. */
    float accel = grounded ? 0.0f
                           : (throttle - sim->hover) * 18.0f - 0.8f * st->vertical_velocity;
    float vz    = st->vertical_velocity + accel * dt;
    float alt   = st->altitude_rel_m + vz * dt;

    if (alt <= 0.0f) {
        alt = 0.0f;
        if (vz < 0.0f) {
            vz    = 0.0f;
            accel = 0.0f;   /* реакція опори: удару немає, апарат стоїть */
        }
    }

    st->vertical_velocity = vz;
    st->altitude_rel_m    = alt;
    st->motor_output      = throttle;
    /* Дисперсія вертикального прискорення: на землі рама тиха, у польоті — ні. */
    st->accel_z_variance  = grounded ? 0.03f : (fabsf(accel) * 0.05f + 0.05f);

    /* Горизонталь: команда нахилу перетворюється на прискорення (tan ~ 0.017/град). */
    const float acc_n = 0.171f * sim->fsm.ctl.tilt_north_deg;
    const float acc_e = 0.171f * sim->fsm.ctl.tilt_east_deg;

    st->vel_north_ms += (acc_n - 0.35f * st->vel_north_ms) * dt;
    st->vel_east_ms  += (acc_e - 0.35f * st->vel_east_ms) * dt;

    /* 1 метр по широті — приблизно 1e7/111320 одиниць координати. */
    st->lat_1e7 += (int32_t)lrintf(st->vel_north_ms * dt * 89.83f);
    st->lon_1e7 += (int32_t)lrintf(st->vel_east_ms * dt * 89.83f
                                   / cosf(0.017453f * (float)st->lat_1e7 * 1e-7f));
}

static void sim_run(sim_t *sim, uint32_t duration_ms)
{
    const uint32_t ticks = duration_ms / SIM_TICK_MS;

    for (uint32_t i = 0; i < ticks; ++i) {
        sim->st.now_ms += SIM_TICK_MS;

        if (sim->rc_alive) {
            sim->st.rc_last_frame_ms = sim->st.now_ms;
        }
        if (sim->gcs_alive) {
            sim->st.gcs_last_heartbeat_ms = sim->st.now_ms;
        }
        if (sim->guided_alive) {
            sim->st.guided_setpoint_ms = sim->st.now_ms;
        }

        fm_fsm_update(&sim->fsm, &sim->st);

        /* Силовий каскад повідомляє автоматові, чи справді генеруються сигнали. */
        sim->st.armed = fm_fsm_armed(&sim->fsm);
        plant_step(sim, fm_fsm_throttle(&sim->fsm), SIM_DT_S);
    }
}

static void show(const sim_t *sim, const char *tag)
{
    printf("  [%6.2f] %-22s mode=%-9s prio=%-16s thr=%.2f alt=%5.1f vz=%+5.2f land=%s\n",
           (double)sim->st.now_ms / 1000.0, tag,
           fm_mode_name(fm_fsm_mode(&sim->fsm)),
           fm_priority_name(fm_fsm_priority(&sim->fsm)),
           (double)fm_fsm_throttle(&sim->fsm),
           (double)sim->st.altitude_rel_m,
           (double)sim->st.vertical_velocity,
           fm_land_phase_name(fm_fsm_land_phase(&sim->fsm)));
}

static void act(const char *title)
{
    printf("\n=== %s ===\n", title);
}

/* ── початкові умови ─────────────────────────────────────────────────────── */

static void sim_init(sim_t *sim)
{
    memset(sim, 0, sizeof(*sim));
    fm_params_default(&sim->params);
    sim->hover        = 0.50f;
    sim->rc_alive     = true;
    sim->gcs_alive    = true;
    sim->guided_alive = true;

    fm_state_t *st = &sim->st;

    st->now_ms               = 1000u;
    st->battery_cell_v       = 4.05f;
    st->battery_remaining    = 0.92f;
    st->gyro_healthy         = true;
    st->accel_healthy        = true;
    st->attitude_valid       = true;
    st->accel_z_variance     = 0.03f;
    st->baro_healthy         = true;
    st->rangefinder_healthy  = true;
    st->ekf_vert_pos_valid   = true;
    st->gnss_fix_type        = 3u;
    st->gnss_sats            = 14u;
    st->gnss_hdop            = 0.8f;
    st->gnss_vdop            = 1.2f;
    st->ekf_horiz_pos_valid  = true;
    st->ekf_innov_pos_norm   = 0.08f;
    st->ekf_innov_vel_norm   = 0.11f;
    st->compass_healthy      = true;
    st->compass_yaw_error_deg = 2.0f;
    st->lat_1e7              = 504500000;   /* умовна точка старту */
    st->lon_1e7              = 303000000;
    st->home_set             = true;
    st->home_lat_1e7         = st->lat_1e7;
    st->home_lon_1e7         = st->lon_1e7;
    st->stick_throttle       = 0.0f;
    st->hover_throttle       = sim->hover;
    st->rc_last_frame_ms     = st->now_ms;
    st->gcs_last_heartbeat_ms = st->now_ms;
    st->guided_setpoint_ms   = st->now_ms;
    st->mission              = &sim->mission;

    fm_mission_clear(&sim->mission);
}

static void load_mission(sim_t *sim, bool valid_crc)
{
    fm_mission_item_t wp;

    fm_mission_clear(&sim->mission);

    for (int i = 1; i <= 3; ++i) {
        memset(&wp, 0, sizeof(wp));
        wp.lat_1e7   = sim->st.home_lat_1e7 + i * 900;   /* ~100 м на крок */
        wp.lon_1e7   = sim->st.home_lon_1e7 + i * 400;
        wp.alt_rel_m = 25.0f;
        wp.command   = 16u;   /* MAV_CMD_NAV_WAYPOINT */
        (void)fm_mission_append(&sim->mission, &wp);
    }
    sim->mission.stored_crc = fm_mission_crc(&sim->mission);
    if (!valid_crc) {
        sim->mission.stored_crc ^= 0x00FFu;   /* зіпсований план */
    }
}

/* ── сценарій ────────────────────────────────────────────────────────────── */

int main(void)
{
    sim_t sim;

    sim_init(&sim);

    const fm_reporter_t reporter = {
        .command_ack = on_ack,
        .statustext  = on_text,
        .tone        = on_tone,
        .ctx         = &sim.st,
    };

    fm_fsm_init(&sim.fsm, &sim.params, &reporter, &sim.st);

    act("1. Озброєння і зліт у Stabilize");
    (void)fm_fsm_request_arm(&sim.fsm, &sim.st);
    sim.st.armed = true;
    sim.st.stick_throttle = 0.68f;          /* ручка вгору: набір висоти */
    sim_run(&sim, 4000u);
    show(&sim, "після набору");

    act("2. Перехід у AltHold: уставка й інтегратор фіксуються");
    sim.st.stick_throttle = 0.50f;          /* ручка в мертву зону */
    (void)fm_fsm_request_mode(&sim.fsm, FM_MODE_ALT_HOLD, FM_PRIO_ROUTINE, &sim.st);
    sim_run(&sim, 3000u);
    show(&sim, "утримання висоти");

    act("3. Перехід у PosHold, потім у Auto з валідним планом");
    (void)fm_fsm_request_mode(&sim.fsm, FM_MODE_POS_HOLD, FM_PRIO_ROUTINE, &sim.st);
    sim_run(&sim, 1000u);
    load_mission(&sim, false);
    printf("  -- план із зіпсованою контрольною сумою:\n");
    (void)fm_fsm_request_mode(&sim.fsm, FM_MODE_AUTO, FM_PRIO_ROUTINE, &sim.st);
    load_mission(&sim, true);
    printf("  -- той самий план із правильною сумою:\n");
    (void)fm_fsm_request_mode(&sim.fsm, FM_MODE_AUTO, FM_PRIO_ROUTINE, &sim.st);
    sim_run(&sim, 2000u);
    show(&sim, "автономна місія");

    act("4. Стрибок газу: спроба перейти в Manual зі скинутою ручкою");
    sim.st.stick_throttle = 0.0f;
    (void)fm_fsm_request_mode(&sim.fsm, FM_MODE_MANUAL, FM_PRIO_ROUTINE, &sim.st);
    show(&sim, "після відмови");
    printf("  -- пілот зводить ручку з поточною тягою:\n");
    sim.st.stick_throttle = fm_fsm_throttle(&sim.fsm);
    (void)fm_fsm_request_mode(&sim.fsm, FM_MODE_STABILIZE, FM_PRIO_ROUTINE, &sim.st);
    sim_run(&sim, 500u);
    show(&sim, "після узгодження");

    act("5. Роззброєння в повітрі: комбінація стіків ігнорується");
    sim.st.stick_disarm_combo = true;
    sim_run(&sim, 100u);
    sim.st.stick_disarm_combo = false;
    show(&sim, "мотори працюють");

    act("6. Втрата супутників у польоті: каскадна деградація");
    (void)fm_fsm_request_mode(&sim.fsm, FM_MODE_POS_HOLD, FM_PRIO_ROUTINE, &sim.st);
    sim_run(&sim, 500u);
    show(&sim, "утримання точки");
    sim.st.gnss_sats           = 3u;
    sim.st.gnss_hdop           = 3.4f;
    sim.st.ekf_innov_pos_norm  = 1.4f;
    sim.st.ekf_horiz_pos_valid = false;
    sim_run(&sim, 500u);
    show(&sim, "після збою GNSS");

    act("7. Гістерезис: повернення нагору лише після витриманої умови");
    sim.st.gnss_sats           = 12u;
    sim.st.gnss_hdop           = 0.9f;
    sim.st.ekf_innov_pos_norm  = 0.10f;
    sim.st.ekf_horiz_pos_valid = true;
    printf("  -- запит одразу після відновлення сигналу:\n");
    (void)fm_fsm_request_mode(&sim.fsm, FM_MODE_POS_HOLD, FM_PRIO_ROUTINE, &sim.st);
    sim_run(&sim, 2500u);
    printf("  -- запит після витримки:\n");
    (void)fm_fsm_request_mode(&sim.fsm, FM_MODE_POS_HOLD, FM_PRIO_ROUTINE, &sim.st);
    show(&sim, "повернення в PosHold");

    act("8. Втрата пульта: витіснення рівня 3");
    sim.rc_alive = false;
    sim_run(&sim, 2000u);
    show(&sim, "аварійне повернення");
    printf("  -- пілот намагається перемкнутися, поки лінк мертвий:\n");
    (void)fm_fsm_request_mode(&sim.fsm, FM_MODE_AUTO, FM_PRIO_ROUTINE, &sim.st);

    act("9. Критичний розряд: витіснення рівня 4 блокує все");
    sim.rc_alive = true;
    sim.st.battery_cell_v    = 3.22f;
    sim.st.battery_remaining = 0.07f;
    sim_run(&sim, 200u);
    show(&sim, "примусова посадка");
    printf("  -- спроба повернутися в місію під критичним failsafe:\n");
    (void)fm_fsm_request_mode(&sim.fsm, FM_MODE_AUTO, FM_PRIO_ROUTINE, &sim.st);

    act("10. Детектор посадки: контакт, витримка, роззброєння");
    sim_run(&sim, 60000u);
    show(&sim, "цикл завершено");

    act("11. Апаратна відсічка перекриває навіть штатний запит");
    sim.st.kill_switch = true;
    sim_run(&sim, 100u);
    show(&sim, "після відсічки");
    (void)fm_fsm_request_mode(&sim.fsm, FM_MODE_STABILIZE, FM_PRIO_ROUTINE, &sim.st);
    (void)fm_fsm_request_arm(&sim.fsm, &sim.st);

    printf("\nсценарій завершено\n");
    return 0;
}
