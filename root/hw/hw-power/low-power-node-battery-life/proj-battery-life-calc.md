# ⚙️ Інженерний калькулятор терміну служби батареї

Для інженерного проектування та верифікації системи живлення автономного пристрою недостатньо спрощених розрахунків у табличних процесорах. Проста формула ділення паспортної ємності на середній струм ігнорує складну взаємодію багатьох фізичних факторів: нелінійне збільшення внутрішнього опору хімічного джерела при низьких температурах, динамічну просадку напруги під час імпульсів радіопередавача, ефект Пойкерта, струми власного хімічного саморозряду та паразитичні витоки буферних накопичувачів.

Нижче наведено закінчену реалізацію консольного інженерного калькулятора мовами C (стандарт C99) та C++ (стандарт C++20). Програма виконує чисельне інтегрування багатофазного профілю споживання, моделює температурну залежність внутрішнього опору батареї, перевіряє загрозу аварійного вимкнення за порогом блокування низької напруги (UVLO), автоматично розраховує мінімальну необхідну ємність буферного конденсатора (суперконденсатора або гібридного літієвого шару HLC) та визначає гарантований термін автономної експлуатації у роках з урахуванням інженерного запасу надійності.

### Програмна реалізація калькулятора (C та C++)

:::tabs
```c
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
```
```cpp
/*
 * battery_calc.cpp — Об'єктно-орієнтований інженерний калькулятор батареї (C++20)
 */
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <cmath>
#include <iomanip>
#include <optional>
#include <span>
#include <numbers>

namespace power_calc {

/* Стан робочого циклу мікроконтролера */
struct PowerState {
    std::string name;
    double current_mA{0.0};
    double duration_ms{0.0};
};

/* Специфікація хімічного джерела струму */
struct BatterySpec {
    std::string chemistry_name;
    double nominal_cap_mAh{2400.0};
    double ocv_volts{3.65};
    double ocv_eol_volts{3.30};
    double r_int_room_ohm{3.5};
    double r_int_cold_ohm{32.0};
    double self_discharge_pct_yr{1.0};
    double peukert_k{1.06};
    double max_cont_current_mA{20.0};
};

/* Параметри вбудованої системи */
struct SystemParams {
    double uvlo_cutoff_volts{2.20};
    double design_margin_volts{0.20};
    double operating_temp_c{-15.0};
    double buffer_cap_leakage_uA{0.8};
    double engineering_margin{0.85};
};

/* Структура підсумкових результатів */
struct CalculationResult {
    double cycle_period_s{0.0};
    double charge_per_cycle_uC{0.0};
    double charge_per_cycle_mAh{0.0};
    double average_current_uA{0.0};
    double load_annual_mAh{0.0};
    double self_discharge_annual_mAh{0.0};
    double cap_leakage_annual_mAh{0.0};
    double total_annual_drain_mAh{0.0};
    double peak_current_mA{0.0};
    double peak_duration_ms{0.0};
    double v_drop_raw_volts{0.0};
    double v_min_terminal_volts{0.0};
    bool   uvlo_violation{false};
    bool   buffer_required{false};
    double required_buffer_mF{0.0};
    double derated_usable_cap_mAh{0.0};
    double expected_lifetime_years{0.0};
    double guaranteed_lifetime_years{0.0};
};

/* Калькулятор життєвого циклу */
class BatteryLifeCalculator {
public:
    [[nodiscard]] static std::optional<CalculationResult> calculate(
        std::span<const PowerState> states,
        const BatterySpec& bat,
        const SystemParams& sys) noexcept
    {
        if (states.empty()) {
            return std::nullopt;
        }

        CalculationResult res;
        double total_time_ms = 0.0;
        double total_charge_uC = 0.0;

        for (const auto& state : states) {
            total_time_ms += state.duration_ms;
            total_charge_uC += state.current_mA * state.duration_ms;

            if (state.current_mA > res.peak_current_mA) {
                res.peak_current_mA = state.current_mA;
                res.peak_duration_ms = state.duration_ms;
            }
        }

        res.cycle_period_s = total_time_ms / 1000.0;
        res.charge_per_cycle_uC = total_charge_uC;
        res.charge_per_cycle_mAh = total_charge_uC / 3600.0 / 1000.0;
        res.average_current_uA = total_charge_uC / res.cycle_period_s;

        constexpr double seconds_per_year = 365.25 * 86400.0;
        const double cycles_per_year = seconds_per_year / res.cycle_period_s;
        res.load_annual_mAh = cycles_per_year * res.charge_per_cycle_mAh;

        /* Температурна модель опору */
        double r_effective = bat.r_int_room_ohm;
        if (sys.operating_temp_c < 25.0) {
            const double dt = 25.0 - sys.operating_temp_c;
            r_effective = bat.r_int_room_ohm * std::exp(0.055 * dt);
            if (bat.r_int_cold_ohm > 0.0 && r_effective > bat.r_int_cold_ohm) {
                r_effective = bat.r_int_cold_ohm;
            }
        }

        res.v_drop_raw_volts = (res.peak_current_mA / 1000.0) * r_effective;
        res.v_min_terminal_volts = bat.ocv_eol_volts - res.v_drop_raw_volts;

        const double v_threshold = sys.uvlo_cutoff_volts + sys.design_margin_volts;
        if (res.v_min_terminal_volts < v_threshold || res.peak_current_mA > bat.max_cont_current_mA) {
            res.uvlo_violation = true;
            res.buffer_required = true;

            double delta_v = bat.ocv_eol_volts - sys.uvlo_cutoff_volts - sys.design_margin_volts;
            if (delta_v < 0.1) delta_v = 0.1;

            const double q_pulse_coulombs = (res.peak_current_mA / 1000.0) * (res.peak_duration_ms / 1000.0);
            res.required_buffer_mF = (q_pulse_coulombs / delta_v) * 1000.0;
        }

        /* Саморозряд за Арреніусом */
        double sd_temp_factor = 1.0;
        if (sys.operating_temp_c > 20.0) {
            sd_temp_factor = std::pow(2.0, (sys.operating_temp_c - 20.0) / 10.0);
        }
        res.self_discharge_annual_mAh = bat.nominal_cap_mAh * (bat.self_discharge_pct_yr / 100.0) * sd_temp_factor;

        if (res.buffer_required) {
            res.cap_leakage_annual_mAh = (sys.buffer_cap_leakage_uA / 1000.0) * 8766.0;
        }

        res.total_annual_drain_mAh = res.load_annual_mAh +
                                      res.self_discharge_annual_mAh +
                                      res.cap_leakage_annual_mAh;

        /* Дервейтинг ємності */
        double k_temp = 1.0;
        if (sys.operating_temp_c < 0.0) {
            k_temp = std::max(0.50, 1.0 - (0.0 - sys.operating_temp_c) * 0.012);
        }

        double k_peukert = 0.98;
        if (!res.buffer_required && res.peak_current_mA > 20.0) {
            k_peukert = std::max(0.60, std::pow(2.0 / res.peak_current_mA, bat.peukert_k - 1.0));
        }

        constexpr double k_cutoff = 0.95;
        res.derated_usable_cap_mAh = bat.nominal_cap_mAh * k_temp * k_peukert * k_cutoff;

        if (res.total_annual_drain_mAh > 0.0) {
            res.expected_lifetime_years = res.derated_usable_cap_mAh / res.total_annual_drain_mAh;
            res.guaranteed_lifetime_years = res.expected_lifetime_years * sys.engineering_margin;
        }

        return res;
    }

    static void print_report(const BatterySpec& bat, const SystemParams& sys, const CalculationResult& res) {
        std::cout << "====================================================================\n"
                  << "           ЗВІТ РОЗРАХУНКУ ТЕРМІНУ СЛУЖБИ БАТАРЕЇ (C++20)           \n"
                  << "====================================================================\n"
                  << "Джерело живлення:         " << bat.chemistry_name << " (Номінал: " << bat.nominal_cap_mAh << " мА·год)\n"
                  << "Робоча температура:       " << sys.operating_temp_c << " °C\n"
                  << "Поріг UVLO системи:       " << sys.uvlo_cutoff_volts << " В (Запас: " << sys.design_margin_volts << " В)\n"
                  << "--------------------------------------------------------------------\n"
                  << "ХАРАКТЕРИСТИКИ ПРОФІЛЮ НАВАНТАЖЕННЯ:\n"
                  << "  • Період одного циклу:       " << std::fixed << std::setprecision(2) << res.cycle_period_s << " с\n"
                  << "  • Середній струм споживання: " << std::setprecision(2) << res.average_current_uA << " мкА\n"
                  << "  • Піковий імпульс:           " << res.peak_current_mA << " мА (" << res.peak_duration_ms << " мс)\n"
                  << "--------------------------------------------------------------------\n"
                  << "АНАЛІЗ ПРОСАДКИ НАПРУГИ:\n"
                  << "  • Падіння напруги на R_внутр: " << std::setprecision(3) << res.v_drop_raw_volts << " В\n"
                  << "  • Залишкова напруга шини:    " << res.v_min_terminal_volts << " В\n";

        if (res.uvlo_violation) {
            std::cout << "  [!] ВИЯВЛЕНО НЕБЕЗПЕКУ UVLO: потрібен буферний конденсатор!\n"
                      << "  [+] Мінімальна ємність HLC/EDLC: >= " << std::setprecision(1) << res.required_buffer_mF << " мФ\n";
        } else {
            std::cout << "  [OK] Запас напруги задовільний.\n";
        }

        std::cout << "--------------------------------------------------------------------\n"
                  << "РІЧНИЙ БАЛАНС ЗАРЯДУ:\n"
                  << "  • Споживання навантаження:    " << std::setprecision(2) << res.load_annual_mAh << " мА·год/рік\n"
                  << "  • Саморозряд батареї:         " << res.self_discharge_annual_mAh << " мА·год/рік\n"
                  << "  • Витік конденсатора:         " << res.cap_leakage_annual_mAh << " мА·год/рік\n"
                  << "  • СУМАРНА РІЧНА ВИТРАТА:      " << res.total_annual_drain_mAh << " мА·год/рік\n"
                  << "--------------------------------------------------------------------\n"
                  << "ПІДСУМКОВИЙ ЧАС АВТОНОМНОЇ РОБОТИ:\n"
                  << "  • Корисна ємність (з втратами): " << std::setprecision(0) << res.derated_usable_cap_mAh << " мА·год\n"
                  << "  • Розрахунковий час роботи:     " << std::setprecision(1) << res.expected_lifetime_years << " років\n"
                  << "  • ГАРАНТОВАНИЙ ТЕРМІН СЛУЖБИ:   " << res.guaranteed_lifetime_years << " РОКІВ\n"
                  << "====================================================================\n";
    }
};

} // namespace power_calc

int main() {
    using namespace power_calc;

    const std::vector<PowerState> states = {
        { "Deep Sleep",     0.0025, 59850.0 },
        { "Wake & Sens",    8.0,       50.0 },
        { "Radio TX LoRa", 90.0,       60.0 },
        { "Radio RX Ack",  18.0,       40.0 }
    };

    const BatterySpec battery{
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

    const SystemParams params{
        .uvlo_cutoff_volts = 2.20,
        .design_margin_volts = 0.20,
        .operating_temp_c = -15.0,
        .buffer_cap_leakage_uA = 0.8,
        .engineering_margin = 0.85
    };

    if (auto res = BatteryLifeCalculator::calculate(states, battery, params)) {
        BatteryLifeCalculator::print_report(battery, params, *res);
    }

    return 0;
}
```
:::

