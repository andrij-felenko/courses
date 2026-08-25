# 📋 Інтерфейс: Двозначний oracle-інтерфейс та API алгебраїчних операцій над 𝔽₂

Ця довідкова вставка містить повну специфікацію публічного програмованого інтерфейсу (API) для взаємодії з оракулом парності класу ⊕P, а також довідник низькорівневих алгебраїчних структур даних для матричних і поліноміальних обчислень над скінченним полем `𝔽₂` (GF(2)). Інтерфейс надає уніфікований контракт для виконання запитів до ⊕P-оракула, лінійного ізолювання розв'язків за лемою Валіанта–Вазірані, обчислення парності за модулем 2 та проведення Гауссового виключення над бітовими вектором-матрицями.

## Архітектурний огляд контракту ⊕P-оракула

Контракт зв'язку між клієнтською програмою поліноміального часу (яка моделює алгоритм класу `P^(⊕P)`) та оракулом парності ⊕P базується на концепції атомарних запитів типу «вхідний екземпляр формули або матриці → 1-бітна відповідь (0 або 1)».

Оракул парності приймає на вхід опис булевої формули `Φ` у кон'юнктивній нормальній формі (КНФ) або систему алгебраїчних обмежень над `𝔽₂` і повертає бітовий результат за наступним строгим правилом:
- `1` (істина) — якщо кількість приймальних гілок обчислення (або здійсненних наборів булевої формули `Φ`) є **непарною** (`N mod 2 = 1`).
- `0` (хиба) — якщо кількість приймальних гілок є **парною** чи дорівнює нулю (`N mod 2 = 0`).

На відміну від числового оракула для класу #P, який повертає повне 64-бітне або довільної точності ціле число розв'язків `N ∈ ℤ`, ⊕P-оракул повертає строго 1 біт інформації. Це створює принципову різницю в обсязі передачі даних через межу оракульного виклику: оракул парності працює як бінарний предикат зі зворотним зв'язком за модулем 2.

### Замикання відносно оракульних викликів

Клас ⊕P володіє унікальною алгебраїчною властивістю: `⊕P^(⊕P) = ⊕P`. Це означає, що машина поліноміального часу з парнісною умовою прийняття, яка робить довільну поліноміальну кількість послідовних або паралельних запитів до іншого ⊕P-оракула, не виходить за межі самого класу ⊕P.

З точки зору програмного API це означає, що виклики оракула можуть вкладатися рекурсивно або об'єднуватися в пакетні запити (batch queries) без втрати обчислювальної ефективності.

---

## Структури даних та бітові прапори

Нижче наведено основні коди повернення, константи, прапорці конфігурації та структури даних для представлення матриць над `𝔽₂` та булевих формул.

### Коди помилок та статусів (`parity_status_t`)

Кожна функція C API повертає значення типу `parity_status_t`, що дозволяє точно ідентифікувати виняткові ситуації без переривання виконання програми. У C++ використовуються строго типізовані `enum class Status`.

:::tabs
```c
typedef enum {
    PARITY_SUCCESS           =  0,  /* Запит успішно виконано */
    PARITY_ERR_NULL_POINTER  = -1,  /* Передано нульовий вказівник */
    PARITY_ERR_INVALID_VAR   = -2,  /* Некоректний індекс змінної або вихід за межі */
    PARITY_ERR_DIM_MISMATCH  = -3,  /* Невідповідність розмірностей матриць над GF(2) */
    PARITY_ERR_MEMORY        = -4,  /* Помилка виділення пам'яті */
    PARITY_ERR_TIMEOUT       = -5,  /* Перевищено встановлений ліміт часу обчислення */
    PARITY_ERR_UNSUPPORTED   = -6   /* Непідтримувана операція або формат даних */
} parity_status_t;
```
```cpp
namespace parity {
enum class Status : int32_t {
    Success          =  0,  // Запит успішно виконано
    NullPointer      = -1,  // Передано нульовий вказівник
    InvalidVariable  = -2,  // Некоректний індекс змінної або вихід за межі
    DimensionMismatch= -3,  // Невідповідність розмірностей матриць над GF(2)
    MemoryError      = -4,  // Помилка виділення пам'яті
    Timeout          = -5,  // Перевищено встановлений ліміт часу обчислення
    Unsupported      = -6   // Непідтримувана операція або формат даних
};
}
```
:::

