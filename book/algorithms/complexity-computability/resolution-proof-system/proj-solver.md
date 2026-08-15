# ⚙️ Алгоритм резолюційного спростування та вивід конфліктних диз'юнктів

Алгоритмічна реалізація системи резолюційних виводів вимагає точних структур даних для швидкого пошуку комплементарних літералів, формування нових резольвент та усунення дубльованих або тавтологічних диз'юнктів. Програмний модуль резолюційного спростування є 핵심 осередком систем автоматичного доведення теорем (Automated Theorem Proving) та розв'язувачів проблеми здійсненності булевих формул (SAT solvers). 

У цій вставці наведено вичерпний теоретичний та практичний розбір алгоритмів резолюції, деталізовано структури даних, простежено виконання на тестових КНФ-формулах та надано закончену реалізацію мовами C та C++.

## 1. Архітектура структур даних та репрезентація літералів

Для забезпечення найвищої швидкості обчислень у пам'яті комп'ютера змінні та літерали подаються у вигляді цілих чисел зі знаком (Signed Integers):
- Булева змінна `x_v` (де `v ∈ {1, 2, ..., N}`) подається додатним цілим числом `+v`.
- Заперечення змінної `¬x_v` подається від'ємним цілим числом `-v`.
- Значення `0` використовується як термінатор списку літералів або маркер порожнього диз'юнкта `⊥`.

Диз'юнкт описується як динамічний або статичний масив унікальних літералів, впорядкованих за абсолютним значенням змінних. Така репрезентація дає змогу виконувати порівняння двох дизюнктів на рівність за лінійний час від довжини диз'юнкта.

### Механізм нормалізації диз'юнкта

Кожен новий диз'юнкт, згенерований у результаті резолюції, проходить обов'язковий етап нормалізації, що складається з трьох послідовних кроків:
1. **Сортування літералів**: літерали впорядковуються за зростанням модуля змінної `|v|`. При однакових модулях додатний літерал `+v` передує від'ємному `-v`.
2. **Усунення дублікатів**: якщо диз'юнкт містить одинаковий літерал двічі (`x_v ∨ x_v`), другий екземпляр вилучається, оскільки за законом ідемпотентності диз'юнкція однакових виразів еквівалентна самому виразу.
3. **Виявлення тавтологій**: якщо диз'юнкт містить паралельно позитивний та негативний літерали однієї й тієї самої змінної (`x_v` та `¬x_v`), такий диз'юнкт є тотожно істинним. Тавтології не несуть інформації для шуканого спростування і негайно відкидаються розв'язувачем.

Сортування літералів виконується у мові C за допомогою стандартної функції `qsort`, а у мові C++ за допомогою `std::sort` з власною лямбда-функцією компаратора. Після сортування дублікати та протилежні літерали виявляються за один лінійний прохід.

## 2. Покроковий алгоритм резолюційного насичення (Resolution Saturation)

Класичний алгоритм резолюційного спростування працює за методом насичення (Saturation Algorithm). На вхід подається початкова КНФ-формула `F`. Алгоритм циклічно генерує всі можливі нові резольвенти між парами дизюнктів з поточного басейну `F`.

Послідовність дій на кожній ітерації насичення:
1. Перебираються всі пари дизюнктів `C_i` та `C_j` з басейну.
2. Для кожного можливого pivot-значення змінної `v` перевіряється умова резолюції: `v ∈ C_i` та `-v ∈ C_j` (або навпаки).
3. Якщо умова виконується, обчислюється резольвента `Res = (C_i \ {v}) ∪ (C_j \ {-v})`.
4. Отримана резольвента нормалізується. Якщо результат є порожнім диз'юнктом `⊥` (`size == 0`), алгоритм негайно зупиняється з результатом `UNSAT` (формула нездійсненна).
5. Якщо резольвента не є тавтологією і відсутня у басейні `F`, вона додається до списку нових дизюнктів.
6. Ітерація завершується. Якщо на поточній ітерації не додано жодного нового диз'юнкта, процес зупиняється з результатом `SAT` (формула здійсненна, спростування `⊥` неможливе).

