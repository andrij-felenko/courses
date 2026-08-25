# ⚙️ Практичний пошук розв'язків та моделювання діофантових рівнянь

Алгоритмічна нерозв'язність десятої проблеми Гільберта встановлює абсолютну теоретичну межу: не існує універсального алгоритму, який був би здатний за скінченний час визначити наявність чи відсутність цілих розв'язків для довільного поліноміального рівняння. Проте в інженерній практиці, комп'ютерній алгебрі, криптографії, сучасних SMT-солверах та верифікації програм виникає протилежне завдання: для конкретних класів діофантових рівнянь побудувати ефективні числові процедури, які знаходять найменші додатні розв'язки, розгортають експоненційні ланцюжки генерації, емулюють машини регістрів або систематично сканують багатовимірні простори пошуку за допомогою комбінації евристичного відсікання та шаруватого перебору.

Нижче детально розібрано архітектуру, математичне обґрунтування та програмну реалізацію шести ключових алгоритмічних механізмів: точного розв'язувача нелінійних рівнянь Пелля `x² − D·y² = 1` через розклад у неперервні дроби, канонічного обчислювача розріджених поліномів багатьох змінних, інтервального сита для відсікання підпросторів, модульного сита локально-глобального фільтрування, прямої діофантової емуляції лічильникових машин Мінського та універсального рушія обмеженого пошуку коренів у багатовимірному гіперкубі методом довблення (*dovetailing*).

---

## 1. Теорія та алгоритм розв'язання рівнянь Пелля

Рівняння Пелля `x² − D·y² = 1` для додатного цілого числа `D`, що не є повним квадратом, є найпростішим нетривіальним прикладом нелінійного діофантового рівняння. Геометрично воно описує гіперболу, а алгебраїчно — групу оборотних елементів (одиниць) дійсного квадратичного поля `ℚ(√D)`.

Множина всіх цілочисельних розв'язків утворює нескінченну мультиплікативну групу, яка породжується єдиним **фундаментальним розв'язком** `(x₁, y₁)` — парою з найменшими додатними значеннями координат `x > 1, y > 0`.

### Зв'язок із неперервними дробами
Найефективнішим методом знаходження фундаментального розв'язку є алгоритм розкладу квадратного кореня `√D` у нескінченний періодичний неперервний дріб:

```
√D = [a₀; (a₁, a₂, ..., a_{L-1}, 2a₀)]
```

де `a₀ = ⌊√D⌋`, а послідовність `(a₁, ..., a_{L-1}, 2a₀)` є найкоротшим періодом довжини `L`.

З теорії діофантових наближень (теорема Лагранжа) відомо, що будь-який розв'язок рівняння `x² − D·y² = 1` відповідає деякому **підхідному дробу** `pₖ / qₖ` до числа `√D`. Підхідні дроби обчислюються за класичними рекурентними формулами другого порядку:

```
p₋₂ = 0,   p₋₁ = 1,   pₖ = aₖ · pₖ₋₁ + pₖ₋₂
q₋₂ = 1,   q₋₁ = 0,   qₖ = aₖ · qₖ₋₁ + qₖ₋₂
```

Фундаментальний розв'язок визначається парністю довжини періоду `L`:
1. Якщо довжина періоду `L` є **парною**, фундаментальний розв'язок досягається наприкінці першого періоду:
   ```
   x₁ = p_{L−1},   y₁ = q_{L−1}
   ```
2. Якщо довжина періоду `L` є **непарною**, підхідний дріб `p_{L−1} / q_{L−1}` дає розв'язок від'ємного рівняння Пелля `x² − D·y² = −1`. Щоб отримати розв'язок вихідного рівняння зі знаком `+1`, необхідно пройти період двічі:
   ```
   x₁ = p_{2L−1},   y₁ = q_{2L−1}
   ```

### Детальний покроковий алгоритм розкладу
Щоб уникнути втрати точності через операції з плаваючою комою, генерація коефіцієнтів `aₖ` виконується виключно в цілих числах за допомогою трьох допоміжних змінних `(mₖ, dₖ, aₖ)`:

```
m₀ = 0,     d₀ = 1,     a₀ = ⌊√D⌋
mₖ₊₁ = dₖ · aₖ − mₖ
dₖ₊₁ = (D − mₖ₊₁²) / dₖ
aₖ₊₁ = ⌊(a₀ + mₖ₊₁) / dₖ₊₁⌋
```

Усі проміжні ділення виконуються націло без залишку завдяки алгебраїчній замкненості квадратичних ірраціональностей.

### Числовий трасувальний приклад для D = 13
Розглянемо покроковий розклад для `D = 13` (`a₀ = 3`, `√13 ≈ 3.60555`):
- Крок 0: `m₀ = 0`, `d₀ = 1`, `a₀ = 3`, `p₀ = 3`, `q₀ = 1`. Перевірка: `3² − 13·1² = 9 − 13 = −4 ≠ 1`.
- Крок 1: `m₁ = 1·3 − 0 = 3`, `d₁ = (13 − 9)/1 = 4`, `a₁ = ⌊(3 + 3)/4⌋ = 1`. `p₁ = 1·3 + 1 = 4`, `q₁ = 1·1 + 0 = 1`. Перевірка: `4² − 13·1² = 16 − 13 = 3`.
- Крок 2: `m₂ = 4·1 − 3 = 1`, `d₂ = (13 − 1)/4 = 3`, `a₂ = ⌊(3 + 1)/3⌋ = 1`. `p₂ = 1·4 + 3 = 7`, `q₂ = 1·1 + 1 = 2`. Перевірка: `7² − 13·2² = 49 − 52 = −3`.
- Крок 3: `m₃ = 3·1 − 1 = 2`, `d₃ = (13 − 4)/3 = 3`, `a₃ = ⌊(3 + 2)/3⌋ = 1`. `p₃ = 1·7 + 4 = 11`, `q₃ = 1·2 + 1 = 3`. Перевірка: `11² − 13·3² = 121 − 117 = 4`.
- Крок 4: `m₄ = 3·1 − 2 = 1`, `d₄ = (13 − 1)/3 = 4`, `a₄ = ⌊(3 + 1)/4⌋ = 1`. `p₄ = 1·11 + 7 = 18`, `q₄ = 1·3 + 2 = 5`. Перевірка: `18² − 13·5² = 324 − 325 = −1` (розв'язок від'ємного рівняння).
- Період `L = 5` непарний. Продовжуючи обчислення до кроку `2L − 1 = 9`, отримуємо фундаментальний розв'язок:
  `p₉ = 649`, `q₉ = 180`. Перевірка: `649² − 13·180² = 421201 − 421200 = 1`.

