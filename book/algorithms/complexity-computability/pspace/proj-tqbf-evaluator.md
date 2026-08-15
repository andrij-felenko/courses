# ⚙️ Обчислювач кванторних булевих формул (TQBF) у поліномній пам'яті

Ця практична вставка детально розбирає інженерну реалізацію оцінювача кванторних булевих формул (TQBF) у пренексній нормальній формі. На прикладі реальних програмних модулів мовами C та C++ показано, як обчислювальний алгоритм на основі рекурсивного пошуку в глибину (DFS) розв'язує PSPACE-повну задачу, споживаючи лише поліноміальний (і навіть строго лінійний) обсяг оперативної пам'яті відносно кількості змінних `O(N)`.

---

## 1. Концепція алгоритму та аналіз використання ресурсів

Булева формула у пренексній нормальній формі подається у вигляді послідовності кванторів, за якими слідує бескванторне ядро у кон'юнктивній нормальній формі (CNF):
```
Q₁ x₁ Q₂ x₂ ... Qₙ xₙ  ϕ(x₁, x₂, ..., xₙ)
```
де кожен квантор `Qᵢ ∈ {QUANT_EXISTS, QUANT_FORALL}`, а бескванторне ядро `ϕ` є кон'юнкцією клауз (диз'юнкцій літералів).

### 1.1. Стратегія рекурсивної оцінки
Алгоритм будує неявне дерево гри для двох гравців і обчислює значення формули за допомогою зворотного трекінгу (backtracking DFS):

1. **База рекурсії (`depth > N`):** усі змінні від `x₁` до `xₙ` мають фіксовані булеві значення. Алгоритм виконує детерміновану перевірку CNF-ядра: формула істинна тоді й лише тоді, коли у кожній клаузі є бодай один істинний літерал.
2. **Крок існування (`QUANT_EXISTS`):** змінній `x[depth]` послідовно присвоюються значення `false` та `true`. Значення вузла дорівнює `Eval(false) OR Eval(true)`. Застосовується **коротке замикання (short-circuiting)**: якщо при `x[depth] = false` повернено `true`, друга гілка не обчислюється зовсім.
3. **Крок загальності (`QUANT_FORALL`):** змінній `x[depth]` послідовно присвоюються значення `false` та `true`. Значення вузла дорівнює `Eval(false) AND Eval(true)`. Якщо при `x[depth] = false` повернено `false`, друга гілка відсікається за коротким замиканням.

### 1.2. Обсяг споживаної пам'яті
Аналіз використання оперативної пам'яті демонструє принципову перевагу просторової складності:
- **Глибина стеку викликів:** строго обмежена кількістю змінних `N`.
- **Локальний фрейм:** зберігає лише номер поточної змінної `depth` та булевий прапорець призначення.
- **Вектор призначень (assignment):** один спільний масив розміру `N + 1`, який перезаписується при сходженні та зануренні в стек.
- **Загальна додаткова пам'ять:** `O(N)` бітів для стеку рекурсії та вектора призначень.

Хоча кількість листків дерева обчислень у найгіршому випадку дорівнює `2ᴺ`, що вимагає експоненційного часу `O(2ᴺ · |ϕ|)`, оперативна пам'ять залишається строго лінійною `O(N)`.

---

## 2. Реалізація C та C++

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

/* Тип квантора: існування або загальності */
typedef enum {
    QUANT_EXISTS,
    QUANT_FORALL
} QuantifierType;

/* Літерал CNF: змінна var (1-based index) та її полярність (is_pos) */
typedef struct {
    int var;
    bool is_pos;
} Literal;

/* Клауза (диз'юнкція літералів) */
typedef struct {
    Literal* lits;
    size_t count;
} Clause;

/* CNF-формула (кон'юнкція клауз) */
typedef struct {
    Clause* clauses;
    size_t count;
} CNFFormula;

/* Кванторна булева формула в пренексній формі */
typedef struct {
    QuantifierType* quantifiers; /* Масив кванторів розміру num_vars */
    int num_vars;                /* Кількість змінних (1 .. N) */
    CNFFormula cnf;              /* Бескванторне ядро */
} TQBFFormula;

/* Перевірка істинності CNF-формули при заданому призначенні змінних assignment */
static bool evaluate_cnf(const CNFFormula* cnf, const bool* assignment) {
    for (size_t i = 0; i < cnf->count; ++i) {
        const Clause* clause = &cnf->clauses[i];
        bool clause_sat = false;
        
        for (size_t j = 0; j < clause->count; ++j) {
            int var = clause->lits[j].var;
            bool is_pos = clause->lits[j].is_pos;
            bool val = assignment[var];
            
            if ((is_pos && val) || (!is_pos && !val)) {
                clause_sat = true;
                break;
            }
        }
        
        if (!clause_sat) {
            return false; /* Знайдено незадоволену клаузу */
        }
    }
    return true; /* Усі клаузи задоволені */
}

