/*
 * battery_calc.c — Інженерний калькулятор терміну служби батареї (C99)
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define MAX_STATES 16

/* Структура одного стану робочого циклу */
typedef struct {
    char name[32];          /* Назва фази (наприклад, "Deep Sleep", "TX") */
    double current_mA;      /* Струм споживання у фазі, мА */
    double duration_ms;     /* Тривалість фази, мілісекунди */
} PowerState;

/* Характеристики джерела живлення */
typedef struct {
    char chemistry_name[32];/* Назва хімії (наприклад, "Li-SOCl2 AA") */
    double nominal_cap_mAh; /* Паспортна ємність, мА·год */
    double ocv_volts;       /* Напруга розімкненого кола (нова), В */
    double ocv_eol_volts;   /* Напруга OCV наприкінці розряду, В */
    double r_int_room_ohm;  /* Внутрішній опір при +25°C, Ом */
    double r_int_cold_ohm;  /* Внутрішній опір при -20°C, Ом */
    double self_discharge_pct_yr; /* Річний саморозряд при +20°C, %/рік */
    double peukert_k;       /* Показник Пойкерта */
    double max_cont_current_mA;   /* Максимальний постійний струм елемента, мА */
} BatterySpec;

/* Параметри системи та навантаження */
typedef struct {
    double uvlo_cutoff_volts;   /* Апаратний поріг вимкнення UVLO, В */
    double design_margin_volts; /* Запас надійності за напругою, В */
    double operating_temp_c;    /* Робоча температура експлуатації, °C */
    double buffer_cap_leakage_uA; /* Струм витоку буферного конденсатора, мкА */
    double engineering_margin;  /* Інженерний коефіцієнт запасу (0.80 - 0.90) */
} SystemParams;

/* Результати розрахунку */
typedef struct {
    double cycle_period_s;          /* Повний період одного циклу, с */
    double charge_per_cycle_uC;     /* Заряд за цикл, мікрокулони */
    double charge_per_cycle_mAh;    /* Заряд за цикл, мА·год */
    double average_current_uA;      /* Середній еквівалентний струм, мкА */
    double load_annual_mAh;         /* Річна витрата навантаження, мА·год */
    double self_discharge_annual_mAh; /* Річний саморозряд хімії, мА·год */
    double cap_leakage_annual_mAh;  /* Річний витік конденсатора, мА·год */
    double total_annual_drain_mAh;  /* Сумарний річний бюджет витрат, мА·год */
    double peak_current_mA;         /* Максимальний піковий струм фази, мА */
    double peak_duration_ms;        /* Тривалість пікового імпульсу, мс */
    double v_drop_raw_volts;        /* Падіння напруги без конденсатора на морозі, В */
    double v_min_terminal_volts;    /* Термінальна напруга під піком без буфера, В */
    bool   uvlo_violation;          /* Прапорець аварійного спрацьовування UVLO */
    bool   buffer_required;         /* Чи необхідний буферний конденсатор */
    double required_buffer_mF;      /* Розрахункова ємність буфера, мФ */
    double derated_usable_cap_mAh;  /* Корисна ємність з урахуванням втрат, мА·год */
    double expected_lifetime_years; /* Розрахунковий час служби, роки */
    double guaranteed_lifetime_years; /* Гарантований час служби із запасом, роки */
} CalculationResult;

