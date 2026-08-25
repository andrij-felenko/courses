# ⚙️ Обчислення LLR та м'яке демодулювання для BPSK, QPSK та 16-QAM

М'який приймач перетворює прийняті неперервні відліки сигналу на логарифмічні відношення правдоподібностей (LLR) для кожного переданого біта. Без цього кроку жоден м'який декодер — від алгоритму Вітербі до LDPC та турбокодів — не зможе отримати вхідні L-значення.

## Демодуляція BPSK та QPSK

Для BPSK із сигнальним сузір'ям `s ∈ {+1, -1}` LLR каналу обчислюється як відношення правдоподібностей прийнятого аналогового відліку `y`:

```
L_ch = 2 · y / σ²
```

Для QPSK із квадратним кодуванням Грея комплексний символ `s = (s_I + j·s_Q) / √2` складається з двох незалежних компонентів `s_I, s_Q ∈ {+1, -1}`. Завдяки ортогональності синфазної та квадратурної осей LLR кожного з двох бітів обчислюється незалежно вздовж своєї осі. Це означає, що проекція сигналу на синфазну вісь `y_I` несе інформацію винятково про перший біт `b₀`, а проекція на квадратурну вісь `y_Q` — про другий біт `b₁`:

```
L(b₀) = 2·√2 · y_I / σ²
L(b₁) = 2·√2 · y_Q / σ²
```

## Геометрія сузір'я 16-QAM та наближення Max-Log

У сигнальному сузір'ї 16-QAM кожен комплексний символ передає 4 біти `(b₀, b₁, b₂, b₃)`. Квадратна сітка сузір'я розбивається на дві незалежні 4-PAM модуляції по осі `I` (біти `b₀, b₁`) та по осі `Q` (біти `b₂, b₃`). Нормована амплітуда точок уздовж кожної осі набуває значень `{-3, -1, +1, +3} / √10`, що забезпечує середню енергію символу, рівну одиниці.

Для обчислення точного LLR довелося б підраховувати суму експоненціальних функцій за всіма точками сузір'я, які відповідають значенню біта 0, та ділити на суму експонент точок зі значенням біта 1. На практиці в цифрових приймачах використовують тотожність Якобі або наближення Max-Log (англ. *Max-Log approximation*), яке замінює логарифм суми експонент на максимум показових аргументів.

Застосування наближення Max-Log дає прості шматочно-лінійні границі прийняття рішень для кожного біта в сузір'ї 16-QAM з кодом Грея:

```
L(b₀) ≈ (4·√10 / σ²) · y_I
L(b₁) ≈ (2·√10 / σ²) · [ 2/√10 - |y_I| ]
```

Аналіз отриманих шматочно-лінійних функцій показує:
1. **Знаковий біт `b₀`:** LLR змінюється лінійно від відліку `y_I`. Перетин нуля у точці `y_I = 0` розділяє ліву та праву півплощини сузір'я.
2. **Біт амплітуди `b₁`:** LLR є симетричним «будинком» з зламом у точках `|y_I| = 2/√10`. Усередині внутрішньої смуги `|y_I| < 2/√10` значення LLR є додатним (впевненість у біті 0), а поза її межами — від'ємним (впевненість у біті 1).
3. **Біти `b₂` та `b₃`:** Обчислюються за абсолютно симетричними формулами, де замість синфазної координати `y_I` підставляється квадратурна координата `y_Q`.

## Алгоритм вузла перевірки парності Min-Sum LDPC

В ітеративних декодерах LDPC (англ. *Low-Density Parity-Check*) вузли перевірки парності (англ. *check nodes*) постійно обробляють вхідні LLR від суміжних бітових вузлів. Точний алгоритм Belief Propagation вимагає обчислення добутку гіперболічних тангенсів `tanh(L/2)`, що є занадто складним для апаратної реалізації.

