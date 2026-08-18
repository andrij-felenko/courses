# ⚙️ Чисельна симуляція фазового переходу в 2D моделі Ізінга

Ця вставка містить практичну реалізацію чисельного алгоритму Монте-Карло (алгоритм Метрополіса) для симуляції двовимірної моделі Ізінга на квадратній ґратці, що дозволяє чисельно спостерігати магнітний фазовий перехід, обчислити точну температуру Кюрі `T_C` та виміряти флуктуаційні піки магнітної сприйнятливості й теплоємності.

---

### 1. Опис фізичної моделі та алгоритму Метрополіса

Модель Ізінга описує систему дискретних спінів `σ[i,j] = ±1`, розташованих у вузлах двовимірної квадратної ґратки розміром `L × L` з періодичними межовими умовами (тороїдальна топологія ґратки). Періодичні умови усувають крайові поверхневі ефекти, роблячи кожен вузол ґратки фізично еквівалентним та усуваючи граничні розриви.

Гамільтоніан системи за наявності зовнішнього магнітного поля `B_ext` описується взаємодією найближчих сусідів та зеєманівським вкладом зовнішнього поля:

```
H = -J · ∑ [⟨(i,j),(k,l)⟩] σ[i,j] · σ[k,l] - g · μ_B · B_ext · ∑ [i,j] σ[i,j]
```

де сумування `⟨(i,j),(k,l)⟩` проводиться за всіма унікальними парами найближчих сусідів (кожен вузол має 4 сусіди у двовимірній квадратній ґратці), а `J > 0` — константа обмінної взаємодії.

Для 2D моделі Ізінга за відсутності зовнішнього поля (`B_ext = 0`) Ларс Онсагер у 1944 році вивів точне аналітичне значення критичної температури Кюрі в термодинамічній границі (`L → ∞`):

```
k_B · T_C / J = 2 / ln(1 + √2) ≈ 2.269185
```

#### Алгоритм Метрополіса (Марковські ланцюги Монте-Карло):
Алгоритм Метрополіса генерує послідовність спінових конфігурацій, які утворюють ланцюг Маркова. Він гарантує виконання умови детального балансу (*detailed balance*):

```
W(μ → ν) · P_eq(μ) = W(ν → μ) · P_eq(ν)
```

де `P_eq(μ) ∝ exp(-E(μ) / (k_B·T))` — больцманівська ймовірність стану `μ`. Це забезпечує асимптотичну збіжність системи до точного термодинамічного ансамблю Больцмана за заданої температури `T`.

#### Покрокова послідовність дій алгоритму Метрополіса:
1. **Вибір випадкового вузла:** Випадковим чином вибираються координати вузла ґратки `(r, c)`.
2. **Обчислення ΔE:** Зміна енергії системи при спробі перевороту спіна `σ[r,c] → -σ[r,c]` дорівнює:
   `ΔE = 2 · s · ( J · (σ[r+1,c] + σ[r-1,c] + σ[r,c+1] + σ[r,c-1]) + g · μ_B · B_ext )`
   Оскільки кожен спін має 4 сусіди із значеннями `±1`, сума найближчих сусідів може набувати лише 5 дискретних значений: `{-4, -2, 0, +2, +4}`. 
3. **Критерій прийняття рішення Метрополіса:**
   - Якщо `ΔE ≤ 0`, переворот зменшує або не змінює енергію системи — новий стан безумовно приймається (`P = 1.0`).
   - Якщо `ΔE > 0`, переворот енергетично невигідний і приймається з ймовірністю Больцмана `P = exp(-ΔE / (k_B · T))`. Для цього генерується випадкове дійсне число `r_val ∈ [0, 1)`. Якщо `r_val < P`, спін перевертається; інакше стан ґратки залишається незмінним.
4. **Крок Монте-Карло (MCS):** Один крок Монте-Карло (1 MCS) визначається як проведення `N = L × L` спроб перевороту спінів. Це відповідає статистичному оновленню кожного спіна ґратки в середньому один раз.

