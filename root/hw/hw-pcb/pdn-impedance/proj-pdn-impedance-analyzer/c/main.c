#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>
#include <stdbool.h>
#include <string.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define MAX_GROUPS 32
#define MAX_PEAKS  64
#define MAX_SWEEP_PTS 2048

/* Структура специфікації вимог до PDN */
typedef struct {
    double v_dd;           /* Напруга живлення (В) */
    double ripple_ratio;   /* Допустима пульсація (частка, напр. 0.03 = 3%) */
    double i_transient;    /* Стрибок струму споживання (А) */
    double t_rise;         /* Тривалість фронту наростання струму (с) */
    double target_z;       /* Розрахований цільовий імпеданс (Ом) */
    double f_knee;         /* Гранична частота спектра (Гц) */
} PdnSpecification;

/* Структура групи конденсаторів */
typedef struct {
    double nominal_cap;    /* Номінальна ємність C0 (Ф) */
    double esr_nominal;    /* Номінальний ESR на 1 кГц (Ом) */
    double esl_nominal;    /* Власний ESL компонента (Гн) */
    double l_mount;        /* Індуктивність монтажу та перехідних отворів (Гн) */
    double r_mount;        /* Опір перехідних отворів (Ом) */
    double v_sat;          /* Напруга насичення DC-Bias (В) */
    double bias_alpha;     /* Показник крутизни DC-Bias */
    double tan_delta;      /* Тангенс кута діелектричних втрат */
    int    count;          /* Кількість паралельних компонентів */
    char   label[64];      /* Текстовий опис групи */
} DecouplingGroup;

/* Структура 2D порожнинного резонатора площин */
typedef struct {
    double length_a;       /* Довжина площини вздовж X (м) */
    double width_b;        /* Ширина площини вздовж Y (м) */
    double thickness_d;    /* Відстань між площинами (м) */
    double eps_r;          /* Діелектрична проникність діелектрика */
    double tan_delta;      /* Тангенс втрат діелектрика */
    double port_x;         /* Координата точки споживача X (м) */
    double port_y;         /* Координата точки споживача Y (м) */
    int    max_modes_m;    /* Максимальний порядок моди M */
    int    max_modes_n;    /* Максимальний порядок моди N */
    bool   enabled;        /* Прапорець активації моделі площин */
} PlaneCavity;

/* Структура моделі стабілізатора VRM */
typedef struct {
    double r_dc;           /* Активний опір DC (Ом) */
    double l_out;          /* Еквівалентна індуктивність дроселів (Гн) */
    double f_crossover;    /* Частота зрізу замкненої петлі (Гц) */
    double a_0;            /* Підсилення інтегратора на DC */
    double f_z1;           /* Частота першого нуля компенсатора (Гц) */
    double f_z2;           /* Частота другого нуля компенсатора (Гц) */
    double f_p1;           /* Частота першого полюса компенсатора (Гц) */
    double f_p2;           /* Частота другого полюса компенсатора (Гц) */
    bool   avp_enabled;    /* Режим AVP навантажувальної прямої */
    double r_droop;        /* Опір просідання AVP (Ом) */
} VrmModel;

/* Структура кристала та корпусу */
typedef struct {
    double c_die;          /* Внутрішньокристальна ємність (Ф) */
    double r_die;          /* Опір кремнієвої підкладки (Ом) */
    double l_pkg;          /* Індуктивність виводів корпусу BGA (Гн) */
    double r_pkg;          /* Опір металізації корпусу BGA (Ом) */
} DiePackageModel;

/* Структура виявленого резонансного піку */
typedef struct {
    double freq_hz;        /* Частота піку (Гц) */
    double magnitude_z;    /* Модуль імпедансу в піку (Ом) */
    double q_factor;       /* Добротність контуру */
    double margin_db;      /* Запас відносно Z_target (дБ) */
    bool   is_violation;   /* Ознака перевищення цільового імпедансу */
} ResonantPeak;

/* Розрахунок ефективної ємності групи з урахуванням DC-Bias */
double calc_derated_capacitance(const DecouplingGroup* g, double v_dc) {
    if (g->v_sat <= 0.0 || v_dc <= 0.0) {
        return g->nominal_cap;
    }
    double norm_v = v_dc / g->v_sat;
    double denom = pow(1.0 + norm_v * norm_v, g->bias_alpha);
    return g->nominal_cap / denom;
}

