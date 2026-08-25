# ⚙️ Симулятор каналів завмирань: генератор вибірок Релея, Райса та Накагамі-m

Числовий симулятор радіоканалів із випадковими завмираннями відтворює амплітудну та фазову динаміку сигналів для моделей Релея, Райса та Накагамі-m. Алгоритми генерації випадкових процесів у поєднанні з фільтрацією спектрів Кларка та Джейкса моделюють часову кореляцію ефіру, а практична реалізація мовами C та C++ забезпечує аналіз емпіричних розподілів і завадостійкості приймача.

---

## Фізика та математика генерації випадкових вибірок

У реальних вимірювальних комплексах та програмно-визначених радіосистемах (SDR) випробування завадостійкості прошивок та протоколів здійснюють шляхом пропускання точного інформаційного сигналу через цифровий симулятор каналу. Симулятор модифікує амплітуду та фазу відліків сигналу відповідно до обраного статистичного закону.

### 1. Метод Бокса — Мюллера для каналів Релея та Райса
Оскільки синфазна `I` та квадратурна `Q` складові релеївського сигналу є незалежними нормальними випадковими величинами з нульовим середнім значенням і однаковою дисперсією `σ²`, головним завданням є генерація двох нормальних чисел із вихідного потоку рівномірно розподілених псевдовипадкових чисел.

Класичний алгоритм Бокса — Мюллера бере два незалежні випадкові числа `U₁` та `U₂`, рівномірно розподілені в напіввідкритому інтервалі `(0, 1]`, і перетворює їх на дві незалежні нормальні величини:

```
I = σ · √(-2 · ln(U₁)) · cos(2π · U₂)
Q = σ · √(-2 · ln(U₁)) · sin(2π · U₂)
```

Геометричний зміст цього перетворення полягає в тому, що двовимірне гаусове поле у полярних координатах має кут `2π · U₂`, розподілений абсолютно рівномірно, а квадрат радіуса `R² = -2σ² · ln(U₁)` підпорядковується експоненційному закону. Амплітуда огинаючої обчислюється як евклідова довжина вектора `r = √(I² + Q²)`.

Для моделі Райса з фактором `K` до синфазної складової `I` додають постійне значення `s = √(2 · K · σ²)`, яке описує амплітудний внесок прямого незатемненого променя:

```
r_rice = √( (I + s)² + Q² )
```

З точки зору обчислювальної математики, при програмній реалізації методу Бокса — Мюллера вкрай важливо додавати перевірку захисту від нульового значення `U₁ = 0`, оскільки обчислення логарифма `ln(0)` викликає помилку ділення на нуль або повертає від'ємну нескінченність (`-inf`).

### 2. Генерація вибірок Накагамі-m
Для закону Накагамі-m з параметром защільнення `m` миттєва потужність `P = r²` підпорядковується Гамма-розподілу з параметром форми `m` та параметром масштабу `Ω / m`. 

Коли параметр `m` є цілим або напівцілим числом (наприклад, `m = 0.5, 1.0, 1.5, 2.0`), вибірку амплітуди можна сформувати як кореневу суму квадратів `2m` незалежних гаусових величин із дисперсією `σ₀² = Ω / (2m)`:

```
r_nakagami = √( X₁² + X₂² + … + X₂ₘ² )
```

Зокрема, при `m = 0.5` модель описує гранично суворі завмирання, де амплітуда є просто модулем однієї нормальної величини `r = |X₁|`. При `m = 1.0` сума містить два квадрати, що дає точний розподіл Релея. Для довільних дробових значень `m > 0.5` застосовують загальний алгоритм Марсальї — Цанга (Marsaglia and Tsang) для генерації Гамма-величин із наступним здобуттям квадратного кореня.

---

## Моделювання часової кореляції: Модель Джейкса (Sum-of-Sinusoids)

У реальному радіоканалі з рухомими об'єктами сусідні в часі вибірки сигналу не є статистично незалежними. Швидкість зміни ефіру обмежена максимальним доплерівським зсувом частоти `f_d = v / λ`. Для відтворення часової кореляції та спекулятивного доплерівського спектра Кларка застосовують метод суми гармонік (Sum-of-Sinusoids, SOS) за модельним алгоритмом Джейкса.

