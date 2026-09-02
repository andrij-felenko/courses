#define _POSIX_C_SOURCE 200809L

#include "link.h"
#include "setpoint.h"

#include <errno.h>
#include <math.h>
#include <stdio.h>
#include <time.h>

#define STREAM_HZ          20                       /* PX4 роняє offboard, якщо потік рідший за 2 Гц */
#define TICK_US            (1000000u / STREAM_HZ)
#define PX4_MAIN_OFFBOARD  6
#define PX4_MAIN_AUTO      4
#define PX4_SUB_AUTO_LOITER 3

#define HOVER_THRUST   0.35f    /* типова тяга зависання коптера */
#define CLIMB_SPEED    1.5f
#define DESCEND_SPEED  0.7f
#define TURN_RATE      0.4f

typedef enum {
    PH_HOLD,      /* нульова швидкість із утриманням курсу */
    PH_CLIMB,     /* набір висоти за швидкістю */
    PH_TRANSIT,   /* політ у точку з випереджувальною швидкістю */
    PH_STATION,   /* утримання точки */
    PH_TURN,      /* обертання на місці за yaw_rate */
    PH_LEVEL,     /* горизонт кватерніоном + тяга */
    PH_RATE,      /* пряме керування кутовими швидкостями */
    PH_DESCEND
} phase_t;

static const char *phase_name(phase_t ph)
{
    switch (ph) {
    case PH_HOLD:    return "HOLD";
    case PH_CLIMB:   return "CLIMB";
    case PH_TRANSIT: return "TRANSIT";
    case PH_STATION: return "STATION";
    case PH_TURN:    return "TURN";
    case PH_LEVEL:   return "LEVEL";
    case PH_RATE:    return "RATE";
    case PH_DESCEND: return "DESCEND";
    }
    return "?";
}

static uint8_t px4_main_mode(uint32_t custom_mode)
{
    return (uint8_t)((custom_mode >> 16) & 0xFFu);
}

static void sleep_until(uint64_t deadline_us)
{
    const uint64_t t = now_us();
    if (t >= deadline_us) return;

    const uint64_t d = deadline_us - t;
    struct timespec ts;
    ts.tv_sec = (time_t)(d / 1000000u);
    ts.tv_nsec = (long)((d % 1000000u) * 1000u);
    while (nanosleep(&ts, &ts) < 0 && errno == EINTR) {
        /* сигнал перервав сон — досипаємо залишок */
    }
}

static int build_phase(link_t *l, phase_t ph, mavlink_message_t *out)
{
    const uint8_t s = l->sys_id, c = l->comp_id, t = l->target_sys;
    const float yaw = l->tlm.have_attitude ? l->tlm.yaw : 0.0f;
    float q[4];

    switch (ph) {
    case PH_HOLD:
        return sp_velocity_ned(out, s, c, t, 0, 0.0f, 0.0f, 0.0f, yaw);
    case PH_CLIMB:
        /* Вісь Z дивиться вниз, тому підйом — від'ємна vz. */
        return sp_velocity_ned(out, s, c, t, 0, 0.0f, 0.0f, -CLIMB_SPEED, yaw);
    case PH_TRANSIT:
        return sp_position_ff_velocity(out, s, c, t, 0,
                                       10.0f, 0.0f, -5.0f,
                                       1.5f, 0.0f, 0.0f, 0.0f);
    case PH_STATION:
        return sp_position_ned(out, s, c, t, 0, 10.0f, 0.0f, -5.0f, 0.0f);
    case PH_TURN:
        return sp_velocity_yawrate(out, s, c, t, 0, 0.0f, 0.0f, 0.0f, TURN_RATE);
    case PH_LEVEL:
        sp_quat_from_euler(0.0f, 0.0f, yaw, q);
        return sp_attitude_thrust(out, s, c, t, 0, q, HOVER_THRUST);
    case PH_RATE:
        return sp_body_rates(out, s, c, t, 0, 0.0f, 0.0f, TURN_RATE, HOVER_THRUST);
    case PH_DESCEND:
        return sp_velocity_ned(out, s, c, t, 0, 0.0f, 0.0f, DESCEND_SPEED, yaw);
    }
    return -1;
}

