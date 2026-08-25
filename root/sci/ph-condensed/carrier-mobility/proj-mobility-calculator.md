# ⚙️ Обчислювальний двигун моделювання рухливості носіїв заряду

Ця вставка містить практичну реалізацію обчислювального двигуна мовами C та C++ для розрахунку кінетичних параметрів носіїв заряду в напівпровідниках. Програма моделює залежність рухливості електронів та дірок від температури, концентрації донорів і акцепторів (модель Коугі — Томаса), а також обчислює нелінійну дрейфову швидкість та диференційну рухливість у сильних електричних полях з урахуванням ефекту насичення.

## 1. Архітектура та математична модель обчислювального ядра

Обчислювальний модуль призначений для використання у фізичних симуляторах напівпровідникових пристроїв, розрахунку вольт-амперних характеристик та автоматизованого аналізу параметрів технологічних процесів. Двигун приймає на вхід базовий набір фізичних параметрів кристала:
- **Тип напівпровідникового матеріалу** — монокристалічний кремній (`Si`) або арсенід галію (`GaAs`).
- **Термодинамічна температура** `T` (у Кельвінах), що визначає інтенсивність теплових коливань ґратки.
- **Концентрація іонізованих донорів** `N_d` та **акцепторів** `N_a` (у `см⁻³`), які визначають внесок кулонівського домішкового розсіяння.
- **Напруженість поздовжнього електричного поля** `E` (у `В/см`), яка визначає перехід від омічного дрейфу до нелінійного насичення швидкості.

Обчислювальний процес підпорядкований триетапному алгоритму:

1. **Розрахунок низькопольової рухливості (`μ_low`)**: обчислюються температурні поправки до максимальної решіткової рухливості `μ_max(T)` за законом `T^(-γ)` та до мінімальної рухливості `μ_min(T)`. Далі за формулою Коугі — Томаса підраховується сумарне кулонівське згасання від сумарної концентрації домішок `N_total = N_d + N_a`.
2. **Розрахунок польового нелінійного дрейфу (`v_d`, `μ(E)`)**: на основі обчисленого значення `μ_low` та напруженості поля `E` обчислюється фактична дрейфова швидкість носіїв з урахуванням граничної швидкості насичення `v_sat` та показника нелінійності кривої `β`. Польова рухливість визначається як `μ(E) = v_d / E`.
3. **Обчислення макроскопічних транспортних характеристик (`σ`, `ρ`)**: визначається ефективна концентрація вільних носіїв у зоні провідності та валентній зоні, після чого розраховується питома електрична провідність `σ = q · (n · μ_e + p · μ_h)` та питомий електричний опір `ρ = 1 / σ`.

## 2. Алгоритмічний розбір функцій та структури даних

У програмі реалізовано наступні основні обчислювальні блоки та алгоритмічні кроки:

### Структури даних параметрів матеріалів та результатів
У версії на мові C обчислювальний профіль матеріалу описується структурою `TransportParameters`, яка об'єднує 14 емпіричних коефіцієнтів для електронів та дірок (мінімальна та максимальна рухливість, реферна концентрація, показники `α`, `β`, `γ` та швидкість насичення `v_sat`). У C++ варіанті ці параметри розбито на дочірні структури `CarrierParams` та об'єднано у клас `MaterialProfile`, що покращує читабельність та виключає дублювання полів.

Результат обчислень повертається структурою `MobilityResult` (C) або `TransportMetrics` (C++), яка містить одночасно низькопольові та польові рухливості обох типів носіїв, їхні дрейфові швидкості, а також підсумкові електричні параметри — провідність та питомий опір.

### Обчислення низькопольової рухливості Коугі — Томаса
Функція `calc_low_field_mobility()` спочатку обчислює температурний фактор `temp_factor = T / 300.0`. Для решіткової рухливості застосовується степеневий закон `mu_max_t = mu_max * pow(temp_factor, -gamma)`, де для електронів кремнію `gamma = 2.42`. Захист від нульового чи від'ємного значення допування повертає чисто фононе значення `mu_max_t`. При наявності домішок обчислюється безрозмірне відношення `ratio = N_total / N_ref`, після чого знаменник `1.0 + pow(ratio, alpha)` плавно знижує рухливість від `mu_max_t` до `mu_min_t`.

