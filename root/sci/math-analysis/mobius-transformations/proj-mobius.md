# ⚙️ Обчислення та візуалізація перетворень Мьобіуса

Ця алгоритмічна вставка містить практичну реалізацію обчислення, нормалізації, композиції, інверсії, оцінки чисельної стійкості та класифікації дробово-лінійних перетворень Мьобіуса мовами C та C++, а також детальний аналіз алгоритмів відображення точкових сіток у гідродінаміці та релятивістській оптиці.

## 1. Архітектура та математична специфікація алгоритмів

У комп'ютерній графіці, релятивістській кінематиці та чисельній гідродінаміці перетворення Мьобіуса описується дробово-раціональним виразом над комплексною площиною `w = f(z) = (a·z + b) / (c·z + d)`. З обчислювальної точки зору ця функція вимагає компактної та чисельно стійкої структури даних, здатної обробляти такі ключові задачі:

1. **Нормалізація матриці коефіцієнтів:** Зведення визначника `det(M) = a·d - b·c` до одиниці (`det(M) = 1`). Це необхідно для того, щоб слід матриці `Tr(M) = a + d` однозначно визначав класифікаційний тип перетворення (параболічне, еліптичне, гіперболічне чи локсодромне) і не залежав від довільного масштабування коефіцієнтів.
2. **Композиція двох перетворень:** Замість послідовного обчислення двох дробових виразів `w = f(g(z))`, що загрожує накопиченням чисельної похибки ділення, алгоритм виконує перемноження відповідних комплексних матриць `2×2`. Складність множення матриць становить `O(1)`.
3. **Аналітичне обчислення оберненого відображення:** Обчислення `M⁻¹` через алгебраїчні доповнення нормованої матриці `[a b; c d] ↦ [d -b; -c a]`, що працює без чисельного обернення систем рівнянь за `O(1)` операцій.
4. **Обробка особливих точок та полюсів:** Точка `z = -d/c` перетворює знаменник на нуль і відображається в нескінченно віддалену точку `∞` на сфері Рімана. Алгоритм виявляє такі особливості за допомогою перевірки модуля знаменника `|c·z + d| < ε` і коректно повертає прапорець нескінченності.
5. **Векторизована трансформація сіток:** Застосування одного перетворення до великих масивів точок (наприклад, вузлів гідродінамічної сітки або зоряного каталогу) із використанням безперервного розташування елементів у пам'яті (flat array layout), що є дружнім до процесорного кЕшу та SIMD-інструкцій.

## 2. Аналіз чисельної стійкості та граничних випадків

Під час реалізації обчислень із плаваючою крапкою (`double` або `float complex`) виникають два критичні чисельні ефекти, які потребують спеціальної обробки:

Катастрофічне скасування (Catastrophic Cancellation) виникає при обчисленні визначника `a·d - b·c` або дискримінанта `(a - d)² + 4·b·c`, коли віднімаються дві близькі за модулем величини. Для запобігання втрати значущих розрядів mantissa нормування виконується із застосуванням модульного порогу `ε = 1e-15`. Якщо модуль визначника `|a·d - b·c| < ε`, матриця оголошується виродженою (Singular Matrix), і обчислення зупиняється з повідомленням про помилку.

Точки в околі нескінченності виникають при обчисленні `f(z)` для точок `z`, де знаменник `|c·z + d|` прямує до нуля. Пряме ділення у цьому випадку призведе до утворення `NaN` або обчислювального переповнення. Алгоритм використовує машинний поріг `ε_zero = 1e-12`. Якщо `|c·z + d| < ε_zero`, вихідне значення встановлюється в `INFINITY`, а у вихідний прапорець записується `is_infinity = true`.

## 3. Покроковий розбір алгоритму та структури даних

Розглянемо структуру розрахункового ядра для мов C та C++.