/* Функція розрахунку терміну служби */
bool calculate_battery_life(const PowerState states[], size_t state_count,
                            const BatterySpec *bat, const SystemParams *sys,
                            CalculationResult *res)
{
    if (state_count == 0 || bat == NULL || sys == NULL || res == NULL) {
        return false;
    }

    memset(res, 0, sizeof(CalculationResult));

    double total_time_ms = 0.0;
    double total_charge_uC = 0.0;
    double max_current_mA = 0.0;
    double max_curr_duration_ms = 0.0;

    /* 1. Інтегрування заряду за робочим циклом */
    for (size_t i = 0; i < state_count; i++) {
        total_time_ms += states[i].duration_ms;
        /* Заряд у мікрокулонах: струм у мА * час у мс = мкКл */
        double q_state_uC = states[i].current_mA * states[i].duration_ms;
        total_charge_uC += q_state_uC;

        if (states[i].current_mA > max_current_mA) {
            max_current_mA = states[i].current_mA;
            max_curr_duration_ms = states[i].duration_ms;
        }
    }

    res->cycle_period_s = total_time_ms / 1000.0;
    res->charge_per_cycle_uC = total_charge_uC;
    res->charge_per_cycle_mAh = total_charge_uC / 3600.0 / 1000.0;
    res->average_current_uA = (total_charge_uC / (total_time_ms / 1000.0));
    res->peak_current_mA = max_current_mA;
    res->peak_duration_ms = max_curr_duration_ms;

    /* Річна кількість циклів */
    double seconds_per_year = 365.25 * 86400.0;
    double cycles_per_year = seconds_per_year / res->cycle_period_s;
    res->load_annual_mAh = cycles_per_year * res->charge_per_cycle_mAh;

    /* 2. Температурний перерахунок внутрішнього опору */
    double r_int_effective = bat->r_int_room_ohm;
    if (sys->operating_temp_c < 25.0) {
        double delta_t = 25.0 - sys->operating_temp_c;
        /* Експоненційне зростання опору при охолодженні */
        r_int_effective = bat->r_int_room_ohm * exp(0.055 * delta_t);
        if (r_int_effective > bat->r_int_cold_ohm && bat->r_int_cold_ohm > 0.0) {
            r_int_effective = bat->r_int_cold_ohm;
        }
    }

    /* 3. Перевірка просадки напруги під час імпульсу */
    res->v_drop_raw_volts = (max_current_mA / 1000.0) * r_int_effective;
    res->v_min_terminal_volts = bat->ocv_eol_volts - res->v_drop_raw_volts;

    double v_threshold = sys->uvlo_cutoff_volts + sys->design_margin_volts;
    if (res->v_min_terminal_volts < v_threshold || max_current_mA > bat->max_cont_current_mA) {
        res->uvlo_violation = true;
        res->buffer_required = true;

        /* Розрахунок мінімальної ємності буферного конденсатора */
        double delta_v_allow = bat->ocv_eol_volts - sys->uvlo_cutoff_volts - sys->design_margin_volts;
        if (delta_v_allow < 0.1) delta_v_allow = 0.1;

        double pulse_charge_coulombs = (max_current_mA / 1000.0) * (max_curr_duration_ms / 1000.0);
        res->required_buffer_mF = (pulse_charge_coulombs / delta_v_allow) * 1000.0;
    } else {
        res->uvlo_violation = false;
        res->buffer_required = false;
        res->required_buffer_mF = 0.0;
    }

    /* 4. Саморозряд та витоки буфера */
    double temp_factor_sd = 1.0;
    if (sys->operating_temp_c > 20.0) {
        /* Прискорення саморозряду за Арреніусом: подвоєння на кожні 10°C */
        temp_factor_sd = pow(2.0, (sys->operating_temp_c - 20.0) / 10.0);
    }
    double effective_sd_rate = (bat->self_discharge_pct_yr / 100.0) * temp_factor_sd;
    res->self_discharge_annual_mAh = bat->nominal_cap_mAh * effective_sd_rate;

    if (res->buffer_required) {
        res->cap_leakage_annual_mAh = (sys->buffer_cap_leakage_uA / 1000.0) * 8766.0;
    } else {
        res->cap_leakage_annual_mAh = 0.0;
    }

    res->total_annual_drain_mAh = res->load_annual_mAh +
                                  res->self_discharge_annual_mAh +
                                  res->cap_leakage_annual_mAh;

    /* 5. Корисна ємність з урахуванням дервейтингу */
    double k_temp = 1.0;
    if (sys->operating_temp_c < 0.0) {
        k_temp = 1.0 - (0.0 - sys->operating_temp_c) * 0.012;
        if (k_temp < 0.50) k_temp = 0.50;
    }

    double k_peukert = 0.98;
    if (!res->buffer_required && max_current_mA > 20.0) {
        /* Втрати за Пойкертом за відсутності буфера */
        k_peukert = pow(2.0 / max_current_mA, bat->peukert_k - 1.0);
        if (k_peukert < 0.60) k_peukert = 0.60;
    }

    double k_cutoff = 0.95;
    res->derated_usable_cap_mAh = bat->nominal_cap_mAh * k_temp * k_peukert * k_cutoff;

    /* 6. Підсумковий час автономної роботи */
    if (res->total_annual_drain_mAh > 0.0) {
        res->expected_lifetime_years = res->derated_usable_cap_mAh / res->total_annual_drain_mAh;
        res->guaranteed_lifetime_years = res->expected_lifetime_years * sys->engineering_margin;
    }

    return true;
}

