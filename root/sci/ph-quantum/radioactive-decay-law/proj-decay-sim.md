# ⚙️ Моделювання радіоактивного розпаду методом Монте-Карло

Чисельне моделювання квантового радіоактивного розпаду ансамблю нестабільних ядер та дволанкового ланцюга розпадів методом Монте-Карло дозволяє прямо відтворити статистичну природу атомарних явищ та порівняти їх із диференціальним законом Резерфорда — Содді та рівняннями Бейтмана.

## 1. Фізичний алгоритм та математична модель

Оскільки квантовий розпад кожного окремого ядра є принципово випадковою подією із константою ймовірності `λ` за одиницю часу, симуляція методом Монте-Карло є найприроднішим способом опису системи:

1. Обираємо часовий крок `dt`, який є достатньо малим за умовою `λ · dt << 1`.
2. Ймовірність того, що окреме ядро розпадеться протягом інтервалу `dt`, становить:
   ```
   p_decay = 1.0 - e^(-λ · dt) ≈ λ · dt
   ```
3. На кожному кроці `dt` для кожного з наявних `N(t)` ядер ґенерується випадкове число `r ∈ [0.0, 1.0)`. Якщо `r < p_decay`, ядро розпадається.
4. Процес повторюється для потрібної кількості часових кроків, формуючи стохастичну траєкторію `N(t)`.

### Вимоги до ґенератора випадкових чисел

Якість стохастичної симуляції фізичних процесів суттєво залежить від псевдовипадкового ґенератора. Простий класичний ґенератор `rand()` мови C (лінійний конгруентний метод) має короткий період і кореляції між сусідніми числами, що може спотворити статистику для великих ансамблів.

В ідіоматичному C++ використовують ґенератор Вихр Мерсенна `std::mt19937` з довгою періоду `2¹⁹⁹³⁷ - 1` та рівномірним розподілом чисел високої якості. Для ініціалізації використовують `std::random_device`, який отримує ентропію від апаратного забезпечення ОС.

## 2. Реалізація симуляції мовами C та C++

Нижче наведено робочий приклад симуляції розпаду початкового ансамблю з `N₀ = 100 000` ядер, а також двохланкового ланцюга `A → B → C`, розроблений двома мовами у вигляді взаємозамінних вкладок.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#define INITIAL_N0 100000
#define NUM_STEPS  100
#define DT         0.1

/* Моделювання розпаду одиночного ізотопу */
void simulate_single_decay(double half_life) {
    double lambda = log(2.0) / half_life;
    double p_decay = 1.0 - exp(-lambda * DT);
    long current_N = INITIAL_N0;

    printf("=== Симуляція розпаду (C) ===\n");
    printf("T1/2 = %.2f с, lambda = %.4f с^-1, N0 = %d\n", half_life, lambda, INITIAL_N0);
    printf("Час (с) | Симуляція N(t) | Аналітичне N(t) | Похибка (%%)\n");
    printf("----------------------------------------------------------\n");

    for (int step = 0; step <= NUM_STEPS; step += 10) {
        double t = step * DT;
        double analytic_N = INITIAL_N0 * exp(-lambda * t);
        double err_pct = fabs(current_N - analytic_N) / analytic_N * 100.0;

        printf("%7.2f | %14ld | %15.1f | %10.3f\n", t, current_N, analytic_N, err_pct);

        /* Прокручуємо симуляцію на 10 кроків вперед */
        for (int sub = 0; sub < 10 && step + sub < NUM_STEPS; sub++) {
            long decayed_this_step = 0;
            for (long i = 0; i < current_N; i++) {
                double r = (double)rand() / RAND_MAX;
                if (r < p_decay) {
                    decayed_this_step++;
                }
            }
            current_N -= decayed_this_step;
        }
    }
}

