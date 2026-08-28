#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define MU_0 1.256637061435917295385e-6 /* Гн/м */

/* Структура геометрії друкованої доріжки */
typedef struct {
    double length_mm;    /* Довжина, мм */
    double width_mm;     /* Ширина, мм */
    double thickness_um; /* Товщина міді, мкм (наприклад, 35 мкм = 1 oz) */
    double height_gnd_mm;/* Відстань до шару землі L2, мм */
} TraceGeometry;

/* Структура параметрів перехідних отворів */
typedef struct {
    double board_thickness_mm; /* Висота циліндра (товщина плати), мм */
    double drill_diameter_mm;  /* Діаметр свердла, мм */
    int count;                 /* Кількість паралельних отворів */
    double pitch_mm;           /* Крок сітки отворів, мм */
} ViaArrayParams;

/* Повні вхідні параметри гарячої петлі */
typedef struct {
    double v_in;             /* Напруга живлення, В */
    double i_sw;             /* Комутований струм, А */
    double t_fall_ns;        /* Час вимикання струму, нс */
    TraceGeometry top_trace; /* Провідник верхнього шару */
    ViaArrayParams vias;     /* Перехідні отвори повернення */
    double cap_esl_nh;       /* Власний ESL вхідного конденсатора, нГн */
    double fet_pkg_nh;       /* Індуктивність виводів корпусу транзистора, нГн */
    double c_oss_pf;         /* Вихідна паразитна ємність транзистора, пФ */
    double r_loop_mohm;      /* Активний опір контуру, мОм */
} ConverterSetup;

/* Результати розрахунку та моделювання */
typedef struct {
    double l_trace_nh;       /* Часткова індуктивність доріжки, нГн */
    double m_gnd_nh;         /* Взаємна індуктивність з землею L2, нГн */
    double l_vias_nh;        /* Індуктивність масиву перехідних отворів, нГн */
    double l_total_loop_nh;  /* Повна результуюча індуктивність гарячої петлі, нГн */
    double v_spike_ideal;    /* Теоретичний викид Фарадея L*di/dt, В */
    double v_max_transient;  /* Пікова напруга за результатами RK4, В */
    double f_ringing_mhz;    /* Частота високочастотного дзвону, МГц */
    double r_snub_opt_ohm;   /* Оптимальний резистор снабера, Ом */
    double c_snub_opt_pf;    /* Оптимальна ємність снабера, пФ */
    double p_snub_watt;      /* Потужність розсіювання снабера на 1 МГц, Вт */
} SimulationReport;

/* 1. Розрахунок часткової власної індуктивності прямокутної доріжки за формулою Гровера */
double calc_partial_self_inductance(double l_mm, double w_mm, double t_mm) {
    if (l_mm <= 0.0 || w_mm <= 0.0) return 0.0;
    double l_m = l_mm * 1e-3;
    double w_m = w_mm * 1e-3;
    double t_m = (t_mm > 0.0) ? (t_mm * 1e-3) : 1e-6;

    double term1 = log(2.0 * l_m / (w_m + t_m));
    double term2 = 0.5;
    double term3 = 0.2235 * (w_m + t_m) / l_m;

    double l_henry = (MU_0 / (2.0 * M_PI)) * l_m * (term1 + term2 + term3);
    return l_henry * 1e9; /* Повертаємо в нГн */
}

/* 2. Взаємна індуктивність між прямим провідником та площиною землі */
double calc_mutual_inductance(double l_mm, double d_mm) {
    if (l_mm <= 0.0 || d_mm <= 0.0) return 0.0;
    double l_m = l_mm * 1e-3;
    double d_m = d_mm * 1e-3;

    double ratio = l_m / d_m;
    double inv_ratio = d_m / l_m;

    double term1 = log(ratio + sqrt(1.0 + ratio * ratio));
    double term2 = sqrt(1.0 + inv_ratio * inv_ratio);
    double term3 = inv_ratio;

    double m_henry = (MU_0 / (2.0 * M_PI)) * l_m * (term1 - term2 + term3);
    return m_henry * 1e9; /* нГн */
}

/* 3. Розрахунок еквівалентної індуктивності масиву перехідних отворів */
double calc_via_array_inductance(const ViaArrayParams *v) {
    if (v->count <= 0 || v->board_thickness_mm <= 0.0 || v->drill_diameter_mm <= 0.0) return 0.0;
    
    double h_m = v->board_thickness_mm * 1e-3;
    double d_m = v->drill_diameter_mm * 1e-3;
    
    /* Індуктивність одиночного отвору */
    double l_single_h = (MU_0 / (2.0 * M_PI)) * h_m * (log(4.0 * h_m / d_m) - 0.75);
    double l_single_nh = l_single_h * 1e9;
    
    if (v->count == 1) return l_single_nh;

    /* Взаємна індуктивність між сусідніми отворами */
    double s_m = (v->pitch_mm > 0.0) ? (v->pitch_mm * 1e-3) : (d_m * 2.0);
    double m_h = (MU_0 / (2.0 * M_PI)) * h_m * (log((h_m / s_m) + sqrt(1.0 + (h_m * h_m) / (s_m * s_m))) - sqrt(1.0 + (s_m * s_m) / (h_m * h_m)) + (s_m / h_m));
    double m_nh = m_h * 1e9;

    double n = (double)v->count;
    double l_eff = (1.0 / n) * l_single_nh + ((n - 1.0) / n) * m_nh;
    return (l_eff > 0.05) ? l_eff : 0.05;
}

