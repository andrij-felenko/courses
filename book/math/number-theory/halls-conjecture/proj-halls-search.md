# ⚙️ Алгоритм пошуку рекордно близьких пар (x, y) для гіпотези Холла

<preknowlist>
- [Гіпотеза Холла](book:math/halls-conjecture) — асимптотична оцінка відстані між точними квадратами та кубами.
- [Рівняння Пелля](book:math/pell-equation) — нескінченні серії цілочисельних розв'язків квадратичних рівнянь.
</preknowlist>

Обчислювальний пошук цілочисельних пар `(x, y)`, які мінімізують відношення `|y² - x³| / √x` та утворюють екстремальні приклади для гіпотези Холла, вимагає ефективної алгоритмічної реалізації. Практична побудова такого пошуку охоплює програмну реалізацію мовами C та C++ з використанням 128-бітної арифметики для запобігання переповненню при піднесенні великих чисел до куба та квадрата, аналіз продуктивності на рівні регістрів процесора та розбір ізотеричних алгоритмів Елкіса.

## Постановка задачі та математична оптимізація

Для заданої верхньої межі `X_max` необхідно знайти всі пари натуральних чисел `(x, y)` такі, що `x ≤ X_max`, `y² ≠ x³`, і відношення

```
r(x, y) = |y² - x³| / √x
```

є меншим за задане порогове значення `R_threshold` (наприклад, `R_threshold = 0.5`).

Прямий перебір двох змінних `x` та `y` мав би складність `O(X_max · Y_max) = O(X_max⁵/²)`. При `X_max = 10⁷` це вимагало б виконання понад `10¹⁷` операцій, що зайняло б кілька років роботи потужного обчислювального кластера.

Оптимізація полягає у використанні монотонності квадратичної функції. Для кожного фіксованого значення `x` шукане значення `y` має бути найближчим цілим числом до дійсного значення `x³/² = x · √x`. Оскільки функція `f(y) = y² - x³` є строго зростаючою для `y > 0`, значення `y`, яке мінімізує різницю `|y² - x³|`, може набувати лише двох можливих цілочисельних значень:

```
y_base = ⌊x · √x⌋
y_candidate₁ = y_base
y_candidate₂ = y_base + 1
```

Такий підхід зменшує обчислювальну складність алгоритму до `O(X_max)`. Для перевірки одного значення `x` потрібно лише обчислити дійсний квадратний корінь `√x`, округлити результат і перевірити два сусідні цілочисельні значення `y`.

## Проблема діапазону значень та 128-бітна арифметика

При обчисленні `x³` та `y²` ми швидко стикаємося з обмеженнями розрядності процесора:

- Для `x = 10⁶`: `x³ = 10¹⁸`. Це значення ще вміщується у стандартний 64-бітний беззнаковий цілочисельний тип `uint64_t`, максимальне значення якого становить `2⁶⁴ - 1 ≈ 1.84 × 10¹⁹`.
- Для `x = 10⁷`: `x³ = 10²¹`. Це значення в 50 разів перевищує верхню межу 64-бітного цілого числа. Піднесення до куба викликає цілочисельне переповнення (integer overflow), що призводить до відкидання старших бітів і створення хибних результатів.

Для вирішення цієї проблеми у програмі використовується 128-бітний цілочисельний тип даних (`__int128_t` в C або `unsigned __int128` в C++), який підтримується компіляторами GCC та Clang на 64-бітних архітектурах x86-64 та AArch64. 

Максимальне значення 128-бітного беззнакового числа становить:

```
2¹²⁸ - 1 ≈ 3.4028 × 10³⁸
```

Це дозволяє виконувати точне обчислення кубів `x³` без втрати жодного біта для значень `x` аж до:

```
x_max = ∛(2¹²⁸ - 1) ≈ ∛(3.4 × 10³⁸) ≈ 6.98 × 10¹²
```

На рівні ассемблерного коду x86-64 множення двох 64-бітних регістрів `rax` та `rbx` із використанням інструкції `mulx` або `imul` автоматично записує 128-бітний результат у пару 64-бітних регістрів `rdx:rax` за один інструкційний такт процесора.

## Повна реалізація алгоритму пошуку мовами C та C++

У наведеному нижче блоці коду представлена реалізація алгоритму пошуку рекордно близьких пар для гіпотези Холла. Реалізація розбита на дві незалежні вкладки: ідіоматичний C з ручним управлінням виведенням 128-бітних чисел та ідіоматичний C++20 з використанням концептів, обгортки `std::optional`, векторних контейнерів та семантики переміщення.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

// Структура для збереження знайденої кандидатури пар Холла
typedef struct {
    uint64_t x;
    uint64_t y;
    int64_t diff;
    double ratio;
} HallCandidate;

