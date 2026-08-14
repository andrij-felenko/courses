# ⚙️ Практика QBF: оцінювач і розв'язувач кванторних булевих формул на C та C++

Алгоритм розв'язувача кванторних булевих формул (Quantified Boolean Formulas, QBF) для рівнів поліноміальної ієрархії Σ₁ᵖ (класична SAT) та Σ₂ᵖ (2-QSAT) ґрунтується на рекурсивному обході кванторного дерева з чергуванням бектрекінгу та раннім відсіканням гілок. При обході кванторного дерева алгоритм послідовно фіксує значення змінних: під квантором існування (∃) використовується логічне АБО з раннім поверненням успіху при першому `true`, а під квантором всезагальності (∀) — логічне І з миттєвим бектрекінгом при першому `false`. Така техніка дає змогу швидко оцінювати складні булеві формули та вибудовувати їхні ідіоматичні реалізації мовами C та C++.

---

## 1. Практична задача, кванторна асиметрія та структура даних

Розглянемо оцінку булевої формули у кон'юнктивній нормальній формі (КНФ) з префіксом чергованих кванторів вигляду:
`Φ = ∃ x₁...xₘ  ∀ y₁...yₙ  ϕ(x₁, ..., xₘ, y₁, ..., yₙ)`

Для обчислення значення такої формули звичайного недетермінованого перебору (як у SAT-розв'язувачах алгоритму DPLL чи CDCL) недостатньо. Причина полягає в фундаментальній **асиметрії кванторів**:

1. **Квантор існування (∃):** Вузол дерева обчислень, що відповідає змінній xᵢ під квантором ∃, реалізує логічну операцію **АБО** (OR). Це означає, що розв'язувачу достатньо знайти **бодай одне** значення (0 або 1) для xᵢ, за якого піддерево оцінюється як `true`. Якщо перша гілка дала `true`, другу гілку можна взагалі не обчислювати (раннє повернення успіху).
2. **Квантор всезагальності (∀):** Вузол дерева обчислень для змінної yⱼ під квантором ∀ реалізує логічну операцію **І** (AND). Це означає, що розв'язувач зобов'язаний пересвідчитися, що **обидві** гілки (і при yⱼ = 0, і при yⱼ = 1) дають значення `true`. Якщо ж хоча б одна з гілок повертає `false`, весь вузол негайно стає `false` (раннє відсікання невдачі).

### Вхідне представлення формули
Булева формула ϕ кодується у КНФ як кон'юнкція (операція І) кількох диз'юнктів. Кожен диз'юнкт є диз'юнкцією (операція АБО) літералів.
Літерал — це або сама змінна `v`, або її заперечення `¬v`. У числових масивах ми позначаємо змінну v цілим додатним числом `v`, а її заперечення `¬v` — від'ємним числом `-v`.

---

## 2. Реалізація мовою C

У реалізації мовою C ми орієнтуємося на максимальну швидкодію, використання неперервних буферів пам'яті, відсутність зайвих динамічних виділень усередині рекурсії та явне управління станами змінних через масив `values`.

:::tabs
```c
/* qsat_solver.c — Ідіоматичний розв'язувач 2-QSAT мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

typedef enum {
    QUANT_EXISTS,
    QUANT_FORALL
} QuantifierType;

typedef struct {
    int variable_id;
    QuantifierType type;
} VariableQuant;

typedef struct {
    int* literals; /* Позитивні значення: variable_id; Негативні: -variable_id */
    size_t size;
} Clause;

typedef struct {
    size_t num_vars;
    size_t num_clauses;
    VariableQuant* quantifiers; /* Масив кванторів у порядку їхнього чергування */
    Clause* clauses;
} QBFFormula;

/* Оцінка одного диз'юнкта при заданому призначенні змінних:
   values[i] = 1 (істина), 0 (хиба), -1 (непризначено) */
static int eval_clause(const Clause* clause, const int* values) {
    bool has_unassigned = false;
    for (size_t i = 0; i < clause->size; ++i) {
        int lit = clause->literals[i];
        int var = abs(lit);
        int val = values[var];
        
        if (val == -1) {
            has_unassigned = true;
        } else {
            bool is_positive = (lit > 0);
            if ((is_positive && val == 1) || (!is_positive && val == 0)) {
                return 1; /* Диз'юнкт істинний */
            }
        }
    }
    return has_unassigned ? -1 : 0; /* -1: ще не визначено, 0: точно хибний */
}

/* Оцінка всієї КНФ формули */
static int eval_formula(const QBFFormula* formula, const int* values) {
    bool has_undef = false;
    for (size_t i = 0; i < formula->num_clauses; ++i) {
        int res = eval_clause(&formula->clauses[i], values);
        if (res == 0) return 0; /* Якщо хоч один диз'юнкт 0, вся КНФ = 0 */
        if (res == -1) has_undef = true;
    }
    return has_undef ? -1 : 1;
}

/* Рекурсивний розв'язувач QSAT з чергуванням кванторів */
static bool solve_qsat_rec(const QBFFormula* formula, size_t var_idx, int* values) {
    int status = eval_formula(formula, values);
    if (status == 1) return true;
    if (status == 0) return false;
    if (var_idx > formula->num_vars) return false;

    int var_id = formula->quantifiers[var_idx - 1].variable_id;
    QuantifierType qtype = formula->quantifiers[var_idx - 1].type;

    if (qtype == QUANT_EXISTS) {
        /* Квантор ∃: Достатньо, щоб хоча б одне значення дало true (АБО) */
        values[var_id] = 0;
        if (solve_qsat_rec(formula, var_idx + 1, values)) {
            values[var_id] = -1;
            return true;
        }
        values[var_id] = 1;
        bool res = solve_qsat_rec(formula, var_idx + 1, values);
        values[var_id] = -1;
        return res;
    } else {
        /* Квантор ∀: Вимагається, щоб ОБИДВА значення дали true (І) */
        values[var_id] = 0;
        if (!solve_qsat_rec(formula, var_idx + 1, values)) {
            values[var_id] = -1;
            return false; /* Раннє відсікання: 0 на першій гілці нищить ∀ */
        }
        values[var_id] = 1;
        bool res = solve_qsat_rec(formula, var_idx + 1, values);
        values[var_id] = -1;
        return res;
    }
}

bool solve_qbf(const QBFFormula* formula) {
    int* values = (int*)malloc((formula->num_vars + 1) * sizeof(int));
    for (size_t i = 0; i <= formula->num_vars; ++i) values[i] = -1;
    
    bool result = solve_qsat_rec(formula, 1, values);
    free(values);
    return result;
}

int main(void) {
    /* Приклад формули: ∃ x1 ∀ y2 [ (x1 OR y2) AND (x1 OR NOT y2) ] */
    QBFFormula f;
    f.num_vars = 2;
    f.num_clauses = 2;

    VariableQuant quants[2] = {
        {1, QUANT_EXISTS},
        {2, QUANT_FORALL}
    };
    f.quantifiers = quants;

    Clause clauses[2];
    int l1[2] = {1, 2};   /* x1 OR y2 */
    int l2[2] = {1, -2};  /* x1 OR NOT y2 */
    clauses[0].literals = l1; clauses[0].size = 2;
    clauses[1].literals = l2; clauses[1].size = 2;
    f.clauses = clauses;

    bool ans = solve_qbf(&f);
    printf("Результат оцінки ∃x1 ∀y2 [(x1 OR y2) AND (x1 OR !y2)]: %s\n", 
           ans ? "TRUE (ІСТИНА)" : "FALSE (ХИБА)");

    return 0;
}
```

```cpp
// qsat_solver.cpp — Ідіоматичний розв'язувач QBF сучасним C++20 (RAII, std::vector, std::span)
#include <iostream>
#include <vector>
#include <cmath>
#include <optional>
#include <span>

enum class Quantifier {
    Exists,
    Forall
};

struct Variable {
    int id;
    Quantifier type;
};

class Clause {
public:
    std::vector<int> literals;

    [[nodiscard]] std::optional<bool> evaluate(std::span<const int> values) const {
        bool has_unassigned = false;
        for (int lit : literals) {
            int var = std::abs(lit);
            int val = values[var];
            if (val == -1) {
                has_unassigned = true;
            } else {
                bool is_positive = (lit > 0);
                if ((is_positive && val == 1) || (!is_positive && val == 0)) {
                    return true; // Диз'юнкт істинний
                }
            }
        }
        if (has_unassigned) return std::nullopt; // Ще не визначено
        return false; // Диз'юнкт хибний
    }
};

class QBFFormula {
public:
    size_t num_vars{0};
    std::vector<Variable> quantifiers;
    std::vector<Clause> clauses;

    [[nodiscard]] std::optional<bool> evaluate(std::span<const int> values) const {
        bool has_undefined = false;
        for (const auto& clause : clauses) {
            auto res = clause.evaluate(values);
            if (res == false) return false;
            if (!res.has_value()) has_undefined = true;
        }
        if (has_undefined) return std::nullopt;
        return true;
    }

    [[nodiscard]] bool solve() const {
        std::vector<int> values(num_vars + 1, -1);
        return solve_recursive(0, values);
    }

private:
    bool solve_recursive(size_t quant_idx, std::vector<int>& values) const {
        auto status = evaluate(values);
        if (status.has_value()) {
            return status.value();
        }
        if (quant_idx >= quantifiers.size()) {
            return false;
        }

        const auto& [var_id, qtype] = quantifiers[quant_idx];

        if (qtype == Quantifier::Exists) {
            // Квантор ∃: АБО двох гілок
            values[var_id] = 0;
            if (solve_recursive(quant_idx + 1, values)) {
                values[var_id] = -1;
                return true;
            }
            values[var_id] = 1;
            bool res = solve_recursive(quant_idx + 1, values);
            values[var_id] = -1;
            return res;
        } else {
            // Квантор ∀: І двох гілок (з раннім відсіканням)
            values[var_id] = 0;
            if (!solve_recursive(quant_idx + 1, values)) {
                values[var_id] = -1;
                return false; // Раннє відсікання
            }
            values[var_id] = 1;
            bool res = solve_recursive(quant_idx + 1, values);
            values[var_id] = -1;
            return res;
        }
    }
};

int main() {
    // Формула: ∃ x1 ∀ y2 [ (x1 OR y2) AND (x1 OR NOT y2) ]
    QBFFormula formula;
    formula.num_vars = 2;
    formula.quantifiers = {
        {1, Quantifier::Exists},
        {2, Quantifier::Forall}
    };
    formula.clauses = {
        Clause{{1, 2}},   // x1 OR y2
        Clause{{1, -2}}   // x1 OR NOT y2
    };

    bool is_satisfiable = formula.solve();
    std::cout << "Результат оцінки ∃x1 ∀y2 [(x1 OR y2) AND (x1 OR !y2)]: "
              << (is_satisfiable ? "TRUE (ІСТИНА)" : "FALSE (ХИБА)") << '\n';

    return 0;
}
```
:::

---

## 3. Детальний трасувальний розбір та аналіз крайових випадків

Щоб глибше зрозуміти, як реалізований алгоритм опрацьовує чергування кванторів, простежмо виклики стека на тестовому прикладі з `main()`:
`Φ = ∃ x₁  ∀ y₂  [ (x₁ ∨ y₂) ∧ (x₁ ∨ ¬y₂) ]`

### Покрокове простеження стека рекурсії:

1. **Крок 1 (Старт):** `solve_recursive(quant_idx = 0)`
   - Стан масиву `values = [-1, -1, -1]`. Формула ще незавершена (`std::nullopt`).
   - Перша змінна x₁ належить квантору `QUANT_EXISTS`.
   - Алгоритм робить першу спробу: припускає `x₁ = 0`.

2. **Крок 2 (Перехід до y₂ при x₁ = 0):** `solve_recursive(quant_idx = 1)`
   - Стан масиву `values = [-1, 0, -1]`. Формула ще не визначена.
   - Друга змінна y₂ належить квантору `QUANT_FORALL`.
   - Квантор ∀ вимагає істинності **обох** гілок. Алгоритм тестує `y₂ = 0`.

3. **Крок 3 (Оцінка гілки x₁ = 0, y₂ = 0):** `solve_recursive(quant_idx = 2)`
   - Стан масиву `values = [-1, 0, 0]`.
   - Диз'юнкт 1 `(x₁ ∨ y₂)` оцінюється в `(0 ∨ 0) = 0` (хиба).
   - Функція `evaluate()` повертає `false`.
   - Повертаємося до Кроку 2 з результатом `false`.

4. **Крок 4 (Відсікання гілки ∀):**
   - Оскільки при `y₂ = 0` вираження дало `false`, для квантора `QUANT_FORALL` операція І вже не може повернути `true`!
   - Алгоритм здійснює **раннє відсікання**: він навіть не пробує варіант `y₂ = 1`.
   - Гілка для `x₁ = 0` завершується з вердиктом `false`.
   - Стан `x₁` скидається назад у `-1`.

5. **Крок 5 (Перехід до x₁ = 1):**
   - Оскільки для квантора ∃ перша гілка (`x₁ = 0`) повернула `false`, алгоритм пробує другу гілку: `x₁ = 1`.
   - Стан `values = [-1, 1, -1]`.
   - Знову заходимо у квантор ∀ для y₂: пробуємо `y₂ = 0`.

6. **Крок 6 (Оцінка гілки x₁ = 1, y₂ = 0):**
   - Стан `values = [-1, 1, 0]`.
   - Диз'юнкт 1 `(1 ∨ 0) = 1`. Диз'юнкт 2 `(1 ∨ 1) = 1`. Вся КНФ = `true`.
   - Гілка `y₂ = 0` повернула `true`.

7. **Крок 7 (Оцінка другої гілки ∀: x₁ = 1, y₂ = 1):**
   - Оскільки перша гілка ∀ дала `true`, квантор ∀ мусить перевірити й другу гілку: `y₂ = 1`.
   - Стан `values = [-1, 1, 1]`.
   - Диз'юнкт 1 `(1 ∨ 1) = 1`. Диз'юнкт 2 `(1 ∨ 0) = 1`. Вся КНФ = `true`.
   - Обидві гілки для y₂ повернули `true`! Квантор ∀ повертає `true`.

8. **Крок 8 (Фінал):**
   - Квантор ∃ для x₁ отримав `true` на гілці `x₁ = 1`.
   - Загальний вердикт формули — **TRUE (ІСТИНА)**.

---

## 4. Складність та специфіка юніт-пропагації для QBF

### Часова та просторова складність
- **Пам'ять:** Обсяг пам'яті дорівнює O(n + m), де n — кількість змінних, m — кількість диз'юнктів. Це підтверджує факт, що розв'язання QBF лежить у межах класу **PSPACE**.
- **Час:** У найгіршому випадку кількість викликів становить O(2ⁿ⁺ᵐ). Проте завдяки ранньому відсіканню гілок на кванторах ∀ дерево перебору істотно скорочується.

### Особливість юніт-пропагації у QBF (Q-Resolution / Universal Reduction)
У класичному SAT розв'язувачах використовується правило **юніт-пропагації**: якщо в диз'юнкті лишився один непризначений літерал, йому миттєво призначається значення 1.

У QBF діє додаткове специфічне правило — **універсальна редукція** (Universal Reduction):
Якщо в диз'юнкті літерал `y` належить квантору ∀, і в цьому диз'юнкті **немає жодних літералів під квантором ∃, які стоять після y в порядку кванторного префіксу**, то літерал `y` можна **вилучити** з диз'юнкту!

Чому? Бо квантор ∀ намагається зробити диз'юнкт хибним. Якщо після y немає жодної існувальної змінної, яка б могла врятувати диз'юнкт, супротивник просто обере таке значення y, яке зробить цей літерал хибним.

Це правило та його аналоги формують основу професійних industrial QBF-розв'язувачів (таких як DepQBF або QuBE), що використовуються в реальній формальній верифікації та логічному синтезі.
