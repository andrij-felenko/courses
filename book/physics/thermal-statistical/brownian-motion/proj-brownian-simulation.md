# ⚙️ Симуляція броунівського руху: алгоритм Ейлера—Маруями та обчислення MSD

Чисельне моделювання броунівського руху дає змогу відтворити реалістичні траєкторії частинок у двовимірному та тривимірному просторах, розрахувати статистичний середній квадрат зсуву (MSD) та експериментально дослідити перехід між короткотривалим балістичним польотом і довготривалим дифузійним блуканням. У цій вставці описано математичну дискретизацію стохастичного рівняння Ланжевена за схемою Ейлера—Маруями, наведено детальний аналіз стійкості алгоритму та наведено готові ідіоматичні реалізації мовами C та C++.

### 1. Фізична постановка та дискретизація (схема Ейлера—Маруями)

Рівняння Ланжевена описує динаміку броунівської частинки під дією двох сил — макроскопічного в'язкого гальмування та мікроскопічних хаотичних ударів молекул середовища. У двовимірній площині (2D) система диференціальних рівнянь другого порядку розкладається на пару зв'язаних рівнянь для швидкостей `v_x, v_y` та координат `x, y`:

```
m · (dv_x / dt) = − γ · v_x + ξ_x(t)
m · (dv_y / dt) = − γ · v_y + ξ_y(t)

dx / dt = v_x
dy / dt = v_y
```

де `m` — маса частинки, `γ = 6 · π · η · a` — коефіцієнт тертя Стокса, а `ξ_x(t), ξ_y(t)` — незалежні компоненти гаусового білого шуму з кореляцією `<ξ_i(t) ξ_j(t')> = 2 γ k_B T δ_ij δ(t − t')`.

Для чисельного розв'язання цієї стохастичної системи ми застосовуємо дискретизацію за схемою Ейлера—Маруями (*Euler–Maruyama scheme*). Стохастичний інтеграл від білого шуму за маленький інтервал часу `Δt` дає Вінерівський приріст `ΔW = N(0, 1) · √(Δt)`, де `N(0, 1)` — стандартна нормальна випадкова величина з нульовим математичним сподіванням та дисперсією `1.0`.

Дискретні формули оновлення швидкості та позиції на кожен крок `n → n + 1`:

```
v_x[n+1] = v_x[n] · (1 − (γ / m) · Δt) + (√(2 · γ · k_B · T · Δt) / m) · N_x(0, 1)
v_y[n+1] = v_y[n] · (1 − (γ / m) · Δt) + (√(2 · γ · k_B · T · Δt) / m) · N_y(0, 1)

x[n+1] = x[n] + v_x[n+1] · Δt
y[n+1] = y[n] + v_y[n+1] · Δt
```

Ключовим фактором точності симуляції є вибір кроку за часом `Δt`. Оскільки імпульс частинки релаксує за характерний час `τ_p = m / γ`, чисельна схема буде стійкою лише за умови `Δt < 2 m / γ`. Якщо обрати `Δt >> τ_p`, інерційні доданки розбігатимуться, і симуляція «вибухне». Для довгих проміжків часу без інтересу до балістики застосовують перевизначену (overdamped) схему Ейлера, де швидкість не інтегрується, а крок за координатою розраховується безпосередньо як `Δx = √(2 D Δt) · N(0, 1)`.

![Динаміка зсуву та режими блукання](img/langevin-regimes.svg)
*Прикрокова дискретизація точного рівняння Ланжевена відтворює балістичний режим на коротких часах (t << τ_p) та класичний дифузійний нахил на довгих часах.*

---

### 2. Алгоритм обчислення ансамблевого MSD

Середній квадрат зсуву (*Mean Squared Displacement*, MSD) для ансамблю з `N_trials` частинок обчислюється шляхом симуляції незалежних траєкторій. Для кожної частинки `k` відстежується зміщення від її початкової точки `(x_k(0), y_k(0))`:

```
MSD(t_n) = (1 / N_trials) · ∑ₖ₌₁ⁿᵗʳⁱᵃˡˢ [ (x_k(t_n) − x_k(0))² + (y_k(t_n) − y_k(0))² ]
```

У двовимірному просторі теоретичний зв'язок між коефіцієнтом дифузії та MSD задається формулою `MSD(t) = 4 · D · t`. Звідси оцінка коефіцієнта дифузії за результатами моделювання обчислюється за нахилом кривої на довгих часах: `D_est = MSD(t_max) / (4 · t_max)`.

---

### 3. Реалізації моделі мовами C та C++

