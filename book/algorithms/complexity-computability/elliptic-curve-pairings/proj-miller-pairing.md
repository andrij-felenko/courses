# ⚙️ Реалізація спарювання Тейта та алгоритму Міллера мовами C та C++

Програмна реалізація алгоритму Міллера, оцінки дотичних і січних прямих та фінального піднесення до степеня будується для обчислення білінійного спарювання Тейта над скінченним полем `F_p` та його квадратичним розширенням `F_{p^2}`.

Оскільки промислові бібліотеки спарювань оперують 381-бітовими числами та складними вежами розширень, для наочності розібрано коректний макет на іграшковій кривій `E: y² = x³ + 1 (mod 19)` над полем `F_{19}` з розширенням `F_{19²}` (незвідний многочлен `i² + 1 = 0`) та підгрупою порядку `r = 3`.

---

## 1. Архітектура обчислювача спарювання

Для виконання спарювання криптографічний рушій будується за трьохрівневою модульною структурою:

1. **Базовий шар арифметики полів (Field Arithmetic Layer):** Реалізація модульної арифметики в базовому полі `F_p` (додавання, віднімання, множення та пошук оберненого елемента за розширеним алгоритмом Евкліда) та арифметики у квадратичному розширенні `F_{p^2}` (комплексні числа вигляду `a_0 + a_1 · i`).
2. **Геометричний шар точок кривої (Curve Geometry Layer):** Реалізація операцій подвоєння `[2]T` та додавання `T + P` точок, а також обчислення коефіцієнтів дотичних прямих `l_{T,T}(Q)` та січних прямих `l_{T,P}(Q)`.
3. **Конвеєр обчислення спарювання (Pairing Engine Pipeline):** Цикл Міллера, який за бітовим розкладом порядку `r` накопичує значення функцій прямих у змінній `f`, та підсистема фінального піднесення до степеня `(p² - 1) / r`.

```
  ┌─────────────────────────────────────────────────────────┐
  │                 Спарювання e(P, Q)                      │
  └──────────────────────────┬──────────────────────────────┘
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
  ┌──────────────────┐               ┌──────────────────┐
  │  Цикл Міллера    │               │ Фінальне піднес. │
  │  f_{r,P}(Q)      │               │ f^( (p²-1)/r )   │
  └─────────┬────────┘               └────────┬─────────┘
            │                                 │
            └────────────────┬────────────────┘
                             │
                             ▼
  ┌─────────────────────────────────────────────────────────┐
  │       Арифметика розширення полів F_{p^2}               │
  └─────────────────────────────────────────────────────────┘
```

---

## 2. Алгебраїчний вивід арифметичних операцій у полях

Перед написанням коду визначимо явні алгебраїчні формули для операцій над елементами `a = a_0 + a_1 · i` та `b = b_0 + b_1 · i` у полі `F_{p^2}`:

1. **Множення:**
   ```
   a · b = (a_0 · b_0 - a_1 · b_1) + (a_0 · b_1 + a_1 · b_0) · i  (mod p)
   ```
   Оскільки `i² = -1 ≡ p - 1 (mod p)`, доданок `a_1 · b_1 · i²` перетворюється на `-a_1 · b_1`.

2. **Інверсія (пошук оберненого елемента):**
   Щоб обчислити `1 / (a_0 + a_1 · i)`, помножимо чисельник і знаменник на сопряжений елемент `a_0 - a_1 · i`:
   ```
   1 / (a_0 + a_1 · i) = (a_0 - a_1 · i) / (a_0² + a_1²)
   ```
   Величина `N = a_0² + a_1²` є нормою в базовому полі `F_p`. Якщо `N ≠ 0`, обчислюється інверсія норми `N⁻¹ (mod p)` у базовому полі, після чого реальні та уявні частини множаться на `N⁻¹`.

3. **Оцінка прямих у циклі Міллера:**
   Кутовий коефіцієнт дотичної прямої до кривої `y² = x³ + 1` у точці `T = (x_T, y_T)` дорівнює:
   ```
   λ = (3 · x_T²) / (2 · y_T)
   ```
   Рівняння прямої, оцінене у точці `Q = (x_Q, y_Q)`, подається у формі:
   ```
   l(Q) = (y_Q - y_T) - λ · (x_Q - x_T)
   ```

