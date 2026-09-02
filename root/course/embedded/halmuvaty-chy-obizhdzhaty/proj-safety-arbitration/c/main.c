/* Демонстраційний стенд арбітра: 100-герцовий цикл, модель апарата,
   планувальник на 5 Гц із вікном мовчання і далекомір із шумом та збоєм.
   На реальному борту тіло циклу висить на перериванні таймера. */

#include <math.h>
#include <stdint.h>
#include <stdio.h>

#include "safety_arbiter.h"

#define SIM_TICKS            600
#define CRUISE_MPS           6.0f
#define VEHICLE_YAW_RAD      0.60f   /* курс апарата відносно odom, рад */
#define SENSOR_MAX_RANGE_M   30.0f
#define SENSOR_NOISE_M       0.05f
#define OBSTACLE_X_M         25.0f
#define OBSTACLE_Y_M         0.0f
#define OBSTACLE_RADIUS_M    0.50f
#define PLANNER_EVERY_TICKS  20      /* планувальник 5 Гц */
#define PLANNER_MUTE_FROM    60
#define PLANNER_MUTE_TO      120
#define SENSOR_FAULT_FROM    180
#define SENSOR_FAULT_TO      186
#define PI_KP                8.0f
#define PI_KI                4.0f

/* Поздовжній ПІ-регулятор швидкості — саме він страждає від windup. */
typedef struct {
    float integral;
} SpeedPi;

static float speed_pi_step(SpeedPi *pi, float target, float actual,
                           bool reset_integral, float a_max)
{
    if (reset_integral) {
        /* Пастка зі статті: на вході в ESTOP інтеграл обнуляється. Інакше поки
           апарат стоїть, сума помилки росте, і на виході мотори смикне. */
        pi->integral = 0.0f;
    }
    const float err = target - actual;
    pi->integral += PI_KI * err * SAFETY_DT_SEC;
    if (pi->integral >  a_max) pi->integral =  a_max;
    if (pi->integral < -a_max) pi->integral = -a_max;

    float a = PI_KP * err + pi->integral;
    if (a >  a_max) a =  a_max;
    if (a < -a_max) a = -a_max;
    return a;
}

/* Детермінований шум давача: демо має відтворюватися від запуску до запуску. */
static uint32_t rng_state = 20260830u;

static float sensor_noise(void)
{
    rng_state = rng_state * 1664525u + 1013904223u;
    const float unit = (float)((rng_state >> 8) & 0xFFFFu) / 65535.0f;
    return (unit * 2.0f - 1.0f) * SENSOR_NOISE_M;
}

