# ⚙️ Моделювання процесів електролізу: розрахунок осадження, газовідділення та балансу напруги

Математична та програмна модель електролітичної комірки зв'язує фізико-хімічні параметри процесу з підсумковими показниками установки. Модель дозволяє у цифровому вигляді розраховувати кінетику осадження металу, товщину гальванічного покриття у мікронах, об'єм виділених побічних газів, повний баланс прикладеної напруги з урахуванням ефекту замикання бульбашками та підсумковий енергетичний ККД установки.

## Завдання та інженерна постановка проблеми

Під час проектування промислових електролізерів або розробки програмного забезпечення для автоматизованих систем управління гальванічними лініями перед інженером постає завдання точного розрахунку параметрів процесу:

1. **Масоперенос та товщина шару**: скільки грамів металу буде осаджено за заданий час, яка товщина покриття утвориться на деталі складної конфігурації та чи не перевищить вона допуски креслення?
2. **Газовий баланс**: який об'єм побічних газів (водню `H₂` або хлору `Cl₂`) виділиться у вентиляційну систему реактора і яку потужність витяжки слід забезпечити задля пожежної безпеки?
3. **Енергетичний бюджет**: яка повна напруга знадобиться від джерела живлення при заданій сили струму і скільки кіловат-годин електроенергії витратиться на один кілограм готової продукції?

Для вирішення цих задач будується комплексна математична модель, що об'єднує закони Фарадея, рівняння міжфазної кінетики Тафеля та геометрію переносу в рідинах.

## Математичні основи моделі

Програма обчислює параметри процесу у шість послідовних етапів.

### Етап 1. Кулонометрія та маса за Фарадеєм

Загальний пропущений заряд `q` (в Кулонах) обчислюється як добуток сили струму `I` на час `t`:

```
q = I · t
```

Теоретична маса осадженого металу `m[theo]` визначається за законом Фарадея:

```
m[theo] = (M · q) / (z · F)
```

де `M` — молярна маса металу (г/моль), `z` — валентність іона, а `F = 96485.33 Кл/моль` — стала Фарадея. Реальна маса `m[act]` враховує вихід за струмом `η[F]` (коефіцієнт Фарадея `0.0 .. 1.0`):

```
m[act] = m[theo] · η[F]
```

### Етап 2. Геометрія осадженого покриття

Об'єм осадженого металу `V[metal]` (в см³) визначається з його маси та густини `ρ`:

```
V[metal] = m[act] / ρ
```

Товщина покриття `h` (у мікронах, мкм) на деталі з робочою площею `S` (см²) обчислюється як:

```
h = (V[metal] / S) · 10000.0
```

### Етап 3. Виділення побічного газу

Частка струму `(1.0 - η[F])` витрачається на побічні реакції (найчастіше на виділення водню на катоді `2H⁺ + 2e⁻ → H₂`). Молярна кількість виділеного газу `n[gas]` становить:

```
n[gas] = (q / F) · ((1.0 - η[F]) / 2.0)
```

Об'єм газу `V[gas]` за нормальних умов (л) дорівнює:

```
V[gas] = n[gas] · 22.414
```

### Етап 4. Омічний опір розчину та ефект Бруггемана

Опір рідкого електроліту `R[sol]` залежить від питомого опору `ρ[sol]`, відстані між електродами `d` та площі `S`:

```
R[sol] = (ρ[sol] · d) / S
```

Проте при активному виділенні газу бульбашки заповнюють міжпросторовий зазор, зменшуючи провідний переріз рідини. Ефективний питомий опір `ρ[eff]` розраховується за **формулою Бруггемана**:

```
ρ[eff] = ρ[sol] / (1.0 - ε)^1.5
```

де `ε` — об'ємна частка газових бульбашок у міжелектродному просторі (типово `0.05 .. 0.20`).

### Етап 5. Кінетичні перенапруги Тафеля

Анодна `η[anode]` та катодна `η[cath]` перенапруги обчислюються за логарифмічним рівнянням Тафеля від густини струму `j = I / S` (А/см²):

```
η[anode] = a[anode] + b[anode] · lg(j)
η[cath]  = a[cath]  + b[cath]  · lg(j)
```

