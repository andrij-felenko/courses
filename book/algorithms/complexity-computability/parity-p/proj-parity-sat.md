# ⚙️ Алгоритм: Моделювання ⊕SAT та перевірка парності свідків

Задача **⊕SAT (Parity-SAT)** полягає у визначенні парності (mod 2) кількості здійсненних наборів булевої формули. На відміну від звичайного алгоритму DPLL для стандарної проблеми SAT, який зупиняється одразу при знаходженні першого-ліпшого свідка, лічильник парності ⊕P мусить обчислити суму за модулем 2 усіх привалюючих гілок обчислювального дерева.

## Ідея алгоритму та алгебраїчне звуження простору розв'язків

Алгоритм обчислення ⊕SAT поєднує рекурсивне розгалуження за змінними з двома потужними алгебраїчними спрощеннями:
1. **Поширення одиничних диз'юнктів (Unit Propagation):** Якщо диз'юнкт містить лише одну змінну, її значення фіксується однозначно, що негайно скорочує простір пошуку.
2. **Алгебраїчне зведення за модулем 2 (GF(2) Elimination):** Диз'юнкти виразу XOR (такі як `x₁ ⊕ x₂ ⊕ ... ⊕ xₖ = c`) обробляються за допомогою Гауссового виключення змінних над скінченним полем `𝔽₂`. Це дає змогу миттєво знаходити суперечності або зменшувати кількість вільних змінних без експоненційного розгалуження.

Якщо формула після чергового спрощення розпадається на `v` повністю вільних незадіяних змінних, які не входять до жодного диз'юнкта, то кількість розв'язків цієї підформули дорівнює `2ᵛ`. При обчисленні за модулем 2 виконується важливе алгебраїчне спрощення:
- Якщо `v > 0`, то `2ᵛ ≡ 0 (mod 2)`, тобто ця гілка дає парну кількість розв'язків і взагалі не змінює загальну парність! Її можна негайно відсікти.
- Якщо `v = 0`, то `2⁰ = 1 ≡ 1 (mod 2)`, тобто гілка дає рівно 1 розв'язок.

Ця властивість робить ⊕SAT в чомусь простішим за точний підрахунок #SAT: парність степенів двійки зникає за модулем 2, дозволяючи відтинати велетенські піддерева обчислень.

## Детальний розбір обчислювального простеження (Execution Trace)

Розглянемо покрокове виконання алгоритму ⊕SAT для прикладної булевої формули з трьома змінними:

```
Φ = (x₁ ∨ x₂) ∧ (¬x₁ ∨ x₃) ∧ (x₂ ∨ ¬x₃)
```

Обчислимо парність кількості її моделей за допомогою обчислювального дерева рекурсії:

1. **Початковий стан:** Змінна `x₁` обирається для розгалуження.
2. **Ліва гілка (`x₁ = 0`):**
   - Диз'юнкт `(x₁ ∨ x₂)` спрощується до одиничного диз'юнкт `(x₂)`. Це форсує значення `x₂ = 1`.
   - Диз'юнкт `(¬x₁ ∨ x₃)` стає істинним за рахунок `¬x₁ = 1` і знімається.
   - Диз'юнкт `(x₂ ∨ ¬x₃)` стає істинним за рахунок `x₂ = 1` і знімається.
   - Змінна `x₃` залишається вільною (`v = 1`). Оскільки `x₃` вільна, кількість розв'язків у цій гілці дорівнює `2¹ = 2`.
   - Парність лівої гілки: `2 mod 2 = 0`.
3. **Права гілка (`x₁ = 1`):**
   - Диз'юнкт `(x₁ ∨ x₂)` стає істинним за рахунок `x₁ = 1` і знімається.
   - Диз'юнкт `(¬x₁ ∨ x₃)` спрощується до одиничного диз'юнкт `(x₃)`. Це форсує значення `x₃ = 1`.
   - Диз'юнкт `(x₂ ∨ ¬x₃)` підстановкою `x₃ = 1` спрощується до `(x₂ ∨ 0) = (x₂)`. Це форсує значення `x₂ = 1`.
   - Усі диз'юнкти задоволені, вільних змінних немає (`v = 0`). Отримуємо рівно `2⁰ = 1` свідок (`x₁=1, x₂=1, x₃=1`).
   - Парність правої гілки: `1 mod 2 = 1`.
