# 📋 Специфікація інтерфейсу та структури даних CNF-парсера

Ця специфікація визначає інтерфейсний контракт, формати представлення структур даних у пам'яті, сигнатури функцій та конвенції обробки помилок для вбудовуваного рушія синтаксичного аналізу на основі алгоритму Кока–Янгера–Касамі (CYK). Інтерфейс розроблено для безшовної інтеграції універсального розпізнавача в компілятори, мовні сервери (Language Server Protocol, LSP), статичні аналізатори коду та біоінформатичні конвеєри аналізу послідовностей.

## 1. Архітектурні принципи та модель володіння пам'яттю

Контракт бібліотеки спирається на три фундаментальні інженерні принципи:

1. **Незмінність скомпільованої граматики (Immutability):** Після створення об'єкта `cyk_context_t` усі внутрішні таблиці правил та індекси пар переходять у режим «тільки для читання». Об'єкт контексту є повністю потокобезпечним (thread-safe) і може одночасно використовуватися довільною кількістю робочих потоків без синхронізації та блокувань м'ютексами.
2. **Ізоляція пам'яті запиту (Per-query Allocation):** Таблиця динамічного програмування, необхідна для розбору конкретного вхідного рядка, виділяється або в локальній пам'яті потоку (стек/арена), або динамічно в купі на час виконання виклику `cyk_parse_tokens`. Контекст граматики не зберігає стану попередніх запитів.
3. **Чітке розмежування валідації та побудови дерева:** Якщо додатку потрібна лише перевірка синтаксичної коректності слова, виділення вузлів дерева синтаксичного розбору (AST) вимикається передачею `NULL` у вихідний параметр, що знижує витрати пам'яті до `O(n²)` бітів.

---

## 2. Структури даних у пам'яті

### 2.1. Ідентифікатори символів та бітові маски
Для забезпечення максимальної швидкодії внутрішній рушій оперує числовими дескрипторами нетермінальних та термінальних символів:

:::tabs
```c
typedef uint16_t cyk_symbol_t;  /* Числовий ідентифікатор символу */
typedef uint64_t cyk_bitset_t;  /* Бітова маска для множин нетерміналів */
#define CYK_NULL_SYMBOL 0xFFFF
```
```cpp
#include <cstdint>

using cyk_symbol_t = uint16_t;
using cyk_bitset_t = uint64_t;
inline constexpr cyk_symbol_t CYK_NULL_SYMBOL = 0xFFFF;
```
:::

| Поле / Тип | Діапазон значень | Призначення |
| :--- | :--- | :--- |
| `cyk_symbol_t` | `0 .. 65535` | Унікальний числовий ідентифікатор нетермінала або термінала в таблиці символів |
| `cyk_bitset_t` | `64 біти` | Швидка множина нетерміналів у клітинці таблиці розбору |
| `CYK_NULL_SYMBOL` | `0xFFFF` | Спеціальний маркер відсутності символу або термінального вузла |

### 2.2. Структура правила граматики
Граматика розбивається на два незалежні масиви продукцій для мінімізації промахів кешу процесора (L1 Instruction / Data Cache):

:::tabs
```c
typedef struct {
    cyk_symbol_t lhs;   /* Ліва частина: нетермінал A */
    cyk_symbol_t rhs1;  /* Права частина: перший нетермінал B */
    cyk_symbol_t rhs2;  /* Права частина: другий нетермінал C */
} cyk_binary_rule_t;

typedef struct {
    cyk_symbol_t lhs;       /* Ліва частина: нетермінал A */
    cyk_symbol_t terminal;  /* Права частина: термінальний символ a */
} cyk_terminal_rule_t;
```
```cpp
struct BinaryRule {
    cyk_symbol_t lhs;
    cyk_symbol_t rhs1;
    cyk_symbol_t rhs2;
};

struct TerminalRule {
    cyk_symbol_t lhs;
    cyk_symbol_t terminal;
};
```
:::

### 2.3. Контекст парсера (`cyk_context_t`)
Головний об'єкт стану, що містить скомпільовану граматику, зворотні індекси та конфігурацію:

