#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdbool.h>

#define RF_PI 3.14159265358979323846
#define MAX_SWEEP_POINTS 201

typedef struct {
    double r;
    double i;
} Cplx;

static inline Cplx c_make(double r, double i) { Cplx z = {r, i}; return z; }
static inline Cplx c_add(Cplx a, Cplx b) { return c_make(a.r + b.r, a.i + b.i); }
static inline Cplx c_sub(Cplx a, Cplx b) { return c_make(a.r - b.r, a.i - b.i); }
static inline Cplx c_mul(Cplx a, Cplx b) { return c_make(a.r * b.r - a.i * b.i, a.r * b.i + a.i * b.r); }
static inline Cplx c_div(Cplx a, Cplx b) {
    double d = b.r * b.r + b.i * b.i;
    if (d < 1e-18) d = 1e-18;
    return c_make((a.r * b.r + a.i * b.i) / d, (a.i * b.r - a.r * b.i) / d);
}
static inline double c_mag(Cplx a) { return sqrt(a.r * a.r + a.i * a.i); }
static inline double c_arg_deg(Cplx a) { return atan2(a.i, a.r) * (180.0 / RF_PI); }
static inline Cplx c_inv(Cplx a) { return c_div(c_make(1.0, 0.0), a); }
static inline Cplx c_parallel(Cplx a, Cplx b) {
    Cplx sum = c_add(a, b);
    if (c_mag(sum) < 1e-18) return c_make(0, 0);
    return c_div(c_mul(a, b), sum);
}

typedef struct {
    double freq_hz;
    Cplx s11;
    Cplx z_load;
    double vswr;
    double return_loss_db;
    double mismatch_loss_db;
} RfDataPoint;

typedef struct {
    char name[32];
    bool valid;
    bool is_lowpass;
    double comp1_val; // Послідовний або шунтовий елемент (Ф або Гн)
    char comp1_type;  // 'L' або 'C'
    bool comp1_series; // true якщо послідовний, false якщо шунтовий
    double comp2_val;
    char comp2_type;
    bool comp2_series;
    double comp3_val; // Для П- та T-контурів
    char comp3_type;
    bool comp3_series;
    double q_loaded;
} MatchingTopology;

typedef struct {
    double c_esl_nh;    // Паразитна індуктивність конденсатора, нГн
    double c_esr_ohm;   // Активний опір втрат конденсатора, Ом
    double l_q0;        // Власна добротність котушки на f0
    double l_cp_pf;     // Паразитна паралельна ємність котушки, пФ
    double pad_cap_pf;  // Паразитна ємність монтажного майданчика на землю, пФ
} ParasiticModel;

// Таблиця номіналів ряду E24
static const double E24_SERIES[] = {
    1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
    3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1
};

double snap_to_e24(double val) {
    if (val <= 0.0) return 0.0;
    double dec = pow(10.0, floor(log10(val)));
    double norm = val / dec;
    double best = E24_SERIES[0];
    double min_diff = fabs(norm - E24_SERIES[0]);
    for (int i = 1; i < 24; ++i) {
        double diff = fabs(norm - E24_SERIES[i]);
        if (diff < min_diff) {
            min_diff = diff;
            best = E24_SERIES[i];
        }
    }
    return best * dec;
}

RfDataPoint calc_rf_point(double freq_hz, Cplx s11, double z0) {
    RfDataPoint pt;
    pt.freq_hz = freq_hz;
    pt.s11 = s11;
    double mag = c_mag(s11);
    
    Cplx num = c_add(c_make(1.0, 0.0), s11);
    Cplx den = c_sub(c_make(1.0, 0.0), s11);
    Cplx z_norm = c_div(num, den);
    pt.z_load = c_make(z_norm.r * z0, z_norm.i * z0);
    
    if (mag >= 0.99999) {
        pt.vswr = 999.99;
        pt.return_loss_db = 0.0;
        pt.mismatch_loss_db = 999.99;
    } else {
        pt.vswr = (1.0 + mag) / (1.0 - mag);
        pt.return_loss_db = -20.0 * log10(mag > 1e-6 ? mag : 1e-6);
        double p_ratio = 1.0 - mag * mag;
        pt.mismatch_loss_db = -10.0 * log10(p_ratio > 1e-6 ? p_ratio : 1e-6);
    }
    return pt;
}

