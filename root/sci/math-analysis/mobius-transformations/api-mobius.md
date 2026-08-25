# 📋 Інтерфейс бібліотеки дробово-лінійних перетворень

Цей довідник описує повний контракт публічного програмного інтерфейсу (API) бібліотеки `libmobius` мовами C та C++, призначеної для алгебраїчних операцій з дробово-лінійними перетвореннями Мьобіуса, аналізу їхніх інваріантів, обчислення нерухомих точок, класифікації за слідом та обробки конформних сіток у релятивістській механіці, оптиці й гідродінаміці.

## 1. Загальний огляд інтерфейсу та архітектурні принципи

Бібліотека `libmobius` надає два паралельних, взаємодоповнюючих контракти:

Першим контрактом є C API (`mobius.h`). Це процедурний інтерфейс на основі чистих структур даних `MobiusTransform`, C99-комплексних чисел `double complex` та функціональних викликів із явними покажчиками на статус помилки. Цей інтерфейс не має зовнішніх залежностей від сторонніх бібліотек, володіє високою ефективністю використання кЕшу процесора і призначений для вбудованих систем, розрахункових ядер та C-FFI обгорток для мов високого рівня, таких як Python, Rust чи Julia.

Другим контрактом є C++ API (`mobius.hpp`). Це об'єктно-орієнтований інтерфейс у просторі імен `mobius::`, що використовує `std::complex<double>`, строгу типізацію, безпечні контейнери `std::optional`, `std::vector`, `std::span` (C++20), перевантаження операторів та гарантії RAII. Всі методи даного інтерфейсу є безпечними з точки зору пам'яті та коректно вивільняють ресурси при виникненні виняткових ситуацій.

Обидва інтерфейси є повністю сумісними на рівні Binary ABI та гарантують абсолютно тотожний математичний результат при однакових вхідних даних.

## 2. Модель даних, особливості та канали помилок

### 2.1. Представлення чисел та особливих точок
Перетворення Мьобіуса діє на розширеній комплексній площині `ℂ̂ = ℂ ∪ {∞}` (сфері Рімана). Точка `∞` подається за допомогою спеціального прапорця або значень `INFINITY` у дійсній та уявній частинах.

В інтерфейсі мови C точка на нескінченності позначається прапорцем `is_infinity = true` у структурі або поверненням значення `CMPLX(INFINITY, INFINITY)` та встановленням вихідного прапорця у відповідному аргументі виклику.

В інтерфейсі мови C++ точка на нескінченності позначається порожнім значенням `std::nullopt` у типі `std::optional<Complex>`. Це дозволяє уникнути невизначеної поведінки при обчисленні особливих точок і запобігає виникненню виключень `NaN` під час подальших алгебраїчних маніпуляцій.

### 2.2. Коди помилок та винятки
В інтерфейсі C функції повертають перераховний тип `MobiusStatus` (`MOBIUS_SUCCESS`, `MOBIUS_ERR_SINGULAR`, `MOBIUS_ERR_INVALID_POINTS`, `MOBIUS_ERR_NULL_POINTER`). Будь-який виклик, який повертає значення, відмінне від `MOBIUS_SUCCESS`, гарантує, що вихідні аргументи не були модифіковані в частковому стані.

В інтерфейсі C++ при виникненні виродженого стану (наприклад, спробі створити перетворення з `ad - bc = 0`) ґенерується виняток `mobius::SingularMatrixException`, успадкований від `std::runtime_error`. Це забезпечує повний контроль над ланцюжком помилок при обробці математичних виразів.

---

## 3. Детальний довідник функцій C API (`mobius.h`)

Цей розділ містить детальний опис кожної функції C API, її аргументів, умов виконання, повертаних значень та гарантій чисельної стійкості.

### 3.1. Функція `mobius_create`

Функція `mobius_create` приймає чотири комплексні коефіцієнти `a, b, c, d` типу `double complex` і повертає заповнену структуру `MobiusTransform`. Ця функція є базовим конструктором і не виконує внутрішньої нормалізації чи перевірки визначника, що дозволяє створювати тимчасові вирази з мінімальними затримками виконання.

