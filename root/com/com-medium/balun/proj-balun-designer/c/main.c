#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Структура вхідних даних для розрахунку балуна */
typedef struct {
    double freq_mhz;         /* Робоча частота (МГц) */
    double z0_ohm;           /* Хвильовий опір фідерної лінії (Ом) */
    double target_zcm_ohm;   /* Бажаний опір спільної моди Z_cm (Ом) */
    double power_watts;      /* ВЧ потужність передавача (Вт) */
    double core_al_nh;       /* Коефіцієнт індуктивності осердя A_L (нГн/виток^2) */
    double core_ae_cm2;      /* Ефективна площа перерізу осердя A_e (см^2) */
} balun_input_t;

/* Структура результатів обчислення */
typedef struct {
    double min_l_uh;         /* Необхідна мін. індуктивність L_cm (мкГн) */
    int turns_count;         /* Розрахункова кількість витків N */
    double actual_zcm_ohm;   /* Фактичний опір Z_cm на робочій частоті (Ом) */
    double cmrr_db;          /* Пригнічення спільної моди (дБ) */
    double v_peak;           /* Пікова ВЧ напруга (В) */
    double b_peak_gauss;     /* Пікова магнітна індукція у фериті (Гаусс) */
    int is_saturated;        /* Прапорець ризику насичення (1 - так, 0 - ні) */
} balun_output_t;

/* Функція розрахунку параметрів балуна */
int calculate_balun_params(const balun_input_t *in, balun_output_t *out) {
    if (!in || !out || in->freq_mhz <= 0.0 || in->z0_ohm <= 0.0) {
        return -1;
    }

    double omega = 2.0 * M_PI * (in->freq_mhz * 1e6);
    
    /* 1. Розрахунок мінімально необхідної індуктивності */
    double req_l_h = in->target_zcm_ohm / omega;
    out->min_l_uh = req_l_h * 1e6;

    /* 2. Обчислення кількості витків: N = sqrt( L_nH / A_L ) */
    double req_l_nh = req_l_h * 1e9;
    if (in->core_al_nh > 0.0) {
        out->turns_count = (int)ceil(sqrt(req_l_nh / in->core_al_nh));
        if (out->turns_count < 1) out->turns_count = 1;
    } else {
        out->turns_count = 0;
    }

    /* 3. Фактичний опір та CMRR */
    double actual_l_nh = (double)(out->turns_count * out->turns_count) * in->core_al_nh;
    double actual_l_h = actual_l_nh * 1e-9;
    out->actual_zcm_ohm = omega * actual_l_h;
    
    out->cmrr_db = 20.0 * log10(1.0 + (out->actual_zcm_ohm / (2.0 * in->z0_ohm)));

    /* 4. Розрахунок пікової напруги та магнітної індукції */
    out->v_peak = sqrt(2.0 * in->power_watts * in->z0_ohm);
    
    /* B_peak (Gauss) = (V_peak * 10^8) / (4.44 * f_Hz * A_e_cm2 * N) */
    if (in->core_ae_cm2 > 0.0 && out->turns_count > 0) {
        double f_hz = in->freq_mhz * 1e6;
        out->b_peak_gauss = (out->v_peak * 1e8) / (4.44 * f_hz * in->core_ae_cm2 * (double)out->turns_count);
    } else {
        out->b_peak_gauss = 0.0;
    }

    /* Межа насичення для типових феритів Mix 31/43 становить ~2500 Гаусс (0.25 Тл) */
    out->is_saturated = (out->b_peak_gauss > 2500.0) ? 1 : 0;

    return 0;
}

int main(void) {
    balun_input_t input = {
        .freq_mhz = 14.150,      /* Діапазон 20 метрів (14.15 МГц) */
        .z0_ohm = 50.0,          /* Коаксіал 50 Ом */
        .target_zcm_ohm = 1000.0,/* Цільовий опір Z_cm = 1000 Ом */
        .power_watts = 500.0,    /* Потужність 500 Вт */
        .core_al_nh = 240.0,     /* Осердя FT-240-31 (A_L ≈ 240 нГн/виток^2) */
        .core_ae_cm2 = 1.58      /* Площа перерізу FT-240 A_e = 1.58 см^2 */
    };

    balun_output_t output;
    if (calculate_balun_params(&input, &output) != 0) {
        fprintf(stderr, "Помилка розрахунку параметрів балуна.\n");
        return EXIT_FAILURE;
    }

    printf("=== РОЗРАХУНОК СТРУМОВОГО БАЛУНА ГУАНЕЛЛА (C) ===\n");
    printf("Частота            : %.3f МГц\n", input.freq_mhz);
    printf("Потужність         : %.1f Вт\n", input.power_watts);
    printf("Мін. індуктивність : %.2f мкГн\n", output.min_l_uh);
    printf("Кількість витків N : %d витків\n", output.turns_count);
    printf("Фактичний Z_cm     : %.1f Ом\n", output.actual_zcm_ohm);
    printf("Пригнічення CMRR   : %.2f дБ\n", output.cmrr_db);
    printf("Пікова ВЧ напруга  : %.1f В\n", output.v_peak);
    printf("Магнітна індукція  : %.1f Гаусс\n", output.b_peak_gauss);
    printf("Статус осердя      : %s\n", output.is_saturated ? "УВАГА: Ризик насичення!" : "ОК (Безпечний режим)");

    return EXIT_SUCCESS;
}
