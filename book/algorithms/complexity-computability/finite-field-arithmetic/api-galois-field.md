# 📋 Інтерфейс та специфікація C/C++ бібліотеки для GF(2^8) та GF(2^m)

Цей документ визначає повну професійну специфікацію програмного інтерфейсу (API), структури даних, системи кодування помилок, вимоги до вирівнювання пам'яті та гарантії часової складності для системної C/C++ бібліотеки арифметики скінченних полів Галуа `GF(2ᵐ)`. Специфікація розроблена відповідно до вимог до високопродуктивних обчислювальних модулів криптографічного захисту інформації (стандарти AES, ECC) та висококритичних систем завадостійкого кодування (Reed-Solomon у дискових масивах RAID-6 та супутникових протоколах).

## 1. Загальний огляд архітектури, системи типів та контрактів

Проектне рішення бібліотеки розділено на два сумісні рівні абстракції, що задовольняють протилежним інженерним вимогам:

1. **Спеціалізований рівень `GF(2⁸)` (Фіксована 8-бітна арифметика):** Оперує безпосередньо системним типом `uint8_t`. Забезпечує гранично можливу швидкодію за рахунок табличних алгоритмів Зеха з часовою складністю `O(1)` або гарантовану стійкість до атак за часом виконання (англ. *constant-time execution*) з часовою складністю `O(m)`.
2. **Універсальний шаблонований рівень `GF(2ᵐ)` (Розрядність `1 <= m <= 64`):** Підтримує довільні нормовані незвідні многочлени над `GF(2)` та дозволяє конфігурувати параметри поля як на етапі компіляції (за допомогою `constexpr` у C++20), так і динамічно у процесі виконання (через структуру контексту `gf2m_context_t` у мові C).

### Типобезпека та гарантії пам'яті
- **Відсутність динамічного виділення пам'яті:** Усі структури даних та предобчислені таблиці використовують статичне або стекове виділення пам'яті (`std::array` у C++ або статичні масиви у C). Це робить бібліотеку придатною для використання у ядрах операційних систем (Kernel space), драйверах пристроїв та мікроконтролерах без операційної системи (Bare-metal).
- **Сумісність ABI:** Структури даних C API впорядковано за спаданням розміру полів для запобігання неявному вирівнюванню (padding) та забезпечення повної бінарної сумісності між різними компіляторами (GCC, Clang, MSVC).

### Структури даних API

:::tabs
@tab C
```c
#ifndef GF256_API_H
#define GF256_API_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/**
 * @brief Коди повернення та статусів виконання операцій API
 */
typedef enum {
    GF_SUCCESS              =  0,  /**< Операцію виконано успішно */
    GF_ERR_NULL_POINTER     = -1,  /**< Передано нульовий вказівник у критичний параметр */
    GF_ERR_DIVISION_BY_ZERO = -2,  /**< Спроба ділення на нуль або інверсії нуля */
    GF_ERR_INVALID_POLY     = -3,  /**< Заданий многочлен не є незвідним */
    GF_ERR_OUT_OF_BOUNDS    = -4,  /**< Значення параметра виходить за межі поля */
    GF_ERR_NOT_INITIALIZED  = -5   /**< Таблиці або контекст не були ініціалізовані */
} gf_status_t;

/**
 * @brief Контекст розширеного поля GF(2^m) для розрядності m <= 64
 */
typedef struct {
    uint64_t poly;           /**< Незвідний многочлен (без старшого біта x^m) */
    uint64_t field_size;     /**< Загальна кількість елементів q = 2^m */
    uint64_t poly_mask;      /**< Бітова маска нижніх m бітів (2^m - 1) */
    uint8_t  m;              /**< Степінь розширення поля (1..64) */
    bool     is_primitive;   /**< Прапор примітивності заданого полінома */
} gf2m_context_t;

/**
 * @brief Предобчислені таблиці логарифмів та експонент для GF(2^8)
 */
typedef struct {
    uint8_t exp_table[512];  /**< Таблиця експонент (продубльована для запобігання mod 255) */
    uint8_t log_table[256];  /**< Таблиця дискретних логарифмів */
    bool    initialized;     /**< Прапор готовності таблиць до роботи */
} gf256_tables_t;

#endif /* GF256_API_H */
```
@tab C++
```cpp
#ifndef GALOIS_TYPES_HPP
#define GALOIS_TYPES_HPP

#include <array>
#include <cstdint>
#include <cstddef>
#include <system_error>

namespace galois {

/**
 * @brief C++20 коди помилок у вигляді скінченного перелічення
 */
enum class ErrorCode : int {
    Success = 0,
    NullPointer = -1,
    DivisionByZero = -2,
    InvalidPolynomial = -3,
    OutOfBounds = -4,
    NotInitialized = -5
};

/**
 * @brief Метадані та атрибути поля GF(2^m)
 */
template <typename T>
struct FieldContext {
    uint64_t poly{0};
    uint64_t field_size{0};
    uint64_t poly_mask{0};
    uint8_t m{0};
    bool is_primitive{false};
};

/**
 * @brief Таблиці експонент та дискретних логарифмів
 */
template <size_t Order = 256>
struct FieldTables {
    std::array<uint8_t, Order * 2> exp_table{};
    std::array<uint8_t, Order> log_table{};
    bool initialized{false};
};

} // namespace galois

#endif // GALOIS_TYPES_HPP
```
:::