### Прапорці конфігурації запиту (`parity_flags_t`)

Під час створення контексту оракула клієнтський код може налаштувати поведінку обчислювального двигуна за допомогою бітової маски прапорців:

:::tabs
```c
typedef enum {
    PARITY_FLAG_NONE          = 0x00, /* Стандартний запит парності */
    PARITY_FLAG_USE_GAUSS     = 0x01, /* Вмикає прискорення над GF(2) через метод Гаусса */
    PARITY_FLAG_COMP_CACHE    = 0x02, /* Вмикає кешування незалежних компонент формули */
    PARITY_FLAG_ISOLATE_VAL   = 0x04, /* Застосовує зрізи Валіанта–Вазірані для ізолювання */
    PARITY_FLAG_VERBOSE       = 0x08  /* Вивід детальної зневаджувальної інформації */
} parity_flags_t;
```
```cpp
namespace parity {
enum class Flags : uint32_t {
    None           = 0x00, // Стандартний запит парності
    UseGauss       = 0x01, // Вмикає прискорення над GF(2) через метод Гаусса
    ComponentCache = 0x02, // Вмикає кешування незалежних компонент формули
    IsolateValiant = 0x04, // Застосовує зрізи Валіанта–Вазірані для ізолювання
    Verbose        = 0x08  // Вивід детальної зневаджувальної інформації
};
}
```
:::

---

## Заголовочний інтерфейс мовами C та C++ (`parity_oracle.h` / `parity_oracle.hpp`)

Нижче наведено повні заголовочні файли мовами C та C++.

