#include <stdio.h>
#include <stdbool.h>
#include <math.h>

typedef enum {
    PHASE_COLD_START = 0,
    PHASE_MAIN_CHARGING,
    PHASE_ACTIVE_BURST
} SystemPhase;

typedef struct {
    double v_src;          /* Вхідна напруга джерела (В) */
    double r_src;          /* Внутрішній опір джерела (Ом) */
    double c_aux;          /* Ємність пускового конденсатора (Ф) */
    double c_store;        /* Ємність головного накопичувача (Ф) */
    double v_high;         /* Поріг увімкнення навантаження (В) */
    double v_low;          /* Поріг відсічки навантаження (В) */
    double i_burst;        /* Струм навантаження в імпульсі (А) */
    double t_burst;        /* Тривалість робочого імпульсу (с) */
    double i_q;            /* Струм споживання супервізора (А) */
    double leak_i0;        /* Базовий витік конденсатора при 0 В (А) */
    double leak_alpha;     /* Коефіцієнт експоненційного зростання витоку */
    double eta_cold;       /* ККД автогенератора Мейснера */
    double eta_main;       /* ККД основного boost-перетворювача */
} HarvesterParams;

typedef struct {
    double time_sec;
    double v_aux;
    double v_store;
    SystemPhase phase;
    double burst_timer;
    int burst_count;
} HarvesterState;

static double calculate_leakage(const HarvesterParams *p, double voltage) {
    if (voltage <= 0.0) return 0.0;
    return p->leak_i0 * exp(p->leak_alpha * voltage);
}

static void harvester_step(const HarvesterParams *p, HarvesterState *s, double dt) {
    s->time_sec += dt;

    if (s->phase == PHASE_COLD_START) {
        /* Максимальна вхідна потужність джерела за умови узгодження імпедансів: V_src^2 / (4 * R_src) */
        double p_in = (p->v_src * p->v_src) / (4.0 * p->r_src);
        double p_aux = p_in * p->eta_cold;

        /* dE = P * dt -> d(0.5 * C * V^2) = P * dt -> V_next = sqrt(V_curr^2 + 2 * P * dt / C) */
        double v_sq = s->v_aux * s->v_aux + (2.0 * p_aux * dt) / p->c_aux;
        s->v_aux = sqrt(v_sq);

        /* Умова пробудження основного перетворювача */
        if (s->v_aux >= 1.8) {
            s->phase = PHASE_MAIN_CHARGING;
        }
    } else if (s->phase == PHASE_MAIN_CHARGING) {
        double p_in = (p->v_src * p->v_src) / (4.0 * p->r_src);
        double p_ch = p_in * p->eta_main;

        double i_leak = calculate_leakage(p, s->v_store);
        double p_loss = (i_leak + p->i_q) * s->v_store;
        double p_net = p_ch - p_loss;

        if (p_net > 0.0) {
            double v_sq = s->v_store * s->v_store + (2.0 * p_net * dt) / p->c_store;
            s->v_store = sqrt(v_sq);
        }

        /* Досягнення верхнього гістерезисного порогу V_high */
        if (s->v_store >= p->v_high) {
            s->phase = PHASE_ACTIVE_BURST;
            s->burst_timer = 0.0;
            s->burst_count++;
        }
    } else if (s->phase == PHASE_ACTIVE_BURST) {
        s->burst_timer += dt;

        /* Розряд великим струмом навантаження: I = C * dV/dt */
        double i_total = p->i_burst + p->i_q + calculate_leakage(p, s->v_store);
        double dv = (i_total * dt) / p->c_store;
        s->v_store -= dv;

        /* Умови завершення імпульсу */
        if (s->burst_timer >= p->t_burst || s->v_store <= p->v_low) {
            s->phase = PHASE_MAIN_CHARGING;
        }
    }
}

int main(void) {
    HarvesterParams params = {
        .v_src = 0.040,         /* 40 мВ від термоелемента TEG */
        .r_src = 2.0,           /* 2.0 Ом внутрішнього опору */
        .c_aux = 4.7e-6,        /* 4.7 мкФ пускової ємності */
        .c_store = 470.0e-6,    /* 470 мкФ головного накопичувача */
        .v_high = 3.30,         /* 3.30 В поріг увімкнення */
        .v_low = 2.20,          /* 2.20 В поріг відсічки */
        .i_burst = 0.022,       /* 22 мА струм радіопередавача */
        .t_burst = 0.015,       /* 15 мс тривалість передачі */
        .i_q = 45.0e-9,         /* 45 нА струм споживання супервізора */
        .leak_i0 = 5.0e-9,      /* 5 нА початковий витік */
        .leak_alpha = 0.95,     /* коефіцієнт експоненти витоку */
        .eta_cold = 0.25,       /* 25% ККД JFET автогенератора */
        .eta_main = 0.82        /* 82% ККД синхронного boost */
    };

    HarvesterState state = {
        .time_sec = 0.0,
        .v_aux = 0.0,
        .v_store = 0.0,
        .phase = PHASE_COLD_START,
        .burst_timer = 0.0,
        .burst_count = 0
    };

    double dt = 0.001; /* крок інтегрування 1 мс */
    double max_time = 120.0; /* 2 хвилини симуляції */

    printf("Час (с) | Фаза         | V_aux (В) | V_store (В) | Імпульси\n");
    printf("-----------------------------------------------------------\n");

    double next_print = 0.0;
    while (state.time_sec <= max_time) {
        if (state.time_sec >= next_print) {
            const char *phase_str = (state.phase == PHASE_COLD_START) ? "Холодний старт" :
                                    (state.phase == PHASE_MAIN_CHARGING) ? "Накопичення  " : "АКТИВНИЙ СПАЛАХ";
            printf("%7.2f | %-12s | %9.3f | %11.3f | %8d\n",
                   state.time_sec, phase_str, state.v_aux, state.v_store, state.burst_count);
            next_print += (state.phase == PHASE_ACTIVE_BURST) ? 0.005 : 10.0;
        }

        harvester_step(&params, &state, dt);
    }

    printf("-----------------------------------------------------------\n");
    printf("Підсумок: успішно виконано %d імпульсів за %.1f с.\n",
           state.burst_count, state.time_sec);

    return 0;
}