## 2. Повний специфікований каталог функцій C/C++ API

### 1. `gf256_init_tables`
Обчислює та заповнює таблиці експонент і дискретних логарифмів для поля `GF(2⁸)` за заданим незвідним многочленом та примітивним елементом.

:::tabs
@tab C
```c
gf_status_t gf256_init_tables(gf256_tables_t *tables, uint16_t irreducible_poly, uint8_t primitive_elem);
```
@tab C++
```cpp
namespace galois {
    [[nodiscard]] ErrorCode init_tables(FieldTables<256>& tables, uint16_t irreducible_poly, uint8_t primitive_elem) noexcept;
}
```
:::

- **Параметри:**
  - `tables` `[out]`: Вказівник на структуру `gf256_tables_t` / посилання `FieldTables<256>&`.
  - `irreducible_poly` `[in]`: Незвідний многочлен степеня 8 (наприклад, `0x11B` для AES).
  - `primitive_elem` `[in]`: Породжувальний елемент поля (наприклад, `0x03` для AES).
- **Предумови:** `tables != NULL`, `irreducible_poly & 0x100 != 0`.
- **Постумови:** Таблиці повністю заповнені, `initialized = true`.
- **Коди повернення:** `GF_SUCCESS` / `ErrorCode::Success`.
- **Часова складність:** `O(2^m) = O(256)` кроків ініціалізації.
- **Обсяг пам'яті:** 769 байтів у структурі.

### 2. `gf256_add` та `gf256_sub`
Обчислює суму або різницю двох елементів у полі `GF(2⁸)`.

:::tabs
@tab C
```c
uint8_t gf256_add(uint8_t a, uint8_t b);
uint8_t gf256_sub(uint8_t a, uint8_t b);
```
@tab C++
```cpp
namespace galois {
    [[nodiscard]] constexpr uint8_t add(uint8_t a, uint8_t b) noexcept { return a ^ b; }
    [[nodiscard]] constexpr uint8_t subtract(uint8_t a, uint8_t b) noexcept { return a ^ b; }
}
```
:::

- **Параметри:** `a`, `b` — вхідні елементи поля `GF(2⁸)`.
- **Повертане значення:** Результат `a ^ b`.
- **Часова складність:** `O(1)` (одна побітова інструкція XOR).
- **Гарантія безпеки:** Завжди виконується за строго константний час незалежно від операндів.

### 3. `gf256_mul_fast`
Виконує швидке множення двох елементів у полі `GF(2⁸)` з використанням предобчислених таблиць Зеха.

:::tabs
@tab C
```c
uint8_t gf256_mul_fast(const gf256_tables_t *tables, uint8_t a, uint8_t b);
```
@tab C++
```cpp
namespace galois {
    [[nodiscard]] uint8_t multiply_fast(const FieldTables<256>& tables, uint8_t a, uint8_t b) noexcept;
}
```
:::

- **Параметри:** `tables` `[in]`, `a`, `b` `[in]`.
- **Предумови:** `tables->initialized == true`.
- **Повертане значення:** Добуток `(a · b) mod f(x)`. Якщо `a == 0` або `b == 0`, повертає `0`.
- **Часова складність:** `O(1)` (2 читання з масиву + 1 додавання).
- **Зауваження з безпеки:** Використовує табличний доступ за адресою, що залежить від даних. Не рекомендується для секретних криптографічних ключів через ризик атак по кєш-лініях (Cache-timing attacks).

### 4. `gf256_mul_ct` (Constant-Time Multiplication)
Виконує множення двох елементів без використання таблиць пам'яті і без умовних розгалужень для захисту від атак по побічних каналах.

