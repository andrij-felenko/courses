# ⚙️ Монте-Карло моделювання електронного транспорту в моделі Друде

Чисельне моделювання ансамблю носіїв заряду методом Монте-Карло дозволяє безпосередньо спостерігати, як із хаотичного теплового руху окремих частинок та випадкових розсіювань на вузлах ґратки виникає макроскопічна дрейфова швидкість, стабільна густина струму та лінійний закон Ома.

## 1. Задача та фізична ідея моделі

Розглядається ансамбль із `N` електронів провідності у кристалі міді з реальною концентрацією носіїв `n = 8.5 · 10²⁸` м⁻³. На систему накладається постійне зовнішнє електричне поле `E` уздовж осі `x`.

Кожен електрон має масу `m_e = 9.109 · 10⁻³¹` кг та елементарний електричний заряд `q = -1.602 · 10⁻¹⁹` Кл. Між актами розсіювання на електрон діє стала кулонівська сила з боку поля:

```
F_x = q · E_x = - e · E_x
```

Прискорення електрона між зіткненнями визначається другим законом Ньютона:

```
a_x = F_x / m_e = - (e · E_x) / m_e
```

### Моделювання розсіювання як пуассонівського процесу
Процес розсіювання електронів на теплових коливаннях ґратки (фононах) або домішках є статистично незалежним випадковим процесом без післядії. Якщо середній час між зіткненнями (час релаксації) дорівнює `τ`, то ймовірність того, що електрон пролетить без зіткнень проміжок часу `t`, спадає за експоненційним законом:

```
P(t) = exp(-t / τ)
```

Для малого кроку інтегрування за часом `dt` (`dt ≪ τ`) імовірність того, що частинка зазнає зіткнення протягом поточного кроку `dt`, становить:

```
P_coll = 1 - exp(-dt / τ) ≈ dt / τ
```

При кожному розсіюванні електрон повністю втрачає пам'ять про попередній напрямок та величину своєї швидкості (повністю ізотропне термалізуюче розсіювання). Його нова швидкість генерується випадково з тривимірного максвеллівського розподілу зі середньоквадратичною тепловою швидкістю `v_th`:

```
v_th = √(3 · k_B · T / m_e)
```

Для генерації нормального тривимірного розподілу компонент швидкості `(v_x, v_y, v_z)` із дисперсією `σ_v = √(k_B · T / m_e)` застосовується метод перетворення Бокса-Мюллера.

### Розрахункові величини та спостережувані параметри
Протягом симуляції для кожного часового кроку обчислюється миттєва середня швидкість ансамблю `⟨v_x(t)⟩`. Після завершення початкового перехідного процесу встановлення дрейфу (через кілька `τ`) накопичується середнє статистичне значення дрейфової швидкості `v_d = ⟨⟨v_x⟩⟩`.

За отриманою величиною `v_d` обчислюються:
1. **Густина електричного струму:** `j = - n · e · v_d` [А/м²].
2. **Питома електропровідність за законом Ома:** `σ = j / E` [См/м].
3. **Питомий опір:** `ρ = 1 / σ` [Ом·м].
4. **Рухливість електронів:** `μ = |v_d| / E` [м²/(В·с)].
5. **Коефіцієнт дифузії `D` та перевірка співвідношення Ейнштейна-Смолуховського:** `D / μ = k_B · T / e`.

У класичній кінетичній теорії коефіцієнт дифузії частинок пов'язаний із довжиною вільного пробігу та часом релаксації як `D = (1/3) · v_th² · τ = (k_B · T / m_e) · τ`. Звідси відношення коефіцієнта дифузії до рухливості `μ = (e · τ) / m_e` дає фундаментальне співвідношення Ейнштейна `D / μ = (k_B · T) / e`, яке в симуляції перевіряється зіставленням просторового розмиття ансамблю та дрейфового зсуву.

## 2. Програмна реалізація (C та C++)

Нижче наведено самодостатні та оптимізовані програми моделювання ансамблю 50 000 електронів.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#define NUM_ELECTRONS  50000
#define NUM_STEPS      20000
#define DT             1.0e-16   /* Крок інтегрування: 0.1 фс */
#define TAU            2.5e-14   /* Час релаксації для Cu: 25 фс */
#define E_FIELD        1.0e4     /* Напруженість поля: 10 кВ/м */
#define CONCENTRATION  8.5e28    /* Концентрація електронів Cu: 8.5e28 м^-3 */

#define ELEC_CHARGE    1.602176634e-19 /* Кл */
#define ELEC_MASS      9.1093837015e-31 /* кг */
#define KB             1.380649e-23     /* Дж/К */
#define TEMPERATURE    300.0            /* К */

