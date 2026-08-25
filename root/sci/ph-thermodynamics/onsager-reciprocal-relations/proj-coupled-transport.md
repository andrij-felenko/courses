# ⚙️ Моделювання термоелектричних ефектів на основі матриці Онсагера

Прикладна програма мовами C та C++ для обчислення та чисельного моделювання зв'язаного теплового й електричного переносу в термоелектричному модулі (ефекти Зеебека та Пельтьє) на основі матриці феноменологічних коефіцієнтів Онсагера `L_ij`.

## 1. Фізична постановка задачі та матриця Онсагера

У термоелектричних напівпровідникових матеріалах (наприклад, халькогенідах вісмуту та стибію `Bi₂Te₃`, `Sb₂Te₃`, телуриді свинцю `PbTe` або високотемпературних кремній-германієвих сплавах `SiGe`) перенос тепла та перенос електричного заряду є нерозривно сполученими фізичними процесами. Якщо до термоелектричного елемента прямокутного перерізу площею `A` та довжиною `L_len` одночасно прикласти температурний градієнт `∇T` та електричне поле `E = −∇φ`, локальні густини потоку тепла `J_q` (Вт/м²) та потоку заряду `J_e` (А/м²) описуються системою лінійних феноменологічних рівнянь нерівноважної термодинаміці Онсагера:

```
J_q = L_qq · ∇(1/T) − L_qe · ∇(φ/T)
J_e = L_eq · ∇(1/T) − L_ee · ∇(φ/T)
```

За фундаментальною теоремою Онсагера, перехресні кінетичні коефіцієнти переносу задовольняють строге співвідношення мікроскопічної симетрії:

```
L_qe = L_eq
```

В експериментальній фізиці твердого тіла та інженерній практиці замість абстрактних феноменологічних коефіцієнтів `L_ij` зазвичай використовують макроскопічні транспортні характеристики матеріалу, виміряні у стандартних ізольованих лабораторних експериментах:
- **Питома електропровідність `σ`** (См/м) — вимірюється при відсутності температурного градієнта (`∇T = 0`);
- **Питома теплопровідність `κ`** (Вт/(м·К)) — вимірюється при відсутності електричного струму (`J_e = 0`);
- **Коефіцієнт Зеебека (диференціальна термо-ЕРС) `S`** (В/К) — вимірюється як відношення генерованої напруги до різниці температур у розімкненому колі (`J_e = 0`);
- **Коефіцієнт Пельтьє `Π`** (В) — вимірюється як відношення виділюваного або поглинаного на контакті тепла до величини прохідного струму в ізотермічному стані (`∇T = 0`).

Перехід від феноменологічних коефіцієнтів Онсагера `L_ij` до експериментальних макроскопічних величин `σ`, `κ`, `S`, `Π` здійснюється за допомогою фундаментальних тотожностей при середній абсолютній температурі `T`:

```
L_ee = σ · T
L_eq = S · σ · T²
L_qe = Π · σ · T
L_qq = (κ + S² · σ · T) · T²
```

Підставляючи співвідношення симетрії Онсагера `L_qe = L_eq` у вирази для перехресних коефіцієнтів, ми безпосередньо виводимо формулу Кельвіна для термоелектричних явищ:

```
Π · σ · T = S · σ · T²   ⇒   Π = S · T
```

Це співвідношення доводить, що коефіцієнт Пельтьє `Π` не є незалежною фізичною характеристикою речовини, а повністю визначається коефіцієнтом Зеебека `S` та абсолютною температурою `T`.

## 2. Термоелектрична добротність ZT та коефіцієнт корисної дії

Ефективність термоелектричного перетворення тепла у корисну електричну потужність (або ефективність охолодження у режимі Пельтьє) фундаментально визначається безрозмірним коефіцієнтом термоелектричної добротності **ZT (Figure of Merit)**:

```
ZT = (S² · σ / κ) · T
```

де `S² · σ` називається термоелектричним фактором потужності (Power Factor). З формул Онсагера випливає, що високе значення `ZT` вимагає одночасного поєднання високої електропровідності `σ` (для мінімізації джоулевих втрат), високого коефіцієнта Зеебека `S` (для максимізації генерованої термо-ЕРС) та низької питомої теплопровідності `κ` (для запобігання паразитного витоку тепла від гарячого контакту до холодного).