:::tabs
```c
#ifndef PARITY_ORACLE_H
#define PARITY_ORACLE_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Непрозорий тип контексту оракула парності */
typedef struct parity_oracle_ctx parity_oracle_ctx_t;

/* Структура щільної/ущільненої бітової матриці над GF(2) */
typedef struct {
    size_t rows;         /* Кількість рядків матриці */
    size_t cols;         /* Кількість стовпчиків матриці */
    size_t stride;       /* Кількість 64-бітних слів у одному рядку */
    uint64_t* data;      /* Ущільнений бітовий масив рядків матриці */
} gf2_matrix_t;

/* Структура представлення булевої формули у КНФ */
typedef struct {
    size_t num_vars;            /* Кількість зміних у формулі (1..n) */
    size_t num_clauses;         /* Кількість диз'юнктів */
    const int32_t* clause_data; /* Буфер літералів (0 розділяє диз'юнкти) */
    size_t clause_data_len;     /* Загальна довжина масиву літералів */
} parity_formula_t;

/* Створення та знищення контексту оракула парності */
parity_status_t parity_oracle_create(parity_oracle_ctx_t** ctx_out, uint32_t flags);
void parity_oracle_destroy(parity_oracle_ctx_t* ctx);

/* Атомарний запит парності кількості розв'язків формули */
parity_status_t parity_oracle_query_sat(parity_oracle_ctx_t* ctx,
                                         const parity_formula_t* formula,
                                         uint8_t* parity_out);

/* Пакетний запит парності для масиву формул (Batch Query) */
parity_status_t parity_oracle_query_batch(parity_oracle_ctx_t* ctx,
                                           const parity_formula_t* formulas,
                                           size_t count,
                                           uint8_t* parities_out);

/* Виділення та звільнення пам'яті для бітової матриці над GF(2) */
parity_status_t gf2_matrix_create(gf2_matrix_t** mat_out, size_t rows, size_t cols);
void gf2_matrix_free(gf2_matrix_t* mat);

/* Запис та зчитування окремих бітів матриці */
parity_status_t gf2_matrix_set_bit(gf2_matrix_t* mat, size_t r, size_t c, bool val);
parity_status_t gf2_matrix_get_bit(const gf2_matrix_t* mat, size_t r, size_t c, bool* val_out);

/* Обчислення рангу бітової матриці методом Гаусса над GF(2) */
parity_status_t gf2_matrix_rank(const gf2_matrix_t* mat, size_t* rank_out);

/* Моделювання зрізу Валіанта–Вазірані: додає m випадкових лінійних рівнянь над GF(2) */
parity_status_t parity_apply_valiant_vazirani(const parity_formula_t* in_formula,
                                               size_t num_linear_eqs,
                                               uint64_t seed,
                                               parity_formula_t** out_formula);

#ifdef __cplusplus
}
#endif

#endif /* PARITY_ORACLE_H */
```
```cpp
#ifndef PARITY_ORACLE_HPP
#define PARITY_ORACLE_HPP

#include <vector>
#include <cstdint>
#include <cstddef>
#include <span>
#include <memory>
#include <optional>
#include <expected>
#include <string_view>

namespace parity {

enum class Status : int32_t {
    Success          =  0,
    NullPointer      = -1,
    InvalidVariable  = -2,
    DimensionMismatch= -3,
    MemoryError      = -4,
    Timeout          = -5,
    Unsupported      = -6
};

enum class Flags : uint32_t {
    None           = 0x00,
    UseGauss       = 0x01,
    ComponentCache = 0x02,
    IsolateValiant = 0x04,
    Verbose        = 0x08
};

// ООП обгортка щільної бітової матриці над алгебраїчним полем GF(2)
class Gf2Matrix {
public:
    Gf2Matrix(size_t rows, size_t cols);
    ~Gf2Matrix() = default;

    Gf2Matrix(const Gf2Matrix&) = default;
    Gf2Matrix& operator=(const Gf2Matrix&) = default;
    Gf2Matrix(Gf2Matrix&&) noexcept = default;
    Gf2Matrix& operator=(Gf2Matrix&&) noexcept = default;

    [[nodiscard]] size_t rows() const noexcept { return rows_; }
    [[nodiscard]] size_t cols() const noexcept { return cols_; }

    void set_bit(size_t r, size_t c, bool val);
    [[nodiscard]] bool get_bit(size_t r, size_t c) const;

    // Обчислення рангу над GF(2) за поліноміальний час O(n^3)
    [[nodiscard]] size_t compute_rank() const;

private:
    size_t rows_;
    size_t cols_;
    size_t stride_;
    std::vector<uint64_t> data_;
};

// Представлення булевої формули у КНФ
class Formula {
public:
    using Literal = int32_t;
    using Clause = std::vector<Literal>;

    explicit Formula(size_t num_vars) : num_vars_(num_vars) {}

    void add_clause(std::span<const Literal> lits) {
        clauses_.emplace_back(lits.begin(), lits.end());
    }

    [[nodiscard]] size_t num_vars() const noexcept { return num_vars_; }
    [[nodiscard]] const std::vector<Clause>& clauses() const noexcept { return clauses_; }

private:
    size_t num_vars_;
    std::vector<Clause> clauses_;
};

// Обгортка оракула парності ⊕P
class ParityOracle {
public:
    explicit ParityOracle(Flags flags = Flags::None);
    ~ParityOracle();

    // Запит парності кількості розв'язків формули (повертає true = 1 / false = 0)
    [[nodiscard]] std::expected<bool, Status> query_parity(const Formula& formula) const;

    // Пакетне обчислення парності для масиву формул
    [[nodiscard]] std::expected<std::vector<bool>, Status> query_batch(
        std::span<const Formula> formulas) const;

    // Створення ізольованої формули за лемою Валіанта–Вазірані
    [[nodiscard]] static std::expected<Formula, Status> isolate_unique_solution(
        const Formula& input_formula,
        size_t num_linear_constraints,
        uint64_t seed);
};

} // namespace parity

#endif // PARITY_ORACLE_HPP
```
:::

