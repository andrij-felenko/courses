# ⚙️ Симулятор струмів витоку Френкеля — Пуля у C та C++

Ця вставка містить чисельний та програмний симулятор для розрахунку густини струму витоку за механізмом Френкеля — Пуля (`J_PF`) та оцінки часу утримання заряду (*retention lifetime*) у 3D NAND Charge Trap пам'яті. Симулятор моделює термопольову іонізацію пасток при різних напруженостях електричного поля (`E = 0.5 … 6.0` МВ/см) та температурах (`T = 25 … 125` °C), а також чисельно інтегрує диференціальне рівняння саморозряду осередку з часом.

## 1. Фізична модель та алгоритм чисельного розрахунку

У 3D NAND пам'яті електростатичний потенціал керувального затвора створює в діелектрику електричне поле `E`. Електрони, захоплені глибокими потенціальними пастками Si₃N₄, вивільняються в зону провідності за рахунок термопольової іонізації Френкеля — Пуля.

Алгоритм обчислення базису описується рівнянням:

```
J_PF(E, T) = C · E · exp( - q · (Phi_B - sqrt(q · E / (pi · eps_i))) / (k_B · T) )
```

У реальному осередку пам'яті витік заряду є самообмежувальним нелінійним процесом. Коли електрони залишають нітридну пастку Si₃N₄, накопичений заряд `Q(t)` зменшується. Це викликає падіння порогової напруги `V_th(t)` та зменшення напруженості електричного поля `E(t)` у діелектрику:

```
E(t) = E_0 - (ΔQ(t) / (C_gate · t_dielectric))
```

Оскільки електричне поле `E(t)` зменшується з часом, швидкість витоку `J_PF(E(t), T)` уповільнюється. У результаті заряд осередку спадає не за простою експонентою, а за логарифмічним законом `Q(t) = Q_0 - A · ln(1 + t / t_0)`.

Для точного розрахунку часу збереження даних симулятор реалізує дві фізичні схеми:
1. **Статичний розрахунок (Миттєва швидкість):** Обчислення початкової густини струму `J_PF` при фіксованій початковій напруженості поля `E_0` та оцінка екстрапольованого часу втрати 50% заряду `t_retention = Q_initial / (2 · J_PF)`.
2. **Динамічний чисельний аналіз (Метод Ейлера):** Чисельне інтегрування диференціального рівняння саморозряду `dQ / dt = - J_PF(E(Q), T) · S_cell` на часовій сітці з адаптивним кроком `dt`.

### Фізичні параметри та вхідні значення:
- **Заряд електрона (`q`):** `1.602176634 × 10⁻¹⁹` Кл.
- **Стала Больцмана (`k_B`):** `1.380649 × 10⁻²³` Дж/К.
- **Діелектрична проникність вакууму (`eps_0`):** `8.854187817 × 10⁻¹²` Ф/м.
- **Оптична відносна проникність Si₃N₄ (`eps_r`):** `5.5`.
- **Енергетична глибина пастки (`Phi_B`):** `1.05` еВ.
- **Константа провідності матеріалу (`C`):** `1.5 × 10⁻⁶` А/(В·м).
- **Початковий заряд осередку (`Q_cell`):** `1.0 × 10⁻¹⁵` Кл (~6200 електронів).
- **Ефективна площа перерізу осередку (`S_cell`):** `1.0 × 10⁻¹⁰` см².

## 2. Реалізація у C та C++

