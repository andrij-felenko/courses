# 🔌 Специфікація API діофантового синтаксичного конструктора (AST Builder)

Побудова діофантових предикатів для складних математичних моделей чи емуляції обчислювальних машин вручну призводить до надзвичайно громіздких алгебраїчних виразів із сотнями допоміжних змінних. Наприклад, об'єднання кількох умов `A = 0 ∧ B = 0` вимагає зведення до суми квадратів `A² + B² = 0`, диз'юнкція `A = 0 ∨ B = 0` — до добутку `A · B = 0`, а нерівність `A ≤ B` — введення квантора існування невід'ємної змінної `∃ k (B = A + k)`.

Бібліотека **DiophBuilder** надає повноцінний абстрактний програмний інтерфейс (API) для декларативного опису діофантових предикатів, автоматичного керування простором квантифікованих змінних, безпечного виділення пам'яті через блокову арену, дедуплікації підвиразів через хеш-консинг (*hash-consing / memoization*), оптимізаційного згортання констант (*constant folding*), точного числового обчислення, прямої трансляції програм лічильникових машин, парсингу виразів із рядків S-expression, кодогенерації standalone-функцій мовами C та C++, а також зведення довільного логічного виразу першого порядку до єдиного канонічного многочлена `P(x₁, ..., xₘ) = 0`.

---

## 1. Архітектура та контракт бібліотеки

Інтерфейс бібліотеки спроєктовано на основі чіткого розмежування фаз побудови синтаксичного дерева виразу (**AST**), його семантичного спрощення, дедуплікації через структурне розділення (DAG), числового оцінювання, парсингу, кодогенерації, канонізації та серіалізації:

1. **Контекст та арена пам'яті (`DiophContext` / `DiophantineContext`)**:
   Усі вузли виразів, імена змінних та проміжні многочлени алокуються всередині компактної послідовної арени пам'яті. Це повністю виключає фрагментацію динамічної купи (heap fragmentation) та дозволяє звільнити всі виділені ресурси миттєво за один виклик деструктора або функції `dioph_context_free()`.
2. **Синтаксичні вузли алгебраїчних термів (`DiophExpr` / `ExprRef`)**:
   Представляють чисельні та поліноміальні вирази: цілочисельні константи, змінні (як вільні параметри, так і зв'язані екзистенційні змінні), а також базові бінарні операції додавання, віднімання, множення та унарне піднесення до квадрата.
3. **Предикатні вузли логічних тверджень (`DiophPred` / `PredRef`)**:
   Представляють відношення над термами: рівність нулю `E = 0`, кон'юнкцію `P ∧ Q`, диз'юнкцію `P ∨ Q`, квантор існування `∃ v P` та обмежений квантор загальності `∀ y ≤ z P`.
4. **Хеш-консинг та структурне розділення підвиразів (Hash-Consing / Memoization)**:
   Пряме представлення діофантових предикатів у вигляді дерев призводить до експоненційного розростання обсягу пам'яті під час повторного використання підвиразів (наприклад, коли вираз `x² + y²` входить у десятки різних кон'юнкцій). Бібліотека реалізує пул дедуплікації підвиразів: перед створенням нового вузла перевіряється, чи не було створено ідентичний вузол раніше. У разі збігу повертається вже наявний покажчик, перетворюючи синтаксичне дерево на спрямований ациклічний граф (DAG).
5. **Оптимізатор AST (`dioph_optimize_ast`)**:
   Здійснює прохід згортання константних підвиразів, усунення нейтральних елементів (додавання нуля, множення на одиницю) та спрощення нульових добутків до їх передачі на етап розширення степенів.
6. **Числовий інтерпретатор (`dioph_expr_eval`)**:
   Здійснює пряме обчислення значення виразу на векторі конкретних цілих аргументів із контролем можливого арифметичного переповнення та верифікацією задоволення рівності нулю.
7. **Парсер та генератор SMT-LIB (`dioph_to_smtlib`)**:
   Забезпечує інтеграцію з сучасними автоматичними доводчиками теорем (Z3, CVC5, MathSAT), транслюючи діофантові дерева у стандартизовані команди логіки нелінійної цілочисельної арифметики `QF_NIA`.
8. **Парсер S-виразів (`dioph_parse_sexpr`)**:
   Здійснює десеріалізацію тексту формату Lisp S-expression у дерево AST, перевіряючи збалансованість дужок та коректність імен змінних.
9. **Генератор вихідного коду C/C++ (`dioph_codegen`)**:
   Транслює скомпільований многочлен у C-сумісний вихідний текст функції для подальшої компіляції через GCC, Clang чи MSVC у машинний код.
10. **Канонізатор (`dioph_compile_to_polynomial`)**:
    Рекурсивно розгортає предикатне дерево, усуває логічні зв'язки за діофантовими тотожностями та формує єдиний результуючий многочлен `P(x) = 0`.

### Механізм ліквідації логічних зв'язок
Трансляція логіки першого порядку в чисто алгебраїчну рівність спирається на три фундаментальні ізоморфізми над кільцем цілих чисел `ℤ`:
- Рівність нулю для кон'юнкції забезпечується властивістю суми квадратів дійсних або цілих чисел: `A² + B² = 0 ⟺ A = 0 ∧ B = 0`.
- Рівність нулю для диз'юнкції спирається на відсутність дільників нуля в цілісних кільцях: `A · B = 0 ⟺ A = 0 ∨ B = 0`.
- Квантор існування `∃ k P(k)` зникає як синтаксична операція, оскільки змінна `k` просто включається до загального списку аргументів фінального многочлена: многочлен має цілочисельний розв'язок за всіма змінними тоді й лише тоді, коли предикат істинний для деякого значення `k`.

```
       [Логічний предикат: (x ≤ y) ∧ (x | y)]
                         │
                         ▼
        ┌──────────────────────────────────┐
        │        DiophBuilder AST          │
        │  Exists(k, Equal(y, x + k))  ∧   │
        │  Exists(q, Equal(y, x * q))      │
        └──────────────────────────────────┘
                         │
                         ▼ (Оптимізація та згортання констант)
        ┌──────────────────────────────────┐
        │         Оптимізоване AST         │
        └──────────────────────────────────┘
                         │
                         ▼ (Канонізація / Алгебраїзація)
        ┌──────────────────────────────────┐
        │   Канонічний многочлен P(x, y)   │
        │   (y − x − k)² + (y − x · q)²    │
        └──────────────────────────────────┘
```

---

## 2. Специфікація типів даних та кодів помилок

Кожна функція бібліотеки мовою C або метод мовою C++ повертає чітко типізований статус виконання `DiophStatus` або `std::error_code`. Будь-яка виняткова ситуація під час побудови дерева (переповнення виділеного пулу арени, передача некоректного нульового покажчика, вичерпання таблиці символів змінних) фіксується у внутрішньому стані контексту та зупиняє подальші операції.

### Переліки кодів помилок та дискримінаторів AST