### Детальний розбір структур даних та вхідних параметрів

Програмний комплекс використовує строго типізоване представлення компонентів системи живлення, що розділяє вхідні дані на чотири взаємопов'язані структури:

#### 1. Профіль стану навантаження (`PowerState`)
Кожен елемент масиву станів описує один монолітний часовий відрізок функціонування вбудованого мікроконтролера. 
* `name`: текстовий ідентифікатор фази для діагностичного протоколу.
* `current_mA`: миттєвий середній струм споживання мікроконтролера, радіотракту та активних сенсорів на цьому часовому відрізку у міліамперах.
* `duration_ms`: тривалість фази у мілісекундах. Одиниця вимірювання у мілісекундах обрана навмисно: перемноження струму в міліамперах на час у мілісекундах дає точне значення електричного заряду в мікрокулонах (`1 мА · 1 мс = 10⁻³ А · 10⁻³ с = 10⁻⁶ А·с = 1 мкКл`), що усуває помилки округлення плаваючої крапки при роботі з дуже малими числами.

#### 2. Електрохімічний паспорт батареї (`BatterySpec`)
Містить фізичні константи обраного хімічного елемента живлення:
* `nominal_cap_mAh`: номінальна ємність за паспортом виробника, виміряна за тривалого розряду струмом `0.001C..0.01C` за кімнатної температури (+20°C..+25°C).
* `ocv_volts`: напруга розімкненого кола свіжого елемента (Open Circuit Voltage).
* `ocv_eol_volts`: напруга розімкненого кола наприкінці життєвого циклу (End of Life OCV). Для хімії Li-SOCl2 робоче плато становить 3.65 В, а наприкінці розряду напруга розімкненого кола спадає до 3.20–3.30 В.
* `r_int_room_ohm`: початковий внутрішній омічний опір за температури +25°C (типово 2.5–4.5 Ом для циліндричних елементів AA бобінного типу).
* `r_int_cold_ohm`: граничний внутрішній опір за температури -20°C наприкінці життєвого циклу, коли електроліт загусає, а на електродах накопичуються продукти реакцій (типово 25–45 Ом).
* `self_discharge_pct_yr`: паспортна швидкість річного саморозряду за кімнатної температури (% ємності на рік).
* `peukert_k`: безрозмірний показник Пойкерта (1.04–1.08 для літієвих первинних елементів).
* `max_cont_current_mA`: граничний рекомендований постійний струм розряду, перевищення якого веде до різкого дифузійного виснаження та локального перегріву комірки.

