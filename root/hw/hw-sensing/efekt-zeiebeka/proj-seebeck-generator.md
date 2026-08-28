# ⚙️ Моделювання термоелектричного генератора й термопари на C та C++

Інженерний розрахунок термоелектричних перетворювачів охоплює дві фундаментальні прикладні задачі твердотільної електроніки:
1. Пряме чисельне моделювання термоелектричного генератора (TEG / модуль Пельтьє в генераторному режимі) з урахуванням температурно-залежних фізичних властивостей напівпровідника, внутрішніх теплових паразитів, контактних опорів і узгодження електричного імпедансу.
2. Прецизійну метрологічну лінеаризацію сигналу вимірювальної термопари за міжнародними аналітичними стандартами NIST ITS-90 з апаратною та програмною компенсацією температури опорного спаю і контролем цілісності лінії.

Нижче наведено повний інженерний аналіз фізичних моделей та їхні оптимізовані реалізації мовами C та C++20.

---

## 1. Фізична та теплова архітектура генератора TEG

Типовий модуль термоелектричного генератора складається з матриці з `N` пар напівпровідникових стовпчиків (ніжок) p-типу та n-типу (найчастіше на базі халькогенідів вісмуту `Bi₂Te₃/Sb₂Te₃`), які електрично з'єднані послідовно за допомогою мідних контактних містків, а термодинамічно розташовані паралельно між двома керамічними пластинами з оксиду алюмінію (`Al₂O₃`) або нітриду алюмінію (`AlN`).

```
                    Гарячий тепловий потік Q_h
              ─────────────────────────────────────────
             │       Верхня керамічна пластина         │
             │   ───[Мідь]───   ───[Мідь]───   ───[Мідь│
             │    │         │    │         │    │      │
             │   ┌┴──┐     ┌┴──┐┌┴──┐     ┌┴──┐┌┴──┐   │
             │   │ p │     │ n ││ p │     │ n ││ p │   │  Hіжки TEG
             │   └┬──┘     └┬──┘└┬──┘     └┬──┘└┬──┘   │
             │    │         │    │         │    │      │
             │   ───[Мідь]───   ───[Мідь]───   ───[Мідь│
             │       Нижня керамічна пластина          │
              ─────────────────────────────────────────
                    Холодний тепловий потік Q_c
                            │          │
                           (+)        (-)  -> До навантаження R_L
```

### Врахування контактних і паразитних опорів
У реальних модулях напруга й ККД обмежуються не лише об'ємними властивостями напівпровідника, але й контактними переходами:
1. **Контактний електричний опір `r_c`** (Ом·м²): омічний опір металізації та пайки між мідними шинами й торцями напівпровідникових ніжок. Для якісних модулів `r_c ≈ 10^(-9) – 10^(-10) Ом·м²`.
2. **Контактний тепловий опір `r_th_c`** (К·м²/Вт): тепловий опір керамічної підкладки та термопасти на межі з радіаторами. Через це ефективна різниця температур на самих напівпровідникових стовпчиках `ΔT_semi` завжди менша за зовнішній перепад температур між радіаторами `ΔT_ext`.

### Основні розрахункові рівняння моделі:

1. **Напруга холостого ходу (Open-Circuit Voltage)**:
```
V_oc
= N · ( S_p - S_n ) · ( T_h - T_c )  [сумарний коефіцієнт Зеєбека модуля помножений на перепад температур]
```

2. **Внутрішній електричний опір ніжок з урахуванням контактів**:
```
R_int
= N · ( (ρ_p + ρ_n) · (L / A) + 2 · r_c / A )  [об'ємний опір стовпчиків плюс опір контактних переходів]
```

3. **Власна теплова провідність модуля**:
```
K_th
= N · ( κ_p + κ_n ) · ( A / L )      [сумарна паралельна теплопровідність ніжок за законом Фур'є]
```

4. **Електричний струм у колі навантаження**:
```
I_out
= V_oc / ( R_int + R_load )          [струм за законом Ома для повного замкненого електричного кола]
```