---

## Детальний опис функцій та специфікація викликів

### 1. `parity_oracle_query_sat` / `ParityOracle::query_parity`

Виконує атомарний запит до оракула парності для обчислення значення `|SAT(Φ)| mod 2`.

- **Параметри виклику:**
  - `ctx` / `this`: Указівник на створений контекст оракула. Контекст є потокобезпечним для паралельних читальних запитів, якщо увімкнено внутрішнє кешування.
  - `formula`: Вхідна булева формула `Φ`. Двигун автоматично перевіряє цілісність масиву літералів та коректність індексів змінних у діапазоні `[1, num_vars]`.
- **Значення, що повертаються:**
  - `PARITY_SUCCESS`: Запит виконано успішно. Значення за вказівником `parity_out` містить `1` (якщо кількість розв'язків непарна) або `0` (якщо парна чи дорівнює нулю).
  - `PARITY_ERR_NULL_POINTER`: Передано `NULL` у якості одного з вказівників.
  - `PARITY_ERR_INVALID_VAR`: Знайдено літерал із виходом за межі оголошеної кількості змінних `num_vars`.
  - `PARITY_ERR_TIMEOUT`: Перевищено встановлений ліміт часу обчислення.
- **Вимоги до пам'яті:** Двигун оракула виділяє внутрішні тимчасові буфери розміром `O(num_vars + num_clauses)`. Клієнт відповідає за збереження вхідної формули протягом виклику.
- **Алгебраїчні гарантії:** Якщо формула розпадається на незалежні компоненти `Φ = A ∧ B`, оракул обчислює `Parity(A) AND Parity(B)`. Повернене значення є строго детермінованим математичним результатом.

---

### 2. `gf2_matrix_rank` / `Gf2Matrix::compute_rank`

Обчислює ранг прямокутної бітової матриці над алгебраїчним полем `𝔽₂` за допомогою прямого та зворотного ходу метод Гаусса–Жордана.

- **Алгебраїчний механізм:** Перетворює бітову матрицю до східчастої форми за допомогою порядної операції додавання за модулем 2 (`row[i] ^= row[j]`). Кількість ненульових рядків після повного зведення є оновленим рангом матриці `r`.
- **Зв'язок із парністю підпростору розв'язків:** Для однорідної системи лінійних рівнянь `A · x = 0 (mod 2)` розмір ядра (ядра відображення або підпростору розв'язків) дорівнює `2ⁿ⁻ʳ`, де `n` — кількість змінних, а `r` — ранг матриці `A`.
  - Якщо `n - r > 0` (система має вільні змінні), то кількість розв'язків `2ⁿ⁻ʳ` є **парною** (`2ⁿ⁻ʳ ≡ 0 mod 2`), тому `Parity = 0`.
  - Якщо `n - r = 0` (матриця має повний ранг `r = n`), система має єдиний тривіальний розв'язок `x = 0`, отже `Parity = 1`.
- **Оптимізація продуктивності:** Алгоритм обробляє матрицю 64-бітними словами, використовуючи апаратні інструкції SIMD/AVX2 та побітову операцію `XOR` (`^=`), що дозволяє досягати швидкості зведення до `64` бітів за один такт процесора.

---

### 3. `parity_apply_valiant_vazirani` / `ParityOracle::isolate_unique_solution`

Реалізує імовірнісне ізолювання розв'язків за лемою Валіанта–Вазірані шляхом додавання випадкових гіперплощин над `𝔽₂`.

- **Аргументи функції:**
  - `in_formula`: Початкова булева формула.
  - `num_linear_eqs`: Кількість випадкових лінійних обмежень `m`, які додаються до формули (`1 ≤ m ≤ n + 1`).
  - `seed`: Псевдовипадковий генератор зерна для коефіцієнтів лінійних рівнянь.
- **Внутрішній алгоритм:**
  1. Генерація випадкового вектор-рядка `a ∈ {0,1}ⁿ` та зсуву `b ∈ {0,1}` для кожного з `m` рівнянь.
  2. Кодуванння кожного рівняння `a₁ x₁ ⊕ a₂ x₂ ⊕ ... ⊕ a♞ x♞ = b` через рівносильний набір булевих диз'юнктів у КНФ із введенням допоміжних змінних Tseytin.
  3. Формування нової розширеної формули `Φ'`.
- **Гарантія ізолювання:** Якщо початкова формула `Φ` мала принаймні один розв'язок, існує таке `m`, що нова формула `Φ'` матиме **рівно 1 розв'язок** із імовірністю `p ≥ 1/8`.

---

## Таблиця статусів помилок та діагностики

Нижче наведено повну довідкову таблицю кодів статусів, їх причин виникнення та рекомендованих дій щодо усунення помилок у клієнтському коді.

| Код статусу | Числове значення | Причина виникнення | Рекомендована дія клієнта |
| :--- | :--- | :--- | :--- |
| `PARITY_SUCCESS` | `0` | Запит успішно виконано, біт парності обчислено | Використати результат `0` або `1` |
| `PARITY_ERR_NULL_POINTER` | `-1` | Передано `NULL` указівник у функцію C API | Перевірити ініціалізацію вказівників перед викликом |
| `PARITY_ERR_INVALID_VAR` | `-2` | Індекс змінної перевищує `num_vars` або є рівним `0` | Перевірити коректність нумерації змінних (1-indexed) |
| `PARITY_ERR_DIM_MISMATCH` | `-3` | Несумісні розмірності матриць над `𝔽₂` | Перевірити співпадіння кількості стовпців і рядків |
| `PARITY_ERR_MEMORY` | `-4` | Помилка системного виділення пам'яті `malloc` | Звільнити пам'ять `gf2_matrix_free` та повторити |
| `PARITY_ERR_TIMEOUT` | `-5` | Час обчислення парності перевищив ліміт | Увімкнути `PARITY_FLAG_USE_GAUSS` або зменшити формулу |
| `PARITY_ERR_UNSUPPORTED` | `-6` | Запитано операцію, не підтримувану прапорцями | Оновити прапорці конфігурації `parity_flags_t` |

---

## Пам'ять, потік даних та безпека ресурсів

1. **Модель керування пам'яттю (C API):**
   - Контекст `parity_oracle_ctx_t` створюється функцією `parity_oracle_create` і мусить бути явно знищений за допомогою `parity_oracle_destroy`.
   - Матриці `gf2_matrix_t` виділяються у динамічній пам'яті (купі) та звільняються викликом `gf2_matrix_free`.
   - Клієнт відповідає за виділення та очищення буфера літералів `clause_data`.
2. **Модель керування пам'яттю (C++ API):**
   - Усі ресурси керуються за принципом RAII (Resource Acquisition Is Initialization).
   - Об'єкти `Gf2Matrix` та `Formula` використовують `std::vector` для автоматичного очищення пам'яті.
   - Виняткові ситуації повертаються через тип `std::expected<T, Status>`, що виключає приховані аварійні завершення програми.
3. **Багатопотокова безпека (Thread Safety):**
   - Виклик `parity_oracle_query_sat` є повністю покільнобезпечним (thread-safe) для незалежних контекстів.
   - Спільне використання одного контексту різними потоками вимагає зовнішньої синхронізації або вмикання внутрішнього атомарного локування.

---

## Робочий приклад використання API мовами C та C++

Нижче наведено завершені робочі приклади виклику оракула парності та обчислення рангу матриці над `𝔽₂`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include "parity_oracle.h"

int main(void) {
    parity_oracle_ctx_t* ctx = NULL;
    parity_status_t st = parity_oracle_create(&ctx, PARITY_FLAG_USE_GAUSS | PARITY_FLAG_COMP_CACHE);
    if (st != PARITY_SUCCESS) {
        fprintf(stderr, "Помилка ініціалізації оракула: %d\n", st);
        return 1;
    }

    /* Задаємо булеву формулу: (x1 OR x2) AND (NOT x1 OR x3) */
    int32_t clauses[] = { 1, 2, 0,  -1, 3, 0 };
    parity_formula_t formula = {
        .num_vars = 3,
        .num_clauses = 2,
        .clause_data = clauses,
        .clause_data_len = 6
    };

    uint8_t parity = 0;
    st = parity_oracle_query_sat(ctx, &formula, &parity);
    if (st == PARITY_SUCCESS) {
        printf("Результат ⊕P оракула: %u (%s)\n",
               parity, parity ? "НЕПАРНА" : "ПАРНА");
    } else {
        printf("Помилка виконання запиту: %d\n", st);
    }

    /* Створення та перевірка рангу бітової матриці 2x2 */
    gf2_matrix_t* mat = NULL;
    if (gf2_matrix_create(&mat, 2, 2) == PARITY_SUCCESS) {
        gf2_matrix_set_bit(mat, 0, 0, true);
        gf2_matrix_set_bit(mat, 0, 1, true);
        gf2_matrix_set_bit(mat, 1, 0, false);
        gf2_matrix_set_bit(mat, 1, 1, true);

        size_t rank = 0;
        if (gf2_matrix_rank(mat, &rank) == PARITY_SUCCESS) {
            printf("Ранг матриці над GF(2): %zu\n", rank);
        }
        gf2_matrix_free(mat);
    }

    parity_oracle_destroy(ctx);
    return 0;
}
```
```cpp
#include <iostream>
#include <array>
#include "parity_oracle.hpp"

int main() {
    using namespace parity;

    // Створення оракула з використанням прискорення Гаусса
    ParityOracle oracle(Flags::UseGauss | Flags::ComponentCache);

    Formula formula(3);
    formula.add_clause(std::array<int32_t, 2>{1, 2});
    formula.add_clause(std::array<int32_t, 2>{-1, 3});

    auto parity_result = oracle.query_parity(formula);
    if (parity_result.has_value()) {
        std::cout << "⊕P Oracle parity output: " << (*parity_result ? "1 (ODD)" : "0 (EVEN)") << '\n';
    } else {
        std::cerr << "Oracle query failed with error: "
                  << static_cast<int32_t>(parity_result.error()) << '\n';
    }

    // Обчислення рангу матриці над GF(2)
    Gf2Matrix mat(2, 2);
    mat.set_bit(0, 0, true);
    mat.set_bit(0, 1, true);
    mat.set_bit(1, 0, false);
    mat.set_bit(1, 1, true);

    size_t rank = mat.compute_rank();
    std::cout << "Matrix rank over GF(2): " << rank << '\n';

    return 0;
}
```
:::

## Алгебраїчні застереження та крайові випадки API

1. **Порожні формули та суперечності:** Формула з `num_clauses = 0` вважається тавтологічно здійснюваної при всіх `2ⁿ` наборах. Її парність повертається як `0` для будь-якого `n ≥ 1`, бо `2ⁿ mod 2 = 0`. Порожній диз'юнкт (`len = 0`) є суперечністю з `0` розв'язками (`0 mod 2 = 0`).
2. **Дублювання диз'юнктів:** Повторення одного й того самого диз'юнкта не змінює множину розв'язків формули `S`, тому парність розв'язків залишається незмінною.
3. **Обчислення перманенти над `𝔽₂`:** Оскільки у полі `𝔽₂` виконується `-1 ≡ +1 (mod 2)`, визначник `det(A)` та перманента `perm(A)` тотожно збігаються. Отже, функція обчислення перманенти над `𝔽₂` реалізується за поліноміальний час `O(n³)` через `gf2_matrix_rank`, тоді як над `ℤ` задача обчислення перманенти є #P-повною.
