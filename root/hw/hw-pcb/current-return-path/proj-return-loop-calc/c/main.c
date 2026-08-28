#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define PI 3.14159265358979323846
#define MU_0 (4.0 * PI * 1e-7)  // Магнітна стала, Гн/м

typedef struct {
    double trace_w;      // Ширина сигнальної доріжки, мм
    double trace_t;      // Товщина міді, мм (наприклад, 0.035 для 1 oz)
    double trace_len;    // Довжина доріжки, мм
    double diel_h;       // Висота діелектрика до опорного шару, мм
    double diel_er;      // Відносна діелектрична проникність (4.2 для FR-4)
    double sig_i_ma;     // Амплітуда струму сигналу, мА
    double sig_tr_ns;    // Час наростання фронту сигналу, нс
    double slot_detour;  // Довжина обходу розрізу в площині, мм
    double via_h;        // Висота сигнального via, мм
    double via_d;        // Діаметр отвору via, мм
    double via_ret_dist; // Відстань до зворотного return via, мм
    double iso_ret_dist; // Відстань до випадкового via без пари, мм
} pcb_params_t;

typedef struct {
    double f_crossover_khz;
    double l_solid_nh;
    double l_detour_nh;
    double v_bounce_solid_v;
    double v_bounce_detour_v;
    double l_via_iso_nh;
    double l_via_1ret_nh;
    double l_via_2ret_nh;
    double l_via_4ret_nh;
    double emi_increase_db;
} return_path_result_t;

void calculate_return_path(const pcb_params_t *p, return_path_result_t *res) {
    // 1. Опір постійному струму (мідь: питомий опір 1.72e-8 Ом*м)
    double rho_cu = 1.72e-8;
    double area_m2 = (p->trace_w * 1e-3) * (p->trace_t * 1e-3);
    double r_dc = rho_cu * (p->trace_len * 1e-3) / area_m2;

    // 2. Індуктивність мікросмужки над суцільною площиною (апроксимація IPC-2141)
    // L ≈ 2e-7 * len * ln(5.98 * h / (0.8 * w + t))
    double w_eff = 0.8 * p->trace_w + p->trace_t;
    double l_per_meter = (MU_0 / (2.0 * PI)) * log(5.98 * p->diel_h / w_eff);
    if (l_per_meter < 1e-7) l_per_meter = 1e-7;
    double l_solid_h = l_per_meter * (p->trace_len * 1e-3);
    res->l_solid_nh = l_solid_h * 1e9;

    // 3. Частота кросоверу f_c = R / (2*pi*L)
    res->f_crossover_khz = (r_dc / (2.0 * PI * l_solid_h)) / 1e3;

    // 4. Паразитна індуктивність обходу розрізу
    // s - довжина обходу, r_eff - радіус каналу
    double s_m = p->slot_detour * 1e-3;
    double r_eff = 0.2235 * ((p->trace_w + p->trace_t) * 1e-3);
    double delta_l_h = (MU_0 * s_m / (2.0 * PI)) * (log(2.0 * s_m / r_eff) - 0.75);
    if (delta_l_h < 0.0) delta_l_h = 0.0;
    res->l_detour_nh = res->l_solid_nh + (delta_l_h * 1e9);

    // 5. Викид напруги V = L * (di/dt)
    double didt = (p->sig_i_ma * 1e-3) / (p->sig_tr_ns * 1e-9); // А/с
    res->v_bounce_solid_v = l_solid_h * didt;
    res->v_bounce_detour_v = (l_solid_h + delta_l_h) * didt;

    // 6. Індуктивність переходу через via
    double via_h_m = p->via_h * 1e-3;
    double via_r_m = (p->via_d * 0.5) * 1e-3;
    double d_iso_m = p->iso_ret_dist * 1e-3;
    double s_ret_m = p->via_ret_dist * 1e-3;

    // Без return via (ізольований via)
    double l_via_iso = (MU_0 * via_h_m / (2.0 * PI)) * (log(2.0 * d_iso_m / via_r_m) + 0.25);
    res->l_via_iso_nh = l_via_iso * 1e9;

    // З 1 return via
    double l_via_1 = (MU_0 * via_h_m / (2.0 * PI)) * (log(s_ret_m / via_r_m) + 0.25);
    res->l_via_1ret_nh = l_via_1 * 1e9;

    // З 2 return vias
    double l_via_2 = (MU_0 * via_h_m / (2.0 * PI)) * (log(s_ret_m / via_r_m) / 2.0 + 0.125);
    res->l_via_2ret_nh = l_via_2 * 1e9;

    // З 4 return vias (квадро-кільце)
    double l_via_4 = (MU_0 * via_h_m / (2.0 * PI)) * (log(s_ret_m / via_r_m) / 4.0 + 0.0625);
    res->l_via_4ret_nh = l_via_4 * 1e9;

    // 7. Зростання випромінювання EMI
    double a_solid = p->trace_len * p->diel_h;
    double a_split = a_solid + (p->slot_detour * p->slot_detour * 0.25);
    res->emi_increase_db = 20.0 * log10(a_split / a_solid);
}

