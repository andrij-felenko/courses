# 📋 Інтерфейс C/C++ бібліотеки для обчислення перманентів матриць

Ця довідкова вставка містить вичерпну специфікацію програмного інтерфейсу (API) обчислювальної бібліотеки `libmatrix_perm`, розробленої для знаходження точних та наближених перманентів квадратних матриць у високопродуктивних обчислювальних середовищах. Інтерфейс охоплює як низькорівневі C-функції із гарантованою ABI-сумісністю, так і сучасний C++20 об'єктно-орієнтований wrapper.

Бібліотека надає два рівні програмного інтерфейсу:
1. **Низькорівневий C-ABI сумісний інтерфейс:** Призначений для інтеграції з мовами C, Python (через `ctypes` або `cffi`), Rust, Go, Julia, MATLAB, а також для використання в системних бібліотеках. Забезпечує строго визначений порядок бінарного виклику (C calling convention), відсутність винятків (exception-free guarantee) та прямий контроль над виділенням динамічної пам'яті.
2. **Високорівневий C++20 інтерфейс:** Обгортковий клас `permanent_solver`, який надає ідіоматичний об'єктно-орієнтований доступ через безпечні типи `std::span`, повернення результату через `std::expected` (або винятки за вибором), підтримку семантики переміщення (RAII) та інтеграцію з сучасними контейнерами стандартної бібліотеки.

---

## 1. Коди помилок та структури конфігурації

Усі функції низькорівневого C-API повертають цілочисельний код статусу `perm_status_t`. Значення `0` (`PERM_SUCCESS`) гарантує успішне виконання обчислень та коректність записаного у вихідний буфер результату. Від'ємні значення відповідають конкретним помилкам виконання.

У структурах конфігурації передаються параметри вибору алгоритму, кількості обчислювальних потоків OpenMP та використання апаратних векторних інструкцій (SIMD: AVX2, AVX-512, ARM NEON).

:::tabs
```c
#ifndef MATRIX_PERM_H
#define MATRIX_PERM_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/** Коди повернення та статус виконання */
typedef enum {
    PERM_SUCCESS             =  0,  /**< Обчислення завершено успішно */
    PERM_ERR_NULL_POINTER    = -1,  /**< Передано нульовий вказівник на матрицю або результат */
    PERM_ERR_INVALID_DIM     = -2,  /**< Некоректна розмірність матриці (n == 0 або n > 62) */
    PERM_ERR_OUT_OF_MEMORY   = -3,  /**< Помилка виділення динамічної пам'яті */
    PERM_ERR_OVERFLOW        = -4,  /**< Виявлено неконтрольоване переповнення для знакового типу */
    PERM_ERR_UNSUPPORTED_ALG = -5   /**< Обрано непідтримуваний алгоритм обчислення */
} perm_status_t;

/** Алгоритм обчислення перманента */
typedef enum {
    PERM_ALG_AUTO            = 0,  /**< Автоматичний вибір кращого алгоритму за розмірністю */
    PERM_ALG_NAIVE           = 1,  /**< Наївний перебір перестановок O(n! · n) */
    PERM_ALG_RYSER_GRAY      = 2,  /**< Формула Райзера з кодом Ґрея O(2ⁿ · n) */
    PERM_ALG_GLYNN           = 3   /**< Алгоритм Ґлінна з векторами знаків O(2ⁿ⁻¹ · n) */
} perm_algorithm_t;

/** Конфігурація параметрів обчислення */
typedef struct {
    perm_algorithm_t algorithm;   /**< Обраний алгоритм */
    size_t           num_threads; /**< Кількість потоків (0 для автовизначення) */
    bool             use_simd;    /**< Прапорець використання SIMD інструкцій */
} perm_config_t;

#ifdef __cplusplus
}
#endif

#endif /* MATRIX_PERM_H */
```
```cpp
#pragma once

#include <cstddef>
#include <cstdint>
#include <system_error>
#include <span>
#include <expected>

namespace math::matrix {

enum class perm_errc {
    success             = 0,
    null_pointer        = 1,
    invalid_dimension   = 2,
    out_of_memory       = 3,
    integer_overflow    = 4,
    unsupported_alg     = 5
};

enum class algorithm {
    auto_select = 0,
    naive       = 1,
    ryser_gray  = 2,
    glynn       = 3
};

struct config {
    algorithm   alg{algorithm::auto_select};
    std::size_t num_threads{0};
    bool        use_simd{true};
};

} // namespace math::matrix
```
:::

---

## 2. Сигнатури функцій C-API та C++ інтерфейсу

Бібліотека надає окремі оптимізовані точки входу для обчислення перманентів цілочисельних 64-бітних матриць `uint64_t`, матриць із дійсними числами подвійної точності `double`, а також модульного обчислення 0/1-матриць за простим модулем `mod_p`.

Усі функції приймають вхідні матриці у вигляді єдиного плоского масиву розміром `n * n` у стандартному форматі розташованих по рядках елементів (англ. *row-major order*).

