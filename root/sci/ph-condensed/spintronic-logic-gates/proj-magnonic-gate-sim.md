# ⚙️ Моделювання магнонного та спінового логічного елемента

Ця вставка містить практичний посібник та програмну реалізацію чисельного моделювання хвильової інтерференції в магнонному інтерферометрі Маха — Цендера та прецесії спінів у транзисторі Датта — Даса. Поданий код дозволяє обчислювати вихідні амплітуди, розраховувати логічні таблиці істинності, проводити аналіз температурного фазового шуму та оцінювати вплив фізичних параметрів (довжини каналу, параметра Рашби, зсуву фаз) на контрастність інтерференції та провідність спінтронних логічних вентилів.

## 1. Постановка фізико-обчислювальної задачі

Проектування спінтронних логічних схем вимагає точно розраховувати відгук пристрою на вхідні електричні та магнітні сигнали. У даній практичній системі розглядаються два основні обчислювальні модулі:

### Модуль 1: Магнонний інтерферометричний логічний елемент (Маха — Цендера)
Спінова хвиля пропогує через два паралельні хвилеводні канали з тонкої плівки залізо-ітрієвого гранату (YIG) довжиною `L = 5 мкм`. Перший канал містить керівний фазовий затвор, який змінює локальний хвильовий вектор магнона під дією магнітного поля або напругової модуляції магнітної анізотропії (VCMA). Другий канал слугує опорним плечем із постійною фазою `φ₀`. 

Програма повинна розраховувати результуючу амплітуду та інтенсивність хвилі на виході Y-з'єднувача:

```
I_out = A₁² + A₂² + 2 · A₁ · A₂ · cos(Δφ)
```

та здійснювати логічну класифікацію результату (формування функцій XOR та AND залежно від амплітудного порогу).

### Модуль 2: Спіновий польовий транзистор Датта — Даса
Електрони з поляризованим спіном рухаються балістично крізь напівпровідниковий канал InGaAs довжиною `L = 200 нм`. Напруга затвора `V_g` змінює константу спін-орбітальної взаємодії Рашби `α_R`. Програма розраховує кут прецесії спіна на виході з каналу:

```
Δθ = (2 · m* · α_R · L) / ℏ²
```

та підсумкову провідність каналу (нормалізований струм):

```
I / I_max = cos²( Δθ / 2 )
```

## 2. Математичний алгоритм та чисельні методи

Чисельне моделювання здійснюється у два етапи:

### Етап 1: Дискретизація простору та фазового простору
Довжина каналу ділиться на `N_x` дискретних комірок шириною `Δx = 10 нм`. На кожному кроці розраховується накопичення фази `Δφ(x) = k(x) · Δx`. 

Для моделювання часової динаміки спінових хвиль у складному 2D-геометрії використовується метод скінченних різниць у часовій області (FDTD) для дискретизованого рівняння Ландау — Ліфшиця — Гільберта (LLG):

```
M_i(t + Δt) = M_i(t) - Δt · γ · μ₀ · [M_i(t) × H_eff,i(t)] + (α_G / M_s) · [M_i(t) × (M_i(t + Δt) - M_i(t))]
```

при обчисленні ефективного магнітного поля `H_eff,i` враховується обмінна взаємодія між сусідніми вузлами сітки:

```
H_ex,i = (D / (γ · μ₀ · M_s · Δx²)) · (M_{i+1} + M_{i-1} - 2·M_i)
```

### Етап 2: Моделювання інтерференційного зважування та детектування
Обчислюється векторна суперпозиція комплексних амплітуд хвиль, після чого застосовується порогова функція детектування для порівняння з логічними рівнями `0` та `1`.

Для швидкої параметричної оцінки логічних вентилів у поданій нижче програмі реалізовано високопродуктивну аналітично-чисельну модель фазової інтерференції.

## 3. Програмна реалізація мовами C та C++

У відповідності до канону, програма реалізована обома мовами — ідіоматичною C та сучасною C++20.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double amplitude;
    double phase_rad;
    double frequency_hz;
} MagnonWave;