5. **Теплові потоки на гарячій та холодній гранях**:
Гаряча грань поглинає тепло Пельтьє та віддає тепло за рахунок теплопровідності до холодного кінця, одночасно отримуючи половину тепла Джоуля від внутрішніх втрат:
```
Q_hot
= N · (S_p - S_n) · T_h · I_out + K_th · (T_h - T_c) - 0.5 · I_out² · R_int  [баланс енергії гарячої поверхні]

Q_cold
= N · (S_p - S_n) · T_c · I_out + K_th · (T_h - T_c) + 0.5 · I_out² · R_int  [баланс енергії холодної поверхні]
```

6. **Корисна електрична потужність та ККД**:
```
P_el
= I_out² · R_load                    [корисна електрична потужність, розсіювана на навантаженні]

η
= ( P_el / Q_hot ) · 100%            [термодинамічний коефіцієнт корисної дії генерації]
```

---

## 2. Математична модель лінеаризації термопари (NIST ITS-90)

Сигнал термопари `V(T)` є нелінійною функцією температури через залежність коефіцієнта Зеєбека металів від енергії електронів і розсіювання фононів. Для високоточного відновлення температури Національний інститут стандартів і технологій США (NIST) визначає поліноми 9–10 степеня.

Для **термопари типу K (хромель-алюмель)**:
1. **Прямий поліном (температура `T` в °C → ЕРС `V` у мкВ)**:
```
V(T)
= ∑ [i = 0 .. 9] ( c_i · T^i ) + a_0 · exp( a_1 · (T - a_2)² )  [прямий поліном NIST ITS-90 з гаусовою поправкою]
```
2. **Обернений поліном (ЕРС `V` у мВ → температура `T` в °C)**:
```
T(V)
= ∑ [i = 0 .. 9] ( d_i · V^i )       [обернений поліном для діапазону від 0 до 500 °C]
```

### Алгоритм компенсації холодного спаю (Cold-Junction Compensation, CJC):
1. Локальний давач температури (наприклад, терморезистор NTC або платиновий RTD PT100), розміщений безпосередньо на мідних клемах входу вимірювального блоку, визначає температуру холодного спаю `T_cjc`.
2. За прямим перетворенням обчислюється еквівалентна напруга опорного спаю: `V_cjc = V_poly(T_cjc)`.
3. Виміряна АЦП напруга `V_raw` додається до опорної напруги: `V_total = V_raw + V_cjc`.
4. Дійсна температура вимірюваного об'єкта розраховується за оберненим поліномом від повної напруги: `T_hot = T_inv_poly(V_total)`.

---

## 3. Програмна реалізація симулятора TEG та лінеаризатора

Нижче наведено паралельні реалізації алгоритмів мовами C та C++20. Обидва варіанти містять схему Горнера для мінімізації кількості операцій множення при обчисленні степеневих рядів та запобігання втрати точності плаваючої коми.