---

### 2. Оптимізація та організація обчислень

Оскільки трансцендентна функція `exp()` є відносно повільною при мільйонах викликів на кожній ітерації, у програмах реалізовано табличну оптимізацію (Lookup Table). Для заданої температури `T` значення больцманівських множників для позитивних змін енергії `ΔE = +4J` та `ΔE = +8J` обчислюються заздалегідь один раз на початку вимірювального циклу.

Крім того, вимірювання статистичних величин проводиться лише після фази **термалізації** (виходу системи на термодинамічну рівновагу протягом 3000 MCS), що дозволяє уникнути впливу початкового хаотичного стану.

Магнітна сприйнятливість `χ` та ізобарна теплоємність `C_p` обчислюються через флуктуаційні дисперсії відповідних величин за термодинамічними формулами флуктуаційно-дисипаційної теореми:

```
χ = (N / (k_B · T)) · ( ⟨M²⟩ - ⟨|M|⟩² )
C_p = (N / (k_B · T²)) · ( ⟨E²⟩ - ⟨E⟩² )
```

---

### 3. Реалізація чисельного розрахунку мовами C та C++

:::tabs
```c
/*
 * ising_2d.c — Моделювання 2D моделі Ізінга методом Монте-Карло (C99)
 * Обчислює намагніченість <|M|>, сприйнятливість chi та теплоємність Cp.
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#define L 32              /* Розмір квадратної ґратки L x L */
#define N (L * L)         /* Загальна кількість спінів */
#define J_EXCHANGE 1.0    /* Константа обмінної взаємодії */

/* Таблиця заздалегідь обчислених ймовірностей Больцмана для прискорення */
static double exp_table[9];

/* Періодичні межові умови */
static inline int pbc(int coord) {
    if (coord < 0) return coord + L;
    if (coord >= L) return coord - L;
    return coord;
}

/* Ініціалізація таблиці експонент для даної температури T */
static void init_boltzmann_table(double temp) {
    /* ΔE може бути +4J або +8J для ΔE > 0 */
    exp_table[4] = exp(-4.0 * J_EXCHANGE / temp);
    exp_table[8] = exp(-8.0 * J_EXCHANGE / temp);
}

/* Ініціалізація спінів у випадковий гарячий стан (T -> inf) */
static void init_spins_random(int spin[L][L]) {
    for (int r = 0; r < L; r++) {
        for (int c = 0; c < L; c++) {
            spin[r][c] = (rand() % 2 == 0) ? 1 : -1;
        }
    }
}

/* Повна енергія системи */
static double calc_total_energy(const int spin[L][L]) {
    double energy = 0.0;
    for (int r = 0; r < L; r++) {
        for (int c = 0; c < L; c++) {
            int s = spin[r][c];
            int sum_neighbors = spin[pbc(r + 1)][c] + spin[r][pbc(c + 1)];
            energy -= J_EXCHANGE * s * sum_neighbors;
        }
    }
    return energy;
}

/* Загальна намагніченість ґратки */
static double calc_total_magnetization(const int spin[L][L]) {
    int sum = 0;
    for (int r = 0; r < L; r++) {
        for (int c = 0; c < L; c++) {
            sum += spin[r][c];
        }
    }
    return (double)sum;
}

/* Один крок Монте-Карло (MCS) — N спроб перевороту */
static void monte_carlo_step(int spin[L][L], double temp) {
    for (int step = 0; step < N; step++) {
        int r = rand() % L;
        int c = rand() % L;
        int s = spin[r][c];
        
        int sum_neighbors = spin[pbc(r - 1)][c] + spin[pbc(r + 1)][c] +
                            spin[r][pbc(c - 1)] + spin[r][pbc(c + 1)];
        int dE = 2 * J_EXCHANGE * s * sum_neighbors;

        if (dE <= 0) {
            spin[r][c] = -s;
        } else {
            double p = exp_table[dE];
            double r_val = (double)rand() / (RAND_MAX + 1.0);
            if (r_val < p) {
                spin[r][c] = -s;
            }
        }
    }
}

int main(void) {
    srand((unsigned int)time(NULL));
    int spin[L][L];

    printf("===============================================================\n");
    printf(" 2D Ising Monte Carlo Simulation (C99)\n");
    printf(" Grid: %dx%d (%d spins)\n", L, L, N);
    printf(" Theoretical Curie Temp Tc = %.5f J/kB\n", 2.0 / log(1.0 + sqrt(2.0)));
    printf("===============================================================\n\n");
    printf("  Temp(T) |   <|M|>   |  Chi (Susc)  |   Cp (Heat)  | Notes\n");
    printf("---------------------------------------------------------------\n");

    for (double T = 1.2; T <= 3.41; T += 0.1) {
        init_spins_random(spin);
        init_boltzmann_table(T);

        /* 1. Термалізація (вивід у рівноважний стан) — 3000 MCS */
        for (int mcs = 0; mcs < 3000; mcs++) {
            monte_carlo_step(spin, T);
        }

        /* 2. Збір термодинамічних статистик — 3000 MCS */
        double sum_m = 0.0, sum_m2 = 0.0;
        double sum_e = 0.0, sum_e2 = 0.0;
        int samples = 3000;

        for (int mcs = 0; mcs < samples; mcs++) {
            monte_carlo_step(spin, T);
            
            double m_val = fabs(calc_total_magnetization(spin)) / N;
            double e_val = calc_total_energy(spin) / N;

            sum_m += m_val;
            sum_m2 += m_val * m_val;
            sum_e += e_val;
            sum_e2 += e_val * e_val;
        }

        double avg_m = sum_m / samples;
        double avg_m2 = sum_m2 / samples;
        double avg_e = sum_e / samples;
        double avg_e2 = sum_e2 / samples;

        /* Сприйнятливість chi = N/T * (<M^2> - <|M|>^2) */
        double chi = (N / T) * (avg_m2 - avg_m * avg_m);

        /* Теплоємність Cp = N/T^2 * (<E^2> - <E>^2) */
        double cp = (N / (T * T)) * (avg_e2 - avg_e * avg_e);

        const char* note = (fabs(T - 2.27) < 0.05) ? "<-- Critical Curie Point Tc" : "";
        printf("  %6.2f  |  %8.4f |  %11.4f |  %11.4f | %s\n", T, avg_m, chi, cp, note);
    }

    return 0;
}
```
```cpp
/*
 * ising_2d.cpp — Об'єктно-орієнтована високопродуктивна симуляція (C++17)
 * Використовує std::vector, швидкий випадковий генератор std::mt19937_64 та RAII.
 */

#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <iomanip>
#include <cstdint>
#include <array>

class IsingLattice2D {
private:
    int L_;
    int N_;
    double J_;
    std::vector<int8_t> spin_;
    std::mt19937_64 rng_;
    std::uniform_real_distribution<double> dist_real_{0.0, 1.0};
    std::uniform_int_distribution<int> dist_coord_;
    std::array<double, 9> boltzmann_lut_{};

    [[nodiscard]] inline int pbc(int coord) const noexcept {
        if (coord < 0) return coord + L_;
        if (coord >= L_) return coord - L_;
        return coord;
    }

    [[nodiscard]] inline int idx(int r, int c) const noexcept {
        return r * L_ + c;
    }

public:
    explicit IsingLattice2D(int L, double J = 1.0)
        : L_(L), N_(L * L), J_(J), spin_(L * L),
          rng_(std::random_device{}()), dist_coord_(0, L - 1) {
        randomize();
    }

    void randomize() {
        std::uniform_int_distribution<int> dist_spin(0, 1);
        for (int i = 0; i < N_; ++i) {
            spin_[i] = dist_spin(rng_) ? 1 : -1;
        }
    }

    void set_temperature(double T) noexcept {
        // Заповнення таблиці Больцмана для dE = 2 * J * s * sum (dE може бути 4 або 8)
        boltzmann_lut_[4] = std::exp(-4.0 * J_ / T);
        boltzmann_lut_[8] = std::exp(-8.0 * J_ / T);
    }

    void monte_carlo_step() noexcept {
        for (int i = 0; i < N_; ++i) {
            int r = dist_coord_(rng_);
            int c = dist_coord_(rng_);
            int s = spin_[idx(r, c)];

            int sum_neighbors = spin_[idx(pbc(r - 1), c)] +
                                spin_[idx(pbc(r + 1), c)] +
                                spin_[idx(r, pbc(c - 1))] +
                                spin_[idx(r, pbc(c + 1))];
            int dE = 2 * s * sum_neighbors;

            if (dE <= 0 || dist_real_(rng_) < boltzmann_lut_[dE]) {
                spin_[idx(r, c)] = static_cast<int8_t>(-s);
            }
        }
    }

    [[nodiscard]] double total_magnetization() const noexcept {
        int64_t sum = 0;
        for (int i = 0; i < N_; ++i) {
            sum += spin_[i];
        }
        return static_cast<double>(sum);
    }

    [[nodiscard]] double total_energy() const noexcept {
        double energy = 0.0;
        for (int r = 0; r < L_; ++r) {
            for (int c = 0; c < L_; ++c) {
                int s = spin_[idx(r, c)];
                int sum_neighbors = spin_[idx(pbc(r + 1), c)] + spin_[idx(r, pbc(c + 1))];
                energy -= J_ * s * sum_neighbors;
            }
        }
        return energy;
    }

    [[nodiscard]] int size() const noexcept { return N_; }
};

struct ThermodynamicStats {
    double avg_m;
    double susceptibility;
    double heat_capacity;
};

ThermodynamicStats run_temperature_point(IsingLattice2D& lattice, double T, int thermal_mcs, int sample_mcs) {
    lattice.randomize();
    lattice.set_temperature(T);

    // 1. Термалізація
    for (int mcs = 0; mcs < thermal_mcs; ++mcs) {
        lattice.monte_carlo_step();
    }

    // 2. Збір статистичних даних
    double sum_m = 0.0, sum_m2 = 0.0;
    double sum_e = 0.0, sum_e2 = 0.0;
    const double n_spins = static_cast<double>(lattice.size());

    for (int mcs = 0; mcs < sample_mcs; ++mcs) {
        lattice.monte_carlo_step();

        double m_val = std::abs(lattice.total_magnetization()) / n_spins;
        double e_val = lattice.total_energy() / n_spins;

        sum_m += m_val;
        sum_m2 += m_val * m_val;
        sum_e += e_val;
        sum_e2 += e_val * e_val;
    }

    double avg_m = sum_m / sample_mcs;
    double avg_m2 = sum_m2 / sample_mcs;
    double avg_e = sum_e / sample_mcs;
    double avg_e2 = sum_e2 / sample_mcs;

    double chi = (n_spins / T) * (avg_m2 - avg_m * avg_m);
    double cp = (n_spins / (T * T)) * (avg_e2 - avg_e * avg_e);

    return {avg_m, chi, cp};
}

int main() {
    constexpr int grid_l = 32;
    IsingLattice2D lattice(grid_l);

    std::cout << "===============================================================\n"
              << " 2D Ising Monte Carlo Simulation (Modern C++17)\n"
              << " Lattice: " << grid_l << "x" << grid_l << " (" << lattice.size() << " spins)\n"
              << " Analytical Tc = " << 2.0 / std::log(1.0 + std::sqrt(2.0)) << " J/kB\n"
              << "===============================================================\n\n";

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "  Temp(T) |   <|M|>   |  Chi (Susc)  |   Cp (Heat)  | Notes\n";
    std::cout << "---------------------------------------------------------------\n";

    for (double T = 1.2; T <= 3.41; T += 0.1) {
        auto [m, chi, cp] = run_temperature_point(lattice, T, 3000, 3000);

        std::cout << "  " << std::setw(6) << T << "  |  "
                  << std::setw(8) << m << " |  "
                  << std::setw(11) << chi << " |  "
                  << std::setw(11) << cp << " | ";

        if (std::abs(T - 2.27) < 0.05) {
            std::cout << "<-- Critical Curie Point Tc";
        }
        std::cout << "\n";
    }

    return 0;
}
```
:::