4. **Загальний результат:**
   ```
   Parity(Φ) = (Left_Parity ⊕ Right_Parity) = 0 ⊕ 1 = 1
   ```
   Загальна кількість розв'язків дорівнює 3 (що є непарним числом), і алгоритм повертає біт `1`.

## Програмна реалізація лічильника ⊕SAT

Нижче наведено робочу реалізацію алгоритму перевірки парності розв'язків булевих формул та лінійних обмежень над `𝔽₂` двома мовами — C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#define MAX_VARS 32
#define MAX_CLAUSES 64

typedef struct {
    int vars[MAX_VARS];
    int len;
} Clause;

typedef struct {
    Clause clauses[MAX_CLAUSES];
    int num_clauses;
    int num_vars;
} Formula;

/* Створення нової порожньої формули */
Formula* formula_create(int num_vars) {
    Formula* f = (Formula*)malloc(sizeof(Formula));
    if (!f) return NULL;
    f->num_vars = num_vars;
    f->num_clauses = 0;
    return f;
}

/* Додавання диз'юнкта до формули */
void formula_add_clause(Formula* f, const int* literals, int len) {
    if (f->num_clauses >= MAX_CLAUSES) return;
    Clause* c = &f->clauses[f->num_clauses++];
    c->len = len;
    for (int i = 0; i < len; i++) {
        c->vars[i] = literals[i];
    }
}

/* Звільнення пам'яті */
void formula_free(Formula* f) {
    free(f);
}

/* Рекурсивний обчислювач парності ⊕SAT (mod 2) */
int solve_parity_sat_rec(Formula* f, int var_idx, int* assignment) {
    if (var_idx > f->num_vars) {
        /* Перевірка, чи всі диз'юнкти істинні при даному присвоєнні */
        for (int i = 0; i < f->num_clauses; i++) {
            bool clause_sat = false;
            for (int j = 0; j < f->clauses[i].len; j++) {
                int lit = f->clauses[i].vars[j];
                int var = (lit > 0) ? lit : -lit;
                bool val = (assignment[var] == 1);
                if (lit < 0) val = !val;
                if (val) {
                    clause_sat = true;
                    break;
                }
            }
            if (!clause_sat) return 0; /* Нездійсненна гілка */
        }
        return 1; /* Здійсненний свідок (+1 mod 2) */
    }

    /* Розгалуження за змінною var_idx: присвоєння 0 та 1 */
    assignment[var_idx] = 0;
    int left_parity = solve_parity_sat_rec(f, var_idx + 1, assignment);

    assignment[var_idx] = 1;
    int right_parity = solve_parity_sat_rec(f, var_idx + 1, assignment);

    /* Додавання за модулем 2 (операція XOR) */
    return (left_parity ^ right_parity);
}

/* Головна функція обчислення парності ⊕SAT */
int compute_parity_sat(Formula* f) {
    int assignment[MAX_VARS + 1];
    memset(assignment, 0, sizeof(assignment));
    return solve_parity_sat_rec(f, 1, assignment);
}