:::tabs
```c
typedef struct {
    cyk_symbol_t start_symbol;
    const cyk_binary_rule_t* binary_rules;
    size_t num_binary_rules;
    const cyk_terminal_rule_t* terminal_rules;
    size_t num_terminal_rules;
    
    /* Зворотний індекс пар: lookup[B * max_symbols + C] -> список правил */
    uint32_t* pair_index_offsets;
    cyk_symbol_t* pair_index_rules;
    size_t max_nonterminals;
} cyk_context_t;
```
```cpp
#include <vector>
#include <span>

class GrammarContext {
public:
    cyk_symbol_t start_symbol;
    std::vector<BinaryRule> binary_rules;
    std::vector<TerminalRule> terminal_rules;
    std::vector<uint32_t> pair_index_offsets;
    std::vector<cyk_symbol_t> pair_index_rules;
    size_t max_nonterminals = 0;
};
```
:::

---

## 3. Публічний інтерфейс функцій

### 3.1. Ініціалізація та компіляція граматики

:::tabs
```c
cyk_status_t cyk_context_create(
    cyk_symbol_t start_symbol,
    const cyk_binary_rule_t* bin_rules,
    size_t num_bin,
    const cyk_terminal_rule_t* term_rules,
    size_t num_term,
    cyk_context_t** out_ctx
);
```
```cpp
#include <expected>
#include <memory>
#include <span>

std::expected<std::unique_ptr<GrammarContext>, cyk_status_t> make_grammar_context(
    cyk_symbol_t start_symbol,
    std::span<const BinaryRule> bin_rules,
    std::span<const TerminalRule> term_rules
);
```
:::

- **Параметри:**
  - `start_symbol` — числовий ідентифікатор початкового нетермінала (`S`).
  - `bin_rules` — масив бінарних правил `A → BC`.
  - `num_bin` — кількість бінарних правил у переданому масиві.
  - `term_rules` — масив термінальних правил `A → a`.
  - `num_term` — кількість термінальних правил у переданому масиві.
  - `out_ctx` — вказівник на створений об'єкт контексту.
- **Передмови:** Масиви `bin_rules` та `term_rules` повинні містити виключно валідні індекси символів у діапазоні `0 .. max_nonterminals - 1`. Правила повинні суворо відповідати обмеженням CNF (відсутність змішаних або довгих правил).
- **Повертає:** `CYK_STATUS_OK` у разі успішної валідації та побудови індексів; відповідний код помилки при виявленні некоректних правил.

### 3.2. Синтаксичний розбір рядка токенів

:::tabs
```c
cyk_status_t cyk_parse_tokens(
    const cyk_context_t* ctx,
    const cyk_symbol_t* tokens,
    size_t token_count,
    bool* out_is_accepted,
    cyk_tree_node_t** out_tree_root
);
```
```cpp
#include <optional>
#include <span>

struct ParseResult {
    bool accepted = false;
    std::unique_ptr<TreeNode> tree = nullptr;
};

std::expected<ParseResult, cyk_status_t> parse_tokens(
    const GrammarContext& ctx,
    std::span<const cyk_symbol_t> tokens,
    bool build_tree = true
);
```
:::

- **Параметри:**
  - `ctx` — попередньо скомпільований контекст граматики.
  - `tokens` — неперервний масив вхідних термінальних токенів довжини `token_count`.
  - `token_count` — кількість символів у вхідному рядку.
  - `out_is_accepted` — вихідний булевий прапорець (істина, якщо слово належить граматиці).
  - `out_tree_root` — опційний вказівник для повернення кореня виділеного AST-дерева (може бути `NULL`, якщо потрібна лише валідація).
- **Часова складність:** `O(n³ · |G|)`.
- **Просторова складність:** `O(n² · |V_N|)` для збереження таблиці розбору та `O(n)` для дерева виведення.

### 3.3. Звільнення ресурсів

:::tabs
```c
void cyk_tree_free(cyk_tree_node_t* root);
void cyk_context_destroy(cyk_context_t* ctx);
```
```cpp
/* У C++ пам'ять звільняється автоматично через деструктори
   std::unique_ptr<TreeNode> та GrammarContext (RAII) */
```
:::

- `cyk_tree_free` — рекурсивно вивільняє всю пам'ять вузлів дерева, виділених під час синтаксичного аналізу.
- `cyk_context_destroy` — звільняє всі внутрішні індексні таблиці, масиви пар та структуру контексту.

---

## 4. Коди статусів та діагностика помилок