int synthesize_l_matches(Cplx z_load, double z0, double freq_hz, MatchingTopology results[4]) {
    int count = 0;
    double r_a = z_load.r;
    double x_a = z_load.i;
    double omega = 2.0 * RF_PI * freq_hz;
    
    if (r_a <= 1e-3 || freq_hz <= 0.0) return 0;
    
    if (r_a < z0) {
        // Конфігурація 1: Послідовна L, шунтова C біля Z0 (Low-Pass)
        double q = sqrt((z0 / r_a) - 1.0);
        double x_s = q * r_a - x_a;
        double b_p = q / z0;
        if (x_s > 0.0 && b_p > 0.0) {
            strcpy(results[count].name, "L-Match (Low-Pass, R_A < Z₀)");
            results[count].valid = true;
            results[count].is_lowpass = true;
            results[count].comp1_type = 'L';
            results[count].comp1_series = true;
            results[count].comp1_val = x_s / omega;
            results[count].comp2_type = 'C';
            results[count].comp2_series = false;
            results[count].comp2_val = b_p / omega;
            results[count].comp3_val = 0.0;
            results[count].q_loaded = q;
            count++;
        }
        // Конфігурація 2: Послідовна C, шунтова L біля Z0 (High-Pass)
        double x_s_hp = -q * r_a - x_a;
        double b_p_hp = -q / z0;
        if (x_s_hp < 0.0 && b_p_hp < 0.0) {
            strcpy(results[count].name, "L-Match (High-Pass, R_A < Z₀)");
            results[count].valid = true;
            results[count].is_lowpass = false;
            results[count].comp1_type = 'C';
            results[count].comp1_series = true;
            results[count].comp1_val = 1.0 / (omega * fabs(x_s_hp));
            results[count].comp2_type = 'L';
            results[count].comp2_series = false;
            results[count].comp2_val = 1.0 / (omega * fabs(b_p_hp));
            results[count].comp3_val = 0.0;
            results[count].q_loaded = q;
            count++;
        }
    } else {
        // Конфігурація 3: Шунтова C біля антени, послідовна L (Low-Pass)
        double q = sqrt((r_a / z0) - 1.0);
        double b_p = q / r_a;
        double x_s = q * z0 - x_a;
        if (b_p > 0.0 && x_s > 0.0) {
            strcpy(results[count].name, "L-Match (Low-Pass, R_A > Z₀)");
            results[count].valid = true;
            results[count].is_lowpass = true;
            results[count].comp1_type = 'C';
            results[count].comp1_series = false;
            results[count].comp1_val = b_p / omega;
            results[count].comp2_type = 'L';
            results[count].comp2_series = true;
            results[count].comp2_val = x_s / omega;
            results[count].comp3_val = 0.0;
            results[count].q_loaded = q;
            count++;
        }
        // Конфігурація 4: Шунтова L біля антени, послідовна C (High-Pass)
        double b_p_hp = -q / r_a;
        double x_s_hp = -q * z0 - x_a;
        if (b_p_hp < 0.0 && x_s_hp < 0.0) {
            strcpy(results[count].name, "L-Match (High-Pass, R_A > Z₀)");
            results[count].valid = true;
            results[count].is_lowpass = false;
            results[count].comp1_type = 'L';
            results[count].comp1_series = false;
            results[count].comp1_val = 1.0 / (omega * fabs(b_p_hp));
            results[count].comp2_type = 'C';
            results[count].comp2_series = true;
            results[count].comp2_val = 1.0 / (omega * fabs(x_s_hp));
            results[count].comp3_val = 0.0;
            results[count].q_loaded = q;
            count++;
        }
    }
    return count;
}

MatchingTopology synthesize_pi_match(Cplx z_load, double z0, double freq_hz, double q_target) {
    MatchingTopology t = {0};
    double r_a = z_load.r;
    double x_a = z_load.i;
    double omega = 2.0 * RF_PI * freq_hz;
    
    double r_min = (r_a < z0) ? r_a : z0;
    double r_v = r_min / (1.0 + q_target * q_target);
    
    if (r_v >= z0 || r_v >= r_a) return t;
    
    double q1 = sqrt((z0 / r_v) - 1.0);
    double q2 = sqrt((r_a / r_v) - 1.0);
    
    double b_p1 = q1 / z0;
    double b_p2 = q2 / r_a;
    double x_s = (q1 * r_v) + (q2 * r_v) - x_a;
    
    if (b_p1 <= 0.0 || b_p2 <= 0.0 || x_s <= 0.0) return t;
    
    strcpy(t.name, "Pi-Match (Low-Pass Harmonic Filter)");
    t.valid = true;
    t.is_lowpass = true;
    t.q_loaded = q_target;
    t.comp1_type = 'C';
    t.comp1_series = false;
    t.comp1_val = b_p1 / omega; // C_shunt1 (Source side)
    t.comp2_type = 'L';
    t.comp2_series = true;
    t.comp2_val = x_s / omega;   // L_series
    t.comp3_type = 'C';
    t.comp3_series = false;
    t.comp3_val = b_p2 / omega; // C_shunt2 (Antenna side)
    return t;
}