### Генерація вищих розв'язків
Після того як фундаментальний розв'язок `(x₁, y₁)` знайдено, усі наступні розв'язки `(xₙ, yₙ)` для `n ≥ 2` обчислюються без повторного звернення до неперервних дробів — за формулою піднесення фундаментальної одиниці `x₁ + y₁√D` до `n`-го степеня:

```
xₙ₊₁ + yₙ₊₁√D = (x₁ + y₁√D) · (xₙ + yₙ√D)
```

Перемножуючи та розкриваючи дужки, отримуємо лінійний матричний крок:

```
xₙ₊₁ = x₁ · xₙ + D · y₁ · yₙ
yₙ₊₁ = y₁ · xₙ + x₁ · yₙ
```

Ці розв'язки зростають як точна геометрична прогресія, забезпечуючи той самий експоненційний стрибок, на якому базується теорема ДПРМ.

### Реалізація розв'язувача Пелля

Нижче наведено паралельну реалізацію алгоритму неперервних дробів мовами C та C++. Оскільки проміжні координати розв'язків навіть для невеликих `D` швидко перевищують 64 біти, у коді використано 128-бітні цілі типи (`unsigned __int128`).

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

typedef unsigned __int128 uint128_t;

typedef struct {
    uint128_t x;
    uint128_t y;
    bool found;
} PellSolution;

void print_u128(uint128_t val) {
    if (val == 0) {
        printf("0");
        return;
    }
    char buf[64];
    int idx = 0;
    while (val > 0) {
        buf[idx++] = '0' + (int)(val % 10);
        val /= 10;
    }
    for (int i = idx - 1; i >= 0; --i) {
        putchar(buf[i]);
    }
}

PellSolution pell_solve_fundamental(uint64_t d) {
    PellSolution res = {0, 0, false};
    uint64_t a0 = (uint64_t)sqrt((double)d);
    if (a0 * a0 == d) {
        return res; // D є повним квадратом, нетривіальних розв'язків нема
    }

    uint64_t m = 0;
    uint64_t d_denom = 1;
    uint64_t a = a0;

    uint128_t p_prev2 = 0, p_prev1 = 1, p_curr = a0;
    uint128_t q_prev2 = 1, q_prev1 = 0, q_curr = 1;

    while (1) {
        if (p_curr * p_curr - (uint128_t)d * q_curr * q_curr == 1) {
            res.x = p_curr;
            res.y = q_curr;
            res.found = true;
            return res;
        }

        m = d_denom * a - m;
        d_denom = (d - m * m) / d_denom;
        a = (a0 + m) / d_denom;

        p_prev2 = p_prev1;
        p_prev1 = p_curr;
        p_curr = (uint128_t)a * p_prev1 + p_prev2;

        q_prev2 = q_prev1;
        q_prev1 = q_curr;
        q_curr = (uint128_t)a * q_prev1 + q_prev2;
    }
}

PellSolution pell_next_solution(PellSolution fund, PellSolution prev, uint64_t d) {
    PellSolution next;
    next.x = fund.x * prev.x + (uint128_t)d * fund.y * prev.y;
    next.y = fund.y * prev.x + fund.x * prev.y;
    next.found = true;
    return next;
}
```
```cpp
#include <iostream>
#include <vector>
#include <optional>
#include <cmath>
#include <string>
#include <algorithm>

using uint128_t = unsigned __int128;

struct PellPair {
    uint128_t x{0};
    uint128_t y{0};

    [[nodiscard]] std::string to_string_x() const {
        return format_u128(x);
    }
    [[nodiscard]] std::string to_string_y() const {
        return format_u128(y);
    }

private:
    static std::string format_u128(uint128_t val) {
        if (val == 0) return "0";
        std::string s;
        while (val > 0) {
            s.push_back(static_cast<char>('0' + (val % 10)));
            val /= 10;
        }
        std::reverse(s.begin(), s.end());
        return s;
    }
};

class PellSolver {
public:
    static std::optional<PellPair> find_fundamental(uint64_t d) noexcept {
        const auto a0 = static_cast<uint64_t>(std::sqrt(d));
        if (a0 * a0 == d) {
            return std::nullopt; // Повний квадрат не має розв'язків
        }

        uint64_t m = 0;
        uint64_t d_denom = 1;
        uint64_t a = a0;

        uint128_t p_prev2 = 0, p_prev1 = 1, p_curr = a0;
        uint128_t q_prev2 = 1, q_prev1 = 0, q_curr = 1;

        while (true) {
            if (p_curr * p_curr - static_cast<uint128_t>(d) * q_curr * q_curr == 1) {
                return PellPair{p_curr, q_curr};
            }

            m = d_denom * a - m;
            d_denom = (d - m * m) / d_denom;
            a = (a0 + m) / d_denom;

            p_prev2 = p_prev1;
            p_prev1 = p_curr;
            p_curr = static_cast<uint128_t>(a) * p_prev1 + p_prev2;

            q_prev2 = q_prev1;
            q_prev1 = q_curr;
            q_curr = static_cast<uint128_t>(a) * q_prev1 + q_prev2;
        }
    }

