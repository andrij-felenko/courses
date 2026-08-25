# ⚙️ Інтерпретатор та верифікатор символьних виразів арифметики Пеано

Цей практичний модуль реалізує символьний інтерпретатор та перевіряльник індуктивних доведень для арифметики Пеано мовами C та C++, демонструючи побудову синтаксичного дерева термів, автоматичне спрощення та верифікацію арифметичних тотожностей.

Для глибшого розуміння того, як логічні аксіоми Пеано функціонують у комп'ютерній інженерії та автоматичному доведенні теорем (Automated Theorem Proving, ATP), необхідно перетворити абстрактні правила `PA` на реальний синтаксичний аналізатор та обчислювальний рушій.

У цьому проекті ми побудуємо символьний рушій, який виконує три ключові завдання:
1. Представляє терми мови `L_PA` (`0`, `S(x)`, `x + y`, `x · y`, змінні) у вигляді синтаксичного дерева (Abstract Syntax Tree, AST).
2. Реалізує рекурсивний алгоритм переписування термів (term rewriting) на основі алгебраїчних аксіом Пеано.
3. Автоматично верифікує кроки базових індуктивних доведень (наприклад, тотожність `x + 0 = x` або `x + S(y) = S(x + y)`).

## 1. Архитектура символьного дерева термів Пеано

Синтаксичні терми мови арифметики Пеано можна класифікувати за п'ятьма базовими варіантами:
- `Zero`: Базовий нуль `0`.
- `Var`: Вільна або зв'язана змінна (наприклад, `"x"`, `"y"`).
- `Succ`: Унарний оператор наступника `S(t)`.
- `Add`: Бінарний оператор додавання `t₁ + t₂`.
- `Mul`: Бінарний оператор множення `t₁ · t₂`.

Операції додавання та множення у символьному вигляді не обчислюються миттєво як машинні інструкції процесора, а зберігають свою алгебраїчну форму. Редукція (спрощення) відбувається шляхом орієнтованого застосування аксіом Пеано справа наліво:

```
1. x + 0       ->  x
2. x + S(y)    ->  S(x + y)
3. x · 0       ->  0
4. x · S(y)    ->  (x · y) + x
```

Ці чотири правила утворюють канонічну (сильно нормалізовану та конфлюентну) систему переписування термів. Будь-який замкнений терм без змінних знижується до унікального канонічного нумерала `S(S(...S(0)...))` за скінченне число кроків.

## 2. Реалізація інтерпретатора мовами C та C++

Нижче наведено повну ідіоматичну реалізацію редуктора термів двома мовами у вигляді паралельних вкладок.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

/* Типи вузлів синтаксичного дерева термів Пеано */
typedef enum {
    TERM_ZERO,
    TERM_SUCC,
    TERM_ADD,
    TERM_MUL,
    TERM_VAR
} TermType;

typedef struct Term {
    TermType type;
    union {
        char var_name[16];           /* Для TERM_VAR */
        struct Term* child;          /* Для TERM_SUCC */
        struct {                     /* Для TERM_ADD та TERM_MUL */
            struct Term* left;
            struct Term* right;
        } binary;
    } data;
} Term;

/* Конструктори вузлів AST */
Term* create_zero(void) {
    Term* t = (Term*)malloc(sizeof(Term));
    if (!t) exit(1);
    t->type = TERM_ZERO;
    return t;
}

Term* create_var(const char* name) {
    Term* t = (Term*)malloc(sizeof(Term));
    if (!t) exit(1);
    t->type = TERM_VAR;
    strncpy(t->data.var_name, name, 15);
    t->data.var_name[15] = '\0';
    return t;
}

Term* create_succ(Term* child) {
    Term* t = (Term*)malloc(sizeof(Term));
    if (!t) exit(1);
    t->type = TERM_SUCC;
    t->data.child = child;
    return t;
}