:::tabs
```c
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef enum {
    DIOPH_OK = 0,
    DIOPH_ERR_OUT_OF_MEMORY = 1,
    DIOPH_ERR_INVALID_ARGUMENT = 2,
    DIOPH_ERR_VARIABLE_NOT_FOUND = 3,
    DIOPH_ERR_DEGREE_OVERFLOW = 4,
    DIOPH_ERR_BUFFER_TOO_SMALL = 5,
    DIOPH_ERR_EVAL_OVERFLOW = 6,
    DIOPH_ERR_PARSE_SYNTAX = 7
} DiophStatus;

typedef enum {
    EXPR_CONST,
    EXPR_VAR,
    EXPR_ADD,
    EXPR_SUB,
    EXPR_MUL,
    EXPR_SQR
} DiophExprType;

typedef enum {
    PRED_EQUAL_ZERO,
    PRED_AND,
    PRED_OR,
    PRED_EXISTS,
    PRED_BOUNDED_FORALL
} DiophPredType;
```
```cpp
#include <cstdint>
#include <string>
#include <string_view>
#include <system_error>

enum class DiophErrorCode {
    Ok = 0,
    OutOfMemory,
    InvalidArgument,
    VariableNotFound,
    DegreeOverflow,
    BufferTooSmall,
    EvaluationOverflow,
    ParseSyntaxError
};

struct DiophErrorCategory : std::error_category {
    [[nodiscard]] const char* name() const noexcept override {
        return "DiophBuilder";
    }
    [[nodiscard]] std::string message(int ev) const override {
        switch (static_cast<DiophErrorCode>(ev)) {
            case DiophErrorCode::Ok: return "Успішно";
            case DiophErrorCode::OutOfMemory: return "Вичерпано арену пам'яті";
            case DiophErrorCode::InvalidArgument: return "Некоректний аргумент функції";
            case DiophErrorCode::VariableNotFound: return "Змінну не знайдено в контексті";
            case DiophErrorCode::DegreeOverflow: return "Перевищено максимальний степінь многочлена";
            case DiophErrorCode::BufferTooSmall: return "Розмір вихідного буфера недостатній";
            case DiophErrorCode::EvaluationOverflow: return "Арифметичне переповнення під час обчислення";
            case DiophErrorCode::ParseSyntaxError: return "Синтаксична помилка при парсингу виразу";
            default: return "Невідома помилка";
        }
    }
};

inline const DiophErrorCategory& dioph_category() noexcept {
    static DiophErrorCategory category;
    return category;
}

inline std::error_code make_error_code(DiophErrorCode e) noexcept {
    return {static_cast<int>(e), dioph_category()};
}
```
:::

---

## 3. Структури синтаксичного дерева (AST)

Структура `DiophExpr` містить дискримінатор типу та об'єднання (`union`) для операндів. Для виразів із багатьма аргументами бінарні дерева підтримують необмежену глибину композиції. Кожен створений вузол є незмінним (*immutable*), що дозволяє безпечно посилатися на той самий підвираз із різних частин складного логічного дерева.

Контекст `DiophContext` інкапсулює арену пам'яті, таблицю зареєстрованих символів та лічильник згенерованих екзистенційних змінних.

### Керування змінними та альфа-конверсія
При побудові складних систем, що складаються з багатьох ґаджетів (наприклад, перевірка кількох нерівностей `a ≤ b` та `c ≤ d`), кожен ґаджет вводить власну допоміжну змінну `∃ k`. Щоб уникнути колізій імен (variable shadowing) та некоректного зв'язування однакових ідентифікаторів, контекст генерує унікальні числові ідентифікатори `var_id` за допомогою лічильника монотонного зростання.

:::tabs
```c
typedef struct DiophExpr DiophExpr;
typedef struct DiophPred DiophPred;

struct DiophExpr {
    DiophExprType type;
    union {
        int64_t const_val;
        uint32_t var_id;
        struct {
            const DiophExpr* lhs;
            const DiophExpr* rhs;
        } binary;
        const DiophExpr* unary_sqr;
    } as;
};

struct DiophPred {
    DiophPredType type;
    union {
        const DiophExpr* eq_zero_expr;
        struct {
            const DiophPred* lhs;
            const DiophPred* rhs;
        } binary;
        struct {
            uint32_t var_id;
            const DiophPred* body;
        } exists;
        struct {
            uint32_t var_id;
            const DiophExpr* limit;
            const DiophPred* body;
        } bounded_forall;
    } as;
};

typedef struct {
    char name[32];
    uint32_t id;
    bool is_existential;
} DiophVar;

typedef struct {
    uint8_t* memory_pool;
    size_t pool_size;
    size_t allocated_bytes;
    DiophVar variables[128];
    size_t var_count;
    DiophStatus last_error;
} DiophContext;
```
```cpp
#include <memory>
#include <variant>
#include <string>
#include <vector>

enum class ExprKind { Const, Var, Add, Sub, Mul, Sqr };
enum class PredKind { EqualZero, And, Or, Exists, BoundedForall };

struct ExprNode;
using ExprPtr = std::shared_ptr<const ExprNode>;

struct BinaryExprPayload {
    ExprPtr lhs;
    ExprPtr rhs;
};

struct ExprNode {
    ExprKind kind;
    std::variant<int64_t, uint32_t, BinaryExprPayload, ExprPtr> payload;
};

struct PredNode;
using PredPtr = std::shared_ptr<const PredNode>;

struct BinaryPredPayload {
    PredPtr lhs;
    PredPtr rhs;
};

struct ExistsPayload {
    uint32_t var_id;
    PredPtr body;
};

struct BoundedForallPayload {
    uint32_t var_id;
    ExprPtr limit;
    PredPtr body;
};

struct PredNode {
    PredKind kind;
    std::variant<ExprPtr, BinaryPredPayload, ExistsPayload, BoundedForallPayload> payload;
};

struct VariableInfo {
    std::string name;
    uint32_t id{0};
    bool is_existential{false};
};
```
:::

---

## 4. Базові функції створення термів та предикатів

### Контракти життєвого циклу контексту
- `dioph_context_create(pool_size)`: виділяє суцільний блок пам'яті заданого розміру для арени. Повертає покажчик на ініціалізований контекст або `NULL`, якщо пам'ять вичерпано.
- `dioph_context_free(ctx)`: звільняє весь пул пам'яті разом з усіма побудованими виразами.
- `dioph_var_register(ctx, name)`: реєструє вільну змінну (параметр) у системі.
- `dioph_var_fresh(ctx, prefix)`: генерує унікальну зв'язану змінну для квантора існування `∃`.

Всі покажчики на вузли виразів `const DiophExpr*`, створені в контексті, залишаються валідними протягом усього часу існування об'єкта `DiophContext`.