Спрощений алгоритм Min-Sum замінює трансцендентні обчислення двома базовими кроками:
- **Обчислення підсумкового знаку:** Знак вихідного LLR для ребра є добутком знаків усіх інших вхідних LLR, пов'язаних із цим перевірочним вузлом. Якщо кількість від'ємних LLR серед інших ребер є парною, підсумковий знак є додатним (`+1`), якщо непарною — від'ємним (`-1`).
- **Знаходження мінімального модуля:** Модуль вихідного LLR дорівнює найменшому модулю серед усіх інших вхідних ребер. Для прискорення обчислень у коді знаходять два найменші модулі `min1` та `min2` у всьому масиві вхідних LLR. Для ребра з найменшим значенням вихідним модулем стає `min2`, а для всіх решти ребер — `min1`.

Це дозволяє зменшити складність обробки перевірочного вузла в 10–20 разів за втрати завадостійкості не більше 0.1 дБ порівняно з точним ймовірнісним декодером.

## Програмна реалізація демодулятора та вузла LDPC

Нижче наведено повну реалізацію м'якого демодулятора BPSK, QPSK, 16-QAM, вузла перевірки парності Min-Sum LDPC та квантизатора LLR мовами C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdint.h>
#include <float.h>

/* Обчислення LLR для одного відліку BPSK */
double bpsk_llr_sample(double y, double sigma2) {
    if (sigma2 <= 1e-12) {
        return (y >= 0.0) ? 1000.0 : -1000.0;
    }
    return 2.0 * y / sigma2;
}

/* М'який демодулятор BPSK для масиву відліків */
void demap_bpsk(const double *y, const double *l_prior, double *l_post,
                size_t num_bits, double sigma2) {
    double scale = 2.0 / (sigma2 > 1e-12 ? sigma2 : 1e-12);
    for (size_t i = 0; i < num_bits; i++) {
        double l_ch = y[i] * scale;
        double prior = (l_prior != NULL) ? l_prior[i] : 0.0;
        l_post[i] = l_ch + prior;
    }
}

/* Демодулятор QPSK (Грей): 1 комплексний символ -> 2 LLR бітів */
void demap_qpsk(const double *y_i, const double *y_q, double *l_out,
                size_t num_symbols, double sigma2) {
    double scale = 2.0 * sqrt(2.0) / (sigma2 > 1e-12 ? sigma2 : 1e-12);
    for (size_t i = 0; i < num_symbols; i++) {
        l_out[2 * i]     = y_i[i] * scale;  /* Біт 0 (In-phase sign) */
        l_out[2 * i + 1] = y_q[i] * scale;  /* Біт 1 (Quadrature sign) */
    }
}

/* Демодулятор 16-QAM (Max-Log, Грей): 1 комплексний символ -> 4 LLR бітів */
void demap_16qam_maxlog(const double *y_i, const double *y_q, double *l_out,
                        size_t num_symbols, double sigma2) {
    double safe_sigma2 = (sigma2 > 1e-12) ? sigma2 : 1e-12;
    double sqrt10 = sqrt(10.0);
    double c1 = 4.0 * sqrt10 / safe_sigma2;
    double c2 = 2.0 * sqrt10 / safe_sigma2;
    double threshold = 2.0 / sqrt10;

    for (size_t i = 0; i < num_symbols; i++) {
        double yi = y_i[i];
        double yq = y_q[i];

        /* Синфазна вісь I */
        l_out[4 * i + 0] = c1 * yi;
        l_out[4 * i + 1] = c2 * (threshold - fabs(yi));

        /* Квадратурна вісь Q */
        l_out[4 * i + 2] = c1 * yq;
        l_out[4 * i + 3] = c2 * (threshold - fabs(yq));
    }
}

/* Вузол перевірки парності Min-Sum для LDPC декодера (обновлення L_ext) */
void ldpc_min_sum_check_node(const double *l_in, double *l_ext_out, size_t degree) {
    if (degree < 2) return;

    /* Обчислення загального добутку знаків та двох найменших модулів */
    int global_sign = 1;
    double min1 = DBL_MAX;
    double min2 = DBL_MAX;
    size_t min1_idx = 0;

    for (size_t i = 0; i < degree; i++) {
        if (l_in[i] < 0.0) {
            global_sign = -global_sign;
        }
        double abs_val = fabs(l_in[i]);
        if (abs_val < min1) {
            min2 = min1;
            min1 = abs_val;
            min1_idx = i;
        } else if (abs_val < min2) {
            min2 = abs_val;
        }
    }

    /* Формування вихідного LLR для кожного ребра */
    for (size_t i = 0; i < degree; i++) {
        int edge_sign = (l_in[i] < 0.0) ? -global_sign : global_sign;
        double min_mag = (i == min1_idx) ? min2 : min1;
        l_ext_out[i] = (double)edge_sign * min_mag;
    }
}

