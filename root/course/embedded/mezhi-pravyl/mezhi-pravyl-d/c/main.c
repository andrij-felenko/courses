#include <math.h>
#include <stdio.h>

#include "planner.h"
#include "rover.h"
#include "supervisor.h"

/* Сценарій із трьома збуреннями одночасно: огорожа за 3.8 м, боковий вітер
 * 12 м/с і просілий 4S-пакет. Стенд навмисно мінімальний — предмет тут не
 * симуляція, а поведінка двох контурів під час конфлікту цілей. */

#define SIM_DT      0.005f  /* 200 Гц — жорсткий цикл бар'єра */
#define PLAN_PERIOD 10      /* 20 Гц — повільний контур */
#define SIM_TICKS   1200    /* 6 секунд */
#define FENCE_N     11

typedef struct {
    float x, y, theta;
    float v, w;
    float ocv;
} Plant;

static Obstacle g_fence[FENCE_N];

static void build_fence(void)
{
    for (int i = 0; i < FENCE_N; i++) {
        g_fence[i].x = 6.0f;
        g_fence[i].y = -3.0f + 0.6f * (float)i;
        g_fence[i].radius = 0.35f;
    }
}

static float ray_range(float x, float y, float th)
{
    const float dx = cosf(th), dy = sinf(th);
    float best = 30.0f;

    for (int i = 0; i < FENCE_N; i++) {
        const float ox   = g_fence[i].x - x;
        const float oy   = g_fence[i].y - y;
        const float t_ca = ox * dx + oy * dy;
        if (t_ca < 0.0f) {
            continue; /* позаду */
        }
        const float d2 = ox * ox + oy * oy - t_ca * t_ca;
        const float r2 = g_fence[i].radius * g_fence[i].radius;
        if (d2 > r2) {
            continue; /* промінь проходить мимо */
        }
        float t = t_ca - sqrtf(r2 - d2);
        if (t < 0.0f) {
            t = 0.0f;
        }
        if (t < best) {
            best = t;
        }
    }
    return best;
}

/* Мінімум по передньому сектору ±25°, спроєктований на курс. Один промінь
 * тут був би пасткою: поворот на пів градуса «ховає» огорожу. */
static float sector_range(float x, float y, float th)
{
    float best = 30.0f;

    for (int k = -5; k <= 5; k++) {
        const float a = 0.0873f * (float)k;
        const float r = ray_range(x, y, th + a) * cosf(a);
        if (r < best) {
            best = r;
        }
    }
    return best;
}

static float true_clearance(const Plant *pl)
{
    float best = 1.0e6f;

    for (int i = 0; i < FENCE_N; i++) {
        const float dx = pl->x - g_fence[i].x;
        const float dy = pl->y - g_fence[i].y;
        const float d  = sqrtf(dx * dx + dy * dy) - g_fence[i].radius;
        if (d < best) {
            best = d;
        }
    }
    return best;
}

int main(void)
{
    const RoverParams  params  = rover_default_params();
    const SafetyLimits limits  = rover_default_limits();
    const PlannerConfig cfg    = planner_default_config(12.0f, 5.0f);

    build_fence();

    Plant pl = { .x = 1.85f, .y = 0.0f, .theta = 0.0f,
                 .v = 2.2f, .w = 0.0f, .ocv = 14.25f };

    Supervisor sup;
    supervisor_init(&sup, &limits);

    float min_clear = 1.0e6f;
    float min_h     = 1.0e6f;
    float next_print = 0.0f;

    printf("    t     v      w  range      h   i_pr  budget  V_term  вердикт\n");

    for (int tick = 0; tick < SIM_TICKS; tick++) {
        const float t = (float)tick * SIM_DT;

        VehicleState st;
        st.vx                = pl.v;
        st.yaw_rate          = pl.w;
        st.range_ahead_m     = sector_range(pl.x, pl.y, pl.theta);
        st.range_valid       = !(t > 1.00f && t < 1.15f); /* провал лідара 150 мс */
        st.tilt_rad          = 0.05f;
        st.pack_ocv_v        = pl.ocv;
        st.pack_esr_ohm      = 0.12f;                     /* просілий пакет */
        st.yaw_disturbance_nm = 1.9f;                     /* боковий вітер 12 м/с */

        /* Повільний контур; з 2.0 до 2.4 с планувальник «завис». */
        if (tick % PLAN_PERIOD == 0 && !(t > 2.0f && t < 2.4f)) {
            const Pose     pose = { pl.x, pl.y, pl.theta };
            const Setpoint cur  = { pl.v, pl.w };
            float cost = 0.0f;
            const Setpoint cand = planner_solve(&cfg, &limits, pose, cur,
                                                g_fence, FENCE_N, &cost);
            if (isfinite(cost)) {
                supervisor_submit(&sup, cand);
            }
        }

        const SupervisorTick out = supervisor_step(&sup, &params, &limits, &st, SIM_DT);

        /* Стенд: приводи відпрацьовують уставку з першим порядком. */
        pl.v     += (out.out.vx - pl.v) * (SIM_DT / 0.25f);
        pl.w     += (out.out.yaw_rate - pl.w) * (SIM_DT / 0.12f);
        pl.theta += pl.w * SIM_DT;
        pl.x     += pl.v * cosf(pl.theta) * SIM_DT;
        pl.y     += pl.v * sinf(pl.theta) * SIM_DT + 0.28f * SIM_DT; /* знос вітром */
        pl.ocv   -= out.barrier.predicted_a * SIM_DT / 3600.0f / 5.2f * 1.5f;

        const float clear = true_clearance(&pl);
        if (clear < min_clear) {
            min_clear = clear;
        }
        if (out.barrier.h_value < min_h) {
            min_h = out.barrier.h_value;
        }

        if (t >= next_print) {
            next_print += 0.25f;
            printf("%5.2f %5.2f %6.2f %6.2f %6.2f %6.2f %7.2f %7.2f  %s%s\n",
                   t, pl.v, pl.w, st.range_ahead_m, out.barrier.h_value,
                   out.barrier.predicted_a, out.barrier.budget_a,
                   st.pack_ocv_v - out.barrier.predicted_a * st.pack_esr_ohm,
                   barrier_verdict_name(out.barrier.verdict),
                   out.cand_status == CAND_OK ? ""
                                              : " [кандидат відкинуто]");
        }
    }

    printf("\nмінімальний зазор до огорожі: %.2f м (зазор безпеки %.2f м)\n",
           min_clear, limits.obstacle_margin_m);
    printf("мінімум бар'єрної функції h(x): %.2f (h < 0 = вихід за безпечну множину)\n",
           min_h);
    printf("перемикань вердикту: %u, відкинутих кандидатів: %u\n",
           sup.verdict_changes, sup.rejected_count);
    printf("фінал: v = %.2f м/с — %s\n", pl.v,
           (min_clear > 0.05f) ? "зіткнення не сталося" : "ЗІТКНЕННЯ");
    return 0;
}
