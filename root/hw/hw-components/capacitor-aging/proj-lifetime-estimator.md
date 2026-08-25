# ⚙️ Розрахунок залишкового ресурсу та деградації конденсаторів під профілем навантаження

При проєктуванні надійних пристроїв тривалої експлуатації (промислові джерела безперебійного живлення, сонячні інвертори, автомобільні контролери керування тяговим приводом) температура навколишнього середовища та струм пульсацій не є сталими величинами. Вони змінюються залежно від пори року, добового навантаження, режимів охолодження та алгоритмів ШІМ-комутації.

Розрахунок ресурсу за найгіршою точкою максимального навантаження призводить до необґрунтованого завищення габаритів і вартості конденсаторної батареї. Навпаки, розрахунок за середньорічною температурою повністю ігнорує катастрофічний внесок короткочасних пікових перегрівів, оскільки згідно із законом Арреніуса кожні додаткові 10 °C температури серцевини прискорюють знос рівно вдвічі.

Для точного інженерного прогнозування терміну служби фільтрувальних батарей застосовують правило накопичення пошкоджень Пальмгрена-Майнера (англ. *Palmgren-Miner rule*), скомбіноване з логарифмічною моделлю старіння кераміки та законом Арреніуса для електролітів.

## 1. Постановка задачі та математичний алгоритм

Розглядається вихідний фільтр DC-DC перетворювача потужністю 2 кВт (вхід 48 В, вихід 24 В), який працює у цілодобовому промисловому режимі (8760 годин на рік).

Експлуатаційний профіль місії (англ. *Mission Profile*) розбивається на три дискретні температурно-струмові інтервали (біни):
1. **Зимовий та нічний режим низького навантаження:** температура повітря `T_amb = +35 °C`, струм пульсацій `I_rms = 1.2 А`, напрацювання `5000 годин/рік`;
2. **Номінальний денний режим:** температура повітря `T_amb = +55 °C`, струм пульсацій `I_rms = 1.8 А`, напрацювання `3000 годин/рік`;
3. **Піковий літній режим максимальної потужності:** температура повітря `T_amb = +75 °C`, струм пульсацій `I_rms = 2.2 А`, напрацювання `760 годин/рік`.

Необхідно порівняти поведінку трьох альтернативних варіантів реалізації фільтрувальної ємності 470 мкФ:
- Варіант А: Стандартний алюмінієвий електролітичний конденсатор (`2000 годин` при `+105 °C`, `ESR = 65 мОм`);
- Варіант Б: Довговічний алюмінієвий електролітичний конденсатор серії Long-Life (`5000 годин` при `+105 °C`, `ESR = 38 мОм`);
- Варіант В: Керамічна батарея з 10 паралельних MLCC типорозміру 1210 на базі діелектрика X7R (`10 × 47 мкФ = 470 мкФ`, `ESR = 3.5 мОм`, швидкість старіння `k = 2.0 %/декаду`).

### Покрокова послідовність обчислень:

1. **Розрахунок втрат потужності:** для кожного температурного інтервалу `i` обчислюються активні Джоулеві втрати в конденсаторі:
   ```
   P_loss_i = I_rms_i² · ESR
   ```
2. **Розрахунок температури гарячої точки серцевини (hot-spot):**
   ```
   T_core_i = T_amb_i + P_loss_i · R_th
   ```
3. **Розрахунок індивідуального ресурсу для інтервалу `L_i` за правилом 10 градусів:**
   ```
   L_i = L_base · 2^( (T_max − T_core_i) / 10 )
   ```
4. **Акумуляція річної частки пошкодження за правилом Пальмгрена-Майнера:**
   ```
   Damage_annual = ∑ [ Hours_i / L_i ]
   ```
5. **Прогнозування терміну служби до настання EoL (коли сумарне пошкодження досягає 1.0):**
   ```
   Expected_Life_Years = 1.0 / Damage_annual
   ```
6. **Розрахунок залишкової ємності кераміки MLCC через 10 років експлуатації (87 600 годин):**
   ```
   C_10y = C_nom · [ 1 − k · log₁₀( 87600 / 1000 ) ]
   ```

## 2. Програмна реалізація

Нижче наведено повний вихідний код розрахункового інструменту двома мовами програмування: строгому стандартному C (C99/C11) та ідіоматичному сучасному C++ (C++20) з використанням безпечних типів та `std::span`.

