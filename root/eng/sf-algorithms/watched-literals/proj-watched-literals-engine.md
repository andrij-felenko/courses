# ⚙️ Реалізація двигуна Unit Propagation на базі 2WL

Практична побудова високопродуктивного двигуна поширення одиничних диз'юнктів (Boolean Constraint Propagation, BCP) на основі техніки двох спостережуваних літералів (2WL) мовами C та C++ спирається на оптимізовані структури даних та відсутність накладних витрат під час бектрекінгу.

## Архітектурний дизайн та структури даних двигуна BCP

Двигун 2WL призначений для виконання мільйонів операцій поширення обмежень за секунду. Для забезпечення такої швидкодії архітектура програмного комплексу будується на трьох фундаментальних інженерних принципах: мінімальні накладні витрати на розіменування покажчиків у системній пам'яті, суцільне розташування даних у купі (heap alignment) та абсолютно нульові затрати обчислювальних ресурсів під час скасування присвоєнь змінних (backtracking).

Розглянемо детальніше базові компоненти, з яких складається пропонований двигун BCP:

### 1. Бітове кодування літералів
Усі літерали представляються упакованими 32-бітними цілими числами без знаку. Якщо змінна має номер `v` (від 1 до `N`), її позитивна форма `x[v]` та негативна форма `¬x[v]` кодуються за допомогою побітового зсуву:
- `lit = (v << 1) | sign`, де `sign = 0` для позитивного літерала і `sign = 1` для заперечення.
- Протилежний літерал обчислюється однією миттєвою побітовою операцією інверсії `lit ^ 1`.
- Таке кодування дозволяє використовувати сам кодований літерал як прямий індекс для доступу до масиву списків спостереження `watches[lit]` за `O(1)` операцій.

### 2. Записи спостереження та блокуючі літерали
Списки спостереження `watches` зберігаються як масив динамічних векторів, де для кожного літерала `lit` підтримується список об'єктів `Watcher`. Кожен `Watcher` містить ідентифікатор диз'юнкта `clause_id` та копію другого спостережуваного літерала `blocker`. Під час перевірки диз'юнкта двигун спершу читає значення `blocker`: якщо воно дорівнює True, диз'юнкт вважається задоволеним, і алгоритм не звертається до головного масиву диз'юнкта в купі.

### 3. Стек присвоєнь (Trail) та рівні рішень
Усі призначені змінні зберігаються у неперервному стеку `trail`. Паралельно масив `assign_levels[v]` фіксує рівень рішення, на якому зміна відбулася. При скасуванні присвоєнь під час бектрекінгу двигун просто скорочує розмір стеку `trail` і повертає `values[v]` у стан Unassigned, взагалі не торкаючись списків `watches` та бази диз'юнктів.

## Повний реалізований приклад

Нижче наведено ідіоматичні реалізації двигуна BCP мовами C та C++. Обидва варіанти містять повну логіку ініціалізації, додавання диз'юнктів, виклику BCP та безвитратного бектрекінгу.

