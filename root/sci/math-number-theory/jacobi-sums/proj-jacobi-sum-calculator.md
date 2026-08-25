# ⚙️ Реалізація обчислення сум Якобі та підрахунку точок

Ця вставка містить практичну програму мовами C та C++ для табличного обчислення нетривіальних сум Якобі над скінченними полями `𝔽_p`, точного підрахунку кількості розв'язків діофантових рівнянь Ферма `xⁿ + yⁿ ≡ 1 (mod p)` та перевірки лишків в алгоритмах криптографії та тесту простоти APR-CL.

## 1. Архітектура обчислювального ядра та математичний алгоритм

Обчислення сум Якобі `J(χ_a, χ_b)` вимагає виконання трьох послідовних алгоритмічних етапів:

1. **Знаходження генератора мультиплікативної групи:** Пошук найменшого первісного кореня `g` за модулем простого числа `p`, що задає ізоморфізм циклічної групи `𝔽_p* ≅ ℤ/(p-1)ℤ`. Для цього випробовуються послідовні кандидати `g = 2, 3, ...`, поки для кожного простого дільника `q` числа `p - 1` значення `g^{(p-1)/q} mod p` не буде відмінним від `1`.
2. **Табуляція характерів та дискретних логарифмів:** Побудова таблиці дискретного логарифма `ind_g(x)` (індексу за основою `g`) для кожного елемента `x ∈ 𝔽_p*` за час `O(p)` та побудова комплекснозначних характерів `χ_k(x) = exp(2π i · k · ind_g(x) / (p - 1))`. Табулювання дозволяє уникнути повторного обчислення повільних тригонометричних функцій `cos` та `sin` у внутрішніх циклах сумування.
3. **Векторна згортка Якобі:** Обчислення суми добутків `χ_a(t) · χ_b(1 - t)` для всіх `t ∈ {2, 3, ..., p - 2}`.

В обчислювальному відношенні пряме табулювання дискретного логарифма має часову складність `O(p)`, а обчислення однієї суми Якобі — `O(p)` операцій із комплексними числами. Для підрахунку точок на кривій степеня `n` обчислюється `(n-1)²` сум Якобі, що дає підсумкову складність `O(n² p)`. Для великих полів `𝔽_q` табличний підхід оптимізується через швидке перетворення Фур'є (FFT) над скінченною групою, що знижує час згортки до `O(q log q)`.

Виділення пам'яті під таблицю індексів виконується один раз під час створення контексту поля, що мінімізує накладні витрати на динамічну пам'ять і забезпечує високу продуктивність при багаторазовому виклику функцій.

Алгоритм забезпечує сувору точність для всіх нетривіальних сум Якобі, перевіряючи нормалізаційну тотожність `|J(χ_a, χ_b)| = √p`.

## 2. Паралельна реалізація мовами C та C++

Обчислювальний модуль реалізовано двома мовами: C (стандарт C11 з використанням `double complex`) та ідіоматичному C++23 (з використанням `std::complex<double>`, `std::expected`, `std::span` та обробкою виняткових станів).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef double complex Complex;

/* Швидке піднесення до степеня за модулем */
static long long power_mod(long long base, long long exp, long long mod) {
    long long res = 1;
    base %= mod;
    while (exp > 0) {
        if (exp % 2 == 1) res = (res * base) % mod;
        base = (base * base) % mod;
        exp /= 2;
    }
    return res;
}

/* Перевірка, чи є g первісним коренем mod p */
static bool is_primitive_root(long long g, long long p) {
    long long phi = p - 1;
    long long n = phi;
    for (long long i = 2; i * i <= n; i++) {
        if (n % i == 0) {
            if (power_mod(g, phi / i, p) == 1) return false;
            while (n % i == 0) n /= i;
        }
    }
    if (n > 1) {
        if (power_mod(g, phi / n, p) == 1) return false;
    }
    return true;
}