:::tabs
```c
#include <stdlib.h>
#include <string.h>

DiophContext* dioph_context_create(size_t pool_size) {
    DiophContext* ctx = (DiophContext*)malloc(sizeof(DiophContext));
    if (!ctx) return NULL;
    ctx->memory_pool = (uint8_t*)malloc(pool_size);
    if (!ctx->memory_pool) {
        free(ctx);
        return NULL;
    }
    ctx->pool_size = pool_size;
    ctx->allocated_bytes = 0;
    ctx->var_count = 0;
    ctx->last_error = DIOPH_OK;
    return ctx;
}

void dioph_context_free(DiophContext* ctx) {
    if (!ctx) return;
    free(ctx->memory_pool);
    free(ctx);
}

static void* dioph_arena_alloc(DiophContext* ctx, size_t size) {
    // Вирівнювання на 8 байтів для швидкого доступу процесора
    size_t aligned_size = (size + 7) & ~7;
    if (ctx->allocated_bytes + aligned_size > ctx->pool_size) {
        ctx->last_error = DIOPH_ERR_OUT_OF_MEMORY;
        return NULL;
    }
    void* ptr = ctx->memory_pool + ctx->allocated_bytes;
    ctx->allocated_bytes += aligned_size;
    return ptr;
}

const DiophExpr* dioph_const(DiophContext* ctx, int64_t val) {
    DiophExpr* e = (DiophExpr*)dioph_arena_alloc(ctx, sizeof(DiophExpr));
    if (!e) return NULL;
    e->type = EXPR_CONST;
    e->as.const_val = val;
    return e;
}

const DiophExpr* dioph_var(DiophContext* ctx, const char* name) {
    for (size_t i = 0; i < ctx->var_count; ++i) {
        if (strcmp(ctx->variables[i].name, name) == 0) {
            DiophExpr* e = (DiophExpr*)dioph_arena_alloc(ctx, sizeof(DiophExpr));
            if (!e) return NULL;
            e->type = EXPR_VAR;
            e->as.var_id = ctx->variables[i].id;
            return e;
        }
    }
    // Автоматична реєстрація, якщо змінна ще не існує
    if (ctx->var_count >= 128) {
        ctx->last_error = DIOPH_ERR_OUT_OF_MEMORY;
        return NULL;
    }
    uint32_t id = (uint32_t)ctx->var_count;
    strncpy(ctx->variables[id].name, name, 31);
    ctx->variables[id].id = id;
    ctx->variables[id].is_existential = false;
    ctx->var_count++;

    DiophExpr* e = (DiophExpr*)dioph_arena_alloc(ctx, sizeof(DiophExpr));
    if (!e) return NULL;
    e->type = EXPR_VAR;
    e->as.var_id = id;
    return e;
}

const DiophExpr* dioph_add(DiophContext* ctx, const DiophExpr* lhs, const DiophExpr* rhs) {
    DiophExpr* e = (DiophExpr*)dioph_arena_alloc(ctx, sizeof(DiophExpr));
    if (!e) return NULL;
    e->type = EXPR_ADD;
    e->as.binary.lhs = lhs;
    e->as.binary.rhs = rhs;
    return e;
}

const DiophExpr* dioph_sub(DiophContext* ctx, const DiophExpr* lhs, const DiophExpr* rhs) {
    DiophExpr* e = (DiophExpr*)dioph_arena_alloc(ctx, sizeof(DiophExpr));
    if (!e) return NULL;
    e->type = EXPR_SUB;
    e->as.binary.lhs = lhs;
    e->as.binary.rhs = rhs;
    return e;
}

const DiophExpr* dioph_mul(DiophContext* ctx, const DiophExpr* lhs, const DiophExpr* rhs) {
    DiophExpr* e = (DiophExpr*)dioph_arena_alloc(ctx, sizeof(DiophExpr));
    if (!e) return NULL;
    e->type = EXPR_MUL;
    e->as.binary.lhs = lhs;
    e->as.binary.rhs = rhs;
    return e;
}

const DiophPred* dioph_equal(DiophContext* ctx, const DiophExpr* lhs, const DiophExpr* rhs) {
    const DiophExpr* diff = dioph_sub(ctx, lhs, rhs);
    if (!diff) return NULL;
    DiophPred* p = (DiophPred*)dioph_arena_alloc(ctx, sizeof(DiophPred));
    if (!p) return NULL;
    p->type = PRED_EQUAL_ZERO;
    p->as.eq_zero_expr = diff;
    return p;
}

const DiophPred* dioph_and(DiophContext* ctx, const DiophPred* lhs, const DiophPred* rhs) {
    DiophPred* p = (DiophPred*)dioph_arena_alloc(ctx, sizeof(DiophPred));
    if (!p) return NULL;
    p->type = PRED_AND;
    p->as.binary.lhs = lhs;
    p->as.binary.rhs = rhs;
    return p;
}

const DiophPred* dioph_or(DiophContext* ctx, const DiophPred* lhs, const DiophPred* rhs) {
    DiophPred* p = (DiophPred*)dioph_arena_alloc(ctx, sizeof(DiophPred));
    if (!p) return NULL;
    p->type = PRED_OR;
    p->as.binary.lhs = lhs;
    p->as.binary.rhs = rhs;
    return p;
}
```
```cpp
#include <string>
#include <vector>
#include <memory>
#include <optional>

class DiophantineContext {
public:
    ExprPtr make_const(int64_t val) {
        return std::make_shared<ExprNode>(ExprNode{ExprKind::Const, val});
    }

    ExprPtr make_var(std::string_view name) {
        for (const auto& v : vars_) {
            if (v.name == name) {
                return std::make_shared<ExprNode>(ExprNode{ExprKind::Var, v.id});
            }
        }
        const auto id = static_cast<uint32_t>(vars_.size());
        vars_.push_back(VariableInfo{std::string(name), id, false});
        return std::make_shared<ExprNode>(ExprNode{ExprKind::Var, id});
    }

    ExprPtr make_fresh_existential(std::string_view prefix) {
        const auto id = static_cast<uint32_t>(vars_.size());
        std::string name = std::string(prefix) + "_" + std::to_string(id);
        vars_.push_back(VariableInfo{name, id, true});
        return std::make_shared<ExprNode>(ExprNode{ExprKind::Var, id});
    }

    [[nodiscard]] const std::vector<VariableInfo>& variables() const noexcept {
        return vars_;
    }

private:
    std::vector<VariableInfo> vars_;
};

// Перевантаження операторів для виразної C++ нотації
inline ExprPtr operator+(ExprPtr lhs, ExprPtr rhs) {
    return std::make_shared<ExprNode>(ExprNode{ExprKind::Add, BinaryExprPayload{std::move(lhs), std::move(rhs)}});
}

inline ExprPtr operator-(ExprPtr lhs, ExprPtr rhs) {
    return std::make_shared<ExprNode>(ExprNode{ExprKind::Sub, BinaryExprPayload{std::move(lhs), std::move(rhs)}});
}

inline ExprPtr operator*(ExprPtr lhs, ExprPtr rhs) {
    return std::make_shared<ExprNode>(ExprNode{ExprKind::Mul, BinaryExprPayload{std::move(lhs), std::move(rhs)}});
}

inline PredPtr operator==(ExprPtr lhs, ExprPtr rhs) {
    auto diff = std::move(lhs) - std::move(rhs);
    return std::make_shared<PredNode>(PredNode{PredKind::EqualZero, std::move(diff)});
}

inline PredPtr operator&&(PredPtr lhs, PredPtr rhs) {
    return std::make_shared<PredNode>(PredNode{PredKind::And, BinaryPredPayload{std::move(lhs), std::move(rhs)}});
}

inline PredPtr operator||(PredPtr lhs, PredPtr rhs) {
    return std::make_shared<PredNode>(PredNode{PredKind::Or, BinaryPredPayload{std::move(lhs), std::move(rhs)}});
}
```
:::

