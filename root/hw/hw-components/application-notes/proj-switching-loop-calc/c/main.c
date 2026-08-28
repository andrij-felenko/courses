#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Вхідна специфікація перетворювача */
typedef struct {
    double v_in;             /* Вхідна напруга, В */
    double v_out;            /* Вихідна напруга, В */
    double i_out;            /* Максимальний струм, А */
    double f_sw;             /* Частота комутації, Гц */
    double l_ind;            /* Індуктивність, Гн */
    double c_out_nom;        /* Номінальна ємність, Ф */
    double esr;              /* Опір ESR, Ом */
    double v_ref;            /* Опорна напруга, В */
    double v_ramp;           /* Розмах пилки ШІМ, В */
    double dc_bias_factor;   /* Залишковий коефіцієнт MLCC (0.0..1.0) */
} buck_spec_t;

/* Розраховані компоненти компенсатора Type III */
typedef struct {
    double f_0;              /* Резонанс LC-фільтра, Гц */
    double f_z_esr;          /* Нуль ESR кераміки, Гц */
    double f_c;              /* Частота зрізу петлі, Гц */
    double r1;               /* Резистор дільника (верхній), Ом */
    double r_bot;            /* Резистор дільника (нижній), Ом */
    double r2;               /* Резистор зворотного зв'язку, Ом */
    double r3;               /* Резистор диференціатора, Ом */
    double c1;               /* Конденсатор HF-полюса, Ф */
    double c2;               /* Конденсатор інтегратора, Ф */
    double c3;               /* Конденсатор нуля, Ф */
    double phase_margin_deg; /* Оціночний запас фази, градуси */
    bool is_stable;          /* Прапорець стійкості (PM > 45°) */
} type3_result_t;

/* Округлення до стандартного ряду E24 (±5%) */
static double round_e24(double val) {
    if (val <= 0.0) return 0.0;
    const double e24_base[24] = {
        1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
        3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1
    };
    double exponent = floor(log10(val));
    double mantissa = val / pow(10.0, exponent);
    
    double best_val = e24_base[0];
    double min_diff = fabs(mantissa - best_val);
    for (int i = 1; i < 24; ++i) {
        double diff = fabs(mantissa - e24_base[i]);
        if (diff < min_diff) {
            min_diff = diff;
            best_val = e24_base[i];
        }
    }
    return best_val * pow(10.0, exponent);
}

