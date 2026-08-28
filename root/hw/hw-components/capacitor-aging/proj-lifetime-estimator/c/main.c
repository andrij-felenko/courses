#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define MAX_PROFILE_BINS 8

typedef enum {
    CAP_TYPE_MLCC_CLASS2,
    CAP_TYPE_ALU_ELECTROLYTIC,
    CAP_TYPE_ALU_POLYMER,
    CAP_TYPE_FILM_PP
} CapType;

typedef struct {
    double t_ambient_c;    /* Температура повітря, °C */
    double hours_per_year;  /* Напрацювання за рік, годин */
    double i_ripple_rms_a;  /* Струм пульсацій через конденсатор, А */
    double v_applied_v;    /* Робоча напруга, В */
} ProfileBin;

typedef struct {
    const char *name;
    CapType type;
    double c_nom_uf;       /* Номінальна ємність, мкФ */
    double v_rated_v;      /* Номінальна напруга, В */
    double esr_mohm;       /* Початковий опір ESR, мОм */
    double r_th_c_per_w;   /* Тепловий опір корпус-довкілля, °C/Вт */
    double l_base_hours;   /* Паспортний ресурс при T_max, годин */
    double t_max_c;        /* Гранична температура, °C */
    double aging_rate_pct; /* Швидкість старіння MLCC (%/декаду) */
} CapacitorSpec;

typedef struct {
    double annual_damage;      /* Накопичене пошкодження за 1 рік (0.0 .. 1.0) */
    double expected_life_years;/* Очікуваний термін служби до EoL, років */
    double max_t_core_c;       /* Максимальна температура серцевини, °C */
    double final_c_uf;         /* Розрахункова ємність на кінець терміну, мкФ */
    double final_esr_mohm;     /* Прогнозований ESR на момент EoL, мОм */
    bool is_reliable;          /* Прапор придатності для місії > 10 років */
} AnalysisResult;

/* Розрахунок ресурсу електролітичного конденсатора за Арреніусом (правило 10 °C) */
static double calculate_elec_lifetime_hours(const CapacitorSpec *spec, double t_core_c, double v_op_v) {
    (void)v_op_v;
    double delta_t = spec->t_max_c - t_core_c;
    double af_temp = pow(2.0, delta_t / 10.0);
    double af_voltage = 1.0;
    
    return spec->l_base_hours * af_temp * af_voltage;
}

/* Розрахунок логарифмічного старіння кераміки MLCC */
static double calculate_mlcc_capacitance(const CapacitorSpec *spec, double total_operating_hours) {
    if (total_operating_hours <= 1.0) {
        return spec->c_nom_uf * (1.0 + (spec->aging_rate_pct / 100.0) * 3.0);
    }
    
    /* Відлік від паспортних 1000 годин */
    double decades_from_1000h = log10(total_operating_hours / 1000.0);
    double c_factor = 1.0 - (spec->aging_rate_pct / 100.0) * decades_from_1000h;
    
    return spec->c_nom_uf * c_factor;
}

/* Аналіз надійності за профілем навантаження (Palmgren-Miner) */
AnalysisResult evaluate_capacitor_mission(const CapacitorSpec *spec, const ProfileBin *bins, size_t num_bins) {
    AnalysisResult res;
    res.annual_damage = 0.0;
    res.max_t_core_c = -273.15;
    res.final_c_uf = spec->c_nom_uf;
    res.final_esr_mohm = spec->esr_mohm;
    res.is_reliable = false;

    double total_annual_hours = 0.0;

    for (size_t i = 0; i < num_bins; ++i) {
        const ProfileBin *b = &bins[i];
        total_annual_hours += b->hours_per_year;

        /* Втрати потужності та нагрів серцевини */
        double p_loss_w = pow(b->i_ripple_rms_a, 2.0) * (spec->esr_mohm / 1000.0);
        double delta_t_c = p_loss_w * spec->r_th_c_per_w;
        double t_core_c = b->t_ambient_c + delta_t_c;

        if (t_core_c > res.max_t_core_c) {
            res.max_t_core_c = t_core_c;
        }

        if (spec->type == CAP_TYPE_ALU_ELECTROLYTIC || spec->type == CAP_TYPE_ALU_POLYMER) {
            double l_bin_hours = calculate_elec_lifetime_hours(spec, t_core_c, b->v_applied_v);
            if (l_bin_hours > 0.0) {
                res.annual_damage += b->hours_per_year / l_bin_hours;
            }
        }
    }

    if (res.annual_damage > 0.0) {
        res.expected_life_years = 1.0 / res.annual_damage;
        /* На момент EoL опір ESR алюмінієвих конденсаторів зростає щонайменше вдвічі */
        res.final_esr_mohm = spec->esr_mohm * 2.0;
        res.final_c_uf = spec->c_nom_uf * 0.80; /* спад на 20 % */
    } else {
        res.expected_life_years = 25.0; /* для MLCC та плівки без висихання */
    }

    if (spec->type == CAP_TYPE_MLCC_CLASS2) {
        double hours_10y = 10.0 * (total_annual_hours > 0.0 ? total_annual_hours : 8760.0);
        res.final_c_uf = calculate_mlcc_capacitance(spec, hours_10y);
    }

    res.is_reliable = (res.expected_life_years >= 10.0) && (res.max_t_core_c <= spec->t_max_c);
    return res;
}