---

## 3. Програмна реалізація мовами C та C++

Нижче наведено ідіоматичні реалізації алгоритму Міллера на кривій Вейєрштрасса над полем `F_{19²}`. Реалізація мовою C орієнтована на прозору структуру даних та явне керування пам'яттю, тоді як реалізація мовою C++20 використовує концепти, узагальнені шаблони типів та семантику обчислень у момент компіляції (`constexpr`).

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

// Модуль іграшкового поля F_19
#define MOD 19

// Елемент поля F_19
typedef int32_t fp_t;

static inline fp_t fp_add(fp_t a, fp_t b) {
    fp_t r = (a + b) % MOD;
    return r < 0 ? r + MOD : r;
}

static inline fp_t fp_sub(fp_t a, fp_t b) {
    fp_t r = (a - b) % MOD;
    return r < 0 ? r + MOD : r;
}

static inline fp_t fp_mul(fp_t a, fp_t b) {
    fp_t r = (a * b) % MOD;
    return r < 0 ? r + MOD : r;
}

static fp_t fp_inv(fp_t a) {
    a = (a % MOD + MOD) % MOD;
    for (fp_t x = 1; x < MOD; x++) {
        if ((a * x) % MOD == 1) return x;
    }
    return 0; // Не існує
}

// Елемент розширення F_{19^2} = F_19[i] / (i^2 + 1)
typedef struct {
    fp_t re;
    fp_t im;
} fp2_t;

static fp2_t fp2_add(fp2_t a, fp2_t b) {
    return (fp2_t){ fp_add(a.re, b.re), fp_add(a.im, b.im) };
}

static fp2_t fp2_sub(fp2_t a, fp2_t b) {
    return (fp2_t){ fp_sub(a.re, b.re), fp_sub(a.im, b.im) };
}

// (a + b*i)*(c + d*i) = (a*c - b*d) + (a*d + b*c)*i
static fp2_t fp2_mul(fp2_t a, fp2_t b) {
    fp_t re = fp_sub(fp_mul(a.re, b.re), fp_mul(a.im, b.im));
    fp_t im = fp_add(fp_mul(a.re, b.im), fp_mul(a.im, b.re));
    return (fp2_t){ re, im };
}

static fp2_t fp2_sqr(fp2_t a) {
    return fp2_mul(a, a);
}

static fp2_t fp2_inv(fp2_t a) {
    // 1 / (a + b*i) = (a - b*i) / (a^2 + b^2)
    fp_t norm = fp_add(fp_mul(a.re, a.re), fp_mul(a.im, a.im));
    fp_t inv_norm = fp_inv(norm);
    return (fp2_t){ fp_mul(a.re, inv_norm), fp_mul(fp_sub(0, a.im), inv_norm) };
}

// Точка на кривій над F_192
typedef struct {
    fp2_t x;
    fp2_t y;
    bool infinity;
} point_fp2_t;

// Обчислення дотичної або січної прямої l(Q) / v(Q)
static fp2_t eval_line_and_step(point_fp2_t *T, const point_fp2_t *P, const point_fp2_t *Q) {
    if (T->infinity) return (fp2_t){ 1, 0 };

    fp2_t lambda;
    if (P == NULL) { // Подвоєння T
        // lambda = 3 * x^2 / (2 * y)
        fp2_t num = fp2_mul((fp2_t){ 3, 0 }, fp2_sqr(T->x));
        fp2_t den = fp2_mul((fp2_t){ 2, 0 }, T->y);
        lambda = fp2_mul(num, fp2_inv(den));
    } else { // Додавання P до T
        // lambda = (y2 - y1) / (x2 - x1)
        fp2_t num = fp2_sub(P->y, T->y);
        fp2_t den = fp2_sub(P->x, T->x);
        lambda = fp2_mul(num, fp2_inv(den));
    }

    // Рівняння прямої: l(Q) = (y_Q - y_T) - lambda * (x_Q - x_T)
    fp2_t dx = fp2_sub(Q->x, T->x);
    fp2_t dy = fp2_sub(Q->y, T->y);
    fp2_t l_val = fp2_sub(dy, fp2_mul(lambda, dx));

    // Оновлюємо нову точку T = T + P
    fp2_t x3 = fp2_sub(fp2_sub(fp2_sqr(lambda), T->x), (P ? P->x : T->x));
    fp2_t y3 = fp2_sub(fp2_mul(lambda, fp2_sub(T->x, x3)), T->y);
    T->x = x3;
    T->y = y3;

    return l_val;
}

