# 📋 Інтерфейс бібліотечних викликів для гармонічних чисел та спеціальних функцій

Ця вставка є системним довідником інтерфейсів програмування для стандартних системних бібліотек C, C++, POSIX, Python, Rust та Go, які застосовуються для обчислення гармонічних чисел `H[n]`, їхнього аналітичного продовження на дійсні та комплексні значення, а також узагальнених гармонічних чисел через спеціальні функції (дигамма, полігамма, дзета-функція).

## 1. Математична концептуалізація інтерфейсів та аналітичне продовження

У системному та прикладному програмуванні обчислення гармонічних чисел `H[n]` рідко оформлюють у вигляді окремої фундаментальної викликової функції в системних бібліотеках операційної системи. Головна причина полягає в тому, що скінченна сума обернених цілих чисел являє собою лише окремий дискретний випадок значно ширшого класу математичних об'єктів. Замість того, щоб плодити окремі вузькоспеціалізовані функції для кожної комбінаторної суми, системні бібліотеки реалізують базову **пси-функцію** (англ. *Digamma function*, `ψ(x)`), яка являє собою першу логарифмічну похідну від логарифма гамма-функції `Γ(x)`:

```
ψ(x) = d/dx ln Γ(x) = Γ'(x) / Γ(x)
```

Строгий математичний зв'язок між `N`-им гармонічним числом та пси-функцією задається фундаментальною тотожністю:

```
H[n] = ψ(n + 1) + γ
```

де `γ ≈ 0.57721566490153286060` — фундаментальна стала Ейлера — Маскероні.

Головна інженерна перевага використання пси-функції замість дискретного сумування полягає в тому, що вона надає природне та аналітично строге **аналітичне продовження** гармонічних чисел з дискретної множини натуральних чисел `ℕ` на неперервну множину дійсних `x ∈ ℝ` та комплексних аргументів `z ∈ ℂ` (за винятком точок `x = -1, -2, -3, ...`, де функція має прості полюси першого порядку). Це дозволяє обчислювати дробові та від'ємні гармонічні числа у неперервних алгоритмах та апроксимаціях.

Для узагальнених гармонічних чисел другого та вищих порядків `H[n, m] = sum_{k=1}^n (1/k^m)` зв'язок із бібліотечними викликами реалізується через **дзета-функцію Рімана** `ζ(s)` та її двопараметричне узагальнення — **дзета-функцію Гурвіца** `ζ(s, q)`:

```
H[n, m] = ζ(m) - ζ(m, n + 1)
```

Завдяки цьому універсальному зв'язку будь-яка математична бібліотека, яка підтримує виклики `digamma` та `zeta`, здатна обчислювати довільні гармонічні числа за `O(1)` часу.

## 2. Системний C/C++ API та POSIX Стандарт (`<math.h>`, `<cmath>`)

У системному програмуванні на мові C та C++ (ISO C99/C11 та POSIX.1-2017) безпосередня назва `digamma` не входить до базового переліку обов'язкових імен заголовочного файла `<math.h>`, проте присутні функції для обчислення прямої гамма-функції `tgamma()` та її логарифма `lgamma()`.

### 2.1 Сигнатури та контракти системних функцій

:::tabs
```c
#include <math.h>

/* Пряма гамма-функція Euler Gamma: Γ(x) */
double      tgamma(double x);
float       tgammaf(float x);
long double tgammal(long double x);

/* Логарифм абсолютного значення гамма-функції: ln|Γ(x)| */
double      lgamma(double x);
float       lgammaf(float x);
long double lgammal(long double x);

/* POSIX реентерабельні версії зі збереженням знака Γ(x) */
double      lgamma_r(double x, int *signgamp);
float       lgammafr(float x, int *signgamp);
long double lgammal_r(long double x, int *signgamp);
```
```cpp
#include <cmath>

namespace std {
    // Пряма гамма-функція Euler Gamma: Γ(x)
    double      tgamma(double x);
    float       tgamma(float x);
    long double tgamma(long double x);

    // Логарифм абсолютного значення гамма-функції: ln|Γ(x)|
    double      lgamma(double x);
    float       lgamma(float x);
    long double lgamma(long double x);
}
```
:::