:::tabs
```c
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
```
```cpp
#include <iostream>
#include <vector>
#include <string_view>
#include <cmath>
#include <iomanip>
#include <span>

enum class CapType {
    MlccClass2,
    AluElectrolytic,
    AluPolymer,
    FilmPP
};

struct ProfileBin {
    double tAmbientC;      // Температура повітря, °C
    double hoursPerYear;   // Напрацювання за рік, годин
    double iRippleRmsA;   // Струм пульсацій через конденсатор, А
    double vAppliedV;     // Робоча напруга, В
};

struct CapacitorSpec {
    std::string_view name;
    CapType type;
    double cNomUf;        // Номінальна ємність, мкФ
    double vRatedV;       // Номінальна напруга, В
    double esrMohm;        // Початковий опір ESR, мОм
    double rThCPerW;      // Тепловий опір корпус-довкілля, °C/Вт
    double lBaseHours;    // Паспортний ресурс при T_max, годин
    double tMaxC;         // Гранична температура, °C
    double agingRatePct;  // Швидкість старіння MLCC (%/декаду)
};

struct AnalysisResult {
    double annualDamage{0.0};       // Накопичене пошкодження за 1 рік (0.0 .. 1.0)
    double expectedLifeYears{0.0};  // Очікуваний термін служби до EoL, років
    double maxTCoreC{-273.15};      // Максимальна температура серцевини, °C
    double finalCUf{0.0};          // Розрахункова ємність на кінець терміну, мкФ
    double finalEsrMohm{0.0};       // Прогнозований ESR на момент EoL, мОм
    bool isReliable{false};         // Прапор придатності для місії > 10 років
};

// Розрахунок ресурсу електролітичного конденсатора за Арреніусом (правило 10 °C)
[[nodiscard]] constexpr double calculateElecLifetimeHours(const CapacitorSpec& spec, double tCoreC, [[maybe_unused]] double vOpV) noexcept {
    const double deltaT = spec.tMaxC - tCoreC;
    const double afTemp = std::pow(2.0, deltaT / 10.0);
    const double afVoltage = 1.0;
    
    return spec.lBaseHours * afTemp * afVoltage;
}

// Розрахунок логарифмічного старіння кераміки MLCC
[[nodiscard]] inline double calculateMlccCapacitance(const CapacitorSpec& spec, double totalOperatingHours) noexcept {
    if (totalOperatingHours <= 1.0) {
        return spec.cNomUf * (1.0 + (spec.agingRatePct / 100.0) * 3.0);
    }
    
    const double decadesFrom1000h = std::log10(totalOperatingHours / 1000.0);
    const double cFactor = 1.0 - (spec.agingRatePct / 100.0) * decadesFrom1000h;
    
    return spec.cNomUf * cFactor;
}

// Аналіз надійності за профілем навантаження (Palmgren-Miner)
[[nodiscard]] AnalysisResult evaluateCapacitorMission(const CapacitorSpec& spec, std::span<const ProfileBin> profile) {
    AnalysisResult res;
    res.finalCUf = spec.cNomUf;
    res.finalEsrMohm = spec.esrMohm;

    double totalAnnualHours = 0.0;

    for (const auto& bin : profile) {
        totalAnnualHours += bin.hoursPerYear;

        // Втрати потужності та нагрів серцевини
        const double pLossW = std::pow(bin.iRippleRmsA, 2.0) * (spec.esrMohm / 1000.0);
        const double deltaTC = pLossW * spec.rThCPerW;
        const double tCoreC = bin.tAmbientC + deltaTC;

        if (tCoreC > res.maxTCoreC) {
            res.maxTCoreC = tCoreC;
        }

        if (spec.type == CapType::AluElectrolytic || spec.type == CapType::AluPolymer) {
            const double lBinHours = calculateElecLifetimeHours(spec, tCoreC, bin.vAppliedV);
            if (lBinHours > 0.0) {
                res.annualDamage += bin.hoursPerYear / lBinHours;
            }
        }
    }

    if (res.annualDamage > 0.0) {
        res.expectedLifeYears = 1.0 / res.annualDamage;
        res.finalEsrMohm = spec.esrMohm * 2.0; // критерій EoL: подвоєння ESR
        res.finalCUf = spec.cNomUf * 0.80;       // спад ємності на 20 %
    } else {
        res.expectedLifeYears = 25.0; // для MLCC та плівки без висихання
    }

    if (spec.type == CapType::MlccClass2) {
        const double hours10y = 10.0 * (totalAnnualHours > 0.0 ? totalAnnualHours : 8760.0);
        res.finalCUf = calculateMlccCapacitance(spec, hours10y);
    }

    res.isReliable = (res.expectedLifeYears >= 10.0) && (res.maxTCoreC <= spec.tMaxC);
    return res;
}

int main() {
    const std::vector<ProfileBin> profile = {
        { .tAmbientC = 35.0, .hoursPerYear = 5000.0, .iRippleRmsA = 1.2, .vAppliedV = 24.0 },
        { .tAmbientC = 55.0, .hoursPerYear = 3000.0, .iRippleRmsA = 1.8, .vAppliedV = 24.0 },
        { .tAmbientC = 75.0, .hoursPerYear =  760.0, .iRippleRmsA = 2.2, .vAppliedV = 24.0 }
    };

    const std::vector<CapacitorSpec> caps = {
        {
            .name = "Alu-Electrolytic Standard (105°C / 2000h)",
            .type = CapType::AluElectrolytic,
            .cNomUf = 470.0, .vRatedV = 35.0, .esrMohm = 65.0,
            .rThCPerW = 42.0, .lBaseHours = 2000.0, .tMaxC = 105.0,
            .agingRatePct = 0.0
        },
        {
            .name = "Alu-Electrolytic Long-Life (105°C / 5000h)",
            .type = CapType::AluElectrolytic,
            .cNomUf = 470.0, .vRatedV = 35.0, .esrMohm = 38.0,
            .rThCPerW = 36.0, .lBaseHours = 5000.0, .tMaxC = 105.0,
            .agingRatePct = 0.0
        },
        {
            .name = "MLCC Array 10x47uF X7R (125°C)",
            .type = CapType::MlccClass2,
            .cNomUf = 470.0, .vRatedV = 50.0, .esrMohm = 3.5,
            .rThCPerW = 12.0, .lBaseHours = 100000.0, .tMaxC = 125.0,
            .agingRatePct = 2.0
        }
    };

    std::cout << "================================================================================\n";
    std::cout << "  АНАЛІЗ РЕСУРСУ ТА СТАРІННЯ КОНДЕНСАТОРІВ (MISSION PROFILE 8760 год/рік)\n";
    std::cout << "================================================================================\n\n";

    std::cout << std::fixed << std::setprecision(1);
    for (const auto& cap : caps) {
        const auto res = evaluateCapacitorMission(cap, profile);

        std::cout << "Конденсатор: " << cap.name << "\n"
                  << "  Максимальна T_core:      " << std::setw(6) << res.maxTCoreC << " °C (ліміт: " << cap.tMaxC << " °C)\n"
                  << "  Річна витрата ресурсу:   " << std::setw(6) << (res.annualDamage * 100.0) << " %\n"
                  << "  Очікуваний ресурс (EoL): " << std::setw(6) << res.expectedLifeYears << " років\n"
                  << "  Ємність через 10 років:  " << std::setw(6) << res.finalCUf << " мкФ (початкова: " << cap.cNomUf << " мкФ)\n"
                  << "  Статус надійності (10р): " << (res.isReliable ? "ПРИДАТНИЙ (PASS)" : "НЕДОСТАТНІЙ РЕСУРС (FAIL)") << "\n\n";
    }

    return 0;
}
```
:::