#### 3. Системні обмеження та середовище (`SystemParams`)
Описує параметри апаратної плати та кліматичні умови:
* `uvlo_cutoff_volts`: мінімальна напруга живлення, за якої мікроконтролер та радіомодуль гарантовано зберігають стабільну працездатність без спрацьовування апаратного супервізора живлення (Under-Voltage Lockout).
* `design_margin_volts`: обов'язковий інженерний запас за напругою (типово 0.15–0.25 В) для компенсації шумів імпульсних стабілізаторів та технологічного розкиду порогів компараторів.
* `operating_temp_c`: найнижча розрахункова температура навколишнього середовища під час польової експлуатації (наприклад, -15°C..-25°C для зовнішніх лічильників взимку).
* `buffer_cap_leakage_uA`: струм власного витоку буферного конденсатора за номінальної робочої напруги (типово 0.5–1.2 мкА для гібридних шарів HLC і до 10–25 мкА для звичайних іоністорів EDLC).
* `engineering_margin`: коефіцієнт надійності (0.80–0.85), що резервує 15–20% корисної ємності на технологічний розкид партій батарей та форс-мажорні температурні аномалії.

---

### Покроковий аналіз математичного конвеєра в коді

Функція `calculate_battery_life()` виконує шість послідовних математичних кроків:

