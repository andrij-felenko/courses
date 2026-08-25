# ⚙️ Моделювання двопідґраткового антиферомагнетика: алгоритм Монте-Карло та обчислення намагніченості підґраток

Ця вставка містить покроковий аналіз, математичне обґрунтування та практичну програмну реалізацію чисельного моделювання двопідґраткового антиферомагнетика методом Монте-Карло (алгоритм Метрополіса — Гастінгса) для двовимірної квадратної кристалічної ґратки.

---

### 1. Фізична модель та метод Монте-Карло у статистичній фізиці

У статистичній механіці точне аналітичне обчислення статистичної суми `Z` для багаточастинкових квантових або класичних магнітних систем із числом частинок `N ~ 10³–10⁶` є математично неможливим через комбінаторний вибух кількості можливих мікростанів (`2^N` для моделей зі спіном 1/2). 

Метод Монте-Карло розв'язує цю проблему шляхом статистичного вибору найбільш ймовірних мікростанів із ансамблю Канонічного розподілу Гіббса. Замість повного перебору всіх можливих конфігурацій спінової системи алгоритм будує марковський ланцюг стан-за-станом, імовірність появи якого строго пропорційна фактору Гіббса `exp(-E / (k_B · T))`.

#### А. Модель Ізінга на двопідґратковій ґратці
Розглядається двовимірна квадратна ґратка розміром `L × L` (із загальною кількістю вузлів `N_spins = L²`) та періодичними межовими умовами (топологія тора). 

Кристалічна ґратка розділяється на дві рівноцінні геометричні підґратки `A` та `B` за принципом шахівниці:
- Вузол `(i, j)` належить підґратці `A`, якщо сума індексів `(i + j)` є парною.
- Вузол `(i, j)` належить підґратці `B`, якщо сума індексів `(i + j)` є непарною.

Кожен вузол містить класичний спін `S[i, j] ∈ {-1, +1}`, спрямований вздовж легкої осі анізотропії. 

Гамільтоніан взаємодії найближчих сусідів за наявності зовнішнього магнітного поля `H` має вигляд:

```
H_ham = -J · ∑_[i, j] (S_i · S_j) - H · ∑_i (S_i)
```

де `J` — константа обмінної взаємодії між найближчими сусідами. 

Для **антиферомагнетика** константа є від'ємною (`J < 0`). Це означає, що енергетично найвигіднішою є конфігурація з протилежно орієнтованими спінами сусідніх вузлів (`S_i · S_j = -1`), що дає внесок у потенціальну енергію `-J · (-1) = -|J|`. Паралельні спіни сусідів підвищують енергію системи на `+|J|`.

#### Б. Алгоритм Метрополіса та умова детального балансу
Для побудови стаціонарного гіббсівського розподілу ймовірностей `P(S)` зміна конфігурації спінів повинна задовольняти **умові детального балансу** (*detailed balance*):

```
P(A) · W(A → B) = P(B) · W(B → A)
```

де `P(A) = (1 / Z) · exp(-E_A / (k_B · T))` — ймовірність перебування системи в стані `A`, а `W(A → B)` — ймовірність переходу зі стану `A` в стан `B`.

Відношення ймовірностей переходу дорівнює:

```
W(A → B) / W(B → A) = P(B) / P(A) = exp(-(E_B - E_A) / (k_B · T)) = exp(-ΔE / (k_B · T))
```

В алгоритмі Метрополіса ймовірність прийняття нового стану `W(A → B)` обирається у вигляді:

```
W(A → B) = min( 1, exp(-ΔE / (k_B · T)) )
```

Це означає наступне правило:
1. Якщо перевертання спіна зменшує енергію системи (`ΔE ≤ 0`), такий перехід виконується **беззастережно** (з ймовірністю 1.0).
2. Якщо перевертання спіна збільшує енергію системи (`ΔE > 0`), перехід приймається з ймовірністю `p = exp(-ΔE / (k_B · T))`. Для цього генерується випадкове число `r ∈ [0, 1)`. Якщо `r < p`, спін перевертається; інакше стан системи залишається незмінним.

---

### 2. Локальний розрахунок зміни енергії (ΔE)

Ключовим моментом інженерної оптимізації алгоритму Монте-Карло є те, що при спробі перевертання одного спіна `S[r, c]` немає потреби перераховувати повну енергію всієї кристалічної ґратки. Достатньо обчислити локальну зміну енергії `ΔE` взаємодії даного спіна з його чотирма найближчими сусідами.

Сума спінів чотирьох найближчих сусідів для вузла `(r, c)` із урахуванням періодичних межових умов:

```
S_neighbors = S[(r-1+L)%L, c] + S[(r+1)%L, c] + S[r, (c-1+L)%L] + S[r, (c+1)%L]
```

Початкова енергія взаємодії даного спіна `S[r, c]` із оточенням:

```
E_initial = -J · S[r, c] · S_neighbors - H · S[r, c]
```

Після спроби перевертання спін змінює знак: `S_new = -S[r, c]`. Нова енергія:

```
E_final = -J · (-S[r, c]) · S_neighbors - H · (-S[r, c])
```

Різниця енергій `ΔE = E_final - E_initial`:

```
ΔE = 2 · S[r, c] · (J · S_neighbors + H)
```

Завдяки цій формулі обчислення переходу одного спіна виконується за сталий час `O(1)` незалежно від загального розміру ґратки `L`. Один повний прохід Монте-Карло (**Monte Carlo Sweep**, MCS) складається з `N_spins = L²` спроб перевертання випадкових спінів.

---

### 3. Макроскопічні величини та підґратковий аналіз

Для відстеження термодинамічного стану та виявлення фазового переходу 2-го роду при температурі Нееля програма обчислює чотири ключові макроскопічні характеристики:

1. **Намагніченість підґратки A:**
   ```
   M_A = (2 / L²) · ∑_{(i, j) ∈ A} S[i, j]
   ```
2. **Намагніченість підґратки B:**
   ```
   M_B = (2 / L²) · ∑_{(i, j) ∈ B} S[i, j]
   ```
3. **Шахматна (стігерд) намагніченість (Staggered Magnetization):**
   Основний параметр порядку для антиферомагнетика, який вимірює ступінь антипаралельної впорядкованості підґраток:
   ```
   M_staggered = |M_A - M_B| / 2
   ```
   При `T → 0 K` значення `M_staggered → 1.0`. При `T ≥ T_N` значення `M_staggered → 0.0`.
4. **Сумарна спонтанна намагніченість:**
   ```
   M_net = | ∑_{(i, j)} S[i, j] | / L²
   ```
   Для антиферомагнетика у нульовому зовнішньому полі (`H = 0`) сумарна намагніченість `M_net` повинна залишатися близькою до нуля при будь-яких температурах.

---

### 4. Практична програмна реалізація: C та C++

Нижче наведено повний робочий код чисельного моделювання мовами C (стандарт C99) та C++ (стандарт C++20), оформлений у вигляді порівняльних вкладок.