/* Рекурсивна оцінка TQBF у поліномній пам'яті (стек рекурсії = O(num_vars)) */
static bool evaluate_tqbf_recursive(const TQBFFormula* f, int depth, bool* assignment) {
    /* База рекурсії: усі змінні від 1 до num_vars призначені */
    if (depth > f->num_vars) {
        return evaluate_cnf(&f->cnf, assignment);
    }
    
    QuantifierType q = f->quantifiers[depth - 1];
    
    /* Спроба 1: призначення var = false */
    assignment[depth] = false;
    bool res_false = evaluate_tqbf_recursive(f, depth + 1, assignment);
    
    /* Коротке замикання затискає обчислення гілок */
    if (q == QUANT_EXISTS && res_false) {
        return true;
    }
    if (q == QUANT_FORALL && !res_false) {
        return false;
    }
    
    /* Спроба 2: призначення var = true */
    assignment[depth] = true;
    bool res_true = evaluate_tqbf_recursive(f, depth + 1, assignment);
    
    if (q == QUANT_EXISTS) {
        return res_false || res_true;
    } else {
        return res_false && res_true;
    }
}

/* Головний інтерфейс оцінювача TQBF */
bool evaluate_tqbf(const TQBFFormula* f) {
    /* Пам'ять під стек призначень: 1..num_vars (O(N) додаткової пам'яті) */
    bool* assignment = (bool*)calloc((size_t)(f->num_vars + 1), sizeof(bool));
    if (!assignment) return false;
    
    bool result = evaluate_tqbf_recursive(f, 1, assignment);
    free(assignment);
    return result;
}