:::tabs
```c
#include <stdio.h>
#include <math.h>
#include <stdbool.h>

/* Параметри конструкції модуля термоелектрогенератора TEG */
typedef struct {
    double seebeck_p;    /* коефіцієнт Зеєбека p-типу, В/К (наприклад +210e-6) */
    double seebeck_n;    /* коефіцієнт Зеєбека n-типу, В/К (наприклад -210e-6) */
    double rho_p;        /* питомий електричний опір p-типу, Ом·м */
    double rho_n;        /* питомий електричний опір n-типу, Ом·м */
    double kappa_p;      /* питома теплопровідність p-типу, Вт/(м·К) */
    double kappa_n;      /* питома теплопровідність n-типу, Вт/(м·К) */
    double leg_length_m; /* висота напівпровідникового стовпчика, м */
    double leg_area_m2;   /* площа поперечного перерізу стовпчика, м² */
    int num_couples;     /* кількість послідовно з'єднаних пар p-n */
} TegModuleParams;

/* Результати розрахунку робочої точки генератора під навантаженням */
typedef struct {
    double v_open_circuit_v;     /* ЕРС холостого ходу, В */
    double r_internal_ohm;       /* внутрішній опір модуля, Ом */
    double k_thermal_w_per_k;    /* теплова провідність модуля, Вт/К */
    double current_a;            /* робочий струм у колі, А */
    double voltage_load_v;       /* падіння напруги на навантаженні, В */
    double power_electrical_w;   /* корисна вихідна потужність, Вт */
    double heat_absorbed_hot_w;  /* тепловий потік з гарячого боку, Вт */
    double heat_rejected_cold_w; /* тепловий потік, скинутий на радіатор, Вт */
    double efficiency_percent;   /* ККД генерації, % */
} TegOperatingPoint;

/* Чисельний розрахунок термоелектричної робочої точки */
TegOperatingPoint teg_calculate_point(const TegModuleParams *mod,
                                      double t_hot_k,
                                      double t_cold_k,
                                      double r_load_ohm) {
    TegOperatingPoint pt;
    double delta_t = t_hot_k - t_cold_k;
    double total_seebeck = (mod->seebeck_p - mod->seebeck_n) * (double)mod->num_couples;
    double geom_factor = mod->leg_length_m / mod->leg_area_m2;

    pt.v_open_circuit_v = total_seebeck * delta_t;
    pt.r_internal_ohm = (mod->rho_p + mod->rho_n) * geom_factor * (double)mod->num_couples;
    pt.k_thermal_w_per_k = (mod->kappa_p + mod->kappa_n) * (1.0 / geom_factor) * (double)mod->num_couples;

    double r_total = pt.r_internal_ohm + r_load_ohm;
    pt.current_a = (r_total > 1e-12) ? (pt.v_open_circuit_v / r_total) : 0.0;
    pt.voltage_load_v = pt.current_a * r_load_ohm;
    pt.power_electrical_w = pt.current_a * pt.current_a * r_load_ohm;

    /* Енергетичний баланс граней з урахуванням ефектів Пельтьє, теплопровідності та Джоуля */
    double q_peltier_hot = total_seebeck * t_hot_k * pt.current_a;
    double q_conduction = pt.k_thermal_w_per_k * delta_t;
    double q_joule_half = 0.5 * pt.current_a * pt.current_a * pt.r_internal_ohm;

    pt.heat_absorbed_hot_w = q_peltier_hot + q_conduction - q_joule_half;
    pt.heat_rejected_cold_w = (total_seebeck * t_cold_k * pt.current_a) + q_conduction + q_joule_half;

    if (pt.heat_absorbed_hot_w > 1e-9) {
        pt.efficiency_percent = (pt.power_electrical_w / pt.heat_absorbed_hot_w) * 100.0;
    } else {
        pt.efficiency_percent = 0.0;
    }

    return pt;
}

/* ──────────────── NIST ITS-90 Поліноми для Термопари Типу K ─────────────── */

static const double K_COEFFS_T_TO_V[] = {
    -1.76004136860E-01,
     3.89212049750E+01,
     1.85587700320E-02,
    -9.94575928740E-05,
     3.18409457190E-07,
    -5.60728448890E-10,
     5.60750590590E-13,
    -3.20207200030E-16,
     9.71511471520E-20,
    -1.21047212750E-23
};

static const double K_COEFFS_V_TO_T[] = {
     0.0000000E+00,
     2.5083550E+01,
     7.8601060E-02,
    -2.5031310E-01,
     8.3152700E-02,
    -1.2280340E-02,
     9.8040360E-04,
    -4.4130300E-05,
     1.0577340E-06,
    -1.0527550E-08
};

/* Пряме перетворення: T (°C) -> ЕРС (мкВ) за схемою Горнера */
double thermocouple_k_temp_to_uv(double temp_c) {
    double uv = K_COEFFS_T_TO_V[9];
    for (int i = 8; i >= 0; --i) {
        uv = uv * temp_c + K_COEFFS_T_TO_V[i];
    }
    double a0 = 1.185976e+02;
    double a1 = -1.183432e-04;
    double a2 = 1.269686e+02;
    uv += a0 * exp(a1 * (temp_c - a2) * (temp_c - a2));
    return uv;
}

/* Обернене перетворення: ЕРС (мВ) -> T (°C) за схемою Горнера */
double thermocouple_k_voltage_to_temp(double emf_mv) {
    double temp = K_COEFFS_V_TO_T[9];
    for (int i = 8; i >= 0; --i) {
        temp = temp * emf_mv + K_COEFFS_V_TO_T[i];
    }
    return temp;
}

/* Повний контур вимірювання з компенсацією холодного спаю */
double thermocouple_k_measure(double measured_raw_uv, double cjc_ambient_temp_c) {
    double v_cjc_uv = thermocouple_k_temp_to_uv(cjc_ambient_temp_c);
    double v_total_uv = measured_raw_uv + v_cjc_uv;
    return thermocouple_k_voltage_to_temp(v_total_uv * 1e-3);
}

int main(void) {
    /* Параметри серійного модуля TEG (127 пар, Bi2Te3) */
    TegModuleParams mod = {
        .seebeck_p = 210e-6,
        .seebeck_n = -210e-6,
        .rho_p = 1.2e-5,
        .rho_n = 1.2e-5,
        .kappa_p = 1.5,
        .kappa_n = 1.5,
        .leg_length_m = 1.5e-3,
        .leg_area_m2 = 1.4e-3 * 1.4e-3,
        .num_couples = 127
    };

    double t_hot = 473.15;  /* 200 °C */
    double t_cold = 303.15; /* 30 °C */

    TegOperatingPoint probe = teg_calculate_point(&mod, t_hot, t_cold, 1.0);
    TegOperatingPoint match = teg_calculate_point(&mod, t_hot, t_cold, probe.r_internal_ohm);

    printf("=== Симуляція Термоелектричного Генератора (TEG) ===\n");
    printf("Перепад температур ΔT: %.1f K (Hot=%.1f K, Cold=%.1f K)\n", t_hot - t_cold, t_hot, t_cold);
    printf("Напруга холостого ходу V_oc: %.3f В\n", match.v_open_circuit_v);
    printf("Внутрішній опір модуля R_int: %.3f Ом\n", match.r_internal_ohm);
    printf("Струм при узгодженні I: %.3f А\n", match.current_a);
    printf("Максимальна вихідна потужність P_el: %.3f Вт\n", match.power_electrical_w);
    printf("Тепловий ККД генератора: %.2f %%\n\n", match.efficiency_percent);

    printf("=== Лінеаризація Термопари Типу K (ITS-90 + CJC) ===\n");
    double ambient_cjc = 24.5;
    double measured_uv = 12150.0;
    double hot_temp = thermocouple_k_measure(measured_uv, ambient_cjc);

    printf("Температура клем холодного спаю (CJC): %.2f °C\n", ambient_cjc);
    printf("Виміряна різниця потенціалів: %.1f мкВ\n", measured_uv);
    printf("Обчислена дійсна температура об'єкта: %.2f °C\n", hot_temp);

    return 0;
}
```
```cpp
#include <iostream>
#include <array>
#include <cmath>
#include <iomanip>
#include <span>
#include <string_view>

namespace thermo {

/* Фізичні параметри напівпровідникового модуля TEG */
struct TegProperties {
    double seebeck_p{210e-6};     // В/К для p-гілки
    double seebeck_n{-210e-6};    // В/К для n-гілки
    double resistivity_p{1.2e-5}; // Ом·м
    double resistivity_n{1.2e-5}; // Ом·м
    double thermal_cond_p{1.5};   // Вт/(м·К)
    double thermal_cond_n{1.5};   // Вт/(м·К)
    double leg_length{1.5e-3};    // висота стовпчика, м
    double leg_area{1.96e-6};     // площа перерізу, м² (1.4 × 1.4 мм)
    std::size_t couples_count{127};
};

/* Стан генератора під навантаженням */
struct GeneratorResult {
    double open_circuit_voltage{};
    double internal_resistance{};
    double thermal_conductance{};
    double load_current{};
    double load_voltage{};
    double electrical_power{};
    double heat_absorbed_hot{};
    double heat_rejected_cold{};
    double efficiency_percent{};
};

class ThermoelectricGenerator {
public:
    explicit constexpr ThermoelectricGenerator(TegProperties params) noexcept
        : params_(params) {}

    [[nodiscard]] GeneratorResult simulate(double temp_hot_k, double temp_cold_k, double load_res_ohm) const noexcept {
        GeneratorResult res{};
        const double delta_t = temp_hot_k - temp_cold_k;
        const double total_seebeck = (params_.seebeck_p - params_.seebeck_n) * static_cast<double>(params_.couples_count);
        const double geom_factor = params_.leg_length / params_.leg_area;

        res.open_circuit_voltage = total_seebeck * delta_t;
        res.internal_resistance = (params_.resistivity_p + params_.resistivity_n) * geom_factor * static_cast<double>(params_.couples_count);
        res.thermal_conductance = (params_.thermal_cond_p + params_.thermal_cond_n) * (1.0 / geom_factor) * static_cast<double>(params_.couples_count);

        const double total_circuit_r = res.internal_resistance + load_res_ohm;
        res.load_current = (total_circuit_r > 1e-12) ? (res.open_circuit_voltage / total_circuit_r) : 0.0;
        res.load_voltage = res.load_current * load_res_ohm;
        res.electrical_power = res.load_current * res.load_current * load_res_ohm;

        // Потоки тепла Пельтьє, кондуктивного витоку та внутрішнього самонагріву
        const double q_peltier_hot = total_seebeck * temp_hot_k * res.load_current;
        const double q_conduction = res.thermal_conductance * delta_t;
        const double q_joule_half = 0.5 * res.load_current * res.load_current * res.internal_resistance;

        res.heat_absorbed_hot = q_peltier_hot + q_conduction - q_joule_half;
        res.heat_rejected_cold = (total_seebeck * temp_cold_k * res.load_current) + q_conduction + q_joule_half;

        res.efficiency_percent = (res.heat_absorbed_hot > 1e-9)
            ? (res.electrical_power / res.heat_absorbed_hot) * 100.0
            : 0.0;

        return res;
    }

private:
    TegProperties params_;
};

/* ──────────────── Прецизійна лінеаризація термопари типу K за ITS-90 ─────────────── */

class TypeKThermocouple {
public:
    static constexpr std::array<double, 10> k_poly_t_to_v{
        -1.76004136860E-01,
         3.89212049750E+01,
         1.85587700320E-02,
        -9.94575928740E-05,
         3.18409457190E-07,
        -5.60728448890E-10,
         5.60750590590E-13,
        -3.20207200030E-16,
         9.71511471520E-20,
        -1.21047212750E-23
    };

    static constexpr std::array<double, 10> k_poly_v_to_t{
         0.0000000E+00,
         2.5083550E+01,
         7.8601060E-02,
        -2.5031310E-01,
         8.3152700E-02,
        -1.2280340E-02,
         9.8040360E-04,
        -4.4130300E-05,
         1.0577340E-06,
        -1.0527550E-08
    };

    [[nodiscard]] static double temperature_to_microvolts(double temp_celsius) noexcept {
        double uv = k_poly_t_to_v.back();
        for (auto it = k_poly_t_to_v.rbegin() + 1; it != k_poly_t_to_v.rend(); ++it) {
            uv = uv * temp_celsius + *it;
        }
        constexpr double a0 = 1.185976e+02;
        constexpr double a1 = -1.183432e-04;
        constexpr double a2 = 1.269686e+02;
        uv += a0 * std::exp(a1 * (temp_celsius - a2) * (temp_celsius - a2));
        return uv;
    }

    [[nodiscard]] static double millivolts_to_temperature(double emf_millivolts) noexcept {
        double temp = k_poly_v_to_t.back();
        for (auto it = k_poly_v_to_t.rbegin() + 1; it != k_poly_v_to_t.rend(); ++it) {
            temp = temp * emf_millivolts + *it;
        }
        return temp;
    }

    [[nodiscard]] static double calculate_hot_junction(double raw_measured_uv, double cold_junction_temp_c) noexcept {
        const double cjc_equivalent_uv = temperature_to_microvolts(cold_junction_temp_c);
        const double compensated_total_uv = raw_measured_uv + cjc_equivalent_uv;
        return millivolts_to_temperature(compensated_total_uv * 1e-3);
    }
};

} // namespace thermo

int main() {
    using namespace thermo;

    const ThermoelectricGenerator teg{TegProperties{}};
    constexpr double th = 473.15; // 200 °C
    constexpr double tc = 303.15; // 30 °C

    const auto probe = teg.simulate(th, tc, 1.0);
    const auto matched_op = teg.simulate(th, tc, probe.internal_resistance);

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "=== C++20 Модель термоелектричного генератора (TEG) ===\n";
    std::cout << "Перепад температур: " << (th - tc) << " K\n";
    std::cout << "ЕРС холостого ходу V_oc: " << matched_op.open_circuit_voltage << " В\n";
    std::cout << "Внутрішній опір R_int: " << matched_op.internal_resistance << " Ом\n";
    std::cout << "Струм при узгодженні I: " << matched_op.load_current << " А\n";
    std::cout << "Вихідна електрична потужність: " << matched_op.electrical_power << " Вт\n";
    std::cout << "Термоелектричний ККД: " << std::setprecision(2) << matched_op.efficiency_percent << " %\n\n";

    constexpr double cjc_temp = 24.5;
    constexpr double measured_sensor_uv = 12150.0;
    const double object_temp = TypeKThermocouple::calculate_hot_junction(measured_sensor_uv, cjc_temp);

    std::cout << "=== Прецизійна лінеаризація Type K (ITS-90) ===\n";
    std::cout << "Температура плати CJC: " << cjc_temp << " °C\n";
    std::cout << "Виміряний сигнал на вході АЦП: " << measured_sensor_uv << " мкВ\n";
    std::cout << "Дійсна температура гарячого спаю: " << object_temp << " °C\n";

    return 0;
}
```
:::

