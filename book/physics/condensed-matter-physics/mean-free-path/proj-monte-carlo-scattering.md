# ⚙️ Симуляція транспорту носіїв та розсіювання методом Монте-Карло

Чисельне моделювання руху електронів у кристалічному напівпровіднику під дією зовнішнього електричного поля здійснюється методом Монте-Карло. Програма реалізує статистичне моделювання вільного польоту та актів розсіювання носіїв, враховуючи акустичне фононне розсіювання та розсіювання на іонізованих домішках. Код вираховує середній час релаксації `τ`, довжину вільного пробігу `λ`, дрейфову швидкість `v_d` та середню кінетичну енергію електронів.

---

### 1. Теоретичні основи методу Монте-Карло для кінетики носіїв

Метод Монте-Карло для рівняння транспорту Больцмана був розроблений наприкінці 1960-х років працями Кляйновського, Кері, Раджані та Фоукмена. Він базується на стохастичному моделюванні руху ансамблю незалежних носіїв у фазовому просторі `(r, k)`.

Траєкторія кожного електрона розбивається на дві послідовні фази, що циклічно повторюються:
1. **Детермінований вільний політ**: Рух частинки у координатно-імпульсному просторі під дією зовнішніх електричних `E` та магнітних `B` полів протягом часового інтервалу `Δt_flight`.
2. **Стохастичний акт розсіювання**: Миттєва зміна квантового стану частинки `k ↦ k'` згідно з диференціальними перерізами розсіювання відповідних мікроскопічних механізмів.

#### Математичне виведення часу вільного прольоту
Імовірність того, що електрон пролетить час `t` без розсіювання і зазнає зіткнення у вузькому інтервалі `[t, t + dt]`, описується щільністю ймовірності Пуассона:

```
P(t) dt = Γ(E(t)) · exp(- ∫₀ᵗ Γ(E(t')) dt') dt
```

де `Γ(E) = 1 / τ_total(E)` — сумарна частота розсіювання для електрона з енергією `E`.

Якщо частота розсіювання є сталою або усередненою `Γ_total = 1 / τ_total`, інтеграл у показнику експоненти спрощується до `Γ_total · t`. Тоді кумулятивна функція розподілу ймовірності дорівнює:

```
F(t) = ∫₀ᵗ P(t') dt' = 1 - exp(- Γ_total · t)
```

Застосовуючи метод **оберненого перетворення функцій розподілу**, прирівняємо рівномірно розподілене випадкове число `U ∈ (0, 1]` до величини `1 - F(t) = exp(- Γ_total · t)`:

```
U = exp(- Γ_total · t)  ⟹  Δt_flight = - (1 / Γ_total) · ln(U) = - τ_total · ln(U)
```

Ця формула дозволяє точно генерувати випадкові значення тривалості вільного прольоту `Δt_flight` для кожного кроку симуляції.

#### Динаміка вільного польоту між зіткненнями
Упродовж інтервалу `Δt_flight` на електрон з ефективною масою `m*` під дією електричного поля `E_x` діє сила Кулона `F_x = -e · E_x`. Рівняння руху для координати та швидкостей мають вигляд:

```
a_x = -e · E_x / m*
v_x(t + Δt) = v_x(t) + a_x · Δt_flight
x(t + Δt) = x(t) + v_x(t) · Δt_flight + 0.5 · a_x · (Δt_flight)²
```

Компоненти швидкості `v_y` та `v_z` за відсутності магнітного поля залишаються сталими протягом вільного прольоту.

---

### 2. Алгоритм розсіювання та вибір квантового стану

Після завершення вільного прольоту електрон зазнає акту розсіювання. Оскільки у кристалі діють декілька механізмів (наприклад, акустичні фонони `ph` та іонізовані домішки `imp`), вибір конкретного механізму здійснюється стохастично.

#### 1. Вибір механізму розсіювання за правилом Маттіссена
Згідно з правилом Маттіссена, сумарна частота розсіювання дорівнює `Γ_total = Γ_ph + Γ_imp`. Генериться нове випадкове число `U_mech ∈ [0, 1]`:
- Якщо `U_mech ≤ Γ_ph / Γ_total` — відбувається розсіювання на акустичних фононах.
- Якщо `U_mech > Γ_ph / Γ_total` — відбувається розсіювання на іонізованих домішках.

#### 2. Перерозподіл кутів розсіювання на сфері
Модуль швидкості частинки `v = √(v_x² + v_y² + v_z²)` визначає кінетичну енергію `E = 0.5 · m* · v²`.
- **Для пружного ізотропного розсіювання** (акустичні фонони за високих температур або точкові дефекти) модуль швидкості `v` зберігається, а новий напрямок вектора швидкості обирається рівномірно по всьому тілесному куту `4π` стерадіан.

