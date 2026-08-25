# ⚙️ Алгоритм Метрополіса та чисельне моделювання моделі Ізінга

Оскільки точні аналітичні розрахунки двовимірних спінових решіток у зовнішньому магнітному полі є математично неможливими, а тривимірна модель Ізінга належить до класу NP-важких задач і не має закритого аналітичного розв'язку, основним інструментом дослідження реальних фазових переходів є комп'ютерне моделювання.

Простір станів двовимірної ґратки розміром `L × L` містить `2^N` мікростанів (де `N = L²`). Для скромного розміру `L = 100` кількість можливих конфігурацій становить `2^10000 ≈ 10^3010`, що перевищує кількість атомів у спостережуваному Всесвіті. Пряме підсумовування статистичної суми `Z = sum_μ exp(-β · E_μ)` є обчислювально нездійсненним.

Розв'язанням цієї проблеми є використання **методу Монте-Карло за ланцюгами Маркова (Markov Chain Monte Carlo, MCMC)**, а саме алгоритму Метрополіса — Гастінгса та кластерних алгоритмів Вульфа.

---

### 1. Фізична та алгоритмічна ідея Метрополіса

Замість рівномірного випадкового вибору конфігурацій (яке б у переважній більшості генерувало високоенергетичні парамагнітні стани з нульовою статистичною вагою), алгоритм Метрополіса генерує послідовність станів із ймовірністю, строго пропорційною їхній канонічній вазі Больцмана:

```
P(μ) = (1 / Z) · exp(-β · E_μ)                                    [ймовірність стану Больцмана]
```

Для забезпечення збіжності ланцюга Маркова до стану термодинамічної рівноваги перехідні ймовірності `W(μ → ν)` мусять задовольняти **умову детального балансу**:

```
P(μ) · W(μ → ν) = P(ν) · W(ν → μ)                                  [умова детального балансу]
```

Переписавши це співвідношення для відношення ймовірностей переходу:

```
W(μ → ν) / W(ν → μ) = P(ν) / P(μ) = exp(-β · ΔE)                  [відношення ймовірностей переходу]
```

де `ΔE = E_ν - E_μ` — зміна повної енергії системи при спробі перевороту одного спіна `σ_{i,j} → -σ_{i,j}`.

Умову детального балансу задовольняє **ймовірність прийняття спроби Метрополіса**:

```
A(μ → ν) = min( 1, exp(-β · ΔE) )                                  [ймовірність прийняття Метрополіса]
```

---

### 2. Оптимізація обчислення ΔE та Lookup-таблиці

При перевороті одного спіна `σ_{i,j}` не потрібно перераховувати повну енергію всієї ґратки (`O(N)` операцій). Зміна енергії залежить виключно від поточного значення спіна та суми його 4 найближчих сусідів `S_neighbors = sum_nn σ_nn`:

```
ΔE = 2J · σ_{i,j} · sum_nn σ_nn + 2h · σ_{i,j}                    [зміна енергії при перевороті спіна]
```

У нульовому зовнішньому полі (`h = 0`) сума 4 найближчих сусідів на квадратній ґратці може набувати лише 5 значень: `S_neighbors ∈ {-4, -2, 0, +2, +4}`. Отже, зміна енергії `ΔE` належить дискретній множині `{-8J, -4J, 0, +4J, +8J}`.

Це дозволяє заздалегідь перед початком симуляції обчислити експоненти `exp(-β · ΔE)` у вигляді масиву із 5 елементів. Завдяки цьому обчислювально дорога функція `exp()` викликується нуль разів у внутрішньому циклі симуляції, скорочуючи час виконання у 8–10 разів.

#### Вибір початкових умов та релаксація
Симуляцію можна починати з двох типів початкових умов:
1. **Гарячий старт (Hot start):** Спіни ініціалізуються повністю випадково з ймовірністю 50% (+1 або -1). Це відповідає стану нескінченно високої температури (`T → ∞`).
2. **Холодний старт (Cold start):** Усі спіни ініціалізуються паралельно у стані +1. Це відповідає нулеві температури (`T = 0 K`).

Для виходу системи у стан термодинамічної рівноваги проводиться етап прогріву (**burn-in phase**), який зазвичай становить від 10 000 до 50 000 пасів Метрополіса (`Monte Carlo Sweeps`). Один пасс відповідає `N = L²` спробам перевороту спінів.

---

### 3. Термодинамічні спостережувані величини та флуктуації