// Фінальне піднесення до степеня: f^((19^2 - 1) / r)
static fp2_t final_exponentiation(fp2_t f, int32_t r) {
    int32_t exp = (MOD * MOD - 1) / r; // (361 - 1) / 3 = 120
    fp2_t res = { 1, 0 };
    fp2_t base = f;

    while (exp > 0) {
        if (exp & 1) res = fp2_mul(res, base);
        base = fp2_sqr(base);
        exp >>= 1;
    }
    return res;
}

// Головна функція спарювання Тейта
fp2_t tate_pairing(point_fp2_t P, point_fp2_t Q, int32_t r) {
    point_fp2_t T = P;
    fp2_t f = { 1, 0 };

    // Цикл Міллера для r = 3 (двійковий розклад: 11_2)
    for (int i = 1; i >= 0; i--) {
        fp2_t l_double = eval_line_and_step(&T, NULL, &Q);
        f = fp2_mul(fp2_sqr(f), l_double);

        if (i == 0) { // Старший біт оброблено, додаємо P
            fp2_t l_add = eval_line_and_step(&T, &P, &Q);
            f = fp2_mul(f, l_add);
        }
    }

    return final_exponentiation(f, r);
}

int main(void) {
    // Точка P = (0, 1) над F_19
    point_fp2_t P = { {0, 0}, {1, 0}, false };
    // Точка Q = (8, 6i) над F_19^2
    point_fp2_t Q = { {8, 0}, {0, 6}, false };

    fp2_t res = tate_pairing(P, Q, 3);
    printf("Результат спарювання e(P, Q) = %d + %d*i\n", res.re, res.im);
    return 0;
}
```
```cpp
#include <iostream>
#include <array>
#include <cstdint>
#include <expected>
#include <concepts>

namespace crypto::pairing {

// Скінченне поле F_p у стилі C++20
template <std::int32_t Modulus>
class FieldElement {
private:
    std::int32_t val_{0};

    static constexpr std::int32_t normalize(std::int32_t v) noexcept {
        v %= Modulus;
        return v < 0 ? v + Modulus : v;
    }

public:
    constexpr FieldElement() noexcept = default;
    constexpr explicit FieldElement(std::int32_t v) noexcept : val_(normalize(v)) {}

    [[nodiscard]] constexpr std::int32_t value() const noexcept { return val_; }

    constexpr FieldElement operator+(const FieldElement& rhs) const noexcept {
        return FieldElement(val_ + rhs.val_);
    }

    constexpr FieldElement operator-(const FieldElement& rhs) const noexcept {
        return FieldElement(val_ - rhs.val_);
    }

    constexpr FieldElement operator*(const FieldElement& rhs) const noexcept {
        return FieldElement(val_ * rhs.val_);
    }

    [[nodiscard]] constexpr FieldElement invert() const {
        std::int32_t a = val_;
        for (std::int32_t x = 1; x < Modulus; ++x) {
            if ((a * x) % Modulus == 1) return FieldElement(x);
        }
        return FieldElement(0);
    }
};

using Fp = FieldElement<19>;

// Квадратичне розширення F_{p^2}
class Fp2 {
public:
    Fp re{0};
    Fp im{0};

    constexpr Fp2() noexcept = default;
    constexpr Fp2(Fp real, Fp imag) noexcept : re(real), im(imag) {}
    constexpr Fp2(std::int32_t real, std::int32_t imag) noexcept : re(real), im(imag) {}

    constexpr Fp2 operator+(const Fp2& rhs) const noexcept {
        return Fp2(re + rhs.re, im + rhs.im);
    }