int main(void) {
    /* Формула: (x1 OR x2) AND (NOT x1 OR x3) AND (x2 OR NOT x3) */
    Formula* f = formula_create(3);
    
    int c1[] = {1, 2};
    int c2[] = {-1, 3};
    int c3[] = {2, -3};

    formula_add_clause(f, c1, 2);
    formula_add_clause(f, c2, 2);
    formula_add_clause(f, c3, 2);

    int parity = compute_parity_sat(f);
    printf("Кількість розв'язків непарна? %s (Parity = %d)\n",
           parity ? "ТАК" : "НІ", parity);

    formula_free(f);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <numeric>
#include <span>
#include <memory>
#include <array>

class Formula {
public:
    using Literal = int; // >0 для позитивної змінної, <0 для заперечення
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

class ParitySatSolver {
public:
    explicit ParitySatSolver(const Formula& formula)
        : formula_(formula), assignment_(formula.num_vars() + 1, 0) {}

    // Обчислює парність кількості розв'язків (0 = парна, 1 = непарна)
    [[nodiscard]] int solve_parity() {
        return solve_recursive(1);
    }

private:
    int solve_recursive(size_t var_idx) {
        if (var_idx > formula_.num_vars()) {
            return check_assignment() ? 1 : 0;
        }

        // Гілка 0
        assignment_[var_idx] = 0;
        int left = solve_recursive(var_idx + 1);

        // Гілка 1
        assignment_[var_idx] = 1;
        int right = solve_recursive(var_idx + 1);

        // Додавання за модулем 2 (XOR)
        return left ^ right;
    }

    [[nodiscard]] bool check_assignment() const {
        for (const auto& clause : formula_.clauses()) {
            bool clause_sat = false;
            for (int lit : clause) {
                size_t var = static_cast<size_t>(std::abs(lit));
                bool val = (assignment_[var] == 1);
                if (lit < 0) val = !val;
                if (val) {
                    clause_sat = true;
                    break;
                }
            }
            if (!clause_sat) return false;
        }
        return true;
    }

    const Formula& formula_;
    std::vector<int> assignment_;
};

int main() {
    Formula f(3);
    f.add_clause(std::array<int, 2>{1, 2});
    f.add_clause(std::array<int, 2>{-1, 3});
    f.add_clause(std::array<int, 2>{2, -3});

    ParitySatSolver solver(f);
    int parity = solver.solve_parity();

    std::cout << "Parity of satisfying assignments (mod 2): " << parity << '\n';
    std::cout << "Is odd: " << (parity == 1 ? "YES" : "NO") << '\n';

    return 0;
}
```
:::

## Складність, оптимізації та практичні підводні камені

Часова складність базового рекурсивного перебору ⊕SAT становить `O(2ⁿ · |Φ|)`, де `n` — кількість змінних, а `|Φ|` — розмір булевої формули.

Проте практичні алгоритми обчислення ⊕P застосовують чотири ключові оптимізації, які дозволяють розв'язувати промислові екземпляри формул:
1. **Інтеграція Гауссового виключення (Gauss-Jordan elimination над 𝔽₂):** Булеві формули часто містять розширення лінійних рівнянь XOR. Замість рекурсивного розгалуження за кожною змінною, ці рівняння зводяться до східчастої форми за поліноміальний час `O(n³)`. Ранг отриманої матриці над `𝔽₂` дає точну кількість розв'язків безпосередньо у вигляді `2ⁿ⁻ʳᵃⁿᵏ`.
2. **Апаратна векторація бітових масивів (SIMD Bit-parallelism):** На низькому рівні операції додавання за модулем 2 над бітовими вектором-рядками реалізуються за допомогою апаратних інструкцій SIMD/AVX2 (`_mm256_xor_si256`), що дозволяє обробляти по 256 бітів за один такт процесора. У поєднанні з оптимізаціями кешу процесора це дає прискорення обчислень у десятки разів на великих бітових матрицях.
3. **Кешування компонент (Component Caching):** Якщо під час розгалуження формула розпадається на декілька незалежних графів змінних, парність кожної компоненти обчислюється окремо. Загальна кількість моделей є добутком кількостей моделей компонент `N = N₁ · N₂`. Для парності це означає:
   ```
   Parity(N) = Parity(N₁) AND Parity(N₂)
   ```
   Тобто загальна кількість розв'язків непарна тоді й лише тоді, коли непарною є кількість розв'язків **кожної** незалежної компоненти.
4. **Обрізання за непарністю степенів 2:** Будь-який підпростір розв'язків розмірності `d ≥ 1` містить парне число елементів `2ᵈ`, тому його парність за модулем 2 дорівнює нулю. Це дозволяє негайно повертати `0` для всіх піддерев, що містять вільні незв'язані змінні.

Крайові випадки обчислювача ⊕SAT включають обробку порожніх формул та формул із суперечностями:
- Формула з 0 диз'юнктів має `2ⁿ` розв'язків (усі набори є моделями). При `n ≥ 1` парність дорівнює `0`, при `n = 0` (порожня формула без змінних) — `1`.
- Формула з порожнім диз'юнктом (`()`) є несумісною, містить `0` розв'язків, отже її парність дорівнює `0`.

Завдяки цим алгебраїчним властивостям обчислення парності ⊕P у багатьох комбінаторних структурованих задачах виконується значно швидше, ніж повний точний підрахунок кількості розв'язків #P. Векторизація XOR дає змогу швидко знаходити базис ядра відображення у реальних системах.
