# ⚙️ Міні-солвер залежностей: алгоритм CDCL мовами C та C++

Цей проект показує практичну реалізацію математичного рушія розв'язання залежностей пакунків на основі алгоритму перевірки здійснюваності булевих формул (SAT solver). Наведений код демонструє класичний алгоритм DPLL (Davis-Putnam-Logemann-Loveland) з елементами CDCL (Conflict-Driven Clause Learning): поширення одиничних диз'юнктів (Unit Propagation), відкат за умов виникнення конфліктів (Backtracking) та автоматичну оцінку стану графа залежностей.

## 1. Постановка математичної задачі

Кожен пакунок у системі дистрибуції позначається цілочисельним ідентифікатором `Id` в діапазоні від `1` до `N`. 
Правила взаємозв'язків між пакунками подаються у кон'юнктивній нормальній формі (CNF). У цій формі загальний опис репозиторію є кон'юнкцією (логічним І) окремих диз'юнктів (`Clause`). Кожен диз'юнкт є диз'юнкцією (логічним АБО) декількох літералів.

Закони кодування метаданих у булеві літерали:
- Позитивний літерал `+x` означає обов'язкову вимогу "пакунок `x` мусить бути встановлений у системі".
- Негативний літерал `-x` означає вимогу "пакунок `x` мусить бути відсутній або видалений із системи".

Трансляція стандартних зв'язків пакунків у булеві диз'юнкти:
- **Пряма залежність `App ⇒ LibA`:** Згідно з імпликацією, якщо встановлено `App`, має бути встановлено й `LibA`. Формула: `¬App ∨ LibA`. У коді це записується як диз'юнкт із двох літералів `{-App, +LibA}`.
- **Прямий конфлікт `Postfix ⊕ Sendmail`:** Пакунки не можуть бути встановлені одночасно: `¬(Postfix ∧ Sendmail)`. За правилом Де Моргана це перетворюється у диз'юнкт `{-Postfix, -Sendmail}`.
- **Альтернативна залежність `App ⇒ (Postfix ∨ Sendmail)`:** Програмі потрібен хоча б один із двох поштових серверів: `{-App, +Postfix, +Sendmail}`.
- **Вимога користувача "Встановити App":** Подається як одиничний диз'юнкт (Unit Clause) з одного позитивного літерала `{+App}`.

Завдання розв'язувача полягає у знаходженні такого вектора призначень `(Assignment[1], Assignment[2], ..., Assignment[N])`, де кожне значення дорівнює `1` (True) або `-1` (False), за якого кожен диз'юнкт у базі знань приймає значення `True`.

## 2. Теоретичні засади алгоритму: від обходу до CDCL

Класичний рекурсивний перебір варіантів має експоненційну складність `O(2^N)`. Для системи з 50 000 пакунків кількість можливих станів перевищує кількість атомів у спостережуваному Всесвіті. Щоб вирішити цю проблему у реальному часі, SAT-солвери використовують два фундаментальні прийоми:

### 2.1. Поширення одиничних диз'юнктів (Unit Propagation)
Якщо у якомусь диз'юнкті всі літерали, крім одного, вже приймають значення `False` відповідно до поточного вектора призначень, то єдиний неоцінений літерал **зобов'язаний** прийняти значення `True`.

Наприклад, якщо у нас є диз'юнкт `{-App, +LibA}` і ми вже встановили `App = True` (тобто літерал `-App` дорівнює `False`), то для збереження істинності всього диз'юнкта змінна `LibA` повинна негайно прийняти значення `True`. Це виведення відбувається автоматично без створення нових гілок пошуку. Ланцюгова реакція Unit Propagation дозволяє скоротити простір пошуку на 99.9%.

