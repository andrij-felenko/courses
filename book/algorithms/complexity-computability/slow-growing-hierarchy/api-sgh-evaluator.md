# 📋 Специфікація програмного інтерфейсу SGH Engine

Бібліотека `SGH Engine` надає універсальний програмний інтерфейс для представлення, маніпуляції, синтаксичного розбору та обчислення повільнозростаючої ієрархії `G_α(n)` на множині зліченних трансфінітних ординалів Кантора, Веблена та систем ординального колапсу.

Цей документ містить вичерпний довідник типів даних, функцій мови C, об'єктно-орієнтованих класів C++20, специфікацію кодів помилок, інваріантів пам'яті, гарантій часової складності та правил інтеграції у сторонні програмні комплекси.

## Загальні конвенції та архітектурна модель

Бібліотека поширюється у вигляді двох взаємоузгоджених заголовних інтерфейсів, які реалізують єдину концептуальну модель трансфінітних обчислень:
- `sgh_engine.h` — низькорівневий процедурний інтерфейс мовою C (стандарт C99/C11), орієнтований на максимальну швидкодію, вбудовані системи та створення біндінгів до інших мов програмування (Rust, Python, Java, C# через механізм Foreign Function Interface, FFI).
- `sgh_engine.hpp` — високорівневий об'єктно-орієнтований інтерфейс мовою C++ (стандарт C++20), побудований на використанні семантики володіння розумними вказівниками `std::unique_ptr`, стандартних контейнерів, типізованих винятків та концептів.

Усі числові аргументи, рівні ієрархії та повертані значення використовують 64-бітні беззнакові цілі числа `uint64_t` (`uint64_t` у C, `std::uint64_t` у C++), що забезпечує однакову розрядність на всіх цільових апаратних платформах.

### Дисципліна володіння пам'яттю та контракти життєвого циклу

Під час проєктування програмного інтерфейсу для обчислення трансфінітних ієрархій ключовим викликом є запобігання витокам пам'яті під час генерації проміжних дерев редукції. Оскільки крок наближення фундаментальної послідовності `λ ↦ λ[n]` будує нове піддерево на кожному виклику, неконтрольоване копіювання може швидко виснажити системні ресурси.

Дисципліна володіння пам'яттю в `SGH Engine` базується на трьох чітких правилах:
1. **Правило поглинання власності (Sink Rule):** будь-яка функція-конструктор або метод додавання, що приймає вказівник на дочірній вузол, безповоротно забирає його у своє виключне володіння. Викликаюча сторона втрачає право самостійно вивільняти переданий вузол.
2. **Єдиний деструктор (Root Ownership):** користувач зобов'язаний вивільняти пам'ять лише для кореневого вузла дерева за допомогою функції `ord_free()`. Вся структура піддерева обходиться та звільняється рекурсивно за один прохід.
3. **Незмінність під час обчислень (Immutability Guarantee):** функції обчислення `sgh_eval_homomorphism` та метод `evaluate()` є чистими функціями (англ. *pure functions*) з погляду пам'яті — вони приймають константні посилання, не виділяють динамічної пам'яті в купі та не змінюють стан переданого синтаксичного дерева.

### Інтеграція в системи автоматичного доведення теорем

Інтерфейс бібліотеки спроєктовано спеціально для інтеграції у сучасні інтерактивні середовища формальних доведень (англ. *Interactive Theorem Provers*, ITP), такі як Lean 4, Coq, Agda та Isabelle/HOL:
- **Експорт сертифікатів завершуваності:** після обчислення значення `G_α(n)` двигун формує компактний слід виконання (англ. *execution trace*), який може бути верифікований зовнішнім ядром доведень.
- **Гарантія повноти та детермінізму:** алгоритм синтаксичного розбору та редукції є строго детермінованим і не використовує глобальних змінних стану, що робить його придатним для паралельного виконання у багатопотокових конвеєрах верифікації.

## Публічні типи даних та структури

Основою інтерфейсу є структури абстрактного синтаксичного дерева ординальних чисел, коди статусів виконання та метрики обчислювальних ресурсів.

### Коди повернення та статусні типи

Для сигналізації про успішність або тип помилки функції бібліотеки повертають значення типу `SghStatus` у C або генерують типізовані винятки у C++:

:::tabs
```c
typedef enum {
    SGH_OK = 0,                    /* Успішне виконання операції */
    SGH_ERR_NULL_PTR = 1,          /* Передано неприпустимий нульовий покажчик */
    SGH_ERR_OVERFLOW = 2,          /* Арифметичне переповнення 64-бітного цілого числа */
    SGH_ERR_INVALID_ORDINAL = 3,   /* Порушення інваріанту спадання форми Кантора */
    SGH_ERR_OUT_OF_MEMORY = 4,     /* Помилка виділення динамічної пам'яті в купі */
    SGH_ERR_PARSE_SYNTAX = 5,      /* Синтаксична помилка при розборі вхідного рядка */
    SGH_ERR_NOT_A_LIMIT = 6        /* Спроба взяти фундаментальну послідовність від наступника */
} SghStatus;
```
```cpp
namespace sgh {
enum class Status : uint32_t {
    Ok = 0,
    NullPtr = 1,
    Overflow = 2,
    InvalidOrdinal = 3,
    OutOfMemory = 4,
    ParseSyntax = 5,
    NotALimit = 6
};
}
```
:::

### Типи категорій вузлів `OrdinalKind`

Кожен вузол синтаксичного дерева належить до однієї з чотирьох фундаментальних категорій ординальної граматики:

:::tabs
```c
typedef enum {
    ORD_CONST = 0,        /* Скінченна константа c in N_0 */
    ORD_OMEGA_TERM = 1,   /* Моном виду w^beta * c */
    ORD_SUM = 2,          /* Нормалізована сума Кантора */
    ORD_COLLAPSE = 3      /* Колапсувальний вузол psi(beta) */
} OrdinalKind;
```
```cpp
namespace sgh {
enum class OrdinalKind : uint8_t {
    Const = 0,
    OmegaTerm = 1,
    Sum = 2,
    Collapse = 3
};
}
```
:::

### Структура вузла абстрактного синтаксичного дерева

Синтаксичний вузол оптимізований за розміром для забезпечення високої просторової локальності в кеш-пам'яті сучасних процесорів:

:::tabs
```c
typedef struct OrdinalNode OrdinalNode;

struct OrdinalNode {
    OrdinalKind kind;
    union {
        uint64_t constant;
        struct {
            OrdinalNode *exponent;
            uint64_t coefficient;
        } omega_term;
        struct {
            OrdinalNode **terms;
            size_t count;
            size_t capacity;
        } sum;
        struct {
            OrdinalNode *inner;
        } collapse;
    } as;
};
```
```cpp
namespace sgh {
class OrdinalNode {
public:
    virtual ~OrdinalNode() = default;
    [[nodiscard]] virtual uint64_t evaluate(uint64_t n) const = 0;
    [[nodiscard]] virtual std::string to_string() const = 0;
    [[nodiscard]] virtual std::unique_ptr<OrdinalNode> clone() const = 0;
    [[nodiscard]] virtual std::unique_ptr<OrdinalNode> fundamental_step(uint64_t n) const = 0;
    [[nodiscard]] virtual bool is_zero() const noexcept { return false; }
    [[nodiscard]] virtual bool is_successor() const noexcept { return false; }
    [[nodiscard]] virtual bool is_limit() const noexcept { return false; }
};
using OrdinalPtr = std::unique_ptr<OrdinalNode>;
}
```
:::

| Поле структури | Тип | Опис та інваріанти |
| :--- | :--- | :--- |
| `kind` | `OrdinalKind` | Дискримінатор типу вузла. Визначає активне поле в об'єднанні `as`. |
| `as.constant` | `uint64_t` | Числове значення скінченного ординала (`0, 1, 2, ...`). |
| `as.omega_term.exponent` | `OrdinalNode*` | Вказівник на піддерево показника степеня `β`. Не може бути `NULL`. |
| `as.omega_term.coefficient` | `uint64_t` | Додатний коефіцієнт множення `c ≥ 1`. |
| `as.sum.terms` | `OrdinalNode**` | Динамічний масив вказівників на мономи, упорядковані за спаданням степенів. |
| `as.sum.count` | `size_t` | Поточна кількість доданків у сумі. |
| `as.sum.capacity` | `size_t` | Загальна виділена місткість динамічного масиву доданків. |
| `as.collapse.inner` | `OrdinalNode*` | Вказівник на внутрішній ординальний вираз під оператором колапсу `ψ`. |

## Детальна специфікація функцій C API

Публічний процедурний C-інтерфейс бібліотеки розділено на чотири логічні групи: конструктори вузлів, деструктори, процедури обчислення та функції синтаксичного аналізу.

### 1. Функція `ord_create_const`
- **Сигнатура:** `OrdinalNode *ord_create_const(uint64_t val);`
- **Призначення:** Створює новий термінальний вузол скінченного ординала.
- **Параметри:** `val` — натуральне число (`0` представляє порожній нульовий ординал).
- **Повертане значення:** Вказівник на новостворений вузол або `NULL` при вичерпанні пам'яті в купі.
- **Передмови:** Немає.
- **Післяумови:** Створено ізольований вузол з типом `ORD_CONST`.
- **Складність:** `O(1)` за часом та пам'яттю.

### 2. Функція `ord_create_omega_term`
- **Сигнатура:** `OrdinalNode *ord_create_omega_term(OrdinalNode *exponent, uint64_t coeff);`
- **Призначення:** Створює моном Кантора вигляду `ω^exponent · coeff`.
- **Параметри:**
  - `exponent` — вказівник на піддерево показника (переходить у виключну власність нового вузла). Не повинен бути `NULL`.
  - `coeff` — додатний цілочисельний коефіцієнт (`coeff ≥ 1`).
- **Повертане значення:** Вказівник на новий вузол або `NULL` при помилці виділення пам'яті.
- **Передмови:** `exponent != NULL`, `coeff > 0`.
- **Складність:** `O(1)`.

### 3. Функція `ord_create_sum`
- **Сигнатура:** `OrdinalNode *ord_create_sum(void);`
- **Призначення:** Ініціалізує порожній динамічний контейнер суми Кантора.
- **Повертане значення:** Вказівник на порожній вузол суми з початковою місткістю 4 елементи.
- **Складність:** `O(1)`.

### 4. Процедура `ord_sum_append`
- **Сигнатура:** `void ord_sum_append(OrdinalNode *sum_node, OrdinalNode *term);`
- **Призначення:** Додає новий доданок до суми Кантора з автоматичним геометричним розширенням буфера.
- **Параметри:**
  - `sum_node` — вузол типу `ORD_SUM`.
  - `term` — вказівник на доданок, що додається (переходить у власність суми).
- **Складність:** Амортизована `O(1)`.

### 5. Функція `ord_create_collapse`
- **Сигнатура:** `OrdinalNode *ord_create_collapse(OrdinalNode *inner);`
- **Призначення:** Створює вузол колапсу незліченного кардинала `ψ(inner)` для моделювання виходу на ординал Бахмана — Говарда.
- **Параметри:** `inner` — вказівник на внутрішній ординальний вираз.
- **Повертане значення:** Вказівник на вузол колапсу.
- **Складність:** `O(1)`.

### 6. Процедура `ord_free`
- **Сигнатура:** `void ord_free(OrdinalNode *node);`
- **Призначення:** Рекурсивно вивільняє всю динамічну пам'ять, зайняту піддеревом ординала.
- **Параметри:** `node` — корінь дерева. Безпечно приймає `NULL` (операція no-op).
- **Складність:** `O(|α|)` за часом, `O(depth(α))` за пам'яттю викликів.

### 7. Функція `ord_clone`
- **Сигнатура:** `OrdinalNode *ord_clone(const OrdinalNode *node);`
- **Призначення:** Створює повну незалежну глибоку копію (англ. *deep copy*) всього ординального дерева.
- **Параметри:** `node` — корінь дерева для копіювання.
- **Повертане значення:** Новий незалежний екземпляр дерева або `NULL` при помилці виділення пам'яті.
- **Складність:** `O(|α|)`.

### 8. Функція `ord_compare`
- **Сигнатура:** `int ord_compare(const OrdinalNode *a, const OrdinalNode *b);`
- **Призначення:** Порівнює два ординали за канонічним трансфінітним порядком.
- **Повертане значення:** Від'ємне значення, якщо `a < b`; `0`, якщо `a == b`; додатне значення, якщо `a > b`.
- **Складність:** `O(min(|a|, |b|))`.

### 9. Функція `sgh_eval_homomorphism`
- **Сигнатура:** `uint64_t sgh_eval_homomorphism(const OrdinalNode *node, uint64_t n);`
- **Призначення:** Обчислює точне значення функції повільнозростаючої ієрархії `G_α(n)` за теоремою про алгебраїчний гомоморфізм `ω ↦ n`.
- **Параметри:**
  - `node` — корінь ординального дерева Кантора.
  - `n` — числовий аргумент (`n ≥ 1`).
- **Повертане значення:** 64-бітне беззнакове ціле число результату.
- **Помилки:** При арифметичному переповненні повертає константу `UINT64_MAX`.
- **Складність:** `O(|α| · log(E))`, де `E` — максимальний показник степеня у виразі.

### 10. Функція `sgh_fundamental_step`
- **Сигнатура:** `SghStatus sgh_fundamental_step(const OrdinalNode *node, uint64_t n, OrdinalNode **out_reduced);`
- **Призначення:** Виконує один крок редукції граничного ординала за канонічною фундаментальною послідовністю: `λ ↦ λ[n]`.
- **Параметри:**
  - `node` — вихідний граничний ординал.
  - `n` — числовий індекс наближення фундаментальної послідовності.
  - `out_reduced` — вихідний вказівник, куди записується адреса нового редукованого ординала.
- **Повертане значення:** Статус операції `SGH_OK` або код помилки `SGH_ERR_NOT_A_LIMIT`.
- **Складність:** `O(depth(α))`.

### 11. Функція `sgh_parse_string`
- **Сигнатура:** `SghStatus sgh_parse_string(const char *str, OrdinalNode **out_node);`
- **Призначення:** Здійснює синтаксичний розбір текстового рядка у нормальній формі Кантора.
- **Параметри:**
  - `str` — нуль-термінований рядок з виразом (наприклад, `"w^3 * 2 + w^2 * 5 + 7"`).
  - `out_node` — вказівник для запису результату.
- **Повертане значення:** `SGH_OK` або `SGH_ERR_PARSE_SYNTAX`.
- **Складність:** `O(N)`, де `N` — довжина вхідного рядка.

## Детальний довідник C++ API (`sgh_engine.hpp`)

Усі класи та допоміжні функції бібліотеки C++20 інкапсульовані у простір імен `namespace sgh`.

### Клас `sgh::ConstantNode`
Представляє скінченний термінальний ординал `c ∈ ℕ₀`.
- **Конструктор:** `explicit ConstantNode(uint64_t val) noexcept;`
- **Методи:**
  - `uint64_t evaluate(uint64_t n) const noexcept override;` — повертає числове значення `val`.
  - `std::string to_string() const override;` — повертає рядковий запис числа.
  - `OrdinalPtr clone() const override;` — створює незалежний дублікат вузла.
  - `OrdinalPtr fundamental_step(uint64_t n) const override;` — для `val > 0` повертає `ConstantNode(val - 1)`.
  - `bool is_zero() const noexcept override;` — повертає `true`, якщо `val == 0`.
  - `bool is_successor() const noexcept override;` — повертає `true`, якщо `val > 0`.

### Клас `sgh::OmegaTermNode`
Представляє моном вигляду `ω^exponent · coefficient`.
- **Конструктор:** `OmegaTermNode(OrdinalPtr exp, uint64_t coeff = 1);`
  - *Винятки:* Генерує `std::invalid_argument`, якщо `exp == nullptr` або `coeff == 0`.
- **Методи:**
  - `uint64_t evaluate(uint64_t n) const override;` — обчислює `n^(exp->evaluate(n)) * coeff`.
  - `std::string to_string() const override;` — форматує вираз як `"w^(...) * c"`.
  - `OrdinalPtr clone() const override;` — рекурсивно дублює моном.
  - `OrdinalPtr fundamental_step(uint64_t n) const override;` — виконує редукцію `(ω^β · c)[n]`.
  - `const OrdinalNode& exponent() const noexcept;` — повертає константне посилання на показник.
  - `uint64_t coefficient() const noexcept;` — повертає числовий коефіцієнт.

### Клас `sgh::SumNode`
Представляє спадну суму Кантора `∑ ω^(βᵢ) · cᵢ`.
- **Конструктор:** `SumNode() = default;`
- **Методи:**
  - `void add_term(OrdinalPtr term);` — додає новий доданок із перевіркою валідності.
  - `uint64_t evaluate(uint64_t n) const override;` — підсумовує результати обчислення всіх доданків.
  - `std::string to_string() const override;` — форматує суму через знак `+`.
  - `OrdinalPtr clone() const override;` — створює глибоку копію всієї суми.
  - `OrdinalPtr fundamental_step(uint64_t n) const override;` — редукує наймолодший доданок суми.
  - `size_t size() const noexcept;` — повертає кількість доданків.
  - `const OrdinalNode& operator[](size_t idx) const;` — забезпечує індексований доступ до доданків.

### Клас `sgh::CollapseNode`
Представляє колапс незліченного ординала `ψ(inner)`.
- **Конструктор:** `explicit CollapseNode(OrdinalPtr inner);`
- **Методи:**
  - `uint64_t evaluate(uint64_t n) const override;` — моделює дію колапсу через вкладену ітерацію.
  - `std::string to_string() const override;` — повертає `"psi(...)"`.
  - `OrdinalPtr clone() const override;` — створює дублікат колапсованого вузла.
  - `OrdinalPtr fundamental_step(uint64_t n) const override;` — виконує заміну `Ω ↦ n`.

### Клас синтаксичного аналізатора `sgh::OrdinalParser`
- **Метод:** `[[nodiscard]] static OrdinalPtr parse(std::string_view expression);`
- **Призначення:** Транслює текстовий вираз ординала у дерево AST.
- **Підтримуваний синтаксис:** `"0"`, `"7"`, `"w"`, `"w^2 * 3 + w + 5"`, `"w^(w+1)"`, `"psi(w^2)"`.
- **Винятки:** Генерує `sgh::ParseException` із зазначенням точної позиції помилки у рядку при некоректному синтаксисі.

## Ієрархія винятків C++

Бібліотека використовує типізовані класи винятків, похідні від `std::runtime_error`:

:::tabs
```cpp
namespace sgh {

class OrdinalException : public std::runtime_error {
    using std::runtime_error::runtime_error;
};

class OverflowException final : public OrdinalException {
public:
    OverflowException() : OrdinalException("Arithmetic integer overflow in SGH evaluation") {}
};

class ParseException final : public OrdinalException {
private:
    size_t position_;
public:
    ParseException(const std::string& msg, size_t pos)
        : OrdinalException(msg + " at position " + std::to_string(pos)), position_(pos) {}
    [[nodiscard]] size_t position() const noexcept { return position_; }
};

class InvalidOrdinalException final : public OrdinalException {
public:
    explicit InvalidOrdinalException(const std::string& msg) : OrdinalException(msg) {}
};

}
```
```c
/* У C API помилки обробляються через повернення кодів SghStatus */
const char *sgh_status_to_string(SghStatus status) {
    switch (status) {
        case SGH_OK: return "OK";
        case SGH_ERR_NULL_PTR: return "Null pointer argument";
        case SGH_ERR_OVERFLOW: return "Arithmetic integer overflow";
        case SGH_ERR_INVALID_ORDINAL: return "Invalid Cantor normal form";
        case SGH_ERR_OUT_OF_MEMORY: return "Out of memory";
        case SGH_ERR_PARSE_SYNTAX: return "Syntax parsing error";
        case SGH_ERR_NOT_A_LIMIT: return "Not a limit ordinal";
        default: return "Unknown error";
    }
}
```
:::

## Приклади інтеграції та типові сценарії використання

### Сценарій 1: Повний життєвий цикл C API

Нижче наведено приклад правильного створення, обчислення та безпечного звільнення ординала Кантора `α = ω² · 3 + ω · 4 + 5`:

:::tabs
```c
#include "sgh_engine.h"
#include <stdio.h>
#include <inttypes.h>

void run_c_example(void) {
    /* 1. Створення доданків */
    OrdinalNode *term1 = ord_create_omega_term(ord_create_const(2), 3); /* w^2 * 3 */
    OrdinalNode *term2 = ord_create_omega_term(ord_create_const(1), 4); /* w^1 * 4 */
    OrdinalNode *term3 = ord_create_const(5);                           /* 5 */

    /* 2. Агрегація в суму Кантора */
    OrdinalNode *sum = ord_create_sum();
    ord_sum_append(sum, term1);
    ord_sum_append(sum, term2);
    ord_sum_append(sum, term3);

    /* 3. Обчислення значення G_alpha(n) для n = 4 */
    uint64_t n = 4;
    uint64_t result = sgh_eval_homomorphism(sum, n);
    printf("G_alpha(%" PRIu64 ") = %" PRIu64 "\n", n, result);
    /* Очікуваний результат: 4^2 * 3 + 4 * 4 + 5 = 16 * 3 + 16 + 5 = 48 + 16 + 5 = 69 */

    /* 4. Вивільнення пам'яті всього дерева */
    ord_free(sum);
}
```
```cpp
#include "sgh_engine.hpp"
#include <iostream>

void run_cpp_example() {
    auto sum = std::make_unique<sgh::SumNode>();
    sum->add_term(std::make_unique<sgh::OmegaTermNode>(std::make_unique<sgh::ConstantNode>(2), 3));
    sum->add_term(std::make_unique<sgh::OmegaTermNode>(std::make_unique<sgh::ConstantNode>(1), 4));
    sum->add_term(std::make_unique<sgh::ConstantNode>(5));

    constexpr uint64_t n = 4;
    const uint64_t result = sum->evaluate(n);
    std::cout << "G_alpha(" << n << ") = " << result << "\n";
}
```
:::

### Сценарій 2: Ідіоматичне використання C++20 API з парсером та обробкою винятків

:::tabs
```cpp
#include "sgh_engine.hpp"
#include <iostream>

void run_cpp_parser_example() {
    try {
        std::string expr = "w^3 * 2 + w^2 * 5 + 7";
        auto ordinal = sgh::OrdinalParser::parse(expr);

        constexpr uint64_t n = 3;
        uint64_t value = ordinal->evaluate(n);

        std::cout << "Вираз: " << ordinal->to_string() << "\n";
        std::cout << "G_alpha(" << n << ") = " << value << "\n";

        auto next_step = ordinal->fundamental_step(n);
        std::cout << "Після редукції [3]: " << next_step->to_string() << "\n";

    } catch (const sgh::ParseException& e) {
        std::cerr << "Синтаксична помилка: " << e.what() << " на позиції " << e.position() << "\n";
    } catch (const sgh::OverflowException& e) {
        std::cerr << "Арифметичне переповнення: " << e.what() << "\n";
    } catch (const std::exception& e) {
        std::cerr << "Стандартний виняток: " << e.what() << "\n";
    }
}
```
```c
#include "sgh_engine.h"
#include <stdio.h>

void run_c_parser_example(void) {
    OrdinalNode *node = NULL;
    SghStatus st = sgh_parse_string("w^3 * 2 + w^2 * 5 + 7", &node);
    if (st != SGH_OK) {
        fprintf(stderr, "Помилка парсингу: %d\n", st);
        return;
    }
    uint64_t val = sgh_eval_homomorphism(node, 3);
    printf("Обчислено у C: %lu\n", (unsigned long)val);
    ord_free(node);
}
```
:::

## Зведена матриця часової та просторової складності

Нижче наведено вичерпну таблицю обчислювальної складності всіх відкритих функцій інтерфейсу:

| Функція / Метод | Часова складність (найкраща) | Часова складність (найгірша) | Просторова складність (стек) | Виділення купи |
| :--- | :--- | :--- | :--- | :--- |
| `ord_create_const` | `O(1)` | `O(1)` | `O(1)` | 32 байти |
| `ord_create_omega_term` | `O(1)` | `O(1)` | `O(1)` | 32 байти |
| `ord_create_sum` | `O(1)` | `O(1)` | `O(1)` | 64 байти |
| `ord_sum_append` | `O(1)` | `O(M)` (реалокація) | `O(1)` | Амортизоване |
| `ord_free` | `O(1)` (для константи) | `O(|α|)` | `O(depth(α))` | 0 (звільнення) |
| `ord_clone` | `O(|α|)` | `O(|α|)` | `O(depth(α))` | `O(|α|)` байти |
| `ord_compare` | `O(1)` | `O(min(\|a\|, \|b\|))` | `O(min(d(a), d(b)))` | 0 |
| `sgh_eval_homomorphism` | `O(1)` | `O(|α| · log(max_exp))` | `O(depth(α))` | 0 |
| `sgh_fundamental_step` | `O(1)` | `O(depth(α))` | `O(depth(α))` | `O(depth(α))` |
| `sgh_parse_string` | `O(N)` | `O(N)` | `O(depth(α))` | `O(|α|)` |

## Порівняльний аналіз підходів: C API проти C++20 API

При виборі між використанням `sgh_engine.h` та `sgh_engine.hpp` розробникам слід враховувати такі архітектурні та продуктивні компроміси:

1. **Продуктивність та накладні витрати (Zero-Cost Abstractions):**
Низькорівневий інтерфейс мовою C не використовує динамічного зв'язування чи віртуальних таблиць (vtable), що забезпечує прямий виклик функцій та максимальні можливості для агресивного інлайнінгу компілятором. У C++20 поліморфізм реалізовано через віртуальні функції, проте використання атрибутів `final` для конкретних класів дозволяє компілятору виконувати devirtualization під час оптимізації LTO.

2. **Безпека ресурсів та простота підтримки:**
C++20 API повністю усуває людський фактор при керуванні пам'яттю. Завдяки патерну RAII та типу `sgh::OrdinalPtr` витоки пам'яті стають неможливими навіть при виникненні глибоких рекурсивних винятків. У C API розробник зобов'язаний суворо дотримуватися парності викликів конструкторів та `ord_free()`.

3. **Обробка виняткових ситуацій:**
У C API помилки передаються через коди повернення `SghStatus`, що вимагає ручної перевірки статусів після кожного виклику. У C++ API помилки транслюються в типізовані винятки (`OverflowException`, `ParseException`), що дозволяє відокремити основну логіку трансфінітних обчислень від блоків обробки збоїв.

## Деталізований аналіз поведінки на крайових випадках

Під час роботи з екстремальними ординальними виразами бібліотека гарантує суворо визначену поведінку:

- **Нульовий аргумент `n = 0`:** Функція `evaluate(0)` повертає константу для скінченних ординалів або генерує помилку `SGH_ERR_INVALID_ORDINAL`, оскільки фундаментальні послідовності та гомоморфізм Кантора строго визначені для натурального ряду `n ≥ 1`.
- **Порожні суми та константи `0`:** Вузол `ConstantNode(0)` поводиться як нейтральний елемент додавання: додавання нульового вузла до суми Кантора автоматично редукується без виділення зайвої пам'яті.
- **Глибокі вежі омег `ω ↑↑ k`:** При обчисленні виразів високої ординальної глибини двигун контролює розмір системного стека і повертає `SGH_ERR_OVERFLOW` до виникнення фатального апаратного збою `Stack Overflow`.

## Вимоги до системного оточення та сумісність компіляторів

Бібліотека протестована та гарантує повну сумісність із такими стандартами та інструментами збирання:

- **Компілятори C:** GCC 9+, Clang 10+, Apple Clang 12+, MSVC 2019 (версія 16.8+) з підтримкою стандарту C99 або C11.
- **Компілятори C++:** GCC 11+, Clang 13+, MSVC 2022 з повною підтримкою стандартних концептів C++20, `std::string_view`, атрибутів `[[nodiscard]]` та заголовка `<memory>`.
- **Апаратні архітектури:** x86-64 (Intel 64 / AMD64), ARM64 (AArch64), RISC-V 64. Не вимагає наявності апаратного модуля чисел із рухомою комою (FPU), оскільки всі операції є строго цілочисельними.
- **Операційні системи:** Linux (glibc 2.17+, musl libc), macOS 11+, FreeBSD 12+, Microsoft Windows 10/11 та Windows Server (MSVC ABI та MinGW-w64).

## Гарантії безпеки, паралелізму та інваріанти пам'яті

1. **Сувора безпека винятків (Strong Exception Guarantee):**
Усі модифікуючі методи гарантують, що у разі виникнення помилки виділення пам'яті або арифметичного переповнення стан існуючих об'єктів не пошкоджується. Всі ресурси автоматично вивільняються деструкторами `std::unique_ptr`.

2. **Потокобезпечність (Thread Safety):**
- Одночасне читання та виклик методу `evaluate()` над тим самим екземпляром `OrdinalNode` з кількох незалежних потоків є повністю безпечним і не вимагає синхронізації (Read-Only Concurrency).
- Одночасна модифікація дерева вимагає зовнішнього блокування через `std::shared_mutex` або застосування патерну копіювання при записі (COW).

3. **Складність операцій:**
- Створення вузлів: `O(1)` час, `O(1)` пам'ять.
- Оцінка `evaluate(n)`: `O(|α| · log(max_exp))` час, `O(depth(α))` пам'ять стека.
- Крок редукції `fundamental_step(n)`: `O(depth(α))` час та пам'ять.
- Порівняння двох ординалів: `O(min(|a|, |b|))`.

Цей програмний інтерфейс повністю покриває всі практичні потреби сучасних математичних та інженерних застосувань, забезпечуючи детерміновану роботу, максимальну швидкодію, сувору безпеку пам'яті та надійний математичний контроль за трансфінітними обчислювальними процесами будь-якої глибини. Завдяки модульній архітектурі бібліотека легко інтегрується як у високонавантажені мікросервісні хмарні платформи аналізу програмного коду, так і в автономні локальні компілятори сучасних системних мов програмування для критично важливих обчислювальних систем.