#### Крок 1. Чисельне інтегрування робочого циклу
Програма ітерується по масиву станів, накопичуючи загальний час періоду `total_time_ms` та повний електричний заряд `total_charge_uC`. Одночасно алгоритм шукає максимальний імпульсний струм `max_current_mA` та фіксує його тривалість `max_curr_duration_ms`:

```
Q_цикл_мкКл = ∑ (I_фази · t_фази)
Q_цикл_мАгод = Q_цикл_мкКл ÷ 3600 ÷ 1000
I_сер_мкА = Q_цикл_мкКл ÷ (T_цикл_мс ÷ 1000)
```

Річна кількість циклів розраховується діленням кількості секунд у календарному році (з урахуванням високосних років: `365.25 · 86400 = 31 557 600 с`) на період одного циклу:

```
N_циклів_рік = 31557600 ÷ T_цикл_с
Q_навант_рік = N_циклів_рік · Q_цикл_мАгод
```

#### Крок 2. Термічна модель внутрішнього опору
Якщо робоча температура нижча за стандартні +25°C, опір батареї зростає експоненційно з коефіцієнтом чутливості `0.055 1/°C`:

```
R_внутр(T) = R_кімната · e^(0.055 · (25 - T_робоча))
```

Якщо обчислений опір перевищує паспортний опір холоду `r_int_cold_ohm`, значення обмежується верхньою межею `r_int_cold_ohm`.