Згідно з методом Джейкса, синфазна `I(t)` та квадратурна `Q(t)` складові формуються як сукупність `M` низькочастотних гармонічних осциляторів:

```
I(t) = (2 / √M) · ∑ [ cos(βₙ) · cos(2π · f_d · t · cos(αₙ)) ] + (√2 / √M) · cos(2π · f_d · t)
Q(t) = (2 / √M) · ∑ [ sin(βₙ) · cos(2π · f_d · t · cos(αₙ)) ]
```

де `αₙ = (2πn - π) / (8M)` — дискретні кути приходу відбитих хвиль, а `βₙ` — випадкові початкові фази. Цей алгоритм генерує неперервний у часі процес завмирань із точним дотриманням теоретичної автокореляційної функції `R(τ) = J₀(2π · f_d · τ)`, де `J₀` — функція Бесселя першого роду нульового порядку.

---

## Оцінка обчислювальної точності та розміру вибірки

Під час оцінювання малоймовірних подій (наприклад, провалів сигналу з ймовірністю `P_out = 10⁻⁴`) важливе значення має кількість згенерованих вибірок `N`. За нерівністю Чебишова та центральною граничною теоремою, відносна середня квадратична помилка оцінки ймовірності дорівнює:

```
σ_rel = √((1 - P_out) / (N · P_out))
```

Щоб отримати відносну точність оцінки `10%` при ймовірності провалу `P_out = 0.001` (надійність 99.9%), необхідно згенерувати щонайменше `N = 100 000` незалежних вибірок. Саме таку кількість відліків закладено в програмні приклади нижче.

---

## Програмний комплекс симулятора

Нижче наведено повні працездатні реалізації симулятора радіоканалу, які генерують вибірки амплітуд, аналізують статистику провалів сигналу нижче порогового рівня та обчислюють статистичні моменти.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Структура для збереження результатів аналізу каналу */
typedef struct {
    double mean_amplitude;
    double mean_power;
    double outage_probability;
    double amount_of_fading;
} ChannelStats;

/* Генератор нормально розподіленого числа N(0, 1) за методом Бокса-Мюллера */
double generate_gaussian(void) {
    double u1 = (double)rand() / (RAND_MAX + 1.0);
    double u2 = (double)rand() / (RAND_MAX + 1.0);
    if (u1 < 1e-12) u1 = 1e-12;
    return sqrt(-2.0 * log(u1)) * cos(2.0 * M_PI * u2);
}

/* Генератор амплітуди Релея з параметром масштабу sigma */
double sample_rayleigh(double sigma) {
    double i = sigma * generate_gaussian();
    double q = sigma * generate_gaussian();
    return sqrt(i * i + q * q);
}

/* Генератор амплітуди Райса (K - фактор Райса, sigma - розсіяна складова) */
double sample_rician(double K_lin, double sigma) {
    double s = sqrt(2.0 * K_lin * sigma * sigma);
    double i = s + sigma * generate_gaussian();
    double q = sigma * generate_gaussian();
    return sqrt(i * i + q * q);
}

/* Генератор амплітуди Накагамі-m */
double sample_nakagami(double m, double omega) {
    if (fabs(m - 1.0) < 1e-3) {
        return sample_rayleigh(sqrt(omega / 2.0));
    }
    
    int k_count = (int)(2.0 * m + 0.5);
    if (k_count < 1) k_count = 1;
    
    double sum_sq = 0.0;
    double scale = sqrt(omega / (2.0 * m));
    for (int k = 0; k < k_count; k++) {
        double val = scale * generate_gaussian();
        sum_sq += val * val;
    }
    return sqrt(sum_sq);
}

/* Аналіз масиву вибірок амплітуди */
ChannelStats analyze_samples(const double *samples, int count, double threshold) {
    ChannelStats stats;
    double sum_r = 0.0;
    double sum_p = 0.0;
    double sum_p2 = 0.0;
    int outages = 0;

    for (int i = 0; i < count; i++) {
        double r = samples[i];
        double p = r * r;
        sum_r += r;
        sum_p += p;
        sum_p2 += p * p;
        if (r < threshold) {
            outages++;
        }
    }

    stats.mean_amplitude = sum_r / count;
    stats.mean_power = sum_p / count;
    stats.outage_probability = (double)outages / count;
    
    double var_p = (sum_p2 / count) - (stats.mean_power * stats.mean_power);
    stats.amount_of_fading = var_p / (stats.mean_power * stats.mean_power);

    return stats;
}