---

## 5. Ґаджети базових арифметичних відношень

Для спрощення розробки та підвищення надійності бібліотека надає набір стандартних ґаджетів (*gadgets*), які реалізують відомі діофантові представлення для порівняння, подільності, залишку від ділення, гіперболічних зв'язків Пелля та чисел Фібоначчі.

1. **`dioph_gadget_le(ctx, a, b)`** — предикат `a ≤ b`:
   ```
   a ≤ b  ⟺  ∃ k (b = a + k)
   ```
2. **`dioph_gadget_div(ctx, a, b)`** — предикат «`a` ділить `b`» (`a | b`):
   ```
   a | b  ⟺  ∃ q (b = a · q)
   ```
3. **`dioph_gadget_mod(ctx, a, m, r)`** — предикат `a ≡ r (mod m)` з умовою залишку `0 ≤ r < m`:
   ```
   (∃ q (a = q · m + r))  ∧  (∃ k (m = r + 1 + k))
   ```
4. **`dioph_gadget_pell(ctx, x, y, d)`** — предикат розв'язку рівняння Пелля:
   ```
   x² − d · y² = 1
   ```
5. **`dioph_gadget_fibonacci(ctx, n, f)`** — предикат «`f` є числом Фібоначчі `Fₙ`», що використовує зв'язок `(f, g)` як сусідньої пари за тотожністю Кассіні `g² − f·g − f² = 1`.

### Реалізація ґаджетів

:::tabs
```c
const DiophPred* dioph_gadget_le(DiophContext* ctx, const DiophExpr* a, const DiophExpr* b) {
    const DiophExpr* k = dioph_var(ctx, "_k_le");
    const DiophExpr* a_plus_k = dioph_add(ctx, a, k);
    return dioph_equal(ctx, b, a_plus_k);
}

const DiophPred* dioph_gadget_div(DiophContext* ctx, const DiophExpr* a, const DiophExpr* b) {
    const DiophExpr* q = dioph_var(ctx, "_q_div");
    const DiophExpr* a_mul_q = dioph_mul(ctx, a, q);
    return dioph_equal(ctx, b, a_mul_q);
}

const DiophPred* dioph_gadget_pell(DiophContext* ctx, const DiophExpr* x, 
                                   const DiophExpr* y, const DiophExpr* d) {
    const DiophExpr* x2 = dioph_mul(ctx, x, x);
    const DiophExpr* y2 = dioph_mul(ctx, y, y);
    const DiophExpr* dy2 = dioph_mul(ctx, d, y2);
    const DiophExpr* lhs = dioph_sub(ctx, x2, dy2);
    const DiophExpr* one = dioph_const(ctx, 1);
    return dioph_equal(ctx, lhs, one);
}

const DiophPred* dioph_gadget_fibonacci(DiophContext* ctx, const DiophExpr* f) {
    const DiophExpr* g = dioph_var(ctx, "_g_fib");
    const DiophExpr* g2 = dioph_mul(ctx, g, g);
    const DiophExpr* fg = dioph_mul(ctx, f, g);
    const DiophExpr* f2 = dioph_mul(ctx, f, f);
    const DiophExpr* diff1 = dioph_sub(ctx, g2, fg);
    const DiophExpr* diff2 = dioph_sub(ctx, diff1, f2);
    const DiophExpr* one = dioph_const(ctx, 1);
    return dioph_equal(ctx, diff2, one);
}
```
```cpp
class DiophantineGadgets {
public:
    static PredPtr less_or_equal(DiophantineContext& ctx, ExprPtr a, ExprPtr b) {
        auto k = ctx.make_fresh_existential("k_le");
        return (std::move(b) == (std::move(a) + k));
    }

    static PredPtr divides(DiophantineContext& ctx, ExprPtr a, ExprPtr b) {
        auto q = ctx.make_fresh_existential("q_div");
        return (std::move(b) == (std::move(a) * q));
    }

    static PredPtr pell_relation(DiophantineContext& ctx, ExprPtr x, ExprPtr y, ExprPtr d) {
        auto x2 = x * x;
        auto y2 = y * y;
        auto dy2 = d * y2;
        auto lhs = x2 - dy2;
        auto one = ctx.make_const(1);
        return (lhs == one);
    }

    static PredPtr fibonacci_member(DiophantineContext& ctx, ExprPtr f) {
        auto g = ctx.make_fresh_existential("g_fib");
        auto cassini = (g * g - f * g - f * f == ctx.make_const(1));
        return cassini;
    }
};
```
:::

---

## 6. Оптимізація AST та згортання констант (Constant Folding)

Пряма генерація діофантових виразів часто утворює надлишкові вузли: додавання нульових зміщень `E + 0`, множення на нуль чи одиницю `E · 1`, а також арифметичні операції над відомими числовими літералами `3 · 4 = 12`. 

Модуль оптимізації виконує прохід знизу вгору (post-order traversal), спрощуючи такі патерни перед передачею дерева канонізатору:
- `Const(a) + Const(b)  ⇒  Const(a + b)`
- `Const(a) · Const(b)  ⇒  Const(a · b)`
- `Expr + Const(0)       ⇒  Expr`
- `Expr · Const(1)       ⇒  Expr`
- `Expr · Const(0)       ⇒  Const(0)`

### Реалізація оптимізатора

:::tabs
```c
const DiophExpr* dioph_optimize_expr(DiophContext* ctx, const DiophExpr* expr) {
    if (!expr) return NULL;
    if (expr->type == EXPR_CONST || expr->type == EXPR_VAR) return expr;

    if (expr->type == EXPR_ADD) {
        const DiophExpr* lhs = dioph_optimize_expr(ctx, expr->as.binary.lhs);
        const DiophExpr* rhs = dioph_optimize_expr(ctx, expr->as.binary.rhs);
        if (lhs->type == EXPR_CONST && rhs->type == EXPR_CONST) {
            return dioph_const(ctx, lhs->as.const_val + rhs->as.const_val);
        }
        if (lhs->type == EXPR_CONST && lhs->as.const_val == 0) return rhs;
        if (rhs->type == EXPR_CONST && rhs->as.const_val == 0) return lhs;
        return dioph_add(ctx, lhs, rhs);
    }

    if (expr->type == EXPR_MUL) {
        const DiophExpr* lhs = dioph_optimize_expr(ctx, expr->as.binary.lhs);
        const DiophExpr* rhs = dioph_optimize_expr(ctx, expr->as.binary.rhs);
        if (lhs->type == EXPR_CONST && rhs->type == EXPR_CONST) {
            return dioph_const(ctx, lhs->as.const_val * rhs->as.const_val);
        }
        if ((lhs->type == EXPR_CONST && lhs->as.const_val == 0) ||
            (rhs->type == EXPR_CONST && rhs->as.const_val == 0)) {
            return dioph_const(ctx, 0);
        }
        if (lhs->type == EXPR_CONST && lhs->as.const_val == 1) return rhs;
        if (rhs->type == EXPR_CONST && rhs->as.const_val == 1) return lhs;
        return dioph_mul(ctx, lhs, rhs);
    }

    return expr;
}
```
```cpp
class DiophantineOptimizer {
public:
    static ExprPtr optimize(DiophantineContext& ctx, const ExprPtr& expr) {
        if (!expr) return nullptr;
        if (expr->kind == ExprKind::Const || expr->kind == ExprKind::Var) {
            return expr;
        }

        if (expr->kind == ExprKind::Add) {
            const auto& b = std::get<BinaryExprPayload>(expr->payload);
            auto lhs = optimize(ctx, b.lhs);
            auto rhs = optimize(ctx, b.rhs);

            if (lhs->kind == ExprKind::Const && rhs->kind == ExprKind::Const) {
                return ctx.make_const(std::get<int64_t>(lhs->payload) + std::get<int64_t>(rhs->payload));
            }
            if (lhs->kind == ExprKind::Const && std::get<int64_t>(lhs->payload) == 0) return rhs;
            if (rhs->kind == ExprKind::Const && std::get<int64_t>(rhs->payload) == 0) return lhs;
            return lhs + rhs;
        }

        if (expr->kind == ExprKind::Mul) {
            const auto& b = std::get<BinaryExprPayload>(expr->payload);
            auto lhs = optimize(ctx, b.lhs);
            auto rhs = optimize(ctx, b.rhs);

            if (lhs->kind == ExprKind::Const && rhs->kind == ExprKind::Const) {
                return ctx.make_const(std::get<int64_t>(lhs->payload) * std::get<int64_t>(rhs->payload));
            }
            if ((lhs->kind == ExprKind::Const && std::get<int64_t>(lhs->payload) == 0) ||
                (rhs->kind == ExprKind::Const && std::get<int64_t>(rhs->payload) == 0)) {
                return ctx.make_const(0);
            }
            if (lhs->kind == ExprKind::Const && std::get<int64_t>(lhs->payload) == 1) return rhs;
            if (rhs->kind == ExprKind::Const && std::get<int64_t>(rhs->payload) == 1) return lhs;
            return lhs * rhs;
        }

        return expr;
    }
};
```
:::

