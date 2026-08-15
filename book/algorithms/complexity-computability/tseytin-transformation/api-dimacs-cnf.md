# 📋 Інтерфейс та специфікація формату DIMACS CNF для SAT-інструментів

Стандарт формату DIMACS CNF визначає текстову структуру представлення булевих диз'юнктів для взаємодії між кодерами Цейтіна та SAT-розв'язувачами.

Формат DIMACS CNF розроблено Центром дискретної математики та теоретичної інформатики (DIMACS) при Ратґерському університеті як універсальний протокол обміну даними між інструментами логічної обробки. Він є стандартом de facto для всіх сучасних SAT-розв'язувачів (MiniSAT, Z3, CaDiCaL, Glucose, Lingeling, CryptoMiniSat). Усі сучасні промислові інструменти верифікації апаратного забезпечення (EDA), транслятори логічних схем (Yosys, ABC) та системи статичного аналізу коду зводять вхідні вирази до цього текстового або бінарного стандарту.

## 1. Специфікація текстового формату DIMACS CNF

Файл формату DIMACS CNF є текстовим файлом у кодуванні ASCII, який складається з трьох послідовних секцій: секції коментарів, рядка заголовка (Problem Line) та секції диз'юнктів (Clause Section).

```
c =====================================================================
c Файл згенеровано алгоритмом Цейтіна для формули: (A ∧ B) ∨ ¬C
c Символьна таблиця: 1=A, 2=B, 3=C, 4=x1(A AND B), 5=x2(Root)
c =====================================================================
p cnf 5 7
-4 1 0
-4 2 0
4 -1 -2 0
-5 4 0
-5 3 0
5 -4 -3 0
5 0
```

### 1.1. Секція коментарів

Секція коментарів слугує для збереження метаінформації, описів вхідної формули та таблиць символів.

- Кожен рядок коментаря обов'язково починається з малого латинського символу `c`, після якого йде пробіл або символ табуляції.
- Коментарі можуть розміщуватися у будь-якому місці до рядка заголовка `p cnf`. Більшість сучасних SAT-солверів ігнорують рядки, що починаються з `c`, навіть якщо вони розміщені між диз'юнктами, але для сумісності зі строгими парсерами коментарі згруповують на початку файла.
- Інструменти Цейтін-кодування використовують коментарі для збереження таблиці відповідності (Symbol Table) між оригінальними іменами булевих змінних, назвами сигналів логічної схеми та їх числовими індексами у КНФ:

```
c Symbol Table:
c Variable 1 -> A (input_pin_0)
c Variable 2 -> B (input_pin_1)
c Variable 3 -> C (input_pin_2)
c Variable 4 -> x1 (Internal node: A AND B)
c Variable 5 -> x2 (Internal node / Root: x1 OR NOT C)
```

### 1.2. Рядок заголовка (Problem Line)

Рядок заголовка є обов'язковим і має з'являтися раніше за будь-які диз'юнкти. Він визначає розмірність задачі для попереднього виділення пам'яті у SAT-розв'язувачі. Рядок заголовка має наступний точний синтаксис:

```
p cnf <NUM_VARIABLES> <NUM_CLAUSES>
```

- `p` — ідентифікатор рядка проблеми (Problem Marker).
- `cnf` — специфікатор формату. Вказує, що формула подана у кон'юнктивній нормальній формі.
- `<NUM_VARIABLES>` — ціле додатне число, що визначає максимальний числовий індекс булевої змінної у файлі. Усі змінні нумеруються послідовно натуральними числами від `1` до `NUM_VARIABLES`. Використання змінного індексу `0` як ідентифікатора змінної заборонено, оскільки нуль зарезервовано як термінатор.
- `<NUM_CLAUSES>` — ціле додатне число, що визначає точну кількість диз'юнктів (рядків або логічних блоків), присутніх у секції диз'юнктів. Якщо фактична кількість диз'юнктів у файлі відрізняється від `NUM_CLAUSES`, парсер SAT-солвера видає помилку або попередження про розбіжність розмірності.

### 1.3. Секція диз'юнктів (Clause Section)

Секція диз'юнктів визначає логічну кон'юнкцію всіх диз'юнктів, побудованих алгоритмом Цейтіна.

- Кожен диз'юнкт подається послідовністю цілих чисел, розділених пробілами, символами табуляції або символами нового рядка.
- Позитивне ціле число `k` (де `1 ≤ k ≤ NUM_VARIABLES`) позначає позитивний літерал змінної `xₖ`.
- Негативне ціле число `-k` (де `1 ≤ -k ≤ NUM_VARIABLES`) позначає заперечення літерала `¬xₖ`.
- Число `0` позначає термінатор (розділювач кінця) поточного диз'юнкта. Воно не вважається літералом.
- Диз'юнкт може переноситися на кілька текстових рядків; термінатор `0` однозначно вказує на завершення диз'юнкта незалежно від символів переносу рядка.
- Порожній диз'юнкт (який складається лише з термінатора `0`) позначає константну хибність (UNSAT).
- Одиничний диз'юнкт (Unit Clause), наприклад `5 0`, вимагає, щоб змінна з індексом 5 мала значення 1 у будь-якій задовольняючій інтерпретації.