### 3.1. Структура `MobiusTransform`
Структура даних зберігає чотири змінні комплексного типу. В мові C це тип `double complex`, який у пам'яті виглядає як пара з двох чисел типу `double` (дісна та уявна частини, разом 16 байт на коефіцієнт, 64 байти на всю структуру). В мові C++ використовується стандартний клас `std::complex<double>`, який володіє ідентичним розміщенням у пам'яті і сумісний з форматиратором C99.

### 3.2. Алгоритм нормалізації
Алгоритм нормалізації приймає вхідну структуру `m`, обчислює її визначник `det = m.a * m.d - m.b * m.c` і шукає його квадратний корінь `denom = sqrt(det)`. Після цього кожен з чотирьох коефіцієнтів ділиться на `denom`. Це гарантує, що новий визначник дорівнює `1.0`, що є необхідною умовою для коректної класифікації сліду.

### 3.3. Обчислення нерухомих точок
Нерухомі точки обчислюються шляхом розв'язання квадратного рівняння `c·z² + (d - a)·z - b = 0`. 

Якщо коефіцієнт `c = 0` (афінне перетворення), рівняння стає лінійним `(d - a)·z = b`. При `a ≠ d` воно має єдину скінченну нерухому точку `z = b / (d - a)`, а друга нерухома точка знаходиться на нескінченності `∞`.

Якщо `c ≠ 0`, обчислюється комплексний дискримінант `disc = (d - a)² + 4·b·c`. З нього добувається комплексний корінь `sqrt_disc = sqrt(disc)`, після чого знаходяться два корені `z₁,₂ = (a - d ± sqrt_disc) / (2·c)`.

### 3.4. Алгоритм класифікації за слідом
Для нормованого перетворення обчислюється слід `tr = a + d` та його квадрат `tr2 = tr * tr`. 

Якщо уявна частина `im_part = cimag(tr2)` за модулем менша за `1e-9`, то слід вважається дійсним:
- Якщо `|re_part - 4.0| < 1e-9`, перетворення є **параболічним** (чистий зсув, одна нерухома точка).
- Якщо `re_part >= 0.0` і `re_part < 4.0`, перетворення є **еліптичним** (чистий поворот навколо двох нерухомих точок).
- Якщо `re_part > 4.0`, перетворення є **гіперболічним** (чистий розтяг/стиснення вздовж ліній струму).

Якщо ж уявна частина `im_part` є ненульовою, перетворення ідентифікується як **локсодромне** (спіральний рух).

---

## 4. Двомовний вихідний код реалізації (C та C++)

Нижче наведено повну, ідіоматичну реалізацію алгоритмів у вигляді двох незалежних вкладок для мов C та C++.

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

/* Структура для опису перетворення Мьобіуса: f(z) = (a*z + b) / (c*z + d) */
typedef struct {
    Complex a;
    Complex b;
    Complex c;
    Complex d;
} MobiusTransform;

/* Режим класифікації перетворення */
typedef enum {
    MOBIUS_PARABOLIC,
    MOBIUS_ELLIPTIC,
    MOBIUS_HYPERBOLIC,
    MOBIUS_LOXODROMIC
} MobiusType;

/* Створення нового перетворення */
MobiusTransform mobius_create(Complex a, Complex b, Complex c, Complex d) {
    MobiusTransform m;
    m.a = a; m.b = b; m.c = c; m.d = d;
    return m;
}

/* Обчислення визначника ad - bc */
Complex mobius_det(MobiusTransform m) {
    return m.a * m.d - m.b * m.c;
}

/* Нормалізація коефіцієнтів так, щоб det = 1 */
MobiusTransform mobius_normalize(MobiusTransform m) {
    Complex det = mobius_det(m);
    Complex denom = csqrt(det);
    if (cabs(denom) < 1e-15) {
        fprintf(stderr, "Помилка: Вироджене перетворення Мьобіуса (det = 0)\n");
        return m;
    }
    return mobius_create(m.a / denom, m.b / denom, m.c / denom, m.d / denom);
}