    static PellPair next_power(const PellPair& fund, const PellPair& prev, uint64_t d) noexcept {
        return PellPair{
            fund.x * prev.x + static_cast<uint128_t>(d) * fund.y * prev.y,
            fund.y * prev.x + fund.x * prev.y
        };
    }
};
```
:::

---

## 2. Канонічне представлення розріджених поліномів багатьох змінних

При аналізі довільних діофантових предикатів многочлен задається не як чорний ящик `f(x)`, а як розріджена сума мономів:

```
P(x₁, ..., xₘ) = ∑ [k=1..K] cₖ · x₁^{e_{k,1}} · x₂^{e_{k,2}} · ... · xₘ^{e_{k,m}}
```

де `cₖ ∈ ℤ` — цілий коефіцієнт, а кортеж `(e_{k,1}, ..., e_{k,m})` — вектор невід'ємних степенів. Таке представлення забезпечує компактне збереження в пам'яті, швидке паралельне обчислення значення на векторі аргументів та автоматичне виділення часткових похідних для градієнтного аналізу.

### Ефективність кешу та векторизація
Зберігання мономів у вигляді суцільного масиву структур (`Array of Structures` або `Structure of Arrays`) забезпечує лінійний доступ до пам'яті без непрямих стрибків за вказівниками. На відміну від деревоподібних абстрактних синтаксичних дерев (AST), де кожен вузол породжує окрему алокацію в динамічній пам'яті, послідовне обчислення розріджених мономів у компактному буфері дозволяє процесору завантажувати дані безпосередньо в L1-кеш інструкцій та даних. Крім того, сучасні оптимізуючі компілятори здатні виконувати автоматичну векторизацію (SIMD AVX2/AVX-512) для одночасного множення кількох змінних.

### Реалізація розрідженого полінома

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    int64_t coeff;
    uint8_t exponents[8]; // Степені для до 8 змінних
} SparseMonomial;

typedef struct {
    size_t num_vars;
    size_t num_terms;
    SparseMonomial terms[32];
} SparsePoly;

int64_t sparse_poly_eval(const SparsePoly* p, const int64_t* v) {
    int64_t total = 0;
    for (size_t t = 0; t < p->num_terms; ++t) {
        int64_t term_val = p->terms[t].coeff;
        for (size_t i = 0; i < p->num_vars; ++i) {
            uint8_t exp = p->terms[t].exponents[i];
            for (uint8_t e = 0; e < exp; ++e) {
                term_val *= v[i];
            }
        }
        total += term_val;
    }
    return total;
}
```
```cpp
#include <vector>
#include <span>
#include <array>
#include <cstdint>

struct Monomial {
    int64_t coeff{0};
    std::array<uint8_t, 8> exponents{};
};

class SparsePolynomial {
public:
    explicit SparsePolynomial(std::size_t num_vars, std::vector<Monomial> terms)
        : num_vars_(num_vars), terms_(std::move(terms)) {}

    [[nodiscard]] int64_t evaluate(std::span<const int64_t> v) const noexcept {
        int64_t total = 0;
        for (const auto& term : terms_) {
            int64_t term_val = term.coeff;
            for (std::size_t i = 0; i < num_vars_; ++i) {
                for (uint8_t e = 0; e < term.exponents[i]; ++e) {
                    term_val *= v[i];
                }
            }
            total += term_val;
        }
        return total;
    }

private:
    std::size_t num_vars_;
    std::vector<Monomial> terms_;
};
```
:::

---

## 3. Інтервальне оцінювання та відсікання підпросторів

Для швидкого виключення цілих прямокутних областей пошуку `Box = [x₁_min, x₁_max] × ... × [xₘ_min, xₘ_max]` застосовується техніка **інтервальної арифметики**. Якщо для заданого інтервалу змінних мінімально можливе значення многочлена перевищує нуль (`P_min(Box) > 0`) або максимально можливе є строго меншим за нуль (`P_max(Box) < 0`), то у всьому підпросторі `Box` гарантовано немає жодного кореня.

### Правила інтервальних операцій
Для двох цілих інтервалів `A = [a₁, a₂]` та `B = [b₁, b₂]`:
- **Додавання**: `[a₁ + b₁, a₂ + b₂]`
- **Віднімання**: `[a₁ − b₂, a₂ − b₁]`
- **Множення**: `[min(a₁b₁, a₁b₂, a₂b₁, a₂b₂), max(a₁b₁, a₁b₂, a₂b₁, a₂b₂)]`
- **Піднесення до парного степеня**: якщо `0 ∈ A`, то `[0, max(a₁², a₂²)]`, інакше `[min(a₁², a₂²), max(a₁², a₂²)]`.

Завдяки збереженню інваріантів монотонності інтервальний аналіз дозволяє відсікати дерево рекурсивного пошуку на верхніх рівнях глибини, заощаджуючи мільйони непотрібних точкових обчислень.

### Реалізація інтервального фільтра

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    int64_t lo;
    int64_t hi;
} Interval;

Interval interval_add(Interval a, Interval b) {
    return (Interval){a.lo + b.lo, a.hi + b.hi};
}

Interval interval_sub(Interval a, Interval b) {
    return (Interval){a.lo - b.hi, a.hi - b.lo};
}

Interval interval_mul(Interval a, Interval b) {
    int64_t p1 = a.lo * b.lo, p2 = a.lo * b.hi;
    int64_t p3 = a.hi * b.lo, p4 = a.hi * b.hi;
    int64_t min_p = p1 < p2 ? p1 : p2;
    if (p3 < min_p) min_p = p3;
    if (p4 < min_p) min_p = p4;
    int64_t max_p = p1 > p2 ? p1 : p2;
    if (p3 > max_p) max_p = p3;
    if (p4 > max_p) max_p = p4;
    return (Interval){min_p, max_p};
}

Interval interval_sqr(Interval a) {
    if (a.lo <= 0 && a.hi >= 0) {
        int64_t m1 = a.lo * a.lo, m2 = a.hi * a.hi;
        return (Interval){0, m1 > m2 ? m1 : m2};
    }
    int64_t m1 = a.lo * a.lo, m2 = a.hi * a.hi;
    return (Interval){m1 < m2 ? m1 : m2, m1 > m2 ? m1 : m2};
}

bool interval_contains_zero(Interval a) {
    return a.lo <= 0 && a.hi >= 0;
}
```
```cpp
#include <algorithm>
#include <cstdint>

struct Interval {
    int64_t lo{0};
    int64_t hi{0};

    [[nodiscard]] constexpr bool contains_zero() const noexcept {
        return lo <= 0 && hi >= 0;
    }

    friend constexpr Interval operator+(Interval a, Interval b) noexcept {
        return {a.lo + b.lo, a.hi + b.hi};
    }

    friend constexpr Interval operator-(Interval a, Interval b) noexcept {
        return {a.lo - b.hi, a.hi - b.lo};
    }

    friend constexpr Interval operator*(Interval a, Interval b) noexcept {
        const int64_t p1 = a.lo * b.lo, p2 = a.lo * b.hi;
        const int64_t p3 = a.hi * b.lo, p4 = a.hi * b.hi;
        return {
            std::min({p1, p2, p3, p4}),
            std::max({p1, p2, p3, p4})
        };
    }