int main(void) {
    /* 1. Задаємо профіль експлуатації (8760 годин на рік) */
    ProfileBin profile[3] = {
        { .t_ambient_c = 35.0, .hours_per_year = 5000.0, .i_ripple_rms_a = 1.2, .v_applied_v = 24.0 },
        { .t_ambient_c = 55.0, .hours_per_year = 3000.0, .i_ripple_rms_a = 1.8, .v_applied_v = 24.0 },
        { .t_ambient_c = 75.0, .hours_per_year =  760.0, .i_ripple_rms_a = 2.2, .v_applied_v = 24.0 }
    };

    /* 2. Порівнюємо різні типи конденсаторів для вихідного фільтра */
    CapacitorSpec caps[3] = {
        {
            .name = "Alu-Electrolytic Standard (105°C / 2000h)",
            .type = CAP_TYPE_ALU_ELECTROLYTIC,
            .c_nom_uf = 470.0, .v_rated_v = 35.0, .esr_mohm = 65.0,
            .r_th_c_per_w = 42.0, .l_base_hours = 2000.0, .t_max_c = 105.0,
            .aging_rate_pct = 0.0
        },
        {
            .name = "Alu-Electrolytic Long-Life (105°C / 5000h)",
            .type = CAP_TYPE_ALU_ELECTROLYTIC,
            .c_nom_uf = 470.0, .v_rated_v = 35.0, .esr_mohm = 38.0,
            .r_th_c_per_w = 36.0, .l_base_hours = 5000.0, .t_max_c = 105.0,
            .aging_rate_pct = 0.0
        },
        {
            .name = "MLCC Array 10x47uF X7R (125°C)",
            .type = CAP_TYPE_MLCC_CLASS2,
            .c_nom_uf = 470.0, .v_rated_v = 50.0, .esr_mohm = 3.5,
            .r_th_c_per_w = 12.0, .l_base_hours = 100000.0, .t_max_c = 125.0,
            .aging_rate_pct = 2.0
        }
    };

    printf("================================================================================\n");
    printf("  АНАЛІЗ РЕСУРСУ ТА СТАРІННЯ КОНДЕНСАТОРІВ (MISSION PROFILE 8760 год/рік)\n");
    printf("================================================================================\n\n");

    for (size_t i = 0; i < 3; ++i) {
        AnalysisResult res = evaluate_capacitor_mission(&caps[i], profile, 3);

        printf("Конденсатор: %s\n", caps[i].name);
        printf("  Максимальна T_core:      %6.1f °C (ліміт: %.0f °C)\n", res.max_t_core_c, caps[i].t_max_c);
        printf("  Річна витрата ресурсу:   %6.2f %%\n", res.annual_damage * 100.0);
        printf("  Очікуваний ресурс (EoL): %6.1f років\n", res.expected_life_years);
        printf("  Ємність через 10 років:  %6.1f мкФ (початкова: %.1f мкФ)\n", res.final_c_uf, caps[i].c_nom_uf);
        printf("  Статус надійності (10р): %s\n\n", res.is_reliable ? "ПРИДАТНИЙ (PASS)" : "НЕДОСТАТНІЙ РЕСУРС (FAIL)");
    }

    return 0;
}
