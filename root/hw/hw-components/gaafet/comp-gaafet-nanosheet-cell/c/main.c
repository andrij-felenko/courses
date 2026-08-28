#include <stdio.h>
#include <math.h>

/* Структура геометричних та фізичних параметрів наношару GAAFET */
typedef struct {
    double w_ns_nm;     /* Ширина наношару (нм) */
    double t_ns_nm;     /* Товщина наношару (нм) */
    double l_gate_nm;   /* Довжина затвора L_g (нм) */
    int    n_sheets;    /* Кількість наношарів у стосі */
    double eot_nm;      /* Еквівалентна товщина діелектрика EOT (нм) */
    double l_sp_nm;     /* Товщина внутрішнього спейсера (нм) */
    double k_spacer;    /* Діелектрична проникність спейсера (SiBCN = 4.2) */
    double v_dd;        /* Напруга живлення (В) */
} gaafet_cell_params_t;

/* Структура вихідних розрахункових характеристик комірки */
typedef struct {
    double w_eff_total_nm;   /* Повна ефективна ширина каналу (нм) */
    double c_channel_ff;     /* Ємність каналу (фемтофаради) */
    double c_spacer_ff;      /* Паразитна ємність внутрішніх спейсерів (фФ) */
    double c_total_gate_ff;  /* Сумарна ємність затвора (фФ) */
    double i_on_ma;          /* Струм відкритого стану (мА) */
    double delay_ps;         /* Власна затримка перемикання вентиля (пс) */
    double delta_t_she_c;    /* Локальний саморозігрів каналу (градуси C) */
} gaafet_cell_results_t;

/* Функція чисельного моделювання характеристик комірки */
gaafet_cell_results_t evaluate_gaafet_cell(const gaafet_cell_params_t *p) {
    gaafet_cell_results_t res;
    const double eps0 = 8.854187e-12;   /* Ф/м */
    const double eps_sio2 = 3.9;

    /* 1. Розрахунок повної ефективної ширини каналу */
    double perim_one_sheet = 2.0 * p->w_ns_nm + 2.0 * p->t_ns_nm;
    res.w_eff_total_nm = (double)p->n_sheets * perim_one_sheet;

    /* 2. Ємність інверсійного каналу: C_gc = W_eff * L_g * (eps_ox / EOT) */
    double c_ox_density = (eps_sio2 * eps0) / (p->eot_nm * 1e-9); /* Ф/м^2 */
    double area_channel_m2 = (res.w_eff_total_nm * 1e-9) * (p->l_gate_nm * 1e-9);
    res.c_channel_ff = (area_channel_m2 * c_ox_density) * 1e15;

    /* 3. Паразитна ємність внутрішніх спейсерів (між сусідніми шарами) */
    double eps_sp = p->k_spacer * eps0;
    double t_sus_nm = 9.0; /* Типовий зазор між наношарами */
    double cap_one_spacer = eps_sp * (p->w_ns_nm * 1e-9) * (t_sus_nm * 1e-9) / (p->l_sp_nm * 1e-9);
    /* 2 спейсери (витік і стік) для кожного з (n_sheets - 1) проміжків */
    res.c_spacer_ff = (2.0 * (double)(p->n_sheets - 1) * cap_one_spacer) * 1e15;

    /* Сумарна ємність затвора з урахуванням оверлапу */
    res.c_total_gate_ff = res.c_channel_ff + res.c_spacer_ff + 0.15 * res.c_channel_ff;

    /* 4. Квазібалістичний струм насичення I_on (приймаємо густину ~1.45 мА/мкм W_eff) */
    double current_density_ma_per_um = 1.45;
    res.i_on_ma = (res.w_eff_total_nm / 1000.0) * current_density_ma_per_um * (p->v_dd / 0.7);

    /* 5. Власна затримка вентиля: t_delay = C_total * V_dd / I_on */
    res.delay_ps = (res.c_total_gate_ff * 1e-15 * p->v_dd / (res.i_on_ma * 1e-3)) * 1e12;

    /* 6. Оцінка локального саморозігріву (SHE) */
    /* Тепловий опір наношару R_th ~ 85 К/мВт на 1 наношар */
    double p_diss_mw = res.i_on_ma * p->v_dd * 0.15; /* 15% робочого коефіцієнта активності */
    double r_th_stack = 85.0 / (double)p->n_sheets;
    res.delta_t_she_c = p_diss_mw * r_th_stack;

    return res;
}

int main(void) {
    gaafet_cell_params_t hp_cell = {
        .w_ns_nm = 40.0, .t_ns_nm = 5.0, .l_gate_nm = 12.0,
        .n_sheets = 3, .eot_nm = 0.8, .l_sp_nm = 5.5,
        .k_spacer = 4.2, .v_dd = 0.7
    };

    gaafet_cell_results_t r = evaluate_gaafet_cell(&hp_cell);
    printf("GAAFET 2nm Cell Evaluation:\n");
    printf("  W_eff total : %.1f nm\n", r.w_eff_total_nm);
    printf("  C_gate      : %.3f fF (Channel: %.3f, Spacer: %.3f)\n",
           r.c_total_gate_ff, r.c_channel_ff, r.c_spacer_ff);
    printf("  I_on        : %.3f mA\n", r.i_on_ma);
    printf("  Cell Delay  : %.2f ps\n", r.delay_ps);
    printf("  Self-Heating: +%.1f C\n", r.delta_t_she_c);
    return 0;
}