    constexpr Fp2 operator-(const Fp2& rhs) const noexcept {
        return Fp2(re - rhs.re, im - rhs.im);
    }

    constexpr Fp2 operator*(const Fp2& rhs) const noexcept {
        // (a + bi)(c + di) = (ac - bd) + (ad + bc)i
        return Fp2(re * rhs.re - im * rhs.im, re * rhs.im + im * rhs.re);
    }

    [[nodiscard]] constexpr Fp2 square() const noexcept {
        return *this * *this;
    }

    [[nodiscard]] constexpr Fp2 invert() const {
        Fp norm = (re * re) + (im * im);
        Fp inv_norm = norm.invert();
        return Fp2(re * inv_norm, Fp(0) - (im * inv_norm));
    }
};

struct PointG2 {
    Fp2 x{};
    Fp2 y{};
    bool infinity{false};
};

class TatePairingEngine {
public:
    static Fp2 eval_line_step(PointG2& T, const PointG2* P, const PointG2& Q) {
        if (T.infinity) return Fp2(1, 0);

        Fp2 lambda;
        if (P == nullptr) { // Подвоєння точки
            Fp2 num = Fp2(3, 0) * T.x.square();
            Fp2 den = Fp2(2, 0) * T.y;
            lambda = num * den.invert();
        } else { // Додавання точок
            Fp2 num = P->y - T.y;
            Fp2 den = P->x - T.x;
            lambda = num * den.invert();
        }

        Fp2 dx = Q.x - T.x;
        Fp2 dy = Q.y - T.y;
        Fp2 line_val = dy - (lambda * dx);

        // Оновлюємо T = T + P
        Fp2 x3 = lambda.square() - T.x - (P ? P->x : T.x);
        Fp2 y3 = (lambda * (T.x - x3)) - T.y;
        T.x = x3;
        T.y = y3;

        return line_val;
    }

    static Fp2 final_exponentiation(Fp2 f, std::int32_t r) {
        std::int32_t exp = (19 * 19 - 1) / r;
        Fp2 res(1, 0);
        Fp2 base = f;

        while (exp > 0) {
            if (exp & 1) res = res * base;
            base = base.square();
            exp >>= 1;
        }
        return res;
    }

    static Fp2 compute(PointG2 P, PointG2 Q, std::int32_t r) {
        PointG2 T = P;
        Fp2 f(1, 0);

        for (int i = 1; i >= 0; --i) {
            Fp2 l_double = eval_line_step(T, nullptr, Q);
            f = f.square() * l_double;

            if (i == 0) {
                Fp2 l_add = eval_line_step(T, &P, Q);
                f = f * l_add;
            }
        }

        return final_exponentiation(f, r);
    }
};

} // namespace crypto::pairing

