# ⚙️ Обчислення коефіцієнтів Фур'є та дії операторів Гекке

Обчислення коефіцієнтів Фур'є рядів Ейзенштейна `E₄(τ)`, `E₆(τ)` та параболічного дискримінанта `Δ(τ)` (функції Рамануджана `τ(n)`) спирається на дискретне подання формальних степеневих рядів та згортку масивів. Алгоритмічна реалізація дії операторів Гекке `T_p` перетворює абстрактні алгебраїчні співвідношення на точні числові векторні перетворення, дозволяючи програмно перевіряти ейлерові добутки L-функцій та мультиплікативні тотожності між власними значеннями.

## 1. Математична основа та архітектура алгоритму

Програмна реалізація модулярних форм опирається на зображення формальних степеневих рядів у вигляді дискретних масивів коефіцієнтів Фур'є:

```
f(q) = a₀ + a₁·q + a₂·q² + ... + a_N · qᴺ + O(qᴺ⁺¹)
```

Для аналізу арифметичних властивостей розробляються три базові обчислювальні блоки:

1. **Генерація рядів Ейзенштейна `E₄` та `E₆`:**
   Коефіцієнти Фур'є опираються на арифметичну функцію суми степеней дільників `σ_k(n) = ∑_{d | n} dᵏ`:
   ```
   E₄(q) = 1 + 240 · ∑_{n=1}^N σ₃(n) · qⁿ
   E₆(q) = 1 - 504 · ∑_{n=1}^N σ₅(n) · qⁿ
   ```
   Алгоритм обчислення `σ_k(n)` застосовує метод перевірки дільників до `√n` зі складністю `O(√n)` для кожного числа, що забезпечує загальну складність генерації рядів `O(N · √N)`.

2. **Множення урізаних степеневих рядів:**
   Множення двох рядів `A(q) = ∑ a_k qᵏ` та `B(q) = ∑ b_k qᵏ` за модулем `q^{N+1}` виконується за алгоритмом узагальненої згортки:
   ```
   C(q) = A(q) · B(q)  ⇒  c_n = ∑_{k=0}^n a_k · b_{n - k}
   ```
   Це дозволяє обчислити `E₄³(q)` та `E₆²(q)`, після чого дискримінант `Δ(q)` знаходиться за формулою:
   ```
   Δ(q) = ( E₄(q)³ - E₆(q)² ) / 1728 = ∑_{n=1}^N τ(n) · qⁿ
   ```

3. **Алгоритм дії оператора Гекке `T_p`:**
   Для модулярної форми ваги `k` дію оператора `T_p` за простим модулем `p` дискретизовано формулою:
   ```
   (T_p f)[n] = a_{p · n} + pᵏ⁻¹ · a_{n / p}      (де a_{n/p} = 0, якщо p ∤ n)
   ```

## 2. Реалізація мовами C та C++

Нижче наведено дві повноцінні, компільно стійкі реалізації: класична версія на мові C з ручним управлінням пам'яттю та ідіоматична версія на C++ з використанням шаблонів, RAII-контейнерів `std::vector` та інкапсульованого класу `ModularFormSeries`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

/* Обчислення суми степеней дільників sigma_k(n) = sum_{d|n} d^k */
static uint64_t sum_divisor_powers(uint32_t n, uint32_t power) {
    uint64_t sum = 0;
    for (uint32_t d = 1; d * d <= n; ++d) {
        if (n % d == 0) {
            uint64_t p1 = 1;
            for (uint32_t i = 0; i < power; ++i) p1 *= d;
            sum += p1;

            uint32_t div2 = n / d;
            if (div2 != d) {
                uint64_t p2 = 1;
                for (uint32_t i = 0; i < power; ++i) p2 *= div2;
                sum += p2;
            }
        }
    }
    return sum;
}

/* Обчислення добутку двох степеневих рядів A(q) * B(q) mod q^(max_deg + 1) */
static void multiply_series(const int64_t *a, const int64_t *b, int64_t *res, size_t max_deg) {
    for (size_t n = 0; n <= max_deg; ++n) {
        res[n] = 0;
        for (size_t k = 0; k <= n; ++k) {
            res[n] += a[k] * b[n - k];
        }
    }
}