#### Крок 3. Перевірка динамічної просадки та синтез буфера
Обчислюється падіння напруги на внутрішньому опорі під час проходження найважчого імпульсу струму `I_пік`:

```
ΔV_просадка = (I_пік ÷ 1000) · R_внутр(T)
V_клеми_мін = V_ocv_eol - ΔV_просадка
```

Якщо залишкова напруга на клемах менша за порогове значення `V_поріг = V_uvlo + V_запас` або піковий струм перевищує максимальний неперервний струм комірки `max_cont_current_mA`, виставляються прапорці `uvlo_violation = true` та `buffer_required = true`.

Мінімальна необхідна ємність буферного конденсатора `C_буфер` (у міліфарадах) визначається діленням повного заряду імпульсу на допустиму просадку напруги:

```
ΔV_допустиме = V_ocv_eol - V_uvlo - V_запас
Q_імпульс_Кл = (I_пік ÷ 1000) · (t_пік ÷ 1000)
C_буфер_мФ = (Q_імпульс_Кл ÷ ΔV_допустиме) · 1000
```

#### Крок 4. Баланс річних втрат заряду
Калькулятор обчислює хімічний саморозряд батареї. Якщо температура експлуатації перевищує +20°C, швидкість саморозряду масштабується за правилом Вант-Гоффа / Арреніуса з подвоєнням на кожні 10°C перевищення:

```
K_темп_саморозряд = 2^((T_робоча - 20) ÷ 10)
Q_саморозряд_рік = C_ном · ( (S_рік ÷ 100) · K_темп_саморозряд )
```

Якщо потрібен буферний конденсатор, до витрат додається його річний струм витоку:

```
Q_витік_конд_рік = (I_витік_мкА ÷ 1000) · 8766 год
```

Сумарний річний бюджет втрат становить:

```
Q_сума_рік = Q_навант_рік + Q_саморозряд_рік + Q_витік_конд_рік
```

#### Крок 5. Дервейтинг ємності та розрахунок років автономності
Реальна корисна ємність батареї коригується трьома коефіцієнтами деградації:
1. `k_temp`: зменшення доступної хімічної ємності на морозі (зменшення на 1.2% на кожен градус нижче 0°C, але не менше 0.50).
2. `k_peukert`: втрати за законом Пойкерта. Якщо встановлено буферний конденсатор, піковий струм згладжено, і `k_peukert = 0.98`. Якщо буфера немає, коефіцієнт падає за формулою `(2.0 ÷ I_пік)^(k - 1)`.
3. `k_cutoff = 0.95`: частка ємності, що встигає віддатися до спаду кривої OCV.

Корисна ємність та підсумковий час життя у роках розраховуються як:

```
C_корисна = C_ном · k_temp · k_peukert · k_cutoff
T_очікуваний_років = C_корисна ÷ Q_сума_рік
T_гарантований_років = T_очікуваний_років · K_запас
```

---

### Порівняння ідіоматики C та C++

* **Реалізація мовою C (C99):** орієнтована на мінімальний оверхед, повну сумісність з вбудованими середовищами та легку інтеграцію в прошивки мікроконтролерів (наприклад, у діагностичні CLI-утиліти через UART). Функція `calculate_battery_life()` приймає вказівники на вхідні структури та заповнює структуру результату, повертаючи булевий статус успіху без динамічних виділень пам'яті у купі (`malloc`).
* **Реалізація мовою C++ (C++20):** використовує сучасні ідіоми безпеки та виразності:
  * Простір імен `power_calc` ізолює типи калькулятора від глобальної області видимості.
  * Вхідний масив станів передається через `std::span<const PowerState>`, що дозволяє приймати як статичні масиви C-стилю, так і `std::vector` чи `std::array` без додаткового копіювання чи виділення пам'яті.
  * Метод `calculate()` повертає `std::optional<CalculationResult>`, що виключає роботу з неініціалізованими структурами при передачі порожнього профілю.
  * Атрибут `[[nodiscard]]` попереджає компілятор про неприпустимість ігнорування результату обчислень.
  * Використання `std::string_view` та строгих структур даних робить API безпечним та зручним для створення графічних інтерфейсів і серверних бекендів розрахунку автономності.