Term* create_add(Term* left, Term* right) {
    Term* t = (Term*)malloc(sizeof(Term));
    if (!t) exit(1);
    t->type = TERM_ADD;
    t->data.binary.left = left;
    t->data.binary.right = right;
    return t;
}

Term* create_mul(Term* left, Term* right) {
    Term* t = (Term*)malloc(sizeof(Term));
    if (!t) exit(1);
    t->type = TERM_MUL;
    t->data.binary.left = left;
    t->data.binary.right = right;
    return t;
}

void free_term(Term* t) {
    if (!t) return;
    if (t->type == TERM_SUCC) {
        free_term(t->data.child);
    } else if (t->type == TERM_ADD || t->type == TERM_MUL) {
        free_term(t->data.binary.left);
        free_term(t->data.binary.right);
    }
    free(t);
}

/* Глибоке копіювання терма */
Term* copy_term(const Term* t) {
    if (!t) return NULL;
    switch (t->type) {
        case TERM_ZERO: return create_zero();
        case TERM_VAR:  return create_var(t->data.var_name);
        case TERM_SUCC: return create_succ(copy_term(t->data.child));
        case TERM_ADD:  return create_add(copy_term(t->data.binary.left), copy_term(t->data.binary.right));
        case TERM_MUL:  return create_mul(copy_term(t->data.binary.left), copy_term(t->data.binary.right));
    }
    return NULL;
}

/* Перевірка синтаксичної рівності двох термів */
bool terms_equal(const Term* a, const Term* b) {
    if (a == b) return true;
    if (!a || !b || a->type != b->type) return false;
    switch (a->type) {
        case TERM_ZERO: return true;
        case TERM_VAR:  return strcmp(a->data.var_name, b->data.var_name) == 0;
        case TERM_SUCC: return terms_equal(a->data.child, b->data.child);
        case TERM_ADD:
        case TERM_MUL:
            return terms_equal(a->data.binary.left, b->data.binary.left) &&
                   terms_equal(a->data.binary.right, b->data.binary.right);
    }
    return false;
}

/* Друк терма у звичній синтаксичній формі */
void print_term(const Term* t) {
    if (!t) return;
    switch (t->type) {
        case TERM_ZERO: printf("0"); break;
        case TERM_VAR:  printf("%s", t->data.var_name); break;
        case TERM_SUCC:
            printf("S(");
            print_term(t->data.child);
            printf(")");
            break;
        case TERM_ADD:
            printf("(");
            print_term(t->data.binary.left);
            printf(" + ");
            print_term(t->data.binary.right);
            printf(")");
            break;
        case TERM_MUL:
            printf("(");
            print_term(t->data.binary.left);
            printf(" · ");
            print_term(t->data.binary.right);
            printf(")");
            break;
    }
}

/* Редукція (спрощення) терма за аксіомами Пеано:
   1. x + 0 -> x
   2. x + S(y) -> S(x + y)
   3. x · 0 -> 0
   4. x · S(y) -> (x · y) + x
*/
Term* reduce_term(Term* t, bool* changed) {
    if (!t) return NULL;

    if (t->type == TERM_SUCC) {
        t->data.child = reduce_term(t->data.child, changed);
        return t;
    }

    if (t->type == TERM_ADD) {
        t->data.binary.left = reduce_term(t->data.binary.left, changed);
        t->data.binary.right = reduce_term(t->data.binary.right, changed);
        
        Term* right = t->data.binary.right;
        /* Аксіома: x + 0 -> x */
        if (right->type == TERM_ZERO) {
            Term* left = t->data.binary.left;
            free(right);
            free(t);
            *changed = true;
            return left;
        }
        /* Аксіома: x + S(y) -> S(x + y) */
        if (right->type == TERM_SUCC) {
            Term* left = t->data.binary.left;
            Term* y = right->data.child;
            Term* new_add = create_add(left, y);
            free(right);
            free(t);
            *changed = true;
            return create_succ(new_add);
        }
    }

    if (t->type == TERM_MUL) {
        t->data.binary.left = reduce_term(t->data.binary.left, changed);
        t->data.binary.right = reduce_term(t->data.binary.right, changed);

        Term* right = t->data.binary.right;
        /* Аксіома: x · 0 -> 0 */
        if (right->type == TERM_ZERO) {
            free_term(t->data.binary.left);
            free(right);
            free(t);
            *changed = true;
            return create_zero();
        }
        /* Аксіома: x · S(y) -> (x · y) + x */
        if (right->type == TERM_SUCC) {
            Term* left = t->data.binary.left;
            Term* y = right->data.child;
            Term* mul_xy = create_mul(copy_term(left), y);
            Term* new_add = create_add(mul_xy, left);
            free(right);
            free(t);
            *changed = true;
            return new_add;
        }
    }

    return t;
}