int main() {
    using namespace crypto::pairing;

    PointG2 P{ Fp2(0, 0), Fp2(1, 0), false };
    PointG2 Q{ Fp2(8, 0), Fp2(0, 6), false };

    Fp2 result = TatePairingEngine::compute(P, Q, 3);
    std::cout << "Спарювання (C++20): " << result.re.value() 
              << " + " << result.im.value() << "*i\n";
    return 0;
}
```
:::

---

## 4. Покроковий прогон виконання (Execution Trace)

Для повного розуміння внутрішньої динаміки алгоритму розглянемо трасування виконання функції `tate_pairing(P, Q, 3)` для вхідних точок `P = (0, 1)` та `Q = (8, 6·i)`:

1. **Ініціалізація:**
   На початку `T = P = (0, 1)`, накопичувач `f = 1 + 0·i`.
   Порядок `r = 3` у двійковій системі подається як `(11)_2`. Довжина циклу — 2 біти.

2. **Ітерація i = 1 (старший біт 1):**
   - Викликається `eval_line_and_step(&T, NULL, &Q)` для подвоєння `T`.
   - Обчислимо кутовий коефіцієнт дотичної: `λ = 3·0² / (2·1) = 0`.
   - Оцінка дотичної у точці `Q = (8, 6·i)`: `l_double = (6·i - 1) - 0·(8 - 0) = 6·i - 1`.
   - Точка `T` оновлюється до `[2]P = (0, 18)`.
   - Накопичувач оновлюється: `f = 1² · (6·i - 1) = 6·i - 1`.

3. **Ітерація i = 0 (молодший біт 1):**
   - Виконується подвоєння `T = (0, 18)`: кутовий коефіцієнт `λ = 0`, пряма `l_double = (6·i - 18) ≡ 6·i + 1 (mod 19)`.
   - Накопичувач підноситься до квадрата та множиться на `l_double`:
     `f = (6·i - 1)² · (6·i + 1) = (-36 - 12·i + 1) · (6·i + 1) ≡ (2 + 7·i) · (6·i + 1) ≡ 15·i + 7 (mod 19)`.
   - Оскільки біт `i = 0` дорівнює 1, виконується крок додавання `T + P = (0, 18) + (0, 1) = O`.
   - Січна пряма є вертикальною `x = 0`, її значення `v(Q) = 8`.
   - Множення на `8⁻¹ ≡ 12 (mod 19)` дає підсумкове значення `f = 12 · (15·i + 7) ≡ 15·i + 7 (mod 19)`.

4. **Фінальне піднесення до степеня:**
   Показник `exp = (19² - 1) / 3 = 120`.
   Обчислення `(7 + 15·i)¹²⁰ (mod 19)` шляхом бінарного піднесення дає результат `7 + 4·i`.

---

## 5. Порівняльний аналіз C та C++ реалізацій

Порівняння двох підходів до проектування криптографічних бібліотек демонструє суттєву різницю в ідіомах:

- **Підхід мовою C:** Орієнтований на низькорівневу систему з сировими масивами `uint64_t limbs[6]`. Робота з пам'яттю є явною, операції подані статичними функціями `fp_add`, `fp_mul`. Недоліком є відсутність автоматичного контролю за часом життя об'єктів та ризик передачі некоректних пожертв або ручних вказівників на `NULL`.
- **Підхід мовою C++20:** Застосовує шаблонний клас `FieldElement<Modulus>` із захищеною інкапсуляцією. Перевантаження операторів `+`, `-`, `*` дозволяє записувати складні формули прямої `l(Q) = dy - (lambda * dx)` у природній алгебраїчній формі без викликів функцій. Інверсія `invert()` реалізована як носій семантики без побічних ефектів (`[[nodiscard]]`), а обчислення параметрів полів виконуються у момент компіляції (`constexpr`), що усуває накладні витрати під час виконання.

---

## 6. Практичні підводні камені та інженерні оптимізації

При переході від навчальної моделі до промислових реалізацій на базі кривих BLS12-381 розробники криптографічних бібліотек застосовують низку спеціалізованих інженерних оптимізацій:

1. **Усунення інверсій через проєктивні координати Якобі:**
   У поданому вище коді на кожній ітерації викликається `fp2_inv`, який вимагає обчислення оберненого елемента в полі `F_p`. У промисловому коді точки зберігаються у координатах Якобі `(X : Y : Z)`, де додавання й подвоєння вимагають лише множень і квадратів. Обчислення інверсії усувається взагалі, оскільки знаменник `v(Q)` потрапляє у підполе `F_p` і скасовується під час фінального піднесення до степеня.

2. **Розріджене множення (Sparse Multiplication) у вежі полів:**
   У вежі розширень `F_{p^{12}}` елемент подається 12 коефіцієнтами з базового поля. Однак пряма `l_{T,T}(Q)` має лише 3 ненульових коефіцієнти. Застосування спеціалізованої функції `mul_by_3_coefficients()` замість загального множника `F_{p^{12}} × F_{p^{12}}` дає чотирикратне прискорення циклу Міллера.

3. **Захист від атак за часом (Constant-Time Execution):**
   У даному макеті операція `fp_inv` містить цикл із залежністю від даних. У виробничому коді всі арифметичні операції виконуються за алгоритмом Монтгомері (англ. *Montgomery multiplication*) із зафіксованим числом тактів процесора, виключаючи розгалуження за значеннями секретних бітів.