:::tabs
```c
/* c */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef int Literal;
typedef int Var;

#define LIT_VAR(lit) ((lit) >> 1)
#define LIT_SIGN(lit) ((lit) & 1)
#define LIT_MAKE(v, sign) (((v) << 1) | ((sign) ? 1 : 0))
#define LIT_NEG(lit) ((lit) ^ 1)

typedef enum {
    VAL_FALSE = -1,
    VAL_UNASSIGNED = 0,
    VAL_TRUE = 1
} VarValue;

typedef struct {
    int size;
    Literal* lits;
} Clause;

typedef struct {
    int clause_id;
    Literal blocker;
} Watcher;

typedef struct {
    Watcher* data;
    int capacity;
    int size;
} WatchList;

typedef struct {
    int num_vars;
    VarValue* values;
    int* assign_levels;
    
    Clause** clauses;
    int num_clauses;
    
    WatchList* watches; // Масив розміром 2 * (num_vars + 1)
    
    Literal* trail;
    int trail_size;
    int trail_head;
    
    int current_level;
} Solver;

Solver* solver_create(int num_vars) {
    Solver* s = (Solver*)malloc(sizeof(Solver));
    s->num_vars = num_vars;
    s->values = (VarValue*)calloc(num_vars + 1, sizeof(VarValue));
    s->assign_levels = (int*)calloc(num_vars + 1, sizeof(int));
    
    s->clauses = NULL;
    s->num_clauses = 0;
    
    int num_lits = 2 * (num_vars + 1);
    s->watches = (WatchList*)calloc(num_lits, sizeof(WatchList));
    
    s->trail = (Literal*)malloc(sizeof(Literal) * (num_vars + 1));
    s->trail_size = 0;
    s->trail_head = 0;
    s->current_level = 0;
    
    return s;
}

void solver_free(Solver* s) {
    for (int i = 0; i < s->num_clauses; i++) {
        free(s->clauses[i]->lits);
        free(s->clauses[i]);
    }
    free(s->clauses);
    
    int num_lits = 2 * (s->num_vars + 1);
    for (int i = 0; i < num_lits; i++) {
        free(s->watches[i].data);
    }
    free(s->watches);
    
    free(s->values);
    free(s->assign_levels);
    free(s->trail);
    free(s);
}

static void watch_list_add(WatchList* wl, int clause_id, Literal blocker) {
    if (wl->size >= wl->capacity) {
        wl->capacity = (wl->capacity == 0) ? 4 : wl->capacity * 2;
        wl->data = (Watcher*)realloc(wl->data, sizeof(Watcher) * wl->capacity);
    }
    wl->data[wl->size].clause_id = clause_id;
    wl->data[wl->size].blocker = blocker;
    wl->size++;
}

VarValue solver_lit_value(Solver* s, Literal lit) {
    Var v = LIT_VAR(lit);
    VarValue val = s->values[v];
    if (val == VAL_UNASSIGNED) return VAL_UNASSIGNED;
    return LIT_SIGN(lit) ? -val : val;
}

void solver_enqueue(Solver* s, Literal lit) {
    Var v = LIT_VAR(lit);
    s->values[v] = LIT_SIGN(lit) ? VAL_FALSE : VAL_TRUE;
    s->assign_levels[v] = s->current_level;
    s->trail[s->trail_size++] = lit;
}

void add_clause(Solver* s, Literal* lits, int size) {
    Clause* c = (Clause*)malloc(sizeof(Clause));
    c->size = size;
    c->lits = (Literal*)malloc(sizeof(Literal) * size);
    for (int i = 0; i < size; i++) {
        c->lits[i] = lits[i];
    }
    
    int cid = s->num_clauses++;
    s->clauses = (Clause**)realloc(s->clauses, sizeof(Clause*) * s->num_clauses);
    s->clauses[cid] = c;
    
    if (size >= 2) {
        watch_list_add(&s->watches[lits[0]], cid, lits[1]);
        watch_list_add(&s->watches[lits[1]], cid, lits[0]);
    }
}

bool solver_propagate(Solver* s, int* conflict_clause_out) {
    while (s->trail_head < s->trail_size) {
        Literal p = s->trail[s->trail_head++];
        Literal false_lit = LIT_NEG(p);
        WatchList* wl = &s->watches[false_lit];
        
        int i = 0, j = 0;
        while (i < wl->size) {
            Watcher w = wl->data[i];
            Clause* c = s->clauses[w.clause_id];
            
            // Перевірка блокуючого літерала
            if (solver_lit_value(s, w.blocker) == VAL_TRUE) {
                wl->data[j++] = w;
                i++;
                continue;
            }
            
            // Перестановка: пересвідчимося, що false_lit є у lits[0]
            if (c->lits[1] == false_lit) {
                c->lits[1] = c->lits[0];
                c->lits[0] = false_lit;
            }
            
            Literal first = c->lits[0];
            Literal second = c->lits[1];
            
            if (solver_lit_value(s, second) == VAL_TRUE) {
                wl->data[j++] = (Watcher){ w.clause_id, second };
                i++;
                continue;
            }
            
            // Сканування нових кандидатів для заміни w[1]
            bool found_new = false;
            for (int k = 2; k < c->size; k++) {
                if (solver_lit_value(s, c->lits[k]) != VAL_FALSE) {
                    c->lits[0] = c->lits[k];
                    c->lits[k] = false_lit;
                    watch_list_add(&s->watches[c->lits[0]], w.clause_id, second);
                    found_new = true;
                    break;
                }
            }
            
            if (found_new) {
                i++;
                continue;
            }
            
            // Заміни немає
            wl->data[j++] = w;
            i++;
            
            if (solver_lit_value(s, second) == VAL_FALSE) {
                // Конфлікт!
                while (i < wl->size) {
                    wl->data[j++] = wl->data[i++];
                }
                wl->size = j;
                if (conflict_clause_out) *conflict_clause_out = w.clause_id;
                return false;
            } else {
                // Одиничне поширення!
                solver_enqueue(s, second);
            }
        }
        wl->size = j;
    }
    return true;
}

void solver_backtrack(Solver* s, int target_level) {
    while (s->trail_size > 0) {
        Literal lit = s->trail[s->trail_size - 1];
        Var v = LIT_VAR(lit);
        if (s->assign_levels[v] <= target_level) break;
        
        s->values[v] = VAL_UNASSIGNED;
        s->assign_levels[v] = 0;
        s->trail_size--;
    }
    s->trail_head = s->trail_size;
    s->current_level = target_level;
}

int main(void) {
    Solver* s = solver_create(4);
    
    // (x1 v x2 v x3)
    Literal c1[] = { LIT_MAKE(1, false), LIT_MAKE(2, false), LIT_MAKE(3, false) };
    add_clause(s, c1, 3);
    
    // (¬x1 v x4)
    Literal c2[] = { LIT_MAKE(1, true), LIT_MAKE(4, false) };
    add_clause(s, c2, 2);
    
    // Прийняття рішення: x1 := 1 (True)
    s->current_level = 1;
    solver_enqueue(s, LIT_MAKE(1, false));
    
    int conflict_cid = -1;
    bool ok = solver_propagate(s, &conflict_cid);
    
    printf("BCP Result: %s\n", ok ? "SUCCESS" : "CONFLICT");
    printf("Value x4: %d\n", s->values[4]);
    
    // Безвитратний бектрекінг
    solver_backtrack(s, 0);
    printf("After backtrack Value x1: %d, x4: %d\n", s->values[1], s->values[4]);
    
    solver_free(s);
    return 0;
}
```
```cpp
// cpp
#include <iostream>
#include <vector>
#include <cstdint>
#include <expected>
#include <span>
#include <memory>

enum class LVal : int8_t { False = -1, Unassigned = 0, True = 1 };

class Literal {
    uint32_t code_;
public:
    constexpr Literal() : code_(0) {}
    constexpr Literal(uint32_t var, bool is_neg) : code_((var << 1) | (is_neg ? 1 : 0)) {}
    
    [[nodiscard]] constexpr uint32_t var() const noexcept { return code_ >> 1; }
    [[nodiscard]] constexpr bool is_neg() const noexcept { return (code_ & 1) != 0; }
    [[nodiscard]] constexpr Literal neg() const noexcept { Literal l; l.code_ = code_ ^ 1; return l; }
    [[nodiscard]] constexpr uint32_t code() const noexcept { return code_; }
    
    constexpr bool operator==(const Literal& o) const noexcept { return code_ == o.code_; }
};

struct Watcher {
    uint32_t clause_id;
    Literal  blocker;
};

class Clause {
    std::vector<Literal> lits_;
public:
    explicit Clause(std::span<const Literal> lits) : lits_(lits.begin(), lits.end()) {}
    
    [[nodiscard]] size_t size() const noexcept { return lits_.size(); }
    [[nodiscard]] Literal& operator[](size_t idx) noexcept { return lits_[idx]; }
    [[nodiscard]] const Literal& operator[](size_t idx) const noexcept { return lits_[idx]; }
    [[nodiscard]] std::span<Literal> literals() noexcept { return lits_; }
};

class WatchedLiteralsEngine {
    uint32_t num_vars_;
    std::vector<LVal> values_;
    std::vector<uint32_t> levels_;
    
    std::vector<Clause> clauses_;
    std::vector<std::vector<Watcher>> watches_;
    
    std::vector<Literal> trail_;
    size_t trail_head_{0};
    uint32_t current_level_{0};

public:
    explicit WatchedLiteralsEngine(uint32_t num_vars)
        : num_vars_(num_vars),
          values_(num_vars + 1, LVal::Unassigned),
          levels_(num_vars + 1, 0),
          watches_(2 * (num_vars + 1)) {}

    [[nodiscard]] LVal value(Literal lit) const noexcept {
        LVal v = values_[lit.var()];
        if (v == LVal::Unassigned) return LVal::Unassigned;
        return lit.is_neg() ? static_cast<LVal>(-static_cast<int8_t>(v)) : v;
    }

    void add_clause(std::span<const Literal> lits) {
        uint32_t cid = static_cast<uint32_t>(clauses_.size());
        clauses_.emplace_back(lits);
        
        if (lits.size() >= 2) {
            watches_[lits[0].code()].push_back({cid, lits[1]});
            watches_[lits[1].code()].push_back({cid, lits[0]});
        }
    }

    void enqueue(Literal lit) {
        values_[lit.var()] = lit.is_neg() ? LVal::False : LVal::True;
        levels_[lit.var()] = current_level_;
        trail_.push_back(lit);
    }

    void set_decision_level(uint32_t level) noexcept {
        current_level_ = level;
    }

    [[nodiscard]] std::expected<void, uint32_t> propagate() {
        while (trail_head_ < trail_.size()) {
            Literal p = trail_[trail_head_++];
            Literal false_lit = p.neg();
            auto& wl = watches_[false_lit.code()];
            
            size_t i = 0, j = 0;
            while (i < wl.size()) {
                Watcher w = wl[i];
                Clause& c = clauses_[w.clause_id];
                
                if (value(w.blocker) == LVal::True) {
                    wl[j++] = w;
                    i++;
                    continue;
                }
                
                if (c[1] == false_lit) {
                    std::swap(c[0], c[1]);
                }
                
                Literal second = c[1];
                if (value(second) == LVal::True) {
                    wl[j++] = Watcher{w.clause_id, second};
                    i++;
                    continue;
                }
                
                bool found_new = false;
                for (size_t k = 2; k < c.size(); ++k) {
                    if (value(c[k]) != LVal::False) {
                        c[0] = c[k];
                        c[k] = false_lit;
                        watches_[c[0].code()].push_back({w.clause_id, second});
                        found_new = true;
                        break;
                    }
                }
                
                if (found_new) {
                    i++;
                    continue;
                }
                
                wl[j++] = w;
                i++;
                
                if (value(second) == LVal::False) {
                    while (i < wl.size()) wl[j++] = wl[i++];
                    wl.resize(j);
                    return std::unexpected(w.clause_id);
                } else {
                    enqueue(second);
                }
            }
            wl.resize(j);
        }
        return {};
    }

    void backtrack(uint32_t target_level) {
        while (!trail_.empty()) {
            Literal lit = trail_.back();
            if (levels_[lit.var()] <= target_level) break;
            
            values_[lit.var()] = LVal::Unassigned;
            levels_[lit.var()] = 0;
            trail_.pop_back();
        }
        trail_head_ = trail_.size();
        current_level_ = target_level;
    }
};

int main() {
    WatchedLiteralsEngine engine(4);
    
    // (x1 v x2 v x3)
    Literal c1_lits[] = { Literal(1, false), Literal(2, false), Literal(3, false) };
    engine.add_clause(c1_lits);
    
    // (¬x1 v x4)
    Literal c2_lits[] = { Literal(1, true), Literal(4, false) };
    engine.add_clause(c2_lits);
    
    engine.set_decision_level(1);
    engine.enqueue(Literal(1, false)); // x1 := True
    
    auto res = engine.propagate();
    if (res.has_value()) {
        std::cout << "BCP Propagated successfully!\n";
    } else {
        std::cout << "Conflict in clause: " << res.error() << "\n";
    }
    
    engine.backtrack(0);
    std::cout << "Backtracked to level 0 without clause database writes.\n";
    return 0;
}
```
:::