Нижче наведено робочі реалізації симулятора та розрахунку MSD. Приклади написані так, щоб показати відмінності у підходах між низькорівневим C (пряме управління пам'яттю, перетворення Бокса—Мюллера) та сучасним C++ (RAII, шаблони, контейнери `std::vector` та бібліотека `<random>`).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Фізичні параметри системи */
typedef struct {
    double temp;      /* Температура, К (напр. 300.0) */
    double gamma;     /* Коефіцієнт в'язкого тертя, кг/с */
    double mass;      /* Маса частинки, кг */
    double dt;        /* Крок симуляції за часом, с */
    size_t num_steps; /* Кількість кроків у траєкторії */
    size_t num_trials;/* Кількість частинок в ансамблі */
} SimulationParams;

/* Результати аналізу MSD */
typedef struct {
    double *time_array;
    double *msd_array;
    double estimated_D;
    size_t num_steps;
} SimulationResult;

/* Генератор випадкових чисел Ґаусса (перетворення Бокса—Мюллера) */
static double generate_gaussian(void) {
    double u1 = (double)rand() / (double)RAND_MAX;
    double u2 = (double)rand() / (double)RAND_MAX;
    if (u1 < 1e-12) u1 = 1e-12;
    return sqrt(-2.0 * log(u1)) * cos(2.0 * M_PI * u2);
}

/* Вільна пам'ять для результатів */
void free_simulation_result(SimulationResult *res) {
    if (res) {
        free(res->time_array);
        free(res->msd_array);
        res->time_array = NULL;
        res->msd_array = NULL;
    }
}

/* Симуляція ансамблю частинок та розрахунок MSD */
int run_brownian_simulation(const SimulationParams *p, SimulationResult *res) {
    const double kB = 1.380649e-23; /* Стала Больцмана, Дж/К */
    const double noise_amp = sqrt(2.0 * p->gamma * kB * p->temp * p->dt) / p->mass;
    const double damping = 1.0 - (p->gamma / p->mass) * p->dt;

    res->num_steps = p->num_steps;
    res->time_array = (double *)calloc(p->num_steps, sizeof(double));
    res->msd_array = (double *)calloc(p->num_steps, sizeof(double));

    if (!res->time_array || !res->msd_array) {
        free_simulation_result(res);
        return -1;
    }

    for (size_t i = 0; i < p->num_steps; ++i) {
        res->time_array[i] = (double)i * p->dt;
    }

    /* Накопичення квадрата зсуву по ансамблю */
    for (size_t trial = 0; trial < p->num_trials; ++trial) {
        double x = 0.0, y = 0.0;
        /* Початкова теплова швидкість v ~ N(0, sqrt(kB T / m)) */
        double v_scale = sqrt(kB * p->temp / p->mass);
        double vx = generate_gaussian() * v_scale;
        double vy = generate_gaussian() * v_scale;

        res->msd_array[0] += (x * x + y * y);

        for (size_t step = 1; step < p->num_steps; ++step) {
            vx = vx * damping + noise_amp * generate_gaussian();
            vy = vy * damping + noise_amp * generate_gaussian();

            x += vx * p->dt;
            y += vy * p->dt;

            res->msd_array[step] += (x * x + y * y);
        }
    }

    /* Усереднення по ансамблю */
    for (size_t step = 0; step < p->num_steps; ++step) {
        res->msd_array[step] /= (double)p->num_trials;
    }

    /* Оцінка коефіцієнта дифузії в 2D: D = MSD / (4 * t) на лінійній ділянці */
    size_t last_idx = p->num_steps - 1;
    if (res->time_array[last_idx] > 0.0) {
        res->estimated_D = res->msd_array[last_idx] / (4.0 * res->time_array[last_idx]);
    } else {
        res->estimated_D = 0.0;
    }

    return 0;
}

int main(void) {
    srand((unsigned int)time(NULL));

    SimulationParams params = {
        .temp = 300.0,
        .gamma = 1e-8,
        .mass = 1e-14,
        .dt = 1e-7,
        .num_steps = 1000,
        .num_trials = 500
    };

    SimulationResult result = {0};
    if (run_brownian_simulation(&params, &result) == 0) {
        double theory_D = (1.380649e-23 * params.temp) / params.gamma;
        printf("Теоретичний D = %.4e м²/с\n", theory_D);
        printf("Оцінений D    = %.4e м²/с\n", result.estimated_D);
        printf("MSD на кроці 100 (t = %.2e с): %.4e м²\n",
               result.time_array[100], result.msd_array[100]);
        printf("MSD на кроці 999 (t = %.2e с): %.4e м²\n",
               result.time_array[999], result.msd_array[999]);
        free_simulation_result(&result);
    } else {
        fprintf(stderr, "Помилка виділення пам'яті під час симуляції\n");
        return 1;
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <random>
#include <cmath>
#include <numbers>
#include <stdexcept>

struct SimulationConfig {
    double temp{300.0};       // Температура, К
    double gamma{1e-8};       // Коефіцієнт тертя, кг/с
    double mass{1e-14};       // Маса частинки, кг
    double dt{1e-7};          // Крок за часом, с
    std::size_t steps{1000};  // Довжина траєкторії
    std::size_t trials{500};  // Кількість частинок в ансамблі
};

struct SimulationResult {
    std::vector<double> time;
    std::vector<double> msd;
    double estimated_diffusion_coeff{0.0};
    double theoretical_diffusion_coeff{0.0};
};

class BrownianSimulator {
public:
    explicit BrownianSimulator(SimulationConfig config)
        : config_(config), rd_(), gen_(rd_()) {}

    SimulationResult run() {
        if (config_.dt <= 0.0 || config_.steps == 0 || config_.trials == 0) {
            throw std::invalid_argument("Некоректні параметри симуляції");
        }

        constexpr double kB = 1.380649e-23;
        const double noise_scale = std::sqrt(2.0 * config_.gamma * kB * config_.temp * config_.dt) / config_.mass;
        const double damping = 1.0 - (config_.gamma / config_.mass) * config_.dt;
        const double v_thermal = std::sqrt(kB * config_.temp / config_.mass);

        SimulationResult res;
        res.time.resize(config_.steps);
        res.msd.assign(config_.steps, 0.0);
        res.theoretical_diffusion_coeff = (kB * config_.temp) / config_.gamma;

        for (std::size_t i = 0; i < config_.steps; ++i) {
            res.time[i] = static_cast<double>(i) * config_.dt;
        }

        std::normal_distribution<double> dist_norm(0.0, 1.0);

        for (std::size_t trial = 0; trial < config_.trials; ++trial) {
            double x = 0.0;
            double y = 0.0;
            double vx = dist_norm(gen_) * v_thermal;
            double vy = dist_norm(gen_) * v_thermal;

            res.msd[0] += (x * x + y * y);

            for (std::size_t step = 1; step < config_.steps; ++step) {
                vx = vx * damping + noise_scale * dist_norm(gen_);
                vy = vy * damping + noise_scale * dist_norm(gen_);

                x += vx * config_.dt;
                y += vy * config_.dt;

                res.msd[step] += (x * x + y * y);
            }
        }

        for (auto &val : res.msd) {
            val /= static_cast<double>(config_.trials);
        }

        const std::size_t last = config_.steps - 1;
        if (res.time[last] > 0.0) {
            // У 2D просторі: MSD = 4 * D * t
            res.estimated_diffusion_coeff = res.msd[last] / (4.0 * res.time[last]);
        }

        return res;
    }

private:
    SimulationConfig config_;
    std::random_device rd_;
    std::mt19937 gen_;
};

int main() {
    try {
        SimulationConfig cfg{
            .temp = 300.0,
            .gamma = 1e-8,
            .mass = 1e-14,
            .dt = 1e-7,
            .steps = 1000,
            .trials = 500
        };

        BrownianSimulator simulator(cfg);
        auto result = simulator.run();

        std::cout << "Теоретичний D = " << result.theoretical_diffusion_coeff << " м²/с\n";
        std::cout << "Оцінений D    = " << result.estimated_diffusion_coeff << " м²/с\n";
        std::cout << "MSD на фініші (t = " << result.time.back() << " с): " 
                  << result.msd.back() << " м²\n";
    } catch (const std::exception &e) {
        std::cerr << "Помилка симуляції: " << e.what() << '\n';
        return 1;
    }

    return 0;
}
```
:::

---

### 4. Часове (TA-MSD) проти ансамблевого (EA-MSD) усереднення

У комп'ютерному моделюванні та реальному мікроскопічному експерименті існують два фундаментальні шляхи обчислення середнього квадрата зсуву:

1. **Ансамблеве усереднення (Ensemble-Averaged MSD, EA-MSD):**
   Вимагає одночасної наявності великої кількості `N` незалежних траєкторій частинок. Для кожної часової мітки `t` обчислюється розкид координат відносного початкового стану `t = 0`. Цей метод ідеально підходить для комп'ютерного моделювання, де легко створити тисячі частинок.

2. **Часове усереднення уздовж однієї траєкторії (Time-Averaged MSD, TA-MSD):**
   У реальних дослідах із мікроскопом часто вдається відстежити лише **один** довгоживучий флуоресцентний трек частинки тривалістю `T`. Тоді для кожного часового лагу `Δ` розраховується ковзаюче середнє уздовж всієї траєкторії:

```
δ²(Δ; T) = (1 / (T − Δ)) · ∫₀ᵀ⁻Δ [ r(t + Δ) − r(t) ]² dt
```

Дискретний аналог для сітки з `N` кроків:

```
δ²(m · Δt) = (1 / (N − m)) · ∑ₖ₌₀ᴺ⁻ᵐ⁻¹ [ (x[k + m] − x[k])² + (y[k + m] − y[k])² ]
```

Для класичного броунівського руху виконується **ергодична гіпотеза**: при `T → ∞` часове усереднення для однієї траєкторії `δ²(Δ; T)` повністю збігається з ансамблевим усередненням `<r²(Δ)>`. Проте при наявності субдифузії у пористому середовищі або неергодичних процесів (наприклад, у гелях) ергодичність порушується (`δ²(Δ) ≠ <r²(Δ)>`), що є важливою діагностичною ознакою у біофізиці.

---

### 5. Практичні пастки, чисельні обмеження та векторна оптимізація

При моделюванні стохастичних диференціальних рівнянь розробники часто припустиються типових помилок, які викривляють статистику:

1. **Неправильний дільник у залежності MSD від просторової розмірності:**
   - 1D простір: `<Δx²(t)> = 2 · D · t` (дільник `2`).
   - 2D простір: `<Δr²(t)> = 4 · D · t` (дільник `4`).
   - 3D простір: `<Δr²(t)> = 6 · D · t` (дільник `6`).
   Плутанина коефіцієнтів розрахунку призводить до систематичної помилки на 33–50%.

2. **Статистична похибка генераторів випадкових чисел:** стандартний генератор `rand()` у мові C має малий період та некорельованість на коротких вибірках. У високоточних розрахунках слід використовувати алгоритм «Мерсеннів вихор» (`std::mt19937` у C++) або криптографічно стійкі генератори.

3. **Стійкість за часовим кроком `Δt`:** якщо чисельний крок `Δt` підбирається близьким до згасання `m / γ`, у неявній схемі Ейлера виникають нефізичні осциляції швидкості. У такому випадку рекомендовано зменшувати крок або переходити на схему Мільштейна чи вищого порядку Рунге—Кутти для СДР.

4. **Апаратно-векторна прискореність (SIMD та OpenMP):** оскільки кроки інтегрування частинок не залежать один від одного, розрахунок легко прискорити на високопродуктивних серверах за допомогою директив OpenMP `#pragma omp parallel for` або використання векторних інструкцій AVX-512 для одночасної генерації 8 випадкових чисел Ґаусса.

Опис повного програмного інтерфейсу та виробничих C/C++ бібліотек подано у вставці [Інтерфейс бібліотеки симуляції](book:physics/brownian-motion/api-simulation-lib.md).

[step] += (x * x + y * y);
            }
        }

        for (auto &val : res.msd) {
            val /= static_cast<double>(config_.trials);
        }

        const std::size_t last = config_.steps - 1;
        if (res.time[last] > 0.0) {
            // У 2D просторі: MSD = 4 * D * t
            res.estimated_diffusion_coeff = res.msd[last] / (4.0 * res.time[last]);
        }

        return res;
    }