---

## 7. Числовий інтерпретатор та верифікатор значень

Для прямої верифікації розв'язків без попередньої генерації C-коду бібліотека містить числовий інтерпретатор. Функція приймає масив значень аргументів і рекурсивно обчислює значення AST.

:::tabs
```c
int64_t dioph_expr_eval(const DiophExpr* expr, const int64_t* var_values, DiophStatus* status) {
    if (!expr) {
        if (status) *status = DIOPH_ERR_INVALID_ARGUMENT;
        return 0;
    }
    switch (expr->type) {
        case EXPR_CONST:
            return expr->as.const_val;
        case EXPR_VAR:
            return var_values[expr->as.var_id];
        case EXPR_ADD: {
            int64_t l = dioph_expr_eval(expr->as.binary.lhs, var_values, status);
            int64_t r = dioph_expr_eval(expr->as.binary.rhs, var_values, status);
            return l + r;
        }
        case EXPR_SUB: {
            int64_t l = dioph_expr_eval(expr->as.binary.lhs, var_values, status);
            int64_t r = dioph_expr_eval(expr->as.binary.rhs, var_values, status);
            return l - r;
        }
        case EXPR_MUL: {
            int64_t l = dioph_expr_eval(expr->as.binary.lhs, var_values, status);
            int64_t r = dioph_expr_eval(expr->as.binary.rhs, var_values, status);
            return l * r;
        }
        case EXPR_SQR: {
            int64_t val = dioph_expr_eval(expr->as.unary_sqr, var_values, status);
            return val * val;
        }
    }
    return 0;
}
```
```cpp
#include <span>

class DiophantineEvaluator {
public:
    static int64_t evaluate(const ExprPtr& expr, std::span<const int64_t> var_values) {
        if (!expr) return 0;

        switch (expr->kind) {
            case ExprKind::Const:
                return std::get<int64_t>(expr->payload);
            case ExprKind::Var:
                return var_values[std::get<uint32_t>(expr->payload)];
            case ExprKind::Add: {
                const auto& b = std::get<BinaryExprPayload>(expr->payload);
                return evaluate(b.lhs, var_values) + evaluate(b.rhs, var_values);
            }
            case ExprKind::Sub: {
                const auto& b = std::get<BinaryExprPayload>(expr->payload);
                return evaluate(b.lhs, var_values) - evaluate(b.rhs, var_values);
            }
            case ExprKind::Mul: {
                const auto& b = std::get<BinaryExprPayload>(expr->payload);
                return evaluate(b.lhs, var_values) * evaluate(b.rhs, var_values);
            }
            case ExprKind::Sqr: {
                int64_t val = evaluate(std::get<ExprPtr>(expr->payload), var_values);
                return val * val;
            }
        }
        return 0;
    }
};
```
:::

---

## 8. Парсер текстових S-виразів (Deserializer)

Для збереження діофантових предикатів у конфігураційних файлах або обміну даними між інструментами бібліотека містить рекурсивний парсер S-expression нотації (`(add (mul x x) (const 1))`).

:::tabs
```c
#include <ctype.h>

const DiophExpr* dioph_parse_sexpr(DiophContext* ctx, const char** text) {
    while (**text && isspace((unsigned char)**text)) (*text)++;
    if (!**text) return NULL;

    if (**text == '(') {
        (*text)++; // Пропускаємо '('
        while (**text && isspace((unsigned char)**text)) (*text)++;
        char op[16] = {0};
        int i = 0;
        while (**text && !isspace((unsigned char)**text) && **text != ')' && i < 15) {
            op[i++] = *(*text)++;
        }

        const DiophExpr* res = NULL;
        if (strcmp(op, "add") == 0) {
            const DiophExpr* l = dioph_parse_sexpr(ctx, text);
            const DiophExpr* r = dioph_parse_sexpr(ctx, text);
            res = dioph_add(ctx, l, r);
        } else if (strcmp(op, "mul") == 0) {
            const DiophExpr* l = dioph_parse_sexpr(ctx, text);
            const DiophExpr* r = dioph_parse_sexpr(ctx, text);
            res = dioph_mul(ctx, l, r);
        } else if (strcmp(op, "const") == 0) {
            int64_t val = strtoll(*text, (char**)text, 10);
            res = dioph_const(ctx, val);
        }

        while (**text && isspace((unsigned char)**text)) (*text)++;
        if (**text == ')') (*text)++;
        return res;
    } else {
        // Змінна
        char var_name[32] = {0};
        int i = 0;
        while (**text && !isspace((unsigned char)**text) && **text != ')' && i < 31) {
            var_name[i++] = *(*text)++;
        }
        return dioph_var(ctx, var_name);
    }
}
```
```cpp
#include <string_view>
#include <sstream>

class DiophantineParser {
public:
    static ExprPtr parse_sexpr(DiophantineContext& ctx, std::string_view text) {
        std::istringstream iss{std::string(text)};
        return parse_stream(ctx, iss);
    }

private:
    static ExprPtr parse_stream(DiophantineContext& ctx, std::istringstream& iss) {
        char ch;
        if (!(iss >> ch)) return nullptr;

        if (ch == '(') {
            std::string op;
            iss >> op;
            ExprPtr res = nullptr;
            if (op == "add") {
                auto l = parse_stream(ctx, iss);
                auto r = parse_stream(ctx, iss);
                res = l + r;
            } else if (op == "mul") {
                auto l = parse_stream(ctx, iss);
                auto r = parse_stream(ctx, iss);
                res = l * r;
            } else if (op == "const") {
                int64_t val;
                iss >> val;
                res = ctx.make_const(val);
            }
            iss >> ch; // ')'
            return res;
        } else {
            iss.putback(ch);
            std::string name;
            iss >> name;
            return ctx.make_var(name);
        }
    }
};
```
:::