    [[nodiscard]] constexpr Interval square() const noexcept {
        if (lo <= 0 && hi >= 0) {
            return {0, std::max(lo * lo, hi * hi)};
        }
        const int64_t m1 = lo * lo, m2 = hi * hi;
        return {std::min(m1, m2), std::max(m1, m2)};
    }
};
```
:::

---

## 4. Модульне сито та локально-глобальний фільтр

Перш ніж запускати ресурсомісткий пошук коренів діофантового многочлена `P(x₁, ..., xₘ) = 0` у необмеженому цілочисельному просторі, застосовується перевірка необхідних умов розв'язності за допомогою модульної редукції.

### Принцип Хассе (локально-глобальний аналіз)
Якщо поліноміальне рівняння має розв'язок у цілих числах `ℤ`, воно зобов'язане мати розв'язок за **будь-яким натуральним модулем** `M ≥ 2`:

```
∃ x ∈ ℤᵐ : P(x) = 0  ⇒  ∀ M ≥ 2 ∃ x ∈ (ℤ/Mℤ)ᵐ : P(x) ≡ 0 (mod M)
```

Якщо хоча б для одного малого модуля `M` (зазвичай обирають прості числа `M ∈ {2, 3, 5, 7, 8, 9, 16}`) рівняння `P(x) ≡ 0 (mod M)` не має жодного розв'язку в кільці лишків `ℤ/Mℤ`, то вихідне діофантове рівняння гарантовано не має цілих коренів.

Класичний приклад: рівняння `x² + y² = 4k + 3`. Оскільки квадрати за модулем 4 можуть дорівнювати лише `0` або `1`, сума двох квадратів `x² + y² (mod 4)` може набувати значень `{0, 1, 2}`, але ніколи не дорівнює `3`. Модульне сито за модулем 4 миттєво відкидає це рівняння за `O(1)` операцій, не витрачаючи ресурси на нескінченний пошук.

### Реалізація модульного сита

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

typedef int64_t (*PolyEvalFn)(const int64_t* v, size_t n);

// Перевірка існування розв'язку за малим модулем m перебором лишків
bool modular_sieve_check(PolyEvalFn poly, size_t n, int64_t modulus) {
    int64_t current[8] = {0};
    if (n > 8) return true; // Пропускаємо перевірку для великих розмірностей

    size_t total_combinations = 1;
    for (size_t i = 0; i < n; ++i) total_combinations *= modulus;

    for (size_t step = 0; step < total_combinations; ++step) {
        size_t temp = step;
        for (size_t i = 0; i < n; ++i) {
            current[i] = temp % modulus;
            temp /= modulus;
        }
        int64_t val = poly(current, n);
        if ((val % modulus + modulus) % modulus == 0) {
            return true; // Знайдено локальний розв'язок за модулем
        }
    }
    return false; // Локальних розв'язків нема -> глобальний розв'язок неможливий
}
```
```cpp
#include <vector>
#include <span>
#include <functional>
#include <cstdint>

class ModularSieve {
public:
    template <typename Fn>
    static bool has_local_solution(Fn&& poly, std::size_t n, int64_t modulus) noexcept {
        if (n > 8) return true; // Пропускаємо для високих розмірностей

        std::vector<int64_t> current(n, 0);
        std::size_t total = 1;
        for (std::size_t i = 0; i < n; ++i) total *= modulus;

        for (std::size_t step = 0; step < total; ++step) {
            std::size_t temp = step;
            for (std::size_t i = 0; i < n; ++i) {
                current[i] = static_cast<int64_t>(temp % modulus);
                temp /= modulus;
            }
            const int64_t val = poly(std::span<const int64_t>(current));
            if ((val % modulus + modulus) % modulus == 0) {
                return true;
            }
        }
        return false;
    }
};
```
:::

---

## 5. Діофантове моделювання лічильникових машин Мінського

Щоб побачити, як теоретичні машини обчислень перетворюються на поліноміальні рівняння, розглянемо модель **машини Мінського з двома лічильниками** (англ. *2-counter Minsky machine*). Марвін Мінський у 1961 році довів, що машина з двома регістрами `(r₁, r₂)` та набором інструкцій двох типів:
1. `INC(r, next_pc)`: збільшити лічильник `r` на 1 і перейти до команди `next_pc`.
2. `DEC_JNZ(r, next_pc, zero_pc)`: якщо `r > 0`, зменшити `r` на 1 і перейти до `next_pc`; якщо `r = 0`, перейти до `zero_pc`.
є **Тюрінг-повною** (здатною моделювати довільне обчислення).

### Алгебраїзація переходів стану
Стан машини на кроці `t` описується вектором `(pc_t, r1_t, r2_t)`. Кожен крок виконання кодується поліноміальним предикатом переходу `Step(State_t, State_{t+1}) = 0`. Повна траса довжини `T` від початкового стану до термінального стану `pc_T = HALT` задається кон'юнкцією перехідних рівнянь:

```
(State_0 = Initial) ∧ (State_T = Halt) ∧ ∀ t < T ( Step(State_t, State_{t+1}) = 0 )
```

Усуваючи квантор `∀ t < T` через кодування послідовностей Пелля, довільна програма Мінського зводиться до єдиного діофантового рівняння.

### Покроковий приклад виконання програми подвоєння лічильника
Розглянемо програму подвоєння значення регістра `r1` з використанням допоміжного регістра `r2`:
- `0: DEC_JNZ(0, next_pc=1, zero_pc=3)` (зменшити `r1`, перейти до 1; якщо 0 — завершити на 3)
- `1: INC(1, next_pc=2)` (збільшити `r2` на 1)
- `2: INC(1, next_pc=0)` (ще раз збільшити `r2` на 1 і повернутися на 0)
- `3: HALT`

Якщо початковий стан `State_0 = (0, r1=2, r2=0)`, траса обчислень має вигляд:
- Крок 0: `(0, 2, 0) → (1, 1, 0)` (`verify_diophantine_step = 0`)
- Крок 1: `(1, 1, 0) → (2, 1, 1)` (`verify_diophantine_step = 0`)
- Крок 2: `(2, 1, 1) → (0, 1, 2)` (`verify_diophantine_step = 0`)
- Крок 3: `(0, 1, 2) → (1, 0, 2)` (`verify_diophantine_step = 0`)
- Крок 4: `(1, 0, 2) → (2, 0, 3)` (`verify_diophantine_step = 0`)
- Крок 5: `(2, 0, 3) → (0, 0, 4)` (`verify_diophantine_step = 0`)
- Крок 6: `(0, 0, 4) → (3, 0, 4)` (перехід за нулем, фінал з `r2 = 4 = 2 · 2`).

### Реалізація верифікатора кроку

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

typedef enum { OP_INC, OP_DEC_JNZ, OP_HALT } OpCode;

typedef struct {
    OpCode op;
    int reg;      // 0 для r1, 1 для r2
    int next_pc;  // Наступний крок
    int zero_pc;  // Крок при r == 0
} Instruction;

typedef struct {
    int pc;
    int64_t r1;
    int64_t r2;
} MachineState;