/* Синтез компенсатора Type III за методикою Application Note */
bool calculate_type3_compensation(const buck_spec_t* spec, type3_result_t* res) {
    if (!spec || !res) return false;
    if (spec->f_sw <= 0 || spec->l_ind <= 0 || spec->c_out_nom <= 0) return false;

    /* Врахування дератингу ємності кераміки від постійної напруги */
    double c_eff = spec->c_out_nom * (spec->dc_bias_factor > 0 ? spec->dc_bias_factor : 1.0);
    
    /* Критичні частоти силової частини */
    res->f_0 = 1.0 / (2.0 * M_PI * sqrt(spec->l_ind * c_eff));
    res->f_z_esr = 1.0 / (2.0 * M_PI * spec->esr * c_eff);

    /* Цільова частота зрізу (f_sw / 10) */
    res->f_c = spec->f_sw / 10.0;
    if (res->f_c > spec->f_sw / 5.0) {
        res->f_c = spec->f_sw / 5.0; /* Обмеження теоремою Найквіста */
    }

    /* Розміщення полюсів і нулів компенсатора */
    double f_z1 = 0.75 * res->f_0;
    double f_z2 = res->f_0;
    double f_p1 = (res->f_z_esr < spec->f_sw * 0.5) ? res->f_z_esr : spec->f_sw * 0.5;
    double f_p2 = spec->f_sw * 0.5;

    /* Базовий верхній резистор дільника (10 кОм) */
    res->r1 = 10000.0;
    
    /* Нижній резистор дільника для заданої вихідної напруги */
    res->r_bot = round_e24((res->r1 * spec->v_ref) / (spec->v_out - spec->v_ref));

    /* Розрахунок елементів інтегратора та підсилення */
    double r2_raw = (spec->v_ramp * res->f_c * f_p1 * res->r1) / (spec->v_in * res->f_0 * res->f_0);
    res->r2 = round_e24(r2_raw);

    double c2_raw = 1.0 / (2.0 * M_PI * res->r2 * f_z1);
    res->c2 = round_e24(c2_raw);

    double c1_raw = 1.0 / (2.0 * M_PI * res->r2 * f_p1);
    res->c1 = round_e24(c1_raw);

    /* Розрахунок ланцюга високочастотної корекції */
    double r3_raw = res->r1 / ((f_p2 / f_z2) - 1.0);
    res->r3 = round_e24(r3_raw);

    double c3_raw = 1.0 / (2.0 * M_PI * (res->r1 + res->r3) * f_z2);
    res->c3 = round_e24(c3_raw);

    /* Аналітична оцінка фазового запасу на частоті зрізу f_c */
    double phi_plant = -180.0 * (atan2(res->f_c / res->f_0, 1.0 - pow(res->f_c / res->f_0, 2.0)) / M_PI);
    if (phi_plant > 0) phi_plant -= 180.0;
    phi_plant += (atan(res->f_c / res->f_z_esr) * 180.0 / M_PI);

    double phi_comp = -90.0; /* Інтегратор */
    phi_comp += (atan(res->f_c / f_z1) * 180.0 / M_PI);
    phi_comp += (atan(res->f_c / f_z2) * 180.0 / M_PI);
    phi_comp -= (atan(res->f_c / f_p1) * 180.0 / M_PI);
    phi_comp -= (atan(res->f_c / f_p2) * 180.0 / M_PI);

    double total_phase = phi_plant + phi_comp;
    res->phase_margin_deg = 180.0 + total_phase;
    res->is_stable = (res->phase_margin_deg >= 45.0);

    return true;
}

int main(void) {
    buck_spec_t spec = {
        .v_in = 12.0,
        .v_out = 3.3,
        .i_out = 4.0,
        .f_sw = 500000.0,         /* 500 кГц */
        .l_ind = 2.2e-6,          /* 2.2 мкГн */
        .c_out_nom = 66.0e-6,     /* 3 x 22 мкФ */
        .esr = 0.003,             /* 3 мОм */
        .v_ref = 0.8,             /* 0.8 В */
        .v_ramp = 1.2,            /* 1.2 В */
        .dc_bias_factor = 0.65    /* 65% залишкової ємності */
    };

    type3_result_t res;
    if (calculate_type3_compensation(&spec, &res)) {
        printf("=== Результати розрахунку Type III компенсатора ===\n");
        printf("Резонанс LC фільтра:      f_0   = %.2f кГц\n", res.f_0 / 1000.0);
        printf("Нуль ESR кераміки:        f_esr = %.2f кГц\n", res.f_z_esr / 1000.0);
        printf("Частота зрізу петлі:      f_c   = %.2f кГц\n", res.f_c / 1000.0);
        printf("--------------------------------------------------\n");
        printf("R1 = %.1f кОм,  R_bot = %.2f кОм\n", res.r1 / 1000.0, res.r_bot / 1000.0);
        printf("R2 = %.1f кОм,  C2 = %.1f пФ\n", res.r2 / 1000.0, res.c2 * 1e12);
        printf("C1 = %.1f пФ\n", res.c1 * 1e12);
        printf("R3 = %.1f Ом,   C3 = %.1f пФ\n", res.r3, res.c3 * 1e12);
        printf("--------------------------------------------------\n");
        printf("Очікуваний запас фази:    PM = %.1f° (%s)\n",
               res.phase_margin_deg, res.is_stable ? "СТІЙКИЙ" : "НЕСТІЙКИЙ!");
    }
    return 0;
}
