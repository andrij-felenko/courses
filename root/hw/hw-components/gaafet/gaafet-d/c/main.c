#include <stdio.h>
#include <math.h>

/* Структура геометричних та електричних параметрів наношару GAAFET */
typedef struct {
    double w_ns_nm;       /* Ширина наношару W_ns (нм) */
    double t_ns_nm;       /* Товщина наношару T_ns (нм) */
    double l_gate_nm;     /* Довжина затвора L_g (нм) */
    int    n_sheets;      /* Кількість наношарів у стосі */
    double v_dd;          /* Напруга живлення (В) */
    double r_front_pdn;   /* Опір шини живлення Frontside (Ом) */
    double r_back_pdn;    /* Опір шини живлення Backside / TSV (Ом) */
} gaafet_transistor_sim_t;

/* Структура результатів моделювання */
typedef struct {
    double w_eff_total_nm;      /* Повна ефективна ширина W_eff (нм) */
    double i_drive_ma;          /* Струм відкритого стану I_on (мА) */
    double v_drop_front_mv;     /* Падіння напруги IR-drop у Frontside PDN (мВ) */
    double v_drop_back_mv;      /* Падіння напруги IR-drop у Backside PDN (мВ) */
    double effective_vdd_front; /* Ефективна напруга на транзисторі (Frontside) */
    double effective_vdd_back;  /* Ефективна напруга на транзисторі (Backside) */
    double speedup_percent;     /* Приріст струму завдяки Backside PDN (%) */
} gaafet_sim_results_t;

/* Функція моделювання транзистора та мережі живлення */
gaafet_sim_results_t run_gaafet_simulation(const gaafet_transistor_sim_t *cfg) {
    gaafet_sim_results_t res;

    /* 1. Розрахунок повної ефективної ширини 4-стороннього затвора */
    double perim = 2.0 * cfg->w_ns_nm + 2.0 * cfg->t_ns_nm;
    res.w_eff_total_nm = (double)cfg->n_sheets * perim;

    /* 2. Питомий струм квазібалістичного насичення ~1.42 мА/мкм за V_dd = 0.7 В */
    double base_density_ma_per_um = 1.42;
    double nominal_i_on_ma = (res.w_eff_total_nm / 1000.0) * base_density_ma_per_um;

    /* 3. Розрахунок IR-drop для Frontside PDN (тонкі довгі провідники M0-M15) */
    /* Падіння напруги V_drop = I_total * R_network */
    res.v_drop_front_mv = (nominal_i_on_ma * 1e-3) * cfg->r_front_pdn * 1000.0;
    res.effective_vdd_front = cfg->v_dd - (res.v_drop_front_mv / 1000.0);

    /* 4. Розрахунок IR-drop для Backside PDN (прямі короткі Nano-TSV і товста мідь) */
    res.v_drop_back_mv = (nominal_i_on_ma * 1e-3) * cfg->r_back_pdn * 1000.0;
    res.effective_vdd_back = cfg->v_dd - (res.v_drop_back_mv / 1000.0);

    /* 5. Реальний струм з урахуванням просідання напруги живлення */
    double v_th = 0.22; /* Порогова напруга транзистора (В) */
    double i_front = nominal_i_on_ma * ((res.effective_vdd_front - v_th) / (cfg->v_dd - v_th));
    double i_back  = nominal_i_on_ma * ((res.effective_vdd_back - v_th) / (cfg->v_dd - v_th));

    res.i_drive_ma = i_back;
    res.speedup_percent = ((i_back - i_front) / i_front) * 100.0;

    return res;
}

int main(void) {
    gaafet_transistor_sim_t sim_cfg = {
        .w_ns_nm = 35.0, .t_ns_nm = 5.0, .l_gate_nm = 12.0,
        .n_sheets = 3, .v_dd = 0.70,
        .r_front_pdn = 85.0,  /* Опір довгого ланцюжка Frontside Vias (Ом) */
        .r_back_pdn  = 18.0   /* Опір прямого Nano-TSV Backside (Ом) */
    };

    gaafet_sim_results_t res = run_gaafet_simulation(&sim_cfg);

    printf("GAAFET 2nm Nanosheet Simulation:\n");
    printf("  Total Effective Width W_eff : %.1f nm\n", res.w_eff_total_nm);
    printf("  Frontside PDN IR-Drop       : %.1f mV (V_dd_eff = %.3f V)\n",
           res.v_drop_front_mv, res.effective_vdd_front);
    printf("  Backside PowerVia IR-Drop   : %.1f mV (V_dd_eff = %.3f V)\n",
           res.v_drop_back_mv, res.effective_vdd_back);
    printf("  Net Drive Current Gain      : +%.2f %%\n", res.speedup_percent);

    return 0;
}