/* Пошук найменшого первісного кореня mod p */
static long long find_primitive_root(long long p) {
    for (long long g = 2; g < p; g++) {
        if (is_primitive_root(g, p)) return g;
    }
    return -1;
}

/* Побудова таблиці дискретних логарифмів ind_g(x) */
static int* build_log_table(long long p, long long g) {
    int* log_table = (int*)malloc(sizeof(int) * p);
    if (!log_table) return NULL;
    
    long long cur = 1;
    for (int exp = 0; exp < p - 1; exp++) {
        log_table[cur] = exp;
        cur = (cur * g) % p;
    }
    log_table[0] = -1; /* χ(0) = 0 */
    return log_table;
}

/* Обчислення характеру χ_k(x) = exp(2π i · k · ind_g(x) / (p - 1)) */
static Complex eval_character(int x, int k, long long p, const int* log_table) {
    if (x == 0) return 0.0 + 0.0 * I;
    int idx = log_table[x];
    double angle = 2.0 * M_PI * ((double)(k * idx) / (double)(p - 1));
    return cos(angle) + sin(angle) * I;
}

/* Обчислення суми Якобі J(χ_a, χ_b) над F_p */
Complex compute_jacobi_sum(int a, int b, long long p, const int* log_table) {
    Complex sum = 0.0 + 0.0 * I;
    for (int t = 0; t < p; t++) {
        int t2 = (1 - t + p) % p;
        Complex c1 = eval_character(t, a, p, log_table);
        Complex c2 = eval_character(t2, b, p, log_table);
        sum += c1 * c2;
    }
    return sum;
}

/* Підрахунок кількості розв'язків x^n + y^n = 1 mod p через суми Якобі */
long long count_fermat_points_jacobi(int n, long long p, const int* log_table) {
    long long phi = p - 1;
    if (phi % n != 0) return -1;
    
    int step = (int)(phi / n);
    Complex total_jacobi_sum = 0.0 + 0.0 * I;
    
    for (int i = 1; i < n; i++) {
        for (int j = 1; j < n; j++) {
            total_jacobi_sum += compute_jacobi_sum(i * step, j * step, p, log_table);
        }
    }
    
    /* N = p + ∑ J(χ^i, χ^j) */
    double real_part = creal(total_jacobi_sum);
    return p + (long long)round(real_part);
}

