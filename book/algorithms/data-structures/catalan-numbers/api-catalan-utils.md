# 📋 Інтерфейс та утиліти чисел Каталана

Довідник системного інтерфейсу, архітектури заголовних файлів, специфікації типів даних та програмних контрактів бібліотеки утиліти для обчислення чисел Каталана, валідації дужкових послідовностей Дюка, генерації топологій двійкових дерев та лаконічного бітового кодування.

## 1. Архітектурні принципи та системні контракти

Бібліотека утиліт чисел Каталана розроблена відповідно до вимог низькорівневого системного програмування. Вона надає сумісний із C89/C99 низькорівневий процедурний інтерфейс для вбудованих систем, ОС-модулів та ядреного коду, а також високорівневу обгортку мовою C++20 із застосуванням семантики переміщення, RAII-управління пам'яттю, типобезпечної системи помилок `std::error_code` та контейнерів `std::vector` і `std::optional`.

### Основні концептуальні вимоги до системного інтерфейсу
1. **Відсутність побічних ефектів та глобального стану**: Усі обчислювальні функції є чистими процедурами (pure functions). Вони не використовують глобальних чи статичних змінних, що змінюються (mutable state), завдяки чому є повністю реентерабельними (reentrant) та беззастережно безпечними для паралельного виконання у багатопотоковому середовищі (thread-safe).
2. **Передбачуваність і детермінізм пам'яті**: Функції точного обчислення одиничних чисел (`catalan_compute`) працюють виключно у фіксованій стековій пам'яті без жодного виклику динамічного аллокатора (`malloc` / `new`). Це гарантує детермінований час виконання `O(n)` без ризику фрагментації купи або затримок аллокатора. Для функцій генерації послідовностей чи дерев пам'ять виділяється явними блоками із чітким розподілом відповідальності за її звільнення між бібліотекою та клієнтським кодом.
3. **Строга перевірка меж та захист від цілочисельного переповнення**: Оскільки 64-бітне беззнакове ціле `uint64_t` переповнюється при `n ≥ 36`, системні функції здійснюють валідацію вхідних аргументів на самому початку і повертають явний код помилки до виконання потенційно небезпечних арифметичних операцій.
4. **Відсутність математичного модуля з плаваючою крапкою (No FPU dependency)**: Обчислення виконуються виключно у цілочисельних регістрах ALU. Це дозволяє використовувати бібліотеку в модулях ядра Linux, обробниках переривань (ISR) та мікроконтролерах без блоку FPU.

### Таблиця складності та меж застосування функцій

| Операція / Функція | Часова складність | Просторова складність | Граничні умови та вимоги до пам'яті |
| :--- | :--- | :--- | :--- |
| `catalan_compute(n)` | `O(n)` | `O(1)` | `n ≤ 35` (для 64-бітного беззнакового `uint64_t`), без динамічної пам'яті |
| `catalan_sequence_dp(n)` | `O(n²)` | `O(n)` | `n ≤ 35`, динамічна пам'ять під масив `(n + 1) * 8` байт у купі |
| `catalan_mod_compute(n, m)` | `O(n log m)` | `O(1)` | `n < m`, `m` — просте число (наприклад `10⁹ + 7` або `998,244,353`) |
| `dyck_validate(seq)` | `O(n)` | `O(1)` | Перевірка балансу дужок за один послідовний прохід без стеку |
| `catalan_tree_unrank(n, r)` | `O(n²)` | `O(n)` | `r < Cₙ`, глибина рекурсивного стеку викликів пропорційна `n` |

### Коди помилок та статуси повернення

Для процедурного C API використовується стандартне цілочисельне кодування статусів повернення. Значення `0` (`CATALAN_SUCCESS`) сигналізує про успішне завершення операції, а від'ємні значення вказують на конкретну причину відмови:

:::tabs
```c
// Коди статусів та помилок процедурного C API
typedef enum {
    CATALAN_SUCCESS          =  0,  // Операція виконана успішно без помилок
    CATALAN_ERR_OVERFLOW     = -1,  // Значення n перевищує межу 64-бітного типу (n > 35)
    CATALAN_ERR_INVALID_PARAM= -2,  // Передано NULL-вказівник або недопустимий аргумент
    CATALAN_ERR_NO_MEMORY    = -3,  // Помилка виділення динамічної пам'яті (calloc/malloc повернув NULL)
    CATALAN_ERR_INVALID_DYCK = -4   // Рядок порушує інваріант правильної дужкової послідовності
} catalan_status_t;
```
```cpp
// Перелічувальний клас статусів та помилок високорівневого C++ API
enum class ErrorCode : std::int32_t {
    Success          =  0,  // Операція виконана успішно без помилок
    Overflow         = -1,  // Значення n перевищує межу 64-бітного типу (n > 35)
    InvalidParameter = -2,  // Передано недопустимий аргумент
    AllocationFailure= -3,  // Помилка виділення динамічної пам'яті
    InvalidDyckSequence = -4 // Рядок порушує інваріант правильної дужкової послідовності
};
```
:::

Для C++ API статуси помилок інтегровані у стандартну систему `std::error_code` та `std::optional`, що дозволяє обробляти відмови у високопродуктивних модулях реального часу без виклику винятків (exceptionless environment).

## 2. Специфікація функцій процедурного C API

### 1. `catalan_compute` — Точне обчислення одиничного числа
Обчислює точне значення `Cₙ` за допомогою лінійного мультиплікативного співвідношення `Cᵢ = Cᵢ⋇ · (4i - 2) / (i + 1)`.
- **Попередні умови (Preconditions)**: Вказівник `out_val` повинен вказувати на дісну виділену область пам'яті. Аргумент `n` повинен відповідати умові `n ≤ 35`.
- **Післяумови (Postconditions)**: У разі повернення `CATALAN_SUCCESS` за адресою `out_val` записано точне значення `Cₙ`. Змінна не змінюється у разі помилки.
- **Аргументи**:
  - `n` (`uint32_t`): Індекс числа Каталана. Допустимий діапазон: `0 ≤ n ≤ 35`.
  - `out_val` (`uint64_t*`): Вказівник на змінну для запису результату.
- **Повертане значення**: `CATALAN_SUCCESS` у разі успіху; `CATALAN_ERR_INVALID_PARAM`, якщо `out_val == NULL`; `CATALAN_ERR_OVERFLOW`, якщо `n > 35`.

### 2. `catalan_sequence_dp` — Генерація таблиці динамічного програмування
Будує та заповнює масив усіх чисел Каталана від `C₀` до `Cₙ` включно за квадратичною формулою Зегнера.
- **Попередні умови**: Вказівник `out_array` не повинен бути `NULL`. Індекс `n` повинен бути не більшим за 35.
- **Аргументи**:
  - `n` (`uint32_t`): Максимальний індекс послідовності (`n ≤ 35`).
  - `out_array` (`uint64_t**`): Вказівник на вказівник, у який записується адреса нововиділеного масиву з `n + 1` елементів.
- **Управління пам'яттю**: Отриманий масив виділяється у динамічній пам'яті через `calloc`. Викликач зобов'язаний звільнити пам'ять викликом `free(*out_array)` після завершення роботи з даними.

### 3. `dyck_validate` — Перевірка валідності шляху Дюка
Оцінює рядок дужок довжини `len` на відповідність інваріантам мови Дюка за один послідовний прохід.
- **Попередні умови**: Вказівник `str` не повинен бути `NULL`. Буфер повинен містити принаймні `len` байт.
- **Аргументи**:
  - `str` (`const char*`): Вказівник на символ-буфер, що містить дужкову послідовність з символів `(` та `)`.
  - `len` (`size_t`): Довжина рядка в байтах.
- **Алгоритмічний інваріант**: Функція підтримує цілочисельний лічильник поточного балансу `balance`. Якщо при скануванні зліва направо `balance < 0` у будь-якій точці, або якщо підсумковий `balance != 0`, функція негайно припиняє обхід і повертає `false`.

## 3. Граничні випадки та протокол перевірки результатів

При інтеграційному тестуванні модуля утиліт необхідно забезпечити повне покриття граничних ситуацій:

1. **Базовий випадок `n = 0`**: За означенням `C₀ = 1`. Функція `catalan_compute(0, &val)` повинна миттєво повертати `CATALAN_SUCCESS` та записувати значення `1`. Рядок порожньої довжини `len = 0` вважається тривіально валідним шляхом Дюка (`balance = 0`).
2. **Верхня межа `n = 35`**: Значення `C₃₅ = 3,116,285,494,907,301,260` є найбільшим числом Каталана, яке розміщується у стандартному беззнаковому 64-бітному типі `uint64_t`. Виклик для `n = 35` повинен завершуватися успішно.
3. **Точка переповнення `n = 36`**: Виклик `catalan_compute(36, &val)` повинен повертати `CATALAN_ERR_OVERFLOW`, залишаючи значення `val` незмінним.
4. **Невалідні дужкові рядки**: Рядки `")("`, `"(()"`, `"))(("` мають негайно відхилятися функцією `dyck_validate` без читання за межами виділеного буфера.

## 4. Модель пам'яті, потокобезпечність та відмовостійкість

Усі алгоритми обчислення числа Каталана в цій бібліотеці спроєктовані з урахуванням суворих вимог до системного програмування:

1. **Реентерабельність**: Алгоритми не зберігають проміжні стани між викликами. Кілька потоків виконання можуть одночасно викликати `catalan_compute` або `dyck_validate` для різних даних без застосування блокувань чи м'ютексів (lock-free / zero-contention).
2. **Захист від витоків пам'яті**: Усі функції C++ API повертають контейнер `std::vector<std::uint64_t>` за семантикою переміщення (move semantics), що унеможливлює витоки пам'яті при виникненні винятків. У C API при виникненні помилки аллокації `catalan_sequence_dp` гарантовано повертає `NULL` і встановлює код `CATALAN_ERR_NO_MEMORY`, не залишаючи частково виділених блоків.
3. **Безоб'єктний дизайн для вбудованих систем**: Інтерфейси C API не вимагають ініціалізації глобальних структур чи контекстів. Це дозволяє використовувати їх безпосередньо в середовищах без операційної системи (bare-metal) та в контролерах із обмеженим обсягом RAM.

## 5. Заголовні файли бібліотеки (C та C++ API)

