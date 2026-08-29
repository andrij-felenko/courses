/* Демонстраційний контур 1 кГц: рука підводить інструмент до жорсткої
   деталі, працює податливо, переживає зрив із деталі й удар.
   Модель довкілля тут груба — важливий саме порядок обробки:
   давач → компенсація ваги → адмітанс → DLS → швидкості суглобів. */

#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

#include "admittance.h"
#include "armkin.h"
#include "toolgravity.h"

#define SIM_STEPS      4000
#define APPROACH_SPEED 0.020f   /* м/с уздовж осі інструмента */
#define WALL_GAP       0.010f   /* зазор до деталі на старті, м */
#define ENV_STIFFNESS  25000.0f /* Н/м — жорстка металева деталь */
#define SLIP_STEP      2000     /* t = 2.0 с: інструмент зривається з деталі */
#define HIT_STEP       2600     /* t = 2.6 с: удар по інструменту */
#define HIT_LENGTH     30       /* тривалість удару, тактів */
#define HIT_FORCE      220.0f   /* Н */

/* Сталий зсув нуля п'єзорезистивних мостів після прогрівання —
   саме його знімає тарування. */
static const float THERMAL_BIAS[ADM_DOF] = { 0.9f, -1.4f, 2.2f, 0.05f, -0.03f, 0.02f };

static uint32_t g_rng = 0x2545F491u;

/* Шум комутації інвертора живе на 10–40 кГц; на 1 кГц ми бачимо його
   вже підмішаним, тож у моделі це просто широкосмуговий шум. */
static float noise_unit(void)
{
    g_rng = g_rng * 1664525u + 1013904223u;
    return (float)((g_rng >> 9) & 0xFFFFu) / 32767.5f - 1.0f;
}

static const char *mode_name(admittance_mode_t m)
{
    switch (m) {
    case ADMITTANCE_MODE_IDLE:           return "IDLE";
    case ADMITTANCE_MODE_TARING:         return "TARING";
    case ADMITTANCE_MODE_ACTIVE:         return "ACTIVE";
    case ADMITTANCE_MODE_FORCE_EXCEEDED: return "FORCE_EXCEEDED";
    case ADMITTANCE_MODE_RETRACT:        return "RETRACT";
    default:                             return "FAULT";
    }
}

static void mat3_apply(const float r[9], const float v[3], float out[3])
{
    for (int i = 0; i < 3; ++i) {
        out[i] = r[3 * i] * v[0] + r[3 * i + 1] * v[1] + r[3 * i + 2] * v[2];
    }
}

static void mat3_apply_transposed(const float r[9], const float v[3], float out[3])
{
    for (int i = 0; i < 3; ++i) {
        out[i] = r[i] * v[0] + r[3 + i] * v[1] + r[6 + i] * v[2];
    }
}

static void cross3(const float a[3], const float b[3], float out[3])
{
    out[0] = a[1] * b[2] - a[2] * b[1];
    out[1] = a[2] * b[0] - a[0] * b[2];
    out[2] = a[0] * b[1] - a[1] * b[0];
}

