/* ============================================================================
   Демонстрація розділення наведення й регулювання на імітаторі мультиротора.

   Швидкий домен  — 1000 Гц: control_step + мікшер + фізика.
   Повільний домен —   50 Гц: guidance_step.
   Обмін — тільки через Seqlock-скриньку та один біт зворотного зв'язку.

   Сценарій: висіння на 5 м; бічний порив; низхідний потік із насиченням моторів;
   на 4-й секунді задача навігації "зависає" — спрацьовує сторож уставки.

   Збірка: cc -O2 -std=c11 *.c -lm -o guidance_demo
   ============================================================================ */

#include <math.h>
#include <stdio.h>

#include "control.h"
#include "guidance.h"
#include "linalg.h"
#include "mixer.h"
#include "setpoint.h"

#define DT_FAST        0.001f          /* 1000 Гц */
#define GUIDANCE_DIV   20              /* 50 Гц */
#define SIM_SECONDS    6.5f

/* Груба модель рами: нормована тяга/момент -> прискорення. */
#define A_MAX_THRUST   (2.0f * 9.80665f)   /* тягоозброєність 2:1 */
#define ALPHA_MAX_XY   600.0f              /* рад/с^2 на одиничний момент */
#define ALPHA_MAX_Z    120.0f
#define DRAG_LINEAR    0.25f               /* 1/с */
#define DRAG_ANGULAR   0.60f               /* 1/с */

typedef struct {
    Vec3 pos;    /* NED, м (z вниз: -5 = висота 5 м) */
    Vec3 vel;
    Quat q;
    Vec3 omega;  /* рад/с, зв'язана система */
} Vehicle;

static void vehicle_step(Vehicle *v, Vec3 torque, float thrust, Vec3 disturb_acc,
                         Vec3 disturb_alpha, float dt)
{
    /* Трансляція: тяга вздовж -Z корпуса, гравітація вниз, лінійний опір. */
    const Vec3 thrust_body = v3(0.0f, 0.0f, -thrust * A_MAX_THRUST);
    Vec3 acc = quat_rotate(v->q, thrust_body);
    acc = v3_add(acc, v3(0.0f, 0.0f, 9.80665f));
    acc = v3_add(acc, v3_scale(v->vel, -DRAG_LINEAR));
    acc = v3_add(acc, disturb_acc);

    v->vel = v3_add(v->vel, v3_scale(acc, dt));
    v->pos = v3_add(v->pos, v3_scale(v->vel, dt));

    /* Обертання: момент -> кутове прискорення, плюс аеродинамічний демпфер. */
    Vec3 alpha = v3(torque.x * ALPHA_MAX_XY,
                    torque.y * ALPHA_MAX_XY,
                    torque.z * ALPHA_MAX_Z);
    alpha = v3_add(alpha, v3_scale(v->omega, -DRAG_ANGULAR));
    alpha = v3_add(alpha, disturb_alpha);

    v->omega = v3_add(v->omega, v3_scale(alpha, dt));

    /* Інтегрування кватерніона: q += 0.5 * q * (0, omega) * dt. */
    const Quat w = { 0.0f, v->omega.x, v->omega.y, v->omega.z };
    const Quat dq = quat_mul(v->q, w);
    v->q.w += 0.5f * dq.w * dt;
    v->q.x += 0.5f * dq.x * dt;
    v->q.y += 0.5f * dq.y * dt;
    v->q.z += 0.5f * dq.z * dt;
    v->q = quat_normalized(v->q);
}

/* Кут між віссю тяги й вертикаллю — те, що обмежує tilt limiter. */
static float tilt_deg(Quat q)
{
    const Vec3 zb = quat_rotate(q, v3(0.0f, 0.0f, 1.0f));
    return acosf(clampf(zb.z, -1.0f, 1.0f)) * 57.29578f;
}