:::tabs
```c
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Обчислення перманента цілочисельної 64-бітної матриці n x n.
 *
 * @param[in]  matrix   Вказівник на плоский масив елементів розміром n*n в C-style (row-major).
 * @param[in]  n        Розмірність квадратної матриці (n <= 62).
 * @param[in]  cfg      Вказівник на конфігурацію (можна NULL для параметрів за замовчуванням).
 * @param[out] out_perm Вказівник на змінну для запису результату.
 * @return Код статусу perm_status_t.
 */
perm_status_t perm_compute_u64(const uint64_t *matrix,
                               size_t           n,
                               const perm_config_t *cfg,
                               uint64_t        *out_perm);

/**
 * @brief Обчислення перманента матриці дійсних чисел double n x n.
 *
 * @param[in]  matrix   Вказівник на плоский масив елементів n*n.
 * @param[in]  n        Розмірність квадратної матриці.
 * @param[in]  cfg      Вказівник на конфігурацію.
 * @param[out] out_perm Вказівник на змінну результату.
 * @return Код статусу perm_status_t.
 */
perm_status_t perm_compute_f64(const double    *matrix,
                               size_t           n,
                               const perm_config_t *cfg,
                               double          *out_perm);

/**
 * @brief Обчислення перманента 0/1 матриці за модулем p.
 *
 * @param[in]  matrix   Вказівник на 0/1 матрицю.
 * @param[in]  n        Розмірність матриці.
 * @param[in]  mod_p    Просте число p для модульної арифметики.
 * @param[out] out_perm Вказівник на результат mod p.
 * @return Код статусу perm_status_t.
 */
perm_status_t perm_compute_mod_p(const uint8_t *matrix,
                                 size_t          n,
                                 uint64_t        mod_p,
                                 uint64_t       *out_perm);

#ifdef __cplusplus
}
#endif
```
```cpp
#pragma once

#include <span>
#include <cstddef>
#include <cstdint>
#include <expected>

namespace math::matrix {

class permanent_solver {
public:
    explicit permanent_solver(config cfg = {}) noexcept : cfg_(cfg) {}

    // Обчислення перманента для цілочисельного срізу std::span
    [[nodiscard]] std::expected<std::uint64_t, perm_errc>
    compute(std::span<const std::uint64_t> matrix, std::size_t n) const noexcept;

    // Обчислення перманента для дійсних чисел std::span
    [[nodiscard]] std::expected<double, perm_errc>
    compute(std::span<const double> matrix, std::size_t n) const noexcept;

    // Модульне обчислення перманента mod p
    [[nodiscard]] std::expected<std::uint64_t, perm_errc>
    compute_mod(std::span<const std::uint8_t> matrix, std::size_t n, std::uint64_t mod_p) const noexcept;

private:
    config cfg_;
};

} // namespace math::matrix
```
:::

---

## 3. Деталізація контрактів, пам'яті та крайових випадків

Обчислення перманентів вимагає дотримання чітких математичних та системних контрактів між викликаючим кодом та бібліотекою `libmatrix_perm`. Нижче детально розібрано кожен аспект.

### Порядок розміщення елементів (Memory Layout)
- **Розташування за рядками (Row-Major Order):** Усі масиви сприймаються як послідовність рядків. Елемент у рядку `r` (від `0` до `n-1`) та стовпці `c` (від `0` до `n-1`) повинен мати індекс у масиві `index = r * n + c`.
- **Вирівнювання вказувачів (Alignment):** Для забезпечення максимальної продуктивності векторизатора AVX2/AVX-512 рекомендується вирівнювати вказівники на елементи матриці на межу 32 або 64 байт за допомогою системних викликів `aligned_alloc` або `posix_memalign`.

### Еевристичний вибір алгоритму (`PERM_ALG_AUTO`)
Якщо у конфігурації вказано `PERM_ALG_AUTO`, бібліотека застосовує наступне правило:
1. Якщо `n <= 6`, обирається наївний алгоритм через незначні накладні витрати підготовки коду Ґрея.
2. Якщо матриця дійсних чисел `double`, обирається алгоритм Ґлінна `PERM_ALG_GLYNN` через меншу кількість ітерацій `2ⁿ⁻¹` та вищу чисельну стійкість.
3. Якщо матриця цілочисельна 0/1 `uint64_t`, обирається алгоритм Райзера з кодом Ґрея `PERM_ALG_RYSER_GRAY`.

### Крайові випадки та обробка виключних ситуацій (Edge Cases)
1. **Порожня матриця (`n = 0`):** Передача `n = 0` вважається помилкою розмірності. Функція повертає статус `PERM_ERR_INVALID_DIM` у C-API або об'єкт помилки `perm_errc::invalid_dimension` у C++ API.
2. **Матриця розміром 1 × 1 (`n = 1`):** Значення перманента збігається з єдиним елементом матриці: `perm([a₁₁]) = a₁₁`. Обчислення виконується напряму за `O(1)` без виділення пам'яті.
3. **Нульові рядки та стовпці:** До початку обчислень бібліотека виконує швидке сканування вхідної матриці. Якщо виявлено хоча б один повністю нульовий рядок або стовпець, функція перериває виконання та миттєво повертає `0` без виконання експоненційного обходу `2ⁿ` підмножин.
4. **Обмеження бітової маски (`n > 62`):** Швидкі алгоритми Райзера та Ґлінна спираються на 64-бітну цілочисельну маску коду Ґрея. Для матриць з `n > 62` повертається помилка `PERM_ERR_INVALID_DIM`.