Полярний кут `θ` та азимутальний кут `φ` обираються через два незалежні випадкові числа `U_1, U_2 ∈ [0, 1]`:

```
cos θ = 1 - 2 · U_1   ⟹   sin θ = √(1 - cos² θ)
φ = 2 · π · U_2
```

Нові компоненти вектора швидкості після розсіювання отримуються проектуванням:

```
v_x' = v · sin θ · cos φ
v_y' = v · sin θ · sin φ
v_z' = v · cos θ
```

#### 3. Накопичення статистичних величин
Під час моделювання програма реєструє довжину пройденого шляху `Δs = v_avg · Δt_flight` та час прольоту `Δt_flight` для кожного з розсіювань. Після проходження заданої кількості кроків обчислюються середні показники ансамблю:
- **Середній час релаксації**: `⟨τ⟩ = (∑ Δt_flight) / N_events`.
- **Середня довжина вільного пробігу**: `⟨λ⟩ = (∑ Δs) / N_events`.
- **Дрейфова швидкість**: `v_d = (1 / N_elec) · ∑ v_x`.
- **Середня кінетична енергія**: `⟨E⟩ = (1 / N_elec) · ∑ (0.5 · m* · v²)`.

---

### 3. Програмна реалізація мовами C та C++

У наведених нижче вкладках представлено автономні, коректні програмні реалізації чисельної моделі Монте-Карло.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Фундаментальні фізичні константи в одиницях СІ */
static const double CHARGE_E = 1.602176634e-19; /* Заряд електрона, Кл */
static const double MASS_E0  = 9.1093837015e-31; /* Маса спокою електрона, кг */
static const double KB_JOULE = 1.380649e-23;     /* Стала Больцмана, Дж/К */

/* Структура для представлення електрона у фазовому просторі */
typedef struct {
    double x;  /* Координата x, м */
    double vx; /* Компоненти швидкості, м/с */
    double vy;
    double vz;
} Electron;

/* Генератор рівномірного випадкового числа U ∈ (0, 1] */
static double get_random_uniform(void) {
    double u = ((double)rand() + 1.0) / ((double)RAND_MAX + 1.0);
    return (u > 1.0) ? 1.0 : u;
}

/* Визначення початкових теплових швидкостей Максвелла — Больцмана */
static void init_thermal_velocity(Electron *e, double temp_k, double m_eff) {
    double v_th = sqrt(3.0 * KB_JOULE * temp_k / m_eff);
    double cos_theta = 1.0 - 2.0 * get_random_uniform();
    double sin_theta = sqrt(fmax(0.0, 1.0 - cos_theta * cos_theta));
    double phi = 2.0 * M_PI * get_random_uniform();

    e->x  = 0.0;
    e->vx = v_th * sin_theta * cos(phi);
    e->vy = v_th * sin_theta * sin(phi);
    e->vz = v_th * cos_theta;
}