:::tabs
```c
typedef enum {
    CYK_STATUS_OK                  = 0,
    CYK_ERROR_INVALID_ARGUMENT     = 1,
    CYK_ERROR_OUT_OF_MEMORY        = 2,
    CYK_ERROR_EMPTY_INPUT          = 3,
    CYK_ERROR_SYMBOL_OUT_OF_BOUNDS = 4,
    CYK_ERROR_INVALID_CNF_RULE     = 5,
    CYK_ERROR_AMBIGUOUS_OVERFLOW   = 6
} cyk_status_t;
```
```cpp
enum class cyk_status_t : uint8_t {
    OK = 0,
    InvalidArgument = 1,
    OutOfMemory = 2,
    EmptyInput = 3,
    SymbolOutOfBounds = 4,
    InvalidCnfRule = 5,
    AmbiguousOverflow = 6
};
```
:::

| Код помилки | Опис ситуації | Спосіб відновлення |
| :--- | :--- | :--- |
| `CYK_STATUS_OK` | Операція завершилася успішно | Продовжити обробку результату |
| `CYK_ERROR_INVALID_ARGUMENT` | Передано нульовий вказівник (`NULL`) або невалідний розмір | Перевірити аргументи перед викликом |
| `CYK_ERROR_OUT_OF_MEMORY` | Не вдалося виділити пам'ять під таблицю розбору | Зменшити розмір блоку або збільшити ліміти пам'яті |
| `CYK_ERROR_EMPTY_INPUT` | Вхідний рядок має довжину 0 без наявності правила `S → ε` | Перевірити наявність порожніх вихідних файлів |
| `CYK_ERROR_INVALID_CNF_RULE` | Правило містить неприпустиму комбінацію символів | Виконати попередню 5-крокову нормалізацію CNF |

---

## 5. Дерево синтаксичного розбору (AST Node Structure)

:::tabs
```c
typedef struct cyk_tree_node {
    cyk_symbol_t symbol;              /* Нетермінал вузла (A) */
    cyk_symbol_t terminal_value;      /* Термінал (якщо листок), або CYK_NULL_SYMBOL */
    size_t span_start;                /* Початковий індекс підрядка (1-indexed) */
    size_t span_length;               /* Довжина охопленого підрядка */
    struct cyk_tree_node* left_child;  /* Лівий нащадок (B) */
    struct cyk_tree_node* right_child; /* Правий нащадок (C) */
} cyk_tree_node_t;
```
```cpp
#include <memory>
#include <optional>

struct TreeNode {
    cyk_symbol_t symbol;
    std::optional<cyk_symbol_t> terminal_value;
    size_t span_start;
    size_t span_length;
    std::unique_ptr<TreeNode> left_child;
    std::unique_ptr<TreeNode> right_child;
};
```
:::

Кожен внутрішній вузол гарантує виконання інваріанта:
```
node->span_length = node->left_child->span_length + node->right_child->span_length
node->right_child->span_start = node->left_child->span_start + node->left_child->span_length
```

## 6. Механізми діагностики та локалізації синтаксичних помилок

Коли синтаксичний аналізатор повертає `out_is_accepted = false`, виникає необхідність повідомити користувачеві точне місце синтаксичної помилки в тексті програми. У класичному CYK пряма локалізація ускладнена тим, що алгоритм працює глобально знизу-вгору.

Для ефективної діагностики рушій надає алгоритм аналізу найбільшого розпізнаного префікса (Longest Parsed Prefix Analysis):
1. **Сканування діагоналей чарту:** Визначається максимальний індекс `j`, для якого в клітинці `P[j, 1]` міститься хоча б один нетермінал, що може бути лівою частиною валідного синтаксичного правила.
2. **Множина очікуваних символів (Expected Symbols Set):** Для позиції збою `j + 1` обчислюється множина терміналів `EXPECTED = { a ∈ V_T | ∃ (A → B C), B ∈ P[j, 1], C ⇒* a ... }`.
3. **Формування діагностичного повідомлення:** Помилка позиціонується на токені `tokens[j]`, а користувачеві виводиться перелік очікуваних токенів, які дозволили б продовжити виведення.

## 7. Розширення для ймовірнісних граматик (Probabilistic CYK)

Для задач комп'ютерної лінгвістики та аналізу неоднозначних природних мов інтерфейс розширюється підтримкою ваг та ймовірностей:

:::tabs
```c
typedef struct {
    cyk_symbol_t lhs;
    cyk_symbol_t rhs1;
    cyk_symbol_t rhs2;
    float log_probability; /* Логарифм ймовірності log P(A -> BC) */
} cyk_prob_binary_rule_t;

typedef struct {
    cyk_symbol_t lhs;
    cyk_symbol_t terminal;
    float log_probability; /* Логарифм ймовірності log P(A -> a) */
} cyk_prob_terminal_rule_t;
```
```cpp
struct ProbBinaryRule {
    cyk_symbol_t lhs;
    cyk_symbol_t rhs1;
    cyk_symbol_t rhs2;
    float log_probability;
};

struct ProbTerminalRule {
    cyk_symbol_t lhs;
    cyk_symbol_t terminal;
    float log_probability;
};
```
:::

Використання логарифмів ймовірностей замість прямих чисел із плаваючою комою усуває арифметичне зникнення порядку (underflow) при множенні десятків малих ймовірностей у глибоких деревах синтаксичного виведення.

## 8. Оцінка споживання пам'яті та ліміти реального часу

Для вбудованих систем реального часу важливо розрахувати максимальний обсяг оперативної пам'яті (RAM), необхідний парсеру до початку виконання:

```
RAM_Bytes(n, |V_N|) = ((n(n + 1)) / 2) · [ sizeof(cyk_bitset_t) + k_avg · sizeof(Backpointer) ]
```

Для типових параметрів вхідного тексту в компіляторах та DSL (`n = 100` токенів, `|V_N| ≤ 64` нетермінали):
- Розмір таблиці становить `(100 · 101) / 2 = 5050` клітинок.
- Бітова маска займає `5050 · 8 = 40.4 КБ`.
- Зворотні вказівники для однозначної граматики займають близько `120 КБ`.
- Загальні витрати пам'яті не перевищують `200 КБ`, що дозволяє запускати CYK-парсер навіть на мікроконтролерах із зовнішньою SRAM.

## 9. Потокобезпечність та арена пам'яті для серверних навантажень

У високонавантажених серверах обробки запитів (наприклад, веб-серверах синтаксичного аналізу природної мови) часті виклики системного розподільника пам'яті `malloc`/`free` створюють суттєву конкуренцію за системні блокування купи (heap lock contention).

Для усунення цієї проблеми рекомендовано використовувати патерн арени пам'яті (Memory Arena):
1. Кожен робочий потік виділяє фіксований лінійний буфер пам'яті розміру `RAM_Bytes(max_n)`.
2. Усі вузли AST-дерева та клітинки чарту виділяються простим зміщенням покажчика арени `offset += size` за час `O(1)`.
3. Після завершення розбору вся арена скидається єдиною операцією `offset = 0` без потреби у рекурсивному обході та індивідуальному вивільненні сотень дрібних блоків пам'яті.

## 10. Приклад використання API у сторонньому додатку

:::tabs
```c
/* Приклад компіляції граматики та розбору послідовності токенів */
cyk_context_t* ctx = NULL;
cyk_binary_rule_t bin_rules[] = {
    { 0, 1, 2 }, /* S -> A B */
    { 1, 2, 1 }  /* A -> B A */
};
cyk_terminal_rule_t term_rules[] = {
    { 1, 100 },  /* A -> 'a' */
    { 2, 101 }   /* B -> 'b' */
};

cyk_status_t status = cyk_context_create(0, bin_rules, 2, term_rules, 2, &ctx);
if (status == CYK_STATUS_OK) {
    cyk_symbol_t input_tokens[] = { 101, 100 }; /* "ba" */
    bool accepted = false;
    cyk_tree_node_t* tree = NULL;
    
    if (cyk_parse_tokens(ctx, input_tokens, 2, &accepted, &tree) == CYK_STATUS_OK) {
        if (accepted) {
            /* Обробка синтаксичного дерева */
            cyk_tree_free(tree);
        }
    }
    cyk_context_destroy(ctx);
}
```
```cpp
/* Приклад на C++20 із безпечним керуванням пам'яттю */
std::vector<BinaryRule> bin_rules = {
    { 0, 1, 2 },
    { 1, 2, 1 }
};
std::vector<TerminalRule> term_rules = {
    { 1, 100 },
    { 2, 101 }
};

auto ctx_res = make_grammar_context(0, bin_rules, term_rules);
if (ctx_res.has_value()) {
    std::vector<cyk_symbol_t> input_tokens = { 101, 100 };
    auto parse_res = parse_tokens(*ctx_res.value(), input_tokens);
    if (parse_res.has_value() && parse_res.value().accepted) {
        /* Обробка синтаксичного дерева: parse_res.value().tree */
    }
}
```
:::