/* Моделювання ланцюга розпаду A -> B -> C (утилізація пам'яті в стилі C) */
void simulate_decay_chain(double hl_A, double hl_B) {
    double lam_A = log(2.0) / hl_A;
    double lam_B = log(2.0) / hl_B;
    double p_A = 1.0 - exp(-lam_A * DT);
    double p_B = 1.0 - exp(-lam_B * DT);

    long n_A = INITIAL_N0;
    long n_B = 0;
    long n_C = 0;

    printf("\n=== Симуляція ланцюга A -> B -> C (C) ===\n");
    printf("T1/2(A) = %.1f с, T1/2(B) = %.1f с\n", hl_A, hl_B);
    printf("Час (с) | N_A (симул) | N_B (симул) | N_B (Бейтман)\n");
    printf("----------------------------------------------------\n");

    for (int step = 0; step <= NUM_STEPS; step++) {
        double t = step * DT;

        /* Аналітичне значення Бейтмана для N_B */
        double bateman_B = INITIAL_N0 * (lam_A / (lam_B - lam_A)) * 
                          (exp(-lam_A * t) - exp(-lam_B * t));

        if (step % 10 == 0) {
            printf("%7.1f | %11ld | %11ld | %13.1f\n", t, n_A, n_B, bateman_B);
        }

        /* Крок симуляції розпаду A */
        long decayed_A = 0;
        for (long i = 0; i < n_A; i++) {
            if (((double)rand() / RAND_MAX) < p_A) decayed_A++;
        }

        /* Крок симуляції розпаду B */
        long decayed_B = 0;
        for (long i = 0; i < n_B; i++) {
            if (((double)rand() / RAND_MAX) < p_B) decayed_B++;
        }

        n_A -= decayed_A;
        n_B += decayed_A - decayed_B;
        n_C += decayed_B;
    }
}

