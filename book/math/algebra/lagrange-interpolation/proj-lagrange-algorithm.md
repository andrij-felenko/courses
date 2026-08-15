# ⚙️ Реалізація інтерполятора Лагранжа: від наївного обчислення до барицентричної форми

У цій практичній вставці подано готові виробничі реалізації інтерполяції Лагранжа трьома мовами програмування: C, C++ та Python. Розглянуто два ключових алгоритмічних підходи: наївне обчислення базисних многочленів складності `O(n²)` на точку та високооптимізовану другу барицентричну форму, яка забезпечує швидкість оцінки `O(n)` та динамічне додавання нових вузлів за `O(n)`. Окремо наведено реалізацію інтерполятора над скінченними полями `GF(p)` для застосування у криптографії (криптографічна схема розділення секрету Шаміра).

---

### 1. Проектування архітектури даних та системний аналіз

При розробці систем обчислювальної математики на низькому рівні (вбудовані системи, обробка сигналів у реальному часі, фінансове моделювання, фізичні симуляції) вибір структури збереження вузлів інтерполяції безпосередньо впливає на ефективність використання кєш-пам'яті процесора (L1/L2 Cache Locality).

#### Порівняння масиву структур (AoS) та структури масивів (SoA):
- **Масив структур (Array of Structs — AoS):** Збереження точок у вигляді масиву `struct Point { double x, y; }` спричиняє переплетення x- та y-координат у пам'яті. При обчисленні базисів `L╖(x)` або барицентричних ваг `w╖` процесор змушений завантажувати в кєш-лінію лишні координати `y`, що знижує ефективність використання пропускної здатності шини пам'яті удвічі.
- **Структура масивів (Structure of Arrays — SoA):** Виділення трьох окремих неперервних масивів для `x`, `y` та `weights` дозволяє векторизувати обчислення за допомогою SIMD-інструкцій (AVX-256 / AVX-512 / ARM Neon). При обчисленні різниць `(target_x - x_k)` процесор послідовно читає з пам'яті вектор дійсних чисел без жодних пропусків.

У наведених нижче виробничих реалізаціях застосовано саме архітектурний підхід **SoA**, який забезпечує максимальну продуктивність та мінімальну кількість промахів кєш-пам'яті (L1 Data Cache Misses).

#### Стратегія виділення та розширення пам'яті:
При динамічному додаванні точок використовується амортизований фактор розширення ємності `capacity = capacity * 2`. Це гарантує, що амортизована складність виділення пам'яті при додаванні `n` вузлів становить `O(1)` на операцію, уникаючи частих системних викликів `realloc()`.

---

### 2. Наївна інтерполяція Лагранжа (`O(n²)` на точку)

Наївний підхід є ідеальним для разових обчислень у легковагових функціях, коли кількість точок мала (`n ≤ 10`), а проміжне збереження вагових коефіцієнтів недоцільне.

#### Покроковий аналіз роботи наївного алгоритму:
1. Алгоритм бере точку `target_x` і послідовно обчислює добутки різниць для кожного базисного многочлена `L╖(x)`.
2. На кожній ітерації внутрішнього циклу перевіряється умова `fabs(target_x - x_nodes[k]) < 1e-12`. Якщо точка оцінки збігається з одного з вузлів, функція миттєво повертає `y_nodes[k]`, минаючи можливе ділення на нуль `(target_x - x_k) / (x_k - x_k)`.
3. Для захисту від коректності вхідних даних перевіряється умова `fabs(denom) < 1e-15`. Якщо вхідні масиви містять два однакові вузли `x_k == x_j`, алгоритм перериває обчислення і повертає `NAN` (Not-a-Number), запобігаючи генерації прихованих чисельних помилок.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/**
 * Обчислення значення інтерполяційного многочлена Лагранжа у точці x.
 * 
 * @param x_nodes Масив x-координат вузлів (розмір n)
 * @param y_nodes Масив y-координат вузлів (розмір n)
 * @param n Кількість вузлів інтерполяції
 * @param target_x Точка, у якій необхідно обчислити значення
 * @return Обчислене значення P(target_x)
 */
