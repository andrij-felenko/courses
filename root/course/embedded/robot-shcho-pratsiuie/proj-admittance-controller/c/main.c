#include <stdbool.h>
#include <stdint.h>
#include <math.h>

#define DOF_CARTESIAN 6
#define DT_SEC 0.001f
#define TARE_SAMPLES 500

typedef enum {
    ADMITTANCE_STATE_IDLE = 0,
    ADMITTANCE_STATE_TARING = 1,
    ADMITTANCE_STATE_ACTIVE = 2,
    ADMITTANCE_STATE_FORCE_EXCEEDED = 3,
    ADMITTANCE_STATE_RETRACT = 4,
    ADMITTANCE_STATE_FAULT = 5
} admittance_mode_t;

typedef struct {
    float m_d[DOF_CARTESIAN];         /* Віртуальна маса (кг, кг·м²) */
    float d_d[DOF_CARTESIAN];         /* Віртуальне демпфування (Н·с/м, Н·м·с/рад) */
    float k_d[DOF_CARTESIAN];         /* Віртуальна жорсткість (Н/м, Н·м/рад) */
    float filter_alpha;               /* Коефіцієнт згладжування фільтра сили */
    float deadband[DOF_CARTESIAN];    /* Зона нечутливості датчика (Н, Н·м) */
    float max_force[DOF_CARTESIAN];   /* Аварійний ліміт сили (Н, Н·м) */
    float max_disp[DOF_CARTESIAN];    /* Максимальне зміщення податливості (м, рад) */
    float retract_speed;              /* Швидкість аварійного відведення (м/с) */
} admittance_config_t;

typedef struct {
    float f_raw_offset[DOF_CARTESIAN]; /* Калібрувальне зміщення нуля */
    float f_filt[DOF_CARTESIAN];       /* Відфільтрована сила */
    float disp[DOF_CARTESIAN];         /* Поточне зміщення податливості */
    float vel[DOF_CARTESIAN];          /* Поточна швидкість зміщення */
    uint32_t tare_counter;             /* Лічильник вибірок тарування */
    float tare_accumulator[DOF_CARTESIAN];
    admittance_mode_t mode;
} admittance_context_t;

void admittance_init(admittance_context_t *ctx) {
    if (!ctx) return;
    for (int i = 0; i < DOF_CARTESIAN; ++i) {
        ctx->f_raw_offset[i] = 0.0f;
        ctx->f_filt[i] = 0.0f;
        ctx->disp[i] = 0.0f;
        ctx->vel[i] = 0.0f;
        ctx->tare_accumulator[i] = 0.0f;
    }
    ctx->tare_counter = 0;
    ctx->mode = ADMITTANCE_STATE_IDLE;
}

void admittance_start_tare(admittance_context_t *ctx) {
    if (!ctx) return;
    for (int i = 0; i < DOF_CARTESIAN; ++i) {
        ctx->tare_accumulator[i] = 0.0f;
    }
    ctx->tare_counter = 0;
    ctx->mode = ADMITTANCE_STATE_TARING;
}