## 3. Детальний аналіз результатів моделювання

Виконання програми демонструє драматичну різницю в надійності трьох підходів:

```
================================================================================
  АНАЛІЗ РЕСУРСУ ТА СТАРІННЯ КОНДЕНСАТОРІВ (MISSION PROFILE 8760 год/рік)
================================================================================

Конденсатор: Alu-Electrolytic Standard (105°C / 2000h)
  Максимальна T_core:        88.2 °C (ліміт: 105 °C)
  Річна витрата ресурсу:    23.09 %
  Очікуваний ресурс (EoL):    4.3 років
  Ємність через 10 років:   376.0 мкФ (початкова: 470.0 мкФ)
  Статус надійності (10р): НЕДОСТАТНІЙ РЕСУРС (FAIL)

Конденсатор: Alu-Electrolytic Long-Life (105°C / 5000h)
  Максимальна T_core:        81.6 °C (ліміт: 105 °C)
  Річна витрата ресурсу:     6.45 %
  Очікуваний ресурс (EoL):   15.5 років
  Ємність через 10 років:   376.0 мкФ (початкова: 470.0 мкФ)
  Статус надійності (10р): ПРИДАТНИЙ (PASS)

Конденсатор: MLCC Array 10x47uF X7R (125°C)
  Максимальна T_core:        75.2 °C (ліміт: 125 °C)
  Річна витрата ресурсу:     0.00 %
  Очікуваний ресурс (EoL):   25.0 років
  Ємність через 10 років:   451.7 мкФ (початкова: 470.0 мкФ)
  Статус надійності (10р): ПРИДАТНИЙ (PASS)
```