/* Квантизація LLR у 8-бітне ціле зі знаком [-127, 127] */
int8_t quantize_llr(double llr, double scale_factor) {
    double scaled = llr * scale_factor;
    if (scaled > 127.0) return 127;
    if (scaled < -127.0) return -127;
    return (int8_t)round(scaled);
}
```
```cpp
#include <vector>
#include <complex>
#include <cmath>
#include <cstdint>
#include <algorithm>
#include <span>
#include <numbers>
#include <limits>

class SoftDemapper {
public:
    explicit SoftDemapper(double noise_variance)
        : sigma2_(std::max(noise_variance, 1e-12)) {}

    // LLR для BPSK з додаванням апріорної інформації
    [[nodiscard]] std::vector<double> demap_bpsk(
        std::span<const double> rx_symbols,
        std::span<const double> prior_llr = {}) const 
    {
        const double scale = 2.0 / sigma2_;
        std::vector<double> post_llr(rx_symbols.size());

        for (size_t i = 0; i < rx_symbols.size(); ++i) {
            double prior = (i < prior_llr.size()) ? prior_llr[i] : 0.0;
            post_llr[i] = rx_symbols[i] * scale + prior;
        }
        return post_llr;
    }

    // LLR для QPSK (карта Грея)
    [[nodiscard]] std::vector<double> demap_qpsk(
        std::span<const std::complex<double>> rx_symbols) const 
    {
        const double scale = 2.0 * std::numbers::sqrt2 / sigma2_;
        std::vector<double> bit_llrs;
        bit_llrs.reserve(rx_symbols.size() * 2);

        for (const auto& sym : rx_symbols) {
            bit_llrs.push_back(sym.real() * scale);
            bit_llrs.push_back(sym.imag() * scale);
        }
        return bit_llrs;
    }

    // LLR для 16-QAM (Max-Log наближення, карта Грея)
    [[nodiscard]] std::vector<double> demap_16qam_maxlog(
        std::span<const std::complex<double>> rx_symbols) const 
    {
        constexpr double sqrt10 = 3.1622776601683795;
        const double c1 = 4.0 * sqrt10 / sigma2_;
        const double c2 = 2.0 * sqrt10 / sigma2_;
        const double threshold = 2.0 / sqrt10;

        std::vector<double> bit_llrs;
        bit_llrs.reserve(rx_symbols.size() * 4);

        for (const auto& sym : rx_symbols) {
            const double yi = sym.real();
            const double yq = sym.imag();

            bit_llrs.push_back(c1 * yi);
            bit_llrs.push_back(c2 * (threshold - std::abs(yi)));
            bit_llrs.push_back(c1 * yq);
            bit_llrs.push_back(c2 * (threshold - std::abs(yq)));
        }
        return bit_llrs;
    }

    // Вузол перевірки парності Min-Sum LDPC
    [[nodiscard]] static std::vector<double> min_sum_check_node(
        std::span<const double> l_in) 
    {
        if (l_in.size() < 2) return {};

        int global_sign = 1;
        double min1 = std::numeric_limits<double>::max();
        double min2 = std::numeric_limits<double>::max();
        size_t min1_idx = 0;

        for (size_t i = 0; i < l_in.size(); ++i) {
            if (l_in[i] < 0.0) {
                global_sign = -global_sign;
            }
            double abs_val = std::abs(l_in[i]);
            if (abs_val < min1) {
                min2 = min1;
                min1 = abs_val;
                min1_idx = i;
            } else if (abs_val < min2) {
                min2 = abs_val;
            }
        }

        std::vector<double> l_ext(l_in.size());
        for (size_t i = 0; i < l_in.size(); ++i) {
            int edge_sign = (l_in[i] < 0.0) ? -global_sign : global_sign;
            double min_mag = (i == min1_idx) ? min2 : min1;
            l_ext[i] = static_cast<double>(edge_sign) * min_mag;
        }
        return l_ext;
    }