/* Дія оператора Гекке T_p на модулярну форму ваги weight */
static void apply_hecke_operator(const int64_t *a, int64_t *b, size_t max_deg, uint32_t p, uint32_t weight) {
    uint64_t p_pow = 1;
    for (uint32_t i = 0; i < weight - 1; ++i) p_pow *= p;

    for (size_t n = 0; n <= max_deg; ++n) {
        int64_t term1 = 0;
        if (n * p <= max_deg) {
            term1 = a[n * p];
        }
        int64_t term2 = 0;
        if (n % p == 0) {
            term2 = (int64_t)p_pow * a[n / p];
        }
        b[n] = term1 + term2;
    }
}

int main(void) {
    const size_t max_n = 10;
    int64_t *e4 = (int64_t *)calloc(max_n + 1, sizeof(int64_t));
    int64_t *e6 = (int64_t *)calloc(max_n + 1, sizeof(int64_t));
    int64_t *e4_2 = (int64_t *)calloc(max_n + 1, sizeof(int64_t));
    int64_t *e4_3 = (int64_t *)calloc(max_n + 1, sizeof(int64_t));
    int64_t *e6_2 = (int64_t *)calloc(max_n + 1, sizeof(int64_t));
    int64_t *delta = (int64_t *)calloc(max_n + 1, sizeof(int64_t));
    int64_t *t2_delta = (int64_t *)calloc(max_n + 1, sizeof(int64_t));

    if (!e4 || !e6 || !e4_2 || !e4_3 || !e6_2 || !delta || !t2_delta) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        free(e4); free(e6); free(e4_2); free(e4_3); free(e6_2); free(delta); free(t2_delta);
        return 1;
    }

    e4[0] = 1;
    e6[0] = 1;
    for (size_t n = 1; n <= max_n; ++n) {
        e4[n] = 240 * (int64_t)sum_divisor_powers((uint32_t)n, 3);
        e6[n] = -504 * (int64_t)sum_divisor_powers((uint32_t)n, 5);
    }

    multiply_series(e4, e4, e4_2, max_n);
    multiply_series(e4_2, e4, e4_3, max_n);
    multiply_series(e6, e6, e6_2, max_n);

    for (size_t n = 0; n <= max_n; ++n) {
        delta[n] = (e4_3[n] - e6_2[n]) / 1728;
    }

    printf("=== Коефіцієнти Фур'є E4, E6 та Delta (tau(n)) ===\n");
    printf("n\tE4(n)\t\tE6(n)\t\tDelta(n) [tau(n)]\n");
    for (size_t n = 1; n <= max_n; ++n) {
        printf("%zu\t%lld\t\t%lld\t\t%lld\n", n, (long long)e4[n], (long long)e6[n], (long long)delta[n]);
    }

    /* Дія оператора Гекке T_2 на параболічну форму Delta (вага 12) */
    apply_hecke_operator(delta, t2_delta, max_n, 2, 12);

    printf("\n=== Дія оператора Гекке T_2 на Delta (tau(2) = %lld) ===\n", (long long)delta[2]);
    printf("n\ttau(n)\t\tT_2(Delta)[n]\tВласне значення T_2(Delta) == tau(2)*tau(n)?\n");
    for (size_t n = 1; n <= 5; ++n) {
        int64_t expected = delta[2] * delta[n];
        printf("%zu\t%lld\t\t%lld\t\t%s (%lld)\n", 
               n, (long long)delta[n], (long long)t2_delta[n],
               (t2_delta[n] == expected) ? "ТАК" : "НІ", (long long)expected);
    }

    free(e4); free(e6); free(e4_2); free(e4_3); free(e6_2); free(delta); free(t2_delta);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <cstdint>
#include <iomanip>

namespace ModularEngine {

class ModularFormSeries {
private:
    std::size_t max_degree_;
    std::size_t weight_;
    std::vector<std::int64_t> coeffs_;

public:
    explicit ModularFormSeries(std::size_t max_degree, std::size_t weight = 0)
        : max_degree_(max_degree), weight_(weight), coeffs_(max_degree + 1, 0) {}