### Етап 6. Підсумковий баланс напруги та ККД

Повна прикладена напруга клем бака `V[applied]`:

```
V[applied] = E⁰[cell] + η[anode] + η[cath] + I · R[sol,eff]
```

Енергетичний ККД установки `η[Energy]` та питома витрата електроенергії `W[spec]` (кВт·год/кг):

```
η[Energy] = η[F] · (E⁰[cell] / V[applied]) · 100%
W[spec] = (V[applied] · I · t) / (3600.0 · m[act])
```

## Реалізація моделі мовами C та C++

Нижче наведено повністю автономні, ідіоматичні реалізації моделі для використання в вбудованих контролерах (C) та симуляційних інженерних пакетах (C++23).

:::tabs
```c
#include <stdio.h>
#include <math.h>

/* Фізичні константи */
#define FARADAY_CONST 96485.33215  /* Кл/моль */
#define MOLAR_GAS_VOL 22.414       /* л/моль за НУ */

/* Структура параметрів речовини */
typedef struct {
    double molar_mass_g;    /* Молярна маса, г/моль */
    int valence;            /* Заряд іона z */
    double density_g_cm3;   /* Густина металу, г/см³ */
    double faraday_eff;     /* Вихід за струмом (0.0 .. 1.0) */
} IonParams;

/* Структура геометрії та електроліту */
typedef struct {
    double area_cm2;        /* Площа електрода, см² */
    double distance_cm;     /* Відстань між електродами, см */
    double resist_ohm_cm;   /* Питомий опір електроліту, Ом·см */
    double bubble_fraction; /* Газовміст ε (0.0 .. 0.3) */
    double e0_cell_v;       /* Рівноважна напруга розкладу, В */
    double tafel_a_anode;   /* Константа Тафеля a для анода, В */
    double tafel_b_anode;   /* Константа Тафеля b для анода, В */
    double tafel_a_cath;    /* Константа Тафеля a для катода, В */
    double tafel_b_cath;    /* Константа Тафеля b для катода, В */
} CellConfig;

/* Результати моделювання */
typedef struct {
    double total_charge_c;      /* Пропущений заряд, Кл */
    double mass_deposited_g;    /* Маса осадженого металу, г */
    double thickness_um;        /* Товщина покриття, мкм */
    double gas_volume_liters;   /* Об'єм виділеного газу при НУ, л */
    double overpotential_anode; /* Анодна перенапруга, В */
    double overpotential_cath;  /* Катодна перенапруга, В */
    double ohmic_drop_v;        /* Омічне падіння напруги, В */
    double applied_voltage_v;   /* Повна прикладена напруга, В */
    double total_energy_wh;     /* Витрачена енергія, Вт·год */
    double specific_energy_kwh_kg; /* Питома витрата енергії, кВт·год/кг */
    double energy_efficiency_pct;  /* Енергетичний ККД, % */
} SimResult;

/* Функція моделювання розрахунку електролізу */
int simulate_electrolysis(const IonParams* ion, const CellConfig* cell,
                          double current_a, double time_sec, SimResult* res) {
    if (!ion || !cell || !res || current_a <= 0.0 || time_sec <= 0.0) {
        return -1;
    }

    /* 1. Розрахунок заряду та маси за законом Фарадея */
    res->total_charge_c = current_a * time_sec;
    
    double mass_theo_g = (ion->molar_mass_g * res->total_charge_c) / 
                         (ion->valence * FARADAY_CONST);
    res->mass_deposited_g = mass_theo_g * ion->faraday_eff;

    /* 2. Товщина гальванічного покриття у мікронах (1 см = 10000 мкм) */
    double volume_cm3 = res->mass_deposited_g / ion->density_g_cm3;
    res->thickness_um = (volume_cm3 / cell->area_cm2) * 10000.0;

    /* 3. Об'єм побічного газу (наприклад, H₂ при z_gas = 2) */
    double moles_electrons = res->total_charge_c / FARADAY_CONST;
    double moles_gas = (moles_electrons / 2.0) * (1.0 - ion->faraday_eff);
    res->gas_volume_liters = moles_gas * MOLAR_GAS_VOL;

    /* 4. Розрахунок густини струму (А/см²) */
    double current_density = current_a / cell->area_cm2;

    /* 5. Обчислення перенапруг за рівнянням Тафеля η = a + b * lg(j) */
    res->overpotential_anode = cell->tafel_a_anode + 
                               cell->tafel_b_anode * log10(current_density);
    res->overpotential_cath = cell->tafel_a_cath + 
                              cell->tafel_b_cath * log10(current_density);
    if (res->overpotential_anode < 0.0) res->overpotential_anode = 0.0;
    if (res->overpotential_cath < 0.0) res->overpotential_cath = 0.0;

    /* 6. Омічний опір розчину з урахуванням газовмісту за Бруггеманом */
    double eps = cell->bubble_fraction;
    if (eps < 0.0) eps = 0.0;
    if (eps > 0.4) eps = 0.4;
    double eff_resist = cell->resist_ohm_cm / pow(1.0 - eps, 1.5);
    double r_solution = (eff_resist * cell->distance_cm) / cell->area_cm2;
    res->ohmic_drop_v = current_a * r_solution;

    /* 7. Повна прикладена напруга */
    res->applied_voltage_v = cell->e0_cell_v + res->overpotential_anode + 
                             res->overpotential_cath + res->ohmic_drop_v;

    /* 8. Енергетичні характеристики */
    res->total_energy_wh = (res->applied_voltage_v * current_a * time_sec) / 3600.0;
    
    if (res->mass_deposited_g > 0.0) {
        res->specific_energy_kwh_kg = (res->total_energy_wh / 1000.0) / 
                                      (res->mass_deposited_g / 1000.0);
    } else {
        res->specific_energy_kwh_kg = 0.0;
    }

    res->energy_efficiency_pct = ion->faraday_eff * 
                                 (cell->e0_cell_v / res->applied_voltage_v) * 100.0;

    return 0;
}

int main(void) {
    /* Налаштування для покриття міддю (Cu²⁺ z=2) */
    IonParams copper = {
        .molar_mass_g = 63.546,
        .valence = 2,
        .density_g_cm3 = 8.96,
        .faraday_eff = 0.96
    };

    CellConfig bath = {
        .area_cm2 = 250.0,        /* Деталь площею 250 см² */
        .distance_cm = 10.0,      /* Відстань 10 см */
        .resist_ohm_cm = 4.5,     /* Розчин CuSO₄ + H₂SO₄ */
        .bubble_fraction = 0.08,  /* 8% газів у об'ємі */
        .e0_cell_v = 0.89,
        .tafel_a_anode = 0.35,
        .tafel_b_anode = 0.12,
        .tafel_a_cath = 0.15,
        .tafel_b_cath = 0.08
    };

    SimResult res;
    double current = 12.5;        /* Струм 12.5 А */
    double duration = 3600.0;     /* 1 година = 3600 с */

    if (simulate_electrolysis(&copper, &bath, current, duration, &res) == 0) {
        printf("=== Результати симуляції електролізу міді ===\n");
        printf("Пропущений заряд:     %.2f Кл\n", res.total_charge_c);
        printf("Маса осадженої міді:  %.3f г\n", res.mass_deposited_g);
        printf("Товщина покриття:     %.2f мкм\n", res.thickness_um);
        printf("Виділений водень H2:  %.3f л\n", res.gas_volume_liters);
        printf("Перенапруга анода:    %.3f В\n", res.overpotential_anode);
        printf("Перенапруга катода:   %.3f В\n", res.overpotential_cath);
        printf("Омічне падіння IR:    %.3f В\n", res.ohmic_drop_v);
        printf("Повна напруга бака:   %.3f В\n", res.applied_voltage_v);
        printf("Витрачено енергії:    %.2f Вт·год\n", res.total_energy_wh);
        printf("Питома енергія:       %.2f кВт·год/кг\n", res.specific_energy_kwh_kg);
        printf("Енергетичний ККД:     %.1f %%\n", res.energy_efficiency_pct);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <iomanip>
#include <cmath>
#include <expected>
#include <string_view>

namespace electrolysis {

constexpr double FARADAY_CONST = 96485.33215; // Кл/моль
constexpr double MOLAR_GAS_VOL = 22.414;      // л/моль за НУ

struct IonProperties {
    double molar_mass_g;
    int valence;
    double density_g_cm3;
    double faraday_eff; // 0.0 .. 1.0
};

struct CellParameters {
    double area_cm2;
    double distance_cm;
    double resist_ohm_cm;
    double bubble_fraction{0.05};
    double e0_cell_v;
    double tafel_a_anode;
    double tafel_b_anode;
    double tafel_a_cath;
    double tafel_b_cath;
};

struct SimulationResult {
    double total_charge_c;
    double mass_deposited_g;
    double thickness_um;
    double gas_volume_liters;
    double overpotential_anode;
    double overpotential_cath;
    double ohmic_drop_v;
    double applied_voltage_v;
    double total_energy_wh;
    double specific_energy_kwh_kg;
    double energy_efficiency_pct;
};

enum class SimulationError {
    InvalidCurrentOrTime,
    InvalidGeometry,
    ZeroDensity
};

class ElectrolysisSimulator {
public:
    [[nodiscard]] static std::expected<SimulationResult, SimulationError> 
    compute(const IonProperties& ion, const CellParameters& cell,
            double current_a, double time_sec) noexcept 
    {
        if (current_a <= 0.0 || time_sec <= 0.0) {
            return std::unexpected(SimulationError::InvalidCurrentOrTime);
        }
        if (cell.area_cm2 <= 0.0 || cell.distance_cm <= 0.0 || ion.density_g_cm3 <= 0.0) {
            return std::unexpected(SimulationError::InvalidGeometry);
        }

        SimulationResult res{};

        // 1. Закон Фарадея
        res.total_charge_c = current_a * time_sec;
        const double mass_theo = (ion.molar_mass_g * res.total_charge_c) / 
                                 (ion.valence * FARADAY_CONST);
        res.mass_deposited_g = mass_theo * ion.faraday_eff;

        // 2. Геометрія осадженого шару
        const double volume_cm3 = res.mass_deposited_g / ion.density_g_cm3;
        res.thickness_um = (volume_cm3 / cell.area_cm2) * 10000.0;

        // 3. Газоутворення
        const double moles_e = res.total_charge_c / FARADAY_CONST;
        const double moles_gas = (moles_e / 2.0) * (1.0 - ion.faraday_eff);
        res.gas_volume_liters = moles_gas * MOLAR_GAS_VOL;

        // 4. Кінетика та перенапруга Тафеля
        const double j = current_a / cell.area_cm2;
        res.overpotential_anode = std::max(0.0, cell.tafel_a_anode + cell.tafel_b_anode * std::log10(j));
        res.overpotential_cath  = std::max(0.0, cell.tafel_a_cath  + cell.tafel_b_cath  * std::log10(j));

        // 5. Омічні втрати в рідині з урахуванням ефекту Бруггемана
        const double eps = std::clamp(cell.bubble_fraction, 0.0, 0.4);
        const double eff_resist = cell.resist_ohm_cm / std::pow(1.0 - eps, 1.5);
        const double r_sol = (eff_resist * cell.distance_cm) / cell.area_cm2;
        res.ohmic_drop_v = current_a * r_sol;

        // 6. Повна прикладена напруга
        res.applied_voltage_v = cell.e0_cell_v + res.overpotential_anode + 
                                 res.overpotential_cath + res.ohmic_drop_v;

        // 7. Енергетичні характеристики
        res.total_energy_wh = (res.applied_voltage_v * current_a * time_sec) / 3600.0;
        res.specific_energy_kwh_kg = (res.mass_deposited_g > 0.0) 
            ? (res.total_energy_wh / 1000.0) / (res.mass_deposited_g / 1000.0)
            : 0.0;

        res.energy_efficiency_pct = ion.faraday_eff * (cell.e0_cell_v / res.applied_voltage_v) * 100.0;

        return res;
    }
};

} // namespace electrolysis

int main() {
    using namespace electrolysis;

    const IonProperties nickel{
        .molar_mass_g = 58.6934,
        .valence = 2,
        .density_g_cm3 = 8.908,
        .faraday_eff = 0.95
    };

    const CellParameters bath{
        .area_cm2 = 500.0,
        .distance_cm = 8.0,
        .resist_ohm_cm = 5.0,
        .bubble_fraction = 0.10,
        .e0_cell_v = 1.25,
        .tafel_a_anode = 0.40,
        .tafel_b_anode = 0.10,
        .tafel_a_cath = 0.20,
        .tafel_b_cath = 0.09
    };

    auto sim_res = ElectrolysisSimulator::compute(nickel, bath, 25.0, 7200.0);

    if (sim_res) {
        const auto& r = *sim_res;
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "=== Симуляція нікелювання (C++23) ===\n";
        std::cout << "Маса осадженого Ni:   " << r.mass_deposited_g << " г\n";
        std::cout << "Товщина покриття:     " << r.thickness_um << " мкм\n";
        std::cout << "Виділений H2:         " << r.gas_volume_liters << " л\n";
        std::cout << "Анодна перенапруга:   " << r.overpotential_anode << " В\n";
        std::cout << "Катодна перенапруга:  " << r.overpotential_cath << " В\n";
        std::cout << "Омічне падіння IR:    " << r.ohmic_drop_v << " В\n";
        std::cout << "Прикладена напруга:   " << r.applied_voltage_v << " В\n";
        std::cout << "Питома енергія:       " << r.specific_energy_kwh_kg << " кВт·год/кг\n";
        std::cout << "Енергетичний ККД:     " << r.energy_efficiency_pct << " %\n";
    }

    return 0;
}
```
:::