Під час моделювання обчислюються такі ключові фізичні характеристики:

1. **Середня енергія на спін `<e>`:**
   ```
   <e> = <E> / N                                                   [середня енергія на вузол]
   ```

2. **Середня абсолютна намагніченість `<|m|>`:**
   Оскільки у скінченній ґратці без зовнішнього поля середня намагніченість `<m>` через флуктуації на великих часових інтервалах прямує до нуля, параметром порядку слугує модуль намагніченості:
   ```
   <|m|> = < | sum_i σ_i | > / N                                   [середній модуль намагніченості]
   ```

3. **Питома теплоємність `C_v` через флуктуаційну теорему:**
   Замість чисельного диференціювання енергії за температурою, теплоємність обчислюється через дисперсію флуктуацій повної енергії:
   ```
   C_v = ( <E²> - <E>² ) / (N · k_B · T²)                           [флуктуаційна формула теплоємності]
   ```

4. **Магнітна сприйнятливість `χ` через флуктуації намагніченості:**
   ```
   χ = ( <M²> - <|M|>² ) · N / (k_B · T)                            [флуктуаційна формула сприйнятливості]
   ```

---

### 4. Реалізація C та C++

Нижче наведено паралельні реалізації алгоритму Метрополіса для 2D моделі Ізінга мовами C та C++.

:::tabs
@tab C (C99)
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#define L 64
#define N (L * L)

/* Оптимізована структура симуляції з таблицею експонент */
typedef struct {
    int spins[L][L];
    double exp_table[5]; /* Lookup table для exp(-beta * dE) */
    double J;
    double T;
    double beta;
    long long total_energy;
    long long total_magnetization;
} IsingSim;

/* Таблиця для шквал-індексування періодичних межевих умов (тор) */
static int p_next[L];
static int p_prev[L];

void ising_init(IsingSim *sim, double J, double T) {
    sim->J = J;
    sim->T = T;
    sim->beta = 1.0 / T;
    sim->total_energy = 0;
    sim->total_magnetization = 0;

    /* Ініціалізація граничних умов */
    for (int i = 0; i < L; i++) {
        p_next[i] = (i + 1) % L;
        p_prev[i] = (i - 1 + L) % L;
    }

    /* Таблиця експонент для dE = -8J, -4J, 0, 4J, 8J */
    /* Індекси таблиці: (dE / 4J) + 2 */
    for (int k = -2; k <= 2; k++) {
        double dE = 4.0 * J * k;
        sim->exp_table[k + 2] = (dE <= 0) ? 1.0 : exp(-sim->beta * dE);
    }

    /* Початковий гарячий/випадковий стан спінів */
    for (int r = 0; r < L; r++) {
        for (int c = 0; c < L; c++) {
            sim->spins[r][c] = (rand() % 2 == 0) ? 1 : -1;
            sim->total_magnetization += sim->spins[r][c];
        }
    }

    /* Початковий розрахунок повної енергії */
    long long E = 0;
    for (int r = 0; r < L; r++) {
        for (int c = 0; c < L; c++) {
            int s = sim->spins[r][c];
            int sum_nn = sim->spins[p_next[r]][c] + sim->spins[r][p_next[c]];
            E -= J * s * sum_nn;
        }
    }
    sim->total_energy = E;
}

/* Один крок Метрополіса (спроба перевороту одного спіна) */
void ising_metropolis_step(IsingSim *sim) {
    int r = rand() % L;
    int c = rand() % L;
    int s = sim->spins[r][c];

    int sum_neighbors = sim->spins[p_next[r]][c] + sim->spins[p_prev[r]][c] +
                        sim->spins[r][p_next[c]] + sim->spins[r][p_prev[c]];

    int dE = 2 * sim->J * s * sum_neighbors;

    /* Прийняття за таблицею Метрополіса */
    int lookup_idx = (dE / (2 * (int)sim->J)) / 2 + 2;
    double prob = sim->exp_table[lookup_idx];

    double r_val = (double)rand() / RAND_MAX;
    if (r_val < prob) {
        sim->spins[r][c] = -s;
        sim->total_energy += dE;
        sim->total_magnetization += (-2 * s);
    }
}

/* Один пасс (Monte Carlo Sweep) = N спроб Метрополіса */
void ising_sweep(IsingSim *sim) {
    for (int i = 0; i < N; i++) {
        ising_metropolis_step(sim);
    }
}