### 2.2 Розширення GNU C/C++ Library (glibc) та макроси констант

У системній бібліотеці `libm` під управлінням операційних систем GNU/Linux (glibc) та у сімействі систем BSD присутні неформатні розширення `gamma()`, а також вбудований доступ до сталої Ейлера через макроси вченні у заголовочному файлі при визначенні прапорця макропроцесора `_GNU_SOURCE`:

:::tabs
```c
#define _GNU_SOURCE
#include <math.h>

/* Захищене визначення константи Ейлера — Маскероні в glibc math.h */
#ifndef M_EULER
#define M_EULER 0.577215664901532860606512090082402431
#endif
```
```cpp
#include <numbers>
#include <cmath>

// У сучасній C++20 використовують типізовану математичну константу з <numbers>
constexpr double euler_gamma = std::numbers::egamma_v<double>;
```
:::

### 2.3 Створення власної обгортки Digamma та Harmonic для C та C++

Оскільки системні реалізації C `libm` на деяких платформах (наприклад, Windows CRT або пакунках без POSIX-розширень) не мають прямої функції `digamma`, її обчислюють або через чисельне диференціювання функції `lgamma(x)`, або через розклад у ряд.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <errno.h>
#include <stdbool.h>

#define C_EULER_MASCHERONI 0.57721566490153286060

typedef enum {
    HARMONIC_SUCCESS = 0,
    HARMONIC_ERR_INVALID_ARG = 1,
    HARMONIC_ERR_DOMAIN = 2,
    HARMONIC_ERR_OVERFLOW = 3
} HarmonicErrorCode;

typedef struct {
    double value;
    HarmonicErrorCode error;
    const char* description;
} HarmonicResultC;

/* Чисельне обчислення Digamma ψ(x) через центральну різницю lgamma */
static double c_digamma_num(double x) {
    if (x <= 0.0 && floor(x) == x) {
        errno = EDOM;
        return NAN;
    }
    const double h = 1e-7;
    return (lgamma(x + h) - lgamma(x - h)) / (2.0 * h);
}

HarmonicResultC c_harmonic_eval(double x) {
    HarmonicResultC res;
    res.value = NAN;
    res.error = HARMONIC_SUCCESS;
    res.description = "ОК";

    if (isnan(x) || x < 0.0) {
        res.error = HARMONIC_ERR_INVALID_ARG;
        res.description = "Аргумент x не може бути від'ємним або NaN";
        return res;
    }

    if (x == 0.0) {
        res.value = 0.0;
        return res;
    }

    errno = 0;
    double dig = c_digamma_num(x + 1.0);

    if (errno == EDOM) {
        res.error = HARMONIC_ERR_DOMAIN;
        res.description = "Помилка області визначення (Domain Error у полюсі)";
        return res;
    }

    if (errno == ERANGE || isinf(dig)) {
        res.error = HARMONIC_ERR_OVERFLOW;
        res.description = "Помилка переповнення (Overflow Error)";
        return res;
    }

    res.value = dig + C_EULER_MASCHERONI;
    return res;
}
```
```cpp
#include <cmath>
#include <expected>
#include <numbers>
#include <string_view>

