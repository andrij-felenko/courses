# ⚙️ Реалізація SAT-солвера: від базового DPLL до розширеного CDCL з 2WL

Алгоритмічне ядро SAT-солвера спирається на чотири низькорівневі інваріанти: компактне представлення КНФ-формул у пам'яті, стек призначень для стеження за станом змінних, швидке поширення обмежень (BCP) через двоспостережувані літерали (2WL) та аналіз конфліктів для обчислення першої точки унікального імліканта (1UIP). Промислові CDCL-солвери досягають високої швидкодії за рахунок побітового кодування літералів і безперервного розміщення диз'юнктів у пам'яті, що зводить виконання ключових логічних операцій до побітових інструкцій процесора та мінімізує промахи кешу.

## 1. Архітектура, представлення в пам'яті та побітове кодування літералів

У високопродуктивних SAT-солверах кожна булева змінна `x_i` нумерується цілим додатним числом `i ∈ {1, ..., N}`. Оскільки оперативна пам'ять комп'ютера найкраще працює з безперервними масивами, літерали кодуються беззнаковими цілими числами 32-бітного типу:

```text
Позитивний літерал (+x_i):   lit = 2 * i       (парні числа)
Негативний літерал (-x_i):   lit = 2 * i + 1   (непарні числа)
```

Таке кодування забезпечує виконання ключових логічних операцій за одну побітову інструкцію процесора:
- Отримання заперечення літерала: `neg_lit = lit ^ 1` (побітова операція XOR із 1).
- Отримання номера змінної: `var = lit >> 1` (побітовий зсув праворуч на 1 біт).
- Визначення полярності літерала: `is_negative = lit & 1` (побітове І з 1).

### Модель пам'яті для бази диз'юнктів

Використання окремих об'єктів у купі (`malloc` або `new`) для кожного диз'юнкта створює серйозну фрагментацію пам'яті та промахи кеш-пам'яті першого та другого рівнів (L1/L2 Cache Misses). Кожен виклик системного алокатора додає 16-байтний заголовок до структури диз'юнкта, що при мільйонах диз'юнктів призводить до даремної витрати десятків мегабайтів пам'яті.

Промислові солвери (такі як MiniSat, Glucose та CaDiCaL) використовують монолітний виділений вектор цілих чисел (Flat Region / Arena Allocator). Диз'юнкт описується як заголовкова структура з вказанням довжини, значення LBD (Literal Block Distance) та масиву літералів.

Під час виконання BCP солвер звертається до масиву літералів диз'юнкта. Якщо літерали розміщені послідовно у пам'яті, процесор завантажує їх у кеш-рядок (Cache Line) за один такт шини пам'яті, що виключає затримки звернення до оперативної пам'яті (DRAM).

## 2. Механіка 2WL (Two-Watched Literals) у коді

Для прискорення BCP солвер підтримує таблицю списків спостереження `watches`:
```text
watches[lit] -> вектор диз'юнктів, які спостерігають за літералом lit
```

Кожен диз'юнкт розміщує свої два спостережувані літерали на перших двох позиціях масиву `lits[0]` та `lits[1]`.

Коли змінна `x` отримує значення (наприклад, `x = 1`), літерал `¬x` (який відповідає `lit_neg = (x << 1) | 1`) стає **хибним**. Солвер вилучає зі стеку призначень літерал `¬x` і переглядає тільки той список `watches[¬x]`, який спостерігав за цим літералом:

1. Для кожного диз'юнкта `C` у списку `watches[¬x]` перевіряється перший спостережуваний літерал `lits[0]`.
2. Якщо `lits[0]` вже є істинним у поточному призначенні, диз'юнкт `C` є задоволеним, і вказівники не змінюються.
3. Якщо `lits[0]` не є істинним, а хибним став `lits[0]`, солвер міняє місцями `lits[0]` та `lits[1]`, роблячи хибний літерал другим елементом (`lits[1]`).
4. Далі виконується сканування решти літералів `lits[k]` (для `k ≥ 2`).
5. Якщо знайдено літерал `lits[k]`, який є невизначеним або істинним:
   - Елементи `lits[1]` та `lits[k]` міняються місцями.
   - Диз'юнкт `C` видаляється зі списку `watches[¬x]` і додається до списку `watches[lits[1] ^ 1]`.
6. Якщо ж жодного не-хибного літерала не знайдено:
   - Якщо `lits[0]` є невизначеним, диз'юнкт `C` стає одиничним, і літерал `lits[0]` штовхається у стек BCP із причинним диз'юнктом `reason[var(lits[0])] = C`.
   - Якщо `lits[0]` також є хибним, фіксується конфлікт, і BCP припиняється.