// Поліноміальна нев'язка переходу (повинна дорівнювати 0 для валідного кроку)
int64_t verify_diophantine_step(const Instruction* code, MachineState s_curr, MachineState s_next) {
    const Instruction* inst = &code[s_curr.pc];
    if (inst->op == OP_HALT) {
        return (s_next.pc - s_curr.pc) + (s_next.r1 - s_curr.r1) + (s_next.r2 - s_curr.r2);
    }
    if (inst->op == OP_INC) {
        int64_t r1_diff = (inst->reg == 0) ? (s_next.r1 - (s_curr.r1 + 1)) : (s_next.r1 - s_curr.r1);
        int64_t r2_diff = (inst->reg == 1) ? (s_next.r2 - (s_curr.r2 + 1)) : (s_next.r2 - s_curr.r2);
        int64_t pc_diff = s_next.pc - inst->next_pc;
        return r1_diff * r1_diff + r2_diff * r2_diff + pc_diff * pc_diff;
    }
    // OP_DEC_JNZ: розгалуження моделюється через добуток умов
    int64_t reg_val = (inst->reg == 0) ? s_curr.r1 : s_curr.r2;
    if (reg_val == 0) {
        int64_t pc_diff = s_next.pc - inst->zero_pc;
        int64_t r1_diff = s_next.r1 - s_curr.r1;
        int64_t r2_diff = s_next.r2 - s_curr.r2;
        return pc_diff * pc_diff + r1_diff * r1_diff + r2_diff * r2_diff;
    } else {
        int64_t pc_diff = s_next.pc - inst->next_pc;
        int64_t r1_diff = (inst->reg == 0) ? (s_next.r1 - (s_curr.r1 - 1)) : (s_next.r1 - s_curr.r1);
        int64_t r2_diff = (inst->reg == 1) ? (s_next.r2 - (s_curr.r2 - 1)) : (s_next.r2 - s_curr.r2);
        return pc_diff * pc_diff + r1_diff * r1_diff + r2_diff * r2_diff;
    }
}
```
```cpp
#include <vector>
#include <cstdint>

enum class OpCode { Inc, DecJnz, Halt };

struct Instruction {
    OpCode op{OpCode::Halt};
    int reg{0};      // 0 -> r1, 1 -> r2
    int next_pc{0};
    int zero_pc{0};
};

struct MachineState {
    int pc{0};
    int64_t r1{0};
    int64_t r2{0};
};

class MinskyVerifier {
public:
    static int64_t verify_step(const std::vector<Instruction>& code, 
                               MachineState s_curr, MachineState s_next) noexcept {
        const auto& inst = code[s_curr.pc];
        if (inst.op == OpCode::Halt) {
            return (s_next.pc - s_curr.pc) + (s_next.r1 - s_curr.r1) + (s_next.r2 - s_curr.r2);
        }
        if (inst.op == OpCode::Inc) {
            const int64_t r1_diff = (inst.reg == 0) ? (s_next.r1 - (s_curr.r1 + 1)) : (s_next.r1 - s_curr.r1);
            const int64_t r2_diff = (inst.reg == 1) ? (s_next.r2 - (s_curr.r2 + 1)) : (s_next.r2 - s_curr.r2);
            const int64_t pc_diff = s_next.pc - inst.next_pc;
            return r1_diff * r1_diff + r2_diff * r2_diff + pc_diff * pc_diff;
        }

        const int64_t reg_val = (inst.reg == 0) ? s_curr.r1 : s_curr.r2;
        if (reg_val == 0) {
            const int64_t pc_diff = s_next.pc - inst.zero_pc;
            const int64_t r1_diff = s_next.r1 - s_curr.r1;
            const int64_t r2_diff = s_next.r2 - s_curr.r2;
            return pc_diff * pc_diff + r1_diff * r1_diff + r2_diff * r2_diff;
        } else {
            const int64_t pc_diff = s_next.pc - inst.next_pc;
            const int64_t r1_diff = (inst.reg == 0) ? (s_next.r1 - (s_curr.r1 - 1)) : (s_next.r1 - s_curr.r1);
            const int64_t r2_diff = (inst.reg == 1) ? (s_next.r2 - (s_curr.r2 - 1)) : (s_next.r2 - s_curr.r2);
            return pc_diff * pc_diff + r1_diff * r1_diff + r2_diff * r2_diff;
        }
    }
};
```
:::

---

## 6. Рушій обмеженого пошуку в гіперкубі (Dovetailing Search)

У загальному випадку діофантове рівняння `P(x₁, x₂, ..., xₘ) = 0` може мати нескінченний простір пошуку `ℕᵐ`. Якщо ми спробуємо перебирати змінні наївним вкладеним циклом (наприклад, змінюючи `x₁` від `0` до `∞` для фіксованих інших змінних), то в разі відсутності розв'язку при `x₂ = 0` алгоритм назавжди зависне у нескінченному внутрішньому циклі за `x₁`, так і не перевіривши жодного іншого значення `x₂`.

### Метод шаруватого сканування за нормою L_∞
Щоб побудувати напіввирішувач, який гарантовано знаходить розв'язок, якщо той існує, простір `ℕᵐ` розбивається на концентричні шари за нескінченною нормою Чебишова:

```
||x||_∞ = max(|x₁|, |x₂|, ..., |xₘ|) = B
```

Для кожного послідовного значення границі `B = 0, 1, 2, ...` алгоритм обчислює поліном **виключно на зовнішній оболонці гіперкуба**:

```
Shell(B) = { x ∈ ℕᵐ ∣ ||x||_∞ = B } = { x ∈ ℕᵐ ∣ ||x||_∞ ≤ B } ∖ { x ∈ ℕᵐ ∣ ||x||_∞ ≤ B − 1 }
```

Кількість точок у шарі `Shell(B)` дорівнює `(B + 1)ᵐ − Bᵐ`. Обхід лише зовнішньої межі усуває повторні перевірки точок внутрішнього об'єму, які вже були перевірені на попередніх ітераціях.

### Алгоритмічна складність та інваріанти
- **Повнота перебору**: Будь-яка точка `x* ∈ ℕᵐ` із нормою `B* = ||x*||_∞` гарантовано буде досягнута та перевірена рівно на ітерації з номером `B*`.
- **Просторова складність**: `O(m)` пам'яті для зберігання поточного вектора змінних на стеку викликів.
- **Часова складність**: `O(Bᵐ)` операцій обчислення многочлена, де `B` — норма першого знайденого кореня.

### Реалізація пошуку у гіперкубі

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

typedef int64_t (*DiophantinePoly)(const int64_t* vars, size_t n);

typedef struct {
    size_t num_vars;
    int64_t max_bound;
    uint64_t evaluated_points;
} SearchStats;

// Рекурсивний обхід граней гіперкуба з поточною нормою B
static bool search_layer(DiophantinePoly poly, int64_t* current, size_t idx, 
                         size_t n, int64_t bound, bool has_boundary, SearchStats* stats) {
    if (idx == n) {
        if (!has_boundary) {
            return false; // Точка вже перевірялася на попередніх кроках
        }
        stats->evaluated_points++;
        return poly(current, n) == 0;
    }

    for (int64_t val = 0; val <= bound; ++val) {
        current[idx] = val;
        bool on_bound = has_boundary || (val == bound);
        if (search_layer(poly, current, idx + 1, n, bound, on_bound, stats)) {
            return true;
        }
    }
    return false;
}

bool diophantine_dovetail_search(DiophantinePoly poly, size_t n, int64_t max_bound, 
                                 int64_t* out_solution, SearchStats* stats) {
    stats->num_vars = n;
    stats->max_bound = max_bound;
    stats->evaluated_points = 0;

    int64_t current[16] = {0};
    if (n > 16) return false; // Захист стеку від переповнення

    for (int64_t b = 0; b <= max_bound; ++b) {
        if (search_layer(poly, current, 0, n, b, (b == 0), stats)) {
            for (size_t i = 0; i < n; ++i) {
                out_solution[i] = current[i];
            }
            return true;
        }
    }
    return false;
}
```
```cpp
#include <iostream>
#include <vector>
#include <optional>
#include <functional>
#include <span>

struct SearchProfile {
    std::size_t num_vars{0};
    int64_t max_bound{0};
    uint64_t evaluated_points{0};
};

template <typename Predicate>
class DiophantineSolver {
public:
    explicit DiophantineSolver(Predicate poly, std::size_t dimensions)
        : poly_(std::move(poly)), dimensions_(dimensions) {}

    std::optional<std::vector<int64_t>> search(int64_t max_bound, SearchProfile& stats) {
        stats.num_vars = dimensions_;
        stats.max_bound = max_bound;
        stats.evaluated_points = 0;

        std::vector<int64_t> current(dimensions_, 0);

        for (int64_t b = 0; b <= max_bound; ++b) {
            if (search_layer(current, 0, b, (b == 0), stats)) {
                return current;
            }
        }
        return std::nullopt;
    }

private:
    bool search_layer(std::vector<int64_t>& current, std::size_t idx, 
                      int64_t bound, bool has_boundary, SearchProfile& stats) {
        if (idx == dimensions_) {
            if (!has_boundary) return false;
            stats.evaluated_points++;
            return poly_(std::span<const int64_t>(current)) == 0;
        }

        for (int64_t val = 0; val <= bound; ++val) {
            current[idx] = val;
            const bool on_bound = has_boundary || (val == bound);
            if (search_layer(current, idx + 1, bound, on_bound, stats)) {
                return true;
            }
        }
        return false;
    }

    Predicate poly_;
    std::size_t dimensions_;
};
```
:::

