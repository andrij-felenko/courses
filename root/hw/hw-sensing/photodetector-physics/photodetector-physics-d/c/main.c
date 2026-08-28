#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#define CONST_Q       1.602176634e-19 /* Кулон */
#define CONST_H       6.62607015e-34  /* Дж * с */
#define CONST_C       2.99792458e8    /* м / с */
#define CONST_KB      1.380649e-23    /* Дж / К */
#define CONST_EPS0    8.8541878128e-12 /* Ф / м */

typedef struct {
    double wavelength_m;      /* Довжина хвилі світла, м */
    double quantum_efficiency;/* Квантова ефективність eta (0.0 .. 1.0) */
    double area_m2;           /* Площа фоточутливої зони кристала, м^2 */
    double eps_r;             /* Відносна діелектрична проникність (11.7 для Si) */
    double v_bi;              /* Контактна різниця потенціалів, В */
    double v_reverse;         /* Зворотна напруга зміщення, В */
    double n_doping_m3;       /* Концентрація домішок у базі N_d, м^-3 */
    double v_sat_m_s;         /* Швидкість насичення носіїв, м/с (1.0e5 для Si) */
    double r_series_ohm;      /* Послідовний опір кристала й контактів, Ом */
    double r_load_ohm;        /* Опір навантаження / схеми, Ом */
    double r_shunt_ohm;       /* Опір шунтування переходу, Ом */
    double dark_current_a;    /* Темновий струм витоку при заданій напрузі, А */
    double temperature_k;     /* Температура кристала, К */
} PhotodiodeParams;

typedef struct {
    double responsivity_a_w;   /* Спектральна чутливість R(lambda), А/Вт */
    double depletion_width_m;  /* Товщина збідненої області W, м */
    double junction_cap_f;     /* Бар'єрна ємність C_j, Фарад */
    double f_rc_hz;            /* Частота зрізу за RC-постійною, Гц */
    double f_transit_hz;       /* Частота зрізу за часом прольоту, Гц */
    double f_cutoff_3db_hz;    /* Результуюча смуга пропускання -3 дБ, Гц */
    double total_noise_current_a_rthz; /* Густина шуму струму, А / sqrt(Гц) */
    double nep_w_rthz;         /* Еквівалентна потужність шуму NEP, Вт / sqrt(Гц) */
} PhotodiodeResult;

bool calculate_photodiode_physics(const PhotodiodeParams* in, PhotodiodeResult* out) {
    if (!in || !out) return false;
    if (in->wavelength_m <= 0.0 || in->quantum_efficiency <= 0.0 || in->quantum_efficiency > 1.0) return false;
    if (in->area_m2 <= 0.0 || in->n_doping_m3 <= 0.0 || in->v_sat_m_s <= 0.0) return false;

    /* 1. Спектральна чутливість: R(lambda) = (eta * q * lambda) / (h * c) */
    out->responsivity_a_w = (in->quantum_efficiency * CONST_Q * in->wavelength_m) / (CONST_H * CONST_C);

    /* 2. Ширина збідненої зони: W = sqrt( (2 * eps_0 * eps_r * (V_bi + V_R)) / (q * N_d) ) */
    double total_voltage = in->v_bi + in->v_reverse;
    if (total_voltage < 0.0) total_voltage = 0.0;

    double eps_total = CONST_EPS0 * in->eps_r;
    out->depletion_width_m = sqrt((2.0 * eps_total * total_voltage) / (CONST_Q * in->n_doping_m3));

    /* 3. Бар'єрна ємність: C_j = (eps_total * Area) / W */
    if (out->depletion_width_m > 0.0) {
        out->junction_cap_f = (eps_total * in->area_m2) / out->depletion_width_m;
    } else {
        out->junction_cap_f = 0.0;
    }

    /* 4. Гранична частота за RC-постійною: f_RC = 1 / (2 * pi * (R_s + R_load) * C_j) */
    double r_total = in->r_series_ohm + in->r_load_ohm;
    if (r_total > 0.0 && out->junction_cap_f > 0.0) {
        out->f_rc_hz = 1.0 / (2.0 * M_PI * r_total * out->junction_cap_f);
    } else {
        out->f_rc_hz = 0.0;
    }

    /* 5. Гранична частота за часом прольоту: f_transit = 0.443 * v_sat / W */
    if (out->depletion_width_m > 0.0) {
        out->f_transit_hz = (0.443 * in->v_sat_m_s) / out->depletion_width_m;
    } else {
        out->f_transit_hz = 0.0;
    }

    /* 6. Результуюча смуга: 1/f_3dB^2 = 1/f_RC^2 + 1/f_transit^2 */
    if (out->f_rc_hz > 0.0 && out->f_transit_hz > 0.0) {
        double inv_sq = (1.0 / (out->f_rc_hz * out->f_rc_hz)) + (1.0 / (out->f_transit_hz * out->f_transit_hz));
        out->f_cutoff_3db_hz = 1.0 / sqrt(inv_sq);
    } else {
        out->f_cutoff_3db_hz = 0.0;
    }

    /* 7. Густина шумового струму: i_n = sqrt( 2*q*I_dark + 4*kB*T/R_sh ) */
    double shot_noise_sq = 2.0 * CONST_Q * in->dark_current_a;
    double thermal_noise_sq = (in->r_shunt_ohm > 0.0) ? (4.0 * CONST_KB * in->temperature_k / in->r_shunt_ohm) : 0.0;
    out->total_noise_current_a_rthz = sqrt(shot_noise_sq + thermal_noise_sq);

    /* 8. NEP = i_n / R(lambda) */
    if (out->responsivity_a_w > 0.0) {
        out->nep_w_rthz = out->total_noise_current_a_rthz / out->responsivity_a_w;
    } else {
        out->nep_w_rthz = 0.0;
    }

    return true;
}