/* Розрахунок комплексного імпедансу групи конденсаторів */
double complex calc_group_impedance(const DecouplingGroup* g, double v_dc, double freq_hz) {
    if (g->count <= 0 || freq_hz <= 0.0) {
        return CMPLX(1e9, 0.0);
    }
    double w = 2.0 * M_PI * freq_hz;
    double c_eff = calc_derated_capacitance(g, v_dc);
    
    /* Діелектричні втрати */
    double tan_d = g->tan_delta + 0.008 * log10(fmax(freq_hz, 1000.0) / 1000.0);
    double r_diel = tan_d / (w * c_eff);
    double esr_total = g->esr_nominal + r_diel + g->r_mount;
    double l_total = g->esl_nominal + g->l_mount;
    
    double r_eq = esr_total / (double)g->count;
    double l_eq = l_total / (double)g->count;
    double c_eq = c_eff * (double)g->count;
    
    double x_react = w * l_eq - 1.0 / (w * c_eq);
    return CMPLX(r_eq, x_react);
}

/* Розрахунок вихідного імпедансу стабілізатора VRM */
double complex calc_vrm_impedance(const VrmModel* vrm, double freq_hz, double target_z) {
    double w = 2.0 * M_PI * freq_hz;
    double complex s = CMPLX(0.0, w);
    
    double complex z_open = CMPLX(vrm->r_dc, w * vrm->l_out);
    
    /* Передавальна функція петлі регулювання T(s) */
    double complex num = vrm->a_0 * (1.0 + s / (2.0 * M_PI * vrm->f_z1)) * 
                                    (1.0 + s / (2.0 * M_PI * vrm->f_z2));
    double complex den = s * (1.0 + s / (2.0 * M_PI * vrm->f_p1)) * 
                             (1.0 + s / (2.0 * M_PI * vrm->f_p2));
    double complex t_loop = num / den;
    
    if (vrm->avp_enabled) {
        double r_d = (vrm->r_droop > 0.0) ? vrm->r_droop : target_z;
        return CMPLX(r_d, 0.0) + (z_open - CMPLX(r_d, 0.0)) / (1.0 + t_loop);
    } else {
        return z_open / (1.0 + t_loop);
    }
}

/* Розрахунок імпедансу площин друкованої плати за 2D модальною моделлю */
double complex calc_plane_impedance(const PlaneCavity* plane, double freq_hz) {
    if (!plane->enabled || plane->length_a <= 0.0 || plane->width_b <= 0.0 || plane->thickness_d <= 0.0) {
        return CMPLX(1e9, 0.0);
    }
    double w = 2.0 * M_PI * freq_hz;
    double mu_0 = 4.0 * M_PI * 1e-7;
    double eps_0 = 8.8541878128e-12;
    double sigma_cu = 5.8e7;
    
    double delta_s = sqrt(2.0 / (w * mu_0 * sigma_cu));
    double complex k = w * sqrt(mu_0 * eps_0 * plane->eps_r) * 
                       (1.0 - CMPLX(0.0, 0.5 * (plane->tan_delta + delta_s / plane->thickness_d)));
    double complex k_sq = k * k;
    
    double complex sum = CMPLX(0.0, 0.0);
    double a = plane->length_a;
    double b = plane->width_b;
    double xp = plane->port_x;
    double yp = plane->port_y;
    
    for (int m = 0; m <= plane->max_modes_m; ++m) {
        double eps_m = (m == 0) ? 1.0 : sqrt(2.0);
        double kx = (double)m * M_PI / a;
        double cos_x = cos(kx * xp);
        
        for (int n = 0; n <= plane->max_modes_n; ++n) {
            double eps_n = (n == 0) ? 1.0 : sqrt(2.0);
            double ky = (double)n * M_PI / b;
            double cos_y = cos(ky * yp);
            
            double k_mn_sq = kx * kx + ky * ky;
            double c_term = eps_m * eps_m * eps_n * eps_n * cos_x * cos_x * cos_y * cos_y;
            
            sum += c_term / (k_mn_sq - k_sq);
        }
    }
    double complex coeff = CMPLX(0.0, w * mu_0 * plane->thickness_d / (a * b));
    return coeff * sum;
}