## Покроковий аналіз виконання двигуна BCP

Розглянемо в деталях, які саме обчислювальні процеси відбуваються всередині циклу поширення `solver_propagate` під час роботи зі списками спостереження 2WL:

1. **Отримання хибного літерала зі стеку:**
   Коли з черги `trail` витягується літерал `p`, який щойно набув значення True, його логічне заперечення `false_lit = LIT_NEG(p)` стає False. Солвер відкриває вектор `watches[false_lit]`.

2. **Двівказівникова фільтрація списку (Two-Pointer Filtering):**
   Обхід вектора `wl` здійснюється за допомогою двох індексів: `i` (індекс читання) та `j` (індекс запису).
   - Якщо диз'юнкт змінює свій спостережуваний літерал `w[1]` на новий літерал `L_new`, він вилучається зі списку `watches[false_lit]`. Для цього елемент не копіюється у позицію `j`, а індекс `i` просто інкрементується.
   - Якщо диз'юнкт залишається у списку `watches[false_lit]`, його запис переноситься на позицію `j++`. Наприкінці циклу розмір вектора скорочується до `wl.size = j`. Це виключає потребу у використанні повільних операцій видалення з середини масиву (`vector::erase`).

3. **Нормалізація покажчиків:**
   Перед скануванням двигун перевіряє, який саме з двох покажчиків дорівнює `false_lit`. Якщо `c->lits[1] == false_lit`, вони міняються місцями `swap(lits[0], lits[1])`. Це гарантує, що хибний літерал завжди перебуває за індексом 0, а другий спостережуваний літерал — за індексом 1.