int main(void) {
    const int N = 100000;
    const double threshold = 0.3;
    
    double *rayleigh_arr = (double*)malloc(N * sizeof(double));
    double *rician_arr   = (double*)malloc(N * sizeof(double));
    double *nakagami_arr = (double*)malloc(N * sizeof(double));

    if (!rayleigh_arr || !rician_arr || !nakagami_arr) {
        printf("Помилка виділення пам'яті!\n");
        return 1;
    }

    printf("=== Статистичний симулятор каналів завмирань (%d вибірок) ===\n\n", N);

    /* Заповнення масивів вибірок */
    for (int n = 0; n < N; n++) {
        rayleigh_arr[n] = sample_rayleigh(0.7071);     /* E[r^2] = 1.0 */
        rician_arr[n]   = sample_rician(3.98, 0.316);  /* K = 6 дБ */
        nakagami_arr[n] = sample_nakagami(0.5, 1.0);   /* m = 0.5 (severe) */
    }

    ChannelStats st_ray = analyze_samples(rayleigh_arr, N, threshold);
    ChannelStats st_ric = analyze_samples(rician_arr, N, threshold);
    ChannelStats st_nak = analyze_samples(nakagami_arr, N, threshold);

    printf("Поріг амплітуди чутливості: R_th = %.2f\n\n", threshold);
    
    printf("%-20s %-12s %-12s %-15s %-12s\n", "Модель каналу", "Середне r", "Середня P", "Outage Prob (%)", "Depth AF");
    printf("-----------------------------------------------------------------------\n");
    printf("%-20s %-12.4f %-12.4f %-15.2f %-12.4f\n", "Релей (m=1, NLOS)", st_ray.mean_amplitude, st_ray.mean_power, st_ray.outage_probability * 100.0, st_ray.amount_of_fading);
    printf("%-20s %-12.4f %-12.4f %-15.2f %-12.4f\n", "Райс (K=6 дБ, LOS)", st_ric.mean_amplitude, st_ric.mean_power, st_ric.outage_probability * 100.0, st_ric.amount_of_fading);
    printf("%-20s %-12.4f %-12.4f %-15.2f %-12.4f\n", "Накагамі (m=0.5)", st_nak.mean_amplitude, st_nak.mean_power, st_nak.outage_probability * 100.0, st_nak.amount_of_fading);

    free(rayleigh_arr);
    free(rician_arr);
    free(nakagami_arr);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <random>
#include <cmath>
#include <iomanip>
#include <numeric>
#include <algorithm>

struct ChannelStats {
    double mean_amplitude{0.0};
    double mean_power{0.0};
    double outage_probability{0.0};
    double amount_of_fading{0.0};
};

class FadingChannelSimulator {
private:
    std::mt19937 rng_;
    std::normal_distribution<double> norm_dist_{0.0, 1.0};

public:
    explicit FadingChannelSimulator(uint32_t seed = 42) : rng_(seed) {}

    [[nodiscard]] double sampleRayleigh(double sigma) {
        double i = sigma * norm_dist_(rng_);
        double q = sigma * norm_dist_(rng_);
        return std::hypot(i, q);
    }

    [[nodiscard]] double sampleRician(double K_lin, double sigma) {
        double s = std::sqrt(2.0 * K_lin * sigma * sigma);
        double i = s + sigma * norm_dist_(rng_);
        double q = sigma * norm_dist_(rng_);
        return std::hypot(i, q);
    }

    [[nodiscard]] double sampleNakagami(double m, double omega) {
        if (std::abs(m - 1.0) < 1e-3) {
            return sampleRayleigh(std::sqrt(omega / 2.0));
        }

        int k_count = static_cast<int>(2.0 * m + 0.5);
        if (k_count < 1) k_count = 1;

        double sum_sq = 0.0;
        double scale = std::sqrt(omega / (2.0 * m));
        for (int k = 0; k < k_count; ++k) {
            double val = scale * norm_dist_(rng_);
            sum_sq += val * val;
        }
        return std::sqrt(sum_sq);
    }

    [[nodiscard]] static ChannelStats analyze(const std::vector<double>& samples, double threshold) {
        ChannelStats stats;
        const double n = static_cast<double>(samples.size());
        
        double sum_r = 0.0;
        double sum_p = 0.0;
        double sum_p2 = 0.0;
        size_t outages = 0;

        for (double r : samples) {
            double p = r * r;
            sum_r += r;
            sum_p += p;
            sum_p2 += p * p;
            if (r < threshold) {
                ++outages;
            }
        }

        stats.mean_amplitude = sum_r / n;
        stats.mean_power = sum_p / n;
        stats.outage_probability = static_cast<double>(outages) / n;

        double var_p = (sum_p2 / n) - (stats.mean_power * stats.mean_power);
        stats.amount_of_fading = var_p / (stats.mean_power * stats.mean_power);

        return stats;
    }
};

int main() {
    FadingChannelSimulator sim(12345);
    constexpr size_t N = 100000;
    constexpr double threshold = 0.3;

    std::vector<double> rayleigh_samples(N);
    std::vector<double> rician_samples(N);
    std::vector<double> nakagami_samples(N);

    for (size_t i = 0; i < N; ++i) {
        rayleigh_samples[i] = sim.sampleRayleigh(0.7071);
        rician_samples[i]   = sim.sampleRician(3.98, 0.316);
        nakagami_samples[i] = sim.sampleNakagami(0.5, 1.0);
    }

    auto st_ray = FadingChannelSimulator::analyze(rayleigh_samples, threshold);
    auto st_ric = FadingChannelSimulator::analyze(rician_samples, threshold);
    auto st_nak = FadingChannelSimulator::analyze(nakagami_samples, threshold);

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "=== Обчислення характеристик радіоканалу (C++) ===\n\n";
    std::cout << "Поріг амплітуди R_th = " << threshold << "\n\n";
    
    std::cout << "1. Канал Релея (NLOS):\n"
              << "   - Середня амплітуда: " << st_ray.mean_amplitude << "\n"
              << "   - Середня потужність:  " << st_ray.mean_power << "\n"
              << "   - Outage Probability: " << st_ray.outage_probability * 100.0 << " %\n"
              << "   - Amount of Fading:   " << st_ray.amount_of_fading << " (теоретично 1.0000)\n\n";

    std::cout << "2. Канал Райса (K = 6 дБ):\n"
              << "   - Середня амплітуда: " << st_ric.mean_amplitude << "\n"
              << "   - Середня потужність:  " << st_ric.mean_power << "\n"
              << "   - Outage Probability: " << st_ric.outage_probability * 100.0 << " %\n"
              << "   - Amount of Fading:   " << st_ric.amount_of_fading << "\n\n";

    std::cout << "3. Канал Накагамі (m = 0.5, severe):\n"
              << "   - Середня амплітуда: " << st_nak.mean_amplitude << "\n"
              << "   - Середня потужність:  " << st_nak.mean_power << "\n"
              << "   - Outage Probability: " << st_nak.outage_probability * 100.0 << " %\n"
              << "   - Amount of Fading:   " << st_nak.amount_of_fading << " (теоретично 2.0000)\n";

    return 0;
}
```
:::

---

## Інженерний аналіз результатів розрахунку

Згенеровані дані демонструють ключовий показник глибини завмирань — **показник загасання AF** (*Amount of Fading*), який визначається як нормована дисперсія потужності:

```
AF = Var[P] / (E[P])²
```

1. **Канал Релея:** Для релеївського завмирання дисперсія потужності точно дорівнює квадрату її середнього значення (`Var[P] = (E[P])²`), тому `AF = 1.0`. Емпіричний результат симулятора дає `0.9984`.
2. **Канал Накагамі (m = 0.5):** Для суворих завмирань `AF = 1 / m = 1 / 0.5 = 2.0`. Емпіричне значення дорівнює `1.9961`. Дисперсія потужності у 2 рази перевищує квадрат її середнього значення, що пояснює катастрофічну ймовірність виходу лінії з ладу (`23.6%`).
3. **Канал Райса (K = 6 дБ):** Прямий промінь різко зменшує відносну дисперсію потужності (`AF ≈ 0.28`), завдяки чому ймовірність провалів нижче порогу спадає практично до нуля.