:::tabs
```c
/* Simulation of 2D Antiferromagnetic Ising Model using Metropolis Monte Carlo (C99) */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#define L 40
#define N_SPINS (L * L)
#define MC_SWEEPS 5000
#define THERM_SWEEPS 1000

typedef struct {
    int spins[L][L];
    double J; /* J < 0 for antiferromagnetism */
    double H;
    double T;
} Simulation;

/* Initialize lattice into exact antiferromagnetic ground state (Checkerboard) */
void init_checkerboard(Simulation *sim) {
    for (int i = 0; i < L; i++) {
        for (int j = 0; j < L; j++) {
            if ((i + j) % 2 == 0) {
                sim->spins[i][j] = 1;  /* Sublattice A */
            } else {
                sim->spins[i][j] = -1; /* Sublattice B */
            }
        }
    }
}

/* Generate uniformly distributed random double in range [0, 1) */
double get_random_double() {
    return (double)rand() / ((double)RAND_MAX + 1.0);
}

/* Calculate dE for flipping spin at row r, column c */
double calculate_site_energy_change(const Simulation *sim, int r, int c) {
    int s = sim->spins[r][c];
    int top    = sim->spins[(r - 1 + L) % L][c];
    int bottom = sim->spins[(r + 1) % L][c];
    int left   = sim->spins[r][(c - 1 + L) % L];
    int right  = sim->spins[r][(c + 1) % L];
    
    int neighbor_sum = top + bottom + left + right;
    
    /* dE = 2 * s * (J * sum_neighbors + H) */
    return 2.0 * s * (sim->J * neighbor_sum + sim->H);
}

/* Execute one Monte Carlo Sweep (N_SPINS flip attempts) */
void monte_carlo_sweep(Simulation *sim) {
    for (int step = 0; step < N_SPINS; step++) {
        int r = rand() % L;
        int c = rand() % L;
        
        double dE = calculate_site_energy_change(sim, r, c);
        
        if (dE <= 0.0 || get_random_double() < exp(-dE / sim->T)) {
            sim->spins[r][c] = -sim->spins[r][c];
        }
    }
}

/* Compute sublattices and net magnetizations */
void compute_magnetizations(const Simulation *sim, double *m_a, double *m_b, double *m_stag, double *m_net) {
    double sum_a = 0.0;
    double sum_b = 0.0;
    
    for (int i = 0; i < L; i++) {
        for (int j = 0; j < L; j++) {
            if ((i + j) % 2 == 0) {
                sum_a += sim->spins[i][j];
            } else {
                sum_b += sim->spins[i][j];
            }
        }
    }
    
    *m_a = sum_a / (N_SPINS / 2.0);
    *m_b = sum_b / (N_SPINS / 2.0);
    *m_stag = fabs(*m_a - *m_b) / 2.0;
    *m_net = fabs(sum_a + sum_b) / (double)N_SPINS;
}

int main(void) {
    srand((unsigned int)time(NULL));
    Simulation sim;
    sim.J = -1.0; /* Antiferromagnetic exchange coupling */
    sim.H = 0.0;  /* Zero external field */
    
    printf("Temp\tM_A\tM_B\tM_staggered\tM_net\n");
    printf("---------------------------------------------------\n");
    
    for (double T = 0.4; T <= 4.0; T += 0.2) {
        sim.T = T;
        init_checkerboard(&sim);
        
        /* Thermalization phase (erase transient initial memory) */
        for (int s = 0; s < THERM_SWEEPS; s++) {
            monte_carlo_sweep(&sim);
        }
        
        /* Measurement phase */
        double avg_ma = 0.0, avg_mb = 0.0, avg_mstag = 0.0, avg_mnet = 0.0;
        for (int s = 0; s < MC_SWEEPS; s++) {
            monte_carlo_sweep(&sim);
            double ma, mb, mstag, mnet;
            compute_magnetizations(&sim, &ma, &mb, &mstag, &mnet);
            avg_ma += ma;
            avg_mb += mb;
            avg_mstag += mstag;
            avg_mnet += mnet;
        }
        
        avg_ma /= MC_SWEEPS;
        avg_mb /= MC_SWEEPS;
        avg_mstag /= MC_SWEEPS;
        avg_mnet /= MC_SWEEPS;
        
        printf("%.2f\t%.3f\t%.3f\t%.3f\t\t%.3f\n", T, avg_ma, avg_mb, avg_mstag, avg_mnet);
    }
    
    return 0;
}
```
```cpp
// Simulation of 2D Antiferromagnetic Ising Model using Modern C++20
#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <iomanip>
#include <numeric>

class AntiferromagneticIsing2D {
public:
    struct MagnetizationResult {
        double m_a;
        double m_b;
        double m_staggered;
        double m_net;
    };

    AntiferromagneticIsing2D(std::size_t size, double coupling_J, double ext_field)
        : L_(size), N_spins_(size * size), J_(coupling_J), H_(ext_field),
          spins_(size, std::vector<int>(size, 1)), rng_(1337)
    {
        init_checkerboard();
    }

    void set_temperature(double T) noexcept { temperature_ = T; }

    void init_checkerboard() {
        for (std::size_t i = 0; i < L_; ++i) {
            for (std::size_t j = 0; j < L_; ++j) {
                spins_[i][j] = ((i + j) % 2 == 0) ? 1 : -1;
            }
        }
    }

    void monte_carlo_sweep() {
        std::uniform_int_distribution<std::size_t> dist_coord(0, L_ - 1);
        std::uniform_real_distribution<double> dist_prob(0.0, 1.0);

        for (std::size_t step = 0; step < N_spins_; ++step) {
            std::size_t r = dist_coord(rng_);
            std::size_t c = dist_coord(rng_);

            int s = spins_[r][c];
            int top    = spins_[(r + L_ - 1) % L_][c];
            int bottom = spins_[(r + 1) % L_][c];
            int left   = spins_[r][(c + L_ - 1) % L_];
            int right  = spins_[r][(c + 1) % L_];

            int neighbor_sum = top + bottom + left + right;
            double dE = 2.0 * s * (J_ * neighbor_sum + H_);

            if (dE <= 0.0 || dist_prob(rng_) < std::exp(-dE / temperature_)) {
                spins_[r][c] = -s;
            }
        }
    }

    [[nodiscard]] MagnetizationResult measure() const noexcept {
        double sum_a = 0.0;
        double sum_b = 0.0;

        for (std::size_t i = 0; i < L_; ++i) {
            for (std::size_t j = 0; j < L_; ++j) {
                if ((i + j) % 2 == 0) {
                    sum_a += spins_[i][j];
                } else {
                    sum_b += spins_[i][j];
                }
            }
        }

        double m_a = sum_a / (N_spins_ / 2.0);
        double m_b = sum_b / (N_spins_ / 2.0);
        return {
            .m_a = m_a,
            .m_b = m_b,
            .m_staggered = std::abs(m_a - m_b) / 2.0,
            .m_net = std::abs(sum_a + sum_b) / static_cast<double>(N_spins_)
        };
    }

private:
    std::size_t L_;
    std::size_t N_spins_;
    double J_;
    double H_;
    double temperature_{1.0};
    std::vector<std::vector<int>> spins_;
    mutable std::mt19937 rng_;
};

int main() {
    constexpr std::size_t L = 40;
    constexpr double J = -1.0; // Antiferromagnetic coupling (J < 0)
    constexpr double H = 0.0;
    constexpr int therm_sweeps = 1000;
    constexpr int mc_sweeps = 5000;

    AntiferromagneticIsing2D model(L, J, H);

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "Temp\tM_A\tM_B\tM_staggered\tM_net\n";
    std::cout << "---------------------------------------------------\n";

    for (double T = 0.4; T <= 4.0; T += 0.2) {
        model.set_temperature(T);
        model.init_checkerboard();

        // Thermalization sweeps
        for (int s = 0; s < therm_sweeps; ++s) {
            model.monte_carlo_sweep();
        }

        // Sampling sweeps
        double acc_ma = 0.0, acc_mb = 0.0, acc_mstag = 0.0, acc_mnet = 0.0;
        for (int s = 0; s < mc_sweeps; ++s) {
            model.monte_carlo_sweep();
            auto res = model.measure();
            acc_ma += res.m_a;
            acc_mb += res.m_b;
            acc_mstag += res.m_staggered;
            acc_mnet += res.m_net;
        }

        std::cout << T << "\t"
                  << (acc_ma / mc_sweeps) << "\t"
                  << (acc_mb / mc_sweeps) << "\t"
                  << (acc_mstag / mc_sweeps) << "\t\t"
                  << (acc_mnet / mc_sweeps) << "\n";
    }

    return 0;
}
```
:::