Cplx eval_real_cap(double c_val, double freq_hz, const ParasiticModel* p) {
    double omega = 2.0 * RF_PI * freq_hz;
    double esl = p->c_esl_nh * 1e-9;
    double esr = p->c_esr_ohm;
    double x_c = (omega * esl) - (1.0 / (omega * c_val));
    return c_make(esr, x_c);
}

Cplx eval_real_ind(double l_val, double freq_hz, const ParasiticModel* p) {
    double omega = 2.0 * RF_PI * freq_hz;
    double esr = (omega * l_val) / (p->l_q0 > 1.0 ? p->l_q0 : 30.0);
    Cplx z_l_branch = c_make(esr, omega * l_val);
    double cp = p->l_cp_pf * 1e-12;
    if (cp > 1e-15) {
        Cplx z_cp_branch = c_make(0.0, -1.0 / (omega * cp));
        return c_parallel(z_l_branch, z_cp_branch);
    }
    return z_l_branch;
}

void simulate_frequency_sweep(const MatchingTopology* top, Cplx z_antenna_at_f0, double f0, double z0, const ParasiticModel* p) {
    printf("\n=== РЕЗУЛЬТАТИ ЧАСТОТНОЇ РОЗГОРТКИ (SIMULATION SWEEP) ===\n");
    printf("Топологія: %s\n", top->name);
    printf("Частота [МГц] | S₁₁ [дБ] |  КСХ   | Втрати [дБ] | Вхідний Z_in [Ом]\n");
    printf("--------------+----------+--------+-------------+------------------\n");
    
    double f_start = f0 * 0.85;
    double f_stop = f0 * 1.15;
    int steps = 11;
    
    for (int i = 0; i < steps; ++i) {
        double f = f_start + (double)i * (f_stop - f_start) / (steps - 1);
        // Модель навантаження: лінійна апроксимація реактивності антени
        double x_ant = z_antenna_at_f0.i + 2.0 * (f - f0) / f0 * 50.0;
        Cplx z_load = c_make(z_antenna_at_f0.r, x_ant);
        
        Cplx z_node = z_load;
        
        // Для П-контуру: 3 компоненти
        if (top->comp3_val > 0.0) {
            Cplx z_c2 = eval_real_cap(top->comp3_val, f, p);
            z_node = c_parallel(z_node, z_c2);
            Cplx z_l = eval_real_ind(top->comp2_val, f, p);
            z_node = c_add(z_node, z_l);
            Cplx z_c1 = eval_real_cap(top->comp1_val, f, p);
            z_node = c_parallel(z_node, z_c1);
        } else {
            // Для L-контуру
            if (top->comp1_series) {
                Cplx z_s = (top->comp1_type == 'L') ? eval_real_ind(top->comp1_val, f, p) : eval_real_cap(top->comp1_val, f, p);
                z_node = c_add(z_node, z_s);
                Cplx z_p = (top->comp2_type == 'C') ? eval_real_cap(top->comp2_val, f, p) : eval_real_ind(top->comp2_val, f, p);
                z_node = c_parallel(z_node, z_p);
            } else {
                Cplx z_p = (top->comp1_type == 'C') ? eval_real_cap(top->comp1_val, f, p) : eval_real_ind(top->comp1_val, f, p);
                z_node = c_parallel(z_node, z_p);
                Cplx z_s = (top->comp2_type == 'L') ? eval_real_ind(top->comp2_val, f, p) : eval_real_cap(top->comp2_val, f, p);
                z_node = c_add(z_node, z_s);
            }
        }
        
        Cplx s11 = c_div(c_sub(z_node, c_make(z0, 0)), c_add(z_node, c_make(z0, 0)));
        double mag = c_mag(s11);
        double vswr = (mag >= 0.999) ? 99.9 : (1.0 + mag) / (1.0 - mag);
        double rl_db = (mag < 1e-6) ? 80.0 : -20.0 * log10(mag);
        double p_trans = 1.0 - mag * mag;
        double il_db = (p_trans < 1e-6) ? 40.0 : -10.0 * log10(p_trans);
        
        printf("  %7.1f     |  %6.2f  |  %5.2f |    %5.2f    | %5.1f + j%5.1f\n",
               f * 1e-6, -rl_db, vswr, il_db, z_node.r, z_node.i);
    }
}