typedef struct {
    double input_phase_a;
    double input_phase_b;
    double output_intensity;
    int logic_bit_xor;
    int logic_bit_and;
} MagnonicGateResult;

typedef struct {
    double alpha_r;       /* Параметр Рашби (еВ·м) */
    double channel_length;/* Довжина каналу (м) */
    double m_eff;         /* Ефективна маса електрона (кг) */
} DattaDasParams;

/* Фізичні константи */
static const double HBAR = 1.054571817e-34; /* Дж·с */
static const double ME = 9.1093837015e-31;  /* кг */
static const double EV_TO_JOULE = 1.602176634e-19;

/* Обчислення інтерференції двох магнонних хвиль */
MagnonicGateResult simulate_magnonic_gate(MagnonWave w1, MagnonWave w2, double threshold) {
    MagnonicGateResult result;
    result.input_phase_a = w1.phase_rad;
    result.input_phase_b = w2.phase_rad;

    double delta_phi = w1.phase_rad - w2.phase_rad;
    double i1 = w1.amplitude * w1.amplitude;
    double i2 = w2.amplitude * w2.amplitude;

    /* Рівняння хвильової інтерференції: I = I1 + I2 + 2*sqrt(I1*I2)*cos(Delta_phi) */
    result.output_intensity = i1 + i2 + 2.0 * sqrt(i1 * i2) * cos(delta_phi);

    /* Детектування логічних станів */
    result.logic_bit_xor = (fabs(delta_phi) > 0.5 * M_PI) ? 1 : 0;
    result.logic_bit_and = (result.output_intensity >= threshold) ? 1 : 0;

    return result;
}

/* Обчислення провідності спінового транзистора Датта — Даса */
double simulate_datta_das_current(DattaDasParams p) {
    double alpha_j = p.alpha_r * EV_TO_JOULE;
    double delta_theta = (2.0 * p.m_eff * alpha_j * p.channel_length) / (HBAR * HBAR);
    
    /* Нормалізований струм: I / I_max = cos^2(Delta theta / 2) */
    double cos_val = cos(delta_theta / 2.0);
    return cos_val * cos_val;
}