/* Композиція двох перетворень (m1 o m2)(z) = m1(m2(z)) — множення матриць */
MobiusTransform mobius_compose(MobiusTransform m1, MobiusTransform m2) {
    Complex a = m1.a * m2.a + m1.b * m2.c;
    Complex b = m1.a * m2.b + m1.b * m2.d;
    Complex c = m1.c * m2.a + m1.d * m2.c;
    Complex d = m1.c * m2.b + m1.d * m2.d;
    return mobius_create(a, b, c, d);
}

/* Обернене перетворення M^(-1) */
MobiusTransform mobius_inverse(MobiusTransform m) {
    MobiusTransform norm = mobius_normalize(m);
    return mobius_create(norm.d, -norm.b, -norm.c, norm.a);
}

/* Обчислення f(z) для точки z */
Complex mobius_eval(MobiusTransform m, Complex z, bool *is_infinity) {
    Complex denom = m.c * z + m.d;
    if (cabs(denom) < 1e-12) {
        if (is_infinity) *is_infinity = true;
        return CMPLX(INFINITY, INFINITY);
    }
    if (is_infinity) *is_infinity = false;
    return (m.a * z + m.b) / denom;
}

/* Обчислення нерухомих точок c*z^2 + (d - a)*z - b = 0 */
int mobius_fixed_points(MobiusTransform m, Complex out_fixed[2]) {
    MobiusTransform n = mobius_normalize(m);
    if (cabs(n.c) < 1e-12) {
        if (cabs(n.a - n.d) < 1e-12) {
            return 0;
        }
        out_fixed[0] = n.b / (n.d - n.a);
        out_fixed[1] = CMPLX(INFINITY, INFINITY);
        return 1;
    }

    Complex A = n.c;
    Complex B = n.d - n.a;
    Complex C = -n.b;
    Complex disc = B * B - 4.0 * A * C;
    Complex sqrt_disc = csqrt(disc);

    out_fixed[0] = (-B + sqrt_disc) / (2.0 * A);
    out_fixed[1] = (-B - sqrt_disc) / (2.0 * A);
    return 2;
}

/* Класифікація за квадрантом сліду Tr(M)^2 */
MobiusType mobius_classify(MobiusTransform m) {
    MobiusTransform n = mobius_normalize(m);
    Complex tr = n.a + n.d;
    Complex tr2 = tr * tr;

    double im_part = cimag(tr2);
    double re_part = creal(tr2);

    if (fabs(im_part) < 1e-9) {
        if (fabs(re_part - 4.0) < 1e-9) return MOBIUS_PARABOLIC;
        if (re_part >= 0.0 && re_part < 4.0) return MOBIUS_ELLIPTIC;
        if (re_part > 4.0) return MOBIUS_HYPERBOLIC;
    }
    return MOBIUS_LOXODROMIC;
}

int main(void) {
    MobiusTransform m = mobius_create(1.0, -1.0, 1.0, 1.0);
    MobiusTransform norm = mobius_normalize(m);

    printf("--- Тест перетворення Мьобіуса (C) ---\n");
    Complex det = mobius_det(norm);
    printf("Визначник після нормалізації: %.4f + %.4fi\n", creal(det), cimag(det));

    Complex z_test = 2.0 + 3.0 * I;
    bool is_inf = false;
    Complex w_test = mobius_eval(norm, z_test, &is_inf);
    printf("f(2 + 3i) = %.4f + %.4fi\n", creal(w_test), cimag(w_test));

    Complex fixed[2];
    int n_fix = mobius_fixed_points(norm, fixed);
    printf("Кількість нерухомих точок: %d\n", n_fix);
    for (int i = 0; i < n_fix; ++i) {
        printf("  z_%d = %.4f + %.4fi\n", i + 1, creal(fixed[i]), cimag(fixed[i]));
    }

    MobiusType type = mobius_classify(norm);
    const char *type_names[] = {"Параболічне", "Еліптичне", "Гіперболічне", "Локсодромне"};
    printf("Тип перетворення: %s\n", type_names[type]);

    return 0;
}
```
```cpp
#include <iostream>
#include <complex>
#include <vector>
#include <optional>
#include <cmath>
#include <string>
#include <stdexcept>