// Допоміжна функція для виведення 128-бітного цілого числа у стандартний потік
void print_int128(__int128 n) {
    if (n < 0) {
        putchar('-');
        n = -n;
    }
    if (n == 0) {
        putchar('0');
        return;
    }
    char buf[40];
    int i = 0;
    while (n > 0) {
        buf[i++] = (char)('0' + (n % 10));
        n /= 10;
    }
    while (i > 0) {
        putchar(buf[--i]);
    }
}

// Пошук кандидатури з найменшим ratio для заданого x
bool evaluate_x(uint64_t x, double threshold, HallCandidate *best_out) {
    double x_dbl = (double)x;
    double sqrt_x = sqrt(x_dbl);
    double y_ideal = x_dbl * sqrt_x;
    
    uint64_t y_base = (uint64_t)floor(y_ideal);
    bool found = false;
    double min_ratio = 1e18;
    HallCandidate best_cand = {0};

    // Перевіряємо два сусідні цілі значення: floor(y_ideal) та floor(y_ideal) + 1
    for (uint64_t dy = 0; dy <= 1; ++dy) {
        uint64_t y = y_base + dy;
        if (y == 0) continue;

        __int128 x128 = (__int128)x;
        __int128 y128 = (__int128)y;
        
        __int128 x_cube = x128 * x128 * x128;
        __int128 y_sq = y128 * y128;
        
        __int128 diff128 = y_sq - x_cube;
        if (diff128 == 0) continue; // Ігноруємо тривіальну рівність y^2 = x^3

        double abs_diff = (double)(diff128 < 0 ? -diff128 : diff128);
        double ratio = abs_diff / sqrt_x;

        if (ratio < threshold && ratio < min_ratio) {
            min_ratio = ratio;
            best_cand.x = x;
            best_cand.y = y;
            best_cand.diff = (int64_t)diff128;
            best_cand.ratio = ratio;
            found = true;
        }
    }

    if (found && best_out) {
        *best_out = best_cand;
    }
    return found;
}