    std::size_t degree() const noexcept { return max_degree_; }
    std::size_t weight() const noexcept { return weight_; }
    
    std::int64_t& operator[](std::size_t idx) { return coeffs_.at(idx); }
    std::int64_t operator[](std::size_t idx) const { return coeffs_.at(idx); }

    static std::uint64_t sigma(std::uint32_t n, std::uint32_t k) {
        std::uint64_t sum = 0;
        for (std::uint32_t d = 1; d * d <= n; ++d) {
            if (n % d == 0) {
                sum += static_cast<std::uint64_t>(std::pow(d, k));
                std::uint32_t div2 = n / d;
                if (div2 != d) {
                    sum += static_cast<std::uint64_t>(std::pow(div2, k));
                }
            }
        }
        return sum;
    }

    static ModularFormSeries create_e4(std::size_t max_deg) {
        ModularFormSeries e4(max_deg, 4);
        e4[0] = 1;
        for (std::size_t n = 1; n <= max_deg; ++n) {
            e4[n] = 240 * static_cast<std::int64_t>(sigma(static_cast<std::uint32_t>(n), 3));
        }
        return e4;
    }

    static ModularFormSeries create_e6(std::size_t max_deg) {
        ModularFormSeries e6(max_deg, 6);
        e6[0] = 1;
        for (std::size_t n = 1; n <= max_deg; ++n) {
            e6[n] = -504 * static_cast<std::int64_t>(sigma(static_cast<std::uint32_t>(n), 5));
        }
        return e6;
    }

    ModularFormSeries operator*(const ModularFormSeries& rhs) const {
        std::size_t deg = std::min(max_degree_, rhs.max_degree_);
        ModularFormSeries res(deg, weight_ + rhs.weight_);
        for (std::size_t n = 0; n <= deg; ++n) {
            std::int64_t sum = 0;
            for (std::size_t k = 0; k <= n; ++k) {
                sum += coeffs_[k] * rhs.coeffs_[n - k];
            }
            res[n] = sum;
        }
        return res;
    }

    ModularFormSeries hecke_operator(std::uint32_t p) const {
        ModularFormSeries result(max_degree_, weight_);
        std::uint64_t p_pow = static_cast<std::uint64_t>(std::pow(p, weight_ - 1));

        for (std::size_t n = 0; n <= max_degree_; ++n) {
            std::int64_t term1 = (n * p <= max_degree_) ? coeffs_[n * p] : 0;
            std::int64_t term2 = (n % p == 0) ? static_cast<std::int64_t>(p_pow) * coeffs_[n / p] : 0;
            result[n] = term1 + term2;
        }
        return result;
    }
};

} // namespace ModularEngine