int main(void) {
    /* Кремнієвий PIN-фотодіод високої швидкодії: площа 0.2 мм^2, зворотне зміщення 10 В */
    PhotodiodeParams si_pd = {
        .wavelength_m       = 850.0e-9,  /* 850 нм (лазерний діод) */
        .quantum_efficiency = 0.82,      /* 82% */
        .area_m2            = 0.2e-6,    /* 0.2 мм^2 */
        .eps_r              = 11.7,      /* Кремній */
        .v_bi               = 0.7,       /* 0.7 В */
        .v_reverse          = 10.0,      /* 10 В зворотного зміщення */
        .n_doping_m3        = 5.0e20,    /* 5e14 см^-3 n-база */
        .v_sat_m_s          = 1.0e5,     /* 10^7 см/с = 10^5 м/с */
        .r_series_ohm       = 12.0,      /* 12 Ом */
        .r_load_ohm         = 50.0,      /* Навантаження 50 Ом */
        .r_shunt_ohm        = 2.0e9,     /* 2 ГОм */
        .dark_current_a     = 0.8e-9,    /* 0.8 нА */
        .temperature_k      = 300.0      /* 300 К (27 °C) */
    };

    PhotodiodeResult res;
    if (calculate_photodiode_physics(&si_pd, &res)) {
        printf("--- Результати розрахунку фотодіода ---\n");
        printf("Спектральна чутливість R(850 нм): %.4f А/Вт\n", res.responsivity_a_w);
        printf("Товщина збідненої області W:     %.2f мкм\n", res.depletion_width_m * 1e6);
        printf("Бар'єрна ємність переходу C_j:   %.2f пФ\n", res.junction_cap_f * 1e12);
        printf("Частотний зріз за RC (f_RC):     %.2f МГц\n", res.f_rc_hz * 1e-6);
        printf("Частотний зріз за дрейфом:       %.2f МГц\n", res.f_transit_hz * 1e-6);
        printf("Підсумкова смуга (-3 дБ):        %.2f МГц\n", res.f_cutoff_3db_hz * 1e-6);
        printf("Густина шуму струму:             %.3e А/sqrt(Гц)\n", res.total_noise_current_a_rthz);
        printf("Еквівалентна потужність шуму NEP: %.3e Вт/sqrt(Гц)\n", res.nep_w_rthz);
    }
    return 0;
}
