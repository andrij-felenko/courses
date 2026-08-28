/* thermo_sim.c - Чисельний симулятор термодинамічних процесів та циклів мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define R_GAS 8.3144626

typedef enum {
    PROC_ISOCHORIC,
    PROC_ISOBARIC,
    PROC_ISOTHERMAL,
    PROC_ADIABATIC
} ProcessType;

typedef struct {
    double p; /* Тиск [Па] */
    double v; /* Об'єм [м³] */
    double t; /* Температура [К] */
} State;

typedef struct {
    ProcessType type;
    State start;
    State end;
    double work;   /* Робота W [Дж] */
    double heat;   /* Тепло Q [Дж] */
    double delta_u;/* Зміна внутрішньої енергії dU [Дж] */
} ProcessResult;

typedef struct {
    double n_moles;
    double degrees_of_freedom; /* i = 3 (одноатомний), 5 (двохатомний) */
    double c_v;
    double c_p;
    double gamma;
} GasModel;

GasModel gas_init(double n_moles, double dof) {
    GasModel g;
    g.n_moles = n_moles;
    g.degrees_of_freedom = dof;
    g.c_v = (dof / 2.0) * R_GAS;
    g.c_p = g.c_v + R_GAS;
    g.gamma = g.c_p / g.c_v;
    return g;
}

ProcessResult step_isochoric(const GasModel *g, State start, double target_t) {
    ProcessResult res;
    res.type = PROC_ISOCHORIC;
    res.start = start;
    res.end.v = start.v;
    res.end.t = target_t;
    res.end.p = (g->n_moles * R_GAS * target_t) / start.v;
    
    res.work = 0.0;
    res.delta_u = g->n_moles * g->c_v * (target_t - start.t);
    res.heat = res.delta_u;
    return res;
}

ProcessResult step_isobaric(const GasModel *g, State start, double target_v) {
    ProcessResult res;
    res.type = PROC_ISOBARIC;
    res.start = start;
    res.end.p = start.p;
    res.end.v = target_v;
    res.end.t = (start.p * target_v) / (g->n_moles * R_GAS);
    
    res.work = start.p * (target_v - start.v);
    res.delta_u = g->n_moles * g->c_v * (res.end.t - start.t);
    res.heat = res.delta_u + res.work;
    return res;
}

ProcessResult step_isothermal(const GasModel *g, State start, double target_v) {
    ProcessResult res;
    res.type = PROC_ISOTHERMAL;
    res.start = start;
    res.end.v = target_v;
    res.end.t = start.t;
    res.end.p = (g->n_moles * R_GAS * start.t) / target_v;
    
    res.delta_u = 0.0;
    res.work = g->n_moles * R_GAS * start.t * log(target_v / start.v);
    res.heat = res.work;
    return res;
}

ProcessResult step_adiabatic(const GasModel *g, State start, double target_v) {
    ProcessResult res;
    res.type = PROC_ADIABATIC;
    res.start = start;
    res.end.v = target_v;
    res.end.p = start.p * pow(start.v / target_v, g->gamma);
    res.end.t = (res.end.p * target_v) / (g->n_moles * R_GAS);
    
    res.heat = 0.0;
    res.delta_u = g->n_moles * g->c_v * (res.end.t - start.t);
    res.work = -res.delta_u;
    return res;
}

void print_cycle_summary(const ProcessResult *steps, size_t count) {
    double total_work = 0.0;
    double q_in = 0.0;
    double q_out = 0.0;
    double total_du = 0.0;

    printf("=== РЕЗУЛЬТАТИ ТЕРМОДИНАМІЧНОГО ЦИКЛУ ===\n");
    for (size_t i = 0; i < count; ++i) {
        printf("Крок %zu: W = %10.2f Дж, Q = %10.2f Дж, dU = %10.2f Дж\n",
               i + 1, steps[i].work, steps[i].heat, steps[i].delta_u);
        total_work += steps[i].work;
        total_du += steps[i].delta_u;
        if (steps[i].heat > 0) {
            q_in += steps[i].heat;
        } else {
            q_out += -steps[i].heat;
        }
    }

    double eta = (q_in > 0) ? (total_work / q_in) * 100.0 : 0.0;
    printf("-----------------------------------------\n");
    printf("Суммарна робота за цикл W_net : %10.2f Дж\n", total_work);
    printf("Підведене тепло Q_in          : %10.2f Дж\n", q_in);
    printf("Відведене тепло Q_out         : %10.2f Дж\n", q_out);
    printf("Баланс енергії sum(dU)       : %10.2f Дж (має бути 0)\n", total_du);
    printf("Термічний ККД циклу eta       : %10.2f %%\n", eta);
}

int main(void) {
    /* Моделюємо цикл Карно для 1 моля двохатомного газу (повітря, i = 5) */
    GasModel gas = gas_init(1.0, 5.0);
    
    /* Початковий стан 1: P = 500 кПа, V = 0.002 м³ */
    State s1;
    s1.p = 500000.0;
    s1.v = 0.002;
    s1.t = (s1.p * s1.v) / (gas.n_moles * R_GAS); /* ~120.27 K */

    ProcessResult cycle[4];

    /* 1->2: Ізотермічне розширення при Т1 до V2 = 0.006 м³ */
    cycle[0] = step_isothermal(&gas, s1, 0.006);

    /* 2->3: Адіабатне розширення до V3 = 0.012 м³ */
    cycle[1] = step_adiabatic(&gas, cycle[0].end, 0.012);

    /* 3->4: Ізотермічне стиснення до V4 = 0.004 м³ */
    cycle[2] = step_isothermal(&gas, cycle[1].end, 0.004);

    /* 4->1: Адіабатне стиснення назад до V1 = 0.002 м³ */
    cycle[3] = step_adiabatic(&gas, cycle[2].end, 0.002);

    print_cycle_summary(cycle, 4);
    return 0;
}