int main(void)
{
    const SafetyParams params = {
        .max_accel      = 2.5f,
        .reaction_time  = 0.05f,
        .planner_period = 0.20f,
        .stop_margin    = 0.40f,
        .warn_buffer    = 0.80f
    };

    SafetyArbiter arb;
    if (!safety_arbiter_init(&arb, &params)) {
        fprintf(stderr, "safety_arbiter_init: неприйнятні параметри\n");
        return 1;
    }

    Vec2 pos = { 0.0f, 0.0f };            /* положення в odom */
    Vec2 vel = { CRUISE_MPS, 0.0f };      /* швидкість в odom */
    Vec2 heading = { 1.0f, 0.0f };        /* напрямок, який тримаємо при нульовій уставці */
    SpeedPi pi = { 0.0f };
    SafetyZone prev_zone = ZONE_OBSERVATION;

    printf("тік   t,с   зазор  R_stop R_warn  зона        alpha  |v_cmd|  швидк.  прапорці\n");

    for (int tick = 0; tick < SIM_TICKS; ++tick) {
        /* --- Планувальник: 5 Гц у глобальному фреймі, з вікном мовчання --- */
        const Vec2 plan_odom = { CRUISE_MPS, 0.0f };
        const Vec2 plan_body = safety_odom_to_body(plan_odom, VEHICLE_YAW_RAD);
        const bool muted = (tick >= PLANNER_MUTE_FROM && tick <= PLANNER_MUTE_TO);
        if (!muted && (tick % PLANNER_EVERY_TICKS) == 0) {
            safety_arbiter_planner_heartbeat(&arb);
        }

        /* --- Далекомір --- */
        const Vec2 rel_odom = { OBSTACLE_X_M - pos.x, OBSTACLE_Y_M - pos.y };
        float gap = sqrtf(rel_odom.x * rel_odom.x + rel_odom.y * rel_odom.y) - OBSTACLE_RADIUS_M;
        if (gap < 0.0f) {
            gap = 0.0f;
        }
        const bool range_valid = !(tick >= SENSOR_FAULT_FROM && tick <= SENSOR_FAULT_TO);
        /* Немає відлуння — значить, у межах дальності чисто; це не те саме,
           що збій давача, і плутати їх не можна. */
        float measured = (gap > SENSOR_MAX_RANGE_M) ? SENSOR_MAX_RANGE_M : gap + sensor_noise();
        if (measured < 0.0f) {
            measured = 0.0f;
        }

        /* --- Рефлекс: обхід перешкоди по лівій нормалі, у body-фреймі --- */
        const Vec2 rel_body = safety_odom_to_body(rel_odom, VEHICLE_YAW_RAD);
        const float rel_len = sqrtf(rel_body.x * rel_body.x + rel_body.y * rel_body.y);
        Vec2 react_body = { 0.0f, 0.0f };
        if (rel_len > 1e-3f) {
            /* Сторона обходу фіксована навмисно: коли перешкода строго по курсу,
               вибір боку — підкидання монети, а рефлекс не має права
               передумувати щотакту, інакше апарат затанцює на місці. */
            react_body.x = -rel_body.y / rel_len * CRUISE_MPS;
            react_body.y =  rel_body.x / rel_len * CRUISE_MPS;
        }

        /* --- Такт арбітра --- */
        const float speed = sqrtf(vel.x * vel.x + vel.y * vel.y);
        const SafetyInput in = {
            .v_plan        = plan_body,
            .v_react       = react_body,
            .min_range_m   = measured,
            .range_valid   = range_valid,
            .current_speed = speed
        };
        const SafetyOutput out = safety_arbiter_update(&arb, &in);

        /* --- Виконавчий рівень: уставка з body назад в odom --- */
        const Vec2 cmd_odom = safety_odom_to_body(out.v_cmd, -VEHICLE_YAW_RAD);
        const float cmd_len = sqrtf(cmd_odom.x * cmd_odom.x + cmd_odom.y * cmd_odom.y);
        if (cmd_len > 1e-3f) {
            heading.x = cmd_odom.x / cmd_len;
            heading.y = cmd_odom.y / cmd_len;
        }
        const float accel = speed_pi_step(&pi, cmd_len, speed, out.override_active,
                                          params.max_accel);
        float new_speed = speed + accel * SAFETY_DT_SEC;
        if (new_speed < 0.0f) {
            new_speed = 0.0f;
        }
        /* Модель голономна: справжній ровер довертався б кермом,
           тут же напрямок міняється миттєво — для демонстрації арбітражу цього досить. */
        vel.x = heading.x * new_speed;
        vel.y = heading.y * new_speed;
        pos.x += vel.x * SAFETY_DT_SEC;
        pos.y += vel.y * SAFETY_DT_SEC;

        if ((tick % 10) == 0 || out.zone != prev_zone) {
            printf("%4d %5.2f %7.2f %6.2f %6.2f  %-11s %5.2f %8.2f %7.2f  %s%s%s\n",
                   tick, (float)tick * SAFETY_DT_SEC, gap, out.r_stop, out.r_warn,
                   safety_zone_name(out.zone), out.alpha, cmd_len, new_speed,
                   out.override_active ? "OVERRIDE " : "",
                   out.planner_timed_out ? "PLAN-STALE " : "",
                   range_valid ? "" : "SENSOR-FAULT");
        }
        prev_zone = out.zone;
    }

    printf("\nфініш: x=%.2f м, y=%.2f м, швидкість %.2f м/с\n",
           pos.x, pos.y, sqrtf(vel.x * vel.x + vel.y * vel.y));
    return 0;
}