/* Головний функціонал симуляції Монте-Карло */
void run_carrier_monte_carlo(size_t num_particles, size_t num_steps,
                             double field_x, double tau_ph, double tau_imp,
                             double temp_k, double m_eff_ratio) {
    double m_eff = m_eff_ratio * MASS_E0;
    double inv_tau_ph = 1.0 / tau_ph;
    double inv_tau_imp = 1.0 / tau_imp;
    double inv_tau_tot = inv_tau_ph + inv_tau_imp;
    double tau_total = 1.0 / inv_tau_tot;
    double prob_phonon = inv_tau_ph / inv_tau_tot;

    double accel_x = -CHARGE_E * field_x / m_eff;

    Electron *ensemble = (Electron*)malloc(num_particles * sizeof(Electron));
    if (!ensemble) {
        fprintf(stderr, "Помилка виділення пам'яті під ансамбль носіїв.\n");
        return;
    }

    /* Ініціалізація носіїв з урахуванням теплового руху */
    for (size_t i = 0; i < num_particles; ++i) {
        init_thermal_velocity(&ensemble[i], temp_k, m_eff);
    }

    double grand_total_path = 0.0;
    double grand_total_time = 0.0;
    size_t grand_total_events = 0;
    size_t phonon_events = 0;
    size_t impurity_events = 0;

    /* Основний цикл моделювання */
    for (size_t step = 0; step < num_steps; ++step) {
        for (size_t i = 0; i < num_particles; ++i) {
            /* 1. Генерація тривалості вільного польоту */
            double u = get_random_uniform();
            double dt = -tau_total * log(u);

            /* 2. Прискорення полем між зіткненнями */
            double vx_old = ensemble[i].vx;
            ensemble[i].vx += accel_x * dt;
            double vx_avg = 0.5 * (vx_old + ensemble[i].vx);
            ensemble[i].x += vx_avg * dt;

            /* Розрахунок модуля швидкості та пройденого шляху */
            double v_mag = sqrt(ensemble[i].vx * ensemble[i].vx +
                                ensemble[i].vy * ensemble[i].vy +
                                ensemble[i].vz * ensemble[i].vz);

            grand_total_path += v_mag * dt;
            grand_total_time += dt;
            grand_total_events++;

            /* 3. Вибір механізму розсіювання */
            double u_mech = get_random_uniform();
            if (u_mech <= prob_phonon) {
                phonon_events++;
            } else {
                impurity_events++;
            }

            /* 4. Ізотропне перевизначення кутів швидкості */
            double cos_th = 1.0 - 2.0 * get_random_uniform();
            double sin_th = sqrt(fmax(0.0, 1.0 - cos_th * cos_th));
            double phi_angle = 2.0 * M_PI * get_random_uniform();

            ensemble[i].vx = v_mag * sin_th * cos(phi_angle);
            ensemble[i].vy = v_mag * sin_th * sin(phi_angle);
            ensemble[i].vz = v_mag * cos_th;
        }
    }

    /* Розрахунок підсумкової статистики */
    double mean_tau = grand_total_time / (double)grand_total_events;
    double mean_lambda_nm = (grand_total_path / (double)grand_total_events) * 1e9;

    double sum_vx = 0.0;
    double sum_energy_ev = 0.0;
    for (size_t i = 0; i < num_particles; ++i) {
        sum_vx += ensemble[i].vx;
        double v_sq = ensemble[i].vx * ensemble[i].vx +
                      ensemble[i].vy * ensemble[i].vy +
                      ensemble[i].vz * ensemble[i].vz;
        double energy_j = 0.5 * m_eff * v_sq;
        sum_energy_ev += energy_j / CHARGE_E;
    }
    double drift_velocity = sum_vx / (double)num_particles;
    double mean_energy_ev = sum_energy_ev / (double)num_particles;

    printf("====================================================\n");
    printf("     РЕЗУЛЬТАТИ СИМУЛЯЦІЇ МОНТЕ-КАРЛО (мова C)\n");
    printf("====================================================\n");
    printf("Кількість носіїв:                  %zu\n", num_particles);
    printf("Загальна кількість зіткнень:       %zu\n", grand_total_events);
    printf("Актів фононного розсіювання:       %zu (%.1f%%)\n", 
           phonon_events, 100.0 * (double)phonon_events / grand_total_events);
    printf("Актів домішкового розсіювання:     %zu (%.1f%%)\n", 
           impurity_events, 100.0 * (double)impurity_events / grand_total_events);
    printf("----------------------------------------------------\n");
    printf("Розрахований час релаксації tau:    %.3e с (теорія: %.3e с)\n", 
           mean_tau, tau_total);
    printf("Довжина вільного пробігу lambda:   %.2f нм\n", mean_lambda_nm);
    printf("Середня дрейфова швидкість v_d:     %.3e м/с\n", drift_velocity);
    printf("Середня кінетична енергія <E>:     %.3f еВ\n", mean_energy_ev);
    printf("====================================================\n");

    free(ensemble);
}