:::tabs
@tab C
```c
uint8_t gf256_mul_ct(uint8_t a, uint8_t b, uint16_t poly) {
    uint8_t res = 0;
    for (int i = 0; i < 8; i++) {
        uint8_t mask = (uint8_t)(-(b & 1));
        res ^= (a & mask);
        uint8_t carry = (uint8_t)(-(a >> 7));
        a = (a << 1) ^ ((poly & 0xFF) & carry);
        b >>= 1;
    }
    return res;
}
```
@tab C++
```cpp
namespace galois {
    [[nodiscard]] constexpr uint8_t multiply_constant_time(uint8_t a, uint8_t b, uint16_t poly) noexcept {
        uint8_t res = 0;
        for (int i = 0; i < 8; ++i) {
            uint8_t mask = static_cast<uint8_t>(0) - (b & 1);
            res ^= (a & mask);
            uint8_t carry = static_cast<uint8_t>(0) - ((a >> 7) & 1);
            a = static_cast<uint8_t>(a << 1) ^ ((poly & 0xFF) & carry);
            b >>= 1;
        }
        return res;
    }
}
```
:::

- **Часова складність:** `O(m)` = 8 фіксованих ітерацій.
- **Гарантія безпеки:** Строго константний час виконання (Constant-time guarantee).

### 5. `gf256_inv_eea`
Обчислює мультиплікативно обернений елемент `a⁻¹` через Розширений алгоритм Евкліда.

:::tabs
@tab C
```c
gf_status_t gf256_inv_eea(uint8_t a, uint16_t poly, uint8_t *out_inv);
```
@tab C++
```cpp
namespace galois {
    [[nodiscard]] std::optional<uint8_t> inverse_eea(uint8_t a, uint16_t poly) noexcept;
}
```
:::

- **Параметри:** `a` `[in]`, `poly` `[in]`, `out_inv` `[out]`.
- **Коди повернення:** `GF_SUCCESS` / `std::optional<uint8_t>`.
- **Часова складність:** `O(m^2)` бітових операцій.

## 3. Специфікація C++20 шаблонованого API

C++20 інтерфейс забезпечує максимальну продуктивність завдяки використанню `constexpr` обчислень на етапі компіляції.

:::tabs
@tab C
```c
/* Базовий контекстний підхід у мові C */
typedef struct {
    uint8_t (*add)(uint8_t, uint8_t);
    uint8_t (*mul)(uint8_t, uint8_t);
    uint8_t (*inv)(uint8_t);
} gf256_ops_t;
```
@tab C++
```cpp
#ifndef GALOIS_FIELD_HPP
#define GALOIS_FIELD_HPP

#include <array>
#include <cstdint>
#include <optional>
#include <type_traits>
#include <concepts>

namespace galois {

template <typename T>
concept UnsignedInteger = std::is_unsigned_v<T> && !std::is_same_v<T, bool>;

template <UnsignedInteger T, size_t m, T IrreduciblePolynomial>
class Field {
public:
    static_assert(m > 0 && m <= sizeof(T) * 8, "Степінь m повинна відповідати розміру типу T");

    using value_type = T;

    constexpr Field() noexcept = default;

    [[nodiscard]] constexpr T add(T a, T b) const noexcept {
        return a ^ b;
    }

    [[nodiscard]] constexpr T subtract(T a, T b) const noexcept {
        return a ^ b;
    }

    [[nodiscard]] constexpr T multiply_constant_time(T a, T b) const noexcept {
        T res = 0;
        T cur_a = a;
        T cur_b = b;
        const T poly_lower = IrreduciblePolynomial & ((static_cast<T>(1) << m) - 1);

        for (size_t i = 0; i < m; ++i) {
            T mask = static_cast<T>(0) - (cur_b & 1);
            res ^= (cur_a & mask);
            T carry = static_cast<T>(0) - ((cur_a >> (m - 1)) & 1);
            cur_a = static_cast<T>(cur_a << 1) ^ (poly_lower & carry);
            cur_b = static_cast<T>(cur_b >> 1);
        }
        return res;
    }

    [[nodiscard]] constexpr std::optional<T> inverse_fermat(T a) const noexcept {
        if (a == 0) return std::nullopt;
        T result = 1;
        T base = a;
        uint64_t exponent = (1ULL << m) - 2;

        while (exponent > 0) {
            if (exponent & 1) {
                result = multiply_constant_time(result, base);
            }
            base = multiply_constant_time(base, base);
            exponent >>= 1;
        }
        return result;
    }
};

using GF256_AES = Field<uint8_t, 8, 0x11B>;
using GF64_CRCPOLY = Field<uint64_t, 64, 0x1BULL>;

} // namespace galois

#endif // GALOIS_FIELD_HPP
```
:::