## 2. Стандартна таблиця КНФ-трансляції логічних елементів

Під час виконання алгоритму Цейтіна кожен логічний оператор (вентиль) перетворюється у набір диз'юнктів формату DIMACS. Нехай `p` — числовий індекс вихідної (допоміжної) змінної вентиля, а `q` та `r` — індекси вхідних операндів.

| Логічний оператор / Вентиль | Локальна еквівалентність | Диз'юнкти КНФ у математичній формі | Запис у форматі DIMACS |
| :--- | :--- | :--- | :--- |
| **NOT (Заперечення)** | `p ↔ ¬q` | `(¬p ∨ ¬q) ∧ (p ∨ q)` | `-p -q 0`<br>`p q 0` |
| **AND (Кон'юнкція)** | `p ↔ (q ∧ r)` | `(¬p ∨ q) ∧ (¬p ∨ r) ∧ (p ∨ ¬q ∨ ¬r)` | `-p q 0`<br>`-p r 0`<br>`p -q -r 0` |
| **OR (Диз'юнкція)** | `p ↔ (q ∨ r)` | `(p ∨ ¬q) ∧ (p ∨ ¬r) ∧ (¬p ∨ q ∨ r)` | `p -q 0`<br>`p -r 0`<br>`-p q r 0` |
| **IMPLIES (Імплікація)** | `p ↔ (q → r)` | `(p ∨ q) ∧ (p ∨ ¬r) ∧ (¬p ∨ ¬q ∨ r)` | `p q 0`<br>`p -r 0`<br>`-p -q r 0` |
| **XOR (Виключне АБО)** | `p ↔ (q ⊕ r)` | `(¬p ∨ ¬q ∨ ¬r) ∧ (¬p ∨ q ∨ r) ∧`<br>`(p ∨ ¬q ∨ r) ∧ (p ∨ q ∨ ¬r)` | `-p -q -r 0`<br>`-p q r 0`<br>`p -q r 0`<br>`p q -r 0` |
| **EQUIV (Еквівалентність)**| `p ↔ (q ↔ r)` | `(¬p ∨ ¬q ∨ r) ∧ (¬p ∨ q ∨ ¬r) ∧`<br>`(p ∨ ¬q ∨ ¬r) ∧ (p ∨ q ∨ r)` | `-p -q r 0`<br>`-p q -r 0`<br>`p -q -r 0`<br>`p q r 0` |
| **NAND (І-НЕ)** | `p ↔ ¬(q ∧ r)` | `(p ∨ q) ∧ (p ∨ r) ∧ (¬p ∨ ¬q ∨ ¬r)` | `p q 0`<br>`p r 0`<br>`-p -q -r 0` |
| **NOR (АБО-НЕ)** | `p ↔ ¬(q ∨ r)` | `(¬p ∨ ¬q) ∧ (¬p ∨ ¬r) ∧ (p ∨ q ∨ r)` | `-p -q 0`<br>`-p -r 0`<br>`p q r 0` |
| **MUX (Мультиплексор)** | `p ↔ (s ? q : r)` | `(¬p ∨ ¬s ∨ q) ∧ (¬p ∨ s ∨ r) ∧`<br>`(p ∨ ¬s ∨ ¬q) ∧ (p ∨ s ∨ ¬r)` | `-p -s q 0`<br>`-p s r 0`<br>`p -s -q 0`<br>`p s -r 0` |

## 3. Специфікація Програмного Інтерфейсу C та C++ API для Цейтін-кодера

Для інтеграції алгоритму Цейтіна у програмні комплекси верифікації використовується інтерфейс API. Нижче наведено структуру типів, констант та процедур генерації КНФ мовами C та C++.

:::tabs
```c
/* Оголошення C99 API для Цейтін-кодера */
#include <stdint.h>
#include <stddef.h>

typedef enum {
    TSEYTIN_OP_VAR     = 0,
    TSEYTIN_OP_NOT     = 1,
    TSEYTIN_OP_AND     = 2,
    TSEYTIN_OP_OR      = 3,
    TSEYTIN_OP_IMPLIES = 4,
    TSEYTIN_OP_XOR     = 5,
    TSEYTIN_OP_EQUIV   = 6
} TseytinOpType;

typedef int32_t TseytinLit;
typedef int32_t TseytinVar;

typedef struct {
    TseytinLit* lits;
    size_t size;
} TseytinClause;

typedef struct {
    TseytinVar max_var;
    TseytinClause* clauses;
    size_t clause_count;
    size_t clause_capacity;
} TseytinContext;

TseytinContext* tseytin_context_create(size_t num_input_vars);
void tseytin_context_free(TseytinContext* ctx);
TseytinVar tseytin_var_fresh(TseytinContext* ctx);

void tseytin_add_clause(TseytinContext* ctx, const TseytinLit* lits, size_t size);
void tseytin_encode_and(TseytinContext* ctx, TseytinVar out_var, TseytinVar in1, TseytinVar in2);
void tseytin_encode_or(TseytinContext* ctx, TseytinVar out_var, TseytinVar in1, TseytinVar in2);
void tseytin_encode_not(TseytinContext* ctx, TseytinVar out_var, TseytinVar in1);
void tseytin_encode_xor(TseytinContext* ctx, TseytinVar out_var, TseytinVar in1, TseytinVar in2);

int tseytin_export_dimacs(const TseytinContext* ctx, TseytinVar root_var, const char* filename);
```
```cpp
// Ідіоматичний C++20 API для Цейтін-кодера
#include <cstdint>
#include <vector>
#include <string_view>
#include <span>
#include <ostream>
#include <expected>

namespace tseytin {

enum class OpType : std::uint8_t {
    Var,
    Not,
    And,
    Or,
    Implies,
    Xor,
    Equiv
};

using Literal = std::int32_t;
using Variable = std::int32_t;
using Clause = std::vector<Literal>;

class Encoder {
    Variable m_maxVar;
    std::vector<Clause> m_clauses;

public:
    explicit Encoder(std::size_t numInputVars) 
        : m_maxVar(static_cast<Variable>(numInputVars)) {}

    [[nodiscard]] Variable freshVar() noexcept {
        return ++m_maxVar;
    }

    void addClause(std::span<const Literal> lits) {
        m_clauses.emplace_back(lits.begin(), lits.end());
    }

    void encodeAnd(Variable out, Variable in1, Variable in2) {
        addClause(std::array<Literal, 2>{-out, in1});
        addClause(std::array<Literal, 2>{-out, in2});
        addClause(std::array<Literal, 3>{out, -in1, -in2});
    }

    void encodeOr(Variable out, Variable in1, Variable in2) {
        addClause(std::array<Literal, 2>{out, -in1});
        addClause(std::array<Literal, 2>{out, -in2});
        addClause(std::array<Literal, 3>{-out, in1, in2});
    }

    void encodeNot(Variable out, Variable in1) {
        addClause(std::array<Literal, 2>{-out, -in1});
        addClause(std::array<Literal, 2>{out, in1});
    }

    [[nodiscard]] std::expected<void, std::string_view> 
    exportDimacs(std::ostream& os, Variable rootVar) const;
};

} // namespace tseytin
```
:::

## 4. Специфікація виходу SAT-солвера та парсинг результатів

Після того як файл у форматі DIMACS CNF передається на вхід SAT-розв'язувача (наприклад, команду `minisat input.cnf output.sat`), розв'язувач генерує стандартну відповідь:

1. **Рядок статусу рішення:**
   - `SATISFIABLE` — формула здійсненна (існує задовольняюча оцінка змінних).
   - `UNSATISFIABLE` — формула нездійсненна (доведено відсутність задовольняючих оцінок).
   - `UNKNOWN` — розв'язувач зупинився за таймаутом або лімітом пам'яті.

2. **Рядок оцінки змінних (Model Line):**
   У разі статусу `SATISFIABLE` більшість розв'язувачів виводять задовольняючу модель, яка починається з літери `v` і містить список істинних літералів, що закінчується `0`:

```
s SATISFIABLE
v 1 -2 -3 4 5 0
```

У наведеному прикладі модель призначає `x₁ = 1`, `x₂ = 0`, `x₃ = 0`, `x₄ = 1`, `x₅ = 1`.

Для отримання відповіді у термінах вхідних змінних початкової формули (наприклад `A`, `B`, `C`) кодер Цейтіна зчитує вихідний рядок `v` і фільтрує змінні, чиї індекси знаходяться в діапазоні від `1` до `num_input_vars`, ігноруючи внутрішні допоміжні змінні `x₄, x₅`.

## 5. Розширення формату: Стиснутий DIMACS (gzipped) та WCNF

У практичних застосуваннях EDA розмір DIMACS файлу для схем із мільйонами вентилів може досягати кількох гігабайт. Для економії диску використовуються розширення стандарта:

- **Compressed DIMACS (.cnf.gz):** Більшість сучасних солверів (MiniSAT, CaDiCaL) здатні напряму зчитувати стиснуті за допомогою `zlib` файли без їх попереднього розпакування.
- **Weighted CNF (WCNF / MaxSAT):** Для задач оптимізації рядки диз'юнктів доповнюються вагами (ваговими коефіцієнтами) на початку кожного рядка диз'юнкта, а заголовок має вигляд `p wcnf <vars> <clauses> <top_weight>`.

## 6. Практичний приклад виклику SAT-розв'язувача через CLI

Сформований Цейтін-кодером файл `formula.cnf` можна безпосередньо передати у консольні інструменти:

```bash
# Виклик MiniSAT із збереженням результату у result.txt
minisat formula.cnf result.txt

# Виклик Z3 у режимі DIMACS
z3 -dimacs formula.cnf

# Виклик CaDiCaL
cadical formula.cnf
```

Прямий зв'язок між Цейтін-кодером та SAT-розв'язувачем через DIMACS CNF гарантує повну сумісність інструментів формальної верифікації незалежно від мови програмування та операційної системи.