---

## 7. Генератор простих чисел Джонса–Сато–Вади–Вієнса (JSWW)

Одним із найбільш вражаючих наслідків теореми ДПРМ є існування многочленів, множина додатних значень яких на невід'ємних цілих аргументах збігається в точності з множиною всіх простих чисел.

У 1976 році четверо математиків — Джеймс Джонс, Дайхачіро Сато, Хідео Вада та Пітер Вієнс — побудували явний многочлен 25-го степеня від 26 змінних `v = (a, b, c, ..., z)`. В основі їхньої конструкції лежить теорема Вілсона: число `k + 2` є простим тоді й лише тоді, коли `(k + 1)! + 1` ділиться на `k + 2`.

Загальний вираз має вигляд:

```
P(a, b, ..., z) = (k + 2) · (1 − ∑ [i=1..14] Eᵢ²)
```

Коли сума чотирнадцяти квадратів `∑ Eᵢ²` дорівнює нулю, усі 14 допоміжних рівнянь виконуються одночасно, а многочлен повертає значення `k + 2`, яке гарантовано є простим числом. Якщо ж хоча б одне рівняння не виконується, сума квадратів `∑ Eᵢ² ≥ 1`, а множник `(1 − ∑ Eᵢ²)` стає недодатним, внаслідок чого весь многочлен набуває від'ємного значення або нуля.

### Структура 14 компонентів системи Вілсона

1. **`e₁ = wz + h + j − q` та `e₂ = (gk + 2g + k + 1)(h + j) + h − z`**: кодують модульну арифметику для факторіала за теоремою Вілсона.
2. **`e₃ = 16(k + 1)²(z + 1)² + 1 − f²`**: задає квадратичний бар'єр, який гарантує коректне обмеження величини факторіала.
3. **`e₄ = 2n + p + q + z − e` та `e₅ = e³(e + 2)(a + 1)² + 1 − o²`**: встановлюють параметри великої основи `a` для наближення факторіала.
4. **`e₆ = (a² − 1)y² + 1 − x²` та `e₇ = 16r²y⁴(a² − 1) + 1 − u²`**: два екземпляри рівняння Пелля для основи `a`, що генерують послідовність експоненційного зростання `yₙ(a)`.
5. **`e₈ = ((a + u²(u² − a))² − 1)(n + 4dy)² + 1 − (x + cu)²`**: синхронізує розв'язки Пелля з індексом `n`.
6. **`e₉ = (a² − 1)l² + 1 − m²` та `e₁₀ = ai + k + 1 − l − i`**: задають розв'язки Пелля для допоміжної змінної `l`.
7. **`e₁₁, e₁₂, e₁₃`**: фіксують точні конгруенції, які пов'язують розв'язки Пелля зі значенням факторіала `k!`.

### Реалізація обчислення полінома JSWW

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