/* Розрахунок повного комплексного імпедансу PDN на заданій частоті */
double complex calc_total_pdn_impedance(
    const PdnSpecification* spec,
    const DecouplingGroup* groups, size_t num_groups,
    const VrmModel* vrm,
    const PlaneCavity* plane,
    const DiePackageModel* die_pkg,
    double freq_hz)
{
    /* Провідність VRM */
    double complex z_vrm = calc_vrm_impedance(vrm, freq_hz, spec->target_z);
    double complex y_pcb = 1.0 / z_vrm;
    
    /* Провідності груп конденсаторів на платі */
    for (size_t i = 0; i < num_groups; ++i) {
        double complex z_grp = calc_group_impedance(&groups[i], spec->v_dd, freq_hz);
        y_pcb += 1.0 / z_grp;
    }
    
    /* Провідність площин плати */
    if (plane->enabled) {
        double complex z_plane = calc_plane_impedance(plane, freq_hz);
        y_pcb += 1.0 / z_plane;
    }
    double complex z_pcb = 1.0 / y_pcb;
    
    /* Додавання паразитів корпусу BGA та кристала */
    double w = 2.0 * M_PI * freq_hz;
    double complex z_pkg = CMPLX(die_pkg->r_pkg, w * die_pkg->l_pkg);
    double complex z_die = CMPLX(die_pkg->r_die, -1.0 / (w * die_pkg->c_die));
    
    /* Паралельне з'єднання ємності кристала з виходом плати крізь індуктивність BGA */
    double complex z_board_pkg = z_pcb + z_pkg;
    double complex z_total = (z_board_pkg * z_die) / (z_board_pkg + z_die);
    return z_total;
}