Обчислювальна складність наївного алгоритму насичення становить `O(2^n)` у найгіршому випадку, оскільки кількість виведених диз'юнктів може зростати експоненційно від кількості змінних. Для оптимізації пошуку пари дизюнктів у реальних розв'язувачах використовуються індексовані списки суміжності для кожного літерала, що дозволяє миттєво знаходити диз'юнкти з протилежною полярністю `¬v`.

## 3. Вивід конфліктного диз'юнкта 1UIP в алгоритмах CDCL

У сучасних CDCL SAT-розв'язувачах насичення замінюється цілеспрямованим виводом конфліктних диз'юнктів за допомогою **імпликаційного графа** (Implication Graph).

Коли поширення одиничних літералів (Unit Propagation) спричиняє конфлікт (наприклад, змінна `x₅` вимушено отримує значення 1 за диз'юнктом `C₁`, і значення 0 за диз'юнктом `C₂`), розв'язувач виконує зворотну резолюцію:
1. За початковий диз'юнкт приймається диз'юнкт конфлікту `C_{conflict}`.
2. Знаходиться літерал `l`, який був виведений останнім на поточному рівні прийняття рішень, та його диз'юнкт-причина `C_{reason}`.
3. Обчислюється резольвента `Res(C_{conflict}, C_{reason})` за змінною літерала `l`.
4. Процес повторюється доти, доки резольвента не міститиме лише один літерал з поточного рівня прийняття рішень (Перша точка унікальної імпликації — 1UIP). Отриманий конфліктний диз'юнкт додається до бази даних, і виконується невимогальний хронологічний відкат (non-chronological backtracking).

Побудова конфліктного диз'юнкта 1UIP гарантує, що виведений диз'юнкт буде асертивним: після відкату на рівень рішення він негайно перетворюється на одиничний диз'юнкт і вимушує нове значення змінної, запобігаючи повторному потраплянню розв'язувача у ту саму суперечливу область простору пошуку.

## 4. Порівняльний аналіз реалізацій мовами C та C++

Реалізація мовою C орієнтована на мінімальний оверхед пам'яті та максимальну швидкість виконання. Вона використовує статичні масиви фіксованого розміру для зберження диз'юнктів, що усуває динамічне виділення пам'яті у внутрішньому циклі резолюційного насичення. Для нормалізації застосовується функція `qsort`, а порівняння здійснюється прямою ітерацією по масиву цілих чисел.

Реалізація мовою C++ спирається на сучасні стандарти C++17 та принципи RAII. Диз'юнкти обгортаються у клас `Clause`, який автоматично нормалізує літерали при конструюванні. База даних диз'юнктів зберігається у `std::set<Clause>`, що забезпечує автоматичне усунення дублікатів диз'юнктів та пошук за логарифмічний час `O(log M)`. Повернення результату резолюції через `std::optional<Clause>` дозволяє елегантно обробляти випадки, коли резолюція є неможливою або дає тавтологію, не вдаючись до використання спеціальних маркерних значень чи винятків.

## 5. Закончена програма мовами C та C++

Нижче наведено закончений вихідний код обидвома мовами, який компілюється стандартними засобами (`gcc -std=c11` або `g++ -std=c++17`) та виконує резолюційне спростування тестових КНФ-формул.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

#define MAX_LITS_PER_CLAUSE 64
#define MAX_CLAUSES 1024

// Структура диз'юнкта
typedef struct {
    int lits[MAX_LITS_PER_CLAUSE];
    size_t size;
} Clause;

// Структура формули КНФ
typedef struct {
    Clause clauses[MAX_CLAUSES];
    size_t count;
} CNFFormula;

// Допоміжна функція порівняння для qsort
static int compare_literals(const void *a, const void *b) {
    int l1 = *(const int *)a;
    int l2 = *(const int *)b;
    if (abs(l1) != abs(l2)) return abs(l1) - abs(l2);
    return l1 - l2;
}