private:
    SimulationConfig config_;
    std::random_device rd_;
    std::mt19937 gen_;
};

int main() {
    try {
        SimulationConfig cfg{
            .temp = 300.0,
            .gamma = 1e-8,
            .mass = 1e-14,
            .dt = 1e-7,
            .steps = 1000,
            .trials = 500
        };

        BrownianSimulator simulator(cfg);
        auto result = simulator.run();

        std::cout << "Теоретичний D = " << result.theoretical_diffusion_coeff << " м²/с\n";
        std::cout << "Оцінений D    = " << result.estimated_diffusion_coeff << " м²/с\n";
        std::cout << "MSD на фініші (t = " << result.time.back() << " с): " 
                  << result.msd.back() << " м²\n";
    } catch (const std::exception &e) {
        std::cerr << "Помилка симуляції: " << e.what() << '\n';
        return 1;
    }

    return 0;
}
```
:::

### Пастки та рекомендації щодо обчислень

1. **Вибір часового кроку `Δt`:** якщо `Δt > m / γ`, чисельна схема Ейлера виходить за межі стійкості і «вибухає». Для стійкості обов'язково має виконуватися умова `Δt < 2 m / γ`.
2. **Розмірність простору:** у 1D просторі `MSD = 2 D t`, у 2D — `MSD = 4 D t`, у 3D — `MSD = 6 D t`. Не плутайте дільник при визначенні коефіцієнта дифузії!
3. **Статистичний шум:** для гладкої кривої MSD потрібен ансамбль із щонайменше 500–1000 незалежних частинок, або застосування часового усереднення (*Time-Averaged MSD*) уздовж однієї довгої траєкторії.

Опис повного програмного інтерфейсу та API бібліотеки аналізу подано у вставці [Інтерфейс бібліотеки симуляції](book:physics/brownian-motion/api-simulation-lib.md).