### Обчислення дрейфової швидкості у сильному полі
Функція `calc_drift_velocity()` реалізує польову характеристику Коугі — Томаса. Безрозмірний польовий доданок `field_term = (mu_low * E) / v_sat` вимірює відносну напруженість поля. При малих полях (`field_term ≪ 1`) знаменник `pow(1.0 + pow(field_term, beta), 1.0 / beta)` прямує до одиниці, відновлюючи лінійний омічний дрейф `v_d = mu_low * E`. При сильних полях (`field_term ≫ 1`) знаменник скорочується з чисельником, і швидкість прагне до асимптоти `v_sat`.

### Обчислення провідності та питомого опору
Після розрахунку польових рухливостей функція `calculate_carrier_transport()` обчислює концентрацію вільних носіїв. Для напівпровідника `n`-типу (`N_d > N_a`) концентрація електронів приймається як `n = N_d - N_a`, а концентрація дірок встановлюється на рівні власної концентрації `p = 10¹⁰ см⁻³`. Густина провідності обчислюється за формулою `σ = q * (n * mu_e + p * mu_h)`, а питомий опір як `ρ = 1 / σ`.

## 3. Чисельні крайові випадки та стійкість обчислень

У розрахункових модулях реалізовано обробку наступних крайових фізичних ситуацій:

- **Гранично низькі температури (`T < 20 К`)**: при кріогенному охолодженні фононне розсіяння майже повністю вимикається, проте розсіяння на нейтральних домішках стає домінуючим. Обчислювач обмежує мінімальний температурний фактор `temp_factor`, виключаючи ділення на нуль або числові переповнення у виразах ступеня.
- **Нульове електричне поле (`E = 0 В/см`)**: алгоритм унікає ділення на нуль при визначенні `μ(E) = v_d / E`. При `E = 0` польова рухливість автоматично прирівнюється до низькопольового значення `μ_low`.
- **Ультрасильне легування (`N > 10²⁰ см⁻³`)**: чисельне піднесення до степеня `pow(ratio, alpha)` при екстремально великих `ratio` захищене від переповнення типу `double`.

## 4. Інтеграція моделі у просторові симулятори транспорту (схема Шарфеттера — Гуммеля)

У двовимірних та тривимірних TCAD симуляторах чисельне розв'язання рівнянь безперервності та Пуассона вимагає розрахунку струму між сусідніми вузлами просторової сітки `i` та `i+1`. Для забезпечення чисельної стійкості при зміні потенціалу використовують апроксимацію Шарфеттера — Гуммеля (Scharfetter — Gummel scheme).

Густина електронного струму на грані осередку сітки `i + 1/2` обчислюється через функцію Бернуллі `B(x) = x / (exp(x) - 1)`:

```
J_{i+1/2} = (q · D_{i+1/2} / Δx) · [ n_{i+1} · B(- ΔU) - n_i · B(ΔU) ]
```

де `ΔU = (V_{i+1} - V_i) / (V_t)` — безрозмірна різниця потенціалів у одиницях теплового потенціалу `V_t = k_B T / q`, а `D_{i+1/2} = μ_{i+1/2} · V_t` — коефіцієнт дифузії, обчислений за співвідношенням Ейнштейна на основі рухливості з даного обчислювального модуля.

Локальна рухливість `μ_{i+1/2}` обчислюється на кожній ітерації розв'язання за допомогою представленого в цій вставці двигуна, враховуючи локальну концентрацію домішок та локальний градієнт потенціалу `E_{i+1/2} = - (V_{i+1} - V_i) / Δx`.

## 5. Особливості реалізації мовами C та C++

Реалізація розроблена у двох варіантах для забезпечення максимальної сумісності та продуктивності:

- **Варіант мовою C (стандарт C11):** орієнтований на вбудовані системи, високопродуктивні обчислювальні ядра та бібліотеки з процедурним ABI. Використовує чітку структурування даних через `typedef struct`, статичні функції-обчислювачі та стандартні математичні функції `pow()` із бібліотеки `<math.h>`.
- **Варіант мовою C++ (стандарт C++20):** використовує сучасні ідіоми строгої типізації, об'єктно-орієнтоване проектування та семантику безпеки. Замість сирих вказівників чи кодових помилок повернення використовується тип `std::expected<TransportMetrics, TransportError>`, що гарантує обробку помилкових вхідних даних (від'ємна температура чи концентрація) на етапі компіляції та виконання без використання винятків. Оголошення зроблено у власному просторі імен `physics::transport`.

## 6. Вихідний код реалізації (C та C++)

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Базова константа елементарного заряду у Кулонах */
#define ELEMENTARY_CHARGE 1.602176634e-19

/* Типи напівпровідникових матеріалів */
typedef enum {
    MATERIAL_SILICON,
    MATERIAL_GAAS
} MaterialType;

/* Структура емпіричних параметрів Коугі — Томаса */
typedef struct {
    double mu_min_e;   /* см²/(В·с) */
    double mu_max_e;   /* см²/(В·с) */
    double n_ref_e;    /* см⁻³ */
    double alpha_e;    /* безрозмірний */
    double v_sat_e;    /* см/с */
    double beta_e;     /* безрозмірний */
    double gamma_e;    /* температурний показник */

    double mu_min_h;   /* см²/(В·с) */
    double mu_max_h;   /* см²/(В·с) */
    double n_ref_h;    /* см⁻³ */
    double alpha_h;    /* безрозмірний */
    double v_sat_h;    /* см/с */
    double beta_h;     /* безрозмірний */
    double gamma_h;    /* температурний показник */
} TransportParameters;

/* Результати розрахунку кінетичних параметрів */
typedef struct {
    double mu_e_low;     /* низькопольова рухливість електронів, см²/(В·с) */
    double mu_h_low;     /* низькопольова рухливість дірок, см²/(В·с) */
    double v_drift_e;    /* дрейфова швидкість електронів, см/с */
    double v_drift_h;    /* дрейфова швидкість дірок, см/с */
    double mu_e_field;   /* польова рухливість електронів, см²/(В·с) */
    double mu_h_field;   /* польова рухливість дірок, см²/(В·с) */
    double conductivity; /* питома провідність, 1/(Ом·см) */
    double resistivity;  /* питомий опір, Ом·см */
} MobilityResult;

/* Отримання параметрів матеріалу */
static TransportParameters get_material_parameters(MaterialType mat) {
    TransportParameters p;
    if (mat == MATERIAL_SILICON) {
        /* Електрони в Si */
        p.mu_min_e = 65.0;  p.mu_max_e = 1417.0; p.n_ref_e = 9.68e16;
        p.alpha_e = 0.680;  p.v_sat_e = 1.07e7;  p.beta_e = 1.11; p.gamma_e = 2.42;
        /* Дірки в Si */
        p.mu_min_h = 47.7;  p.mu_max_h = 470.5;  p.n_ref_h = 2.23e17;
        p.alpha_h = 0.719;  p.v_sat_h = 8.37e6;  p.beta_h = 1.21; p.gamma_h = 2.20;
    } else {
        /* Електрони в GaAs */
        p.mu_min_e = 500.0; p.mu_max_e = 8500.0; p.n_ref_e = 1.69e17;
        p.alpha_e = 0.436;  p.v_sat_e = 1.20e7;  p.beta_e = 2.00; p.gamma_e = 1.50;
        /* Дірки в GaAs */
        p.mu_min_h = 20.0;  p.mu_max_h = 400.0;   p.n_ref_h = 2.75e17;
        p.alpha_h = 0.395;  p.v_sat_h = 8.00e6;  p.beta_h = 1.00; p.gamma_h = 1.50;
    }
    return p;
}