// Нормалізація диз'юнкта: сортування та вилучення дублікатів
// Повертає false, якщо диз'юнкт є тавтологією (містить x і -x)
bool normalize_clause(Clause *c) {
    if (c->size <= 1) return true;
    
    qsort(c->lits, c->size, sizeof(int), compare_literals);
    
    size_t new_size = 0;
    for (size_t i = 0; i < c->size; i++) {
        if (i > 0 && c->lits[i] == c->lits[i - 1]) {
            continue; // Дублікат літерала
        }
        if (i > 0 && c->lits[i] == -c->lits[i - 1]) {
            return false; // Тавтологія: містить y та -y
        }
        c->lits[new_size++] = c->lits[i];
    }
    c->size = new_size;
    return true;
}

// Перевірка, чи диз'юнкт є порожнім ⊥
bool is_empty_clause(const Clause *c) {
    return c->size == 0;
}

// Перевірка рівності двох диз'юнктів
bool clauses_equal(const Clause *c1, const Clause *c2) {
    if (c1->size != c2->size) return false;
    for (size_t i = 0; i < c1->size; i++) {
        if (c1->lits[i] != c2->lits[i]) return false;
    }
    return true;
}

// Виконання резолюції між c1 та c2 за змінною pivot_var (pivot_var > 0)
// Повертає true, якщо резольвента створена успішно і не є тавтологією
bool resolve_clauses(const Clause *c1, const Clause *c2, int pivot_var, Clause *out_res) {
    bool found_pos = false, found_neg = false;
    
    // Перевіряємо полярність pivot у c1 та c2
    for (size_t i = 0; i < c1->size; i++) {
        if (c1->lits[i] == pivot_var) found_pos = true;
        if (c1->lits[i] == -pivot_var) found_neg = true;
    }
    bool c2_pos = false, c2_neg = false;
    for (size_t i = 0; i < c2->size; i++) {
        if (c2->lits[i] == pivot_var) c2_pos = true;
        if (c2->lits[i] == -pivot_var) c2_neg = true;
    }
    
    if (!((found_pos && c2_neg) || (found_neg && c2_pos))) {
        return false; // Немає комплементарної пари за pivot_var
    }
    
    out_res->size = 0;
    
    // Копіюємо літерали з c1, крім pivot
    for (size_t i = 0; i < c1->size; i++) {
        if (abs(c1->lits[i]) != pivot_var) {
            out_res->lits[out_res->size++] = c1->lits[i];
        }
    }
    // Копіюємо літерали з c2, крім pivot
    for (size_t i = 0; i < c2->size; i++) {
        if (abs(c2->lits[i]) != pivot_var) {
            if (out_res->size >= MAX_LITS_PER_CLAUSE) return false;
            out_res->lits[out_res->size++] = c2->lits[i];
        }
    }
    
    return normalize_clause(out_res);
}

// Перевірка, чи міститься диз'юнкт у формулі
bool formula_contains(const CNFFormula *formula, const Clause *c) {
    for (size_t i = 0; i < formula->count; i++) {
        if (clauses_equal(&formula->clauses[i], c)) return true;
    }
    return false;
}