### Потокобезпечність та модель паралелізму (Thread Safety & Concurrency)
- Усі функції C-API та методи C++ класу `permanent_solver` є чисто функціональними (`reentrant`). Вони не використовують статичні або глобальні змінні стану.
- Багатопотоковість розбиває діапазон ітерацій підмножин `2ⁿ⁻¹` між обчислювальними ядрами за допомогою OpenMP. Кожен потік оперує власним вектором рядкових сум `row_sum` у локальній пам'яті, що запобігає ефекту хибного розділення кеш-ліній (англ. *false sharing*).
- Проміжні вектори рядкових сум виділяються у стеку або через виділений локальний алокатор, що забезпечує повну потокобезпечність при паралельному виклику з різних ниток.

### Чисельна стійкість та втрата точності (Numerical Stability)
- При обчисленні перманентів матриць із дійсними числами `double` великих розмірностей (`n > 25`) скасування великих значень у знакозмінній сумі Райзера може призвести до катастрофічної втрати точності (англ. *catastrophic cancellation*).
- У таких випадках розробникам рекомендується обирати алгоритм Ґлінна або використовувати модульну арифметику за кількома простими числами `mod_p` із подальшим відновленням за китайською теоремою про остачі.

### Управління пам'яттю та ресурсами (Memory Ownership Contract)
- Вхідні масиви передаються за вказівниками типу `const` і залишаються незмінними впродовж всього виклику.
- Бібліотека не зберігає вказівники на передані матриці після завершення роботи функції та не виконує асинхронного фонового фонового захоплення ресурсів.
- Уся динамічна пам'ять, необхідна для проміжних рядкових сум `row_sum`, виділяється при вході у функцію та гарантовано звільняється перед поверненням управління викликаючій програмі.

---

## 4. Комплексний приклад використання C та C++ API

Нижче наведено самодостатні приклади програм, які ініціалізують 0/1-матрицю суміжності двочасткового графа та обчислюють її перманент за допомогою бібліотечного інтерфейсу.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include "matrix_perm.h"

int main(void) {
    /* 0/1 матриця суміжності двочасткового графа 4x4 */
    const uint64_t matrix[16] = {
        1, 1, 0, 1,
        1, 0, 1, 0,
        0, 1, 1, 1,
        1, 1, 0, 1
    };
    const size_t n = 4;

    perm_config_t cfg = {
        .algorithm   = PERM_ALG_RYSER_GRAY,
        .num_threads = 1,
        .use_simd    = true
    };

    uint64_t perm_val = 0;
    perm_status_t status = perm_compute_u64(matrix, n, &cfg, &perm_val);

    if (status == PERM_SUCCESS) {
        printf("Перманент матриці 4x4 дорівнює: %lu\n", perm_val);
    } else {
        fprintf(stderr, "Помилка обчислення з кодом: %d\n", status);
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include "matrix_perm.hpp"

int main() {
    const std::vector<double> matrix = {
        1.0, 2.0, 0.0,
        3.0, 1.0, 4.0,
        0.0, 2.0, 1.0
    };
    const std::size_t n = 3;

    math::matrix::permanent_solver solver{
        {.alg = math::matrix::algorithm::glynn}
    };

    auto result = solver.compute(matrix, n);

    if (result.has_value()) {
        std::cout << "Перманент матриці 3x3 дорівнює: " << result.value() << '\n';
    } else {
        std::cerr << "Помилка обчислення перманента\n";
        return 1;
    }

    return 0;
}
```
:::

## 5. Інтеграція з іншими мовами програмування

Завдяки дотриманню C-ABI сумісності, бібліотека `libmatrix_perm` легко підключається до високорівневих мов. Наприклад, у мові Python виклик обчислення перманента через бібліотеку `ctypes` виконується наступним чином:

```python
import ctypes
import numpy as np

# Завантаження динамічної бібліотеки
lib = ctypes.CDLL("./libmatrix_perm.so")

# Визначення аргументів та типу повернення
lib.perm_compute_u64.argtypes = [
    ctypes.POINTER(ctypes.c_uint64),
    ctypes.c_size_t,
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.c_uint64)
]
lib.perm_compute_u64.restype = ctypes.c_int

def compute_permanent(mat: np.ndarray) -> int:
    n = mat.shape[0]
    mat_flat = mat.astype(np.uint64).flatten()
    c_arr = mat_flat.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64))
    res = ctypes.c_uint64(0)
    
    status = lib.perm_compute_u64(c_arr, n, None, ctypes.byref(res))
    if status != 0:
        raise RuntimeError(f"Error computing permanent: code {status}")
    return res.value
```

Це дозволяє використовувати швидкі низькорівневі C/C++ алгоритми обчислення перманентів у середовищах наукових обчислень Python та Data Science.