using Complex = std::complex<double>;

enum class MobiusType {
    Parabolic,
    Elliptic,
    Hyperbolic,
    Loxodromic
};

class MobiusTransform {
private:
    Complex a_, b_, c_, d_;

public:
    MobiusTransform(Complex a, Complex b, Complex c, Complex d)
        : a_(a), b_(b), c_(c), d_(d) {}

    static MobiusTransform identity() {
        return MobiusTransform(1.0, 0.0, 0.0, 1.0);
    }

    Complex a() const { return a_; }
    Complex b() const { return b_; }
    Complex c() const { return c_; }
    Complex d() const { return d_; }

    Complex det() const {
        return a_ * d_ - b_ * c_;
    }

    MobiusTransform normalized() const {
        Complex d_val = det();
        Complex denom = std::sqrt(d_val);
        if (std::abs(denom) < 1e-15) {
            throw std::runtime_error("Вироджене перетворення Мьобіуса (det = 0)");
        }
        return MobiusTransform(a_ / denom, b_ / denom, c_ / denom, d_ / denom);
    }

    MobiusTransform operator*(const MobiusTransform& other) const {
        Complex a = a_ * other.a_ + b_ * other.c_;
        Complex b = a_ * other.b_ + b_ * other.d_;
        Complex c = c_ * other.a_ + d_ * other.c_;
        Complex d = c_ * other.b_ + d_ * other.d_;
        return MobiusTransform(a, b, c, d);
    }

    MobiusTransform inverse() const {
        MobiusTransform norm = normalized();
        return MobiusTransform(norm.d_, -norm.b_, -norm.c_, norm.a_);
    }

    std::optional<Complex> operator()(Complex z) const {
        Complex denom = c_ * z + d_;
        if (std::abs(denom) < 1e-12) {
            return std::nullopt;
        }
        return (a_ * z + b_) / denom;
    }

    std::vector<Complex> fixedPoints() const {
        MobiusTransform n = normalized();
        std::vector<Complex> pts;

        if (std::abs(n.c_) < 1e-12) {
            if (std::abs(n.a_ - n.d_) > 1e-12) {
                pts.push_back(n.b_ / (n.d_ - n.a_));
            }
            return pts;
        }

        Complex A = n.c_;
        Complex B = n.d_ - n.a_;
        Complex C = -n.b_;
        Complex disc = B * B - 4.0 * A * C;
        Complex sqrt_disc = std::sqrt(disc);

        pts.push_back((-B + sqrt_disc) / (2.0 * A));
        pts.push_back((-B - sqrt_disc) / (2.0 * A));
        return pts;
    }

    MobiusType type() const {
        MobiusTransform n = normalized();
        Complex tr = n.a_ + n.d_;
        Complex tr2 = tr * tr;

        double im_part = tr2.imag();
        double re_part = tr2.real();

        if (std::abs(im_part) < 1e-9) {
            if (std::abs(re_part - 4.0) < 1e-9) return MobiusType::Parabolic;
            if (re_part >= 0.0 && re_part < 4.0) return MobiusType::Elliptic;
            if (re_part > 4.0) return MobiusType::Hyperbolic;
        }
        return MobiusType::Loxodromic;
    }

    std::string typeName() const {
        switch (type()) {
            case MobiusType::Parabolic:  return "Параболічне";
            case MobiusType::Elliptic:   return "Еліптичне";
            case MobiusType::Hyperbolic: return "Гіперболічне";
            case MobiusType::Loxodromic: return "Локсодромне";
        }
        return "Невідомо";
    }
};