/* Повне нормалізуюче спрощення терма до нормальної форми Пеано */
Term* normalize(Term* t) {
    bool changed = false;
    do {
        changed = false;
        t = reduce_term(t, &changed);
    } while (changed);
    return t;
}

int main(void) {
    printf("=== Інтерпретатор та редуктор термів арифметики Пеано (C) ===\n\n");

    /* Побудова терма: (x + S(0)) + S(S(0)) */
    Term* x = create_var("x");
    Term* one = create_succ(create_zero());
    Term* two = create_succ(create_succ(create_zero()));
    
    Term* expr = create_add(create_add(x, one), two);

    printf("Початковий терм: ");
    print_term(expr);
    printf("\n");

    expr = normalize(expr);

    printf("Нормалізована форма: ");
    print_term(expr);
    printf("\n\n");

    free_term(expr);
    return 0;
}
```

```cpp
#include <iostream>
#include <memory>
#include <string>
#include <variant>
#include <string_view>

namespace peano {

struct Term;
using TermPtr = std::unique_ptr<Term>;

struct Zero {};
struct Var { std::string name; };
struct Succ { TermPtr child; };
struct Add { TermPtr left; TermPtr right; };
struct Mul { TermPtr left; TermPtr right; };

struct Term {
    std::variant<Zero, Var, Succ, Add, Mul> node;

