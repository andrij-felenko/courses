#include <stdio.h>
#include <math.h>
#include "supervisor.h"

/* Прогін фільтра на найпростішій моделі ровера. Модель тут лише для того,
 * щоб згодувати супервізору правдоподібний потік давачів: приводи вважаємо
 * ідеальними, тобто фактична швидкість дорівнює виданій уставці. */

#define TICK_HZ       200.0f
#define DT            (1.0f / TICK_HZ)
#define PLAN_PERIOD_S 0.05f   /* планувальник — 20 Гц */
#define WALL_X_M      14.0f   /* стіна попереду, м від старту */
#define SIM_END_S     9.6f
#define TILT_LIMIT    0.52f   /* ~30° перекидання */

static bool lidar_blind(float t)    { return t >= 1.0f && t < 1.3f; }
static bool planner_frozen(float t) { return t >= 4.5f && t < 5.5f; }
static bool estop_pressed(float t)  { return t >= 9.0f; }

/* Просідання напруги під струмом розгону, потім глибокий розряд */
static float battery_voltage(float t)
{
    if (t < 3.2f) return 16.0f;
    if (t < 4.5f) return 16.0f - (t - 3.2f) * 1.4f;
    return 14.2f;
}

/* Виїзд на схил і повернення на рівне */
static float tilt_rad(float t)
{
    if (t < 2.2f || t >= 3.2f) return 0.05f;
    return 0.05f + (t - 2.2f) * 0.50f;
}

static void print_row(float t, const SensorEnvelope *sn, float wish_vx,
                      const CommandVector *safe, SafetyStatus st)
{
    char dist_text[16];
    if (sn->obstacle_dist_valid) {
        snprintf(dist_text, sizeof dist_text, "%6.2f", (double)sn->obstacle_dist_m);
    } else {
        snprintf(dist_text, sizeof dist_text, "   ---");
    }
    printf("%6.3f  %s  %5.2f  %5.3f | %6.2f  %6.2f  %6.2f | %s\n",
           (double)t, dist_text, (double)sn->battery_voltage,
           (double)sn->current_tilt_rad, (double)wish_vx,
           (double)safe->vx, (double)safe->yaw_rate,
           bb_status_name((uint8_t)st));
}

static void dump_blackbox(const BlackBox *log)
{
    printf("\n=== Чорна скринька: %u епізодів (затерто %u) ===\n",
           blackbox_size(log), log->dropped);
    for (uint32_t i = 0; i < blackbox_size(log); ++i) {
        const BbEntry *e = blackbox_at(log, i);
        printf("  %6.3f…%6.3f с  %-11s %-16s знач=%8.3f  тактів=%u\n",
               (double)e->t_begin, (double)e->t_end,
               bb_status_name(e->status), bb_reason_name(e->reason),
               (double)e->value, e->repeats);
    }
}

int main(void)
{
    SafetySupervisor sup;
    safety_init(&sup);

    float t = 0.0f;
    float rover_x = 0.0f;
    float next_plan = 0.0f;
    float next_report = 0.0f;
    SafetyStatus prev_status = SAFETY_PASS_THROUGH;
    bool first = true;

    printf("  час    dist   вольт  крен  |  vx_кмд  vx_безп  yaw_бзп | статус\n");

    while (t < SIM_END_S) {
        /* Повільний потік: «жадібний» планувальник просить повний хід */
        if (!planner_frozen(t) && t >= next_plan) {
            const CommandVector wish = { 2.2f, 0.0f, 0.6f };
            if (!safety_submit_plan(&sup, &wish)) {
                printf("!! уставку відкинуто: нечислове значення\n");
            }
            next_plan = t + PLAN_PERIOD_S;
        }

        const float true_dist = WALL_X_M - rover_x;
        const SensorEnvelope sensors = {
            .obstacle_dist_m     = lidar_blind(t) ? NAN : true_dist,
            .obstacle_dist_valid = !lidar_blind(t),
            .battery_voltage     = battery_voltage(t),
            .current_tilt_rad    = tilt_rad(t),
            .max_tilt_limit      = TILT_LIMIT,
            .emergency_switch    = estop_pressed(t)
        };

        CommandVector safe_cmd;
        const SafetyStatus status = safety_step(&sup, &sensors, DT, &safe_cmd);

        /* Ідеальні приводи: що видали, те й поїхало */
        rover_x += safe_cmd.vx * DT;

        if (first || status != prev_status || t >= next_report) {
            print_row(t, &sensors, sup.candidate.vx, &safe_cmd, status);
            next_report = t + 0.5f;
            first = false;
        }
        prev_status = status;
        t += DT;
    }

    printf("\nпройдено %.2f м, до стіни лишилось %.2f м\n",
           (double)rover_x, (double)(WALL_X_M - rover_x));
    dump_blackbox(&sup.log);
    return 0;
}