int main(int argc, char** argv) {
    printf("===================================================================\n");
    printf(" RF IMPEDANCE MATCHING & S11 SYNTHESIS CALCULATOR (C99)\n");
    printf("===================================================================\n");
    
    double f0 = 2440.0 * 1e6; // 2.44 GHz за замовчуванням
    double z0 = 50.0;
    Cplx z_ant = c_make(18.0, -42.0); // Типовий незбалансований імпеданс MIFA антени
    
    if (argc >= 4) {
        f0 = atof(argv[1]) * 1e6;
        z_ant.r = atof(argv[2]);
        z_ant.i = atof(argv[3]);
    }
    
    printf("Параметри розрахунку:\n");
    printf("  Центральна частота f₀: %.2f МГц\n", f0 * 1e-6);
    printf("  Опорний імпеданс Z₀:   %.1f Ом\n", z0);
    printf("  Імпеданс антени Z_A:   %.2f %c j%.2f Ом\n\n", z_ant.r, z_ant.i >= 0 ? '+' : '-', fabs(z_ant.i));
    
    Cplx s11_init = c_div(c_sub(z_ant, c_make(z0, 0)), c_add(z_ant, c_make(z0, 0)));
    RfDataPoint init_pt = calc_rf_point(f0, s11_init, z0);
    
    printf("Вхідні характеристики неузгодженої антени:\n");
    printf("  |S₁₁|:           %.4f (%.2f дБ)\n", c_mag(init_pt.s11), -init_pt.return_loss_db);
    printf("  Фаза S₁₁:        %.1f°\n", c_arg_deg(init_pt.s11));
    printf("  КСХ (VSWR):      %.2f\n", init_pt.vswr);
    printf("  Втрати неузг.:   %.2f дБ\n", init_pt.mismatch_loss_db);
    printf("  Потужність в ан.: %.1f %%\n\n", (1.0 - c_mag(init_pt.s11)*c_mag(init_pt.s11)) * 100.0);
    
    MatchingTopology l_matches[4];
    int l_count = synthesize_l_matches(z_ant, z0, f0, l_matches);
    
    printf("=== СИНТЕЗ ДВОЕЛЕМЕНТНИХ L-КОНТУРІВ ===\n");
    for (int i = 0; i < l_count; ++i) {
        printf("[%d] %s (Q_L = %.2f):\n", i + 1, l_matches[i].name, l_matches[i].q_loaded);
        double v1 = l_matches[i].comp1_val;
        double v2 = l_matches[i].comp2_val;
        if (l_matches[i].comp1_type == 'L') {
            printf("    Елемент 1 (%s): L = %.2f нГн (E24: %.2f нГн)\n",
                   l_matches[i].comp1_series ? "Послідовний" : "Шунтовий", v1 * 1e9, snap_to_e24(v1 * 1e9));
        } else {
            printf("    Елемент 1 (%s): C = %.2f пФ (E24: %.2f пФ)\n",
                   l_matches[i].comp1_series ? "Послідовний" : "Шунтовий", v1 * 1e12, snap_to_e24(v1 * 1e12));
        }
        if (l_matches[i].comp2_type == 'L') {
            printf("    Елемент 2 (%s): L = %.2f нГн (E24: %.2f нГн)\n",
                   l_matches[i].comp2_series ? "Послідовний" : "Шунтовий", v2 * 1e9, snap_to_e24(v2 * 1e9));
        } else {
            printf("    Елемент 2 (%s): C = %.2f пФ (E24: %.2f пФ)\n",
                   l_matches[i].comp2_series ? "Послідовний" : "Шунтовий", v2 * 1e12, snap_to_e24(v2 * 1e12));
        }
    }
    
    MatchingTopology pi_match = synthesize_pi_match(z_ant, z0, f0, 3.0);
    if (pi_match.valid) {
        printf("\n=== СИНТЕЗ ТРЬОХЕЛЕМЕНТНОГО П-КОНТУРУ (Q_L = 3.0) ===\n");
        printf("    C_shunt1 (Source):  %.2f пФ (E24: %.2f пФ)\n", pi_match.comp1_val * 1e12, snap_to_e24(pi_match.comp1_val * 1e12));
        printf("    L_series (Middle):  %.2f нГн (E24: %.2f нГн)\n", pi_match.comp2_val * 1e9, snap_to_e24(pi_match.comp2_val * 1e9));
        printf("    C_shunt2 (Antenna): %.2f пФ (E24: %.2f пФ)\n", pi_match.comp3_val * 1e12, snap_to_e24(pi_match.comp3_val * 1e12));
    }
    
    ParasiticModel parasitics = {
        .c_esl_nh = 0.35,
        .c_esr_ohm = 0.08,
        .l_q0 = 45.0,
        .l_cp_pf = 0.04,
        .pad_cap_pf = 0.05
    };
    
    if (l_count > 0) {
        simulate_frequency_sweep(&l_matches[0], z_ant, f0, z0, &parasitics);
    }
    
    return 0;
}