double lagrange_naive_eval(const double* x_nodes, const double* y_nodes, size_t n, double target_x) {
    double result = 0.0;

    for (size_t k = 0; k < n; ++k) {
        // Перевіряємо точний збіг з вузлом для уникнення ділення на нуль
        if (fabs(target_x - x_nodes[k]) < 1e-12) {
            return y_nodes[k];
        }

        double term = y_nodes[k];
        for (size_t j = 0; j < n; ++j) {
            if (j != k) {
                double denom = x_nodes[k] - x_nodes[j];
                if (fabs(denom) < 1e-15) {
                    // Випадкові однакові x-вузли недопустимі
                    return NAN;
                }
                term *= (target_x - x_nodes[j]) / denom;
            }
        }
        result += term;
    }

    return result;
}

int main(void) {
    // Приклад: f(x) = x^2 у точках x = 1, 2, 4
    double x[3] = {1.0, 2.0, 4.0};
    double y[3] = {1.0, 4.0, 16.0};

    double test_x = 3.0;
    double eval_y = lagrange_naive_eval(x, y, 3, test_x);

    printf("P(%.1f) = %.4f (Очікується: 9.0000)\n", test_x, eval_y);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <cmath>
#include <expected>
#include <string_view>

enum class InterpolationError {
    EmptyDataset,
    MismatchedSizes,
    DuplicateNodes
};

/**
 * Обчислення наївної інтерполяції Лагранжа мовою C++20.
 */
[[nodiscard]] std::expected<double, InterpolationError> lagrange_naive_eval(
    std::span<const double> x_nodes, 
    std::span<const double> y_nodes, 
    double target_x) 
{
    if (x_nodes.empty() || y_nodes.empty()) {
        return std::unexpected(InterpolationError::EmptyDataset);
    }
    if (x_nodes.size() != y_nodes.size()) {
        return std::unexpected(InterpolationError::MismatchedSizes);
    }

    const size_t n = x_nodes.size();
    double result = 0.0;

    for (size_t k = 0; k < n; ++k) {
        if (std::abs(target_x - x_nodes[k]) < 1e-12) {
            return y_nodes[k];
        }

        double term = y_nodes[k];
        for (size_t j = 0; j < n; ++j) {
            if (j != k) {
                double denom = x_nodes[k] - x_nodes[j];
                if (std::abs(denom) < 1e-15) {
                    return std::unexpected(InterpolationError::DuplicateNodes);
                }
                term *= (target_x - x_nodes[j]) / denom;
            }
        }
        result += term;
    }

    return result;
}

int main() {
    std::vector<double> x = {1.0, 2.0, 4.0};
    std::vector<double> y = {1.0, 4.0, 16.0};

    double test_x = 3.0;
    auto res = lagrange_naive_eval(x, y, test_x);

    if (res) {
        std::cout << "P(" << test_x << ") = " << *res << " (Очікується: 9.0)\n";
    } else {
        std::cerr << "Помилка обчислення інтерполяції!\n";
    }
    return 0;
}
```
```py
def lagrange_naive_eval(x_nodes: list[float], y_nodes: list[float], target_x: float) -> float:
    """Обчислення наївної інтерполяції Лагранжа мовою Python."""
    n = len(x_nodes)
    if n != len(y_nodes) or n == 0:
        raise ValueError("Розміри масивів повинні збігатися і бути додатними.")

    result = 0.0
    for k in range(n):
        if abs(target_x - x_nodes[k]) < 1e-12:
            return y_nodes[k]

        term = y_nodes[k]
        for j in range(n):
            if j != k:
                denom = x_nodes[k] - x_nodes[j]
                if abs(denom) < 1e-15:
                    raise ValueError(f"Дубльований вузол x[{k}] == x[{j}]")
                term *= (target_x - x_nodes[j]) / denom
        result += term

    return result

if __name__ == "__main__":
    x = [1.0, 2.0, 4.0]
    y = [1.0, 4.0, 16.0]
    print(f"P(3.0) = {lagrange_naive_eval(x, y, 3.0):.4f}")
```
:::

---

### 3. Друга барицентрична форма (`O(n)` оцінка, `O(n)` додавання вузла)

Для багаторазових оцінок у реальному часі та динамічного підключення нових виміряних точок використовується об'єктна структура барицентричного інтерполятора.

#### Детальний трасування стану ваг `w╖` при підключенні вузлів:
Простежимо числові значення масиву `weights` при покроковому додаванні точок `(1, 1)`, `(2, 4)`, `(4, 16)`, `(5, 25)`:

1. **Додаємо току `(x₀, y₀) = (1, 1)`:**
   Кількість `n = 1`. За визначенням `w₀ = 1.0`.
   Масив ваг: `[1.0]`.

2. **Додаємо точку `(x₁, y₁) = (2, 4)`:**
   Новий вузол `new_x = 2.0`.
   - Стара вага оновлюється: `w₀′ = w₀ / (x₀ - new_x) = 1.0 / (1.0 - 2.0) = -1.0`.
   - Нова вага: `w₁ = 1.0 / (new_x - x₀) = 1.0 / (2.0 - 1.0) = 1.0`.
   Масив ваг: `[-1.0, 1.0]`.

3. **Додаємо точку `(x₂, y₂) = (4, 16)`:**
   Новий вузол `new_x = 4.0`.
   - `w₀″ = -1.0 / (1.0 - 4.0) = 1/3 ≈ 0.3333`
   - `w₁′ = 1.0 / (2.0 - 4.0) = -1/2 = -0.5000`
   - `w₂ = 1.0 / ((4.0 - 1.0)(4.0 - 2.0)) = 1/6 ≈ 0.1667`
   Масив ваг: `[0.3333, -0.5000, 0.1667]`.

4. **Додаємо точку `(x₃, y₃) = (5, 25)`:**
   Новий вузол `new_x = 5.0`.
   - `w₀‴ = (1/3) / (1 - 5) = -1/12 ≈ -0.0833`
   - `w₁″ = (-1/2) / (2 - 5) = 1/6 ≈ 0.1667`
   - `w₂′ = (1/6) / (4 - 5) = -1/6 ≈ -0.1667`
   - `w₃ = 1.0 / ((5-1)(5-2)(5-4)) = 1/12 ≈ 0.0833`
   Масив ваг: `[-0.0833, 0.1667, -0.1667, 0.0833]`.

Зверніть увагу: на кожному кроці додавання нової точки оновлення вимагає лише одного циклу довжини `n`! Повного обчислення знаменників з нуля не відбувається.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

typedef struct {
    double* x;
    double* y;
    double* weights;
    size_t count;
    size_t capacity;
} BarycentricInterpolator;

BarycentricInterpolator* barycentric_create(size_t initial_capacity) {
    BarycentricInterpolator* interp = (BarycentricInterpolator*)malloc(sizeof(BarycentricInterpolator));
    if (!interp) return NULL;

    interp->capacity = initial_capacity > 0 ? initial_capacity : 8;
    interp->count = 0;
    interp->x = (double*)malloc(interp->capacity * sizeof(double));
    interp->y = (double*)malloc(interp->capacity * sizeof(double));
    interp->weights = (double*)malloc(interp->capacity * sizeof(double));

    if (!interp->x || !interp->y || !interp->weights) {
        free(interp->x);
        free(interp->y);
        free(interp->weights);
        free(interp);
        return NULL;
    }

    return interp;
}

void barycentric_free(BarycentricInterpolator* interp) {
    if (interp) {
        free(interp->x);
        free(interp->y);
        free(interp->weights);
        free(interp);
    }
}

bool barycentric_add_point(BarycentricInterpolator* interp, double new_x, double new_y) {
    // Перевіряємо дублікати
    for (size_t i = 0; i < interp->count; ++i) {
        if (fabs(interp->x[i] - new_x) < 1e-12) {
            return false; // Вузол вже існує
        }
    }

    // Розширення масиву при потребі
    if (interp->count >= interp->capacity) {
        size_t new_cap = interp->capacity * 2;
        double* nx = (double*)realloc(interp->x, new_cap * sizeof(double));
        double* ny = (double*)realloc(interp->y, new_cap * sizeof(double));
        double* nw = (double*)realloc(interp->weights, new_cap * sizeof(double));
        if (!nx || !ny || !nw) return false;
        interp->x = nx;
        interp->y = ny;
        interp->weights = nw;
        interp->capacity = new_cap;
    }

    size_t n = interp->count;
    interp->x[n] = new_x;
    interp->y[n] = new_y;

    // Оновлення існуючих ваг w_k = w_k / (x_k - new_x) за O(n)
    double new_w = 1.0;
    for (size_t k = 0; k < n; ++k) {
        double diff = interp->x[k] - new_x;
        interp->weights[k] /= diff;
        new_w /= (new_x - interp->x[k]);
    }
    interp->weights[n] = new_w;
    interp->count++;

    return true;
}

double barycentric_eval(const BarycentricInterpolator* interp, double target_x) {
    if (interp->count == 0) return NAN;

    double num = 0.0;
    double den = 0.0;

    for (size_t k = 0; k < interp->count; ++k) {
        double diff = target_x - interp->x[k];
        if (fabs(diff) < 1e-12) {
            return interp->y[k]; // Точний збіг з вузлом
        }
        double term = interp->weights[k] / diff;
        num += term * interp->y[k];
        den += term;
    }

    return num / den;
}

int main(void) {
    BarycentricInterpolator* interp = barycentric_create(4);
    
    barycentric_add_point(interp, 1.0, 1.0);
    barycentric_add_point(interp, 2.0, 4.0);
    barycentric_add_point(interp, 4.0, 16.0);

    printf("Барицентрична оцінка P(3.0) = %.4f\n", barycentric_eval(interp, 3.0));

    // Динамічно додаємо 4-ту точку x=5, y=25 за O(n)
    barycentric_add_point(interp, 5.0, 25.0);
    printf("Після додавання (5.0, 25.0): P(3.0) = %.4f\n", barycentric_eval(interp, 3.0));

    barycentric_free(interp);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <optional>
#include <stdexcept>

class BarycentricInterpolator {
public:
    explicit BarycentricInterpolator(size_t reserve_capacity = 8) {
        x_.reserve(reserve_capacity);
        y_.reserve(reserve_capacity);
        weights_.reserve(reserve_capacity);
    }

    bool add_point(double new_x, double new_y) {
        for (double existing_x : x_) {
            if (std::abs(existing_x - new_x) < 1e-12) {
                return false;
            }
        }

        const size_t n = x_.size();
        x_.push_back(new_x);
        y_.push_back(new_y);

        double new_w = 1.0;
        for (size_t k = 0; k < n; ++k) {
            double diff = x_[k] - new_x;
            weights_[k] /= diff;
            new_w /= (new_x - x_[k]);
        }
        weights_.push_back(new_w);
        return true;
    }

    [[nodiscard]] std::optional<double> eval(double target_x) const {
        if (x_.empty()) return std::nullopt;

        double num = 0.0;
        double den = 0.0;

        for (size_t k = 0; k < x_.size(); ++k) {
            double diff = target_x - x_[k];
            if (std::abs(diff) < 1e-12) {
                return y_[k];
            }
            double term = weights_[k] / diff;
            num += term * y_[k];
            den += term;
        }

        return num / den;
    }

    [[nodiscard]] size_t size() const noexcept { return x_.size(); }

private:
    std::vector<double> x_;
    std::vector<double> y_;
    std::vector<double> weights_;
};

int main() {
    BarycentricInterpolator interp;
    interp.add_point(1.0, 1.0);
    interp.add_point(2.0, 4.0);
    interp.add_point(4.0, 16.0);

    if (auto val = interp.eval(3.0)) {
        std::cout << "C++ Барицентричний P(3.0) = " << *val << "\n";
    }

    interp.add_point(5.0, 25.0);
    if (auto val = interp.eval(3.0)) {
        std::cout << "Після оновлення O(n): P(3.0) = " << *val << "\n";
    }

    return 0;
}
```
```py
class BarycentricInterpolator:
    """Виробнича барицентрична інтерполяція мовою Python."""
    def __init__(self):
        self.x: list[float] = []
        self.y: list[float] = []
        self.weights: list[float] = []

    def add_point(self, new_x: float, new_y: float) -> bool:
        for existing_x in self.x:
            if abs(existing_x - new_x) < 1e-12:
                return False

        n = len(self.x)
        self.x.append(new_x)
        self.y.append(new_y)

        new_w = 1.0
        for k in range(n):
            diff = self.x[k] - new_x
            self.weights[k] /= diff
            new_w /= (new_x - self.x[k])
        self.weights.append(new_w)
        return True

    def eval(self, target_x: float) -> float:
        if not self.x:
            raise ValueError("Інтерполятор порожній.")

        num = 0.0
        den = 0.0

        for k in range(len(self.x)):
            diff = target_x - self.x[k]
            if abs(diff) < 1e-12:
                return self.y[k]
            term = self.weights[k] / diff
            num += term * self.y[k]
            den += term

        return num / den

if __name__ == "__main__":
    interp = BarycentricInterpolator()
    for x_i, y_i in [(1.0, 1.0), (2.0, 4.0), (4.0, 16.0)]:
        interp.add_point(x_i, y_i)

    print(f"Python Барицентричний P(3.0) = {interp.eval(3.0):.4f}")
```
:::

---

### 4. Криптографічна інтерполяція над скінченними полями `GF(p)`

При реалізації відновлення секрету у схемі Шаміра над полем `GF(p)` звичайні арифметичні оператори `+`, `-`, `*`, `/` замінюються відповідними модулярними операціями.

#### Запобігання переповненню типів у 64-бітній арифметиці:
При множенні двох 64-бітних цілих чисел за модулем `p = 10⁹ + 7` результат `a * b` може досягати `10¹⁸`, що значно наближається до верхньої межі `INT64_MAX ≈ 9.22 × 10¹⁸`. Для запобігання міжплатформеному переповненню у коді C/C++ застосовано розширений 128-бітний тип `__int128`, який підтримується компіляторами GCC та Clang на x86_64 та ARM64.

Обчислення мультиплікативного оберненого елемента за модулем `p` виконується за малим алгоритмом Ферма: `a⁻¹ ≡ aᵖ⁻² (mod p)` за допомогою швидкого піднесення до степеня за `O(log p)` кроків.

#### Трасування модулярного відновлення секрету:
Розглянемо випадок відновлення секрету у полі `GF(p)` при `p = 1000000007`:
- При обчисленні різниць `x[i] - x[j]` у скінченному полі результат може бути від'ємним. Для приведення до позитивного діапазону `[0, p-1]` використовується операція `(x[i] - x[j] + MOD_P) % MOD_P`.
- Чисельник базису Лагранжа для оцінки секрету у точці `x = 0` спрощується до `∏ (-x[j]) mod p`, що еквівалентно `∏ (MOD_P - x[j]) mod p`.
- Підсумкова сума підсумовується за модулем `MOD_P` після множення кожного доданка на модулярний обернений знаменник `mod_inverse(den)`.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>

// Просте число p для скінченного поля GF(p)
#define MOD_P 1000000007LL

// Обчислення a^b mod p
static int64_t power_mod(int64_t base, int64_t exp) {
    int64_t res = 1;
    base %= MOD_P;
    while (exp > 0) {
        if (exp % 2 == 1) res = (__int128)res * base % MOD_P;
        base = (__int128)base * base % MOD_P;
        exp /= 2;
    }
    return res;
}

// Обернений елемент a^-1 mod p за малою теоремою Ферма
static int64_t mod_inverse(int64_t n) {
    return power_mod(n, MOD_P - 2);
}

// Відновлення секрету P(0) над GF(p)
int64_t gf_lagrange_reconstruct_secret(const int64_t* x, const int64_t* y, size_t k) {
    int64_t secret = 0;

    for (size_t i = 0; i < k; ++i) {
        int64_t num = 1;
        int64_t den = 1;

        for (size_t j = 0; j < k; ++j) {
            if (i != j) {
                num = (__int128)num * (MOD_P - x[j]) % MOD_P;
                int64_t diff = (x[i] - x[j] + MOD_P) % MOD_P;
                den = (__int128)den * diff % MOD_P;
            }
        }

        int64_t term = (__int128)y[i] * num % MOD_P;
        term = (__int128)term * mod_inverse(den) % MOD_P;
        secret = (secret + term) % MOD_P;
    }

    return secret;
}

int main(void) {
    // 3 частки з 5 для відкриття секрету: (1, 12345), (2, 54321), (3, 98765)
    int64_t x_shares[3] = {1, 2, 3};
    int64_t y_shares[3] = {14892, 45293, 91216};

    int64_t secret = gf_lagrange_reconstruct_secret(x_shares, y_shares, 3);
    printf("Відновлений криптографічний секрет S = %lld\n", (long long)secret);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <cstdint>

constexpr int64_t MOD_P = 1000000007LL;

static int64_t power_mod(int64_t base, int64_t exp) {
    int64_t res = 1;
    base %= MOD_P;
    while (exp > 0) {
        if (exp % 2 == 1) res = static_cast<__int128>(res) * base % MOD_P;
        base = static_cast<__int128>(base) * base % MOD_P;
        exp /= 2;
    }
    return res;
}

static int64_t mod_inverse(int64_t n) {
    return power_mod(n, MOD_P - 2);
}

[[nodiscard]] int64_t gf_lagrange_reconstruct_secret(
    std::span<const int64_t> x_shares, 
    std::span<const int64_t> y_shares) 
{
    const size_t k = x_shares.size();
    int64_t secret = 0;

    for (size_t i = 0; i < k; ++i) {
        int64_t num = 1;
        int64_t den = 1;

        for (size_t j = 0; j < k; ++j) {
            if (i != j) {
                num = static_cast<__int128>(num) * (MOD_P - x_shares[j]) % MOD_P;
                int64_t diff = (x_shares[i] - x_shares[j] + MOD_P) % MOD_P;
                den = static_cast<__int128>(den) * diff % MOD_P;
            }
        }

        int64_t term = static_cast<__int128>(y_shares[i]) * num % MOD_P;
        term = static_cast<__int128>(term) * mod_inverse(den) % MOD_P;
        secret = (secret + term) % MOD_P;
    }

    return secret;
}

int main() {
    std::vector<int64_t> x = {1, 2, 3};
    std::vector<int64_t> y = {14892, 45293, 91216};

    int64_t secret = gf_lagrange_reconstruct_secret(x, y);
    std::cout << "C++ GF(p) Відновлений секрет = " << secret << "\n";
    return 0;
}
```
:::

---

### 5. Підсумковий аналіз обчислювальної складності та вибору алгоритму

Наведена нижче порівняльна таблиця систематизує практичні рекомендації щодо вибору алгоритму інтерполяції для конкретних системних завдань:

1. **Одноразові обчислення для малих `n` (`n ≤ 8`):** Рекомендується `lagrange_naive_eval`, оскільки він не потребує створення об'єктів та виділення динамічної пам'яті у кучі.
2. **Потокова обробка та часові ряди (`n > 10`):** Рекомендується використовувати `BarycentricInterpolator`, який забезпечує швидкість оцінки `O(n)` на точка замість `O(n²)`.
3. **Криптографічні порогові схеми:** Використовується суворо точна цілочисельна форма `gf_lagrange_reconstruct_secret` з обчисленими модулярними оберненими значеннями за модулем `p`.