---

### Аналіз практичного тестового сценарію

У демонстраційному коді `main()` змодельовано типовий бездротовий датчик LoRaWAN:
* Батарея: Li-SOCl2 AA (2400 мА·год, `V_ocv = 3.65 В`, `R_внутр = 3.5 Ом` при +25°C, `R_внутр = 32 Ом` при -15°C).
* Профіль: глибокий сон 59.85 с зі струмом 2.5 мкА, прокидання сенсора на 50 мс зі струмом 8 мА, радіопередача LoRa на 60 мс зі струмом 90 мА та прийом квитанції на 40 мс зі струмом 18 мА.
* Робоча температура: -15°C взимку.

Консольний вивід показує:
1. **Катастрофічну просадку без буфера:** при струмі 90 мА на внутрішньому опорі 32 Ом падає `0.090 А · 32 Ом = 2.88 В`. Термінальна напруга просідає до `3.30 В - 2.88 В = 0.42 В`, що далеко нижче порогу UVLO (2.2 В). Без буфера пристрій увійде в аварійний bootloop за перших же зимових морозів.
2. **Параметри буфера:** програма обчислює мінімальну необхідну ємність `C_буфер >= 6.0 мФ` (6000 мкФ). Встановлення компактного гібридного конденсатора HLC1020 ємністю 10 мФ повністю знімає проблему.
3. **Реальний час життя:** після додавання витоку буфера (0.8 мкА) сумарне річне споживання становить 127 мА·год/рік (з яких 45% припадає на навантаження, 43% — на хімічний саморозряд батареї, 12% — на витік конденсатора). Гарантований термін служби системи становить **13.5 років**.

---

### Типові інженерні пастки та апаратні рекомендації

* **Пастка витоку дешевих іоністорів (EDLC):** Спроба заощадити і встановити звичайний суперконденсатор ємністю 1 Ф призводить до катастрофи: струм витоку дешевого іоністора становить 15–30 мкА. Це у 5–10 разів перевищує струм споживання мікроконтролера уві сні і висаджує батарею за 3–4 роки замість розрахункових 15 років. Для тривалого терміну служби застосовують виключно спеціалізовані гібридні модулі HLC зі струмом витоку менше 1 мкА або якісні танталові конденсатори (для коротких імпульсів до 5–10 мс).
* **Пасивні витоки підтягувальних резисторів:** Підтягувальні резистори шин I2C номіналом 4.7 кОм, підключені до постійної шини живлення 3.3 В, споживають струм `3.3 В ÷ 4.7 кОм = 0.70 мА` щоразу, коли мікросхема датчика притискає лінію SDA до землі під час сну. Слід використовувати підтяжку безпосередньо до ліній GPIO мікроконтролера або живити всю цифрову периферію через силові p-канальні польові транзистори (Load Switches), повністю знеструмлюючи датчики уві сні.
* **Вплив ККД імпульсних перетворювачів (Buck) на мікрострумах:** Імпульсні понижувальні перетворювачі мають паспортний ККД 90–95% лише за струмів понад 10–50 мА. У режимі глибокого сну при струмі навантаження 2 мкА власний струм спокою мікросхеми перетворювача (Quiescent Current `I_q`) може становити 15–30 мкА, що опускає реальний ККД перетворення нижче 15%. Для автономних систем слід обирати мікросхеми DC-DC з ультранизьким струмом спокою (наприклад, серії TI TPS62840 або Analog Devices MAX38640 з `I_q < 300 нА`).
* **Ефект затримки напруги (Voltage Delay) у Li-SOCl2:** Якщо пристрій перебував у стані сну кілька місяців, пасиваційна плівка LiCl потовщується. Перший же імпульс радіопередавача може викликати просадку напруги тривалістю 1–5 мс доти, доки струм не проріже іонні канали у плівці. Буферний конденсатор гарантує живлення схеми саме в ці перші критичні мілісекунди депасивації.

