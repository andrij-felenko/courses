/* loading_coil_calc.c - Розрахунок завантажувальної котушки мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double freq_mhz;        /* Робоча частота в МГц */
    double height_m;        /* Висота штиря в метрах */
    double wire_radius_mm;  /* Радіус провідника в мм */
    double ground_loss_ohm; /* Опір втрат у землі/кузові (Ом) */
    double coil_q;          /* Власна добротність котушки (Q) */
    double power_watts;     /* Вхідна потужність передавача (Вт) */
    double coil_diam_cm;    /* Діаметр каркаса котушки (см) */
    double coil_len_cm;     /* Довжина намотки котушки (см) */
} AntennaInputs;

typedef struct {
    double wavelength_m;    /* Довжина хвилі (м) */
    double c_ant_pf;        /* Власна ємність штиря (пФ) */
    double x_c_ohm;         /* Ємнісна реактивність (Ом) */
    double l_coil_uh;       /* Необхідна індуктивність (мкГн) */
    double r_rad_ohm;       /* Опір випромінювання (Ом) */
    double r_coil_ohm;      /* Опір втрат котушки (Ом) */
    double r_total_ohm;     /* Повний опір системи (Ом) */
    double efficiency_pct;  /* ККД випромінювання (%) */
    double q_ant;           /* Добротність антени */
    double bandwidth_khz;   /* Смуга пропускання -3dB (кГц) */
    double v_peak_volts;    /* Пікова напруга на котушці (В) */
    double p_heat_watts;    /* Теплова потужність на котушці (Вт) */
    int turns_count;        /* Кількість витків за Нагаока */
} AntennaResults;

int calculate_loading_coil(const AntennaInputs* in, AntennaResults* out) {
    if (!in || !out) {
        return -1;
    }
    if (in->freq_mhz <= 0.0 || in->height_m <= 0.0 || in->wire_radius_mm <= 0.0 || in->coil_q <= 0.0) {
        return -2;
    }

    const double c_speed = 299792458.0;  /* Швидкість світла в м/с */
    const double eps0 = 8.854187817e-12; /* Електрична стала Ф/м */

    double freq_hz = in->freq_mhz * 1.0e6;
    double omega = 2.0 * M_PI * freq_hz;
    out->wavelength_m = c_speed / freq_hz;

    /* 1. Ємність штиря C_ant за Шелкуновим */
    double wire_radius_m = in->wire_radius_mm / 1000.0;
    double ln_ratio = log(in->height_m / wire_radius_m) - 1.0;
    if (ln_ratio <= 0.2) {
        return -3; /* Геометричне виродження штиря */
    }

    double c_farads = (2.0 * M_PI * eps0 * in->height_m) / ln_ratio;
    out->c_ant_pf = c_farads * 1.0e12;

    /* 2. Ємнісна реактивність та необхідна індуктивність */
    out->x_c_ohm = 1.0 / (omega * c_farads);
    out->l_coil_uh = (out->x_c_ohm / omega) * 1.0e6;

    /* 3. Опори випромінювання та втрат */
    double h_lambda_ratio = in->height_m / out->wavelength_m;
    out->r_rad_ohm = 160.0 * M_PI * M_PI * h_lambda_ratio * h_lambda_ratio;
    out->r_coil_ohm = out->x_c_ohm / in->coil_q;
    out->r_total_ohm = out->r_rad_ohm + in->ground_loss_ohm + out->r_coil_ohm;

    /* 4. ККД, Q-фактор та смуга */
    out->efficiency_pct = (out->r_rad_ohm / out->r_total_ohm) * 100.0;
    out->q_ant = out->x_c_ohm / out->r_total_ohm;
    out->bandwidth_khz = (in->freq_mhz * 1000.0) / out->q_ant;

    /* 5. Висока напруга та теплові втрати */
    double i_ant_rms = sqrt(in->power_watts / out->r_total_ohm);
    double v_rms = i_ant_rms * out->x_c_ohm;
    out->v_peak_volts = v_rms * sqrt(2.0);
    out->p_heat_watts = i_ant_rms * i_ant_rms * out->r_coil_ohm;

    /* 6. Формула Нагаока для обчислення витків */
    double d = in->coil_diam_cm;
    double l = in->coil_len_cm;
    if (d > 0.0 && l > 0.0) {
        double n_squared = (out->l_coil_uh * (45.0 * d + 100.0 * l)) / (2.54 * d * d);
        out->turns_count = (int)ceil(sqrt(n_squared));
    } else {
        out->turns_count = 0;
    }

    return 0;
}