:::tabs
```c
// catalan_utils.h — C89/C99 сумісний заголовок процедурного C API
#ifndef CATALAN_UTILS_H
#define CATALAN_UTILS_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    CATALAN_SUCCESS          =  0,
    CATALAN_ERR_OVERFLOW     = -1,
    CATALAN_ERR_INVALID_PARAM= -2,
    CATALAN_ERR_NO_MEMORY    = -3,
    CATALAN_ERR_INVALID_DYCK = -4
} catalan_status_t;

/**
 * Обчислює точне значення C_n за лінійний час O(n).
 * @param n Індекс числа Каталана (0 <= n <= 35).
 * @param out_val Вказівник на змінну для запису результату.
 * @return CATALAN_SUCCESS або код помилки.
 */
catalan_status_t catalan_compute(uint32_t n, uint64_t* out_val);

/**
 * Генерує масив усіх чисел Каталана від C_0 до C_n включно.
 * @param n Максимальний індекс (0 <= n <= 35).
 * @param out_array Вказівник на виділений масив (потрібно викликати free()).
 * @return CATALAN_SUCCESS або CATALAN_ERR_NO_MEMORY.
 */
catalan_status_t catalan_sequence_dp(uint32_t n, uint64_t** out_array);

/**
 * Перевіряє, чи є рядок дужок правильною послідовністю (Dyck path).
 * @param str Рядок з символів '(' та ')'.
 * @param len Довжина рядка.
 * @return true, якщо послідовність валідна, інакше false.
 */
bool dyck_validate(const char* str, size_t len);

#ifdef __cplusplus
}
#endif

#endif // CATALAN_UTILS_H
```
```cpp
// catalan_utils.hpp — C++20 заголовок з RAII та типобезпечною обробкою помилок
#ifndef CATALAN_UTILS_HPP
#define CATALAN_UTILS_HPP

#include <cstdint>
#include <vector>
#include <string_view>
#include <optional>
#include <system_error>
#include <stdexcept>

namespace catalan {

enum class ErrorCode {
    Overflow = 1,
    InvalidParameter,
    AllocationFailure,
    InvalidDyckSequence
};

class CatalanErrorCategory : public std::error_category {
public:
    [[nodiscard]] const char* name() const noexcept override { 
        return "catalan"; 
    }
    
    [[nodiscard]] std::string message(int ev) const override {
        switch (static_cast<ErrorCode>(ev)) {
            case ErrorCode::Overflow: 
                return "Catalan number exceeds 64-bit unsigned integer limit (n > 35)";
            case ErrorCode::InvalidParameter: 
                return "Invalid input parameter passed to catalan function";
            case ErrorCode::AllocationFailure: 
                return "Dynamic memory allocation failed during sequence generation";
            case ErrorCode::InvalidDyckSequence: 
                return "Provided string violates Dyck path balance invariant";
            default: 
                return "Unknown catalan system error";
        }
    }
};

inline const CatalanErrorCategory& error_category() noexcept {
    static CatalanErrorCategory instance;
    return instance;
}

inline std::error_code make_error_code(ErrorCode e) noexcept {
    return {static_cast<int>(e), error_category()};
}

class CatalanCalculator {
public:
    // Обчислення точного значення за O(n) з поверненням std::optional
    [[nodiscard]] static std::optional<std::uint64_t> compute(std::uint32_t n) noexcept {
        if (n > 35) {
            return std::nullopt;
        }
        std::uint64_t res = 1;
        for (std::uint64_t i = 1; i <= n; ++i) {
            res = res * (4 * i - 2) / (i + 1);
        }
        return res;
    }

    // Генерація таблиці динамічного програмування в контейнер std::vector
    [[nodiscard]] static std::vector<std::uint64_t> generate_sequence(std::uint32_t n) {
        if (n > 35) {
            throw std::overflow_error("Catalan index n exceeds 64-bit uint limit");
        }
        std::vector<std::uint64_t> c(n + 1, 0);
        c[0] = 1;
        for (std::size_t i = 1; i <= n; ++i) {
            for (std::size_t j = 0; j < i; ++j) {
                c[i] += c[j] * c[i - 1 - j];
            }
        }
        return c;
    }

    // Валідація дужкової послідовності Дюка без виділення пам'яті
    [[nodiscard]] static bool validate_dyck_path(std::string_view seq) noexcept {
        int balance = 0;
        for (char ch : seq) {
            if (ch == '(') {
                balance++;
            } else if (ch == ')') {
                balance--;
                if (balance < 0) return false;
            }
        }
        return balance == 0;
    }
};

} // namespace catalan

#endif // CATALAN_UTILS_HPP
```
:::

## 6. Демонстраційний приклад інтеграції та використання

Нижче наведено детальні приклади використання написаної бібліотеки у реальних проєктах системної розробки.

:::tabs
```c
// main.c — Демонстрація процедурного C API
#include <stdio.h>
#include <stdlib.h>
#include "catalan_utils.h"

int main(void) {
    uint64_t val;
    catalan_status_t st = catalan_compute(10, &val);
    if (st == CATALAN_SUCCESS) {
        printf("Успіх: C_10 = %llu\n", (unsigned long long)val); // 16796
    } else {
        printf("Помилка обчислення: код %d\n", st);
    }

    const char* valid_seq = "((()()))";
    if (dyck_validate(valid_seq, 8)) {
        printf("Рядок %s є валідним шляхом Дюка.\n", valid_seq);
    }

    const char* invalid_seq = "())(";
    if (!dyck_validate(invalid_seq, 4)) {
        printf("Рядок %s некоректний (баланс від'ємний).\n", invalid_seq);
    }

    return 0;
}
```
```cpp
// main.cpp — Демонстрація високорівневого C++ API
#include <iostream>
#include "catalan_utils.hpp"

int main() {
    // 1. Обчислення значення
    if (auto c10 = catalan::CatalanCalculator::compute(10)) {
        std::cout << "C_10 = " << *c10 << "\n";
    }

    // 2. Валідація рядка Dyck
    constexpr std::string_view seq = "((()()))";
    if (catalan::CatalanCalculator::validate_dyck_path(seq)) {
        std::cout << "Послідовність " << seq << " є валідною.\n";
    }

    // 3. Генерація послідовності
    try {
        auto table = catalan::CatalanCalculator::generate_sequence(5);
        std::cout << "Перші 6 чисел Каталана: ";
        for (auto v : table) {
            std::cout << v << " ";
        }
        std::cout << "\n";
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << "\n";
    }

    return 0;
}
```
:::