int main(void) {
    srand((unsigned int)time(NULL));
    IsingSim sim;

    double T_crit = 2.269;
    ising_init(&sim, 1.0, T_crit);

    /* Прогрів (Thermalization burn-in) */
    for (int i = 0; i < 10000; i++) {
        ising_sweep(&sim);
    }

    /* Накопичення статистики */
    double sum_m = 0.0;
    double sum_m2 = 0.0;
    int num_samples = 5000;

    for (int s = 0; s < num_samples; s++) {
        ising_sweep(&sim);
        double m_abs = fabs((double)sim.total_magnetization / N);
        sum_m += m_abs;
        sum_m2 += m_abs * m_abs;
    }

    double avg_m = sum_m / num_samples;
    double avg_m2 = sum_m2 / num_samples;
    double chi = (avg_m2 - avg_m * avg_m) * N / sim.T;

    printf("2D Ising Model (L=%d, T=%.3f)\n", L, sim.T);
    printf("Magnetization <|m|>: %.4f\n", avg_m);
    printf("Susceptibility chi:  %.4f\n", chi);

    return 0;
}
```

@tab C++ (C++17/C++20)
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <array>
#include <numeric>
#include <iomanip>

class IsingSimulation {
public:
    IsingSimulation(std::size_t lattice_size, double J_coupling, double temperature)
        : L_(lattice_size), N_(lattice_size * lattice_size), J_(J_coupling), T_(temperature),
          beta_(1.0 / temperature), rng_(std::random_device{}()), dist_unif_(0.0, 1.0),
          dist_grid_(0, lattice_size - 1), spins_(N_, 1) {
        
        precompute_lookup_table();
        initialize_lattice();
    }

    void run_sweep() {
        for (std::size_t i = 0; i < N_; ++i) {
            std::size_t r = dist_grid_(rng_);
            std::size_t c = dist_grid_(rng_);
            
            int s = spin_at(r, c);
            int sum_nn = spin_at(prev(r), c) + spin_at(next(r), c) +
                         spin_at(r, prev(c)) + spin_at(r, next(c));
            
            int dE = 2 * static_cast<int>(J_) * s * sum_nn;
            int idx = (dE / 4) + 2;

            if (dE <= 0 || dist_unif_(rng_) < exp_table_[idx]) {
                set_spin_at(r, c, -s);
                total_energy_ += dE;
                total_magnetization_ += (-2 * s);
            }
        }
    }

    [[nodiscard]] double mean_magnetization() const noexcept {
        return std::abs(static_cast<double>(total_magnetization_)) / static_cast<double>(N_);
    }

    [[nodiscard]] double mean_energy() const noexcept {
        return static_cast<double>(total_energy_) / static_cast<double>(N_);
    }

private:
    std::size_t L_;
    std::size_t N_;
    double J_;
    double T_;
    double beta_;

    std::mt19937 rng_;
    std::uniform_real_distribution<double> dist_unif_;
    std::uniform_int_distribution<std::size_t> dist_grid_;

    std::vector<int> spins_;
    std::array<double, 5> exp_table_{};
    long long total_energy_{0};
    long long total_magnetization_{0};

    [[nodiscard]] inline std::size_t next(std::size_t idx) const noexcept {
        return (idx + 1 == L_) ? 0 : idx + 1;
    }

    [[nodiscard]] inline std::size_t prev(std::size_t idx) const noexcept {
        return (idx == 0) ? L_ - 1 : idx - 1;
    }

    [[nodiscard]] inline int spin_at(std::size_t r, std::size_t c) const noexcept {
        return spins_[r * L_ + c];
    }

    inline void set_spin_at(std::size_t r, std::size_t c, int val) noexcept {
        spins_[r * L_ + c] = val;
    }

    void precompute_lookup_table() {
        for (int k = -2; k <= 2; ++k) {
            double dE = 4.0 * J_ * k;
            exp_table_[k + 2] = (dE <= 0) ? 1.0 : std::exp(-beta_ * dE);
        }
    }

    void initialize_lattice() {
        std::bernoulli_distribution dist_spin(0.5);
        total_magnetization_ = 0;

        for (std::size_t r = 0; r < L_; ++r) {
            for (std::size_t c = 0; c < L_; ++c) {
                int val = dist_spin(rng_) ? 1 : -1;
                set_spin_at(r, c, val);
                total_magnetization_ += val;
            }
        }

        total_energy_ = 0;
        for (std::size_t r = 0; r < L_; ++r) {
            for (std::size_t c = 0; c < L_; ++c) {
                int s = spin_at(r, c);
                int sum_nn = spin_at(next(r), c) + spin_at(r, next(c));
                total_energy_ -= static_cast<long long>(J_) * s * sum_nn;
            }
        }
    }
};

int main() {
    constexpr std::size_t lattice_size = 64;
    constexpr double temp_crit = 2.269185;

    IsingSimulation sim(lattice_size, 1.0, temp_crit);

    // Thermalization phase (burn-in)
    constexpr std::size_t burn_in_sweeps = 10'000;
    for (std::size_t i = 0; i < burn_in_sweeps; ++i) {
        sim.run_sweep();
    }

    // Production measurement phase
    constexpr std::size_t sample_sweeps = 5'000;
    double sum_m = 0.0;
    double sum_m2 = 0.0;

    for (std::size_t s = 0; s < sample_sweeps; ++s) {
        sim.run_sweep();
        double m = sim.mean_magnetization();
        sum_m += m;
        sum_m2 += m * m;
    }

    double avg_m = sum_m / sample_sweeps;
    double avg_m2 = sum_m2 / sample_sweeps;
    double susceptibility = (avg_m2 - avg_m * avg_m) * (lattice_size * lattice_size) / temp_crit;

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "=== 2D Ising Model Simulation (C++17) ===\n";
    std::cout << "Lattice Size: " << lattice_size << "x" << lattice_size << "\n";
    std::cout << "Temperature T: " << temp_crit << "\n";
    std::cout << "Mean Magnetization <|m|>: " << avg_m << "\n";
    std::cout << "Magnetic Susceptibility:   " << susceptibility << "\n";

    return 0;
}
```
:::