/* 4. Чисельне моделювання перехідного процесу комутації методом Рунге-Кутти (RK4) */
double simulate_transient_rk4(double v_in, double i_init, double l_loop_nh, double c_oss_pf, double r_loop_ohm, double *out_f_ring_mhz) {
    double l_h = l_loop_nh * 1e-9;
    double c_f = c_oss_pf * 1e-12;
    
    if (l_h <= 0.0 || c_f <= 0.0) return v_in;

    double dt = 1e-12; /* Крок 1 пікосекунда */
    double t_end = 50e-9; /* Тривалість 50 наносекунд */
    
    double i = i_init;
    double v = 0.0;
    double v_max = v_in;

    double t_first_peak = 0.0;
    double t_second_peak = 0.0;
    int peak_count = 0;
    double prev_v = 0.0;
    bool rising = true;

    for (double t = 0.0; t < t_end; t += dt) {
        /* Функції похідних: di/dt = (V_in - v - R*i)/L; dv/dt = i/C */
        /* k1 */
        double di1 = (v_in - v - r_loop_ohm * i) / l_h;
        double dv1 = i / c_f;

        /* k2 */
        double i_k2 = i + 0.5 * dt * di1;
        double v_k2 = v + 0.5 * dt * dv1;
        double di2 = (v_in - v_k2 - r_loop_ohm * i_k2) / l_h;
        double dv2 = i_k2 / c_f;

        /* k3 */
        double i_k3 = i + 0.5 * dt * di2;
        double v_k3 = v + 0.5 * dt * dv2;
        double di3 = (v_in - v_k3 - r_loop_ohm * i_k3) / l_h;
        double dv3 = i_k3 / c_f;

        /* k4 */
        double i_k4 = i + dt * di3;
        double v_k4 = v + dt * dv3;
        double di4 = (v_in - v_k4 - r_loop_ohm * i_k4) / l_h;
        double dv4 = i_k4 / c_f;

        /* Оновлення стану */
        i += (dt / 6.0) * (di1 + 2.0 * di2 + 2.0 * di3 + di4);
        v += (dt / 6.0) * (dv1 + 2.0 * dv2 + 2.0 * dv3 + dv4);

        if (v > v_max) v_max = v;

        /* Детектування локальних піків для вимірювання періоду дзвону */
        if (rising && v < prev_v && t > 1e-10) {
            rising = false;
            if (peak_count == 0) {
                t_first_peak = t;
                peak_count++;
            } else if (peak_count == 1) {
                t_second_peak = t;
                peak_count++;
            }
        } else if (!rising && v > prev_v) {
            rising = true;
        }
        prev_v = v;
    }

    if (peak_count >= 2 && (t_second_peak - t_first_peak) > 0.0) {
        double period = t_second_peak - t_first_peak;
        *out_f_ring_mhz = (1.0 / period) / 1e6;
    } else {
        *out_f_ring_mhz = (1.0 / (2.0 * M_PI * sqrt(l_h * c_f))) / 1e6;
    }

    return v_max;
}

/* 5. Головна функція екстракції та повного аналізу перетворювача */
SimulationReport run_converter_analysis(const ConverterSetup *cs) {
    SimulationReport rep;
    
    double t_mm = cs->top_trace.thickness_um * 1e-3;
    rep.l_trace_nh = calc_partial_self_inductance(cs->top_trace.length_mm, cs->top_trace.width_mm, t_mm);
    rep.m_gnd_nh = calc_mutual_inductance(cs->top_trace.length_mm, cs->top_trace.height_gnd_mm);
    
    /* Ефективна індуктивність доріжки з урахуванням екрану землі L2 */
    double l_trace_eff = rep.l_trace_nh - rep.m_gnd_nh;
    if (l_trace_eff < 0.1) l_trace_eff = 0.1;

    rep.l_vias_nh = calc_via_array_inductance(&cs->vias);

    /* Повна індуктивність петлі */
    rep.l_total_loop_nh = l_trace_eff + rep.l_vias_nh + cs->cap_esl_nh + cs->fet_pkg_nh;

    /* Розрахунок ідеального викиду Фарадея */
    double di_dt = cs->i_sw / (cs->t_fall_ns * 1e-9);
    rep.v_spike_ideal = (rep.l_total_loop_nh * 1e-9) * di_dt;

    /* Чисельне моделювання RK4 */
    double r_loop = cs->r_loop_mohm * 1e-3;
    rep.v_max_transient = simulate_transient_rk4(cs->v_in, cs->i_sw, rep.l_total_loop_nh, cs->c_oss_pf, r_loop, &rep.f_ringing_mhz);

    /* Синтез RC-снабера */
    double l_h = rep.l_total_loop_nh * 1e-9;
    double c_f = cs->c_oss_pf * 1e-12;
    rep.r_snub_opt_ohm = sqrt(l_h / c_f);
    rep.c_snub_opt_pf = cs->c_oss_pf * 2.5;

    /* Потужність розсіювання на частоті комутації 1 МГц */
    double f_sw = 1e6;
    double c_snub_f = rep.c_snub_opt_pf * 1e-12;
    rep.p_snub_watt = c_snub_f * cs->v_in * cs->v_in * f_sw;

    return rep;
}