## Опис архітектури коду та порівняльний аналіз реалізацій

Розроблені реалізації демонструють різні підходи до керування ресурсами та безпеки даних, властиві мовам C та C++.

### Особливості реалізації мовою C

1. **Сумісність із мікроконтролерами**: код написано у чистому стандарті C99 без динамічного виділення пам'яті (`malloc`/`free`), що дозволяє запускати його безпосередньо у перериваннях або задачах FreeRTOS на мікроконтролерах STM32 чи ESP32.
2. **Передача за вказівником**: вхідні структури `IonParams` та `CellConfig` передаються як вказівники на константу (`const IonParams*`), що виключає копіювання даних у стеку та захищає конфігурацію від випадкової модифікації.
3. **Обробка помилок**: функція повертає цілочисловий код стану (`0` — успіх, `-1` — помилка вихідних даних), заповнюючи вихідну структуру `SimResult` за наданою адресою.

### Особливості реалізації мовою C++23

1. **Типобезпечний монодичний тип `std::expected`**: замість сирих кодів помилок функція `ElectrolysisSimulator::compute` повертає `std::expected<SimulationResult, SimulationError>`. Це унеможливлює використання необчисленого результату і позбавляє від потреби обробляти винятки (завдяки пометці `noexcept`).
2. **Константні вирази та атрибути**: використання атрибута `[[nodiscard]]` гарантує, що розробник не забуде перевірити результат обчислення.
3. **Безелементна безпека `std::clamp` та `std::max`**: гарантується захист від виходу за межі допустимих фізичних значень (наприклад, від'ємна перенапруга чи газовміст понад 40%).

## Практичний аналіз результатів та чутливість параметрів

Аналіз результатів симуляції показує дві найважливіші інженерні закономірності:

1. **Вплив газовмісту (ефект Бруггемана)**: збільшення накопичення бульбашок водню у розчині з 0% до 15% призводить до зростання ефективного питного опору розчину в `(1 - 0.15)⁻¹·⁵ ≈ 1.27` раза (на 27%). Це додає майже 0.5 В падіння напруги і знижує загальний ККД установки на 8–10%.
2. **Оптимізація густини струму**: надмірне нарощування струму `I` для прискорення осадження металу підвищує густину струму `j`, що викликає логарифмічне зростання перенапруг Тафеля `η[a] + η[c]` та квадратичне зростання Джоулевих втрат. Оптимальна густина струму для гальваномічних ванн зазвичай лежить у вузькому діапазоні `0.02 .. 0.08 А/см²`.