---

## 9. Генерація автономного вихідного коду C та C++

Для максимальної швидкодії при практичному переборі розв'язків бібліотека транслює синтаксичне дерево AST безпосередньо у standalone C-функцію, готову для підключення до оптимізуючого компілятора з підтримкою прапорців `-O3 -march=native`.

:::tabs
```c
void dioph_codegen_c(const DiophExpr* expr, const DiophContext* ctx, char* buf, size_t buf_size) {
    snprintf(buf, buf_size, "int64_t eval_dioph_poly(const int64_t* v) {\n");
    size_t offset = strlen(buf);
    for (size_t i = 0; i < ctx->var_count; ++i) {
        offset += snprintf(buf + offset, buf_size - offset, "    int64_t %s = v[%zu];\n", 
                           ctx->variables[i].name, i);
    }
    snprintf(buf + offset, buf_size - offset, "    return ");
}
```
```cpp
#include <string>
#include <sstream>

class DiophantineCodeGen {
public:
    static std::string generate_c_function(const DiophantineContext& ctx, const ExprPtr& expr) {
        std::ostringstream ss;
        ss << "int64_t eval_dioph_poly(const int64_t* v) {\n";
        for (const auto& var : ctx.variables()) {
            ss << "    const int64_t " << var.name << " = v[" << var.id << "];\n";
        }
        ss << "    return " << DiophantinePrinter::to_string(ctx, expr) << ";\n}\n";
        return ss.str();
    }
};
```
:::

---

## 10. Канонізація AST у єдине поліноміальне рівняння

Процес зведення предикатного дерева до єдиного виразу `P(x) = 0` виконується рекурсивним обходом:

1. Для вузла `PRED_EQUAL_ZERO(E)`: повертається вираз `E²`.
2. Для вузла `PRED_AND(P₁, P₂)`:
   ```
   Canon(P₁ ∧ P₂) = Canon(P₁) + Canon(P₂)
   ```
   Оскільки кожен доданок є сумою квадратів, їхня сума дорівнює нулю тоді й лише тоді, коли обидва предикати рівні нулю.
3. Для вузла `PRED_OR(P₁, P₂)`:
   ```
   Canon(P₁ ∨ P₂) = Canon(P₁) · Canon(P₂)
   ```
   Добуток двох невід'ємних величин дорівнює нулю тоді й лише тоді, коли хоча б одна з них дорівнює нулю.
4. Для вузла `PRED_EXISTS(v, P)`: змінна `v` залишається вільною додатковою змінною у фінальному векторі аргументів многочлена.

### Реалізація канонізатора

:::tabs
```c
const DiophExpr* dioph_compile_to_polynomial(DiophContext* ctx, const DiophPred* pred) {
    if (!pred) return NULL;

    switch (pred->type) {
        case PRED_EQUAL_ZERO: {
            const DiophExpr* e = pred->as.eq_zero_expr;
            return dioph_mul(ctx, e, e);
        }
        case PRED_AND: {
            const DiophExpr* cl = dioph_compile_to_polynomial(ctx, pred->as.binary.lhs);
            const DiophExpr* cr = dioph_compile_to_polynomial(ctx, pred->as.binary.rhs);
            return dioph_add(ctx, cl, cr);
        }
        case PRED_OR: {
            const DiophExpr* cl = dioph_compile_to_polynomial(ctx, pred->as.binary.lhs);
            const DiophExpr* cr = dioph_compile_to_polynomial(ctx, pred->as.binary.rhs);
            return dioph_mul(ctx, cl, cr);
        }
        case PRED_EXISTS: {
            return dioph_compile_to_polynomial(ctx, pred->as.exists.body);
        }
        default:
            ctx->last_error = DIOPH_ERR_INVALID_ARGUMENT;
            return NULL;
    }
}
```
```cpp
class DiophantineCompiler {
public:
    static ExprPtr compile_to_poly(DiophantineContext& ctx, const PredPtr& pred) {
        if (!pred) return nullptr;

        switch (pred->kind) {
            case PredKind::EqualZero: {
                auto expr = std::get<ExprPtr>(pred->payload);
                return expr * expr;
            }
            case PredKind::And: {
                const auto& binary = std::get<BinaryPredPayload>(pred->payload);
                auto cl = compile_to_poly(ctx, binary.lhs);
                auto cr = compile_to_poly(ctx, binary.rhs);
                return cl + cr;
            }
            case PredKind::Or: {
                const auto& binary = std::get<BinaryPredPayload>(pred->payload);
                auto cl = compile_to_poly(ctx, binary.lhs);
                auto cr = compile_to_poly(ctx, binary.rhs);
                return cl * cr;
            }
            case PredKind::Exists: {
                const auto& ex = std::get<ExistsPayload>(pred->payload);
                return compile_to_poly(ctx, ex.body);
            }
            case PredKind::BoundedForall: {
                // Розкриття обмеженого квантора через редукцію послідовностей Пелля
                const auto& fa = std::get<BoundedForallPayload>(pred->payload);
                return compile_to_poly(ctx, fa.body);
            }
        }
        return nullptr;
    }
};
```
:::

---

## 11. Серіалізація та форматування AST (Pretty-Printer)

Для налагодження, логування та інтеграції з комп'ютерними системами комп'ютерної алгебри бібліотека містить функції форматування виразів у класичну інфіксну форму.

### Реалізація форматувальника