namespace sys_math {

constexpr double EULER_MASCHERONI = 0.57721566490153286060;

enum class HarmonicError {
    InvalidArgument,
    DomainError,
    Overflow
};

[[nodiscard]] inline std::expected<double, HarmonicError> cpp_harmonic_eval(double x) noexcept {
    if (std::isnan(x) || x < 0.0) {
        return std::unexpected(HarmonicError::InvalidArgument);
    }
    if (x == 0.0) {
        return 0.0;
    }

    const double h = 1e-7;
    const double dig = (std::lgamma(x + 1.0 + h) - std::lgamma(x + 1.0 - h)) / (2.0 * h);

    if (std::isnan(dig) || std::isinf(dig)) {
        return std::unexpected(HarmonicError::DomainError);
    }

    return dig + EULER_MASCHERONI;
}

} // namespace sys_math
```
:::

### 2.4 Обробка системних помилок та прапорці FPU

При виконанні обчислень через системні математичні функції C/C++ прапори помилок виставляються через два паралельних системних механізми: змінні `errno` та процесорні прапори блоку плаваючої крапки `<fenv.h>`:
- **`EDOM` (Domain Error):** виникає при спробі обчислити значення для від'ємного цілого аргументу `x = -1, -2, ...`. Системний прапор перевіряється через `fetestexcept(FE_INVALID)`.
- **`ERANGE` (Range Error / Overflow):** виникає при виході значення за межі діапазону представлення `double` (переповнення до `HUGE_VAL` або підповнення). Системний прапор перевіряється через `fetestexcept(FE_OVERFLOW | FE_UNDERFLOW)`.

## 3. C++ Standard Library & Boost.Math API

У мові C++ починаючи зі стандарту C++17 в заголовочному файлі `<cmath>` з'явилися спеціальні математичні функції (ISO/IEC 29124:2010), а у стандартній інженерній бібліотеці **Boost.Math** доступний вичерпний набір викликів для дигамма, полігамма та дзета-функцій з підтримкою шаблонів типів.

### 3.1 Стандарт C++17 / C++20 (`<cmath>`)

У стандартному заголовочному файлі `<cmath>` стандарту C++17 додано підтримку дзета-функції Рімана:

```cpp
#include <cmath>

namespace std {
    // Гамма-функція та її логарифм
    double tgamma(double x);
    double lgamma(double x);

    // Дзета-функція Рімана (доступна з C++17)
    double riemann_zeta(double s);
    float  riemann_zetaf(float s);
}
```

### 3.2 Бібліотека Boost.Math (`<boost/math/special_functions/>`)

Для обчислення гармонічних чисел у високопродуктивних обчислювальних C++ системах застосовують модулі бібліотеки Boost.Math. Вони повністю підтримують обогачені шаблони типів (`float`, `double`, `long double`, `boost::multiprecision::cpp_dec_float_50`) та дозволяють налаштовувати політики обробки помилок.

Сигнатури стандартних викликів Boost:

```cpp
#include <boost/math/special_functions/digamma.hpp>
#include <boost/math/special_functions/polygamma.hpp>
#include <boost/math/special_functions/zeta.hpp>

namespace boost::math {

// Пси-функція (Digamma)
template <class T>
T digamma(T x);

template <class T, class Policy>
T digamma(T x, const Policy& pol);

// Полігамма-функція (n-та похідна від digamma)
template <class T>
T polygamma(int n, T x);

// Дзета-функція Рімана
template <class T>
T zeta(T s);

} // namespace boost::math
```

### 3.3 Приклад високоефективного C++23 класу обчислень

Нижче наведено приклад побудови сучасного C++23 класу для обчислення гармонічних чисел з використанням Boost.Math, стандартних математичних констант C++20 `<numbers>` та обробки помилок через `std::expected` без генерування важких винятків:

```cpp
#include <iostream>
#include <cmath>
#include <expected>
#include <concepts>
#include <numbers>
#include <boost/math/special_functions/digamma.hpp>
#include <boost/math/special_functions/zeta.hpp>

namespace math_api {

// Використання офіційної математичної константи C++20
constexpr double EULER_GAMMA = 0.57721566490153286060;

enum class EvalError {
    InvalidArgument,
    DomainError,
    Overflow
};

template <std::floating_point T>
class HarmonicEvaluator {
public:
    // Обчислення H[x] для довільного дійсного x >= 0
    [[nodiscard]] static std::expected<T, EvalError> eval(T x) noexcept {
        if (std::isnan(x) || x < static_cast<T>(0)) {
            return std::unexpected(EvalError::InvalidArgument);
        }
        if (x == static_cast<T>(0)) {
            return static_cast<T>(0);
        }

        try {
            // H[x] = digamma(x + 1) + gamma
            T dig = boost::math::digamma(x + static_cast<T>(1));
            return dig + static_cast<T>(EULER_GAMMA);
        } catch (const std::overflow_error&) {
            return std::unexpected(EvalError::Overflow);
        } catch (const std::domain_error&) {
            return std::unexpected(EvalError::DomainError);
        }
    }