### Фізичні висновки з моделювання:
1. **Стандартний електролітичний конденсатор** (2000 год) вичерпує свій ресурс уже через **4.3 роки**, незважаючи на те, що 5000 годин на рік він працює за комфортної температури +35 °C. Вирішальний внесок у руйнування дають усього 760 годин роботи при +75 °C: через вищий початковий опір `ESR = 65 мОм` струм пульсацій 2.2 А нагріває його серцевину до `+88.2 °C`. За такої температури 1 година роботи еквівалентна 3.2 годинам роботи при паспортних +105 °C.
2. **Довговічний конденсатор Long-Life** (5000 год) має нижчий опір `ESR = 38 мОм`. Це зменшує Джоулів нагрів удвічі (`ΔT = 6.6 °C` проти `13.2 °C` у стандартного), знижуючи максимальну температуру серцевини до `+81.6 °C`. Завдяки комбінації в 2.5 раза вищого базового ресурсу та нижчої робочої температури підсумковий ресурс зростає у 3.6 раза — до **15.5 років**.
3. **Керамічна батарея MLCC** завдяки мікроскопічному сумарному опору `ESR = 3.5 мОм` взагалі не відчуває внутрішнього самонагріву (`ΔT < 0.2 °C`). Її деградація обмежена виключно релаксацією доменів: за 10 років безперервної служби ємність падає лише з 470 мкФ до 451.7 мкФ (втрата всього 3.9 % від паспортного стану через 1000 годин).

## 4. Гармонійний аналіз несинусоїдальних пульсацій струму

У реальних імпульсних перетворювачах струм через конденсатор є негармонійним:
- У прямоходових та понижувальних перетворювачах (Buck) струм являє собою трикутну пилку;
- У підвищувальних (Boost) та зворотноходових (Flyback) — трапецієподібні імпульси з крутими фронтами;
- У випрямлячах мережі 50 Гц — напівсинусоїдальні куполоподібні імпульси тривалістю 3–5 мс.

Оскільки опір `ESR(f)` має сильну частотну дисперсію (спадає від 100 Гц до 100 кГц у 2–4 рази), сумарні теплові втрати розраховують через розклад струму пульсацій у ряд Фур'є:

```
P_loss_total = ∑ [ I_rms_k² · ESR(f_k) ]
```

де `I_rms_k` — середньоквадратичне значення `k`-ї гармоніки струму, а `ESR(f_k)` — значення активного опору на відповідній частоті `f_k`.

Якщо форма струму відома в часовій області `i(t)`, загальний середньоквадратичний струм визначається інтегралом:

```
I_rms = √[ (1 / T_sw) · ∫[0 .. T_sw] i²(t) dt ]
```

Для трикутної форми струму розмахом `ΔI_pp` середньоквадратичне значення дорівнює `I_rms = ΔI_pp / (2√3) ≈ 0.289 · ΔI_pp`.

## 5. Практичні інженерні пастки при проєктуванні

1. **Частотна дисперсія ESR:**
   Опір `ESR` алюмінієвого електролітичного конденсатора на низьких частотах (100–120 Гц після мостового випрямляча) у 2–4 рази вищий, ніж на високій частоті (100 кГц), через внесок опору діелектричних втрат в оксиді. Якщо розробник розраховує нагрів від мережевих пульсацій 100 Гц за паспортним 100 кГц значенням `ESR`, розрахункові втрати `P_loss` виявляться заниженими у 3 рази, а реальний ресурс скоротиться у 4–8 разів від очікуваного.
2. **Теплове сусідство на друкованій платі:**
   Якщо конденсатор розміщений поруч із гарячим радіатором силового транзистора (MOSFET/IGBT) або планарним трансформатором, тепловий потік через мідні полігони виводів та інфрачервоне випромінювання нагріває корпус додатково на +15...+25 °C. У формулі Арреніуса це означає скорочення терміну служби у 3–5 разів порівняно з розрахунком за середньою температурою повітря всередині шафи.
3. **Суперпозиція DC-bias та логарифмічного старіння кераміки:**
   Для керамічних конденсаторів X7R постійна напруга зміщення зменшує ємність миттєво (наприклад, на 35 % при роботі на 60 % номінальної напруги), після чого починається повільний логарифмічний спад на 2 % на декаду часу. Загальний спад ємності є мультиплікативним добутком обох ефектів.
4. **Вимірювання ESR внутрішньосхемними пробниками:**
   Вимірювання `ESR` безпосередньо на платі без випаювання конденсатора часто дає хибно занижений результат через паралельне шунтування керамічними блокувальними конденсаторами 0.1 мкФ. Для достовірної оцінки деградації вимірювання проводять на частоті 100 кГц після відключення паралельних високочастотних кіл.
5. **Втрата відновлювальної здатності при тривалому знеструмленні:**
   Якщо алюмінієвий електролітичний конденсатор зберігається без напруги понад 2–3 роки за підвищеної вологості, оксидний шар `Al2O3` частково розчиняється в електроліті. Перше ввімкнення під повну робочу напругу викликає гігантський струм витоку, локальне закипання та вибух. Такі компоненти вимагають попереднього технологічного тренування (англ. *re-forming*) плавним підйомом напруги через струмообмежувальний резистор 1 кОм протягом 1–2 годин.