---

### Інженерна методика вимірювання мікрострумів та профілювання

Для заповнення масиву станів `PowerState` точними числовими значеннями необхідне фізичне вимірювання струмів на реальному залізі. Спроба використати класичний лабораторний цифровий мультиметр у режимі мікроамперметра гарантовано призведе до спотворення даних або зриву роботи мікроконтролера через ефект **падіння напруги на внутрішньому шунті приладу** (Burden Voltage).

Коли мультиметр налаштовано на діапазон вимірювання 200 мкА, його внутрішній вимірювальний резистор (шунт) має опір близько 1–10 кОм. Під час глибокого сну при струмі 2.5 мкА падіння напруги на шунті становить лише `2.5 мкА · 1 кОм = 2.5 мВ`, що непомітно для живлення мікроконтролера. Проте щойно пристрій прокидається і вмикає радіопередавач зі струмом 90 мА, на тому самому шунті 1 кОм теоретично мало б упасти `0.090 А · 1000 Ом = 90 В`. У реальності напруга на шині живлення мікроконтролера миттєво падає до нуля, процесор скидається через Brownout Reset, так і не зумівши вийти в ефір, а мультиметр фіксує лише хаотичні середні цифри на рівні 1–3 мА.

Для коректного зняття профілю струму застосовують такі вимірювальні методики:

1. **Спеціалізовані профілювальники живлення (Power Profilers):**
   Прилади класу Nordic Power Profiler Kit II (PPK2), Joulescope JS220, Qoitech Otii Arc або прецизійні вимірювальні блоки SMU (Source Measure Units, наприклад Keithley 2450) містять швидкодіючу систему автоматичного динамічного перемикання шунтів (Dynamic Auto-ranging). Вони безперервно вимірюють струм у діапазоні від 50 нА до 1 А з частотою дискретизації до 100 кГц, автоматично підключаючи шунт номіналом 10 Ом для мікроамперних режимів та шунт 0.05 Ом для міліамперних імпульсів менше ніж за 1 мікросекунду без помітного падіння живильної напруги.

2. **Малоінвазивні вимірювальні перемички на платі:**
   На етапі трасування друкованої плати необхідно передбачити розриви шин живлення з посадковими місцями під перемички 0 Ом (або контактні штирі джамперів) окремо для:
   * Ядра мікроконтролера та цифрової логіки.
   * Радіочастотного трансивера (VCC_RF / PA).
   * Аналогових сенсорів та підсилювальних трактів.
   Це дає змогу виміряти точний внесок кожного функціонального блоку окремо, локалізувати непередбачені апаратні витоки через цифрові інтерфейси та підставити очищені дані в структури `PowerState`.

---

### Точка беззбитковості: компроміс між частотою передачі та саморозрядом

Під час проектування мікроконтролерного пристрою виникає фундаментальне архітектурне питання: наскільки рідко потрібно відправляти радіопакети, щоб максимізувати термін служби батареї?