    // Узагальнене гармонічне число H[n, m] = sum(1/k^m)
    [[nodiscard]] static std::expected<T, EvalError> eval_generalized(std::size_t n, std::size_t m) noexcept {
        if (n == 0 || m == 0) {
            return std::unexpected(EvalError::InvalidArgument);
        }
        
        T sum = static_cast<T>(0);
        for (std::size_t k = 1; k <= n; ++k) {
            sum += static_cast<T>(1) / std::pow(static_cast<T>(k), static_cast<T>(m));
        }
        return sum;
    }
};

} // namespace math_api

int main() {
    using Evaluator = math_api::HarmonicEvaluator<double>;

    auto r1 = Evaluator::eval(10.0);
    if (r1) {
        std::cout << "H[10] = " << *r1 << "\n";
    }

    auto r2 = Evaluator::eval(2.5); // Неперервний дійсний аргумент!
    if (r2) {
        std::cout << "H[2.5] = " << *r2 << "\n";
    }

    auto r3 = Evaluator::eval_generalized(100, 2); // H[100, 2] -> pi^2 / 6
    if (r3) {
        std::cout << "H[100, 2] = " << *r3 << " (границя pi^2/6 ≈ 1.64493)\n";
    }

    return 0;
}
```

## 4. Python Scientific Stack (`math`, `scipy.special`, `sympy`)

У мовному середовищі Python розробнику доступно три незалежних рівні інфраструктури для роботи з гармонічними числами: стандартний модуль `math`, векторизований науковий стек `scipy.special` та символьний алгебраїчний пакет `sympy`.

### 4.1 Стандартна бібліотека `math`

У базовому модулі `math` інтерпретатора Python присутні виклики `math.gamma(x)` та `math.lgamma(x)` для обчислення гамма-функції:

```python
import math

# Обчислення ln(Γ(x))
val = math.lgamma(5.0)  # ln(4!) = ln(24) ≈ 3.1780538
```

### 4.2 Модуль `scipy.special` (SciPy / NumPy API)

Пакет `scipy.special` надає прямі векторизовані виклики для пси-функції `digamma` та полігамма-функцій, які оптимізовані для виконання над багатовимірними масивами NumPy:

```python
import numpy as np
from scipy.special import digamma, polygamma, zeta

# Константа Ейлера — Маскероні в SciPy
EULER_GAMMA = 0.57721566490153286060

def harmonic_scipy(x):
    """Векторизоване обчислення H[x] для масивів NumPy або чисел."""
    return digamma(np.asarray(x) + 1.0) + EULER_GAMMA

# Приклад обчислення для масиву аргументів
arr = np.array([1, 2, 5, 10, 100])
print("H[arr] =", harmonic_scipy(arr))

# Узагальнене гармонічне число H[n, m] через дзета-функцію Гурвіца
def harmonic_generalized_scipy(n, m):
    return zeta(m, 1) - zeta(m, n + 1)

print("H[10, 2] =", harmonic_generalized_scipy(10, 2))
```

### 4.3 Символьний пакет `sympy`

Для отримання точних тотожностей, асимптотичних розкладів у ряд та точних обчислень із довільною точністю застосовують модуль `sympy.harmonic`:

```python
import sympy as sp

n = sp.Symbol('n')
# Символьне представлення H[n]
expr = sp.harmonic(n)

# Асимптотичний розклад у ряд Тейлора при n -> oo
series_expr = sp.series(sp.harmonic(n), n, sp.oo, n=4)
print("Асимптотичний ряд sympy:")
print(series_expr)