int main() {
    constexpr std::size_t MAX_N = 10;
    using namespace ModularEngine;

    auto e4 = ModularFormSeries::create_e4(MAX_N);
    auto e6 = ModularFormSeries::create_e6(MAX_N);

    auto e4_3 = e4 * e4 * e4;
    auto e6_2 = e6 * e6;

    ModularFormSeries delta(MAX_N, 12);
    for (std::size_t n = 0; n <= MAX_N; ++n) {
        delta[n] = (e4_3[n] - e6_2[n]) / 1728;
    }

    std::cout << "=== Коефіцієнти Фур'є E4, E6 та Delta (tau(n)) ===\n";
    std::cout << std::setw(4) << "n" << std::setw(14) << "E4(n)" 
              << std::setw(14) << "E6(n)" << std::setw(18) << "Delta(n) [tau(n)]\n";
    std::cout << std::string(50, '-') << "\n";

    for (std::size_t n = 1; n <= MAX_N; ++n) {
        std::cout << std::setw(4) << n << std::setw(14) << e4[n] 
                  << std::setw(14) << e6[n] << std::setw(18) << delta[n] << "\n";
    }

    // Застосування оператора Гекке T_2 до параболічної форми Delta
    auto t2_delta = delta.hecke_operator(2);

    std::cout << "\n=== Перевірка теореми Гекке: T_2(Delta) = tau(2) * Delta ===\n";
    std::cout << "Коефіцієнт tau(2) = " << delta[2] << "\n";
    std::cout << std::setw(4) << "n" << std::setw(14) << "tau(n)" 
              << std::setw(18) << "T_2(Delta)[n]" << std::setw(20) << "tau(2)*tau(n)\n";
    std::cout << std::string(56, '-') << "\n";

    for (std::size_t n = 1; n <= 5; ++n) {
        std::int64_t expected = delta[2] * delta[n];
        std::cout << std::setw(4) << n << std::setw(14) << delta[n] 
                  << std::setw(18) << t2_delta[n] << std::setw(20) << expected 
                  << " (" << (t2_delta[n] == expected ? "ЗБІГАЄТЬСЯ" : "ПОМИЛКА") << ")\n";
    }

    return 0;
}
```
:::

## 3. Детальний трасування обчислень та перевірка тотожностей Гекке

Простежимо крок за кроком дію оператора `T₂` на параболічну форму `Δ(q)` ваги `k = 12` для перших п'яти коефіцієнтів `n = 1, 2, 3, 4, 5`.

За формулою дії оператора `T₂`:
```
(T₂ Δ)[n] = τ(2 · n) + 2¹¹ · τ(n / 2)       (якщо 2 ∤ n, то другий доданок дорівнює 0)
```
Оскільки `2¹¹ = 2048`, отримуємо такі покрокові результати:

1. **Для `n = 1`:**
   Оскільки `2 ∤ 1`, другий доданок відсутній:
   ```
   (T₂ Δ)[1] = τ(2 · 1) + 2048 · τ(1/2) = τ(2) + 0 = -24
   ```
   Перевірка власного значення: `τ(2) · τ(1) = (-24) · 1 = -24`. Збіг ідеальний.

2. **Для `n = 2`:**
   Число `n = 2` ділиться на `2`, тому задіюються обидва доданки:
   ```
   (T₂ Δ)[2] = τ(2 · 2) + 2048 · τ(2 / 2) = τ(4) + 2048 · τ(1)
             = -1472 + 2048 · 1 = 576
   ```
   Перевірка власного значення: `τ(2) · τ(2) = (-24) · (-24) = 576`. Збіг ідеальний!

3. **Для `n = 3`:**
   Число `n = 3` непарне, другий доданок `0`:
   ```
   (T₂ Δ)[3] = τ(2 · 3) + 0 = τ(6) = -6048
   ```
   Перевірка власного значення: `τ(2) · τ(3) = (-24) · 252 = -6048`. Збіг ідеальний!

4. **Для `n = 4`:**
   Число `n = 4` парне, задіюється `τ(2)`:
   ```
   (T₂ Δ)[4] = τ(2 · 4) + 2048 · τ(4 / 2) = τ(8) + 2048 · τ(2)
             = 84480 + 2048 · (-24) = 84480 - 49152 = 35328
   ```
   Перевірка власного значення: `τ(2) · τ(4) = (-24) · (-1472) = 35328`. Збіг ідеальний!

5. **Для `n = 5`:**
   Число `n = 5` непарне:
   ```
   (T₂ Δ)[5] = τ(10) = -115920
   ```
   Перевірка власного значення: `τ(2) · τ(5) = (-24) · 4830 = -115920`. Збіг ідеальний!

## 4. Алгоритмічна складність та масштабні обчислення

Аналіз обчислювальної складності прямого алгоритму показує, що знаходження коефіцієнтів Фур'є до степеня `N` вимагає:
- `O(N · √N)` операцій для сумування дільників `σ_k(n)`.
- `O(N²)` операцій для множення урізаних степеневих рядів методом дискретної згортки.
- `O(N)` операцій для застосування оператора Гекке `T_p`.

Для промислового обчислення коефіцієнтів модулярних форм при `N > 10⁶` використовують швидке перетворення Фур'є (FFT) над скінченними полями, що знижує складність множення рядів до `O(N · log N)`. 

Крім того, застосовують відображення на простір **модулярних символів Маніна** (англ. *Manin modular symbols*). Модулярний символ `{α, β}` кодує інтеграл від параболічної форми вздовж дуги від `α ∈ ℚ ∪ {i∞}` до `β ∈ ℚ ∪ {i∞}` у півплощині `ℍ`. Оскільки група `SL(2, ℤ)` діє на ці символи скінченновимірними матрицями перетворення, обчислення коефіцієнтів `a_p` зводиться до лінійної алгебри над скінченними полями, що реалізовано у пакеті SageMath та бібліотеці PARI/GP.

## 5. Аналіз алгоритмічних переповнень та оптимізацій

При обчисленні коефіцієнтів Фур'є високих степеней слід враховувати швидкості зростання арифметичних функцій:

1. **Зростання коефіцієнтів ряду Ейзенштейна:**
   Оскільки `σ_k(n)` для `k = 5` зростає як `O(n⁵)`, коефіцієнти `E₆[n] = -504 · σ₅(n)` швидко виходять за межі 32-бітного цілочисельного діапазону. Наприклад, при `n = 100` значення `σ₅(100)` перевищує `10¹⁰`, що вимагає обов'язкового використання 64-бітних типів даних (`int64_t` / `std::int64_t`) або моделей довільної точності (GMP / BigInt).

2. **Обчислювальна точність дискримінанта `Δ`:**
   Формула `Δ = (E₄³ - E₆²) / 1728` вимагає точного цілочисельного ділення. Вільні члени `E₄³[0] = 1` та `E₆²[0] = 1` дають чисельну різницю `0`, а коефіцієнт при `q¹`:
   ```
   (3 · 240) - (2 · (-504)) = 720 + 1008 = 1728
   ```
   точнісінько скорочується на `1728`, даючи `τ(1) = 1`. Будь-яке використання чисел із плаваючою крапкою (`double`) призвело б до накопичення помилок округлення вже при `n > 20`.

3. **Властивості власних значень та підтвердження теореми Гекке:**
   Запуск програми показує, що для параболічної форми `Δ` ваги 12 дія оператора `T₂` еквівалентна скалярному множенню на `τ(2) = -24`:
   ```
   T₂ Δ = -24 · Δ
   ```
   Це числово підтверджує, що дискримінант `Δ` є власною формою Гекке, а його L-функція розкладається в Ейлерів добуток.

## 6. Порівняльний аналіз архітектури C та C++

Реалізація на мові C демонструє прямий контроль над пам'яттю через `calloc` та `free`. Проте відсутність об'єктно-орієнтованих абстракцій вимагає передавати розмір масивів `max_deg` та вагу `weight` у кожну функцію окремим аргументом.

Натомість C++ реалізація вносить важливі архітектурні переваги:
- **Інкапсуляція стану:** Клас `ModularFormSeries` зберігає вагу та максимальний степінь усередині об'єкта, гарантуючи відповідність ваг при операції множення рядів `operator*`.
- **Автоматична безпека пам'яті (RAII):** Використання `std::vector<std::int64_t>` виключає можливість витоків пам'яті (англ. *memory leaks*) чи подвійного звільнення (`double free`).
- **Перевантаження операторів:** Синтаксис `auto e4_3 = e4 * e4 * e4;` дозволяє записувати алгебраїчні тотожності модулярних форм природною математичною мовою.

## 7. Крайові випадки та обробка границь

При реалізації дій операторів Гекке та множення рядів слід обробляти такі крайові умови:
- **Нульовий степінь `n = 0`:** Для параболічних форм `Δ` коефіцієнт `a₀ = 0`, що зберігається при дії `T_p` (`b₀ = a₀ + pᵏ⁻¹ a₀ = 0`). Для рядів Ейзенштейна вільний член `b₀ = 1 + pᵏ⁻¹`, що відображає підсумовування постійної складової.
- **Граничні виходи за межі масиву `n · p > max_deg`:** При обчисленні `term1 = a[n * p]` індекс `n * p` може перевищити зафіксовану довжину масиву `max_deg`. У реалізації це захищено перевіркою `n * p <= max_deg`, повертаючи `0` для відсутніх степеней.
- **Ділення на прості числа для подільних рівнів:** Для форм рівня `N > 1` оператор Гекке `T_p` при `p | N` замінюється на оператор Аткіна-Ленера `U_p`, у якому другий доданок `pᵏ⁻¹ a_{n/p}` відсутній, що вимагає розгалуження алгоритму залежно від НСД `gcd(p, N)`.