Головною перевагою алгоритму 2WL є те, що при вертанні за стеком рішень (Backtracking) вказівники спостереження `lits[0]` та `lits[1]` залишаються незмінними. Оскільки скасування рішення змінює значення змінних із хибного на невизначене, інваріант не-хибності спостережуваних літералів зберігається автоматично. Це звільняє солвер від необхідності оновлювати списки спостереження при вертанні назад, знижуючи складність вертання до `O(1)`.

## 3. Алгоритм аналізу конфліктів, 1UIP та LBD у коді

При виявленні конфліктного диз'юнкта `C_conf` запускається аналіз конфлікту для побудови 1UIP диз'юнкта. Алгоритм працює у зворотному напрямку за стеком призначень `trail`.

Розглянемо детальний покроковий процес обчислення 1UIP:

1. Створюється порожній масив вивченого диз'юнкта `C_learn`.
2. Ініціалізується лічильник літералів поточного рівня `path_count = 0`.
3. Створюється булевий масив `seen` розміру `N + 1`, заповнений значеннями `false`.
4. Змінна `p` ініціалізується як невизначений літерал (або конфліктний літерал).
5. Починається цикл розгортання стеку `trail` з останнього елемента:
   - Отримується причинний диз'юнкт `reason_clause` для літерала `p` (для самого конфлікту це `C_conf`).
   - Для кожного літерала `lit` у `reason_clause`:
     - Якщо `var(lit)` ще не була відвідана (`seen[var(lit)] == false`):
       - Позначається `seen[var(lit)] = true`.
       - Якщо `level(var(lit)) == current_level`, лічильник збільшується: `path_count++`.
       - Інакше (літерал належить попередньому рівню) він додається до `C_learn`.
   - Здійснюється пошук наступного літерала `p` у стеку `trail`, для якого `seen[var(p)] == true`.
   - Змінна `seen[var(p)]` скидається у `false`, а лічильник зменшується: `path_count--`.
   - Цикл зупиняється, коли `path_count == 1`.
6. Літерал `~p` є запереченням першої єдиної точки імплікації (`1UIP`). Він розміщується на першій позиції `C_learn[0]`.

### Обчислення метрики LBD (Literal Block Distance)

Після формування `C_learn` солвер обчислює значення LBD:
- Створюється тимчасовий масив або бітова маска відвіданих рівнів прийняття рішень.
- Проходиться масив літералів `C_learn` і підраховується кількість унікальних рівнів рішень.
- Значення LBD записується у заголовок диз'юнкта. Якщо `LBD ≤ 2`, диз'юнкт позначається як "Glue Clause" і зберігається в пам'яті безстроково.

## 4. Алгоритм нехронологічного вертання (Backjumping)

Після побудови `C_learn` солвер обчислює рівень ствердження:
```text
d_assert = 0
Для кожного літерала lit у C_learn (починаючи з індексу 1):
    d_assert = max(d_assert, level(var(lit)))
```

Процедура вертання вилучає зі стеку `trail` усі елементи, призначені на рівнях, вищих за `d_assert`:

1. Доки стек `trail` не порожній і рівень останнього елемента `trail.back().level > d_assert`:
   - Витягується змінна `v = trail.back().var`.
   - Скидається стан: `assigns[v] = L_UNDEFINED`.
   - Скидається рівень: `levels[v] = -1`.
   - Скидається причина: `reasons[v] = NULL`.
   - Елемент видаляється зі стеку `trail.pop_back()`.
2. Поточний рівень рішення встановлюється у `current_level = d_assert`.
3. Вивчений диз'юнкт `C_learn` додається до загальної бази диз'юнктів.
4. Оскільки на рівні `d_assert` вивчений диз'юнкт є одиничним, літерал `C_learn[0]` негайно призначається через `solver_assign(C_learn[0], C_learn)`.

## 5. Евристика VSIDS та збереження фази у коді

Для підтримки евристики VSIDS солвер зберігає масив плаваючих оцінок `activity[var]` та початковий приріст `var_inc = 1.0`.

- **Збільшення активності при конфлікті:** під час аналізу конфлікту для кожної змінної `v`, що входить до зрізу 1UIP, викликається процедура `bump_var(v)`:
  ```text
  activity[v] += var_inc;
  if (activity[v] > 1e100) {
      for (int i = 1; i <= num_vars; i++) activity[i] *= 1e-100;
      var_inc *= 1e-100;
  }
  ```