Аргумент `a` визначає комплексний коефіцієнт при `z` у чисельнику. Аргумент `b` задає вільний комплексний доданок чисельника. Аргумент `c` задає коефіцієнт при `z` у знаменнику, який відповідає за нелінійну інверсію та переведення скінченних точок у нескінченність. Аргумент `d` задає вільний доданок знаменника. Функція не виділяє пам'ять у купі і є абсолютно безпечною для виклику в потоках реального часу.

### 3.2. Функція `mobius_normalize`

Функція `mobius_normalize` приймає покажчик на вхідне перетворення `in_m` і покажчик на вихідну структуру `out_m`. Вона обчислює комплексний визначник `det = a·d - b·c`, знаходить його квадратний корінь `denom = csqrt(det)` і ділить кожен з чотирьох коефіцієнтів на отримане значення.

Якщо модуль визначника `|ad - bc|` є меншим за поріг `1e-15`, матриця вважається чисельно виродженою. У цьому випадку функція повертає код помилки `MOBIUS_ERR_SINGULAR`, а вміст `out_m` залишається незмінним. При успішному виконанні функція повертає `MOBIUS_SUCCESS`, а обчислене перетворення гарантує визначник, точно рівний `1.0 + 0.0i`.

### 3.3. Функція `mobius_from_three_points`

Функція `mobius_from_three_points` здійснює геометричне конструювання перетворення Мьобіуса за трьома парами заданих точок. Вона приймає початкові точки `z1, z2, z3` та їхні бажані образи `w1, w2, w3`.

Використовуючи інваріантність подвійного відношення `(w, w1; w2, w3) = (z, z1; z2, z3)`, функція будує унікальну матрицю `MobiusTransform`. Якщо будь-які дві точки в трійці `z` або в трійці `w` збігаються між собою з точністю до `1e-12`, геометрія відображення втрачає однозначність, і функція повертає код помилки `MOBIUS_ERR_INVALID_POINTS`.

### 3.4. Функція `mobius_compose`

Функція `mobius_compose` обчислює композицію двох перетворень Мьобіуса `(m1 o m2)(z) = m1(m2(z))`. Вона приймає покажчики на два вхідні перетворення `m1` і `m2` та покажчик для збереження результату `out_result`.

Математично операція зводиться до множення двох квадратних комплексних матриць розміру `2×2`. Операція композиції є некомутативною: результат `m1 * m2` у загальному випадку не дорівнює `m2 * m1`. Складність функції становить `O(1)`, вона виконує 8 комплексних множень і 4 комплексні додавання.

### 3.5. Функція `mobius_inverse`

Функція `mobius_inverse` обчислює обернене перетворення Мьобіуса `M⁻¹`. Вона приймає вхідне перетворення `in_m` і записує результат у `out_inv`.

Перед обчисленням оберненої матриці функція виконує нормалізацію вхідного перетворення. Для нормованої матриці з коефіцієнтами `a, b, c, d` обернена матриця обчислюється за явною формулою `a' = d`, `b' = -b`, `c' = -c`, `d' = a`. Це гарантує, що композиція `M * M⁻¹` дає тотожне перетворення з точністю до машинного `ε`.

### 3.6. Функції `mobius_det` та `mobius_trace`

Функція `mobius_det` обчислює та повертає комплексне значення визначника `a·d - b·c`. Вона використовується для перевірки невиродженості перетворення перед виконанням складних геометричних побудов.

Функція `mobius_trace` обчислює слід нормованої матриці `Tr(M) = a + d`. Вона автоматично нормалізує вхідне перетворення і повертає комплексне значення сліду, яке використовується для подальшої класифікації геометричного типу відображення.

### 3.7. Функція `mobius_eval`

Функція `mobius_eval` виконує точкове обчислення відображення `w = (a·z + b)/(c·z + d)`. Вона приймає перетворення `m`, комплексне значення `z` та покажчик на булевий прапорець `out_is_infinity`.