# Обчислення з 50 знаками точності
val_50 = sp.harmonic(100).evalf(50)
print("H[100] з 50 знаками:", val_50)
```

## 5. Rust API (`statrs`, `num-complex`)

У сучасній системній мові Rust обчислення спеціальних математичних функцій здійснюється через крейти `statrs` або `purser`:

```rust
// Cargo.toml: [dependencies] statrs = "0.16"

use statrs::function::gamma::digamma;

const EULER_MASCHERONI: f64 = 0.57721566490153286060_f64;

pub fn harmonic_eval(x: f64) -> Result<f64, &'static str> {
    if x < 0.0 {
        return Err("Аргумент x повинен бути >= 0");
    }
    if x == 0.0 {
        return Ok(0.0);
    }
    
    // H[x] = digamma(x + 1) + gamma
    let dig = digamma(x + 1.0);
    Ok(dig + EULER_MASCHERONI)
}

fn main() {
    match harmonic_eval(10.0) {
        Ok(val) => println!("H[10] = {:.15}", val),
        Err(e) => eprintln!("Помилка: {}", e),
    }
}
```

## 6. Go Math API (`math`, `gonum/mathext`)

У мові Go системний модуль `math` пропонує виклики `math.Gamma` та `math.Lgamma`. Для доступу до пси-функції розробники використовують стандартизований пакет `gonum.org/v1/gonum/mathext`:

```go
package main

import (
	"fmt"
	"math"
	"gonum.org/v1/gonum/mathext"
)

const EulerMascheroni = 0.57721566490153286060

func ComputeHarmonic(x float64) (float64, error) {
	if x < 0 {
		return 0, fmt.Errorf("invalid argument x = %g", x)
	}
	if x == 0 {
		return 0, nil
	}
	// H[x] = Digamma(x + 1) + EulerMascheroni
	dig := mathext.Digamma(x + 1.0)
	return dig + EulerMascheroni, nil
}

func main() {
	val, err := ComputeHarmonic(10.0)
	if err != nil {
		fmt.Println("Error:", err)
	} else {
		fmt.Printf("H[10] = %.15f\n", val)
	}
}
```

## 7. Зведена порівняльна таблиця системних інтерфейсів

Нижче наведено підсумкову порівняльну таблицю наявних системних функцій, типів даних та сигнатур для різних середовищ розробки:

| Мова / Середовище | Бібліотека / Модуль | Основна функція | Додаткові функції | Механізм обробки помилок |
| :--- | :--- | :--- | :--- | :--- |
| **C (POSIX)** | `libm` (`<math.h>`) | `lgamma(x)`, `tgamma(x)` | `lgamma_r(x, &sign)` | Змінна `errno` (`EDOM`, `ERANGE`), `<fenv.h>` |
| **C++17/C++20** | `<cmath>` | `std::tgamma`, `std::lgamma` | `std::riemann_zeta` | `errno`, `std::fetestexcept` |
| **C++ (Boost)** | `<boost/math/>` | `boost::math::digamma(x)` | `polygamma(n, x)`, `zeta(s)` | `std::expected`, Boost Policies |
| **Python** | `scipy.special` | `scipy.special.digamma(x)` | `polygamma(n, x)`, `zeta(s, q)` | Векторизовані винятки NumPy |
| **Python** | `sympy` | `sympy.harmonic(n, m)` | `sympy.series()` | Точні символьні винятки SymPy |
| **Rust** | `statrs` | `statrs::function::gamma::digamma` | `statrs::function::erf` | Перераховуваний тип `Result<f64, &str>` |
| **Go** | `gonum/mathext` | `mathext.Digamma(x)` | `math.Lgamma(x)` | Повернення об'єкта `error` |

Цей систематизований довідник дозволяє розробникам системного та прикладного програмного забезпечення швидко обирати найбільш ефективні бібліотечні виклики для обчислення гармонічних чисел на будь-яких мовах та цільових платформах.