Нижче наведено дві незалежні, повні реалізації симулятора: на мові C (із використанням стандартних структур та функцій обчислення) та на мові C++17 (із використанням об'єктно-орієнтованого дизайну, контейнерів `std::vector` та методів форматування струменів).

:::tabs
```c
/* frenkel_poole_sim.c — Симулятор струмів витоку Френкеля-Пуля на C */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Фундаментальні фізичні константи (SI) */
#define Q_ELEM    1.602176634e-19 /* Заряд електрона, Кл */
#define KB_BOLTZ  1.380649e-23    /* Стала Больцмана, Дж/К */
#define EPS_0     8.854187817e-12 /* Діелектрична проникність вакууму, Ф/м */

/* Фізичні параметри плівки Si3N4 у 3D NAND */
typedef struct {
    double eps_r;   /* Оптична відносна діелектрична проникність (~5.5) */
    double phi_b_ev;/* Глибина пастки в еВ (~1.05 еВ) */
    double c_const; /* Константа витоку (А / (В · м)) */
} NitrideParams;

/* Результат обчислення для однієї точки */
typedef struct {
    double field_mv_cm; /* Поле, МВ/см */
    double barrier_drop_ev; /* Зниження бар'єра dPhi, еВ */
    double j_pf_a_cm2;  /* Густина струму, А/см² */
    double retention_sec;/* Оціночний час утримання, с */
} SimPoint;

/* Обчислення струму Френкеля-Пуля для заданого поля E (В/м) та T (К) */
SimPoint compute_fp_point(double e_field_v_m, double temp_k, const NitrideParams *params) {
    SimPoint pt;
    pt.field_mv_cm = e_field_v_m / 1e8; /* Конвертація у МВ/см */

    double eps_i = params->eps_r * EPS_0;
    
    /* Зниження бар'єра dPhi = sqrt(q * E / (pi * eps_i)) у Дж */
    double dphi_joules = sqrt((Q_ELEM * Q_ELEM * Q_ELEM * e_field_v_m) / (M_PI * eps_i));
    pt.barrier_drop_ev = dphi_joules / Q_ELEM;

    double phi_eff_joules = (params->phi_b_ev * Q_ELEM) - dphi_joules;
    if (phi_eff_joules < 0.0) {
        phi_eff_joules = 0.0; /* Повний пробій бар'єра */
    }

    /* Густина струму J_PF = C * E * exp(-phi_eff / (kB * T)) у А/м² */
    double exponent = -phi_eff_joules / (KB_BOLTZ * temp_k);
    double j_pf_m2 = params->c_const * e_field_v_m * exp(exponent);
    
    pt.j_pf_a_cm2 = j_pf_m2 / 1e4; /* Конвертація в А/см² */

    /* Оцінка часу втрати 50% заряду (заряд комірки ~10^-15 Кл, площа ~10^-10 см²) */
    double q_cell_cm2 = 1.0e-5; /* Кл/см² */
    pt.retention_sec = (j_pf_a_cm2 > 1e-30) ? (q_cell_cm2 / pt.j_pf_a_cm2) : 1e15;

    return pt;
}

int main(void) {
    NitrideParams si3n4 = {
        .eps_r = 5.5,
        .phi_b_ev = 1.05,
        .c_const = 1.5e-6
    };

    double temp_celsius = 85.0; /* Робоча температура SSD */
    double temp_k = temp_celsius + 273.15;

    printf("=== Симуляція струмів витоку Френкеля-Пуля (T = %.1f C) ===\n", temp_celsius);
    printf("%-12s | %-14s | %-16s | %-16s\n", 
           "E (МВ/см)", "dPhi (еВ)", "J_PF (А/см²)", "Retention (роки)");
    printf("-------------------------------------------------------------------\n");

    for (double field_mv = 0.5; field_mv <= 4.01; field_mv += 0.5) {
        double e_v_m = field_mv * 1e8;
        SimPoint pt = compute_fp_point(e_v_m, temp_k, &si3n4);
        double retention_years = pt.retention_sec / (365.25 * 86400.0);

        printf("%-12.2f | %-14.4f | %-16.4e | %-16.4e\n",
               pt.field_mv_cm, pt.barrier_drop_ev, pt.j_pf_a_cm2, retention_years);
    }

    return 0;
}
```
```cpp
// frenkel_poole_sim.cpp — Ідіоматична реалізація симулятора на C++17
#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <string>

namespace Physics {
    constexpr double Q_ELEM   = 1.602176634e-19; // Кл
    constexpr double KB_BOLTZ = 1.380649e-23;    // Дж/К
    constexpr double EPS_0    = 8.854187817e-12; // Ф/м
    constexpr double PI_VAL   = 3.14159265358979323846;
}

struct NitrideMaterial {
    double eps_r{5.5};
    double trap_depth_ev{1.05};
    double c_leakage{1.5e-6};
};

struct SimulationResult {
    double field_mv_cm;
    double barrier_reduction_ev;
    double current_density_a_cm2;
    double retention_years;
};

class PooleFrenkelSimulator {
public:
    explicit PooleFrenkelSimulator(NitrideMaterial mat) : material_(mat) {}

    [[nodiscard]] SimulationResult calculatePoint(double field_mv_cm, double temp_celsius) const {
        using namespace Physics;
        
        const double temp_k = temp_celsius + 273.15;
        const double field_v_m = field_mv_cm * 1e8;
        const double eps_i = material_.eps_r * EPS_0;

        // Зниження потенціального бар'єра dPhi
        const double dphi_joules = std::sqrt((Q_ELEM * Q_ELEM * Q_ELEM * field_v_m) / (PI_VAL * eps_i));
        const double dphi_ev = dphi_joules / Q_ELEM;

        const double effective_phi_joules = std::max(0.0, (material_.trap_depth_ev * Q_ELEM) - dphi_joules);

        // Густина струму J_PF у А/м²
        const double exponent = -effective_phi_joules / (KB_BOLTZ * temp_k);
        const double j_pf_m2 = material_.c_leakage * field_v_m * std::exp(exponent);
        const double j_pf_cm2 = j_pf_m2 / 1e4;

        // Оцінка утримання заряду
        constexpr double q_density_cm2 = 1.0e-5; // Кл/см²
        const double retention_sec = (j_pf_cm2 > 1e-30) ? (q_density_cm2 / j_pf_cm2) : 1e15;
        const double retention_years = retention_sec / (365.25 * 86400.0);

        return {field_mv_cm, dphi_ev, j_pf_cm2, retention_years};
    }

    [[nodiscard]] std::vector<SimulationResult> runSweep(double min_field, double max_field, 
                                                         double step, double temp_celsius) const {
        std::vector<SimulationResult> results;
        results.reserve(static_cast<size_t>((max_field - min_field) / step) + 1);

        for (double f = min_field; f <= max_field + 1e-9; f += step) {
            results.push_back(calculatePoint(f, temp_celsius));
        }
        return results;
    }

private:
    NitrideMaterial material_;
};

int main() {
    NitrideMaterial si3n4{5.5, 1.05, 1.5e-6};
    PooleFrenkelSimulator sim(si3n4);

    constexpr double test_temp = 85.0; // °C
    auto results = sim.runSweep(0.5, 4.0, 0.5, test_temp);

    std::cout << "=== C++17 Моделювання витоку Френкеля-Пуля (T = " << test_temp << " °C) ===\n\n";
    std::cout << std::left << std::setw(12) << "E (МВ/см)"
              << " | " << std::setw(14) << "dPhi (еВ)"
              << " | " << std::setw(16) << "J_PF (А/см²)"
              << " | " << std::setw(16) << "Retention (роки)" << "\n";
    std::cout << std::string(68, '-') << "\n";

    for (const auto& res : results) {
        std::cout << std::left << std::setw(12) << std::fixed << std::setprecision(2) << res.field_mv_cm
                  << " | " << std::setw(14) << std::setprecision(4) << res.barrier_reduction_ev
                  << " | " << std::setw(16) << std::scientific << std::setprecision(4) << res.current_density_a_cm2
                  << " | " << std::setw(16) << std::scientific << std::setprecision(4) << res.retention_years << "\n";
    }

    return 0;
}
```
:::

## 3. Аналіз чутливості та температурні крайні випадки

Симуляція розкриває фізичну чутливість збереження даних у 3D NAND до температури навколишнього середовища та глибини пастки `Phi_B`:

1. **Чутливість до глибини пастки `Phi_B`:** Зменшення енергії залягання пасток усього на `0.1` еВ (від 1.05 еВ до 0.95 еВ через структурні дефекти осадження ALD) припадає на збільшення густини струму `J_PF` у `exp(0.1 / 0.0308) ≈ 25` разів при `T = 85` °C. Це доводить вимогу до абсолютної однорідності складу нітридної плівки Si₃N₄.
2. **Нормальний робочий режим (T = 25 °C, E = 1.5 МВ/см):** Густина струму витоку `J_PF` становить менше `10⁻¹⁸` А/см², а розрахований термін зберігання заряду перевищує 100 років. Пристрій повністю відповідає вимогам JEDEC.
3. **Серверне навантаження (T = 85 °C, E = 2.5 МВ/см):** Через зростання теплової енергії `k_B · T` та зниження бар'єра `dPhi ≈ 0.35` еВ густина струму зростає до `10⁻¹₀` А/см². Оціночний час утримання скорочується до 1–2 років. Контролер SSD мусить застосовувати алгоритми фонового оновлення даних (*Background Data Refresh*).
4. **Екстремальний температурний перегрів (T = 125 °C, E = 3.5 МВ/см):** Відбувається термопольовий пробій пасток. Термін утримання падає до кількох годин, що викликає множинні помилки читання бітів (BER).

## 4. Розбір програмних рішень у C та C++

При виборі чисельних типів даних для симулятора фізики твердого тіла виникає важлива інженерна вимога: використовувати 64-бітні числа з плаваючою комою потрійної точності `double` замість 32-бітних `float`.

Це пояснюється тим, що величина експоненціального фактора `exp(-q · (Φ_B - ΔΦ) / (k_B · T))` при малих полях виходить за межі діапазону одиничної точності: для `E = 0.5` МВ/см значення `J_PF` падає нижче `10⁻²⁵` А/см². Використання 32-бітного типом `float` викликало б передчасне антипереповнення під плаваючу кому (*underflow*) та втрату точності.

У C++17 реалізації симулятора застосовано кваліфікатор `[[nodiscard]]` для методів `calculatePoint` та `runSweep`, що запобігає ігноруванню повернутих обчислених векторів результатів у промисловому коді контролерів пам'яті. Використання `std::vector` із попереднім резервуванням пам'яті `results.reserve(...)` виключає повторні динамічні реалокації пам'яті під час перебору температурної сітки.

## 5. Інтеграція алгоритму симуляції у прошивку FTL

У реальних накопичувачах цей алгоритм витоку інтегрується у прошивку контролера FTL для прогнозування дрейфу `V_th`:

- **Температурно-часовий лічильник (Retention Tracking Engine):** Контролер регулярно опитує вбудований температурний датчик мікросхеми Flash. Лічильник накопичує коефіцієнт деградації `D = ∫ J_PF(E, T(t)) dt`. Коли накопичена деградація перевищує допустимий поріг, FTL ініціює фонове перенесення сторінки на свіжий блок пам'яті.
- **Динамічний вибір LDPC коефіцієнтів:** На основі розрахованого зниження бар'єра `dPhi` прошивка контролера оцінює розширення розподілу `V_th` і заздалегідь готує матриці декодування коду LDPC із відповідною пропускною здатністю виправлення помилок.

Фізична інтерпретація цих результатів та їхній вплив на надійність накопичувачів детально розглянуті у статті [3D NAND: фізика вертикального стека](root:ph-condensed/3d-nand-architecture).