Спочатку функція обчислює знаменник `denom = c·z + d`. Якщо модуль знаменника `|denom|` менший за поріг `1e-12`, функція фіксує особливу точку, записує `true` за покажчиком `out_is_infinity` і повертає константу `CMPLX(INFINITY, INFINITY)`. В іншому випадку вона обчислює частку чисельника та знаменника, записує `false` у прапорець і повертає скінченне комплексне значення `w`.

### 3.8. Функція `mobius_eval_array`

Функція `mobius_eval_array` призначена для масової трансформації масивів комплексних точок. Вона приймає покажчик на перетворення `m`, вхідний масив точок `in_z`, вихідний масив `out_w`, масив прапорців нескінченності `out_is_inf_flags` та кількість точок `count`.

Функція виконує цикл обчислень без виділення додаткової пам'яті в купі. Завдяки суцільному розміщенню даних у пам'яті (flat array layout), сучасні C-компілятори автоматично векторизують цей цикл з використанням векторних інструкцій AVX2 та AVX-512, що забезпечує обробку мільйонів точок за секунду під час розрахунку гідродінамічних сіток чи оптичних полів.

### 3.9. Функції `mobius_fixed_points`, `mobius_cross_ratio` та `mobius_classify`

Функція `mobius_fixed_points` обчислює нерухомі точки перетворення з рівняння `c·z² + (d - a)·z - b = 0`. Вона записує знайдені корені у масив `out_points` і повертає кількість скінченних нерухомих точок (1 або 2).

Функція `mobius_cross_ratio` приймає чотири комплексні точки `z1, z2, z3, z4` і обчислює їхнє подвійне відношення `((z1 - z3)·(z2 - z4)) / ((z1 - z4)·(z2 - z3))`.

Функція `mobius_classify` аналізує квадрат сліду нормованої матриці `Tr(M)²` і повертає значення `MobiusType`, класифікуючи перетворення як параболічне, еліптичне, гіперболічне чи локсодромне.

---

## 4. Опис типів даних та структур C++ API (`mobius.hpp`)

У C++ API клас `mobius::Transform` інкапсулює внутрішній стан і надає методи для безпечного виконання всіх операцій.

Метод `normalized()` повертає новий об'єкт `Transform`, нормований умовою `det = 1`, або кидає виняток `SingularMatrixException`.

Перевантажений оператор `operator*` здійснює композицію двох перетворень.

Перевантажений оператор `operator()(Complex z)` виконує обчислення значення функції у точці `z` і повертає `std::optional<Complex>`, де значення `std::nullopt` відповідає нескінченній точці.

Метод `fixedPoints()` повертає `std::vector<Complex>`, що містить знайдені нерухомі точки.

Метод `type()` повертає значення перераховного типу `MobiusType`, а метод `typeName()` повертає текстову назву класифікаційного типу українською мовою (`"Параболічне"`, `"Еліптичне"`, `"Гіперболічне"`, `"Локсодромне"`).

---

## 5. Повні заголовочні файли інтерфейсу

Нижче наведено повний текст заголовочних файлів бібліотеки `libmobius`.