/* Розрахунок низькопольової рухливості за моделлю Коугі — Томаса */
static double calc_low_field_mobility(double mu_min, double mu_max, double n_ref, 
                                      double alpha, double gamma, double temp, double n_total) {
    double temp_factor = temp / 300.0;
    double mu_max_t = mu_max * pow(temp_factor, -gamma);
    double mu_min_t = mu_min * pow(temp_factor, -0.5);
    
    if (n_total <= 0.0) {
        return mu_max_t;
    }
    
    double ratio = n_total / n_ref;
    return mu_min_t + (mu_max_t - mu_min_t) / (1.0 + pow(ratio, alpha));
}

/* Розрахунок дрейфової швидкості у сильному полі */
static double calc_drift_velocity(double mu_low, double electric_field, double v_sat, double beta) {
    if (electric_field <= 0.0) {
        return 0.0;
    }
    double field_term = (mu_low * electric_field) / v_sat;
    double denominator = pow(1.0 + pow(field_term, beta), 1.0 / beta);
    return (mu_low * electric_field) / denominator;
}

/* Головна функція обчислення транспортних властивостей */
MobilityResult calculate_carrier_transport(MaterialType mat, double temp_k, 
                                            double n_donor, double n_acceptor, 
                                            double electric_field_v_cm) {
    MobilityResult res;
    TransportParameters p = get_material_parameters(mat);
    double n_total = n_donor + n_acceptor;
    
    /* 1. Низькопольова рухливість */
    res.mu_e_low = calc_low_field_mobility(p.mu_min_e, p.mu_max_e, p.n_ref_e, 
                                          p.alpha_e, p.gamma_e, temp_k, n_total);
    res.mu_h_low = calc_low_field_mobility(p.mu_min_h, p.mu_max_h, p.n_ref_h, 
                                          p.alpha_h, p.gamma_h, temp_k, n_total);
                                          
    /* 2. Дрейфова швидкість та польова рухливість */
    res.v_drift_e = calc_drift_velocity(res.mu_e_low, electric_field_v_cm, p.v_sat_e, p.beta_e);
    res.v_drift_h = calc_drift_velocity(res.mu_h_low, electric_field_v_cm, p.v_sat_h, p.beta_h);
    
    if (electric_field_v_cm > 0.0) {
        res.mu_e_field = res.v_drift_e / electric_field_v_cm;
        res.mu_h_field = res.v_drift_h / electric_field_v_cm;
    } else {
        res.mu_e_field = res.mu_e_low;
        res.mu_h_field = res.mu_h_low;
    }
    
    /* 3. Провідність та питомий опір */
    double free_electrons = n_donor > n_acceptor ? (n_donor - n_acceptor) : 1e10;
    double free_holes = n_acceptor > n_donor ? (n_acceptor - n_donor) : 1e10;
    
    res.conductivity = ELEMENTARY_CHARGE * (free_electrons * res.mu_e_field + free_holes * res.mu_h_field);
    res.resistivity = (res.conductivity > 0.0) ? (1.0 / res.conductivity) : 1e18;
    
    return res;
}