int main(void) {
    PdnSpecification spec = {
        .v_dd = 0.85,
        .ripple_ratio = 0.03,
        .i_transient = 20.0,
        .t_rise = 400e-12,
        .target_z = (0.85 * 0.03) / 20.0, /* 1.275 мОм */
        .f_knee = 0.35 / 400e-12          /* 875 МГц */
    };
    
    DecouplingGroup groups[MAX_GROUPS] = {
        { .nominal_cap = 470e-6, .esr_nominal = 0.0045, .esl_nominal = 1.2e-9, .l_mount = 0.3e-9, .r_mount = 0.0002, .v_sat = 16.0, .bias_alpha = 0.2, .tan_delta = 0.05, .count = 4,  .label = "4x 470uF Bulk Polymer" },
        { .nominal_cap = 22e-6,  .esr_nominal = 0.0035, .esl_nominal = 0.65e-9, .l_mount = 0.25e-9, .r_mount = 0.0003, .v_sat = 4.0,  .bias_alpha = 1.1, .tan_delta = 0.02, .count = 16, .label = "16x 22uF 0805 X7R" },
        { .nominal_cap = 2.2e-6, .esr_nominal = 0.0050, .esl_nominal = 0.35e-9, .l_mount = 0.18e-9, .r_mount = 0.0004, .v_sat = 3.5,  .bias_alpha = 1.2, .tan_delta = 0.018, .count = 24, .label = "24x 2.2uF 0402 X7R" },
        { .nominal_cap = 0.47e-6,.esr_nominal = 0.0080, .esl_nominal = 0.18e-9, .l_mount = 0.12e-9, .r_mount = 0.0005, .v_sat = 3.0,  .bias_alpha = 1.3, .tan_delta = 0.015, .count = 40, .label = "40x 0.47uF 0306 Rev-Geo" }
    };
    size_t num_groups = 4;
    
    VrmModel vrm = {
        .r_dc = 0.0005,
        .l_out = 0.35e-9,
        .f_crossover = 120e3,
        .a_0 = 1000.0,
        .f_z1 = 25e3,
        .f_z2 = 40e3,
        .f_p1 = 300e3,
        .f_p2 = 1.5e6,
        .avp_enabled = true,
        .r_droop = 0.001275
    };
    
    PlaneCavity plane = {
        .length_a = 0.120,
        .width_b = 0.090,
        .thickness_d = 50e-6,
        .eps_r = 4.1,
        .tan_delta = 0.018,
        .port_x = 0.060,
        .port_y = 0.045,
        .max_modes_m = 8,
        .max_modes_n = 8,
        .enabled = true
    };
    
    DiePackageModel die_pkg = {
        .c_die = 150e-9,
        .r_die = 0.05,
        .l_pkg = 0.08e-9,
        .r_pkg = 0.0003
    };
    
    printf("=================================================================
");
    printf("        КОМПЛЕКСНИЙ АНАЛІЗАТОР ЧАСТОТНОГО ПРОФІЛЮ PDN (C99)
");
    printf("=================================================================
");
    printf("V_dd = %.2f В | I_step = %.1f А | t_rise = %.0f пс
",
           spec.v_dd, spec.i_transient, spec.t_rise * 1e12);
    printf("Z_target = %.6f Ом (%.3f мОм) | f_knee = %.1f МГц

",
           spec.target_z, spec.target_z * 1000.0, spec.f_knee / 1e6);
    
    double f_start = 10.0;
    double f_stop  = 1.0e9;
    int pts_per_dec = 10;
    double step_factor = pow(10.0, 1.0 / (double)pts_per_dec);
    
    double freq_arr[MAX_SWEEP_PTS];
    double mag_arr[MAX_SWEEP_PTS];
    double phase_arr[MAX_SWEEP_PTS];
    size_t pt_count = 0;
    
    for (double f = f_start; f <= f_stop && pt_count < MAX_SWEEP_PTS; f *= step_factor) {
        double complex z = calc_total_pdn_impedance(&spec, groups, num_groups, &vrm, &plane, &die_pkg, f);
        freq_arr[pt_count] = f;
        mag_arr[pt_count] = cabs(z);
        phase_arr[pt_count] = carg(z) * 180.0 / M_PI;
        pt_count++;
    }
    
    /* Пошук резонансних піків */
    ResonantPeak peaks[MAX_PEAKS];
    size_t peak_count = 0;
    
    for (size_t i = 1; i < pt_count - 1 && peak_count < MAX_PEAKS; ++i) {
        if (mag_arr[i] > mag_arr[i - 1] && mag_arr[i] > mag_arr[i + 1]) {
            double margin = 20.0 * log10(spec.target_z / mag_arr[i]);
            peaks[peak_count].freq_hz = freq_arr[i];
            peaks[peak_count].magnitude_z = mag_arr[i];
            peaks[peak_count].margin_db = margin;
            peaks[peak_count].is_violation = (mag_arr[i] > spec.target_z);
            
            /* Розрахунок добротності за шириною на рівні -3 дБ */
            double level_3db = mag_arr[i] / sqrt(2.0);
            double f_low = freq_arr[i - 1];
            double f_high = freq_arr[i + 1];
            for (int k = (int)i; k >= 0; --k) {
                if (mag_arr[k] <= level_3db) { f_low = freq_arr[k]; break; }
            }
            for (size_t k = i; k < pt_count; ++k) {
                if (mag_arr[k] <= level_3db) { f_high = freq_arr[k]; break; }
            }
            double bw = f_high - f_low;
            peaks[peak_count].q_factor = (bw > 0.0) ? (freq_arr[i] / bw) : 1.0;
            peak_count++;
        }
    }
    
    printf("Результати сканування частотного діапазону (вибірка точок):
");
    printf("-----------------------------------------------------------------
");
    printf("   Частота       |Z| (мОм)   Фаза (град)    Статус відносно Z_target
");
    printf("-----------------------------------------------------------------
");
    for (size_t i = 0; i < pt_count; i += 3) {
        printf("%11.2f Гц  |  %8.4f  |  %7.1f    |  %s
",
               freq_arr[i], mag_arr[i] * 1000.0, phase_arr[i],
               (mag_arr[i] > spec.target_z) ? "[!] ПЕРЕВИЩЕННЯ" : "OK (під порогом)");
    }
    
    printf("
Виявлені антирезонансні піки:
");
    printf("-----------------------------------------------------------------
");
    printf(" Частота піку    |Z_peak|      Добротність Q   Запас (дБ)   Вердикт
");
    printf("-----------------------------------------------------------------
");
    bool any_violation = false;
    for (size_t j = 0; j < peak_count; ++j) {
        printf("%10.2f МГц | %7.3f мОм |    Q = %6.2f   | %6.2f дБ | %s
",
               peaks[j].freq_hz / 1e6, peaks[j].magnitude_z * 1000.0,
               peaks[j].q_factor, peaks[j].margin_db,
               peaks[j].is_violation ? "АВАРІЯ (VIOLATION)" : "В МЕЖАХ ДОПУСКУ");
        if (peaks[j].is_violation) any_violation = true;
    }
    
    printf("-----------------------------------------------------------------
");
    if (any_violation) {
        printf("ФІНАЛЬНИЙ ВИСНОВОК: ПОМИЛКА — PDN потребує додаткового демпфування!
");
    } else {
        printf("ФІНАЛЬНИЙ ВИСНОВОК: УСПІХ — Профіль PDN задовольняє всім вимогам.
");
    }
    return 0;
}