Максимальний коефіцієнт корисної дії (ККД) термоелектричного генератора, що працює між гарячим резервуаром `T_hot` та холодним резервуаром `T_cold`, описується формулою:

```
η_max = ((T_hot − T_cold) / T_hot) · ((√(1 + ZT_avg) − 1) / (√(1 + ZT_avg) + T_cold / T_hot))
```

де перший множник дорівнює граничному ККД ідеального циклу Карно `η_Carnot = (T_hot − T_cold) / T_hot`, а другий множник визначається добротністю матеріалу `ZT_avg` при середній температурі `T_avg = 0.5 · (T_hot + T_cold)`. При `ZT → ∞` ККД термоелектричного елемента наближається до термодинамічної границі Карно.

## 3. Крайові умови та аналіз тепло-електричного балансу

У реальному 1D термоелектричному стрижні довжиною `L_len` розподіл температури `T(x)` та потенціалу `φ(x)` описується стаціонарними рівняннями неперервності потоків:

```
∇ · J_e = 0   ⇒   d/dx (J_e) = 0   ⇒   J_e = const
∇ · J_q = E · J_e   ⇒   d/dx (J_q) = J_e · (−dφ/dx)
```

Права частина другого рівняння описує локальне джоулеве тепловиділення `q_Joule = J_e² / σ`. Крім того, при наявності температурної залежності коефіцієнта Зеебека `dS/dT ≠ 0` виникає об'ємне тепло Томсона `q_Thomson = −τ · J_e · ∇T`, де `τ = T · (dS/dT)` — коефіцієнт Томсона.

Програма моделює фізичний стан термоелектричного стрижня при роботі у режимі генерації електричної енергії з наступними крайовими умовами:
- **На гарячому кінці (`x = 0`):** фіксована температура `T(0) = T_hot`;
- **На холодному кінці (`x = L_len`):** фіксована температура `T(L_len) = T_cold`;
- **На електричних виводах:** підключення зовнішнього корисного навантаження з опором `R_load`.

Алгоритм чисельного розрахунку включає наступні кроки:

1. **Розрахунок середньої температури стрижня:** `T_avg = 0.5 · (T_hot + T_cold)`.
2. **Формування матриці Онсагера `L`** на основі фізичних властивостей матеріалу `σ`, `κ`, `S` при температурі `T_avg`.
3. **Перевірка умов термодинамічної стабільності:** Другий закон термодинаміки вимагає невід'ємності швидкості утворення ентропії `σ_ent = J_q X_q + J_e X_e ≥ 0`. Для цього матриця `L` повинна бути додатно напіввизначеною:
   ```
   L_qq > 0,   L_ee > 0,   det(L) = L_qq · L_ee − L_qe · L_eq ≥ 0
   ```
4. **Обчислення термодинамічних сил:**
   - Сила температурного градієнта: `X_q = ∇(1/T) ≈ −(T_hot − T_cold) / (T_avg² · L_len)`.
   - Термо-ЕРС розімкненого кола: `V_oc = S · (T_hot − T_cold)`.
5. **Розрахунок струму у колі з навантаженням:**
   - Внутрішній електричний опір стрижня: `R_int = L_len / (σ · A)`.
   - Густина струму у колі: `J_e = V_oc / (A · (R_int + R_load))`.
6. **Розрахунок потенціальної термодинамічної сили `X_e`:** `X_e = −∇(φ/T) = (J_e / σ) / T_avg`.
7. **Обчислення підсумкових потоків тепла та енергії:**
   - Потік тепла через гарячий контакт: `J_q = L_qq · X_q + L_qe · X_e`.
   - Корисна електрична потужність на навантаженні: `P_elec = (J_e · A)² · R_load`.
   - Коефіцієнт корисної дії (ККД) перетворення: `η = (P_elec / (J_q · A)) · 100%`.

## 4. Двомовна реалізація моделювання (C та C++)

Нижче наведено повні реалізації алгоритму розрахунку термоелектричного елемента на мовах C (процедурний підхід із суворим контролем пам'яті та структур) та C++ (сучасний об'єктно-орієнтований підхід із використанням `std::expected`, `constexpr` та типів-обгорток).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