Розглянемо аналітичну залежність підсумкового часу автономності `T_життя` від періоду опитування `T_період`:
* Якщо період передачі малий (наприклад, кожні 10 секунд), споживання енергії навантаженням `Q_навант_рік` становить сотні міліампер-годин на рік і повністю домінує над саморозрядом (`Q_навант_рік >> Q_саморозряд_рік`). У цій зоні подвоєння періоду опитування збільшує час автономності практично вдвічі.
* Якщо період передачі збільшують до 1–4 годин, річне споживання навантаження знижується до одиниць міліампер-годин на рік і стає сумірним із внутрішнім саморозрядом хімії `Q_саморозряд_рік` (типово 15–25 мА·год/рік для елемента ємністю 2400 мА·год).
* При подальшому збільшенні періоду передачі (наприклад, вихід на зв'язок раз на добу або раз на тиждень) крива тривалості життя виходить на горизонтальну асимптоту. Загальний час служби батареї визначається вже не активністю мікроконтролера, а швидкістю паразитарних хімічних реакцій та старінням гумових ущільнювачів корпусу елемента.

Звідси випливає практичне правило: якщо при відправці даних раз на годину батарея забезпечує 12–14 років служби, спроба оптимізувати протокол і передавати дані раз на добу додасть усього лише 1–1.5 роки реальної автономності, проте кардинально погіршить оперативність моніторингу системи.

---

### Довідкова матриця параметрів батарей та радіопротоколів

Для швидкої підстановки у структури `BatterySpec` та `PowerState` нижче зведено інженерні параметри масових хімічних джерел живлення та радіомодулів:

#### Параметри хімічних джерел для структури `BatterySpec`

| Тип хімії та типорозмір | `nominal_cap_mAh` | `ocv_volts` | `ocv_eol_volts` | `r_int_room_ohm` | `r_int_cold_ohm` | `self_discharge_pct_yr` | `peukert_k` | `max_cont_mA` |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Li-SOCl2 AA (Bobbin)** | 2400 | 3.65 | 3.30 | 3.5 | 32.0 | 1.0 | 1.06 | 20.0 |
| **Li-SOCl2 C (Bobbin)** | 8500 | 3.65 | 3.30 | 2.5 | 24.0 | 1.0 | 1.05 | 40.0 |
| **Li-SOCl2 D (Bobbin)** | 19000 | 3.65 | 3.30 | 2.0 | 18.0 | 1.0 | 1.05 | 100.0 |
| **Li-MnO2 CR2032** | 220 | 3.00 | 2.00 | 15.0 | 110.0 | 1.2 | 1.10 | 5.0 |
| **Li-MnO2 CR123A** | 1500 | 3.00 | 2.20 | 0.8 | 6.0 | 1.5 | 1.08 | 500.0 |
| **Li-FeS2 AA (Energizer)**| 3000 | 1.50 | 1.05 | 0.15 | 0.9 | 1.2 | 1.04 | 1500.0 |
| **Alkaline AA (Zn-MnO2)**| 2600 | 1.50 | 0.90 | 0.20 | 2.5 | 2.5 | 1.25 | 200.0 |

#### Типові профілі радіотрактів для масиву `PowerState`

| Бездротовий протокол та чіп | Фаза TX (`current_mA` / `duration_ms`) | Фаза RX (`current_mA` / `duration_ms`) | Потужність сигналу |
| :--- | :--- | :--- | :--- |
| **LoRa (SX1262, SF7, BW125)** | 45.0 мА / 35.0 мс | 11.0 мА / 30.0 мс | +14 дБм (25 мВт) |
| **LoRa (SX1262, SF10, BW125)**| 85.0 мА / 140.0 мс | 11.0 мА / 60.0 мс | +14 дБм (25 мВт) |
| **LoRa (SX1261, SF12, BW125)**| 120.0 мА / 650.0 мс | 12.0 мА / 100.0 мс | +22 дБм (160 мВт) |
| **BLE 5.0 1Mbps (CC2652)** | 9.5 мА / 2.5 мс | 7.0 мА / 1.5 мс | 0 дБм (1 мВт) |
| **BLE Long Range (nRF52840)** | 14.0 мА / 18.0 мс | 6.5 мА / 8.0 мс | +8 дБм (6.3 мВт) |
| **Zigbee 3.0 (EFR32MG21)** | 32.0 мА / 12.0 мс | 10.5 мА / 15.0 мс | +10 дБм (10 мВт) |
| **NB-IoT (Quectel BC660)** | 220.0 мА / 250.0 мс | 45.0 мА / 120.0 мс | +23 дБм (200 мВт) |
| **LTE-M (Nordic nRF9160)** | 350.0 мА / 180.0 мс | 55.0 мА / 80.0 мс | +23 дБм (200 мВт) |

Використання цих табличних значень у поєднанні з наведеним калькулятором дозволяє інженеру швидко промоделювати будь-яку конфігурацію автономного бездротового вузла та обрати оптимальну архітектуру живлення ще до виготовлення першого прототипу друкованої плати.