---

### 4. Аналіз чисельних результатів та особливості архітектури коду

#### 1. Особливості представлення даних у пам'яті:
У версії на C++17 двовимірну ґратку розгорнуто у одновимірний послідовний вектор `std::vector<int8_t>`. Використання 8-бітного цілочисельного типу `int8_t` замість 32-бітного `int` дозволяє зменшити об'єм кеш-пам'яті L1 у чотири рази. Це забезпечує ідеальну локальність даних у кеші процессора та запобігає кріпацтву пам'яті (Cache misses) при багаторазовому вибірці сусідніх спінів.

#### 2. Характерні фізичні ознаки фазового переходу в чисельному виводі:
- **Низькотемпературна фаза (`T < 2.0`):** Середня безрозмірна намагніченість `<|M|>` близька до `1.0`. Система перебуває в повністю впорядкованому феромагнітному стані. Флуктуації малі, тому магнітна сприйнятливість `χ` та теплоємність `C_p` мають невеликі значення.
- **Високотемпературна фаза (`T > 2.6`):** Намагніченість спадає до малих значень `<|M|> ~ 0.1` (падіння до нуля обмежується скінченним розміром ґратки). Система перебуває в парамагнітному стані.
- **Критична область (`T ≈ 2.27`):** У районі аналітичної точки Кюрі `T_C ≈ 2.269 J/k_B` спостерігається різкий перегин намагніченості, а також гострі **флуктуаційні піки магнітної сприйнятливості `χ` та теплоємності `C_p`**.