void print_antenna_report(const AntennaInputs* in, const AntennaResults* res) {
    printf("========================================================\n");
    printf("   РЕЗУЛЬТАТИ РОЗРАХУНКУ ЗАВАНТАЖУВАЛЬНОЇ КОТУШКИ (C)   \n");
    printf("========================================================\n");
    printf("Вхідні параметри:\n");
    printf("  Частота: %.2f МГц (λ = %.2f м)\n", in->freq_mhz, res->wavelength_m);
    printf("  Висота штиря h: %.2f м (%.2f%% λ)\n", in->height_m, (in->height_m / res->wavelength_m) * 100.0);
    printf("  Радіус провідника: %.1f мм\n", in->wire_radius_mm);
    printf("  Потужність передавача: %.0f Вт\n", in->power_watts);
    printf("--------------------------------------------------------\n");
    printf("Параметри котушки та імпедансу:\n");
    printf("  Ємність штиря C_ant: %.2f пФ\n", res->c_ant_pf);
    printf("  Реактивний опір X_C: -j%.1f Ом\n", res->x_c_ohm);
    printf("  Необхідна індуктивність L_coil: %.2f мкГн\n", res->l_coil_uh);
    printf("  Каркас D=%.1f см, довжина l=%.1f см  ⇒  %d витків\n", 
           in->coil_diam_cm, in->coil_len_cm, res->turns_count);
    printf("--------------------------------------------------------\n");
    printf("Баланс опорів та ККД:\n");
    printf("  Опір випромінювання R_рад: %.2f Ом\n", res->r_rad_ohm);
    printf("  Опір втрат котушки R_котушки: %.2f Ом\n", res->r_coil_ohm);
    printf("  Опір заземлення/кузова R_землі: %.2f Ом\n", in->ground_loss_ohm);
    printf("  Повний опір R_повн: %.2f Ом\n", res->r_total_ohm);
    printf("  ККД випромінювання η: %.2f %%\n", res->efficiency_pct);
    printf("--------------------------------------------------------\n");
    printf("Характеристики смуги та режими напруги:\n");
    printf("  Добротність антени Q: %.1f\n", res->q_ant);
    printf("  Смуга пропускання BW (-3dB): %.1f кГц\n", res->bandwidth_khz);
    printf("  Теплові втрати на котушці: %.1f Вт\n", res->p_heat_watts);
    printf("  Пікова ВЧ-напруга V_peak: %.0f В (%.2f кВ)\n", 
           res->v_peak_volts, res->v_peak_volts / 1000.0);
    printf("========================================================\n");
}

int main(void) {
    AntennaInputs in = {
        .freq_mhz = 7.10,
        .height_m = 1.80,
        .wire_radius_mm = 2.0,
        .ground_loss_ohm = 4.0,
        .coil_q = 200.0,
        .power_watts = 100.0,
        .coil_diam_cm = 5.0,
        .coil_len_cm = 8.0
    };
    AntennaResults res;

    if (calculate_loading_coil(&in, &res) == 0) {
        print_antenna_report(&in, &res);
    } else {
        fprintf(stderr, "Помилка: некоректні вхідні параметри антени!\n");
        return 1;
    }
    return 0;
}