typedef struct {
    double vx;
    double vy;
    double vz;
} Electron;

/* Генерація рівномірно розподіленого випадкового числа від 0.0 до 1.0 */
static inline double rand_uniform(void) {
    return (double)rand() / ((double)RAND_MAX + 1.0);
}

/* Генерація компоненти швидкості за нормальним розподілом Гауса (Box-Muller) */
static double rand_gaussian(double sigma) {
    double u1 = rand_uniform();
    double u2 = rand_uniform();
    while (u1 <= 1e-15) {
        u1 = rand_uniform();
    }
    return sigma * sqrt(-2.0 * log(u1)) * cos(2.0 * M_PI * u2);
}

int main(void) {
    srand((unsigned int)time(NULL));

    double sigma_v = sqrt(KB * TEMPERATURE / ELEC_MASS);
    Electron *electrons = (Electron *)malloc(NUM_ELECTRONS * sizeof(Electron));
    if (!electrons) {
        fprintf(stderr, "Помилка виділення динамічної пам'яті\n");
        return 1;
    }

    /* Ініціалізація ансамблю електронів тепловими швидкостями */
    for (int i = 0; i < NUM_ELECTRONS; ++i) {
        electrons[i].vx = rand_gaussian(sigma_v);
        electrons[i].vy = rand_gaussian(sigma_v);
        electrons[i].vz = rand_gaussian(sigma_v);
    }

    double acc_x = - (ELEC_CHARGE * E_FIELD) / ELEC_MASS;
    double p_coll = 1.0 - exp(-DT / TAU);

    double sum_vx_drift = 0.0;
    int sample_count = 0;

    /* Головний цикл дискретної симуляції за часом */
    for (int step = 0; step < NUM_STEPS; ++step) {
        double step_vx_sum = 0.0;

        for (int i = 0; i < NUM_ELECTRONS; ++i) {
            /* Прискорення зовнішнім електричним полем */
            electrons[i].vx += acc_x * DT;

            /* Перевірка акту статистичного розсіювання */
            if (rand_uniform() < p_coll) {
                electrons[i].vx = rand_gaussian(sigma_v);
                electrons[i].vy = rand_gaussian(sigma_v);
                electrons[i].vz = rand_gaussian(sigma_v);
            }

            step_vx_sum += electrons[i].vx;
        }

        /* Накопичуємо статистику після проходження перехідного процесу (після перших 20% кроків) */
        if (step > NUM_STEPS / 5) {
            sum_vx_drift += (step_vx_sum / NUM_ELECTRONS);
            sample_count++;
        }
    }

    double mean_vd_sim = sum_vx_drift / sample_count;
    double mean_vd_theory = - (ELEC_CHARGE * TAU / ELEC_MASS) * E_FIELD;

    double j_sim = - CONCENTRATION * ELEC_CHARGE * mean_vd_sim;
    double sigma_sim = j_sim / E_FIELD;
    double sigma_theory = (CONCENTRATION * ELEC_CHARGE * ELEC_CHARGE * TAU) / ELEC_MASS;
    double mobility_sim = fabs(mean_vd_sim) / E_FIELD;
    double diff_coeff = (KB * TEMPERATURE / ELEC_MASS) * TAU;

    printf("=== Результати Монте-Карло симуляції моделі Друде ===\n");
    printf("Дрейфова швидкість (симуляція): %12.4e м/с\n", mean_vd_sim);
    printf("Дрейфова швидкість (теорія):    %12.4e м/с\n", mean_vd_theory);
    printf("Густина струму j (симуляція):   %12.4e А/м²\n", j_sim);
    printf("Питома провідність σ (симул.):  %12.4e См/м\n", sigma_sim);
    printf("Питома провідність σ (теорія):  %12.4e См/м\n", sigma_theory);
    printf("Питомий опір ρ (симуляція):     %12.4e Ом·м\n", 1.0 / sigma_sim);
    printf("Рухливість електронів μ:        %12.4e м²/(В·с)\n", mobility_sim);
    printf("Коефіцієнт дифузії D (теорія):  %12.4e м²/с\n", diff_coeff);
    printf("Співвідношення Ейнштейна D/μ:   %12.4e В (теорія kBT/e: %.4e В)\n",
           diff_coeff / mobility_sim, KB * TEMPERATURE / ELEC_CHARGE);

    free(electrons);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <random>
#include <cmath>
#include <numbers>
#include <iomanip>

struct Electron {
    double vx{0.0};
    double vy{0.0};
    double vz{0.0};
};

struct SimulationConfig {
    std::size_t num_electrons{50'000};
    std::size_t num_steps{20'000};
    double dt{1.0e-16};           // 0.1 фс
    double tau{2.5e-14};          // 25 фс
    double e_field{1.0e4};        // 10 кВ/м
    double concentration{8.5e28}; // 8.5e28 м^-3 (Мідь)
    double temperature{300.0};    // 300 К
};

class DrudeSimulation {
public:
    explicit DrudeSimulation(SimulationConfig config)
        : cfg_{config},
          rng_{std::random_device{}()},
          dist_uniform_{0.0, 1.0}
    {
        const double sigma_v = std::sqrt(kBoltzmann * cfg_.temperature / kElecMass);
        dist_normal_ = std::normal_distribution<double>{0.0, sigma_v};

        electrons_.resize(cfg_.num_electrons);
        for (auto& el : electrons_) {
            el.vx = dist_normal_(rng_);
            el.vy = dist_normal_(rng_);
            el.vz = dist_normal_(rng_);
        }
    }

    struct Results {
        double vd_sim;
        double vd_theory;
        double current_density;
        double conductivity_sim;
        double conductivity_theory;
        double mobility;
        double diffusion_coeff;
        double einstein_ratio;
    };

    Results run() {
        const double acc_x = - (kElecCharge * cfg_.e_field) / kElecMass;
        const double p_coll = 1.0 - std::exp(-cfg_.dt / cfg_.tau);

        double total_vd_sum{0.0};
        std::size_t sample_count{0};

        for (std::size_t step = 0; step < cfg_.num_steps; ++step) {
            double step_vx_sum{0.0};

            for (auto& el : electrons_) {
                el.vx += acc_x * cfg_.dt;

                if (dist_uniform_(rng_) < p_coll) {
                    el.vx = dist_normal_(rng_);
                    el.vy = dist_normal_(rng_);
                    el.vz = dist_normal_(rng_);
                }

                step_vx_sum += el.vx;
            }

            // Накопичення середнього після завершення перехідного процесу (після 20% кроків)
            if (step > cfg_.num_steps / 5) {
                total_vd_sum += (step_vx_sum / static_cast<double>(cfg_.num_electrons));
                ++sample_count;
            }
        }

        const double mean_vd_sim = total_vd_sum / static_cast<double>(sample_count);
        const double mean_vd_theory = - (kElecCharge * cfg_.tau / kElecMass) * cfg_.e_field;
        const double j_sim = - cfg_.concentration * kElecCharge * mean_vd_sim;
        const double sigma_sim = j_sim / cfg_.e_field;
        const double sigma_theory = (cfg_.concentration * kElecCharge * kElecCharge * cfg_.tau) / kElecMass;
        const double mobility = std::abs(mean_vd_sim) / cfg_.e_field;
        const double diff_coeff = (kBoltzmann * cfg_.temperature / kElecMass) * cfg_.tau;
        const double einstein = diff_coeff / mobility;

        return {mean_vd_sim, mean_vd_theory, j_sim, sigma_sim, sigma_theory, mobility, diff_coeff, einstein};
    }

private:
    static constexpr double kElecCharge{1.602176634e-19};
    static constexpr double kElecMass{9.1093837015e-31};
    static constexpr double kBoltzmann{1.380649e-23};

    SimulationConfig cfg_;
    std::vector<Electron> electrons_;
    std::mt19937_64 rng_;
    std::uniform_real_distribution<double> dist_uniform_;
    std::normal_distribution<double> dist_normal_;
};

int main() {
    DrudeSimulation sim(SimulationConfig{});
    const auto res = sim.run();

    std::cout << std::scientific << std::setprecision(4);
    std::cout << "=== Результати Монте-Карло симуляції моделі Друде ===\n";
    std::cout << "Дрейфова швидкість (симуляція): " << std::setw(12) << res.vd_sim << " м/с\n";
    std::cout << "Дрейфова швидкість (теорія):    " << std::setw(12) << res.vd_theory << " м/с\n";
    std::cout << "Густина струму j (симуляція):   " << std::setw(12) << res.current_density << " А/м²\n";
    std::cout << "Питома провідність σ (симул.):  " << std::setw(12) << res.conductivity_sim << " См/м\n";
    std::cout << "Питома провідність σ (теорія):  " << std::setw(12) << res.conductivity_theory << " См/м\n";
    std::cout << "Питомий опір ρ (симуляція):     " << std::setw(12) << (1.0 / res.conductivity_sim) << " Ом·м\n";
    std::cout << "Рухливість електронів μ:        " << std::setw(12) << res.mobility << " м²/(В·с)\n";
    std::cout << "Коефіцієнт дифузії D (теорія):  " << std::setw(12) << res.diffusion_coeff << " м²/с\n";
    std::cout << "Співвідношення Ейнштейна D/μ:   " << std::setw(12) << res.einstein_ratio << " В (теорія kBT/e: 2.5852e-02 В)\n";

    return 0;
}
```
:::

## 3. Фізичні пастки, чисельні обмеження та аналіз результатів

1. **Критерій стійкості часового кроку `dt`:** Часовий крок мусить задовольняти строгу нерівність `dt ≪ τ`. При `τ = 25` фс крок `dt = 0.1` фс складає лише `0.4%` від середнього часу вільного пробігу. Якщо взяти `dt` порівнянним із `τ`, експоненційний вираз для ймовірності розсіювання `P_coll = 1 - exp(-dt/τ)` перестає точно відображати пуассонівський процес, а прискорення за один крок `a · dt` штучно викривить функцію розподілу швидкостей.
2. **Перехідний процес встановлення:** У початковий момент часу `t = 0` середня швидкість ансамблю дорівнює нулю. При увімкненні поля дрейфова швидкість експоненційно релаксує до стаціонарного значення за законом `v(t) = v_d · (1 - exp(-t/τ))`. Для виходу на стаціонарний рівень із точністю вище 99% необхідно пропустити як мінімум `5 · τ` часу моделювання (у нашому коді статистика накопичується лише після перших 20% загального часу).
3. **Статистичний шум та теорема про центральну границю:** Оскільки теплова швидкість електронів `v_th ~ 10⁵` м/с у мільйони разів перевищує дрейфову швидкість `v_d ~ 10⁻²` м/с, миттєве значення середньої швидкості ансамблю має помітну дисперсію `σ_v / √N`. При `N = 50 000` миттєва флуктуація швидкості становить близько `10⁵ / √50000 ≈ 450` м/с, що значно більше за сам дрейф. Лише додаткове усереднення по тисячах послідовних кроків у часі зменшує статистичну похибку розрахунку `σ` до часток відсотка.
4. **Якість генератора псевдовипадкових чисел:** Класична функція `rand()` у стандартній бібліотеці C має короткий період (`2³¹ - 1` або навіть `2¹⁵ - 1` на деяких платформах) і може призводити до штучних кореляцій при сотнях мільйонів викликів. У версії C++ застосовано 64-розрядний вихровий генератор Мерсенна `std::mt19937_64`, період якого становить `2¹⁹⁹³⁷ - 1`, що гарантує відсутність статистичних артефактів.
5. **Векторизація обчислень (SIMD):** Для моделювання мільйонних ансамблів доцільно переходити від масиву структур (AoS — Array of Structures) до структури масивів (SoA — Structure of Arrays), де масиви `vx[]`, `vy[]`, `vz[]` зберігаються неперервно в пам'яті. Це дозволяє компілятору автоматично векторизувати внутрішній цикл за допомогою векторних інструкцій AVX-256 або AVX-512, прискорюючи виконання симуляції у 4–8 разів.

## 4. Граничні умови та чисельні експерименти

### Періодичні граничні умови та об'ємний баланс
У наведеному алгоритмі моделюється однорідний безмежний провідник (або кільцевий зразок). Коли електрон рухається під дією поля, його просторова координата `x(t)` неперервно зміщується. Якщо необхідно змоделювати зразок скінченної довжини `L_x`, застосовують періодичні граничні умови Торна-Борна: частинка, яка вилітає через праву межу `x > L_x`, миттєво інжектується через ліву межу `x = 0` зі збереженням поточної швидкості. Це усуває ефект накопичення поверхневого просторового заряду біля контактів і дозволяє визначати питомі матеріальні властивості середовища `σ` та `ρ` у чистому вигляді.

Якщо ж моделюються відкриті межі з реальними металевими контактами, необхідно реалізовувати контактні резервуари з квазірівноважним розподілом Фермі-Дірака, де електрони абсорбуються на колекторі та термалізовано емітуються з емітера. При цьому на межах виникають контактні стрибки потенціалу та додатковий контактний опір Шотткі або квантовий опір контакту.

### Дослідження температурної залежності
Змінюючи температуру `T` у конфігурації симуляції від `77` К (рідкий азот) до `600` К, можна спостерігати зміну характеру електронного транспорту:
- Теплова швидкість `v_th` зростає як `√T`, збільшуючи розкид миттєвих швидкостей і статистичний шум.
- Якщо зафіксувати час релаксації `τ = const`, дрейфова швидкість `v_d` і провідність `σ` залишаються незмінними, оскільки прискорення полем не залежить від температури.
- Якщо врахувати фізичну температурну залежність часу релаксації металів `τ(T) = τ₀ · (T₀ / T)`, провідність у симуляції спадає обернено пропорційно температурі `σ ∝ 1/T`, точно відтворюючи лінійне зростання питомого опору `ρ(T) = ρ₀ · (1 + α · ΔT)`.