    explicit Term(Zero z) : node(std::move(z)) {}
    explicit Term(Var v) : node(std::move(v)) {}
    explicit Term(Succ s) : node(std::move(s)) {}
    explicit Term(Add a) : node(std::move(a)) {}
    explicit Term(Mul m) : node(std::move(m)) {}
};

// Фабричні функції
inline TermPtr make_zero() {
    return std::make_unique<Term>(Zero{});
}

inline TermPtr make_var(std::string_view name) {
    return std::make_unique<Term>(Var{std::string(name)});
}

inline TermPtr make_succ(TermPtr child) {
    return std::make_unique<Term>(Succ{std::move(child)});
}

inline TermPtr make_add(TermPtr left, TermPtr right) {
    return std::make_unique<Term>(Add{std::move(left), std::move(right)});
}

inline TermPtr make_mul(TermPtr left, TermPtr right) {
    return std::make_unique<Term>(Mul{std::move(left), std::move(right)});
}

// Рекурсивне глибоке копіювання
inline TermPtr copy_term(const TermPtr& t) {
    if (!t) return nullptr;
    return std::visit([](const auto& arg) -> TermPtr {
        using T = std::decay_t<decltype(arg)>;
        if constexpr (std::is_same_v<T, Zero>) return make_zero();
        else if constexpr (std::is_same_v<T, Var>) return make_var(arg.name);
        else if constexpr (std::is_same_v<T, Succ>) return make_succ(copy_term(arg.child));
        else if constexpr (std::is_same_v<T, Add>) return make_add(copy_term(arg.left), copy_term(arg.right));
        else if constexpr (std::is_same_v<T, Mul>) return make_mul(copy_term(arg.left), copy_term(arg.right));
    }, t->node);
}

// Друк терма
inline void print_term(const TermPtr& t) {
    if (!t) return;
    std::visit([](const auto& arg) {
        using T = std::decay_t<decltype(arg)>;
        if constexpr (std::is_same_v<T, Zero>) {
            std::cout << "0";
        } else if constexpr (std::is_same_v<T, Var>) {
            std::cout << arg.name;
        } else if constexpr (std::is_same_v<T, Succ>) {
            std::cout << "S(";
            print_term(arg.child);
            std::cout << ")";
        } else if constexpr (std::is_same_v<T, Add>) {
            std::cout << "(";
            print_term(arg.left);
            std::cout << " + ";
            print_term(arg.right);
            std::cout << ")";
        } else if constexpr (std::is_same_v<T, Mul>) {
            std::cout << "(";
            print_term(arg.left);
            std::cout << " · ";
            print_term(arg.right);
            std::cout << ")";
        }
    }, t->node);
}

// Однокрокова редукція за аксіомами Пеано
inline TermPtr reduce_step(TermPtr t, bool& changed) {
    if (!t) return nullptr;

    if (auto* s = std::get_if<Succ>(&t->node)) {
        s->child = reduce_step(std::move(s->child), changed);
        return t;
    }

    if (auto* a = std::get_if<Add>(&t->node)) {
        a->left = reduce_step(std::move(a->left), changed);
        a->right = reduce_step(std::move(a->right), changed);

        if (std::holds_alternative<Zero>(a->right->node)) {
            changed = true;
            return std::move(a->left); // x + 0 -> x
        }

        if (auto* s = std::get_if<Succ>(&a->right->node)) {
            changed = true;
            TermPtr left = std::move(a->left);
            TermPtr y = std::move(s->child);
            return make_succ(make_add(std::move(left), std::move(y))); // x + S(y) -> S(x + y)
        }
    }

    if (auto* m = std::get_if<Mul>(&t->node)) {
        m->left = reduce_step(std::move(m->left), changed);
        m->right = reduce_step(std::move(m->right), changed);

        if (std::holds_alternative<Zero>(m->right->node)) {
            changed = true;
            return make_zero(); // x · 0 -> 0
        }

        if (auto* s = std::get_if<Succ>(&m->right->node)) {
            changed = true;
            TermPtr left = std::move(m->left);
            TermPtr y = std::move(s->child);
            TermPtr mul_xy = make_mul(copy_term(left), std::move(y));
            return make_add(std::move(mul_xy), std::move(left)); // x · S(y) -> (x · y) + x
        }
    }

    return t;
}

inline TermPtr normalize(TermPtr t) {
    bool changed = false;
    do {
        changed = false;
        t = reduce_step(std::move(t), changed);
    } while (changed);
    return t;
}

} // namespace peano