:::tabs
```c
/* mobius.h — Офіційний C-інтерфейс бібліотеки libmobius */
#ifndef MOBIUS_H
#define MOBIUS_H

#include <stddef.h>
#include <stdbool.h>
#include <complex.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    MOBIUS_SUCCESS = 0,
    MOBIUS_ERR_SINGULAR = -1,
    MOBIUS_ERR_INVALID_POINTS = -2,
    MOBIUS_ERR_NULL_POINTER = -3
} MobiusStatus;

typedef enum {
    MOBIUS_PARABOLIC = 0,
    MOBIUS_ELLIPTIC = 1,
    MOBIUS_HYPERBOLIC = 2,
    MOBIUS_LOXODROMIC = 3
} MobiusType;

typedef struct {
    double complex a;
    double complex b;
    double complex c;
    double complex d;
} MobiusTransform;

/* Публічні прототипи функцій */
MobiusTransform mobius_create(double complex a, double complex b, double complex c, double complex d);
MobiusStatus mobius_normalize(const MobiusTransform *in_m, MobiusTransform *out_m);
MobiusStatus mobius_from_three_points(double complex z1, double complex z2, double complex z3,
                                       double complex w1, double complex w2, double complex w3,
                                       MobiusTransform *out_m);

MobiusStatus mobius_compose(const MobiusTransform *m1, const MobiusTransform *m2, MobiusTransform *out_result);
MobiusStatus mobius_inverse(const MobiusTransform *in_m, MobiusTransform *out_inv);
double complex mobius_det(const MobiusTransform *m);
double complex mobius_trace(const MobiusTransform *m);

double complex mobius_eval(const MobiusTransform *m, double complex z, bool *out_is_infinity);
MobiusStatus mobius_eval_array(const MobiusTransform *m, const double complex *in_z,
                               double complex *out_w, bool *out_is_inf_flags, size_t count);

int mobius_fixed_points(const MobiusTransform *m, double complex out_points[2], bool out_is_inf[2]);
double complex mobius_cross_ratio(double complex z1, double complex z2, double complex z3, double complex z4);
MobiusType mobius_classify(const MobiusTransform *m);

#ifdef __cplusplus
}
#endif

#endif /* MOBIUS_H */
```
```cpp
// mobius.hpp — Офіційний C++20/C++17 інтерфейс бібліотеки libmobius
#ifndef MOBIUS_HPP
#define MOBIUS_HPP

#include <complex>
#include <vector>
#include <optional>
#include <string>
#include <stdexcept>
#include <span>

namespace mobius {

using Complex = std::complex<double>;

class SingularMatrixException : public std::runtime_error {
public:
    explicit SingularMatrixException(const std::string& msg)
        : std::runtime_error(msg) {}
};

enum class MobiusType {
    Parabolic,
    Elliptic,
    Hyperbolic,
    Loxodromic
};

class Transform {
private:
    Complex a_, b_, c_, d_;

public:
    Transform(Complex a, Complex b, Complex c, Complex d)
        : a_(a), b_(b), c_(c), d_(d) {}

    static Transform identity() noexcept {
        return Transform(1.0, 0.0, 0.0, 1.0);
    }

    static Transform fromThreePoints(Complex z1, Complex z2, Complex z3,
                                      Complex w1, Complex w2, Complex w3);

    [[nodiscard]] Complex a() const noexcept { return a_; }
    [[nodiscard]] Complex b() const noexcept { return b_; }
    [[nodiscard]] Complex c() const noexcept { return c_; }
    [[nodiscard]] Complex d() const noexcept { return d_; }

    [[nodiscard]] Complex det() const noexcept {
        return a_ * d_ - b_ * c_;
    }

    [[nodiscard]] Complex trace() const noexcept {
        Transform n = normalized();
        return n.a_ + n.d_;
    }

    [[nodiscard]] Transform normalized() const {
        Complex d_val = det();
        Complex denom = std::sqrt(d_val);
        if (std::abs(denom) < 1e-15) {
            throw SingularMatrixException("Вироджене перетворення Мьобіуса: det = 0");
        }
        return Transform(a_ / denom, b_ / denom, c_ / denom, d_ / denom);
    }

    [[nodiscard]] Transform operator*(const Transform& other) const noexcept {
        Complex a = a_ * other.a_ + b_ * other.c_;
        Complex b = a_ * other.b_ + b_ * other.d_;
        Complex c = c_ * other.a_ + d_ * other.c_;
        Complex d = c_ * other.b_ + d_ * other.d_;
        return Transform(a, b, c, d);
    }

    [[nodiscard]] Transform inverse() const {
        Transform norm = normalized();
        return Transform(norm.d_, -norm.b_, -norm.c_, norm.a_);
    }

    [[nodiscard]] std::optional<Complex> operator()(Complex z) const noexcept {
        Complex denom = c_ * z + d_;
        if (std::abs(denom) < 1e-12) {
            return std::nullopt;
        }
        return (a_ * z + b_) / denom;
    }

    void transformBuffer(std::span<const Complex> in_points,
                         std::span<Complex> out_points,
                         std::span<bool> out_inf_flags) const;

    [[nodiscard]] std::vector<Complex> fixedPoints() const;
    [[nodiscard]] MobiusType type() const;
    [[nodiscard]] std::string typeName() const;
};

[[nodiscard]] Complex crossRatio(Complex z1, Complex z2, Complex z3, Complex z4) noexcept;

} // namespace mobius

#endif // MOBIUS_HPP
```
:::