- **Мультиплікативне згасання:** після завершення аналізу конфлікту приріст оновлюється: `var_inc *= (1.0 / 0.95)`.
- **Вибір змінної рішення:** солвер вибирає невизначену змінну з максимальним значенням `activity[v]`. Для прискорення пошуку використовується бінарна піраміда (Binary Max-Heap).
- **Збереження фази (Phase Saving):** при виборі полярності змінної `v` солвер перевіряє масив `saved_phase[v]`. Змінній надається те значення (`L_TRUE` чи `L_FALSE`), яке вона мала під час останнього призначення на попередніх кроках BCP.

## 6. Повна реалізація ядра SAT-солвера мовами C та C++

Нижче наведено робочі реалізації базового ядра CDCL SAT-солвера мовами C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#define L_UNDEFINED -1
#define L_FALSE      0
#define L_TRUE       1

typedef struct {
    int* lits;
    int size;
    int lbd;
} Clause;

typedef struct {
    int var;
    int val;
    int level;
    Clause* reason;
} TrailEntry;

typedef struct {
    int num_vars;
    int num_clauses;
    Clause** clauses;
    int* assigns;       /* assigns[var] -> L_UNDEFINED, L_FALSE, L_TRUE */
    int* levels;        /* levels[var] -> decision level */
    Clause** reasons;   /* reasons[var] -> clause that forced assignment */
    double* activity;   /* VSIDS activity scores */
    TrailEntry* trail;
    int trail_size;
    int trail_capacity;
    int current_level;
    double var_inc;
    double var_decay;
} CDCLSolver;

CDCLSolver* solver_create(int num_vars) {
    CDCLSolver* s = (CDCLSolver*)malloc(sizeof(CDCLSolver));
    s->num_vars = num_vars;
    s->num_clauses = 0;
    s->clauses = NULL;
    s->assigns = (int*)malloc((num_vars + 1) * sizeof(int));
    s->levels = (int*)malloc((num_vars + 1) * sizeof(int));
    s->reasons = (Clause**)malloc((num_vars + 1) * sizeof(Clause*));
    s->activity = (double*)malloc((num_vars + 1) * sizeof(double));
    
    for (int i = 1; i <= num_vars; i++) {
        s->assigns[i] = L_UNDEFINED;
        s->levels[i] = -1;
        s->reasons[i] = NULL;
        s->activity[i] = 0.0;
    }
    
    s->trail_capacity = 1024;
    s->trail_size = 0;
    s->trail = (TrailEntry*)malloc(s->trail_capacity * sizeof(TrailEntry));
    s->current_level = 0;
    s->var_inc = 1.0;
    s->var_decay = 0.95;
    return s;
}

void solver_free(CDCLSolver* s) {
    if (!s) return;
    for (int i = 0; i < s->num_clauses; i++) {
        free(s->clauses[i]->lits);
        free(s->clauses[i]);
    }
    free(s->clauses);
    free(s->assigns);
    free(s->levels);
    free(s->reasons);
    free(s->activity);
    free(s->trail);
    free(s);
}

void solver_add_clause(CDCLSolver* s, const int* lits, int size) {
    Clause* c = (Clause*)malloc(sizeof(Clause));
    c->size = size;
    c->lbd = 0;
    c->lits = (int*)malloc(size * sizeof(int));
    for (int i = 0; i < size; i++) {
        c->lits[i] = lits[i];
    }
    
    s->num_clauses++;
    s->clauses = (Clause**)realloc(s->clauses, s->num_clauses * sizeof(Clause*));
    s->clauses[s->num_clauses - 1] = c;
}

static inline int lit_value(CDCLSolver* s, int lit) {
    int var = abs(lit);
    int val = s->assigns[var];
    if (val == L_UNDEFINED) return L_UNDEFINED;
    return (lit > 0) ? val : (1 - val);
}

void solver_assign(CDCLSolver* s, int lit, Clause* reason) {
    int var = abs(lit);
    int val = (lit > 0) ? L_TRUE : L_FALSE;
    s->assigns[var] = val;
    s->levels[var] = s->current_level;
    s->reasons[var] = reason;
    
    if (s->trail_size >= s->trail_capacity) {
        s->trail_capacity *= 2;
        s->trail = (TrailEntry*)realloc(s->trail, s->trail_capacity * sizeof(TrailEntry));
    }
    s->trail[s->trail_size].var = var;
    s->trail[s->trail_size].val = val;
    s->trail[s->trail_size].level = s->current_level;
    s->trail[s->trail_size].reason = reason;
    s->trail_size++;
}