int main(void)
{
    admittance_config_t cfg = {
        .m_d       = { 4.0f, 4.0f, 4.0f, 0.06f, 0.06f, 0.06f },
        .k_d       = { 350.0f, 350.0f, 350.0f, 8.0f, 8.0f, 8.0f },
        .deadband  = { 0.8f, 0.8f, 0.8f, 0.05f, 0.05f, 0.05f },
        .max_force = { 60.0f, 60.0f, 60.0f, 6.0f, 6.0f, 6.0f },
        .max_disp  = { 0.030f, 0.030f, 0.030f, 0.20f, 0.20f, 0.20f },
        .max_vel   = { 0.15f, 0.15f, 0.15f, 1.0f, 1.0f, 1.0f },
        .retract_speed = 0.05f,
    };
    cfg.filter_alpha = admittance_alpha_for_cutoff(20.0f);
    admittance_set_critical_damping(&cfg); /* zeta = 1 */

    if (!admittance_config_valid(&cfg)) {
        fprintf(stderr, "негодящі коефіцієнти адмітансу\n");
        return 1;
    }

    const tool_inertia_t tool = {
        .mass = 0.8f,
        .com  = { 0.0f, 0.0f, 0.075f },
        .g    = 9.81f,
    };
    const float r_tip[3] = { 0.0f, 0.0f, 0.150f }; /* вістря у системі фланця */

    float q[ARM_JOINTS] = { 0.0f, -0.40f, 0.80f, 0.0f, 0.60f, 0.0f };
    arm_state_t arm;
    arm_forward(ARM_DEMO_LINKS, q, &arm);

    /* Поверхня деталі: площина, перпендикулярна осі інструмента,
       за WALL_GAP попереду вістря на старті. */
    float tip0[3], offset[3], wall_normal[3], wall_point[3];
    mat3_apply(arm.r_flange, r_tip, offset);
    const float tool_axis[3] = { 0.0f, 0.0f, 1.0f };
    mat3_apply(arm.r_flange, tool_axis, wall_normal);
    for (int i = 0; i < 3; ++i) {
        tip0[i] = arm.p_flange[i] + offset[i];
        wall_point[i] = tip0[i] + WALL_GAP * wall_normal[i];
    }

    admittance_context_t ctx;
    admittance_init(&ctx);
    admittance_start_tare(&ctx);

    float x_nominal[ADM_DOF] = { 0 };
    float v_nominal[ADM_DOF] = { 0 };
    float x_cmd[ADM_DOF], v_cmd[ADM_DOF];

    bool wall_present = true;
    bool acknowledged = false;
    float slip_overshoot = 0.0f;
    admittance_mode_t previous = ctx.mode;

    printf("   t,с | режим          | Fz_filt,Н | зміщ.,мм | зазор,мм |    w   | lambda\n");

    for (int step = 0; step < SIM_STEPS; ++step) {
        const float t = (float)step * ADM_DT_SEC;
        arm_forward(ARM_DEMO_LINKS, q, &arm);

        /* --- Модель контакту --- */
        float tip[3];
        mat3_apply(arm.r_flange, r_tip, offset);
        for (int i = 0; i < 3; ++i) {
            tip[i] = arm.p_flange[i] + offset[i];
        }
        float depth = 0.0f;
        for (int i = 0; i < 3; ++i) {
            depth += (tip[i] - wall_point[i]) * wall_normal[i];
        }

        if (step == SLIP_STEP && wall_present) {
            wall_present = false;
            printf("  t=%.3f с: інструмент зірвався з деталі, сила зникла\n", t);
        }

        float f_world[3] = { 0.0f, 0.0f, 0.0f };
        if (wall_present && depth > 0.0f) {
            for (int i = 0; i < 3; ++i) {
                f_world[i] = -ENV_STIFFNESS * depth * wall_normal[i];
            }
        }
        if (step >= HIT_STEP && step < HIT_STEP + HIT_LENGTH) {
            for (int i = 0; i < 3; ++i) {
                f_world[i] += -HIT_FORCE * wall_normal[i];
            }
        }

        /* --- Сирий вимір давача на зап'ястку (система фланця) --- */
        float f_contact[3], torque_contact[3], w_gravity[ADM_DOF], w_raw[ADM_DOF];
        mat3_apply_transposed(arm.r_flange, f_world, f_contact);
        cross3(r_tip, f_contact, torque_contact);
        tool_gravity_wrench(&tool, arm.r_flange, w_gravity);
        for (int i = 0; i < 3; ++i) {
            w_raw[i] = f_contact[i] + w_gravity[i] + THERMAL_BIAS[i] + 0.40f * noise_unit();
            w_raw[3 + i] = torque_contact[i] + w_gravity[3 + i] + THERMAL_BIAS[3 + i] +
                           0.03f * noise_unit();
        }

        /* --- Компенсація ваги інструмента --- */
        float w_ext[ADM_DOF], f_react[ADM_DOF];
        tool_gravity_compensate(&tool, arm.r_flange, w_raw, w_ext);
        /* Давач віддає силу, ЩО ДІЄ НА інструмент; рівняння адмітансу
           записане для сили реакції — тому знак міняємо тут, один раз. */
        for (int i = 0; i < ADM_DOF; ++i) {
            f_react[i] = -w_ext[i];
        }

        /* --- Номінальна траєкторія: подача вздовж осі інструмента --- */
        for (int i = 0; i < ADM_DOF; ++i) {
            v_nominal[i] = 0.0f;
        }
        if (ctx.mode == ADMITTANCE_MODE_ACTIVE && step < SLIP_STEP) {
            v_nominal[2] = APPROACH_SPEED;
        }
        for (int i = 0; i < ADM_DOF; ++i) {
            x_nominal[i] += v_nominal[i] * ADM_DT_SEC;
        }

        const admittance_mode_t mode = admittance_step(&cfg, &ctx, f_react, x_nominal,
                                                       v_nominal, x_cmd, v_cmd);
        if (mode != previous) {
            printf("  t=%.3f с: %s → %s\n", t, mode_name(previous), mode_name(mode));
            previous = mode;
        }
        if (mode == ADMITTANCE_MODE_FAULT) {
            fprintf(stderr, "аварія регулятора на t=%.3f с, цикл зупинено\n", t);
            return 2;
        }

        /* --- Декартова команда з системи інструмента в базову --- */
        float v_base[CART_DOF];
        arm_rotate6(arm.r_flange, v_cmd, v_base);

        float q_dot[ARM_JOINTS];
        float lambda = 0.0f;
        if (!arm_dls_joint_velocity(&arm, v_base, 0.08f, 0.02f, q_dot, &lambda)) {
            fprintf(stderr, "t=%.3f с: рука в сингулярності, рух зупинено\n", t);
            return 3;
        }
        for (int j = 0; j < ARM_JOINTS; ++j) {
            q[j] += q_dot[j] * ADM_DT_SEC;
        }

        /* Під час контакту зміщення від'ємне (інструмент поступається).
           Після зриву воно повертається до нуля — і при zeta = 1 не має
           перескочити в плюс, тобто вистрілити вперед. */
        if (step > SLIP_STEP && step < HIT_STEP && ctx.disp[2] > slip_overshoot) {
            slip_overshoot = ctx.disp[2];
        }

        if (ctx.mode == ADMITTANCE_MODE_RETRACT && !acknowledged &&
            fabsf(ctx.disp[2]) >= 0.999f * cfg.max_disp[2]) {
            printf("  t=%.3f с: відхід завершено, квитуємо аварію\n", t);
            admittance_acknowledge(&ctx);
            acknowledged = true;
            previous = ctx.mode;
        }

        if (step % 100 == 0) {
            printf("%6.3f | %-14s | %9.2f | %8.2f | %8.2f | %6.4f | %6.4f\n",
                   t, mode_name(mode), ctx.f_filt[2], ctx.disp[2] * 1000.0f,
                   -depth * 1000.0f, arm.manipulability, lambda);
        }
    }

    printf("\nПеререгулювання після зриву: %.3f мм (zeta = 1 → без вистрілювання)\n",
           slip_overshoot * 1000.0f);
    return 0;
}