/* Один такт потоку: уставка, власний HEARTBEAT, розбір вхідної телеметрії. */
static int stream_tick(link_t *l, phase_t ph)
{
    mavlink_message_t msg;
    if (build_phase(l, ph, &msg) < 0) {
        fprintf(stderr, "уставку не сформовано: у полях нечислові значення\n");
        return -1;
    }
    link_send(l, &msg);          /* поодинокий пропуск не фатальний */
    link_heartbeat_tick(l);
    return link_poll(l, 0) < 0 ? -1 : 0;
}

static int check_health(link_t *l, int require_offboard)
{
    if (!l->tlm.have_heartbeat || now_us() - l->tlm.heartbeat_us > 1500000u) {
        fprintf(stderr, "HEARTBEAT автопілота зник — канал утрачено\n");
        return -1;
    }
    if (require_offboard && px4_main_mode(l->tlm.custom_mode) != PX4_MAIN_OFFBOARD) {
        fprintf(stderr, "автопілот покинув offboard (custom_mode=0x%08x): спрацював failsafe\n",
                l->tlm.custom_mode);
        return -1;
    }
    if (require_offboard && l->tlm.have_estimator &&
        (l->tlm.estimator_flags & ESTIMATOR_POS_HORIZ_REL) == 0) {
        fprintf(stderr, "EKF утратив горизонтальну позицію — позиційні уставки більше не тримаються\n");
        return -1;
    }
    return 0;
}

static int run_phase(link_t *l, phase_t ph, double seconds, int require_offboard)
{
    const uint64_t start = now_us();
    const uint64_t deadline = start + (uint64_t)(seconds * 1e6);
    uint64_t next = start;
    uint64_t last_report = start;

    while (now_us() < deadline) {
        if (stream_tick(l, ph) < 0) return -1;
        if (check_health(l, require_offboard) < 0) return -1;

        if (now_us() - last_report >= 1000000u) {
            last_report = now_us();
            printf("[%-7s] NED=(%6.2f %6.2f %6.2f) V=(%5.2f %5.2f %5.2f) yaw=%6.1f°\n",
                   phase_name(ph),
                   l->tlm.x, l->tlm.y, l->tlm.z,
                   l->tlm.vx, l->tlm.vy, l->tlm.vz,
                   l->tlm.yaw * 180.0f / (float)M_PI);
            fflush(stdout);
        }

        next += TICK_US;
        sleep_until(next);
    }
    return 0;
}

/* Чекає COMMAND_ACK, не перериваючи потоку уставок: пауза довша за 500 мс
   вибиває апарат з offboard просто під час очікування. */
static int wait_ack(link_t *l, uint16_t command, double timeout_s, uint8_t *result)
{
    const uint64_t deadline = now_us() + (uint64_t)(timeout_s * 1e6);
    uint64_t next = now_us();

    while (now_us() < deadline) {
        if (stream_tick(l, PH_HOLD) < 0) return -1;
        if (link_take_ack(l, command, result)) return 0;
        next += TICK_US;
        sleep_until(next);
    }
    return -1;
}

static int request_offboard(link_t *l)
{
    for (int attempt = 0; attempt < 3; ++attempt) {
        /* param1 — base_mode з увімкненим власним режимом, param2 — головний режим PX4.
           Для ArduPilot Copter тут стояло б COPTER_MODE_GUIDED = 4. */
        const float p[7] = { (float)MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
                             (float)PX4_MAIN_OFFBOARD, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f };
        if (link_command(l, MAV_CMD_DO_SET_MODE, p, (uint8_t)attempt) < 0) return -1;

        uint8_t result = 0;
        if (wait_ack(l, MAV_CMD_DO_SET_MODE, 1.0, &result) < 0) {
            fprintf(stderr, "COMMAND_ACK на DO_SET_MODE не прийшов (спроба %d)\n", attempt + 1);
            continue;
        }
        printf("DO_SET_MODE → %s (%u)\n", mav_result_name(result), result);

        if (result == MAV_RESULT_ACCEPTED) {
            /* Прийняти команду не означає ввійти в режим: підтвердженням
               є HEARTBEAT із потрібним custom_mode. */
            const uint64_t deadline = now_us() + 2000000u;
            uint64_t next = now_us();
            while (now_us() < deadline) {
                if (stream_tick(l, PH_HOLD) < 0) return -1;
                if (px4_main_mode(l->tlm.custom_mode) == PX4_MAIN_OFFBOARD) return 0;
                next += TICK_US;
                sleep_until(next);
            }
            fprintf(stderr, "режим не підтверджено в HEARTBEAT\n");
            return -1;
        }

        /* DENIED, UNSUPPORTED і FAILED повторювати марно: причина не в часі. */
        if (result != MAV_RESULT_TEMPORARILY_REJECTED) return -1;

        /* Потік уставок ще молодий або EKF не готовий — стрічимо далі й пробуємо ще. */
        if (run_phase(l, PH_HOLD, 1.0, 0) < 0) return -1;
    }
    fprintf(stderr, "offboard не увімкнувся після трьох спроб\n");
    return -1;
}