/* Друк розгорнутого інженерного звіту */
void print_report(const BatterySpec *bat, const SystemParams *sys, const CalculationResult *res)
{
    printf("====================================================================\n");
    printf("           ЗВІТ РОЗРАХУНКУ ТЕРМІНУ СЛУЖБИ БАТАРЕЇ                   \n");
    printf("====================================================================\n");
    printf("Джерело живлення:         %s (Номінал: %.0f мА·год, OCV: %.2f В)\n",
           bat->chemistry_name, bat->nominal_cap_mAh, bat->ocv_volts);
    printf("Робоча температура:       %.1f °C (R_внутр розрахунковий: %.1f Ом)\n",
           sys->operating_temp_c, (res->v_drop_raw_volts / (res->peak_current_mA / 1000.0)));
    printf("Поріг UVLO системи:       %.2f В (Запас надійності: %.2f В)\n",
           sys->uvlo_cutoff_volts, sys->design_margin_volts);
    printf("--------------------------------------------------------------------\n");
    printf("ХАРАКТЕРИСТИКИ ПРОФІЛЮ НАВАНТАЖЕННЯ:\n");
    printf("  • Період одного циклу:       %.2f с\n", res->cycle_period_s);
    printf("  • Витрата заряду за цикл:    %.4f мкКл (%.6f мА·год)\n",
           res->charge_per_cycle_uC, res->charge_per_cycle_mAh);
    printf("  • Середній струм навантаження: %.2f мкА\n", res->average_current_uA);
    printf("  • Піковий струм імпульсу:    %.1f мА (Тривалість: %.1f мс)\n",
           res->peak_current_mA, res->peak_duration_ms);
    printf("--------------------------------------------------------------------\n");
    printf("ПЕРЕВІРКА ДИНАМІЧНОЇ ПРОСАДКИ НАПРУГИ (БЕЗ БУФЕРА):\n");
    printf("  • Падіння напруги на R_внутр: %.3f В\n", res->v_drop_raw_volts);
    printf("  • Залишкова напруга шини:    %.3f В\n", res->v_min_terminal_volts);
    if (res->uvlo_violation) {
        printf("  [!] УВАГА: ЗАГРОЗА АВАРІЙНОГО ВИМКНЕННЯ UVLO!\n");
        printf("      Напруга просідає нижче критичного порогу %.2f В.\n",
               sys->uvlo_cutoff_volts + sys->design_margin_volts);
        printf("  [+] РЕКОМЕНДОВАНО: встановити буферний конденсатор HLC/EDLC.\n");
        printf("      Мінімальна розрахункова ємність: >= %.1f мФ (%.0f мкФ)\n",
               res->required_buffer_mF, res->required_buffer_mF * 1000.0);
    } else {
        printf("  [OK] Запас напруги достатній. Буферний конденсатор не є обов'язковим.\n");
    }
    printf("--------------------------------------------------------------------\n");
    printf("РІЧНИЙ БЮДЖЕТ СПОЖИВАННЯ ЗАРЯДУ:\n");
    printf("  • Корисне навантаження схеми: %.2f мА·год/рік (%.1f%%)\n",
           res->load_annual_mAh, (res->load_annual_mAh / res->total_annual_drain_mAh) * 100.0);
    printf("  • Хімічний саморозряд батареї: %.2f мА·год/рік (%.1f%%)\n",
           res->self_discharge_annual_mAh, (res->self_discharge_annual_mAh / res->total_annual_drain_mAh) * 100.0);
    if (res->buffer_required) {
        printf("  • Струм витоку конденсатора:  %.2f мА·год/рік (%.1f%%)\n",
               res->cap_leakage_annual_mAh, (res->cap_leakage_annual_mAh / res->total_annual_drain_mAh) * 100.0);
    }
    printf("  • СУМАРНА РІЧНА ВИТРАТА:     %.2f мА·год/рік\n", res->total_annual_drain_mAh);
    printf("--------------------------------------------------------------------\n");
    printf("ПІДСУМКОВА ОЦІНКА АВТОНОМНОСТІ:\n");
    printf("  • Корисна ємність батареї:    %.0f мА·год (з урахуванням втрат)\n",
           res->derated_usable_cap_mAh);
    printf("  • Розрахунковий час роботи:   %.1f років (%.0f місяців)\n",
           res->expected_lifetime_years, res->expected_lifetime_years * 12.0);
    printf("  • ГАРАНТОВАНИЙ ТЕРМІН СЛУЖБИ: %.1f РОКІВ (запас %.0f%%)\n",
           res->guaranteed_lifetime_years, (1.0 - sys->engineering_margin) * 100.0);
    printf("====================================================================\n");
}

int main(void)
{
    /* Визначення профілю споживання бездротового датчика LoRaWAN */
    PowerState states[] = {
        { "Deep Sleep",     0.0025, 59850.0 }, /* 2.5 мкА, 59.85 с */
        { "Wake & Sens",    8.0,       50.0 }, /* 8.0 мА, 50 мс */
        { "Radio TX LoRa", 90.0,       60.0 }, /* 90.0 мА, 60 мс */
        { "Radio RX Ack",  18.0,       40.0 }  /* 18.0 мА, 40 мс */
    };
    size_t state_count = sizeof(states) / sizeof(states[0]);

    /* Характеристики бобінного елемента Li-SOCl2 AA */
    BatterySpec battery = {
        .chemistry_name = "Li-SOCl2 AA (Bobbin)",
        .nominal_cap_mAh = 2400.0,
        .ocv_volts = 3.65,
        .ocv_eol_volts = 3.30,
        .r_int_room_ohm = 3.5,
        .r_int_cold_ohm = 32.0,
        .self_discharge_pct_yr = 1.0,
        .peukert_k = 1.06,
        .max_cont_current_mA = 20.0
    };

    /* Параметри експлуатації взимку */
    SystemParams params = {
        .uvlo_cutoff_volts = 2.20,
        .design_margin_volts = 0.20,
        .operating_temp_c = -15.0,
        .buffer_cap_leakage_uA = 0.8,
        .engineering_margin = 0.85
    };

    CalculationResult result;
    if (calculate_battery_life(states, state_count, &battery, &params, &result)) {
        print_report(&battery, &params, &result);
    } else {
        fprintf(stderr, "Помилка виконання розрахунку.\n");
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