// Головний алгоритм резолюційного спростування (насичення)
// Повертає true, якщо формула НЕЗДІЙСНЕННА (виведено ⊥)
bool resolution_refute(CNFFormula *formula, int max_variables) {
    printf("[Спростування] Початкова кількість диз'юнктів: %zu\n", formula->count);
    
    // Нормалізуємо початкові диз'юнкти
    size_t valid_cnt = 0;
    for (size_t i = 0; i < formula->count; i++) {
        if (normalize_clause(&formula->clauses[i])) {
            if (is_empty_clause(&formula->clauses[i])) {
                printf("[Резолюція] Знайдено порожній диз'юнкт у початковій КНФ!\n");
                return true;
            }
            formula->clauses[valid_cnt++] = formula->clauses[i];
        }
    }
    formula->count = valid_cnt;

    size_t added_in_pass = 1;
    size_t pass = 1;

    while (added_in_pass > 0) {
        added_in_pass = 0;
        size_t current_count = formula->count;
        printf("--- Ітерація насичення %zu (диз'юнктів: %zu) ---\n", pass++, current_count);

        for (size_t i = 0; i < current_count; i++) {
            for (size_t j = i + 1; j < current_count; j++) {
                for (int v = 1; v <= max_variables; v++) {
                    Clause res;
                    if (resolve_clauses(&formula->clauses[i], &formula->clauses[j], v, &res)) {
                        if (is_empty_clause(&res)) {
                            printf("[УСПІХ] Виведено порожній диз'юнкт ⊥ на кроці %zu!\n", pass);
                            return true; // UNSAT
                        }
                        if (!formula_contains(formula, &res)) {
                            if (formula->count < MAX_CLAUSES) {
                                formula->clauses[formula->count++] = res;
                                added_in_pass++;
                            }
                        }
                    }
                }
            }
        }
    }
    
    printf("[РЕЗУЛЬТАТ] Можливе насичення без виводу ⊥. Формула здійсненна (SAT).\n");
    return false;
}