static int request_arm(link_t *l, int on)
{
    const float p[7] = { on ? 1.0f : 0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f };
    if (link_command(l, MAV_CMD_COMPONENT_ARM_DISARM, p, 0) < 0) return -1;

    uint8_t result = 0;
    if (wait_ack(l, MAV_CMD_COMPONENT_ARM_DISARM, 2.0, &result) < 0) {
        fprintf(stderr, "%s без підтвердження\n", on ? "ARM" : "DISARM");
        return -1;
    }
    printf("%s → %s (%u)\n", on ? "ARM" : "DISARM", mav_result_name(result), result);
    return result == MAV_RESULT_ACCEPTED ? 0 : -1;
}

/* Аварійний вихід: роззброювати апарат у повітрі не можна, тому віддаємо
   його автопілоту в режим утримання й припиняємо потік уставок. */
static void bail_to_hold(link_t *l)
{
    const float p[7] = { (float)MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
                         (float)PX4_MAIN_AUTO, (float)PX4_SUB_AUTO_LOITER,
                         0.0f, 0.0f, 0.0f, 0.0f };
    fprintf(stderr, "переводимо апарат у AUTO.LOITER\n");
    link_command(l, MAV_CMD_DO_SET_MODE, p, 0);
    link_poll(l, 200);
}

int main(void)
{
    link_t link;
    if (link_open(&link, 14540) < 0) return 1;

    printf("чекаємо HEARTBEAT автопілота на UDP :14540...\n");
    if (link_wait_heartbeat(&link, 10000) < 0) {
        fprintf(stderr, "автопілот мовчить\n");
        link_close(&link);
        return 1;
    }
    printf("автопілот sys=%u, custom_mode=0x%08x, armed=%d\n",
           link.target_sys, link.tlm.custom_mode,
           (link.tlm.base_mode & MAV_MODE_FLAG_SAFETY_ARMED) != 0);

    int rc = 1;

    /* Потік уставок мусить іти ДО перемикання режиму, інакше PX4 віддасть
       TEMPORARILY_REJECTED: він не вмикає offboard без свіжих цілей. */
    if (run_phase(&link, PH_HOLD, 1.0, 0) < 0) goto out;
    if (request_offboard(&link) < 0) goto out;
    if (request_arm(&link, 1) < 0) goto out;

    if (run_phase(&link, PH_CLIMB,   4.0, 1) < 0) goto hold;
    if (run_phase(&link, PH_TRANSIT, 6.0, 1) < 0) goto hold;
    if (run_phase(&link, PH_STATION, 4.0, 1) < 0) goto hold;
    if (run_phase(&link, PH_TURN,    3.0, 1) < 0) goto hold;
    if (run_phase(&link, PH_LEVEL,   2.0, 1) < 0) goto hold;
    if (run_phase(&link, PH_RATE,    2.0, 1) < 0) goto hold;
    /* Після кадрів #83 повертаємо керування швидкістю й лише тоді сідаємо. */
    if (run_phase(&link, PH_HOLD,    1.0, 1) < 0) goto hold;
    if (run_phase(&link, PH_DESCEND, 6.0, 1) < 0) goto hold;

    request_arm(&link, 0);
    rc = 0;
    goto out;

hold:
    bail_to_hold(&link);
out:
    link_close(&link);
    return rc;
}