### 2.2. Аналіз конфліктів та повернення (Backtracking)
Якщо після серії вимушених призначень виникає суперечність (усі літерали якогось диз'юнкта стали `False`), поточна гілка пошуку оголошується тупиковою. Алгоритм скасовує останні здогадки і пробує альтернативне значення змінної.

## 3. Реалізація C та C++

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define MAX_VARS 100
#define MAX_CLAUSES 200
#define MAX_LITS_PER_CLAUSE 10

// Структура, що представляє один булевий диз'юнкт (Clause)
typedef struct {
    int lits[MAX_LITS_PER_CLAUSE];
    int size;
} Clause;

// Структура стан SAT-солвера
typedef struct {
    int num_vars;
    int num_clauses;
    Clause clauses[MAX_CLAUSES];
    int assignment[MAX_VARS + 1]; // 0 = unassigned, 1 = true, -1 = false
} SatSolver;

// Ініціалізація структури солвера
void sat_init(SatSolver *solver, int vars) {
    solver->num_vars = vars;
    solver->num_clauses = 0;
    for (int i = 0; i <= vars; i++) {
        solver->assignment[i] = 0;
    }
}

// Додавання диз'юнкта з двох літералів (наприклад, залежність або конфлікт)
void sat_add_clause_2(SatSolver *solver, int lit1, int lit2) {
    if (solver->num_clauses >= MAX_CLAUSES) return;
    Clause *c = &solver->clauses[solver->num_clauses++];
    c->lits[0] = lit1;
    c->lits[1] = lit2;
    c->size = 2;
}

// Додавання одиничного диз'юнкта (запит користувача)
void sat_add_unit_clause(SatSolver *solver, int lit) {
    if (solver->num_clauses >= MAX_CLAUSES) return;
    Clause *c = &solver->clauses[solver->num_clauses++];
    c->lits[0] = lit;
    c->size = 1;
}

// Оцінка стану диз'юнкта: 1 = Satisfied, 0 = Conflict (всі false), -1 = Unresolved
int eval_clause(const SatSolver *solver, const Clause *c, int *unassigned_lit) {
    int unassigned_count = 0;
    int last_unassigned = 0;

    for (int i = 0; i < c->size; i++) {
        int lit = c->lits[i];
        int var = (lit > 0) ? lit : -lit;
        int val = solver->assignment[var];

        // Якщо хоча б один літерал істинний, увесь диз'юнкт є істинним
        if ((lit > 0 && val == 1) || (lit < 0 && val == -1)) {
            return 1;
        }
        // Якщо змінна ще не оцінена
        if (val == 0) {
            unassigned_count++;
            last_unassigned = lit;
        }
    }

    if (unassigned_count == 0) return 0; // Конфлікт! Усі літерали хибні
    if (unassigned_count == 1 && unassigned_lit) *unassigned_lit = last_unassigned;
    return -1; // Диз'юнкт ще не вирішено, є більше одного неоціненого літерала
}

// Реалізація алгоритму Unit Propagation
bool unit_propagate(SatSolver *solver) {
    bool changed = true;
    while (changed) {
        changed = false;
        for (int i = 0; i < solver->num_clauses; i++) {
            int unit_lit = 0;
            int res = eval_clause(solver, &solver->clauses[i], &unit_lit);
            if (res == 0) return false; // Знайдено логічну суперечність
            if (res == -1 && unit_lit != 0) {
                int var = (unit_lit > 0) ? unit_lit : -unit_lit;
                solver->assignment[var] = (unit_lit > 0) ? 1 : -1;
                changed = true;
            }
        }
    }
    return true;
}

// Основна рекурсивна функція пошуку розв'язку (DPLL)
bool solve_dpll(SatSolver *solver) {
    // 1. Виконуємо автоматичне поширення одиничних диз'юнктів
    if (!unit_propagate(solver)) return false;

    // 2. Шукаємо першу неоцінену змінну для прийняття рішення
    int unassigned_var = 0;
    for (int i = 1; i <= solver->num_vars; i++) {
        if (solver->assignment[i] == 0) {
            unassigned_var = i;
            break;
        }
    }

    // Якщо всі змінні оцінені без конфліктів — розв'язок знайдено!
    if (unassigned_var == 0) return true;

    // Зберігаємо поточний стан для можливого відкату
    SatSolver backup = *solver;

    // Гілка А: Спробуємо встановити змінну у True (+1)
    solver->assignment[unassigned_var] = 1;
    if (solve_dpll(solver)) return true;

    // Гілка Б: Відкат та спроба встановити змінну у False (-1)
    *solver = backup;
    solver->assignment[unassigned_var] = -1;
    return solve_dpll(solver);
}

int main(void) {
    SatSolver solver;
    // Створюємо систему з 4 пакунків: 1: App, 2: LibA, 3: Postfix, 4: Sendmail
    sat_init(&solver, 4);

    // Залежність: App вимагає LibA (-1 v 2)
    sat_add_clause_2(&solver, -1, 2);
    // Залежність: App вимагає Postfix (-1 v 3)
    sat_add_clause_2(&solver, -1, 3);
    // Конфлікт: Postfix не сумісний із Sendmail (-3 v -4)
    sat_add_clause_2(&solver, -3, -4);

    // Запит користувача: встановити App (+1)
    sat_add_unit_clause(&solver, 1);

    printf("Аналіз графа залежностей C SAT-солвером...\n");
    if (solve_dpll(&solver)) {
        printf("ЗНАЙДЕНО ЗДІЙСНЕННИЙ ПЛАН ТРАНЗАЦІЇ:\n");
        printf("  - App (ID 1): %s\n", solver.assignment[1] == 1 ? "УСТАНОВИТИ" : "ПРОПУСТИТИ");
        printf("  - LibA (ID 2): %s\n", solver.assignment[2] == 1 ? "УСТАНОВИТИ" : "ПРОПУСТИТИ");
        printf("  - Postfix (ID 3): %s\n", solver.assignment[3] == 1 ? "УСТАНОВИТИ" : "ПРОПУСТИТИ");
        printf("  - Sendmail (ID 4): %s\n", solver.assignment[4] == 1 ? "УСТАНОВИТИ" : "ПРОПУСТИТИ");
    } else {
        printf("ПОМИЛКА: Транзакція неможлива через внутрішній конфлікт залежностей!\n");
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <optional>
#include <numeric>
#include <string_view>
#include <cmath>

enum class PackageState : int8_t {
    Unassigned = 0,
    Installed = 1,
    Absent = -1
};

struct SatClause {
    std::vector<int> literals; // Позитивний значення (+ID), негативне (-ID)
};

class PackageDependencySolver {
public:
    explicit PackageDependencySolver(size_t package_count)
        : assignments_(package_count + 1, PackageState::Unassigned) {}

    void add_clause(std::vector<int> lits) {
        clauses_.push_back(SatClause{std::move(lits)});
    }

    // Створення правила залежності: pkg_a => pkg_b (-A v B)
    void add_dependency(int pkg_a, int pkg_b) {
        add_clause({-pkg_a, pkg_b});
    }

    // Створення правила конфлікту: NOT (pkg_a AND pkg_b) (-A v -B)
    void add_conflict(int pkg_a, int pkg_b) {
        add_clause({-pkg_a, -pkg_b});
    }

    // Створення прямого запиту користувача (+pkg_id)
    void require_package(int pkg_id) {
        add_clause({pkg_id});
    }

    // Запуск розв'язання залежностей
    [[nodiscard]] std::optional<std::vector<PackageState>> solve() {
        if (!unit_propagate()) {
            return std::nullopt; // Нездійсненна система
        }

        int unassigned_var = find_unassigned_variable();
        if (unassigned_var == 0) {
            return assignments_; // Усі змінні успішно призначені
        }

        // Збереження стану для відкату (RAII)
        auto saved_state = assignments_;

        // Гілка 1: Спробуємо призначити Installed
        assignments_[unassigned_var] = PackageState::Installed;
        if (auto result = solve()) {
            return result;
        }

        // Гілка 2: Відкат та спроба призначити Absent
        assignments_ = std::move(saved_state);
        assignments_[unassigned_var] = PackageState::Absent;
        return solve();
    }

private:
    std::vector<SatClause> clauses_;
    std::vector<PackageState> assignments_;

    int find_unassigned_variable() const {
        for (size_t i = 1; i < assignments_.size(); ++i) {
            if (assignments_[i] == PackageState::Unassigned) {
                return static_cast<int>(i);
            }
        }
        return 0;
    }

    bool unit_propagate() {
        bool changed = true;
        while (changed) {
            changed = false;
            for (const auto& clause : clauses_) {
                int unassigned_lit = 0;
                int unassigned_count = 0;
                bool satisfied = false;

                for (int lit : clause.literals) {
                    int var = std::abs(lit);
                    auto val = assignments_[var];

                    if ((lit > 0 && val == PackageState::Installed) || 
                        (lit < 0 && val == PackageState::Absent)) {
                        satisfied = true;
                        break;
                    }
                    if (val == PackageState::Unassigned) {
                        unassigned_count++;
                        unassigned_lit = lit;
                    }
                }

                if (satisfied) continue;
                if (unassigned_count == 0) return false; // Конфлікт!

                if (unassigned_count == 1 && unassigned_lit != 0) {
                    int var = std::abs(unassigned_lit);
                    assignments_[var] = (unassigned_lit > 0) ? PackageState::Installed : PackageState::Absent;
                    changed = true;
                }
            }
        }
        return true;
    }
};

int main() {
    // Ініціалізація системи на 4 пакунки
    PackageDependencySolver solver(4);

    // Додавання правил графа
    solver.add_dependency(1, 2); // App (1) -> LibA (2)
    solver.add_dependency(1, 3); // App (1) -> Postfix (3)
    solver.add_conflict(3, 4);   // Postfix (3) <-> Sendmail (4)

    // Запит користувача: встановити App (1)
    solver.require_package(1);

    std::cout << "Аналіз графа залежностей C++20 SAT-солвером...\n";
    auto result = solver.solve();

    if (result) {
        std::cout << "ПЛАН ТРАНЗАЦІЇ УСПІШНО СФОРМОВАНО:\n";
        constexpr std::string_view names[] = {"", "App", "LibA", "Postfix", "Sendmail"};
        for (size_t i = 1; i <= 4; ++i) {
            std::cout << "  - " << names[i] << " (ID " << i << "): "
                      << ((*result)[i] == PackageState::Installed ? "УСТАНОВИТИ" : "ПРОПУСТИТИ")
                      << "\n";
        }
    } else {
        std::cout << "ТРАНЗАЦІЯ БЛОКОВАНА: Виявлено незадоволений конфлікт версій!\n";
    }

    return 0;
}
```
:::

## 4. Аналіз детальної роботи коду

Нижче подано покроковий розбір виконання головних функцій наведеного алгоритму.

### 4.1. Функція `eval_clause()` у версії C
Функція приймає покажчик на поточний стан солвера та диз'юнкт. Вона ітерується по всіх літералах диз'юнкта `c->lits[i]`:
- Отримує номер змінної `var = abs(lit)`.
- Отримує поточний стан змінної з масиву `solver->assignment[var]`.
- Перевіряє, чи літерал збігається зі станом: якщо літерал позитивний (`+2`) і змінна має значення `1` (True), або якщо літерал негативний (`-1`) і змінна має значення `-1` (False), функція негайно повертає `1` (Satisfied). Це перериває подальший обхід диз'юнкта, забезпечуючи швидке обчислення.
- Якщо диз'юнкт не є істинним і кількість неоцінених змінних дорівнює нулю (`unassigned_count == 0`), функція повертає `0` (Conflict). Це сигналізує солверу про виникнення суперечності.

### 4.2. Механізм `unit_propagate()`
Функція запускає цикл `while(changed)`, який продовжує обхід бази диз'юнктів доти, доки виводяться нові значення:
- При виявленні диз'юнкта з ровно одним неоціненим літералом (`unassigned_count == 1`), значення відповідної змінної автоматично фіксується у масиві `assignment`.
- Прапор `changed` виставляється у `true`, що змушує цикл пройти по всій базі диз'юнктів ще раз, адже нова вимушена змінна могла перетворити інші сусідні диз'юнкти на одиничні.
- Якщо на будь-якому кроці `eval_clause()` повертає `0`, `unit_propagate()` негайно припиняє роботу і повертає `false`.

### 4.3. Рекурсивний розв'язувач `solve_dpll()`
Функція реалізує пошук у глибину з можливістю відкату:
1. Спочатку виконується `unit_propagate()`.
2. Шукається перша змінна, яка ще не має значення (`assignment[i] == 0`).
3. Якщо всі змінні оцінені без помилок, рекурсія повертає `true` — план транзакції сформовано.
4. Якщо є неоцінена змінна, робиться копія стану `backup = *solver`.
5. Спершу випробовується гілка з позитивним значенням `+1`. Якщо вона повертає `true`, розв'язок знайдено.
6. Якщо гілка повертає `false`, стан відновлюється з копії `*solver = backup`, і випробовується негативне значення `-1`.

## 5. Практичне застосування та відмінності від промислових SAT-солверів

Представлений міні-солвер демонструє фундаментальну математичну ідею, але промислові рушії (такі як `libsolv`) доповнюють її трьома критичними оптимізаціями:

1. **Двокомпонентні спостережувані літерали (Two-Watched Literals):** Замість повного обходу всіх диз'юнктів при кожній зміні змінної, `libsolv` стежить тільки за двома невизначеними літералами у кожному диз'юнкті. Це зменшує кількість перевірок у сотні разів.
2. **Навчання диз'юнктів конфлікту (Clause Learning):** При знаходженні суперечності промисловий CDCL-солвер створює новий диз'юнкт-заборону (Learned Clause) і додає його в систему, блокуючи повторення аналогічних помилок у майбутньому.
3. **Нехронологічний відкат (Non-Chronological Backjumping):** При конфлікті CDCL-солвер аналізує рівень рішення (Decision Level) першопричини і повертається одразу на кілька рівнів вгору, минаючи даремний перебір проміжних гілок.