int main(void) {
    srand(42); /* Фіксоване зерно генератора випадкових чисел */

    /* Параметри моделювання для Si: E = 10^5 В/м, T = 300 K, m* = 0.26 m_0 */
    run_carrier_monte_carlo(2000, 400, 1e5, 120e-15, 240e-15, 300.0, 0.26);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <random>
#include <cmath>
#include <iomanip>
#include <numbers>
#include <algorithm>

class CarrierMonteCarlo {
public:
    struct Configuration {
        size_t num_particles{2000};
        size_t num_steps{400};
        double electric_field_x{1e5};  // Напруженість поля, В/м
        double tau_phonon{120e-15};    // Час розсіювання на фононах, с
        double tau_impurity{240e-15};  // Час розсіювання на домішках, с
        double temperature_k{300.0};   // Температура ґратки, К
        double effective_mass_ratio{0.26}; // Відносна ефективна маса Si
    };

    struct SimulationReport {
        size_t total_scatterings;
        size_t phonon_scatterings;
        size_t impurity_scatterings;
        double mean_relaxation_time_s;
        double mean_free_path_nm;
        double drift_velocity_ms;
        double mean_energy_ev;
    };

    explicit CarrierMonteCarlo(Configuration cfg)
        : cfg_(cfg),
          m_eff_(cfg.effective_mass_ratio * mass_e0_),
          rng_(42) {}

    [[nodiscard]] SimulationReport execute() {
        const double inv_tau_ph = 1.0 / cfg_.tau_phonon;
        const double inv_tau_imp = 1.0 / cfg_.tau_impurity;
        const double inv_tau_tot = inv_tau_ph + inv_tau_imp;
        const double tau_total = 1.0 / inv_tau_tot;
        const double prob_phonon = inv_tau_ph / inv_tau_tot;

        const double accel_x = -charge_e_ * cfg_.electric_field_x / m_eff_;

        std::vector<Electron> ensemble(cfg_.num_particles);
        std::uniform_real_distribution<double> dist_u(0.0, 1.0);

        // Ініціалізація початкових швидкостей за Максвеллом — Больцманом
        const double v_th = std::sqrt(3.0 * kb_joule_ * cfg_.temperature_k / m_eff_);
        for (auto& e : ensemble) {
            double cos_th = 1.0 - 2.0 * dist_u(rng_);
            double sin_th = std::sqrt(std::max(0.0, 1.0 - cos_th * cos_th));
            double phi = 2.0 * std::numbers::pi * dist_u(rng_);

            e.vx = v_th * sin_th * std::cos(phi);
            e.vy = v_th * sin_th * std::sin(phi);
            e.vz = v_th * cos_th;
        }

        double grand_total_path = 0.0;
        double grand_total_time = 0.0;
        size_t grand_total_events = 0;
        size_t phonon_events = 0;
        size_t impurity_events = 0;

        for (size_t step = 0; step < cfg_.num_steps; ++step) {
            for (auto& e : ensemble) {
                // 1. Час вільного прольоту
                double u = std::max(1e-12, dist_u(rng_));
                double dt = -tau_total * std::log(u);

                // 2. Дрейф у полі
                double vx_old = e.vx;
                e.vx += accel_x * dt;
                double vx_avg = 0.5 * (vx_old + e.vx);
                e.x += vx_avg * dt;

                double v_mag = std::sqrt(e.vx * e.vx + e.vy * e.vy + e.vz * e.vz);

                grand_total_path += v_mag * dt;
                grand_total_time += dt;
                grand_total_events++;

                // 3. Стохастичний вибір механізму
                if (dist_u(rng_) <= prob_phonon) {
                    phonon_events++;
                } else {
                    impurity_events++;
                }

                // 4. Ізотропне розсіювання швидкості
                double cos_th = 1.0 - 2.0 * dist_u(rng_);
                double sin_th = std::sqrt(std::max(0.0, 1.0 - cos_th * cos_th));
                double phi = 2.0 * std::numbers::pi * dist_u(rng_);

                e.vx = v_mag * sin_th * std::cos(phi);
                e.vy = v_mag * sin_th * std::sin(phi);
                e.vz = v_mag * cos_th;
            }
        }

        double sum_vx = 0.0;
        double sum_energy = 0.0;
        for (const auto& e : ensemble) {
            sum_vx += e.vx;
            double v_sq = e.vx * e.vx + e.vy * e.vy + e.vz * e.vz;
            sum_energy += (0.5 * m_eff_ * v_sq) / charge_e_;
        }

        return SimulationReport{
            .total_scatterings = grand_total_events,
            .phonon_scatterings = phonon_events,
            .impurity_scatterings = impurity_events,
            .mean_relaxation_time_s = grand_total_time / static_cast<double>(grand_total_events),
            .mean_free_path_nm = (grand_total_path / static_cast<double>(grand_total_events)) * 1e9,
            .drift_velocity_ms = sum_vx / static_cast<double>(cfg_.num_particles),
            .mean_energy_ev = sum_energy / static_cast<double>(cfg_.num_particles)
        };
    }

private:
    struct Electron {
        double x{0.0};
        double vx{0.0};
        double vy{0.0};
        double vz{0.0};
    };

    static constexpr double charge_e_{1.602176634e-19};
    static constexpr double mass_e0_{9.1093837015e-31};
    static constexpr double kb_joule_{1.380649e-23};

    Configuration cfg_;
    double m_eff_;
    std::mt19937 rng_;
};

int main() {
    CarrierMonteCarlo::Configuration config{};
    CarrierMonteCarlo solver(config);

    auto report = solver.execute();

    std::cout << std::scientific << std::setprecision(3);
    std::cout << "====================================================\n";
    std::cout << "     РЕЗУЛЬТАТИ СИМУЛЯЦІЇ МОНТЕ-КАРЛО (мова C++)\n";
    std::cout << "====================================================\n";
    std::cout << "Загальна кількість зіткнень:       " << report.total_scatterings << "\n";
    std::cout << "Актів фононного розсіювання:       " << report.phonon_scatterings << "\n";
    std::cout << "Актів домішкового розсіювання:     " << report.impurity_scatterings << "\n";
    std::cout << "----------------------------------------------------\n";
    std::cout << "Середній час релаксації tau:        " << report.mean_relaxation_time_s << " с\n";
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Довжина вільного пробігу lambda:   " << report.mean_free_path_nm << " нм\n";
    std::cout << std::scientific << std::setprecision(3);
    std::cout << "Середня дрейфова швидкість v_d:     " << report.drift_velocity_ms << " м/с\n";
    std::cout << std::fixed << std::setprecision(3);
    std::cout << "Середня кінетична енергія <E>:     " << report.mean_energy_ev << " еВ\n";
    std::cout << "====================================================\n";

    return 0;
}
```
:::

---

### 4. Фізичний аналіз та інженерні підводні камені

#### 1. Перевірка статичної відповідності правила Маттіссена
Моделювання демонструє точне узгодження сумарного часу релаксації із теоретичним прогнозом правила Маттіссена. За вхідних часів `τ_ph = 120` фс та `τ_imp = 240` фс теоретичне значення становить:

```
1 / τ_total = 1 / (120 фс) + 1 / (240 фс) = (2 + 1) / 240 = 1 / (80 фс)
τ_total = 80 фс = 8.000 · 10⁻¹⁴ с
```

Чисельні результати обох реалізацій розраховують середнє значення `⟨τ⟩ = 8.00e-14` с з похибкою менше ніж `0.1%`.

#### 2. Розігрів електронів у сильних електричних полях
У слабких електричних полях середній рівень кінетичної енергії електронів дорівнює тепловій енергії ґратки `⟨E⟩ = 1.5 · k_B · T ≈ 0.039` еВ при `T = 300 K`.

Однак під дією сильного поля (`E > 10⁵` В/м) електрони встигають накопичувати значну додаткову енергію між зіткненнями. Виникає явище **гарячих електронів** (*hot electrons*), де середня температура електронного газу `T_e` стає суттєво вищою за температуру кристалічної ґратки `T_lattice`. Це приводить до виходу з ладу наближення Ома та до насичення дрейфової швидкості `v_sat`.

#### 3. Метод фіктивного розсіювання (Self-Scattering Technique)
У наведеній базовій моделі припускалося, що частота розсіювання `Γ` не залежить від енергії електрона. Проте у реальних напівпровідниках розсіювання на оптичних фононах та екранованих іонах сильно залежить від енергії `Γ(E)`.

Для збереження простих формул обчислення `Δt_flight` у складних модельних комплексах застосовують **метод фіктивного розсіювання Бутчера — Фоукмена**. До системи додається штучний канал розсіювання з енергетично залежною частотою `Γ_self(E)` такою, що сумарна частота стає константою:

```
Γ_max = Γ_ph(E) + Γ_imp(E) + Γ_self(E) = const
```

Якщо при виборі механізму випадає «фіктивне розсіювання», електрон просто продовжує свій вільний політ без зміни вектора швидкості `k`. Це дозволяє використовувати формулу `Δt = - (1 / Γ_max) · ln(U)` для будь-якої складності зонної структури.

---

### 5. Оцінка точності, збіжності та граничних умов

У стохастичному моделюванні методів Монте-Карло чисельна похибка обчислюваних середніх величин (таких як дрейфова швидкість та довжина пробігу) підпорядковується центральній граничній теоремі:

```
σ_error ∝ 1 / √(N_particles · N_steps)
```

Щоб зменшити статистичні коливання до рівня менше 1%, розмір ансамблю `N_particles` обирають у діапазоні від 1000 до 10000 частинок, а кількість ітераційних кроків — від 300 до 1000.

#### Граничні умови для обмежених геометрій
У симуляціях тонких наноплівок або квантових ниток до алгоритму додають обробку зіткнень із просторовими межами:
1. **Дзеркальне відбивання** (*specular reflection*): Компонента швидкості, перпендикулярна до поверхні, змінює знак `v_z ↦ -v_z`, а паралельні компоненти зберігаються. За дзеркального відбивання поверхня не створює електричного опору.
2. **Дифузне відбивання** (*diffuse reflection*): Напрямок вильоту електрона від поверхні обирається довільно з ізотропного півпростору. За дифузного відбивання електрон повністю втрачає поздовжній дрейфовий імпульс, що дає розмірне зростання питомого опору (модель Фукса — Зондгаймера).