---

### 5. Аналіз автокореляції та оцінка статистичних похибок

У Монте-Карло симуляціях послідовні вимірювання не є статистично незалежними: стан системи у кроці `t + 1` сильно корелює зі станом у кроці `t`. Автокореляційна функція фізичної величини `A` описується виразом:

```
χ_auto(τ) = < ( A(t) - <A> ) · ( A(t + τ) - <A> ) > / < ( A - <A> )² >  [автокореляційна функція]
```

Автокореляційний час `τ_int` визначає кількість пасів, необхідних для отримання одного незалежного вимірювання:

```
τ_int = 1/2 + sum_{τ=1}^∞ χ_auto(τ)                                 [інтегральний час автокореляції]
```

Справжня похибка середнього значення з урахуванням автокореляції перевищує стандартну похибку у `sqrt(2 · τ_int)` разів:

```
σ_true = σ_naive · sqrt( 2 · τ_int / N_samples )                   [коректна похибка симуляції]
```

---

### 6. Критичне сповільнення та кластерний алгоритм Вульфа

Поблизу критичної точки `T → T_c` звичайний односпіновий алгоритм Метрополіса стикається з фізичним явищем **критичного сповільнення (critical slowing down)**. 

Радіус кореляції спінів прямує до нескінченності (`ξ ~ |T - T_c|^(-ν)`), утворюючи гігантські корельовані кластери однакового знака. Час автокореляції симуляції зростає за степеневим законом:

```
τ_corr ~ ξ^z ~ L^z                                                [критичне сповільнення]
```

де `z ≈ 2.16` — динамічний критичний індекс для локальних алгоритмів Метрополіса. Моделювання великих решіток у зоні переходу вимагає мільйонів послідовних пасів для генерації бодай одного статистично незалежного стану.

Для подолання критичного сповільнення Удо Вульф (Udo Wolff) та Свендсен — Ванг розробили **кластерний алгоритм Вульфа**. Замість перевороту поодиноких спінів алгоритм Вульфа будує та повертає цілий взаємопов'язаний кластер спінів за один крок:

1. Випадково обирається початковий спін-зеренце `(r, c)`.
2. Для кожного з його 4 найближчих паралельних сусідів додавання до кластера відбувається з ймовірністю підключення:
   ```
   P_add = 1 - exp(-2 · β · J)                                    [ймовірність підключення до кластера Вульфа]
   ```
3. Процес рекурсивно розростається на сусідів доданих спінів.
4. Весь побудований кластер інвертується як єдине ціле (`σ_i → -σ_i`).

Завдяки нелокальному перевороту великих блоків динамічний критичний індекс алгоритму Вульфа падає майже до нуля (`z_Wolff ≈ 0.25`), що дозволяє проводити вимірювання поблизу `T_c` на два порядки швидше.