## 4. Зведена таблиця часової та просторової складності операцій

Нижче наведено порівняльний аналіз усіх методів реалізації арифметики полів Галуа за часовою та просторовою складністю, а також за ступенем криптографічної захищеності від побічних каналів:

| Операція | Метод алгоритму | Часова складність | Просторова складність | Захист від атак по побічних каналах (Constant-Time) |
| :--- | :--- | :--- | :--- | :--- |
| **Додавання / Віднімання** | Побітовий XOR | `O(1)` (1 інструкція) | `O(1)` (0 bytes) | **Так** (абсолютний захист) |
| **Множення GF(2⁸)** | Таблиці Зеха (Log/Exp) | `O(1)` (3 такти) | `O(2^m)` (768 bytes) | **Ні** (витік через кєш-лінії при вибірці з масиву) |
| **Множення GF(2⁸)** | Зсув-і-складання (Маска) | `O(m)` (8 кроків) | `O(1)` (0 bytes) | **Так** (при використанні бітової маски) |
| **Множення GF(2ᵐ)** | Інструкція PCLMULQDQ | `O(1)` (апаратна) | `O(1)` (0 bytes) | **Так** (забезпечується процесором) |
| **Інверсія GF(2⁸)** | Таблиця S-Box | `O(1)` (1 вибірка) | `O(256)` bytes | **Ні** (витік через кєш-пам'ять) |
| **Інверсія GF(2ᵐ)** | Розширений Евклід | `O(m^2)` біт-операцій | `O(1)` (скаляри) | **Ні** (кількість кроків залежить від значень) |
| **Інверсія GF(2ᵐ)** | Алгоритм Іто — Цуджії | `O(log m)` множень | `O(m)` бітів | **Так** (при константній реалізації множення) |
| **Інверсія GF(2ᵐ)** | Мала теорема Ферма | `O(m)` множень | `O(1)` | **Так** (константна кількість кроків) |

## 5. Гарантії потокобезпечності, обробки помилок та ABI

Для забезпечення високої надійності у промислових криптопроцесорних системах специфікація розробка встановлює строгі правила поведінки інтерфейсу при виникненні нештатних ситуацій, паралельному доступі та лінкуванні бінарних модулів.

### 1. Модель потокобезпечності (Thread-Safety Model)
- **Чисті функції (Reentrant & Pure Functions):** Операції `gf256_add`, `gf256_sub`, `gf256_mul_ct` та метод класу `galois::Field::multiply_constant_time` є чистими функціями. Вони оперують виключно значеннями, переданими через стек, не читають і не модифікують глобальні або статичні змінні процесу. Вони є повністю потокобезпечними і не вимагають м'ютексів чи атоміків.
- **Розділюваний доступ до таблиць Зеха:** Структура `gf256_tables_t` після завершення виклику `gf256_init_tables` є незмінною (read-only). Паралельні потоки можуть одночасно читати з неї без будь-якої синхронізації. Повторний виклик ініціалізації під час роботи інших потоків заборонено.

### 2. Деталізація кодів помилок та виняткових ситуацій
- `GF_ERR_NULL_POINTER`: Повертається функціями `gf256_init_tables`, `gf256_mul_fast` та `gf256_inv_eea`, якщо передано вказівник `NULL`.
- `GF_ERR_DIVISION_BY_ZERO`: Виникає при спробі обчислити обернений елемент для нуля `0⁻¹` у функції `gf256_inv_eea`. У C++20 інтерфейсі ця ситуація обробляється поверненням порожнього об'єкта `std::nullopt` без генерування винятків (exception-free `noexcept` контракт).
- `GF_ERR_INVALID_POLY`: Повертається, якщо переданий многочлен `irreducible_poly` не має старшого біта `x^m` або є звідним.

### 3. Бінарна сумісність (ABI) та специфікація гарантій компілятора
- **Гарантія noexcept:** Усі функції C++20 класу `galois::Field` позначено специфікатором `noexcept`. Компілятор гарантує відсутність накладних витрат на обробку таблиць винятків (zero-overhead exception model).
- **Вирівнювання структур:** Структура `gf2m_context_t` має вирівнювання 8 байтів (64 біти) для оптимізації шини даних нових 64-бітних процесорів RISC-V, ARM64 та x86-64.