int main(void)
{
    SetpointMailbox mailbox;
    ControlFeedback feedback;
    Guidance guidance;
    Control control;

    sp_mailbox_init(&mailbox);
    fb_init(&feedback);
    guidance_init(&guidance);
    control_init(&control);

    Vehicle veh = {
        .pos = { 0.0f, 0.0f, -5.0f },
        .vel = { 0.0f, 0.0f, 0.0f },
        .q = { 1.0f, 0.0f, 0.0f, 0.0f },
        .omega = { 0.0f, 0.0f, 0.0f },
    };

    const Vec3 target = v3(0.0f, 0.0f, -5.0f);   /* висіння над точкою старту */
    const float yaw_sp = 0.0f;

    uint64_t now_us = 0;
    long tick = 0;
    int nav_frozen = 0;
    float thrust_cmd = 0.0f;

    printf("  t, с | пн, м | сх, м | вис, м | нахил | газ | режим  | насич\n");
    printf("-------+-------+-------+--------+-------+-----+--------+------\n");

    const long total_ticks = (long)(SIM_SECONDS / DT_FAST);
    for (tick = 0; tick <= total_ticks; ++tick) {
        const float t = (float)tick * DT_FAST;

        /* --- Збурення середовища ------------------------------------------ */
        Vec3 disturb_acc = v3(0.0f, 0.0f, 0.0f);
        Vec3 disturb_alpha = v3(0.0f, 0.0f, 0.0f);

        if (t >= 1.0f && t < 1.6f) {
            disturb_acc.y = 8.0f;              /* бічний порив на схід */
            if (t < 1.05f) {
                disturb_alpha.x = 45.0f;       /* удар по рамі перекидає її */
            }
        }
        if (t >= 2.5f && t < 3.5f) {
            disturb_acc.z = 7.0f;              /* низхідний потік: газ біля стелі */
            disturb_acc.x = -4.0f;
        }

        /* --- Повільний домен: наведення, 50 Гц ----------------------------- */
        if (tick % GUIDANCE_DIV == 0) {
            if (t >= 4.0f) {
                /* Імітуємо зависання задачі навігації: уставок більше немає. */
                if (!nav_frozen) {
                    printf("       |  <<< задача наведення зупинилась (t = %.2f с) >>>\n", t);
                    nav_frozen = 1;
                }
            } else {
                NavState nav;
                nav.pos_ned = veh.pos;
                nav.vel_ned = veh.vel;
                nav.yaw_rad = yaw_sp;

                const Setpoint sp = guidance_step(&guidance, &nav, target, yaw_sp,
                                                  DT_FAST * GUIDANCE_DIV,
                                                  fb_test(&feedback, FB_SATURATED),
                                                  now_us);
                sp_publish(&mailbox, &sp);
            }
        }

        /* --- Швидкий домен: регулятор + мікшер, 1000 Гц -------------------- */
        const ControlOutput cmd = control_step(&control, &mailbox, &feedback,
                                               veh.q, veh.omega, DT_FAST, now_us);
        const MixerOutput mix = mixer_quad_x(cmd.torque, cmd.thrust);

        /* Насичення актуаторів — назад у скриньку прапорців: його читають
           і петля швидкостей регулятора, і петля позиції наведення. */
        fb_set_bit(&feedback, FB_SATURATED, mix.saturated);
        thrust_cmd = cmd.thrust;

        Vec3 real_torque;
        float real_thrust;
        mixer_to_wrench(mix.motor, &real_torque, &real_thrust);

        vehicle_step(&veh, real_torque, real_thrust, disturb_acc, disturb_alpha, DT_FAST);

        /* --- Незручні випадки, які буває видно лише в польоті -------------- */
        if (!isfinite(veh.pos.z) || !isfinite(veh.q.w)) {
            printf("\nМодель розійшлася на t = %.2f с — контур нестійкий.\n", t);
            return 1;
        }
        if (veh.pos.z >= 0.0f) {
            printf("%6.2f |%6.2f |%6.2f |%7.2f |%6.1f |%4.2f | ТОРКАННЯ ЗЕМЛІ\n",
                   t, veh.pos.x, veh.pos.y, -veh.pos.z, tilt_deg(veh.q), thrust_cmd);
            printf("\nСторож уставки посадив апарат замість того, щоб віддати\n"
                   "керування контуру, який мовчить уже понад 100 мс.\n");
            return 0;
        }

        if (tick % 100 == 0) {   /* друк кожні 100 мс */
            printf("%6.2f |%6.2f |%6.2f |%7.2f |%6.1f |%4.2f | %-6s | %s\n",
                   t, veh.pos.x, veh.pos.y, -veh.pos.z, tilt_deg(veh.q), thrust_cmd,
                   cmd.fallback ? "АВАРІЯ" : "НАВЕД.",
                   mix.saturated ? "так" : "-");
        }

        now_us += (uint64_t)(DT_FAST * 1e6f);
    }

    printf("\nСимуляція завершена: %.1f с, %ld тактів регулятора, %ld тактів наведення.\n",
           SIM_SECONDS, total_ticks, total_ticks / GUIDANCE_DIV);
    return 0;
}