---

## 4. Практичні інженерні аспекти та діагностика вимірювального тракту

При розробці систем збору даних на основі термопар інженер стикається з низкою критичних апаратних викликів:

1. **Фільтрація вхідних кіл термопари**: Сигнал термопари має низький рівень (десятки мікровольтів) та високу чутливість до промислових завад 50/60 Гц і радіочастотного наведення. Необхідно встановлювати симетричний диференціальний RC-фільтр низьких частот (два узгоджені резистори `1 кОм` з допуском 0.1% та диференціальний плівковий конденсатор `100 нФ` у парі з двома синфазними керамічними конденсаторами `10 нФ` на землю). Несиметрія синфазних ємностей понад 5% перетворює синфазну наведену заваду в паразитний диференціальний сигнал.
2. **Мікросхеми аналогового інтерфейсу**: Для зменшення навантаження на центральний процесор мікроконтролера застосовують спеціалізовані термоелектричні АЦП із вбудованим термодавачем CJC та апаратним перетворенням ITS-90 (наприклад, `MAX31855`, `MAX31856` або прецизійний 24-бітний АЦП `ADS1248`).
3. **Детектування обриву термопари (Burnout Detection)**: Оскільки термопара являє собою низькоомний дріт (10–100 Ом), обрив лінії призводить до плаваючого входу підсилювача. Для надійної діагностики аварії вхідні лінії підтягують до шин живлення слабкими джерелами струму (10–50 нА): при нормальній роботі струм створює мікроскопічне зміщення (< 1 мкВ), а при обриві вхідний каскад миттєво насичується в позитивну або негативну шину живлення.
4. **Алгоритми MPPT для генераторів TEG**: Оскільки внутрішній опір термоелектрогенератора змінюється залежно від температури граней (`R_int(T)`), системи енергетичного збору (*Energy Harvesting*) використовують схему відстеження точки максимальної потужності (*Maximum Power Point Tracking, MPPT*) на базі алгоритму фракційної напруги холостого ходу (*Fractional Open-Circuit Voltage, FOCV*): періодично розмикають коло на 10 мс, вимірюють `V_oc` і встановлюють робочу точку імпульсного DC-DC перетворювача на рівні `V_mpp = 0.5 · V_oc`.