4. **Перевірка блокуючого літерала:**
   Командою `solver_lit_value(s, w.blocker) == VAL_TRUE` алгоритм миттєво перевіряє стан істинності другого літерала. Якщо блокуючий літерал вже є True, диз'юнкт гарантовано істинний, і цикл негайно переходить до наступного елемента без читання масиву `c->lits`.

5. **Сканування масиву в пошуку заміни:**
   Якщо `blocker` не є True, цикл ітерується по індексах від `k=2` до `size-1`. Перший знайдений літерал `c->lits[k]`, стан якого є Unassigned або True, стає новим спостережуваним літералом. Виконується `swap(c->lits[0], c->lits[k])`, і диз'юнкт додається до масиву `watches[c->lits[0]]`.

6. **Фіксація одиничного поширення або конфлікту:**
   Якщо жоден із `k-2` літералів не підходить на роль заміни:
   - Якщо `second` має стан Unassigned, він додається до `trail` командою `solver_enqueue(s, second)`.
   - Якщо `second` має стан False, фіксується конфлікт: цикл переривається, і функція повертає ідентифікатор конфліктного диз'юнкта.

## Практичні пастки та висунуті вимоги

При практичній реалізації двигуна 2WL виникають кілька специфічних пасток, на які слід звернути особливу увагу:

1. **Інвалідація ітераторів при `push_back`:**
   Під час сканування альтернатив виконується додавання диз'юнкта до іншого списку `watches[c->lits[0]].push_back(...)`. Якщо новий спостережуваний літерал збігається з поточним оброблюваним літералом, масив `wl` може перевиділити пам'ять. Використання цілочисельних індексів `i` та `j` замість вказівників повністю захищає код від інвалідації пам'яті та виникнення зависших вказівників.
2. **Оновлення блокуючого літерала:**
   Якщо під час сканування заміна не була знайдена, але диз'юнкт виявився задоволеним завдяки другому літералу `second` (тобто `value(second) == True`), блокуючий літерал у записі `Watcher` обов'язково має бути оновлений `w.blocker = second`. Це дозволить майбутнім ітераціям BCP пропускати цей диз'юнкт ще швидше.
3. **Продуктивність бінарних дизюнктів:**
   Для КНФ-формул із великою кількістю бінарних диз'юнктів (`size == 2`) цикл сканування від `k=2` не виконується жодного разу. Солвер одразу переходить до перевірки `second`. Для таких диз'юнктів рекомендується створювати окремі виділені списки суміжності без виділення пам'яті під об'єкти `Clause`.
4. **Безефектифікація при бектрекінгу:**
   При скасуванні рішень функція `solver_backtrack` зменшує `trail_size` і скидає значення змінних. Список `watches` не зазнає жодних змін, що забезпечує амортизований нульовий оклад пам'яті під час скасування.