// Поліном Джонса-Сато-Вади-Вієнса (JSWW, 1976)
int64_t eval_jsww_prime_poly(const int64_t* v) {
    // Змінні відображаються на v[0]..v[25]: a=0, b=1, ..., z=25
    int64_t a = v[0],  b = v[1],  c = v[2],  d = v[3],  e = v[4],  f = v[5],
            g = v[6],  h = v[7],  i = v[8],  j = v[9],  k = v[10], l = v[11],
            m = v[12], n = v[13], o = v[14], p = v[15], q = v[16], r = v[17],
            s = v[18], t = v[19], u = v[20], w = v[21], x = v[22], y = v[23],
            z = v[24], k_val = v[10];

    // 14 квадратичних виразів системи Вілсона
    int64_t e1 = w * z + h + j - q;
    int64_t e2 = (g * k + 2 * g + k + 1) * (h + j) + h - z;
    int64_t e3 = 16 * (k + 1) * (k + 1) * (z + 1) * (z + 1) + 1 - f * f;
    int64_t e4 = 2 * n + p + q + z - e;
    int64_t e5 = e * e * e * (e + 2) * (a + 1) * (a + 1) + 1 - o * o;
    int64_t e6 = (a * a - 1) * y * y + 1 - x * x;
    int64_t e7 = 16 * r * r * y * y * y * y * (a * a - 1) + 1 - u * u;
    int64_t term_a = a + u * u * (u * u - a);
    int64_t e8 = (term_a * term_a - 1) * (n + 4 * d * y) * (n + 4 * d * y) + 1 - (x + c * u) * (x + c * u);
    int64_t e9 = (a * a - 1) * l * l + 1 - m * m;
    int64_t e10 = a * i + k + 1 - l - i;
    int64_t e11 = p + l * (a - n - 1) + b * (2 * a * (n + 1) - (n + 1) * (n + 1) - 1) - m;
    int64_t e12 = q + y * (a - p - 1) + s * (2 * a * (p + 1) - (p + 1) * (p + 1) - 1) - x;
    int64_t e13 = z + p * (a - q - 1) + t * (2 * a * (q + 1) - (q + 1) * (q + 1) - 1) - r;

    int64_t sum_squares = e1*e1 + e2*e2 + e3*e3 + e4*e4 + e5*e5 + e6*e6 + e7*e7 +
                          e8*e8 + e9*e9 + e10*e10 + e11*e11 + e12*e12 + e13*e13;

    return (k_val + 2) * (1 - sum_squares);
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <cstdint>

struct JSWWPolynomial {
    static int64_t evaluate(std::span<const int64_t, 26> v) noexcept {
        const int64_t a = v[0],  b = v[1],  c = v[2],  d = v[3],  e = v[4],  f = v[5],
                      g = v[6],  h = v[7],  i = v[8],  j = v[9],  k = v[10], l = v[11],
                      m = v[12], n = v[13], o = v[14], p = v[15], q = v[16], r = v[17],
                      s = v[18], t = v[19], u = v[20], w = v[21], x = v[22], y = v[23],
                      z = v[24], k_val = v[10];

        const int64_t e1  = w * z + h + j - q;
        const int64_t e2  = (g * k + 2 * g + k + 1) * (h + j) + h - z;
        const int64_t e3  = 16 * (k + 1) * (k + 1) * (z + 1) * (z + 1) + 1 - f * f;
        const int64_t e4  = 2 * n + p + q + z - e;
        const int64_t e5  = e * e * e * (e + 2) * (a + 1) * (a + 1) + 1 - o * o;
        const int64_t e6  = (a * a - 1) * y * y + 1 - x * x;
        const int64_t e7  = 16 * r * r * y * y * y * y * (a * a - 1) + 1 - u * u;
        const int64_t term_a = a + u * u * (u * u - a);
        const int64_t e8  = (term_a * term_a - 1) * (n + 4 * d * y) * (n + 4 * d * y) + 1 - (x + c * u) * (x + c * u);
        const int64_t e9  = (a * a - 1) * l * l + 1 - m * m;
        const int64_t e10 = a * i + k + 1 - l - i;
        const int64_t e11 = p + l * (a - n - 1) + b * (2 * a * (n + 1) - (n + 1) * (n + 1) - 1) - m;
        const int64_t e12 = q + y * (a - p - 1) + s * (2 * a * (p + 1) - (p + 1) * (p + 1) - 1) - x;
        const int64_t e13 = z + p * (a - q - 1) + t * (2 * a * (q + 1) - (q + 1) * (q + 1) - 1) - r;

        const int64_t sum_squares = e1*e1 + e2*e2 + e3*e3 + e4*e4 + e5*e5 + e6*e6 + e7*e7 +
                                    e8*e8 + e9*e9 + e10*e10 + e11*e11 + e12*e12 + e13*e13;

        return (k_val + 2) * (1 - sum_squares);
    }
};
```
:::

---

## 8. Демонстраційний запуск та перевірка розв'язків

Нижче наведено повні модулі тестування для обох мов, які розв'язують складне рівняння Пелля для `D = 61` (знаменитий приклад П'єра Ферма з листування 1657 року, фундаментальний розв'язок якого сягає значень `x = 1766319049, y = 226153980`), виконують модульне та інтервальне сито і здійснюють сканування тривимірного гіперкуба для пошуку піфагорового трикутника `x² + y² − z² = 0` з фіксованим катетом `x = 3`.

Історично вибір Ферма числа `D = 61` був покликаний показати англійським колегам (Вільяму Браункеру та Джону Валлісу), що прості перебори малих чисел виявляються безсилими перед експоненційним зростанням розв'язків: попри мале значення `D`, перший додатний розв'язок має майже 10 десяткових знаків. Алгоритм неперервних дробів знаходить його менш ніж за 20 арифметичних операцій.

:::tabs
```c
int main(void) {
    printf("=== Демонстрація розв'язання рівняння Пелля ===\n");
    uint64_t d = 61;
    PellSolution fund = pell_solve_fundamental(d);
    if (fund.found) {
        printf("Фундаментальний розв'язок для D = %llu:\n  x₁ = ", (unsigned long long)d);
        print_u128(fund.x);
        printf("\n  y₁ = ");
        print_u128(fund.y);
        printf("\n");

        PellSolution sol2 = pell_next_solution(fund, fund, d);
        printf("Другий розв'язок (x₂, y₂):\n  x₂ = ");
        print_u128(sol2.x);
        printf("\n  y₂ = ");
        print_u128(sol2.y);
        printf("\n");
    }

    printf("\n=== Довблення гіперкуба (Пошук піфагорової трійки) ===\n");
    // Многочлен P(x, y, z) = (x^2 + y^2 - z^2)^2 + (x - 3)^2 [для фіксації x=3, y>0]
    int64_t pythagoras_test(const int64_t* v, size_t n) {
        (void)n;
        int64_t x = v[0], y = v[1], z = v[2];
        if (x == 0 || y == 0 || z == 0) return -1;
        return (x * x + y * y - z * z) * (x * x + y * y - z * z) + (x - 3) * (x - 3);
    }

    // Модульне сито перед перебором
    if (!modular_sieve_check(pythagoras_test, 3, 4)) {
        printf("Рівняння відхилено модульним ситом за модулем 4.\n");
    } else {
        printf("Модульне сито пройдено успішно. Запуск довблення...\n");
        int64_t sol[3] = {0};
        SearchStats stats;
        if (diophantine_dovetail_search(pythagoras_test, 3, 10, sol, &stats)) {
            printf("Знайдено розв'язок: x=%lld, y=%lld, z=%lld (Оцінено точок: %llu)\n",
                   (long long)sol[0], (long long)sol[1], (long long)sol[2], 
                   (unsigned long long)stats.evaluated_points);
        }
    }

    return 0;
}
```
```cpp
int main() {
    std::cout << "=== Демонстрація розв'язання рівняння Пелля ===\n";
    constexpr uint64_t d = 61;
    if (auto fund = PellSolver::find_fundamental(d)) {
        std::cout << "Фундаментальний розв'язок для D = " << d << ":\n"
                  << "  x₁ = " << fund->to_string_x() << "\n"
                  << "  y₁ = " << fund->to_string_y() << "\n";

        auto sol2 = PellSolver::next_power(*fund, *fund, d);
        std::cout << "Другий розв'язок (x₂, y₂):\n"
                  << "  x₂ = " << sol2.to_string_x() << "\n"
                  << "  y₂ = " << sol2.to_string_y() << "\n";
    }

    std::cout << "\n=== Довблення гіперкуба (Пошук піфагорової трійки) ===\n";
    auto pythagoras = [](std::span<const int64_t> v) -> int64_t {
        const int64_t x = v[0], y = v[1], z = v[2];
        if (x == 0 || y == 0 || z == 0) return -1;
        return (x * x + y * y - z * z) * (x * x + y * y - z * z) + (x - 3) * (x - 3);
    };

    if (!ModularSieve::has_local_solution(pythagoras, 3, 4)) {
        std::cout << "Рівняння відхилено модульним ситом за модулем 4.\n";
    } else {
        std::cout << "Модульне сито пройдено успішно. Запуск довблення...\n";
        DiophantineSolver solver(pythagoras, 3);
        SearchProfile stats;
        if (auto sol = solver.search(10, stats)) {
            std::cout << "Знайдено розв'язок: x=" << (*sol)[0] 
                      << ", y=" << (*sol)[1] 
                      << ", z=" << (*sol)[2]
                      << " (Оцінено точок: " << stats.evaluated_points << ")\n";
        }
    }

    return 0;
}
```
:::

---

## 9. Порівняння з SMT-солверами, дійсними полями та практичні пастки

Сучасні системи автоматичного доведення теорем та SMT-солвери (зокрема Z3, CVC5, Yices2) містять спеціалізовані рушії для теорії нелінійної цілочисельної арифметики (**QF_NIA** — *Quantifier-Free Non-linear Integer Arithmetic*). Вони поєднують лінійне програмування над цілими числами (LIA), метод гілок і меж (Branch-and-Bound), бази Грьобнера та циліндричний алгебраїчний розклад (CAD).

Цікаво зазначити різницю між арифметиками над різними числовими областями:
- **Арифметика Пресбургера** над цілими числами (де дозволені лише додавання, віднімання та порівняння `+ , − , ≤`) є **алгоритмічно розв'язною** (хоча й має подвійну експоненційну складність у гіршому випадку). Для неї будь-який SMT-солвер гарантує повернення точної відповіді `sat` або `unsat`.
- **Елементарна алгебра над дійсними числами `ℝ`** (з операціями додавання, множення та всіма кванторами першого порядку) є **алгоритмічно розв'язною** завдяки фундаментальній теоремі Тарського про елімінацію кванторів (метод циліндричного алгебраїчного розкладу Колінза, CAD).
- Проте над **цілими числами `ℤ`** додавання нелінійного множення `x · y` миттєво переносить теорію у клас ДПРМ, роблячи задачу перевірки здійсненності алгоритмічно нерозв'язною. (Питання про розв'язність над полем раціональних чисел `ℚ` залишається однією з найглибших відкритих проблем сучасної математики).
- Історично Давид Гільберт у 1900 році очікував знайти позитивний алгоритмічний розв'язок, оскільки для бінарних квадратичних форм `a·x² + b·x·y + c·y² = d` класики математики Жозеф-Луї Лагранж та Карл Фрідріх Гаусс уже розробили повний конструктивний алгоритм за допомогою редукції форм та теорії родів. ДПРМ показала, що перехід від степеня 2 до вищих степенів і більшої кількості змінних якісно змінює обчислювальну природу задачі.

Тому фундаментальний висновок теореми ДПРМ полягає в тому, що **жоден SMT-солвер не може бути одночасно коректним і повним для теорії QF_NIA**:
- Якщо солвер зустрічає діофантове рівняння, що моделює проблему зупинки машини Тюрінга, він неминуче або потрапляє в нескінченний цикл, або змушений повертати невизначений результат `unknown` за таймаутом.
- Будь-який евристичний алгоритм пошуку розв'язків є практичним наближенням напіввирішувача, де кожна оптимізація (інтервальна, модульна чи алгебраїчна) лише прискорює пошук у скінченних підпросторах, не змінюючи глобальної алгоритмічної неповноти.

### Граничні випадки та помилки реалізації

1. **Астрономічний вибух коефіцієнтів у рівнянні Пелля**:
   Довжина періоду неперервного дробу `L` та розмір координат фундаментального розв'язку можуть бути надзвичайно великими навіть для помірних значень `D`. Наприклад, для `D = 991` фундаментальний розв'язок має вигляд:
   ```
   x₁ = 3795164009067114984594695538311173612053703885
   y₁ = 1205573579033135944744253876700088998370
   ```
   Ці числа значно перевищують ліміт навіть 128-бітних типів (`uint128_t` вміщує значення до `≈ 3.4 × 10³⁸`). Для загального аналізу рівнянь Пелля необхідно використовувати бібліотеки довгої арифметики довільної точності (наприклад, GNU GMP у C або `boost::multiprecision::cpp_int` у C++).

2. **Прокляття розмірності при довбленні**:
   Кількість точок у гіперкубі радіуса `B` від `m` змінних зростає як `(B + 1)ᵐ`. Для систем діофантових рівнянь із 10–26 змінними прямий перебір є абсолютно нездійсненним для `B > 2`. Без додаткового аналізу модульних та інтервальних редукцій пошук у гіперкубі залишається виключно теоретичним інструментом напіврозв'язності.