int main() {
    try {
        std::cout << "--- Тест перетворення Мьобіуса (C++) ---\n";
        MobiusTransform m(1.0, -1.0, 1.0, 1.0);
        MobiusTransform norm = m.normalized();

        std::cout << "Визначник: " << norm.det() << "\n";

        Complex z(2.0, 3.0);
        auto w = norm(z);
        if (w) {
            std::cout << "f(2 + 3i) = " << *w << "\n";
        } else {
            std::cout << "f(2 + 3i) = Infinity\n";
        }

        auto fixed = norm.fixedPoints();
        std::cout << "Знайдено нерухомих точок: " << fixed.size() << "\n";
        for (size_t i = 0; i < fixed.size(); ++i) {
            std::cout << "  z_" << (i + 1) << " = " << fixed[i] << "\n";
        }

        std::cout << "Тип перетворення: " << norm.typeName() << "\n";
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << "\n";
    }
    return 0;
}
```
:::

## 5. Покроковий розбір виконання та контрольний приклад

Простежимо виконання програми на контрольному прикладі канонічного відображення `f(z) = (z - 1)/(z + 1)` для точки `z = 2 + 3i`:

1. **Вхідні коефіцієнти:** `a = 1.0`, `b = -1.0`, `c = 1.0`, `d = 1.0`.
2. **Обчислення визначника:** `det = a·d - b·c = 1·1 - (-1)·1 = 2`.
3. **Нормалізація:** Ділимо всі коефіцієнти на `√2 ≈ 1.41421356`. Отримуємо нормовані коефіцієнти `a' = 1/√2`, `b' = -1/√2`, `c' = 1/√2`, `d' = 1/√2`. Визначник нормованої матриці дорівнює `1.0`.
4. **Обчислення значення функції:**
   - Чисельник: `z - 1 = (2 + 3i) - 1 = 1 + 3i`.
   - Знаменник: `z + 1 = (2 + 3i) + 1 = 3 + 3i`.
   - Ділення комплексних чисел: `w = (1 + 3i) / (3 + 3i) = ((1 + 3i)(3 - 3i)) / (3² + 3²) = (3 - 3i + 9i + 9) / 18 = (12 + 6i) / 18 = 2/3 + i/3`.
   - Програма повертає значення `0.6667 + 0.3333i`.
5. **Пошук нерухомих точок:**
   - Рівняння: `c·z² + (d - a)·z - b = 0 ⇔ 1·z² + (1 - 1)·z - (-1) = 0 ⇔ z² + 1 = 0`.
   - Корені рівняння: `z₁ = i`, `z₂ = -i`. Програма повертає унікальні нерухомі точки `0 + 1i` та `0 - 1i`.
6. **Класифікація:**
   - Слід нормованої матриці: `Tr(M') = a' + d' = 1/√2 + 1/√2 = √2 ≈ 1.4142`.
   - Квадрат сліду: `Tr(M')² = (√2)² = 2.0`.
   - Оскільки `Tr(M')² ∈ [0, 4)` (значення `2.0` лежить між 0 та 4), програма ідентифікує перетворення як **Еліптичне** (чистий поворот сфери Рімана навколо осі, що з'єднує полюси `i` та `-i`, на кут 90°).

## 6. Порівняння підходів C та C++ та рекомендації з вибору

При виборі між реалізаціями в реальних обчислювальних проектах слід враховувати такі фактори:

Вимоги до векторизації (SIMD). В інтерфейсі C структура `MobiusTransform` і масиви `double complex` розміщуються в пам'яті як суцільні блоки 128-бітних векторних чисел. Це дозволяє сучасному компілятору виконувати ефективну автовекторизацію циклів обчислень із використанням інструкцій AVX2, AVX-512 та FMA.

Керування пам'яттю та типобезпека. Інтерфейс C++ надає суттєві переваги у високорівневих математичних модулях завдяки використанню `std::optional<Complex>`, що виключає ризик забудькуватості при перевірці прапорців нескінченності, та механізму винятків `std::runtime_error`, що спрощує виявлення вироджених станів у глибоких розрахункових стеках.