    // 8-бітна квантизація LLR для апаратного декодера
    [[nodiscard]] static int8_t quantize(double llr, double scale_factor) {
        double val = std::round(llr * scale_factor);
        return static_cast<int8_t>(std::clamp(val, -127.0, 127.0));
    }

private:
    double sigma2_;
};
```
:::

## Покроковий приклад та аналіз крайових випадків

Простежимо виконання обчислень для конкретних числових значень.

**Приклад 1: Демодуляція 16-QAM.** Нехай дисперсія шуму становить `σ² = 0.4`, а прийнятий символ має координати `y = +0.7 + j·(-0.1)`.
- Для синфазної осі `y_I = +0.7`:
  - `L(b₀) = c₁ · y_I = (4·√10 / 0.4) · 0.7 = 31.62 · 0.7 = +22.13` (впевнено біт 0).
  - `L(b₁) = c₂ · (2/√10 - |y_I|) = (2·√10 / 0.4) · (0.6325 - 0.7000) = 15.81 · (-0.0675) = -1.07` (слабко біт 1).
- Для квадратурної осі `y_Q = -0.1`:
  - `L(b₂) = c₁ · y_Q = 31.62 · (-0.1) = -3.16` (біт 1).
  - `L(b₃) = c₂ · (2/√10 - |y_Q|) = 15.81 · (0.6325 - 0.1000) = 15.81 · 0.5325 = +8.42` (впевнено біт 0).

**Приклад 2: Вузол перевірки LDPC.** Нехай на перевірочний вузол ступеня 3 прийшли три LLR від бітових вузлів: `L_in = [+4.5, -1.2, +2.8]`.
- Добуток знаків: `(+) · (-) · (+) = -1` (непарна кількість мінусів).
- Модулі: `[4.5, 1.2, 2.8]`. Найменший модуль `min1 = 1.2` (індекс 1), другий мінімум `min2 = 2.8`.
- Обчислення вихідних зовнішніх LLR:
  - Для ребра 0 (знак інших `(-)·(+) = -`): `L_ext[0] = -min1 = -1.2`.
  - Для ребра 1 (знак інших `(+)·(+) = +`): `L_ext[1] = +min2 = +2.8` (використовується другий мінімум).
  - Для ребра 2 (знак інших `(+)·(-) = -`): `L_ext[2] = -min1 = -1.2`.

## Ключові нюанси реалізації та апаратні пастки

1. **Захист від нульового шуму:** При `σ² → 0` множник `2/σ²` прямує до нескінченності. В реальному коді обов'язково ставлять нижню межу на дисперсію `σ² ≥ 1e-12`, щоб уникнути ділення на нуль та числової нестабільності.
2. **Динамічний діапазон та насичення:** В ітеративних декодерах (LDPC / Turbo) значні значення LLR (`|L| > 20`) швидко призводять до виродження обчислень у `tanh` або експонентах. Квантування з обмеженням (`[-127, +127]` або `[-7, +7]`) не тільки економить пам'ять, а й стабілізує роботу ітеративного алгоритму.
3. **Оцінка шуму:** Помилка в оцінці `σ²` зміщує масштаб LLR. Для жорсткого рішення (знаку) масштаб байдужий, але для м'якого обміну підказками між ітераціями правильний масштаб `σ²` є критичним.
4. **Масштабування Min-Sum:** Алгоритм Min-Sum трохи переоцінює модуль вихідного LLR. На практиці вихідне значення множать на нормалізуючий коефіцієнт `α ≈ 0.75` або віднімають константу (англ. *Normalized / Offset Min-Sum*), що усуває цей зсув і піднімає завадостійкість майже до точного алгоритму Belief Propagation.