## 6. Зведення контракту, складності та крайових випадків

Нижче наведено підсумкову таблицю параметрів для всіх ключових функцій та методів бібліотеки.

| Операція | C API Функція | C++ API Метод | Часова складність | Крайові випадки та винятки |
| :--- | :--- | :--- | :--- | :--- |
| **Нормалізація** | `mobius_normalize()` | `Transform::normalized()` | `O(1)` | `det = 0` повертає `MOBIUS_ERR_SINGULAR` або `SingularMatrixException` |
| **Побудова по 3 точках** | `mobius_from_three_points()` | `Transform::fromThreePoints()` | `O(1)` | Збіг двох точок повертає `MOBIUS_ERR_INVALID_POINTS` |
| **Композиція** | `mobius_compose()` | `operator*` | `O(1)` | Некомутативна операція (`M1 * M2 ≠ M2 * M1`) |
| **Інверсія** | `mobius_inverse()` | `Transform::inverse()` | `O(1)` | Вимагає попередньої нормалізації |
| **Обчислення точки** | `mobius_eval()` | `operator()(z)` | `O(1)` | `c*z + d = 0` повертає `is_infinity = true` або `std::nullopt` |
| **Трансформація масиву** | `mobius_eval_array()` | `transformBuffer()` | `O(N)` | Призначено для векторизації SIMD; без виділення динамічної пам'яті |
| **Нерухомі точки** | `mobius_fixed_points()` | `fixedPoints()` | `O(1)` | `c = 0` дає 1 корінь у ℂ та 1 на нескінченності |
| **Подвійне відношення** | `mobius_cross_ratio()` | `mobius::crossRatio()` | `O(1)` | Точки мають бути взаємно різними |
| **Класифікація** | `mobius_classify()` | `Transform::type()` | `O(1)` | Залежить від значення `Tr(M)²` після нормалізації |

## 7. Приклади інтеграції та паттерни використання

При розробці розрахункових ядер у гідродінаміці чи релятивістській оптиці вибір між мовами C та C++ визначається вимогами до інфраструктури проекту.

:::tabs
```c
#include "mobius.h"
#include <stdio.h>
#include <stdlib.h>

void process_hydro_grid(const double complex *grid_in, double complex *grid_out, size_t count) {
    MobiusTransform m = mobius_create(1.0, -1.0, 1.0, 1.0);
    MobiusTransform norm;
    if (mobius_normalize(&m, &norm) != MOBIUS_SUCCESS) {
        fprintf(stderr, "Помилка нормалізації матриці гідродінамічного потоку\n");
        return;
    }

    bool *inf_flags = (bool*)malloc(count * sizeof(bool));
    if (!inf_flags) return;

    mobius_eval_array(&norm, grid_in, grid_out, inf_flags, count);
    free(inf_flags);
}
```
```cpp
#include "mobius.hpp"
#include <iostream>
#include <vector>
#include <cmath>

void process_star_catalog(std::vector<mobius::Complex>& stars, double beta) {
    double psi = std::atanh(beta);
    mobius::Complex a = std::exp(-psi / 2.0);
    mobius::Complex d = std::exp(psi / 2.0);

    mobius::Transform boost(a, 0.0, 0.0, d);

    for (auto& star_coord : stars) {
        auto new_coord = boost(star_coord);
        if (new_coord) {
            star_coord = *new_coord;
        }
    }
}
```
:::