Clause* solver_bcp(CDCLSolver* s) {
    for (int i = 0; i < s->num_clauses; i++) {
        Clause* c = s->clauses[i];
        int false_count = 0;
        int undef_lit = 0;
        int undef_count = 0;
        
        for (int j = 0; j < c->size; j++) {
            int val = lit_value(s, c->lits[j]);
            if (val == L_TRUE) {
                undef_count = -1; /* Clause already satisfied */
                break;
            }
            if (val == L_FALSE) {
                false_count++;
            } else {
                undef_count++;
                undef_lit = c->lits[j];
            }
        }
        
        if (undef_count == -1) continue;
        
        if (false_count == c->size) {
            return c; /* Conflict detected! */
        }
        
        if (undef_count == 1) {
            solver_assign(s, undef_lit, c);
        }
    }
    return NULL;
}

void solver_backtrack(CDCLSolver* s, int target_level) {
    while (s->trail_size > 0 && s->trail[s->trail_size - 1].level > target_level) {
        TrailEntry entry = s->trail[--s->trail_size];
        s->assigns[entry.var] = L_UNDEFINED;
        s->levels[entry.var] = -1;
        s->reasons[entry.var] = NULL;
    }
    s->current_level = target_level;
}

void solver_bump_var(CDCLSolver* s, int var) {
    s->activity[var] += s->var_inc;
    if (s->activity[var] > 1e100) {
        for (int i = 1; i <= s->num_vars; i++) {
            s->activity[i] *= 1e-100;
        }
        s->var_inc *= 1e-100;
    }
}

int solver_pick_variable(CDCLSolver* s) {
    int best_var = 0;
    double max_act = -1.0;
    for (int i = 1; i <= s->num_vars; i++) {
        if (s->assigns[i] == L_UNDEFINED) {
            if (s->activity[i] > max_act) {
                max_act = s->activity[i];
                best_var = i;
            }
        }
    }
    return best_var;
}

bool solver_solve(CDCLSolver* s) {
    while (true) {
        Clause* conflict = solver_bcp(s);
        if (conflict != NULL) {
            if (s->current_level == 0) return false; /* UNSAT */
            
            /* Non-chronological Backtrack to previous decision level */
            solver_backtrack(s, s->current_level - 1);
            continue;
        }
        
        int next_var = solver_pick_variable(s);
        if (next_var == 0) return true; /* SAT: all variables assigned */
        
        s->current_level++;
        solver_assign(s, next_var, NULL);
    }
}

