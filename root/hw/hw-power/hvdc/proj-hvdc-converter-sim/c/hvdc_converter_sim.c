/* hvdc_converter_sim.c - Моделювання контуру керування HVDC мостом (C99) */
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Структура параметрів HVDC перетворювального мосту */
typedef struct {
    double u_ll_rms;     /* Лінійна напруга AC мережі (В) */
    double x_c;          /* Комутаційний опір трансформатора (Ом) */
    double r_line;       /* Активний опір DC лінії (Ом) */
    double i_ref;        /* Заданий струм полюса (А) */
    double kp;           /* Пропорційний коефіцієнт ПІ-регулятора */
    double ki;           /* Інтегральний коефіцієнт ПІ-регулятора */
    double alpha_min_deg;/* Мінімальний кут відкривання (град) */
    double alpha_max_deg;/* Максимальний кут відкривання (град) */
    double gamma_min_deg;/* Мінімальний кут погасання для інвертора (град) */
} HvdcConfig;

/* Стан контуру керування */
typedef struct {
    double alpha_deg;    /* Поточний кут відкривання тиристорів (град) */
    double integrator;   /* Аккумулятор інтегратора ПІ */
    double u_dc;         /* Поточна напруга DC (В) */
    double i_dc;         /* Поточний струм DC (А) */
    double mu_deg;       /* Кут комутаційного перекриття (град) */
    double gamma_deg;    /* Кут погасання інвертора (град) */
    bool comm_failure;   /* Прапорець збою комутації */
} HvdcState;

/* Ініціалізація стану */
void hvdc_init(HvdcState *state, double initial_alpha) {
    state->alpha_deg = initial_alpha;
    state->integrator = 0.0;
    state->u_dc = 0.0;
    state->i_dc = 0.0;
    state->mu_deg = 0.0;
    state->gamma_deg = 0.0;
    state->comm_failure = false;
}

/* Обчислення кута комутаційного перекриття mu (в радіанах) */
static double calc_commutation_overlap(double u_ll_rms, double x_c, double i_dc, double alpha_rad) {
    double cos_alpha = cos(alpha_rad);
    double drop = (2.0 * x_c * i_dc) / (sqrt(2.0) * u_ll_rms);
    double cos_alpha_mu = cos_alpha - drop;

    if (cos_alpha_mu < -1.0) cos_alpha_mu = -1.0;
    if (cos_alpha_mu > 1.0)  cos_alpha_mu = 1.0;

    double alpha_mu = acos(cos_alpha_mu);
    double mu_rad = alpha_mu - alpha_rad;
    return (mu_rad < 0.0) ? 0.0 : mu_rad;
}

/* Один крок дискретного моделювання контуру (dt в секундах) */
void hvdc_step(const HvdcConfig *cfg, HvdcState *st, double dt) {
    /* 1. Обчислення помилки регулювання струму */
    double err = cfg->i_ref - st->i_dc;

    /* 2. ПІ-регулятор кута alpha */
    st->integrator += err * dt;
    double alpha_calc = st->alpha_deg - (cfg->kp * err + cfg->ki * st->integrator);

    /* Обмеження насичення регулятора (Anti-windup) */
    if (alpha_calc < cfg->alpha_min_deg) {
        alpha_calc = cfg->alpha_min_deg;
        st->integrator -= err * dt;
    } else if (alpha_calc > cfg->alpha_max_deg) {
        alpha_calc = cfg->alpha_max_deg;
        st->integrator -= err * dt;
    }
    st->alpha_deg = alpha_calc;

    /* 3. Фізика мосту: розрахунок U_dc з урахуванням комутаційного падіння */
    double alpha_rad = st->alpha_deg * (M_PI / 180.0);
    double u_dc0 = (3.0 * sqrt(2.0) / M_PI) * cfg->u_ll_rms * cos(alpha_rad);
    double r_eq = (3.0 / M_PI) * cfg->x_c;

    /* Реакція навантаження */
    st->i_dc = u_dc0 / (cfg->r_line + r_eq);
    if (st->i_dc < 0.0) st->i_dc = 0.0;
    st->u_dc = u_dc0 - r_eq * st->i_dc;

    /* 4. Розрахунок комутаційного кута mu та кута погасання gamma */
    double mu_rad = calc_commutation_overlap(cfg->u_ll_rms, cfg->x_c, st->i_dc, alpha_rad);
    st->mu_deg = mu_rad * (180.0 / M_PI);
    st->gamma_deg = 180.0 - (st->alpha_deg + st->mu_deg);

    /* 5. Перевірка аварійної умови збою комутації інвертора */
    if (st->alpha_deg > 90.0 && st->gamma_deg < cfg->gamma_min_deg) {
        st->comm_failure = true;
    } else {
        st->comm_failure = false;
    }
}

int main(void) {
    HvdcConfig cfg = {
        .u_ll_rms = 400000.0,    /* 400 кВ AC */
        .x_c = 15.0,             /* 15 Ом комутаційний опір */
        .r_line = 100.0,         /* 100 Ом опір DC лінії */
        .i_ref = 2000.0,         /* Заданий струм 2000 А */
        .kp = 0.005,
        .ki = 0.05,
        .alpha_min_deg = 5.0,    /* Мін. кут 5° */
        .alpha_max_deg = 150.0,  /* Макс. кут 150° */
        .gamma_min_deg = 15.0    /* Поріг аварії 15° */
    };

    HvdcState state;
    hvdc_init(&state, 30.0);

    printf("=== Симуляція контуру керування HVDC (C99) ===\n");
    printf("Крок |  Alpha (°) |    U_dc (кВ) |    I_dc (А) |   Mu (°) |  Gamma (°) | Стан\n");
    printf("-----+------------+--------------+-------------+----------+------------+------\n");

    double dt = 0.01; /* 10 мс крок */
    for (int step = 1; step <= 10; ++step) {
        hvdc_step(&cfg, &state, dt);
        printf("%4d | %10.2f | %12.2f | %11.1f | %8.2f | %10.2f | %s\n",
               step, state.alpha_deg, state.u_dc / 1000.0, state.i_dc,
               state.mu_deg, state.gamma_deg,
               state.comm_failure ? "АВАРІЯ (CommFail)" : "ОК");
    }

    return 0;
}