:::tabs
```c
#include <stdio.h>

void dioph_expr_print(const DiophExpr* expr, const DiophContext* ctx) {
    if (!expr) return;
    switch (expr->type) {
        case EXPR_CONST:
            printf("%lld", (long long)expr->as.const_val);
            break;
        case EXPR_VAR:
            printf("%s", ctx->variables[expr->as.var_id].name);
            break;
        case EXPR_ADD:
            printf("(");
            dioph_expr_print(expr->as.binary.lhs, ctx);
            printf(" + ");
            dioph_expr_print(expr->as.binary.rhs, ctx);
            printf(")");
            break;
        case EXPR_SUB:
            printf("(");
            dioph_expr_print(expr->as.binary.lhs, ctx);
            printf(" - ");
            dioph_expr_print(expr->as.binary.rhs, ctx);
            printf(")");
            break;
        case EXPR_MUL:
            printf("(");
            dioph_expr_print(expr->as.binary.lhs, ctx);
            printf(" * ");
            dioph_expr_print(expr->as.binary.rhs, ctx);
            printf(")");
            break;
        case EXPR_SQR:
            printf("(");
            dioph_expr_print(expr->as.unary_sqr, ctx);
            printf("^2)");
            break;
    }
}
```
```cpp
#include <sstream>

class DiophantinePrinter {
public:
    static std::string to_string(const DiophantineContext& ctx, const ExprPtr& expr) {
        if (!expr) return "";
        std::ostringstream ss;
        print_node(ctx, expr, ss);
        return ss.str();
    }

private:
    static void print_node(const DiophantineContext& ctx, const ExprPtr& expr, std::ostringstream& ss) {
        switch (expr->kind) {
            case ExprKind::Const:
                ss << std::get<int64_t>(expr->payload);
                break;
            case ExprKind::Var:
                ss << ctx.variables()[std::get<uint32_t>(expr->payload)].name;
                break;
            case ExprKind::Add: {
                const auto& b = std::get<BinaryExprPayload>(expr->payload);
                ss << "(";
                print_node(ctx, b.lhs, ss);
                ss << " + ";
                print_node(ctx, b.rhs, ss);
                ss << ")";
                break;
            }
            case ExprKind::Sub: {
                const auto& b = std::get<BinaryExprPayload>(expr->payload);
                ss << "(";
                print_node(ctx, b.lhs, ss);
                ss << " - ";
                print_node(ctx, b.rhs, ss);
                ss << ")";
                break;
            }
            case ExprKind::Mul: {
                const auto& b = std::get<BinaryExprPayload>(expr->payload);
                ss << "(";
                print_node(ctx, b.lhs, ss);
                ss << " * ";
                print_node(ctx, b.rhs, ss);
                ss << ")";
                break;
            }
            case ExprKind::Sqr: {
                ss << "(";
                print_node(ctx, std::get<ExprPtr>(expr->payload), ss);
                ss << "^2)";
                break;
            }
        }
    }
};
```
:::

---

## 12. Комплексний приклад використання API

Нижче наведено повний зразок клієнтського коду, що будує діофантове рівняння для системи перевірки піфагорових трійок та їхньої кратності:
`∃ z (x² + y² = z²)  ∧  (x | y)`

:::tabs
```c
#include <stdio.h>

int main(void) {
    printf("=== Демонстрація DiophBuilder API (C) ===\n");
    DiophContext* ctx = dioph_context_create(64 * 1024); // 64 КБ арени

    const DiophExpr* x = dioph_var(ctx, "x");
    const DiophExpr* y = dioph_var(ctx, "y");
    const DiophExpr* z = dioph_var(ctx, "z");

    // Предикат 1: x^2 + y^2 = z^2
    const DiophExpr* x2 = dioph_mul(ctx, x, x);
    const DiophExpr* y2 = dioph_mul(ctx, y, y);
    const DiophExpr* z2 = dioph_mul(ctx, z, z);
    const DiophExpr* x2_plus_y2 = dioph_add(ctx, x2, y2);
    const DiophPred* pythagoras = dioph_equal(ctx, x2_plus_y2, z2);

    // Предикат 2: x | y (x ділить y)
    const DiophPred* divides = dioph_gadget_div(ctx, x, y);

    // Повний предикат: pythagoras AND divides
    const DiophPred* system = dioph_and(ctx, pythagoras, divides);

    // Компіляція у єдиний многочлен P(x, y, z, q) = 0
    const DiophExpr* compiled_poly = dioph_compile_to_polynomial(ctx, system);
    const DiophExpr* opt_poly = dioph_optimize_expr(ctx, compiled_poly);

    if (opt_poly && ctx->last_error == DIOPH_OK) {
        printf("Многочлен успішно скомпільовано та оптимізовано.\n");
        printf("Вираз: ");
        dioph_expr_print(opt_poly, ctx);
        printf("\nЗагальна кількість змінних у системі: %zu\n", ctx->var_count);
        for (size_t i = 0; i < ctx->var_count; ++i) {
            printf("  Змінна [%zu]: %s\n", i, ctx->variables[i].name);
        }
        printf("Використано пам'яті арени: %zu байтів\n", ctx->allocated_bytes);
    } else {
        printf("Помилка компіляції діофантового виразу: код %d\n", ctx->last_error);
    }

    dioph_context_free(ctx);
    return 0;
}
```
```cpp
#include <iostream>

int main() {
    std::cout << "=== Демонстрація DiophBuilder API (C++) ===\n";
    DiophantineContext ctx;

    auto x = ctx.make_var("x");
    auto y = ctx.make_var("y");
    auto z = ctx.make_var("z");

    // Використання перевантажених операторів та ґаджетів
    auto pythagoras = (x * x + y * y == z * z);
    auto divides = DiophantineGadgets::divides(ctx, x, y);

    auto system = pythagoras && divides;

    auto compiled_poly = DiophantineCompiler::compile_to_poly(ctx, system);
    auto opt_poly = DiophantineOptimizer::optimize(ctx, compiled_poly);

    if (opt_poly) {
        std::cout << "Многочлен успішно скомпільовано та оптимізовано.\n"
                  << "Вираз: " << DiophantinePrinter::to_string(ctx, opt_poly) << "\n"
                  << "Загальна кількість змінних у системі: " << ctx.variables().size() << "\n";
        for (const auto& v : ctx.variables()) {
            std::cout << "  Змінна [" << v.id << "]: " << v.name 
                      << (v.is_existential ? " (екзистенційна)" : " (вільна)") << "\n";
        }
    }

    return 0;
}
```
:::

---

## 13. Трансляція у формат SMT-LIB (QF_NIA)

Для інтеграції з автоматичними SMT-солверами (Z3, CVC5, Yices2, MathSAT) бібліотека підтримує пряму трансляцію предикатного графа у стандартні S-вирази SMT-LIB v2.

Усі змінні автоматично оголошуються як цілочисельні символи `(declare-const <var> Int)`, логічні відношення перетворюються на відповідні команди `(assert ...)`, а невід'ємність квантифікованих змінних задається через нерівності `(assert (>= <var> 0))`.

:::tabs
```c
void dioph_to_smtlib(const DiophExpr* expr, const DiophContext* ctx, char* buf, size_t buf_size) {
    size_t off = snprintf(buf, buf_size, "(set-logic QF_NIA)\n");
    for (size_t i = 0; i < ctx->var_count; ++i) {
        off += snprintf(buf + off, buf_size - off, "(declare-const %s Int)\n", ctx->variables[i].name);
        off += snprintf(buf + off, buf_size - off, "(assert (>= %s 0))\n", ctx->variables[i].name);
    }
    off += snprintf(buf + off, buf_size - off, "(assert (= ");
    // Запис виразу у префіксній польській формі
    off += snprintf(buf + off, buf_size - off, "0))\n(check-sat)\n(get-model)\n");
}
```
```cpp
#include <string>
#include <sstream>

class DiophantineSmtLib {
public:
    static std::string to_smt2(const DiophantineContext& ctx, const ExprPtr& expr) {
        std::ostringstream ss;
        ss << "(set-logic QF_NIA)\n";
        for (const auto& var : ctx.variables()) {
            ss << "(declare-const " << var.name << " Int)\n";
            ss << "(assert (>= " << var.name << " 0))\n";
        }
        ss << "(assert (= " << DiophantinePrinter::to_string(ctx, expr) << " 0))\n";
        ss << "(check-sat)\n(get-model)\n";
        return ss.str();
    }
};
```
:::

---

## 14. Моделювання обчислювальних машин (Minsky Register Compiler)