#### 3. Масштабування скінченних розмірів (Finite-Size Scaling):
У чисельному експерименті на ґратці `32 × 32` фазовий перехід розмитий і не утворює математичної нескінченності. Для визначення точки Кюрі в нескінченному кристалі (`L → ∞`) фізики моделюють серію ґраток `L = 16, 32, 64, 128`, знаходять положення максимуму сприйнятливості `T_C(L)` та будують екстраполяцію за законом:

```
T_C(L) = T_C(∞) + A · L^(-1/ν)
```

де `ν = 1.0` — критичний індекс радіуса кореляції для двовимірної моделі Ізінга.

#### 4. Критичне сповільнення (Critical Slowing Down) та кластерні алгоритми:
Поблизу `T_C` час кореляції між спіновими конфігураціями `τ_corr` розбігається як `τ_corr ∝ ξ^z` (де `z ≈ 2.16` для локального алгоритму Метрополіса). Односпінові перевороти Метрополіса стають неефективними, бо великі кластери спінів оновлюються вкрай повільно. Для усунення цього ефекту використовують **кластерні алгоритми Вольфа** (*Wolff algorithm*) або **Свендсена — Ванга** (*Swendsen-Wang*), які перевертають цілі зв'язані кластери спінів за один крок, зменшуючи динамічний критичний індекс до `z ≈ 0.2`.

#### 5. Інструкція з компіляції та оптимізації прапорами компілятора:
Для прискорення виконання симуляцій Монте-Карло рекомендується використовувати високі рівні оптимізації компілятора:

```bash
# Компіляція версії на C99:
gcc -O3 -march=native -flto -std=c99 ising_2d.c -lm -o ising_c

# Компіляція версії на C++17:
g++ -O3 -march=native -flto -std=c++17 ising_2d.cpp -o ising_cpp
```

Прапор `-O3 -march=native` дозволяє компілятору автовекторизувати внутрішні цикли та оптимально використати кеш-пам'ять процесора, що прискорює симуляцію у 3–5 разів.