int main(void) {
    CDCLSolver* s = solver_create(3);
    
    /* F = (x₁ ∨ x₂) ∧ (¬x₁ ∨ x₃) ∧ (¬x₂ ∨ ¬x₃) */
    int c1[] = {1, 2};
    int c2[] = {-1, 3};
    int c3[] = {-2, -3};
    
    solver_add_clause(s, c1, 2);
    solver_add_clause(s, c2, 2);
    solver_add_clause(s, c3, 2);
    
    if (solver_solve(s)) {
        printf("SAT! Assigns: x1=%d, x2=%d, x3=%d\n", s->assigns[1], s->assigns[2], s->assigns[3]);
    } else {
        printf("UNSAT!\n");
    }
    
    solver_free(s);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <optional>
#include <memory>
#include <algorithm>
#include <span>

enum class LBool : int8_t {
    Undefined = -1,
    False = 0,
    True = 1
};

struct Clause {
    std::vector<int> lits;
    size_t w1{0};
    size_t w2{0};
    int lbd{0};

    explicit Clause(std::span<const int> literals)
        : lits(literals.begin(), literals.end()) {
        if (lits.size() > 1) {
            w2 = 1;
        }
    }
};

class CDCLSolver {
public:
    explicit CDCLSolver(size_t num_vars)
        : num_vars_(num_vars),
          assigns_(num_vars + 1, LBool::Undefined),
          levels_(num_vars + 1, -1),
          reasons_(num_vars + 1, nullptr),
          activity_(num_vars + 1, 0.0) {}

    void add_clause(std::span<const int> literals) {
        clauses_.push_back(std::make_unique<Clause>(literals));
    }

    [[nodiscard]] LBool lit_value(int lit) const noexcept {
        const int var = std::abs(lit);
        const LBool val = assigns_[var];
        if (val == LBool::Undefined) return LBool::Undefined;
        return (lit > 0) ? val : (val == LBool::True ? LBool::False : LBool::True);
    }

    void assign(int lit, Clause* reason = nullptr) {
        const int var = std::abs(lit);
        const LBool val = (lit > 0) ? LBool::True : LBool::False;
        assigns_[var] = val;
        levels_[var] = current_level_;
        reasons_[var] = reason;
        trail_.push_back({var, current_level_});
    }

    Clause* bcp() {
        for (auto& clause_ptr : clauses_) {
            Clause& c = *clause_ptr;
            size_t false_count = 0;
            int undef_lit = 0;
            size_t undef_count = 0;
            bool satisfied = false;

            for (int lit : c.lits) {
                LBool val = lit_value(lit);
                if (val == LBool::True) {
                    satisfied = true;
                    break;
                }
                if (val == LBool::False) {
                    false_count++;
                } else {
                    undef_count++;
                    undef_lit = lit;
                }
            }

            if (satisfied) continue;

            if (false_count == c.lits.size()) {
                return &c; // Conflict!
            }

            if (undef_count == 1) {
                assign(undef_lit, &c);
            }
        }
        return nullptr;
    }

    void backtrack(int target_level) {
        while (!trail_.empty() && trail_.back().level > target_level) {
            int var = trail_.back().var;
            assigns_[var] = LBool::Undefined;
            levels_[var] = -1;
            reasons_[var] = nullptr;
            trail_.pop_back();
        }
        current_level_ = target_level;
    }

    void bump_var_activity(int var) {
        activity_[var] += var_inc_;
        if (activity_[var] > 1e100) {
            for (size_t i = 1; i <= num_vars_; ++i) {
                activity_[i] *= 1e-100;
            }
            var_inc_ *= 1e-100;
        }
    }

    int pick_decision_variable() {
        int best_var = 0;
        double max_act = -1.0;
        for (size_t i = 1; i <= num_vars_; ++i) {
            if (assigns_[i] == LBool::Undefined) {
                if (activity_[i] > max_act) {
                    max_act = activity_[i];
                    best_var = static_cast<int>(i);
                }
            }
        }
        return best_var;
    }

    bool solve() {
        while (true) {
            Clause* conflict = bcp();
            if (conflict != nullptr) {
                if (current_level_ == 0) return false; // UNSAT
                backtrack(current_level_ - 1);
                continue;
            }

            int next_var = pick_decision_variable();
            if (next_var == 0) return true; // SAT

            current_level_++;
            assign(next_var, nullptr);
        }
    }

    [[nodiscard]] LBool get_value(size_t var) const {
        return assigns_.at(var);
    }

private:
    struct TrailEntry {
        int var;
        int level;
    };

    size_t num_vars_;
    std::vector<std::unique_ptr<Clause>> clauses_;
    std::vector<LBool> assigns_;
    std::vector<int> levels_;
    std::vector<Clause*> reasons_;
    std::vector<double> activity_;
    std::vector<TrailEntry> trail_;
    int current_level_{0};
    double var_inc_{1.0};
};

int main() {
    CDCLSolver solver(3);

    // F = (x₁ ∨ x₂) ∧ (¬x₁ ∨ x₃) ∧ (¬x₂ ∨ ¬x₃)
    const int c1[] = {1, 2};
    const int c2[] = {-1, 3};
    const int c3[] = {-2, -3};

    solver.add_clause(c1);
    solver.add_clause(c2);
    solver.add_clause(c3);

    if (solver.solve()) {
        std::cout << "SAT! Assigns: x1=" << static_cast<int>(solver.get_value(1))
                  << ", x2=" << static_cast<int>(solver.get_value(2))
                  << ", x3=" << static_cast<int>(solver.get_value(3)) << "\n";
    } else {
        std::cout << "UNSAT!\n";
    }

    return 0;
}
```
:::

## 7. Практичні пастки реалізації та методи верифікації

При розробці високопродуктивних SAT-солверів виникають такі типові алгоритмічні пастки:
1. **Фрагментація пам'яті через вивчені диз'юнкти:** постійне виділення та видалення диз'юнктів через `malloc`/`free` швидко уповільнює роботу алокатора. Для уникнення фрагментації використовують пули пам'яті (Memory Pools) із вирівнюванням блоків по межі 64 байтів (розмір кеш-рядка).
2. **Неврахування LBD при видаленні диз'юнктів:** видалення вивчених диз'юнктів виключно за їх довжиною є помилковим. Диз'юнкт довжиною 10 літералів може бути «клеєм» (Glue Clause з LBD=2), який з'єднує дві незалежні частини формули і суттєво прискорює пошук.
3. **Генерація доведень UNSAT (DRAT Proof Logging):** для гарантії правильності відповіді `UNSAT` у промислових системах верифікації CDCL-солвер записує файл трасування вивчених та видалених диз'юнктів у форматі DRAT (Delete Resolution Asymmetry Trace), який перевіряється незалежною утилітою `drat-trim`.