/* Структура для зберігання коефіцієнтів феноменологічної матриці Онсагера L */
typedef struct {
    double L_qq; /* Коефіцієнт тепло-тепло (Вт·К/м) */
    double L_qe; /* Коефіцієнт тепло-заряд (В·К·См/м) */
    double L_eq; /* Коефіцієнт заряд-тепло (В·К·См/м) */
    double L_ee; /* Коефіцієнт заряд-заряд (К·См/м) */
} OnsagerMatrix;

/* Макроскопічні характеристики термоелектричного матеріалу */
typedef struct {
    double sigma;   /* Питома електропровідність (См/м) */
    double kappa;   /* Питома теплопровідність (Вт/(м·К)) */
    double seebeck; /* Коефіцієнт Зеебека (В/К) */
} ThermoMaterial;

/* Результати чисельного моделювання термоелектричного переносу */
typedef struct {
    double heat_flux;          /* Потік тепла J_q (Вт/м²) */
    double current_density;    /* Густина струму J_e (А/м²) */
    double open_circuit_v;     /* Напруга холостого ходу (В) */
    double peltier_coeff;      /* Обчислений коефіцієнт Пельтьє (В) */
    double electrical_power_w; /* Корисна електрична потужність (Вт) */
    double efficiency_percent; /* Коефіцієнт корисної дії (%) */
    double zt_figure_of_merit; /* Безрозмірна добротність ZT */
} TransportResult;

/* Обчислення елементів матриці Онсагера за макроскопічними параметрами */
OnsagerMatrix compute_onsager_matrix(const ThermoMaterial* mat, double temp_k) {
    OnsagerMatrix L;
    L.L_ee = mat->sigma * temp_k;
    L.L_eq = mat->seebeck * mat->sigma * temp_k * temp_k;
    
    /* Застосування співвідношення взаємності Онсагера L_qe = L_eq */
    L.L_qe = L.L_eq; 
    
    L.L_qq = (mat->kappa + mat->seebeck * mat->seebeck * mat->sigma * temp_k) * temp_k * temp_k;
    return L;
}

/* Перевірка термодинамічної стабільності (додатна визначеність матриці L) */
bool validate_thermodynamic_stability(const OnsagerMatrix* L) {
    if (!L) return false;
    double det = L->L_qq * L->L_ee - L->L_qe * L->L_eq;
    return (L->L_qq > 0.0) && (L->L_ee > 0.0) && (det >= 0.0);
}

/* Симуляція процесів переносу у термоелектричному стрижні */
bool simulate_thermoelectric_leg(const ThermoMaterial* mat,
                                 double t_hot, double t_cold,
                                 double length, double cross_section_area,
                                 double load_resistance,
                                 TransportResult* res) {
    if (!mat || !res || length <= 0.0 || cross_section_area <= 0.0 || t_hot <= t_cold) {
        return false;
    }

    double t_avg = 0.5 * (t_hot + t_cold);
    OnsagerMatrix L = compute_onsager_matrix(mat, t_avg);

    if (!validate_thermodynamic_stability(&L)) {
        fprintf(stderr, "Помилка: порушено умову стабільності матриці Онсагера!\n");
        return false;
    }

    /* Обчислення добротності ZT */
    res->zt_figure_of_merit = (mat->seebeck * mat->seebeck * mat->sigma / mat->kappa) * t_avg;

    /* Термодинамічна сила градієнта температури X_q = ∇(1/T) */
    double X_q = -(t_hot - t_cold) / (t_avg * t_avg * length);

    /* Генерована термо-ЕРС Зеебека */
    res->open_circuit_v = mat->seebeck * (t_hot - t_cold);
    res->peltier_coeff = L.L_qe / L.L_ee; /* Співвідношення Кельвіна: Π = L_qe / L_ee = S · T */

    /* Внутрішній опір стрижня та розрахунок струму */
    double internal_resistance = length / (mat->sigma * cross_section_area);
    double total_current = res->open_circuit_v / (internal_resistance + load_resistance);
    res->current_density = total_current / cross_section_area;
    
    /* Термодинамічна сила електричного потенціалу X_e = -∇(φ/T) */
    double grad_phi = -res->current_density / mat->sigma;
    double X_e = -grad_phi / t_avg;

    /* Обчислення теплового потоку за рівнянням Онсагера */
    res->heat_flux = L.L_qq * X_q + L.L_qe * X_e;

    /* Потужність та ККД перетворення */
    res->electrical_power_w = total_current * total_current * load_resistance;
    double total_thermal_input_w = res->heat_flux * cross_section_area;
    res->efficiency_percent = (res->electrical_power_w / total_thermal_input_w) * 100.0;

    return true;
}