int main(void) {
    uint64_t x_max = 10000000ULL; // Межа пошуку x = 10^7
    double threshold = 0.5;      // Шукаємо відношення |y^2 - x^3| / sqrt(x) < 0.5

    printf("Пошук пар Холла для x <= %llu з порогом ratio < %.2f...\n",
           (unsigned long long)x_max, threshold);

    uint64_t count = 0;
    for (uint64_t x = 2; x <= x_max; ++x) {
        HallCandidate cand;
        if (evaluate_x(x, threshold, &cand)) {
            printf("Знайдено пару #%llu: x = %llu, y = %llu, diff = %lld, ratio = %.6f\n",
                   (unsigned long long)++count,
                   (unsigned long long)cand.x,
                   (unsigned long long)cand.y,
                   (long long)cand.diff,
                   cand.ratio);
        }
    }

    printf("Пошук завершено. Знайдено аномальних пар: %llu\n", (unsigned long long)count);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <optional>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <algorithm>

// Структура для збереження результатів пошуку
struct HallCandidate {
    std::uint64_t x{0};
    std::uint64_t y{0};
    std::int64_t diff{0};
    double ratio{0.0};
};

// Клас-шукач пар з дотриманням принципів RAII та чистоти функцій
class HallSearcher {
public:
    explicit HallSearcher(double threshold) noexcept : threshold_(threshold) {}

    [[nodiscard]] std::optional<HallCandidate> inspect(std::uint64_t x) const noexcept {
        const double x_dbl = static_cast<double>(x);
        const double sqrt_x = std::sqrt(x_dbl);
        const double y_ideal = x_dbl * sqrt_x;
        const auto y_base = static_cast<std::uint64_t>(std::floor(y_ideal));

        std::optional<HallCandidate> best;
        double min_ratio = 1e18;

        for (std::uint64_t dy = 0; dy <= 1; ++dy) {
            const std::uint64_t y = y_base + dy;
            if (y == 0) continue;

            const unsigned __int128 x128 = x;
            const unsigned __int128 y128 = y;
            const unsigned __int128 x_cube = x128 * x128 * x128;
            const unsigned __int128 y_sq = y128 * y128;

            if (y_sq == x_cube) continue; // Ігноруємо тривіальні розв'язки

            const bool is_negative = (y_sq < x_cube);
            const unsigned __int128 abs_diff_128 = is_negative ? (x_cube - y_sq) : (y_sq - x_cube);
            const double abs_diff = static_cast<double>(abs_diff_128);
            const double ratio = abs_diff / sqrt_x;

            if (ratio < threshold_ && ratio < min_ratio) {
                min_ratio = ratio;
                const auto signed_diff = is_negative 
                    ? -static_cast<std::int64_t>(abs_diff_128)
                    : static_cast<std::int64_t>(abs_diff_128);

                best = HallCandidate{x, y, signed_diff, ratio};
            }
        }
        return best;
    }

    [[nodiscard]] std::vector<HallCandidate> search_range(std::uint64_t start_x, std::uint64_t end_x) const {
        std::vector<HallCandidate> results;
        results.reserve(100); // Попереднє виділення пам'яті для уникнення реалокацій
        
        for (std::uint64_t x = start_x; x <= end_x; ++x) {
            if (auto cand = inspect(x)) {
                results.push_back(*cand);
            }
        }
        return results;
    }

private:
    double threshold_;
};

int main() {
    constexpr std::uint64_t max_x = 10'000'000;
    constexpr double threshold = 0.5;

    std::cout << "Запуск обчислювального пошуку пар Холла (x <= " << max_x 
              << ", ratio < " << threshold << ")\n";

    const HallSearcher searcher(threshold);
    const auto candidates = searcher.search_range(2, max_x);

    std::cout << std::setprecision(6) << std::fixed;
    for (std::size_t i = 0; i < candidates.size(); ++i) {
        const auto& c = candidates[i];
        std::cout << "Пара #" << (i + 1) 
                  << ": x = " << c.x 
                  << ", y = " << c.y 
                  << ", diff = " << c.diff 
                  << ", ratio = " << c.ratio << "\n";
    }

    std::cout << "Усього знайдено рекордно близьких пар: " << candidates.size() << "\n";
    return 0;
}
```
:::

## Аналіз обчислювальних підводних каменів та оптимізації

При масштабуванні алгоритму пошуку до значень `X_max > 10¹⁰` виникають три класичних обчислювальних бар'єри.

### 1. Точність чисел із плаваючою крапкою (`double` vs `long double`)

Тип даних `double` у стандарті IEEE 754 має 53 біти мантиси, що забезпечує точність близько 15–17 десяткових цифр. 

При `x > 10⁷` значення `y_ideal = x · √x` перевищує `10¹⁰.5`. При перетворенні такого числа на `double` дробова частина `x · √x` починає втрачати молодші біти. При `x > 10¹⁴` мантиса `double` стає недостатньою навіть для точного представлення цілої частини `⌊x · √x⌋`, що призводить до похибки округлення в 1–2 одиниці і пропуску рекордно близьких пар.

Два способи вирішення цієї проблеми:
- **Використання розширеної точності `long double`:** На архітектурах x86-64 тип `long double` реалізує 80-бітний формат FPU x87 із 64 бітами мантиси (близько 19 десяткових значущих цифр), що розширює точний пошук до `x ≈ 10¹²`.
- **Цілочисельний квадратний корінь `isqrt()`:** Обчислення точного цілого квадратного кореня `isqrt(x³)` за допомогою алгоритму Ньютона-Рафсона в 128-бітній цілочисельній арифметиці без використання плаваючої крапки взагалі.

### 2. Паралелізація на багатоядерних архітектурах (OpenMP)

Оскільки оцінка кожного значення `x` є абсолютно незалежною від інших (відсутній спільний модифікований стан), алгоритм є ідеально придатним для паралельного виконання (embarrassingly parallel).

У мові C/C++ паралелізація циклу досягається додаванням однієї директиви OpenMP над головним циклом:

```cpp
#pragma omp parallel for schedule(dynamic, 65536)
for (std::uint64_t x = 2; x <= max_x; ++x) {
    // Незалежна перевірка кожного x
}
```

Використання `schedule(dynamic, 65536)` ділить обчислювальний діапазон на блоки по 64 857 елементів і рівномірно розподіляє їх між потоками процесора, запобігаючи деградації продуктивності через неоднорідний доступ до пам'яті.

### 3. Алгоритми Елкіса замість прямого перебору

Для значень `x > 10¹²` навіть паралельний прямий перебір складністю `O(X)` вимагає роками обчислювального часу. 

Для виявлення світового рекорду `x = 58 538 601 878` Ноам Елкіс (Noam Elkies) використав не прямий перебір, а псевдолінійний алгебро-геометричний підхід. Елкіс зв'язав задачу з пошуком раціональних точок на модулярних кривих `X₀(N)` та застосував алгоритм скорочення базисів ґраток LLL (Lenstra–Lenstra–Lovász). Це дозволило перебирати не окремі числа `x`, а цілі нескінченні родини точок у ґратці розв'язків, зменшивши складність алгоритму до `O(X¹/⁴)`.