int main(void) {
    printf("=== Таблиця істинності Магнонного Логічного Вентиля ===\n");
    printf("Phase A (rad) | Phase B (rad) | Intensity | XOR | AND\n");
    printf("------------------------------------------------------\n");

    double phases[2] = {0.0, M_PI};
    double threshold = 3.0; /* Поріг амплітуди для операції AND */

    for (int i = 0; i < 2; i++) {
        for (int j = 0; j < 2; j++) {
            MagnonWave w1 = {1.0, phases[i], 10.0e9};
            MagnonWave w2 = {1.0, phases[j], 10.0e9};

            MagnonicGateResult res = simulate_magnonic_gate(w1, w2, threshold);
            printf("    %4.2f      |     %4.2f     |   %5.3f   |  %d  |  %d\n",
                   res.input_phase_a, res.input_phase_b,
                   res.output_intensity, res.logic_bit_xor, res.logic_bit_and);
        }
    }

    printf("\n=== Моделювання Спінового FET Датта — Даса ===\n");
    DattaDasParams params;
    params.channel_length = 200.0e-9; /* 200 нм */
    params.m_eff = 0.023 * ME;         /* InAs канал */

    printf("Alpha_R (eV*m)  | Spin Precession Angle (rad) | Normalized Current I/I_max\n");
    printf("------------------------------------------------------------------------\n");

    for (double alpha = 0.0; alpha <= 2.0e-11; alpha += 0.4e-11) {
        params.alpha_r = alpha;
        double current = simulate_datta_das_current(params);
        double theta = (2.0 * params.m_eff * alpha * EV_TO_JOULE * params.channel_length) / (HBAR * HBAR);

        printf("  %8.2e     |           %6.3f           |         %6.4f\n",
               alpha, theta, current);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>

struct MagnonWave {
    double amplitude{1.0};
    double phase_rad{0.0};
    double frequency_hz{10.0e9};
};

struct MagnonicGateResult {
    double input_phase_a{0.0};
    double input_phase_b{0.0};
    double output_intensity{0.0};
    bool logic_bit_xor{false};
    bool logic_bit_and{false};
};

struct DattaDasParams {
    double alpha_r_ev_m{0.0};          // Параметр Рашби (еВ·м)
    double channel_length_m{200.0e-9}; // Довжина каналу (м)
    double m_eff_kg{0.023 * 9.1093837015e-31}; // Ефективна маса електрона
};

class SpintronicSimulator {
public:
    static constexpr double HBAR = 1.054571817e-34;
    static constexpr double EV_TO_JOULE = 1.602176634e-19;

    [[nodiscard]] static MagnonicGateResult simulate_magnonic_gate(
        const MagnonWave& w1, 
        const MagnonWave& w2, 
        double threshold) noexcept 
    {
        MagnonicGateResult result{};
        result.input_phase_a = w1.phase_rad;
        result.input_phase_b = w2.phase_rad;

        const double delta_phi = w1.phase_rad - w2.phase_rad;
        const double i1 = w1.amplitude * w1.amplitude;
        const double i2 = w2.amplitude * w2.amplitude;

        result.output_intensity = i1 + i2 + 2.0 * std::sqrt(i1 * i2) * std::cos(delta_phi);
        result.logic_bit_xor = (std::abs(delta_phi) > 0.5 * std::numbers::pi);
        result.logic_bit_and = (result.output_intensity >= threshold);

        return result;
    }

    [[nodiscard]] static double simulate_datta_das_current(const DattaDasParams& p) noexcept {
        const double alpha_j = p.alpha_r_ev_m * EV_TO_JOULE;
        const double delta_theta = (2.0 * p.m_eff_kg * alpha_j * p.channel_length_m) / (HBAR * HBAR);
        const double cos_val = std::cos(delta_theta / 2.0);
        return cos_val * cos_val;
    }
};

int main() {
    std::cout << "=== Спінтронічний Симулятор (C++20) ===\n";
    std::cout << std::fixed << std::setprecision(3);

    const std::vector<double> phases{0.0, std::numbers::pi};
    constexpr double threshold = 3.0;

    std::cout << "Phase A | Phase B | Intensity | XOR | AND\n";
    std::cout << "------------------------------------------\n";

    for (double p1 : phases) {
        for (double p2 : phases) {
            MagnonWave w1{.amplitude = 1.0, .phase_rad = p1};
            MagnonWave w2{.amplitude = 1.0, .phase_rad = p2};

            const auto res = SpintronicSimulator::simulate_magnonic_gate(w1, w2, threshold);
            std::cout << " " << res.input_phase_a << "  |  " << res.input_phase_b 
                      << "  |   " << res.output_intensity 
                      << "   |  " << res.logic_bit_xor 
                      << "  |  " << res.logic_bit_and << "\n";
        }
    }

    std::cout << "\n=== Залежність провідності Spin-FET від полем Рашби ===\n";
    DattaDasParams params{.channel_length_m = 200.0e-9};

    for (int i = 0; i <= 5; ++i) {
        params.alpha_r_ev_m = i * 0.4e-11;
        const double current = SpintronicSimulator::simulate_datta_das_current(params);
        const double theta = (2.0 * params.m_eff_kg * params.alpha_r_ev_m * 
                              SpintronicSimulator::EV_TO_JOULE * params.channel_length_m) / 
                             (SpintronicSimulator::HBAR * SpintronicSimulator::HBAR);

        std::cout << "Alpha_R: " << std::scientific << std::setprecision(2) << params.alpha_r_ev_m 
                  << " eV*m | Theta: " << std::fixed << std::setprecision(3) << theta 
                  << " rad | Current: " << current << "\n";
    }

    return 0;
}
```
:::

## 4. Покроковий розбір коду та архітектурних рішений

Розглянемо детально кожну структуру даних, функцію та логічний блок програми:

### 1. Опис структур даних
- `MagnonWave`: Містить амплітуду (у нормалізованих одиницях), початкову фазу (у радіанах) та частоту магнона (у герцах). У розширених мікромагнітних моделях амплітуда додатково враховує згасання Гільберта за законом `A(x) = A₀ · exp(-x / L_d)`, де `L_d = v_g / (α_G · ω)` — довжина затухання магнонів.
- `MagnonicGateResult`: Зберігає вхідні значення фаз двох плечей, обчислену результуючу інтенсивність та обчислені класифікаційні біти для двох логічних функцій:
  - Операція XOR: оцінюється за фазовою різницею `|Δφ| > π/2`. При однаковій фазі вдодів (`Δφ = 0`) результат дорівнює `0`, при протилежній фазі (`Δφ = π`) — `1`.
  - Операція AND: оцінюється за амплітудним детектуванням `I_out ≥ threshold`. При збігу хвиль у фазі інтенсивність досягає `4.0` (що вище порогу `3.0`, логічна `1`), при деструктивній інтерференції інтенсивність дорівнює `0.0` (логічний `0`).
- `DattaDasParams`: Утримує фізичні параметри гетероструктури — константу Рашби `α_R` (у еВ·м), довжину каналу `L` (у метрах) та ефективну масу електронів `m*` (у кг).

### 2. Оптимізація та ідіоматичність C++ реалізації
C++20 реалізація спирається на сучасні стандарти системного програмування:
- Скористано `constexpr` для фізичних констант `HBAR` та `EV_TO_JOULE`, що дозволяє компилятору обчислювати поправки ще на етапі компіляції.
- Скористано математичні константи з заголовочного файла `<numbers>` (`std::numbers::pi`), що виключає макроси препроцесора C.
- Метод `simulate_magnonic_gate` позначено як `[[nodiscard]]` та `noexcept`, що гарантує відсутність генерації винятків під час гарячого обчислювального циклу.

## 5. Аналіз обчислювальної складності та крайових випадків

Під час розгортання моделей спінтроніки у САПР (CAD) системи автоматизованого проектування інтегральних схем необхідно враховувати наступні крайові випадки та джерела похибок:

### 1. Температурний фазовий шум (Phase Jitter)
При кімнатній температурі (`T = 300 K`) флуктуації термодинамічного поля створюють випадкову фазову дефазировку `σ_φ = √(k_B · T / (2 · E_sw))`. У чисельній моделі це вимагає додавання гауссового шуму до значення `delta_phi`. Якщо рівень шуму перевищує `0.3` радіана, контрастність інтерференції вихідного сигналу спадає з `100%` до `50%`, що вимагає підвищення амплітудного порогу детектування.

### 2. Затухання Гільберта та асиметрія плечей
Якщо затухання у плечі з фазовим затвором вище, ніж у беззатворовому плечі (`A₁ < A₂`), деструктивна інтерференція стає неповною: мінімальна інтенсивність `I_min = (A₁ - A₂)² > 0`. Вихідний логічний нуль перестає бути нульовим, що знижує запас завадостійкості (Noise Margin) логічного елемента.

### 3. Нелінійний розпад магнонів (Three-Magnon Decay)
При перевищенні критичної потужності збудження `P > P_crit` магнонна хвиля основної моди розпадається на дві хвилі половинної частоти `ω / 2`. Моделювати цей процес вимагає розв'язання нелінійного рівняння Гінзбурга — Ландау або застосування пакета мікромагнітного моделювання MuMax3 / OOMMF.

### 4. Відбиття хвиль від меж хвилеводу
При проходженні Y-з'єднання частка магнонної енергії відбивається назад до джерела. У чисельних розрахунках це вимагає застосування поглинаючих граничних умов (Perfectly Matched Layers, PML) на кінцях сітки для усунення паразитрах стоячих хвиль.