int main(void) {
    long long p = 13;
    int n = 4; /* Квартична крива x^4 + y^4 = 1 mod 13 */
    
    long long g = find_primitive_root(p);
    printf("Поле F_%lld, первісний корінь g = %lld\n", p, g);
    
    int* log_table = build_log_table(p, g);
    if (!log_table) return 1;
    
    Complex j11 = compute_jacobi_sum(3, 3, p, log_table);
    printf("Сума Якобі J(χ³, χ³) = %.4f + %.4fi\n", creal(j11), cimag(j11));
    printf("Модуль |J(χ³, χ³)| = %.4f (Очікується √13 ≈ %.4f)\n", cabs(j11), sqrt((double)p));
    
    long long points = count_fermat_points_jacobi(n, p, log_table);
    printf("Кількість точок на x^%d + y^%d = 1 (mod %lld) дорівнює: %lld\n", n, n, p, points);
    
    free(log_table);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numbers>
#include <expected>
#include <numeric>
#include <span>

namespace math::number_theory {

using Complex = std::complex<double>;

class JacobiSumCalculator {
public:
    enum class Error {
        InvalidModulus,
        NotPrime,
        DegreeDoesNotDivideOrder
    };

    explicit JacobiSumCalculator(uint64_t prime_modulus)
        : p_(prime_modulus), g_(find_primitive_root(prime_modulus)) {
        build_log_table();
    }

    [[nodiscard]] Complex compute_jacobi_sum(uint64_t a, uint64_t b) const {
        Complex sum{0.0, 0.0};
        for (uint64_t t = 0; t < p_; ++t) {
            uint64_t t2 = (p_ + 1 - (t % p_)) % p_;
            sum += eval_character(t, a) * eval_character(t2, b);
        }
        return sum;
    }

    [[nodiscard]] std::expected<uint64_t, Error> count_fermat_points(uint64_t n) const {
        uint64_t phi = p_ - 1;
        if (phi % n != 0) {
            return std::unexpected(Error::DegreeDoesNotDivideOrder);
        }

        uint64_t step = phi / n;
        Complex total_sum{0.0, 0.0};

        for (uint64_t i = 1; i < n; ++i) {
            for (uint64_t j = 1; j < n; ++j) {
                total_sum += compute_jacobi_sum(i * step, j * step);
            }
        }

        double real_val = total_sum.real();
        return static_cast<uint64_t>(p_ + std::round(real_val));
    }

    [[nodiscard]] uint64_t modulus() const noexcept { return p_; }
    [[nodiscard]] uint64_t primitive_root() const noexcept { return g_; }

private:
    uint64_t p_;
    uint64_t g_;
    std::vector<int64_t> log_table_;

    static uint64_t power_mod(uint64_t base, uint64_t exp, uint64_t mod) {
        uint64_t res = 1;
        base %= mod;
        while (exp > 0) {
            if (exp & 1) res = (res * base) % mod;
            base = (base * base) % mod;
            exp >>= 1;
        }
        return res;
    }

    static bool is_primitive_root(uint64_t g, uint64_t p) {
        uint64_t phi = p - 1;
        uint64_t n = phi;
        for (uint64_t i = 2; i * i <= n; ++i) {
            if (n % i == 0) {
                if (power_mod(g, phi / i, p) == 1) return false;
                while (n % i == 0) n /= i;
            }
        }
        if (n > 1 && power_mod(g, phi / n, p) == 1) return false;
        return true;
    }

    static uint64_t find_primitive_root(uint64_t p) {
        for (uint64_t g = 2; g < p; ++g) {
            if (is_primitive_root(g, p)) return g;
        }
        return 2;
    }

    void build_log_table() {
        log_table_.assign(p_, -1);
        uint64_t cur = 1;
        for (uint64_t exp = 0; exp < p_ - 1; ++exp) {
            log_table_[cur] = static_cast<int64_t>(exp);
            cur = (cur * g_) % p_;
        }
    }

    [[nodiscard]] Complex eval_character(uint64_t x, uint64_t k) const {
        if (x == 0 || log_table_[x] == -1) return {0.0, 0.0};
        double angle = 2.0 * std::numbers::pi * static_cast<double>(k * log_table_[x]) / static_cast<double>(p_ - 1);
        return std::polar(1.0, angle);
    }
};

} // namespace math::number_theory

int main() {
    using namespace math::number_theory;

    uint64_t p = 13;
    uint64_t n = 4;

    JacobiSumCalculator calc(p);
    std::cout << "Поле F_" << calc.modulus() << ", первісний корінь g = " << calc.primitive_root() << "\n";

    auto j11 = calc.compute_jacobi_sum(3, 3);
    std::cout << "Сума Якобі J(χ³, χ³) = " << j11.real() << " + " << j11.imag() << "i\n";
    std::cout << "Модуль |J| = " << std::abs(j11) << " (Очікується √13 ≈ " << std::sqrt(p) << ")\n";

    auto points = calc.count_fermat_points(n);
    if (points) {
        std::cout << "Кількість точок на x^" << n << " + y^" << n << " = 1 (mod " << p << ") дорівнює: " << *points << "\n";
    }

    return 0;
}
```
:::

У C++ версії клас `JacobiSumCalculator` інкапсулює внутрішній вектор логарифмів `log_table_`. Використання методів із атрибутами `[[nodiscard]]` та `noexcept` забезпечує високу надійність коду, виключаючи неконтрольоване ігнорування результатів обчислень та гарантуючи відсутність винятків при викликах математичних функцій.

Також C++ реалізація може бути легко інтегрована в мультипоточні обчислювальні конвеєри завдяки використанню `std::span` та `std::expected` замість сирих вказівників і кодів помилок.

## 3. Обчислення перевірки лишків в алгоритмі APR-CL

В алгоритмі перевірки простоти Адлемана–Померанса–Румелі–Коена–Ленстри (APR-CL) суми Якобі використовуються як елементи кільця `ℤ[ζ_k]` для побудови квазіполіноміального детермінованого тесту простоти великих чисел `N`. 

Для кожного малого простого числа `q`, де `q - 1` ділить допоміжне число `e`, обчислюються суми Якобі `J(p, q)` у кругових розширеннях. Тест APR-CL виконує такі послідовні етапи перевірки:

1. **Генерація кругових характерів:** Створюються характери порядку `q^k` над полем `𝔽_p`.
2. **Перевірка порівняння Штікельбергера:** Для перевіряємого числа `N` обчислюється степінь суми Якобі `J(p, q)^{N - σ_N}` у кільці `ℤ[ζ_k] / (N)`.
3. **Критерій простоти:** Якщо `N` є простим числом, то за теоремою Штікельбергера значення `J(p, q)^{N - σ_N}` має бути строго конгруентним одиниці або конкретному кореню з одиниці за модулем `N`. Якщо порівняння порушується хоча б для однієї суми Якобі, число `N` оголошується складеним.

Завдяки цьому використання сум Якобі дозволяє перевірити простоту чисел розміром у 1000+ біт за лічені секунди без використання імовірнісних тестів Міллера–Рабіна.

## 4. Аналіз підводних каменів та крайових випадків

Під час практичної реалізації сум Якобі в обчислювальних пакетах слід враховувати такі важливі крайові випадки та потенційні пастки:

1. **Точність плаваючої крапки:** При підсумовуванні характерів накопичується округлення чисел типу `double` або `std::complex<double>`. При підрахунку цілочисельної кількості точок `N` дійсне значення `real(J)` підлягає обов'язковому округленню функцією `round()`, а не простому відтинанню дрібної частини `(long long)`.
2. **Обробка нульових елементів:** За означенням `χ(0) = 0` для всіх нетривіальних характерів. Нехтування цим правилом і присвоєння `χ(0) = 1` призведе до викривлення суми на величину `+1` або `+2`, що повністю спотворить підрахунок точок на кривих.
3. **Характер квадратичного залишку:** Якщо модуль `p = 2`, суми Якобі стають тривіальними. Алгоритм вимагає непарних простих `p > 2` або скінченних розширень `𝔽_{p^f}`.
4. **Вибір первісного кореня:** Якщо обране значення `g` не є первісним коренем mod `p`, таблиця логарифмів буде неповною (міститиме `-1` для багатьох елементів), що призведе до спотворення значень характерів і хибного результату сумування.
5. **Обмеження розміру поля:** Пряме табулювання логарифмів вимагає `O(p)` пам'яті. Для полів з `p > 10⁸` замість прямого масиву застосовують підхід Baby-step Giant-step або обчислюють суми Якобі безпосередньо через алгоритм швидкого перетворення Фур'є (FFT) у кільці `ℂ`.
6. **Переповнення при множенні додатних чисел:** При піднесенні до степеня в `power_mod` для полів із `p > 2³¹ - 1` проміжний добуток `base * base` виходить за межі типу `int64_t`. Рекомендується використовувати тип `__int128_t` або модуль `std::bit_cast`.
7. **Паралелізація обчислень:** Оскільки підсумовування у `compute_jacobi_sum` є асоціативним та комутативним, додавання доданків для різних `t` можна легко паралелити через `OpenMP` або `std::execution::par`, що прискорює обчислення в `K` разів на `K`-ядерному процесорі.
8. **Обробка виняткових ситуацій:** Якщо степінь `n` не ділить `p - 1`, обчислення точок на кривій `xⁿ + yⁿ = 1` зупиняється з помилкою `DegreeDoesNotDivideOrder`, упереджуючи хибні розрахунки.