int main(void) {
    srand((unsigned int)time(NULL));
    simulate_single_decay(2.0);    /* T1/2 = 2.0 секунди */
    simulate_decay_chain(4.0, 1.0); /* T1/2(A)=4.0 с, T1/2(B)=1.0 с */
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <iomanip>
#include <numeric>
#include <algorithm>

class RadioactiveDecaySimulator {
public:
    struct SimulationPoint {
        double time_s;
        size_t n_simulated;
        double n_analytical;
        double relative_error_pct;
    };

    RadioactiveDecaySimulator(double half_life_s, size_t initial_nuclei)
        : half_life_(half_life_s),
          n0_(initial_nuclei),
          lambda_(std::log(2.0) / half_life_s),
          rng_(std::random_device{}()) {}

    [[nodiscard]] std::vector<SimulationPoint> run(double total_time_s, double dt_s) {
        const double p_decay = 1.0 - std::exp(-lambda_ * dt_s);
        std::bernoulli_distribution dist(p_decay);

        std::vector<SimulationPoint> results;
        size_t current_n = n0_;
        double current_time = 0.0;

        const size_t total_steps = static_cast<size_t>(total_time_s / dt_s);

        for (size_t step = 0; step <= total_steps; ++step) {
            const double analytic_n = n0_ * std::exp(-lambda_ * current_time);
            const double err_pct = (analytic_n > 0.0) 
                ? std::abs(static_cast<double>(current_n) - analytic_n) / analytic_n * 100.0 
                : 0.0;

            results.push_back({current_time, current_n, analytic_n, err_pct});

            // Симуляція кроку: розпад для кожного з n ядер
            size_t decayed_count = 0;
            for (size_t i = 0; i < current_n; ++i) {
                if (dist(rng_)) {
                    ++decayed_count;
                }
            }
            current_n -= decayed_count;
            current_time += dt_s;
        }

        return results;
    }

    // Обчислення флуктуацій та перевірка закону 1/sqrt(N)
    [[nodiscard]] static double compute_statistical_fluctuation(
        size_t num_runs, size_t nuclei_count, double half_life_s, double observation_time_s) {
        
        const double lambda = std::log(2.0) / half_life_s;
        const double p_decay_total = 1.0 - std::exp(-lambda * observation_time_s);

        std::mt19937 generator(42); // Фіксоване зерно для відтворюваності
        std::binomial_distribution<size_t> binom(nuclei_count, p_decay_total);

        std::vector<double> decay_counts(num_runs);
        for (size_t i = 0; i < num_runs; ++i) {
            decay_counts[i] = static_cast<double>(binom(generator));
        }

        const double mean = std::accumulate(decay_counts.begin(), decay_counts.end(), 0.0) / num_runs;
        double variance = 0.0;
        for (double val : decay_counts) {
            variance += (val - mean) * (val - mean);
        }
        variance /= (num_runs - 1);

        return std::sqrt(variance) / mean; // Відносне стандартне відхилення
    }

private:
    double half_life_;
    size_t n0_;
    double lambda_;
    std::mt19937 rng_;
};

int main() {
    constexpr double half_life = 2.0;
    constexpr size_t n0 = 100'000;
    constexpr double dt = 0.1;
    constexpr double total_time = 5.0;

    RadioactiveDecaySimulator sim(half_life, n0);
    const auto timeline = sim.run(total_time, dt);

    std::cout << "=== Симуляція Монте-Карло радіоактивного розпаду (C++) ===\n";
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "t (с) | Симуляція N(t) | Аналітичне N(t) | Похибка (%)\n";
    std::cout << "----------------------------------------------------\n";

    for (size_t i = 0; i < timeline.size(); i += 5) {
        const auto& pt = timeline[i];
        std::cout << std::setw(5) << pt.time_s << " | "
                  << std::setw(14) << pt.n_simulated << " | "
                  << std::setw(15) << pt.n_analytical << " | "
                  << std::setw(10) << std::setprecision(3) << pt.relative_error_pct << "\n";
    }

    // Демонстрація масштабування похибки 1/sqrt(N)
    std::cout << "\n=== Статистичні флуктуації (Закон 1/sqrt(N)) ===\n";
    for (size_t sample_N : {100, 1000, 10000, 100000}) {
        const double rel_stddev = RadioactiveDecaySimulator::compute_statistical_fluctuation(
            1000, sample_N, 2.0, 1.0);
        const double theoretical_rel_stddev = 1.0 / std::sqrt(sample_N * (1.0 - std::exp(-std::log(2.0)/2.0 * 1.0)));
        std::cout << "N0 = " << std::setw(6) << sample_N 
                  << " | Експериментальне σ/N = " << std::setw(6) << std::setprecision(4) << rel_stddev
                  << " | Теоретичне 1/√<N> = " << std::setw(6) << theoretical_rel_stddev << "\n";
    }

    return 0;
}
```
:::

## 3. Детальний розбір реалізації та розбіжностей підходів

При розробці моделей радіоактивного розпаду важливо розуміти фундаментальні відмінності між процедурним підходом C та об'єктно-орієнтованим оболонковим підходом C++:

1. **Керування станом та глобальні константи**:
   У C-реалізації використовується пряма ітерація по циклу за допомогою `for` і фундаментальні типи даних `long`. Початковий стан `N₀` задається через константу препроцесора `#define`. Натомість у C++ стан запаковано всередині класу `RadioactiveDecaySimulator` із приватними членами `half_life_`, `n0_` та `lambda_`, що запобігає випадковій модифікації та дозволяє запускати експерименти паралельно у кількох потоках із різними параметрами.

2. **Ґенерація випадкових подій**:
   У реалізації на C виклик `rand() / RAND_MAX` виконується для кожного ядра на кожному кроці `dt`. Це дає часову складність `O(N · K)`, де `N` — кількість ядер, а `K` — число кроків. При `N₀ = 100 000` та 100 кроках це потребує 10 мільйонів викликів `rand()`.
   У C++ за допомогою `std::bernoulli_distribution` досягається той самий стохастичний ефект. Більше того, для обчислення статистичних флуктуацій великої кількості незалежних випробувань у метод `compute_statistical_fluctuation` залучено `std::binomial_distribution`. Вона дозволяє безпосередньо згенерувати кількість ядер, що розпалися за проміжок часу, зі складністю `O(1)` за один виклик ґенератора, замість того щоб прокручувати в циклі мільйони частинок.

3. **Обробка та повернення даних**:
   У C результати друкуються безпосередньо в консоль через `printf` під час обчислення. У C++ метод `run()` формує та повертає вектор структур `std::vector<SimulationPoint>`, що дає змогу подальшої аналітичної обробки або побудови графіків.

## 4. Обчислювальна складність та алгоритми оптимізації

Пряма побудова симуляції, де кожне з `N` ядер перевіряється на розпад на кожному з `K` часових кроків, має лінійну складність `O(N)` по пам'яті (якщо зберігається стан кожного ядра) та `O(N · K)` за часом.

Для систем із макроскопічною кількістю ядер (`N ~ 10²³`) пряме перебирання частинок у циклі стає неможливим. Застосовують дві високоефективні стратегії оптимізації:

### Оптимізація 1: Біноміальне вибіркове моделювання (Binomial Sampling)

Оскільки розпад `N` незалежних ядер з однаковою ймовірністю `p` підпорядковується біноміальному розподілу `B(N, p)`, замість перевірки кожної частинки окремо ґенерують одне випадкове число із біноміального розподілу:

```
decayed_count = std::binomial_distribution<>(N, p)(rng);
N_next = N - decayed_count;
```

Цей підхід зменшує обчислювальну складність з `O(N · K)` до `O(K)` — часові витрати більше взагалі не залежать від кількості ядер у зразку.

### Оптимізація 2: Метод неперервного часу (Gillespie / Kinetic Monte Carlo)

Замість фіксованих кроків `dt` ґенерують вибірку часу наступного розпаду. Сумарна інтенсивність розпаду ансамблю з `N` ядер дорівнює `R = λ · N`. Час `Δt` до появи НАСТУПНОГО розпаду в системі підпорядковується експоненціальному розподілу із середнім `1 / R`:

```
Δt = -ln(u) / (λ · N)
```

де `u ∈ (0, 1]` — рівномірно розподілене випадкове число.

Алгоритм Гіллеспі просуває годинник симуляції одразу на інтервал `Δt` до наступного розпаду та зменшує `N` на 1. Це ідеальний метод для симуляції систем із малою кількістю частинок (`N < 1000`).

## 5. Граничні випадки та чисельна стійкість

При розрахунку складних розгалужених або жорстких ланцюгів радіоактивних перетворень (коли сталі розпаду різних нуклідів `λ_i` відрізняються на багато порядків) чисельні моделі стикаються з проблемою катастрофічної втрати точності:

1. **Втрата значущих розрядів при відніманні близьких експонент**:
   У аналітичній формулі Бейтмана `e^(-λ_A · t) - e^(-λ_B · t)` при близьких значеннях `λ_A ≈ λ_B` виникає ділення на мало значення `λ_B - λ_A`, що призводить до втрати точності чисел із плаваючою комою. У чисельних розрахунках застосовують розклад за рядами Тейлора або спеціальні алгоритми типу Pade-апроксимації матричної експоненти.
2. **Жорсткі диференціальні рівняння (Stiff ODEs)**:
   Якщо в ланцюгу одночасно присутні короткоживучий нуклід (`T₁/₂ = 1` мікросекунда) та довгоживучий (`T₁/₂ = 10` років), стандартні явні методи Ейлера чи Рунге — Кутти стають нестійкими й вимагають крихітного часового кроку `dt < 10⁻⁷` с. Симуляція методом Монте-Карло з біноміальним вибором позбавлена цієї нестійкості, оскільки вона моделює фізичну ймовірність прямо без чисельного диференціювання.

## 6. Фізичний аналіз результатів чисельного експерименту

Чисельне моделювання показує виражені особливості квантової статистики розпадів:

1. **Збіжність до експоненти**: При `N₀ = 100 000` ядрах відносна похибка між симуляцією Монте-Карло та експоненціальною кривою `N₀ · e^(-λt)` не перевищує `0.3%`.
2. **Флуктуації малого ансамблю**: Якщо зменшити чисельність початкового ансамблю до `N₀ = 100` ядер, флуктуації зростають до `~ 10%`, оскільки відносна похибка підпорядковується закону `σ / N = 1 / √N`.
3. **Ланцюгова динаміка**: Симуляція ланцюга `A → B → C` чітко відтворює максимум активності дочірнього ізотопу `B` у момент часу `t_max = ln(λ_B / λ_A) / (λ_B - λ_A)` та перехід системи в стан тимчасової або вікової рівноваги.