admittance_mode_t admittance_step(
    const admittance_config_t *cfg,
    admittance_context_t *ctx,
    const float f_raw[DOF_CARTESIAN],
    const float x_nominal[DOF_CARTESIAN],
    const float v_nominal[DOF_CARTESIAN],
    float x_cmd[DOF_CARTESIAN],
    float v_cmd[DOF_CARTESIAN]
) {
    if (!cfg || !ctx || !f_raw || !x_nominal || !v_nominal || !x_cmd || !v_cmd) {
        return ADMITTANCE_STATE_FAULT;
    }

    /* 1. Режим калібрування нуля датчика */
    if (ctx->mode == ADMITTANCE_STATE_TARING) {
        for (int i = 0; i < DOF_CARTESIAN; ++i) {
            ctx->tare_accumulator[i] += f_raw[i];
            x_cmd[i] = x_nominal[i];
            v_cmd[i] = v_nominal[i];
        }
        ctx->tare_counter++;
        if (ctx->tare_counter >= TARE_SAMPLES) {
            for (int i = 0; i < DOF_CARTESIAN; ++i) {
                ctx->f_raw_offset[i] = ctx->tare_accumulator[i] / (float)TARE_SAMPLES;
                ctx->disp[i] = 0.0f;
                ctx->vel[i] = 0.0f;
                ctx->f_filt[i] = 0.0f;
            }
            ctx->mode = ADMITTANCE_STATE_ACTIVE;
        }
        return ctx->mode;
    }

    /* 2. Обробка аварійного стану відтягування */
    if (ctx->mode == ADMITTANCE_STATE_FORCE_EXCEEDED || ctx->mode == ADMITTANCE_STATE_RETRACT) {
        ctx->mode = ADMITTANCE_STATE_RETRACT;
        for (int i = 0; i < DOF_CARTESIAN; ++i) {
            /* Плавне повернення податливості до нуля */
            if (ctx->disp[i] > 0.0001f) {
                ctx->disp[i] -= cfg->retract_speed * DT_SEC;
            } else if (ctx->disp[i] < -0.0001f) {
                ctx->disp[i] += cfg->retract_speed * DT_SEC;
            } else {
                ctx->disp[i] = 0.0f;
            }
            ctx->vel[i] = 0.0f;
            x_cmd[i] = x_nominal[i] + ctx->disp[i];
            v_cmd[i] = v_nominal[i];
        }
        return ctx->mode;
    }

    /* 3. Основний розрахунковий контур адмітансу */
    for (int i = 0; i < DOF_CARTESIAN; ++i) {
        /* Компенсація зсуву нуля */
        float f_unbiased = f_raw[i] - ctx->f_raw_offset[i];

        /* Експоненційна низькочастотна фільтрація */
        ctx->f_filt[i] = (1.0f - cfg->filter_alpha) * ctx->f_filt[i] +
                         cfg->filter_alpha * f_unbiased;

        /* Перевірка аварійного ліміту сили */
        if (fabsf(ctx->f_filt[i]) > cfg->max_force[i]) {
            ctx->mode = ADMITTANCE_STATE_FORCE_EXCEEDED;
            return ctx->mode;
        }

        /* Відсікання зони нечутливості */
        float f_active = 0.0f;
        if (ctx->f_filt[i] > cfg->deadband[i]) {
            f_active = ctx->f_filt[i] - cfg->deadband[i];
        } else if (ctx->f_filt[i] < -cfg->deadband[i]) {
            f_active = ctx->f_filt[i] + cfg->deadband[i];
        }

        /* Динаміка адмітансу: M_d * a + D_d * v + K_d * p = -F_active */
        float accel = (-f_active - cfg->d_d[i] * ctx->vel[i] - cfg->k_d[i] * ctx->disp[i]) / cfg->m_d[i];

        /* Напівнеявний метод Ейлера */
        ctx->vel[i] += accel * DT_SEC;
        ctx->disp[i] += ctx->vel[i] * DT_SEC;

        /* Насичення ходу та захист від інтегрального розгону */
        if (ctx->disp[i] > cfg->max_disp[i]) {
            ctx->disp[i] = cfg->max_disp[i];
            if (ctx->vel[i] > 0.0f) ctx->vel[i] = 0.0f;
        } else if (ctx->disp[i] < -cfg->max_disp[i]) {
            ctx->disp[i] = -cfg->max_disp[i];
            if (ctx->vel[i] < 0.0f) ctx->vel[i] = 0.0f;
        }

        /* Формування вихідних координат */
        x_cmd[i] = x_nominal[i] + ctx->disp[i];
        v_cmd[i] = v_nominal[i] + ctx->vel[i];
    }

    ctx->mode = ADMITTANCE_STATE_ACTIVE;
    return ADMITTANCE_STATE_ACTIVE;
}