int main(void) {
    pcb_params_t p = {
        .trace_w = 0.35,
        .trace_t = 0.035,
        .trace_len = 30.0,
        .diel_h = 0.20,
        .diel_er = 4.2,
        .sig_i_ma = 40.0,
        .sig_tr_ns = 0.8,
        .slot_detour = 14.0,
        .via_h = 1.2,
        .via_d = 0.30,
        .via_ret_dist = 0.70,
        .iso_ret_dist = 12.0
    };

    return_path_result_t res;
    calculate_return_path(&p, &res);

    printf("===============================================================\n");
    printf("   АНАЛІЗАТОР ПЕТЛІ ЗВОРОТНОГО СТРУМУ ДРУКОВАНОЇ ПЛАТИ        \n");
    printf("===============================================================\n");
    printf("Вхідні параметри:\n");
    printf("  Доріжка: довжина = %.1f мм, ширина = %.2f мм, висота h = %.2f мм\n",
           p.trace_len, p.trace_w, p.diel_h);
    printf("  Сигнал: струм = %.1f мА, час наростання t_r = %.2f нс (di/dt = %.2f А/нс)\n",
           p.sig_i_ma, p.sig_tr_ns, (p.sig_i_ma * 1e-3) / (p.sig_tr_ns));
    printf("  Розріз: обхід = %.1f мм | Via: висота = %.2f мм, d = %.2f мм\n",
           p.slot_detour, p.via_h, p.via_d);
    printf("---------------------------------------------------------------\n");
    printf("1. РЕЖИМИ ТЕЧІЇ СТРУМУ:\n");
    printf("  Частота кросоверу f_c (R vs L):  %.2f кГц\n", res.f_crossover_khz);
    printf("  (Вище %.0f кГц зворотний струм повністю стягується під доріжку)\n\n",
           res.f_crossover_khz);

    printf("2. ПАРАЗИТНА ІНДУКТИВНІСТЬ ТА ДЗВІН ПРИ РОЗРІЗІ ПЛОЩИНИ:\n");
    printf("  Індуктивність над суцільною площиною:  %6.2f нГн  (V_drop = %5.1f мВ)\n",
           res.l_solid_nh, res.v_bounce_solid_v * 1e3);
    printf("  Індуктивність при обході розрізу:      %6.2f нГн  (V_drop = %5.1f мВ)\n",
           res.l_detour_nh, res.v_bounce_detour_v * 1e3);
    printf("  Зростання випромінювання петлі (EMI):  +%5.1f дБ\n\n",
           res.emi_increase_db);

    printf("3. ІНДУКТИВНІСТЬ ПЕРЕХОДУ МІЖ ШАРАМИ (VIA TRANSITION):\n");
    printf("  Без return via (d_iso = %.1f мм):      %6.2f нГн\n", p.iso_ret_dist, res.l_via_iso_nh);
    printf("  З 1 return via (відстань %.2f мм):     %6.2f нГн  (x%.1f менше)\n",
           p.via_ret_dist, res.l_via_1ret_nh, res.l_via_iso_nh / res.l_via_1ret_nh);
    printf("  З 2 return vias (симетричні):          %6.2f нГн  (x%.1f менше)\n",
           res.l_via_2ret_nh, res.l_via_iso_nh / res.l_via_2ret_nh);
    printf("  З 4 return vias (квадро-кільце):       %6.2f нГн  (x%.1f менше)\n",
           res.l_via_4ret_nh, res.l_via_iso_nh / res.l_via_4ret_nh);
    printf("===============================================================\n");

    return 0;
}