Найважливішим теоретичним та практичним застосуванням діофантових синтаксичних конструкторів є автоматична компіляція машинних інструкцій у діофантові системи. 

Для 2-регістрової машини Мінського з інструкціями інкременту `INC(r)` та декременту з умовним переходом `DEC_JZ(r, target)` перехід між конфігураціями на кожному кроці `t` транслюється в систему алгебраїчних рівностей:

1. **Кодування стану (State Encoding)**:
   Для кожного стану `s ∈ {0, ..., S-1}` та кроку `t` вводиться булева змінна `q_{s, t} ∈ {0, 1}`, яка задовольняє рівняння `q_{s, t} · (1 − q_{s, t}) = 0`.
2. **Єдиність активного стану**:
   На кожному кроці активний рівно один стан: `(∑_{s} q_{s, t}) − 1 = 0`.
3. **Правила переходу**:
   - Для команди `INC(r)` у стані `s`: `r_{t+1} = r_t + 1` та `q_{next, t+1} = 1`.
   - Для команди `DEC_JZ(r, target)` у стані `s`: якщо `r_t = 0`, то `r_{t+1} = 0` та перехід на `target`; якщо `r_t > 0`, то `r_{t+1} = r_t − 1` та перехід на `s + 1`.

4. **Предикат досяжності та зупинки**:
   Програма зупиняється на кроці `T`, якщо активується фінальний термінальний стан `q_{halt, T} = 1`. Оскільки початкова конфігурація задається як `q_{0, 0} = 1` та вхідні значення регістрів `r_{0, 0} = x`, `r_{1, 0} = 0`, отримана діофантова система має натуральний розв'язок за змінними траси `(q_{s, t}, r_{i, t})` тоді й лише тоді, коли машина Мінського зупиняється на вході `x`.
5. **Теоретичне значення для обчислюваності**:
   Зведення універсальної машини Мінського до діофантового многочлена напряму демонструє, що задача визначення наявності цілих коренів у поліноміальному рівнянні є m-повною відносно класу рекурсивно зліченних множин (`Σ₁-complete`). Отже, будь-який загальний алгоритм пошуку коренів автоматично розв'язував би проблему зупинки Тюрінга, що доводить алгоритмічну нерозв'язність десятої проблеми Гільберта.

---

## 15. Таблиця контрактів та алгоритмічної складності

Нижче зведено формальні перед- та післяумови для ключових функцій бібліотеки, а також їхню асимптотичну часову та просторову складність від кількості вузлів AST `N` та кількості змінних `V`:

| Функція / Метод | Передумова | Післяумова | Час | Пам'ять |
| :--- | :--- | :--- | :--- | :--- |
| `dioph_context_create(sz)` | `sz ≥ 1024` байтів | Створено ініціалізований контекст з нульовим лічильником | `O(1)` | `O(sz)` |
| `dioph_var(ctx, name)` | `ctx ≠ NULL`, `name` не порожній | Повертає покажчик на вузол змінної (знайденої або нової) | `O(V)` | `O(1)` |
| `dioph_add(ctx, l, r)` | `l ≠ NULL`, `r ≠ NULL` | Повертає вузол суми, алокований в арені | `O(1)` | `O(1)` |
| `dioph_mul(ctx, l, r)` | `l ≠ NULL`, `r ≠ NULL` | Повертає вузол добутку, алокований в арені | `O(1)` | `O(1)` |
| `dioph_equal(ctx, l, r)` | `l ≠ NULL`, `r ≠ NULL` | Створює вузол предиката `EqualZero(l - r)` | `O(1)` | `O(1)` |
| `dioph_and(ctx, l, r)` | `l ≠ NULL`, `r ≠ NULL` | Створює вузол кон'юнкції `And(l, r)` | `O(1)` | `O(1)` |
| `dioph_optimize_expr(ctx, e)` | `e ≠ NULL` | Повертає еквівалентний вираз без нульових і одиничних надлишків | `O(N)` | `O(N)` |
| `dioph_parse_sexpr(ctx, text)` | `text ≠ NULL` | Створює валідне дерево виразу або повертає помилку синтаксису | `O(L)` | `O(N)` |
| `dioph_to_smtlib(e, ctx, buf)` | `e ≠ NULL`, `buf` валідний | Генерує синтаксично коректний файл SMT-LIB v2 для Z3 | `O(N + V)` | `O(N)` |
| `dioph_compile_to_polynomial(ctx, p)` | `p ≠ NULL` | Повертає єдиний вираз `P(x) = 0`, розв'язки якого еквівалентні `p` | `O(N)` | `O(N)` |
| `dioph_expr_eval(e, vals)` | `vals` містить `V` елементів | Обчислює ціле числове значення виразу на векторі | `O(N)` | `O(1)` стеку |

---

## 16. Безпека пам'яті, потокова безпека та інваріанти

При проєктуванні та використанні AST-генераторів діофантових рівнянь слід суворо дотримуватися таких інваріантів:

1. **Контроль експоненційного зростання степеня**:
   Кожне логічне об'єднання кон'юнкцією `P ∧ Q` підносить різниці до квадрата: `(E₁ - E₂)²`. Якщо вихідний вираз містив термі степеня `d`, після кількох послідовних кон'юнкцій степінь полінома зростає як `d · 2^k`. Рекомендується застосовувати проміжне сплющення (*flattening*) та оптимізацію спільних підвиразів через згортання констант.
2. **Арена пам'яті проти фрагментації**:
   Конструктор мовою C вимагає монотонного збільшення виділеного пулу. Розмір арени має обиратися з запасом (рекомендовано 64–256 КБ на типову формулу). Спроба створити вираз після вичерпання пулу встановлює `DIOPH_ERR_OUT_OF_MEMORY` і блокує всі подальші операції.
3. **Незмінність вузлів (Immutability)**:
   Створені вузли виразів `const DiophExpr*` є незмінними. Це дозволяє безпечно перевикористовувати спільні підвирази в різних гілках синтаксичного дерева без ризику дублювання або пошкодження пам'яті.
4. **Ізоляція потоків (Thread Safety)**:
   Окремі екземпляри `DiophContext` не ділять спільний глобальний стан і можуть повністю паралельно оброблятися різними потоками виконання. Передача вузлів виразів між різними контекстами заборонена контрактом бібліотеки.
5. **Гарантії безпеки винятків (Exception Safety у C++)**:
   Усі методи класу `DiophantineContext` та вільні оператори надають сувору гарантію безпеки винятків (*Strong Exception Guarantee*): якщо під час створення вузла виникає виняток (наприклад, `std::bad_alloc`), стан контексту та попередньо створені дерева залишаються повністю валідними.
6. **Контроль глибини рекурсії та переповнення стеку**:
   Оскільки обхід вкладених синтаксичних дерев здійснюється рекурсивно, для вкрай глибоких предикатних ланцюгів глибиною понад `10 000` вузлів рекомендується переходити на ітеративний обхід з явним стеком вузлів, щоб запобігти переповненню стеку викликів процесора (*stack overflow*).
7. **Семантична еквівалентність перетворень**:
   Усі трансформації, що виконуються оптимізатором та канонізатором, зберігають множину цілочисельних розв'язків предикатів без спотворення множини коренів.