int main(void) {
    /* Параметри матеріалу телуриду вісмуту Bi2Te3 */
    ThermoMaterial bi2te3 = {
        .sigma = 100000.0,   /* Питома провідність 10^5 См/м */
        .kappa = 1.5,        /* Питома теплопровідність 1.5 Вт/(м·К) */
        .seebeck = 200e-6    /* Коефіцієнт Зеебека 200 мкВ/К */
    };

    double t_hot = 373.15;            /* 100 °C */
    double t_cold = 293.15;           /* 20 °C */
    double leg_length = 0.005;        /* Довжина 5 мм */
    double area = 1e-6;               /* Переріз 1 мм² */
    double r_load = 0.25;             /* Опір навантаження 0.25 Ом */

    TransportResult result;
    if (simulate_thermoelectric_leg(&bi2te3, t_hot, t_cold, leg_length, area, r_load, &result)) {
        printf("=== Результати розрахунку термоелектричного елемента (C) ===\n");
        printf("Різниця температур ΔT: %.2f K\n", t_hot - t_cold);
        printf("Добротність матеріалу ZT: %.4f\n", result.zt_figure_of_merit);
        printf("Генерована термо-ЕРС:   %.4f В\n", result.open_circuit_v);
        printf("Коефіцієнт Пельтьє Π:   %.4f В (Очікувано S·T: %.4f В)\n",
               result.peltier_coeff, bi2te3.seebeck * 0.5 * (t_hot + t_cold));
        printf("Густина тепла J_q:      %.2f Вт/м²\n", result.heat_flux);
        printf("Густина струму J_e:     %.2f А/м²\n", result.current_density);
        printf("Корисна потужність P:   %.6f Вт\n", result.electrical_power_w);
        printf("ККД перетворення:       %.2f %%\n", result.efficiency_percent);
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

struct ThermoMaterial {
    double sigma;   // Питома електропровідність (См/м)
    double kappa;   // Питома теплопровідність (Вт/(м·К))
    double seebeck; // Коефіцієнт Зеебека (В/К)
};

class OnsagerCoupledSolver {
public:
    struct Matrix {
        double L_qq;
        double L_qe;
        double L_eq;
        double L_ee;

        [[nodiscard]] constexpr bool is_thermodynamically_stable() const noexcept {
            const double det = L_qq * L_ee - L_qe * L_eq;
            return (L_qq > 0.0) && (L_ee > 0.0) && (det >= 0.0);
        }
    };

    struct SimulationResult {
        double heat_flux;           // Потік тепла J_q (Вт/м²)
        double current_density;     // Густина струму J_e (А/м²)
        double open_circuit_voltage;// Напруга холостого ходу (В)
        double peltier_coefficient; // Коефіцієнт Пельтьє (В)
        double electrical_power_w;  // Потужність на навантаженні (Вт)
        double efficiency_percent;  // ККД (%)
        double zt_figure_of_merit;  // Безрозмірна добротність ZT
    };

    enum class SimulationError {
        InvalidGeometry,
        InvalidTemperature,
        UnstableMatrix
    };

    static constexpr Matrix build_onsager_matrix(const ThermoMaterial& mat, double temp_k) noexcept {
        const double L_ee = mat.sigma * temp_k;
        const double L_eq = mat.seebeck * mat.sigma * temp_k * temp_k;
        // Симетрія Онсагера: L_qe = L_eq
        const double L_qe = L_eq; 
        const double L_qq = (mat.kappa + mat.seebeck * mat.seebeck * mat.sigma * temp_k) * temp_k * temp_k;

        return Matrix{ .L_qq = L_qq, .L_qe = L_qe, .L_eq = L_eq, .L_ee = L_ee };
    }

    static std::expected<SimulationResult, SimulationError> simulate(
        const ThermoMaterial& mat,
        double t_hot, double t_cold,
        double length, double area,
        double load_resistance) noexcept
    {
        if (length <= 0.0 || area <= 0.0) return std::unexpected(SimulationError::InvalidGeometry);
        if (t_hot <= t_cold) return std::unexpected(SimulationError::InvalidTemperature);

        const double t_avg = 0.5 * (t_hot + t_cold);
        const Matrix L = build_onsager_matrix(mat, t_avg);

        if (!L.is_thermodynamically_stable()) {
            return std::unexpected(SimulationError::UnstableMatrix);
        }

        const double zt = (mat.seebeck * mat.seebeck * mat.sigma / mat.kappa) * t_avg;
        const double X_q = -(t_hot - t_cold) / (t_avg * t_avg * length);
        const double open_circuit_v = mat.seebeck * (t_hot - t_cold);
        const double peltier_coeff = L.L_qe / L.L_ee;

        const double internal_r = length / (mat.sigma * area);
        const double total_current = open_circuit_v / (internal_r + load_resistance);
        const double current_density = total_current / area;

        const double grad_phi = -current_density / mat.sigma;
        const double X_e = -grad_phi / t_avg;

        const double j_q = L.L_qq * X_q + L.L_qe * X_e;
        const double j_e = L.L_eq * X_q + L.L_ee * X_e;

        const double electrical_power = total_current * total_current * load_resistance;
        const double total_thermal_input = j_q * area;
        const double efficiency = (electrical_power / total_thermal_input) * 100.0;

        return SimulationResult{
            .heat_flux = j_q,
            .current_density = j_e,
            .open_circuit_voltage = open_circuit_v,
            .peltier_coefficient = peltier_coeff,
            .electrical_power_w = electrical_power,
            .efficiency_percent = efficiency,
            .zt_figure_of_merit = zt
        };
    }
};

int main() {
    constexpr ThermoMaterial bi2te3{
        .sigma = 100000.0,
        .kappa = 1.5,
        .seebeck = 200e-6
    };

    constexpr double t_hot = 373.15;
    constexpr double t_cold = 293.15;
    constexpr double length = 0.005;
    constexpr double area = 1e-6;
    constexpr double load_r = 0.25;

    auto result = OnsagerCoupledSolver::simulate(bi2te3, t_hot, t_cold, length, area, load_r);

    if (result) {
        std::cout << std::fixed << std::setprecision(4);
        std::cout << "=== Симуляція термоелектричного елемента (C++) ===\n";
        std::cout << "Добротність ZT:        " << result->zt_figure_of_merit << "\n";
        std::cout << "Термо-ЕРС (Зеебек):    " << result->open_circuit_voltage << " В\n";
        std::cout << "Коефіцієнт Пельтьє:    " << result->peltier_coefficient << " В\n";
        std::cout << "Густина тепла J_q:     " << result->heat_flux << " Вт/м²\n";
        std::cout << "Густина струму J_e:    " << result->current_density << " А/м²\n";
        std::cout << "Потужність P:          " << std::setprecision(6) << result->electrical_power_w << " Вт\n";
        std::cout << "ККД перетворення:      " << std::setprecision(2) << result->efficiency_percent << " %\n";
    } else {
        std::cerr << "Помилка симуляції термодинамічного переносу!\n";
    }

    return 0;
}
```
:::

## 5. Аналіз результатів та фізичні висновки

Чисельне моделювання демонструє ключові фундаментальні наслідки теорії Онсагера:

1. **Точне виконання співвідношення Кельвіна `Π = S · T`:** У програмі коефіцієнт Пельтьє обчислюється як відношення коефіцієнтів Онсагера `L_qe / L_ee`. Його значення повністю збігається з макроскопічним добутком `S · T_avg` (`200 мкВ/К · 333.15 К = 0.0666 В`).
2. **Вплив перехресних потоків на ККД:** Наявність електричного струму зменшує загальний потік тепла через термоелемент у порівнянні з чистою теплопровідністю, що забезпечує додатну корисну електричну потужність на навантаженні.
3. **Оптимізація навантаження:** Максимальна корисна потужність досягається при узгодженні опору зовнішнього навантаження `R_load` з внутрішнім опором стрижня `R_int`, що становить основу інженерного проектування термоелектричних генераторів космічних апаратів (РИТЕГ) та побутових модулів Охолодження Пельтьє.