int main(void) {
    /* Приклад TQBF: ∃x₁ ∀x₂ ((x₁ ∨ x₂) ∧ (x₁ ∨ ¬x₂)) */
    QuantifierType quants[2] = { QUANT_EXISTS, QUANT_FORALL };
    
    Literal c1_lits[2] = { {1, true}, {2, true} };
    Literal c2_lits[2] = { {1, true}, {2, false} };
    
    Clause clauses[2] = {
        { c1_lits, 2 },
        { c2_lits, 2 }
    };
    
    TQBFFormula formula = {
        .quantifiers = quants,
        .num_vars = 2,
        .cnf = { clauses, 2 }
    };
    
    bool is_true = evaluate_tqbf(&formula);
    printf("Формула ∃x₁ ∀x₂ ((x₁ ∨ x₂) ∧ (x₁ ∨ ¬x₂)) є: %s\n",
           is_true ? "ІСТИННОЮ (True)" : "ХИБНОЮ (False)");
           
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <memory>
#include <span>
#include <string_view>

enum class Quantifier {
    Exists,
    Forall
};

struct Literal {
    int var;        // Індекс змінної (1-based)
    bool is_pos;    // true = x, false = ¬x
};

using Clause = std::vector<Literal>;

struct CNFFormula {
    std::vector<Clause> clauses;

    [[nodiscard]] bool evaluate(std::span<const bool> assignment) const {
        for (const auto& clause : clauses) {
            bool clause_sat = false;
            for (const auto& lit : clause) {
                const bool val = assignment[lit.var];
                if ((lit.is_pos && val) || (!lit.is_pos && !val)) {
                    clause_sat = true;
                    break;
                }
            }
            if (!clause_sat) {
                return false;
            }
        }
        return true;
    }
};

class TQBFEvaluator {
public:
    TQBFEvaluator(std::vector<Quantifier> quantifiers, CNFFormula cnf)
        : quantifiers_(std::move(quantifiers)), cnf_(std::move(cnf)) {}

    [[nodiscard]] bool evaluate() const {
        // Запитуємо O(N) пам'яті під виділені значення змінних
        std::vector<bool> assignment(quantifiers_.size() + 1, false);
        return evaluate_step(1, assignment);
    }

private:
    std::vector<Quantifier> quantifiers_;
    CNFFormula cnf_;

    bool evaluate_step(size_t depth, std::span<bool> assignment) const {
        if (depth > quantifiers_.size()) {
            return cnf_.evaluate(assignment);
        }

        const Quantifier q = quantifiers_[depth - 1];

        // Гілка 1: var = false
        assignment[depth] = false;
        const bool res_false = evaluate_step(depth + 1, assignment);

        // Оптимізація короткого замикання (Short-circuit evaluation)
        if (q == Quantifier::Exists && res_false) {
            return true;
        }
        if (q == Quantifier::Forall && !res_false) {
            return false;
        }

        // Гілка 2: var = true
        assignment[depth] = true;
        const bool res_true = evaluate_step(depth + 1, assignment);

        if (q == Quantifier::Exists) {
            return res_false || res_true;
        } else {
            return res_false && res_true;
        }
    }
};

int main() {
    // Приклад TQBF: ∃x₁ ∀x₂ ((x₁ ∨ x₂) ∧ (x₁ ∨ ¬x₂))
    std::vector<Quantifier> quants = { Quantifier::Exists, Quantifier::Forall };
    
    CNFFormula cnf;
    cnf.clauses = {
        { Literal{1, true}, Literal{2, true} },   // (x₁ ∨ x₂)
        { Literal{1, true}, Literal{2, false} }   // (x₁ ∨ ¬x₂)
    };

    TQBFEvaluator evaluator(std::move(quants), std::move(cnf));
    const bool result = evaluator.evaluate();

    std::cout << "Формула ∃x₁ ∀x₂ ((x₁ ∨ x₂) ∧ (x₁ ∨ ¬x₂)) є: "
              << (result ? "ІСТИННОЮ (True)" : "ХИБНОЮ (False)") << "\n";

    return 0;
}
```
:::

---

## 3. Інженерні оптимізації та практичні застереження

### 3.1. Обмеження програмного стеку викликів (Call Stack Overflow)
У навчальному прикладі вище рекурсія спирається на системний стек викликів функцій. Для великих формул із `N > 100 000` змінних цей підхід призведе до переповнення стеку потоку (`stack overflow`), адже системний стек зазвичай обмежений 2–8 мегабайтами в більшості операційних систем.

Промислові QSAT-сольвери (такі як DepQBF або QuBE) замінюють системну рекурсію явним стеком у купі (heap stack). Вони зберігають вектор системного стану розміром `N` елементів, де кожен елемент містить лише 2 біти (стан перебору змінної: `UNVISITED`, `TRIED_FALSE`, `TRIED_TRUE`). Це дозволяє аналізувати формули мільйонної розмірності у фіксованому масиві пам'яті.

### 3.2. Навчання на конфліктах та Q-резолюція (Q-Resolution & QCDCL)
Чистий хронологічний DFS відвідує гілки, які не впливають на результат (наприклад, якщо змінні `x₅` та `x₆` взагалі не входять у незадоволені клаузи). Реальні сольвери поєднують поліномну пам'ять із технікою QCDCL (Quantified Conflict-Driven Clause Learning):
- При виявленні незадоволеної клаузи або тупикової гілки аналізується граф причинності конфлікту.
- Алгоритм застосовує правила **Q-резолюції** (видалення універсальних літералів із крайніх позицій кванторного префікса) та генерує нову кубу чи клаузу конфлікту.
- Програма здійснює нехронологічне відкочування (non-chronological backtracking) одразу на кілька рівнів стеку вгору, минаючи нерелевантні квантори.

### 3.3. Евристики вибору змінних (Variable Selection Heuristics)
Оскільки чергування кванторів вимагає строго дотримуватися порядку префікса для різних блоків (`∃` перед `∀`), у межах одного блоку однойменних кванторів (наприклад, `∃x₁ ∃x₂ ∃x₃`) сольвер має свободу обирати порядок гілкування.
- Використовують евристику Jeroslow-Wang для QBF, яка оцінює вагу змінної за частотою її появи у найкоротших клаузах.
- Змінна з найбільшим ваговим коефіцієнтом випробовується першою, що суттєво прискорює спрацьовування короткого замикання (`short-circuiting`).

### 3.4. Очищення та вирівнювання пам'яті (Memory Alignment & Bitsets)
Для досягнення максимальної продуктивності вектор булевих призначень `std::vector<bool>` у C++ реалізований як бітовий масив, де один біт відповідає одній змінній. При аналізі формули з 64 змінними весь вектор розміщується у єдиному 64-бітному регістрі процесора `uint64_t`.

Це дозволяє здійснювати перевірку виконання клауз за допомогою швидких побітових інструкцій `AND`, `OR`, `NOT` та інструкцій підрахунку встановлених бітів (POPCNT), що прискорює виконання оцінювача у десятки разів без будь-якої додаткової витрати оперативної пам'яті.

### 3.5. Принцип перезапису в дії
Найважливіший висновок реалізації — нульова динамічна алокація під час пошуку. Після ініціалізації вектора `assignment` програма не виконує жодного виклику `malloc` чи `new`. Уся робота полягає в модифікації значень у вже виділених комірках пам'яті, що в точності втілює теоретичну модель поліномного простору PSPACE.

### 3.6. Парсинг форматів QDIMACS
У промислових застосуваннях формули TQBF задають у стандартному текстовому форматі QDIMACS. Формат починається з рядка специфікації `p cnf <vars> <clauses>`, за яким слідують кванторні префікси `e 1 3 0` (існує x₁, x₃) та `a 2 4 0` (для всіх x₂, x₄), після чого перелічуються клаузи у вигляді чисел з нулем наприкінці. Наш алгоритм легко розширюється завантажувачем QDIMACS, оскільки вся структура кванторів та CNF-клауз зберігається у вхідному AST-дереві, не збільшуючи обсяг пам'яті для самого рекурсивного обчислювача.