void print_report(const SimulationReport *r) {
    printf("===============================================================\n");
    printf("        ЗВІТ АНАЛІЗУ ГАРЯЧОЇ ПЕТЛІ СИЛОВОГО ПЕРЕТВОРЮВАЧА      \n");
    printf("===============================================================\n");
    printf("  1. ЕКСТРАКЦІЯ ПАРАЗИТНИХ ІНДУКТИВНОСТЕЙ:\n");
    printf("     - Власна індуктивність доріжки L1:        %6.2f нГн\n", r->l_trace_nh);
    printf("     - Взаємна індуктивність з L2 GND:         %6.2f нГн\n", r->m_gnd_nh);
    printf("     - Еквівалентна індуктивність масиву Vias: %6.2f нГн\n", r->l_vias_nh);
    printf("     ----------------------------------------------------------\n");
    printf("     -> ПОВНА ІНДУКТИВНІСТЬ ГАРЯЧОЇ ПЕТЛІ:     %6.2f нГн\n\n", r->l_total_loop_nh);

    printf("  2. ПЕРЕХІДНІ ПРОЦЕСИ ТА ПЕРЕНАПРУГА КОМУТАЦІЇ:\n");
    printf("     - Теоретичний викид Фарадея (L*di/dt):   %6.2f В\n", r->v_spike_ideal);
    printf("     - Пікова напруга на стоці (RK4 Transient):%6.2f В\n", r->v_max_transient);
    printf("     - Частота високочастотного дзвону:       %6.1f МГц\n\n", r->f_ringing_mhz);

    printf("  3. СИНТЕЗ ОПТИМАЛЬНОГО ДЕМПФУВАЛЬНОГО RC-СНАБЕРА:\n");
    printf("     - Оптимальний резистор снабера (R_snub):   %6.2f Ом\n", r->r_snub_opt_ohm);
    printf("     - Оптимальна ємність снабера (C_snub):     %6.1f пФ\n", r->c_snub_opt_pf);
    printf("     - Втрати потужності на 1 МГц (P_snub):     %6.3f Вт\n", r->p_snub_watt);
    printf("===============================================================\n");
}

int main(void) {
    /* Тестовий випадок 1: Невдала топологія (2 шари, довгі траси, одиночні via) */
    ConverterSetup bad_layout = {
        .v_in = 24.0,
        .i_sw = 15.0,
        .t_fall_ns = 2.0,
        .top_trace = { .length_mm = 15.0, .width_mm = 1.0, .thickness_um = 35.0, .height_gnd_mm = 1.5 },
        .vias = { .board_thickness_mm = 1.6, .drill_diameter_mm = 0.3, .count = 1, .pitch_mm = 0.0 },
        .cap_esl_nh = 0.9,
        .fet_pkg_nh = 2.5,
        .c_oss_pf = 400.0,
        .r_loop_mohm = 25.0
    };

    printf("\n[ТЕСТ 1: НЕВДАЛЕ КОМПОНУВАННЯ ПЛАТИ]\n");
    SimulationReport rep_bad = run_converter_analysis(&bad_layout);
    print_report(&rep_bad);

    /* Тестовий випадок 2: Оптимальна 4-шарова топологія (prepreg 0.1 мм, масив via, 0603) */
    ConverterSetup good_layout = {
        .v_in = 24.0,
        .i_sw = 15.0,
        .t_fall_ns = 2.0,
        .top_trace = { .length_mm = 4.0, .width_mm = 3.0, .thickness_um = 35.0, .height_gnd_mm = 0.1 },
        .vias = { .board_thickness_mm = 1.6, .drill_diameter_mm = 0.3, .count = 4, .pitch_mm = 1.0 },
        .cap_esl_nh = 0.35,
        .fet_pkg_nh = 0.4,
        .c_oss_pf = 400.0,
        .r_loop_mohm = 8.0
    };

    printf("\n[ТЕСТ 2: ОПТИМІЗОВАНЕ КОМПОНУВАННЯ З СУЦІЛЬНОЮ ЗЕМЛЕЮ L2]\n");
    SimulationReport rep_good = run_converter_analysis(&good_layout);
    print_report(&rep_good);

    return 0;
}