int main() {
    using namespace peano;

    std::cout << "=== Інтерпретатор термів арифметики Пеано (C++20 RAII) ===\n\n";

    // Побудова виразу: (x · S(0)) + (y + 0)
    auto expr = make_add(
        make_mul(make_var("x"), make_succ(make_zero())),
        make_add(make_var("y"), make_zero())
    );

    std::cout << "Початковий вираз: ";
    print_term(expr);
    std::cout << "\n";

    expr = normalize(std::move(expr));

    std::cout << "Після символьної редукції PA: ";
    print_term(expr);
    std::cout << "\n\n";

    return 0;
}
```
:::

## 3. Детальний аналіз алгоритмічних рішень та оптимізацій

Порівнюючи дві реалізації, можна виділити фундаментальні парадигмальні відмінності у керуванні ресурсами та синтаксичним деревом:

### 3.1. Керування пам'яттю та RAII
У версії мовою C пам'ять для кожного вузла `Term` виділяється у динамічній пам'яті за допомогою `malloc()`. Це вимагає ретельного написання функції `free_term()`, яка рекурсивно звільняє ліве та праве піддерево. Під час проведення редукції (наприклад, коли терм `x + 0` замінюється на `x`), вузол `0` та батьківський вузол `+` мають бути явно звільнені через `free()`, інакше виникне витік пам'яті (Memory Leak).

У версії C++ використовується концепція RAII (Resource Acquisition Is Initialization) через `std::unique_ptr<Term>`. Деструктори розумних вказівників викликаються автоматично при виході з області видимості чи при переміщенні об'єктів за допомогою `std::move()`. Використання `std::variant` замість сирих `union` гарантує типобезпечність (Type Safety) під час виклику `std::get_if` та `std::holds_alternative`.

### 3.2. Алгоритм підстановки та перевірка індукції
Щоб автоматизувати перевірку індуктивних доведень (наприклад, доведення рівності `∀x (x + 0 = x)`), рушій повинен виконувати такі кроки:
1. **Базовий крок:** Замінити змінну `x` на `0` у лівій та правій частинах рівності. Викликати `normalize()`. Якщо обоє нормалізованих термів є синтаксично рівними (наприклад `0 = 0`), базовий крок підтверджено.
2. **Індукційний крок:** Припустити істинність рівності для `x`. Замінити `x` на `S(x)`. Нормалізувати обидві частини за допомогою `reduce_step()`. Застосувати індукційне припущення для зведення виразу до тотожності.

### 3.3. Обчислювальна складність та крайові випадки

1. **Глибина рекурсії та переповнення стека (Stack Overflow):**
   Обчислення нормальної форми терма на кшталт `S(S(...S(0)...)) + S(S(...S(0)...))` вимагає глибини рекурсивних викликів, пропорційної значенню чисел. Для великих чисел `n > 100000` пряма рекурсія спричиняє переповнення стека викликів. Промислові верифікатори (наприклад, Z3) застосовують ітеративні алгоритми редукції з явним стеком або представлення через термові графи (Directed Acyclic Graphs, DAGs) із мемоізацією (Hash-Consing).

2. **Підстановка з уникненням захоплення змінних (Capture-Avoiding Substitution):**
   При реалізації аксіоми індукції або підстановки термів замість змінних слід контролювати вільні та зв'язані змінні. Якщо формула містить квантори `∀y`, підстановка терма зі змінною `y` може призвести до небажаного «захоплення» змінної.

3. **Завершуваність системи переписування (Termination of Rewriting System):**
   Орієнтовані аксіоми Пеано `x + S(y) -> S(x + y)` та `x · S(y) -> (x · y) + x` утворюють строго канонічну (сильно нормалізовану) систему переписування термів. Будь-який замкнений терм без змінних знижується до унікального нумерала `S(S(...0...))` за скінченне число кроків.

## 4. Оптимізація через термові графи та Hash-Consing

У реальних промислових системах автоматичного доведення теорем (наприклад у Coq, Lean, Z3) представлення термів у вигляді класичного розгалуженого дерева (AST) є занадто марнотратним за пам'яттю. Для числа `1000` дерево містить тисячу вкладених об'єктів `S`, кожен із яких зберігає покажчик та службові заголовки виділення пам'яті.

Щоб оптимізувати обчислення, використовується техніка **Hash-Consing** (або представлення через орієнтовані безциклічні графи DAG):
- Створюється глобальна таблиця хешування всіх створених термів.
- Перед створенням нового вузла (наприклад `create_add(left, right)`) перевіряється, чи існує вже в таблиці терм із такими самими аргументами.
- Якщо такий терм існує, повертається повторно використаний вказівник на вже наявний вузол.
- Перевірка синтаксичної рівності термів `terms_equal(a, b)` за таких умов зводиться до миттєвого порівняння вказівників `a == b` за `O(1)` замість рекурсивного обходу дерева за `O(N)`.

Цей підхід дозволяє зменшити використання пам'яті в сотні разів і робить символьні обчислення в арифметиці Пеано практично ефективними для великих формальних доведень.