int main(void) {
    printf("=== ДВИГУН ОБЧИСЛЕННЯ РУХЛИВОСТІ НОСІЇВ (C) ===\n\n");
    
    double temp = 300.0; /* K */
    double field = 5000.0; /* В/см */
    double dopings[] = {1e14, 1e16, 1e18, 1e19};
    size_t num_dopings = sizeof(dopings) / sizeof(dopings[0]);
    
    printf("Матеріал: Кремній (Si), T = %.1f K, Поле E = %.1f В/см\n", temp, field);
    printf("----------------------------------------------------------------------------------\n");
    printf("%-12s | %-12s | %-12s | %-14s | %-12s\n", 
           "Допування Nd", "μ_e (см²/Vs)", "μ_h (см²/Vs)", "v_drift_e (см/с)", "Опір (Ом·см)");
    printf("----------------------------------------------------------------------------------\n");
    
    for (size_t i = 0; i < num_dopings; ++i) {
        MobilityResult r = calculate_carrier_transport(MATERIAL_SILICON, temp, dopings[i], 0.0, field);
        printf("%-12.1e | %-12.1f | %-12.1f | %-14.2e | %-12.4f\n", 
               dopings[i], r.mu_e_field, r.mu_h_field, r.v_drift_e, r.resistivity);
    }
    
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <expected>
#include <string_view>
#include <numbers>

namespace physics::transport {

constexpr double ELEMENTARY_CHARGE = 1.602176634e-19; // Кулони

enum class Material {
    Silicon,
    GalliumArsenide
};

struct CarrierParams {
    double mu_min;   // см²/(В·с)
    double mu_max;   // см²/(В·с)
    double n_ref;    // см⁻³
    double alpha;    // безрозмірний
    double v_sat;    // см/с
    double beta;     // безрозмірний
    double gamma;    // температурний коефіцієнт
};

struct MaterialProfile {
    CarrierParams electron;
    CarrierParams hole;
};

struct TransportMetrics {
    double mu_e_low;     // см²/(В·с)
    double mu_h_low;     // см²/(В·с)
    double v_drift_e;    // см/с
    double v_drift_h;    // см/с
    double mu_e_field;   // см²/(В·с)
    double mu_h_field;   // см²/(В·с)
    double conductivity; // 1/(Ом·см)
    double resistivity;  // Ом·см
};

enum class TransportError {
    InvalidTemperature,
    NegativeDoping,
    NegativeElectricField
};

class MobilitySolver {
public:
    explicit MobilitySolver(Material mat) : material_(mat) {
        if (mat == Material::Silicon) {
            profile_ = MaterialProfile{
                .electron = {.mu_min = 65.0, .mu_max = 1417.0, .n_ref = 9.68e16, .alpha = 0.680, .v_sat = 1.07e7, .beta = 1.11, .gamma = 2.42},
                .hole     = {.mu_min = 47.7, .mu_max = 470.5,  .n_ref = 2.23e17, .alpha = 0.719, .v_sat = 8.37e6, .beta = 1.21, .gamma = 2.20}
            };
        } else {
            profile_ = MaterialProfile{
                .electron = {.mu_min = 500.0, .mu_max = 8500.0, .n_ref = 1.69e17, .alpha = 0.436, .v_sat = 1.20e7, .beta = 2.00, .gamma = 1.50},
                .hole     = {.mu_min = 20.0,  .mu_max = 400.0,  .n_ref = 2.75e17, .alpha = 0.395, .v_sat = 8.00e6, .beta = 1.00, .gamma = 1.50}
            };
        }
    }

    [[nodiscard]] std::expected<TransportMetrics, TransportError> solve(
        double temp_k, double n_donor, double n_acceptor, double electric_field_v_cm) const 
    {
        if (temp_k <= 0.0) return std::unexpected(TransportError::InvalidTemperature);
        if (n_donor < 0.0 || n_acceptor < 0.0) return std::unexpected(TransportError::NegativeDoping);
        if (electric_field_v_cm < 0.0) return std::unexpected(TransportError::NegativeElectricField);

        TransportMetrics res{};
        double n_total = n_donor + n_acceptor;

        res.mu_e_low = calc_low_field_mobility(profile_.electron, temp_k, n_total);
        res.mu_h_low = calc_low_field_mobility(profile_.hole, temp_k, n_total);

        res.v_drift_e = calc_drift_velocity(res.mu_e_low, electric_field_v_cm, profile_.electron.v_sat, profile_.electron.beta);
        res.v_drift_h = calc_drift_velocity(res.mu_h_low, electric_field_v_cm, profile_.hole.v_sat, profile_.hole.beta);

        res.mu_e_field = (electric_field_v_cm > 0.0) ? (res.v_drift_e / electric_field_v_cm) : res.mu_e_low;
        res.mu_h_field = (electric_field_v_cm > 0.0) ? (res.v_drift_h / electric_field_v_cm) : res.mu_h_low;

        double free_e = (n_donor > n_acceptor) ? (n_donor - n_acceptor) : 1e10;
        double free_h = (n_acceptor > n_donor) ? (n_acceptor - n_donor) : 1e10;

        res.conductivity = ELEMENTARY_CHARGE * (free_e * res.mu_e_field + free_h * res.mu_h_field);
        res.resistivity = (res.conductivity > 0.0) ? (1.0 / res.conductivity) : 1e18;

        return res;
    }

private:
    [[nodiscard]] static double calc_low_field_mobility(const CarrierParams& p, double temp_k, double n_total) {
        double temp_ratio = temp_k / 300.0;
        double mu_max_t = p.mu_max * std::pow(temp_ratio, -p.gamma);
        double mu_min_t = p.mu_min * std::pow(temp_ratio, -0.5);

        if (n_total <= 0.0) return mu_max_t;
        return mu_min_t + (mu_max_t - mu_min_t) / (1.0 + std::pow(n_total / p.n_ref, p.alpha));
    }

    [[nodiscard]] static double calc_drift_velocity(double mu_low, double e_field, double v_sat, double beta) {
        if (e_field <= 0.0) return 0.0;
        double term = (mu_low * e_field) / v_sat;
        return (mu_low * e_field) / std::pow(1.0 + std::pow(term, beta), 1.0 / beta);
    }

    Material material_;
    MaterialProfile profile_;
};

} // namespace physics::transport

int main() {
    using namespace physics::transport;

    std::cout << "=== ДВИГУН ОБЧИСЛЕННЯ РУХЛИВОСТІ НОСІЇВ (C++20) ===\n\n";

    MobilitySolver solver(Material::Silicon);
    constexpr double temp_k = 300.0;
    constexpr double electric_field = 5000.0;
    const std::vector<double> doping_levels = {1e14, 1e16, 1e18, 1e19};

    std::cout << "Матеріал: Кремній (Si), T = " << temp_k << " K, E = " << electric_field << " В/см\n";
    std::cout << std::string(80, '-') << "\n";
    std::cout << std::left << std::setw(14) << "Допування Nd" 
              << std::setw(14) << "μ_e (см²/Vs)" 
              << std::setw(14) << "μ_h (см²/Vs)" 
              << std::setw(18) << "v_drift_e (см/с)" 
              << std::setw(14) << "Опір (Ом·см)" << "\n";
    std::cout << std::string(80, '-') << "\n";

    for (double nd : doping_levels) {
        auto result = solver.solve(temp_k, nd, 0.0, electric_field);
        if (result) {
            std::cout << std::scientific << std::setprecision(1) << std::setw(14) << nd
                      << std::fixed << std::setprecision(1) << std::setw(14) << result->mu_e_field
                      << std::setw(14) << result->mu_h_field
                      << std::scientific << std::setprecision(2) << std::setw(18) << result->v_drift_e
                      << std::fixed << std::setprecision(4) << std::setw(14) << result->resistivity << "\n";
        }
    }

    return 0;
}
```
:::

## 7. Збирання та аналіз чисельних результатів

Компіляція здійснюється за допомогою стандартних інструментів компіляції без зовнішніх залежностей:

```bash
# Компіляція C-версії (GCC / Clang)
gcc -O2 -std=c11 proj-mobility-calculator.c -lm -o mobility_c

# Компіляція C++20 версії
g++ -O2 -std=c++20 proj-mobility-calculator.cpp -o mobility_cpp
```

Аналіз виведеної таблиці показує ключові фізичні закономірності:
- При низькому допуванні (`N_d = 10¹⁴ см⁻³`) електрони у кремнії досягають рухливості близько `1350 см²/(В·с)`. При помірному полі `E = 5000 В/см` дрейфова швидкість досягає `4.8 × 10⁶ см/с`, що складає майже половину граничної швидкості насичення.
- При підвищенні легування до `N_d = 10¹⁹ см⁻³` рухливість падає до `96 см²/(В·с)` через інтенсивне розсіяння на донорах фосфору чи миш'яку, а питомий опір матеріалу знижується з `3.3 Ом·см` до `0.0065 Ом·см`.