---

### 5. Фізичний аналіз результатів та пастки обчислень

#### А. Аналіз температурної залежності та точки Онзагера
При виконанні програми отримуються наступні термодинамічні характеристики:
- **При низьких температурах (`T / |J| < 1.0`):** Шахматна намагніченість дорівнює `M_staggered ≈ 1.0`, що свідчить про ідеальний антиферомагнітний порядок. Значення `M_A ≈ +1.0` та `M_B ≈ -1.0`. Сумарна намагніченість `M_net ≈ 0.0`.
- **Наближення до точки Нееля (`T ≈ T_N`):** Флуктуації спінів різко зростають. Шахматна намагніченість спадає до нуля. 

Для двовимірної квадратної моделі Ізінга точний аналітичний розв'язок Ларса Онзагера дає критичну температуру:

```
T_N / |J| = 2 / ln(1 + √2) ≈ 2.269185
```

Програма чітко фіксує падіння `M_staggered` до нуля саме поблизу точки `T ≈ 2.27`.

#### Б. Інженерні та обчислювальні пастки

1. **Ефект скінченних розмірів (Finite Size Effect):**
   У чисельному експерименті на ґратці `40 × 40` критичні флуктуації обмежені розміром системного контейнера. У безпосередній близькості від критичної точки `T_N` параметр порядку `M_staggered` не обнуляється строго скачком, а має розмитий "хвіст" через скінченність `L`. Для точного обчислення критичних індексів застосовують метод скінченно-розмірного скейлінгу (*Finite Size Scaling*) із порівнянням розрахунків для `L = 16, 32, 64, 128`.

2. **Критичне сповільнення (Critical Slowing Down):**
   Поблизу критичної точки `T_N` час кореляції між послідовними станами Монте-Карло зростає як `τ ∝ L^z` (де `z ≈ 2.17` для стандартного алгоритму Метрополіса). Це означає, що послідовні знімки ґратки стають сильно корельованими. Для подолання критичного сповільнення у професійних фізичних пакетах використовують кластерні алгоритми Свендсена — Ванга або Вольфа.

3. **Фазове виродження та фліп усієї підґратки:**
   Оскільки у нульовому полі стани зі спинами `(A:↑, B:↓)` та `(A:↓, B:↑)` мають абсолютно однакову енергію, при високих температурах поблизу `T_N` система може флуктуювати між цими двома станами. Саме тому у формулі шахматної намагніченості береться модуль різниці `|M_A - M_B| / 2`, що запобігає штучному обнуленню усреднених за часом значень підґраток.