int main(void) {
    // Тестова КНФ нездійсненна: (x1 ∨ x2) ∧ (¬x1 ∨ x2) ∧ (x1 ∨ ¬x2) ∧ (¬x1 ∨ ¬x2)
    CNFFormula formula = {
        .clauses = {
            {.lits = {1, 2}, .size = 2},
            {.lits = {-1, 2}, .size = 2},
            {.lits = {1, -2}, .size = 2},
            {.lits = {-1, -2}, .size = 2}
        },
        .count = 4
    };

    bool is_unsat = resolution_refute(&formula, 2);
    printf("Формула нездійсненна (UNSAT): %s\n", is_unsat ? "ТАК" : "НІ");
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <set>
#include <optional>
#include <cmath>
#include <string>

// Опис типу літерала (ціле число зі знаком: +v для x_v, -v для ¬x_v)
using Literal = int;

// Клас диз'юнкта з автоматичною нормалізацією та RAII
class Clause {
private:
    std::vector<Literal> lits_;
    bool is_tautology_{false};

    void normalize() {
        if (lits_.empty()) return;
        
        std::sort(lits_.begin(), lits_.end(), [](Literal a, Literal b) {
            if (std::abs(a) != std::abs(b)) return std::abs(a) < std::abs(b);
            return a < b;
        });

        std::vector<Literal> cleaned;
        for (size_t i = 0; i < lits_.size(); ++i) {
            if (i > 0 && lits_[i] == lits_[i - 1]) continue;
            if (i > 0 && lits_[i] == -lits_[i - 1]) {
                is_tautology_ = true;
                lits_.clear();
                return;
            }
            cleaned.push_back(lits_[i]);
        }
        lits_ = std::move(cleaned);
    }

public:
    Clause() = default;
    explicit Clause(std::vector<Literal> lits) : lits_(std::move(lits)) {
        normalize();
    }

    [[nodiscard]] bool empty() const { return lits_.empty() && !is_tautology_; }
    [[nodiscard]] bool is_tautology() const { return is_tautology_; }
    [[nodiscard]] size_t size() const { return lits_.size(); }
    [[nodiscard]] const std::vector<Literal>& literals() const { return lits_; }

    [[nodiscard]] bool contains(Literal l) const {
        return std::binary_search(lits_.begin(), lits_.end(), l, [](Literal a, Literal b) {
            if (std::abs(a) != std::abs(b)) return std::abs(a) < std::abs(b);
            return a < b;
        });
    }

    bool operator==(const Clause& other) const {
        return lits_ == other.lits_ && is_tautology_ == other.is_tautology_;
    }

    bool operator<(const Clause& other) const {
        return lits_ < other.lits_;
    }

    [[nodiscard]] std::string to_string() const {
        if (empty()) return "⊥";
        if (is_tautology_) return "⊤ (Tautology)";
        std::string s = "(";
        for (size_t i = 0; i < lits_.size(); ++i) {
            s += (lits_[i] > 0 ? "x" + std::to_string(lits_[i]) : "¬x" + std::to_string(-lits_[i]));
            if (i + 1 < lits_.size()) s += " ∨ ";
        }
        s += ")";
        return s;
    }
};

// Функція резолюційного виводу двох дизюнктів за змінною pivot
std::optional<Clause> resolve(const Clause& c1, const Clause& c2, int pivot) {
    bool c1_pos = c1.contains(pivot);
    bool c1_neg = c1.contains(-pivot);
    bool c2_pos = c2.contains(pivot);
    bool c2_neg = c2.contains(-pivot);

    if (!((c1_pos && c2_neg) || (c1_neg && c2_pos))) {
        return std::nullopt; // Резолюція неможлива
    }

    std::vector<Literal> res_lits;
    for (Literal l : c1.literals()) {
        if (std::abs(l) != pivot) res_lits.push_back(l);
    }
    for (Literal l : c2.literals()) {
        if (std::abs(l) != pivot) res_lits.push_back(l);
    }

    Clause res(std::move(res_lits));
    if (res.is_tautology()) return std::nullopt;
    return res;
}

// Двигун резолюційного спростування
class ResolutionSolver {
private:
    std::set<Clause> clause_db_;
    int num_vars_{0};

public:
    explicit ResolutionSolver(int num_vars) : num_vars_(num_vars) {}

    void add_clause(Clause c) {
        if (!c.is_tautology()) {
            clause_db_.insert(std::move(c));
        }
    }

    bool solve() {
        std::cout << "[CDCL/Resolution Engine] Старт насичення. Початкових диз'юнктів: "
                  << clause_db_.size() << std::endl;

        for (const auto& c : clause_db_) {
            if (c.empty()) {
                std::cout << "[Збій] Порожній диз'юнкт ⊥ присутній у вхідній формулі!\n";
                return true;
            }
        }

        bool new_clause_added = true;
        size_t iteration = 1;

        while (new_clause_added) {
            new_clause_added = false;
            std::vector<Clause> current_clauses(clause_db_.begin(), clause_db_.end());
            std::cout << "--- Ітерація " << iteration++ << " (поточний розмір: " 
                      << current_clauses.size() << ") ---\n";

            for (size_t i = 0; i < current_clauses.size(); ++i) {
                for (size_t j = i + 1; j < current_clauses.size(); ++j) {
                    for (int v = 1; v <= num_vars_; ++v) {
                        auto res = resolve(current_clauses[i], current_clauses[j], v);
                        if (res.has_value()) {
                            if (res->empty()) {
                                std::cout << "[УСПІХ] Резолюційний вивід досяг ⊥!\n"
                                          << "Резолюція між " << current_clauses[i].to_string()
                                          << " та " << current_clauses[j].to_string() 
                                          << " за змінною x" << v << "\n";
                                return true; // UNSAT
                            }
                            if (clause_db_.find(*res) == clause_db_.end()) {
                                clause_db_.insert(*res);
                                new_clause_added = true;
                            }
                        }
                    }
                }
            }
        }

        std::cout << "[РЕЗУЛЬТАТ] Формула здійсненна (SAT). Резолюція ⊥ неможлива.\n";
        return false;
    }
};

int main() {
    // Демонстрація на нездійсненному наборі з 3 variables
    ResolutionSolver solver(3);

    // F = (x1 ∨ x2) ∧ (¬x1 ∨ x3) ∧ (¬x2 ∨ x3) ∧ (¬x3)
    solver.add_clause(Clause({1, 2}));
    solver.add_clause(Clause({-1, 3}));
    solver.add_clause(Clause({-2, 3}));
    solver.add_clause(Clause({-3}));

    bool unsat = solver.solve();
    std::cout << "Результат спростування (UNSAT): " << (unsat ? "ТАК" : "НІ") << std::endl;

    return 0;
}
```
:::
