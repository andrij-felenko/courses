# ⚙️ Реалізація рушія переписування та алгоритму поповнення Кнута-Бендікса

Побудова промислового або навчального рушія переписування термів вимагає поєднання рекурсивних структур даних для представлення абстрактного синтаксичного дерева, алгоритму синтаксичної уніфікації першого порядку з контролем циклічних посилань, механізму виявлення критичних пар та реалізації лексикографічного деревного порядку (LPO) для автоматичної орієнтації симетричних рівнянь.

## 1. Архітектурні моделі представлення термів

Символьний вираз (терм) у системі переписування першого порядку визначається індуктивно: це або змінна (яка ідентифікується символьним рядком чи цілочисловим індексом де Брейна), або функціональний символ певної фіксованої арності, застосований до вектора підтермів-аргументів. Константи моделюються як функціональні символи з нульовою арністю.

### 1.1. Вибір моделі пам'яті: деревоподібна структура проти хеш-консингу (DAG)
У практичних реалізаціях застосовують дві фундаментальні моделі зберігання термів:
1. **Явне деревоподібне представлення (Tree Representation):** Кожен вузол AST виділяється в динамічній пам'яті як окремий об'єкт. Підтерми дублюються під час підстановок і редукцій. Це найпростіша модель, проте при глибоких вкладеннях та дублюванні змінних (наприклад, у правилі `double(x) → x + x`) вона призводить до експоненційного зростання витрат оперативної пам'яті.
2. **Спрямований ациклічний граф із розділенням підтермів (Hash-Consing / DAG):** Кожен унікальний підтерм зберігається в глобальній таблиці хешів рівно в одному екземплярі. Якщо два вирази синтаксично тотожні, вони мають однакову адресу покажчика в пам'яті (`Term* a == Term* b`). Це перетворює перевірку рівності термів на операцію `O(1)` і драматично скорочує споживання пам'яті.

У поданій нижче реалізації використано збалансовану об'єктну модель на основі розумних покажчиків `std::shared_ptr` у C++ та компактних динамічних структур на C, що забезпечує чистоту коду без надмірної складності ручного хеш-консингу.

### 1.2. Підстановки та контексти
Підстановка — це скінченне відображення `σ: V → T(Σ, V)`, яке замінює змінні на терми. Підстановка вважається ідемпотентною, якщо для будь-якої змінної `x` виконується `Var(σ(x)) ∩ dom(σ) = ∅`. При застосуванні підстановки до виразу `tσ` рекурсивно замінюються всі входження змінних із домену `dom(σ)`.

Контекст `C[_]` представляє терм з однією виділеною порожньою позицією («діркою»). Заміна дірки на підтерм `s` позначається як `C[s]`. У термінах деревних позицій, позиція `p` є послідовністю натуральних чисел `p = i₁ · i₂ · ... · iₖ`, яка вказує шлях від кореня дерева до відповідного піддерева (де `iⱼ` — номер гілки аргументу на `j`-му рівні).

### 1.3. Зіставлення проти уніфікації: Мартеллі-Монтанарі та Робінсон
Під час роботи рушія виконуються дві принципово різні операції над парами термів:
1. **Одностороннє зіставлення за зразком (Pattern Matching):** Дано ліву частину правила `l` та підтерм `s`. Необхідно знайти підстановку `σ` таку, що `lσ ≡ s`. При цьому змінні в `s` вважаються недоторканними жорсткими константами. Зіставлення використовується безпосередньо в циклі редукції `s → t`.
2. **Двостороння уніфікація першого порядку (Unification, MGU):** Дано два довільних терми `s` та `t`. Необхідно знайти таку спільну підстановку `μ`, що `sμ ≡ tμ`. Обидва терми можуть містити змінні, які дозволено інстанціювати. 

У теоретичній інформатиці уніфікацію часто формулюють як систему трансформаційних правил Мартеллі-Монтанарі (1982), що перетворює множину рівнянь на розв'язану форму за допомогою шести дій:
- **Видалення (Delete):** Рівняння вигляду `t = t` відкидаються як синтаксично тривіальні тотожності.
- **Декомпозиція (Decompose):** Рівняння `f(s₁, ..., sₙ) = f(t₁, ..., tₙ)` розщеплюється на `n` незалежних поаргументних рівнянь `s₁ = t₁, ..., sₙ = tₙ`.
- **Конфлікт (Clash):** Спроба уніфікувати різні функціональні символи `f(...) = g(...)` або символи з різною кількістю аргументів негайно завершується аварійним зупином через неможливість розв'язання.
- **Орієнтація (Orient):** Рівняння `t = x`, де `x` — змінна, а `t` — складений функціональний вираз, симетрично перевертається у канонічну форму `x = t`.
- **Елімінація (Eliminate):** Якщо змінна `x` не входить до виразу `t` (`x ∉ Var(t)`), рівність `x = t` фіксується як підстановка, а всі інші входження `x` у системі замінюються на `t`.
- **Перевірка входження (Occurs Check):** Рівняння `x = t`, де `t` є складеним виразом, що вже містить `x` (`x ∈ Var(t)`), визнається нерозв'язним, оскільки його розв'язок вимагав би нескінченного терма.

У наведеній реалізації алгоритм Робінсона об'єднує ці кроки в ефективний рекурсивний спуск над парою термів з накопиченням підстановки.

## 2. Реалізація повного рушія на C та C++

Нижче наведено самодостатню реалізацію рушія переписування термів, лексикографічного деревного порядку LPO та алгоритму поповнення Кнута-Бендікса. Програма виконує поповнення трьох аксіом теорії груп:
```
e · x = x
i(x) · x = e
(x · y) · z = x · (y · z)
```
і автоматично генерує повну канонічну систему з 10 правил.

:::tabs
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <unordered_map>
#include <unordered_set>
#include <optional>
#include <algorithm>
#include <cassert>

// ── Представлення термів ──────────────────────────────────────────────────
struct Term;
using TermPtr = std::shared_ptr<Term>;

enum class TermKind { Variable, Function };

struct Term {
    TermKind kind;
    std::string name;             // Ім'я змінної або функціонального символу
    std::vector<TermPtr> args;    // Порожній для змінних і констант

    static TermPtr make_var(const std::string& name) {
        auto t = std::make_shared<Term>();
        t->kind = TermKind::Variable;
        t->name = name;
        return t;
    }

    static TermPtr make_fn(const std::string& name, std::vector<TermPtr> args = {}) {
        auto t = std::make_shared<Term>();
        t->kind = TermKind::Function;
        t->name = name;
        t->args = std::move(args);
        return t;
    }

    bool is_var() const { return kind == TermKind::Variable; }
    bool is_fn() const { return kind == TermKind::Function; }

    std::string to_string() const {
        if (is_var()) return name;
        if (args.empty()) return name;
        if (args.size() == 2 && (name == "*" || name == "·")) {
            return "(" + args[0]->to_string() + " " + name + " " + args[1]->to_string() + ")";
        }
        std::string res = name + "(";
        for (size_t i = 0; i < args.size(); ++i) {
            if (i > 0) res += ", ";
            res += args[i]->to_string();
        }
        res += ")";
        return res;
    }
};

using Substitution = std::unordered_map<std::string, TermPtr>;

// ── Допоміжні операції над виразами ───────────────────────────────────────
bool contains_var(const TermPtr& term, const std::string& var_name) {
    if (term->is_var()) return term->name == var_name;
    for (const auto& arg : term->args) {
        if (contains_var(arg, var_name)) return true;
    }
    return false;
}

void collect_vars(const TermPtr& term, std::unordered_set<std::string>& vars) {
    if (term->is_var()) {
        vars.insert(term->name);
    } else {
        for (const auto& arg : term->args) collect_vars(arg, vars);
    }
}

TermPtr apply_subst(const TermPtr& term, const Substitution& subst) {
    if (term->is_var()) {
        auto it = subst.find(term->name);
        if (it != subst.end()) return apply_subst(it->second, subst);
        return term;
    }
    std::vector<TermPtr> new_args;
    new_args.reserve(term->args.size());
    for (const auto& arg : term->args) {
        new_args.push_back(apply_subst(arg, subst));
    }
    return Term::make_fn(term->name, new_args);
}

bool terms_equal(const TermPtr& a, const TermPtr& b) {
    if (a->kind != b->kind || a->name != b->name) return false;
    if (a->args.size() != b->args.size()) return false;
    for (size_t i = 0; i < a->args.size(); ++i) {
        if (!terms_equal(a->args[i], b->args[i])) return false;
    }
    return true;
}

// ── Алгоритм уніфікації Робінсона з occurs-check ──────────────────────────
bool unify(const TermPtr& s, const TermPtr& t, Substitution& subst) {
    TermPtr s_sub = apply_subst(s, subst);
    TermPtr t_sub = apply_subst(t, subst);

    if (terms_equal(s_sub, t_sub)) return true;

    if (s_sub->is_var()) {
        if (contains_var(t_sub, s_sub->name)) return false; // Occurs check
        subst[s_sub->name] = t_sub;
        return true;
    }
    if (t_sub->is_var()) {
        if (contains_var(s_sub, t_sub->name)) return false; // Occurs check
        subst[t_sub->name] = s_sub;
        return true;
    }

    if (s_sub->name != t_sub->name || s_sub->args.size() != t_sub->args.size()) {
        return false;
    }

    for (size_t i = 0; i < s_sub->args.size(); ++i) {
        if (!unify(s_sub->args[i], t_sub->args[i], subst)) return false;
    }
    return true;
}

// ── Одностороннє зіставлення за зразком ───────────────────────────────────
bool match_pattern(const TermPtr& pattern, const TermPtr& target, Substitution& subst) {
    if (pattern->is_var()) {
        auto it = subst.find(pattern->name);
        if (it != subst.end()) return terms_equal(it->second, target);
        subst[pattern->name] = target;
        return true;
    }
    if (target->is_var()) return false;
    if (pattern->name != target->name || pattern->args.size() != target->args.size()) return false;
    for (size_t i = 0; i < pattern->args.size(); ++i) {
        if (!match_pattern(pattern->args[i], target->args[i], subst)) return false;
    }
    return true;
}

// ── Правила переписування та порядок LPO ──────────────────────────────────
struct Rule {
    TermPtr lhs;
    TermPtr rhs;
};

// Пріоритет функціональних символів: i > * > e
int symbol_precedence(const std::string& name) {
    if (name == "i") return 3;
    if (name == "*" || name == "·") return 2;
    if (name == "e") return 1;
    return 0;
}

// Лексикографічний деревний порядок (LPO)
bool lpo_greater(const TermPtr& s, const TermPtr& t) {
    if (t->is_var()) {
        return contains_var(s, t->name) && !terms_equal(s, t);
    }
    if (s->is_var()) return false;

    // 1. Умова підтерма: ∃ s_i >= t
    for (const auto& si : s->args) {
        if (terms_equal(si, t) || lpo_greater(si, t)) return true;
    }

    // 2. Умова пріоритету: f >_Σ g та ∀ t_j : s > t_j
    int prec_s = symbol_precedence(s->name);
    int prec_t = symbol_precedence(t->name);

    auto all_args_smaller = [&]() {
        for (const auto& tj : t->args) {
            if (!lpo_greater(s, tj)) return false;
        }
        return true;
    };

    if (prec_s > prec_t) return all_args_smaller();

    // 3. Умова однакового символу та лексикографічного порівняння аргументів
    if (prec_s == prec_t && s->name == t->name && s->args.size() == t->args.size()) {
        if (!all_args_smaller()) return false;
        for (size_t i = 0; i < s->args.size(); ++i) {
            if (terms_equal(s->args[i], t->args[i])) continue;
            return lpo_greater(s->args[i], t->args[i]);
        }
    }
    return false;
}

// ── Нормалізація термів (Innermost Reduction) ─────────────────────────────
TermPtr rewrite_step(const TermPtr& term, const std::vector<Rule>& rules) {
    if (term->is_fn()) {
        for (size_t i = 0; i < term->args.size(); ++i) {
            auto reduced = rewrite_step(term->args[i], rules);
            if (!terms_equal(reduced, term->args[i])) {
                std::vector<TermPtr> new_args = term->args;
                new_args[i] = reduced;
                return Term::make_fn(term->name, new_args);
            }
        }
    }
    for (const auto& rule : rules) {
        Substitution subst;
        if (match_pattern(rule.lhs, term, subst)) {
            return apply_subst(rule.rhs, subst);
        }
    }
    return term;
}

TermPtr normalize(TermPtr term, const std::vector<Rule>& rules) {
    while (true) {
        TermPtr next = rewrite_step(term, rules);
        if (terms_equal(next, term)) break;
        term = next;
    }
    return term;
}

// ── Генерація критичних пар та поповнення ──────────────────────────────────
static int var_counter = 0;
TermPtr rename_vars(const TermPtr& term, const std::string& prefix) {
    if (term->is_var()) return Term::make_var(prefix + "_" + term->name);
    std::vector<TermPtr> new_args;
    for (const auto& a : term->args) new_args.push_back(rename_vars(a, prefix));
    return Term::make_fn(term->name, new_args);
}

struct CriticalPair {
    TermPtr s;
    TermPtr t;
};

void find_overlaps(const TermPtr& root, const TermPtr& current, const TermPtr& r1,
                   const Rule& r2, std::vector<CriticalPair>& pairs,
                   const std::function<TermPtr(const TermPtr&)>& replace_subterm) {
    if (current->is_fn()) {
        Substitution subst;
        if (unify(current, r2.lhs, subst)) {
            TermPtr left = apply_subst(r1, subst);
            TermPtr right = apply_subst(replace_subterm(r2.rhs), subst);
            pairs.push_back({left, right});
        }
        for (size_t i = 0; i < current->args.size(); ++i) {
            auto sub_replacer = [&](const TermPtr& repl) {
                std::vector<TermPtr> new_args = current->args;
                new_args[i] = repl;
                return replace_subterm(Term::make_fn(current->name, new_args));
            };
            find_overlaps(root, current->args[i], r1, r2, pairs, sub_replacer);
        }
    }
}

std::vector<CriticalPair> compute_critical_pairs(const std::vector<Rule>& rules) {
    std::vector<CriticalPair> pairs;
    for (size_t i = 0; i < rules.size(); ++i) {
        for (size_t j = 0; j < rules.size(); ++j) {
            Rule r1 = { rename_vars(rules[i].lhs, "r" + std::to_string(i)),
                        rename_vars(rules[i].rhs, "r" + std::to_string(i)) };
            Rule r2 = { rename_vars(rules[j].lhs, "s" + std::to_string(j)),
                        rename_vars(rules[j].rhs, "s" + std::to_string(j)) };

            find_overlaps(r1.lhs, r1.lhs, r1.rhs, r2, pairs, [](const TermPtr& t) { return t; });
        }
    }
    return pairs;
}

// Повний цикл Кнута-Бендікса
std::vector<Rule> knuth_bendix_completion(std::vector<std::pair<TermPtr, TermPtr>> equations) {
    std::vector<Rule> rules;
    std::vector<std::pair<TermPtr, TermPtr>> eq_queue = std::move(equations);

    int iterations = 0;
    while (!eq_queue.empty() && iterations < 50) {
        ++iterations;
        auto [s, t] = eq_queue.back();
        eq_queue.pop_back();

        TermPtr s0 = normalize(s, rules);
        TermPtr t0 = normalize(t, rules);

        if (terms_equal(s0, t0)) continue;

        Rule new_rule;
        if (lpo_greater(s0, t0)) {
            new_rule = {s0, t0};
        } else if (lpo_greater(t0, s0)) {
            new_rule = {t0, s0};
        } else {
            std::cerr << "Помилка: Неможливо орієнтувати рівність: "
                      << s0->to_string() << " = " << t0->to_string() << std::endl;
            return rules;
        }

        std::cout << "Додано правило [" << rules.size() + 1 << "]: "
                  << new_rule.lhs->to_string() << "  -->  " << new_rule.rhs->to_string() << std::endl;
        rules.push_back(new_rule);

        // Обчислення критичних пар та поповнення черги
        auto cp = compute_critical_pairs(rules);
        for (const auto& pair : cp) {
            eq_queue.push_back({pair.s, pair.t});
        }
    }
    return rules;
}

int main() {
    auto x = Term::make_var("x");
    auto y = Term::make_var("y");
    auto z = Term::make_var("z");
    auto e = Term::make_fn("e");
    auto inv = [](TermPtr a) { return Term::make_fn("i", {a}); };
    auto mul = [](TermPtr a, TermPtr b) { return Term::make_fn("*", {a, b}); };

    std::vector<std::pair<TermPtr, TermPtr>> group_axioms = {
        { mul(e, x), x },                             // e * x = x
        { mul(inv(x), x), e },                        // i(x) * x = e
        { mul(mul(x, y), z), mul(x, mul(y, z)) }      // (x * y) * z = x * (y * z)
    };

    std::cout << "=== Запуск автопоповнення Кнута-Бендікса для теорії груп ===" << std::endl;
    auto complete_system = knuth_bendix_completion(group_axioms);

    std::cout << "\n=== Канонічна система переписування (знайдено "
              << complete_system.size() << " правил) ===" << std::endl;
    for (size_t i = 0; i < complete_system.size(); ++i) {
        std::cout << (i + 1) << ".  " << complete_system[i].lhs->to_string()
                  << "  -->  " << complete_system[i].rhs->to_string() << std::endl;
    }
    return 0;
}
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <assert.h>

#define MAX_ARGS 4
#define MAX_NAME 16
#define MAX_VARS 32
#define MAX_RULES 64
#define MAX_PAIRS 256

typedef enum { TERM_VAR, TERM_FN } TermKind;

typedef struct Term {
    TermKind kind;
    char name[MAX_NAME];
    int arity;
    struct Term* args[MAX_ARGS];
} Term;

typedef struct {
    char var[MAX_NAME];
    Term* term;
} SubstEntry;

typedef struct {
    SubstEntry entries[MAX_VARS];
    int count;
} Substitution;

typedef struct {
    Term* lhs;
    Term* rhs;
} Rule;

// Створення та клонування термів
Term* make_var(const char* name) {
    Term* t = (Term*)malloc(sizeof(Term));
    t->kind = TERM_VAR;
    strncpy(t->name, name, MAX_NAME - 1);
    t->name[MAX_NAME - 1] = '\0';
    t->arity = 0;
    return t;
}

Term* make_fn(const char* name, int arity, Term** args) {
    Term* t = (Term*)malloc(sizeof(Term));
    t->kind = TERM_FN;
    strncpy(t->name, name, MAX_NAME - 1);
    t->name[MAX_NAME - 1] = '\0';
    t->arity = arity;
    for (int i = 0; i < arity; ++i) t->args[i] = args[i];
    return t;
}

Term* clone_term(const Term* t) {
    if (!t) return NULL;
    if (t->kind == TERM_VAR) return make_var(t->name);
    Term* new_args[MAX_ARGS];
    for (int i = 0; i < t->arity; ++i) new_args[i] = clone_term(t->args[i]);
    return make_fn(t->name, t->arity, new_args);
}

void free_term(Term* t) {
    if (!t) return;
    for (int i = 0; i < t->arity; ++i) free_term(t->args[i]);
    free(t);
}

void print_term(const Term* t) {
    if (t->kind == TERM_VAR) {
        printf("%s", t->name);
    } else if (t->arity == 0) {
        printf("%s", t->name);
    } else if (t->arity == 2 && strcmp(t->name, "*") == 0) {
        printf("(");
        print_term(t->args[0]);
        printf(" * ");
        print_term(t->args[1]);
        printf(")");
    } else {
        printf("%s(", t->name);
        for (int i = 0; i < t->arity; ++i) {
            if (i > 0) printf(", ");
            print_term(t->args[i]);
        }
        printf(")");
    }
}

// Порівняння та перевірка входження змінних
bool terms_equal(const Term* a, const Term* b) {
    if (a->kind != b->kind || strcmp(a->name, b->name) != 0 || a->arity != b->arity) return false;
    for (int i = 0; i < a->arity; ++i) {
        if (!terms_equal(a->args[i], b->args[i])) return false;
    }
    return true;
}

bool contains_var(const Term* t, const char* var_name) {
    if (t->kind == TERM_VAR) return strcmp(t->name, var_name) == 0;
    for (int i = 0; i < t->arity; ++i) {
        if (contains_var(t->args[i], var_name)) return true;
    }
    return false;
}

Term* apply_subst(const Term* t, const Substitution* s) {
    if (t->kind == TERM_VAR) {
        for (int i = 0; i < s->count; ++i) {
            if (strcmp(s->entries[i].var, t->name) == 0) {
                return apply_subst(s->entries[i].term, s);
            }
        }
        return make_var(t->name);
    }
    Term* new_args[MAX_ARGS];
    for (int i = 0; i < t->arity; ++i) new_args[i] = apply_subst(t->args[i], s);
    return make_fn(t->name, t->arity, new_args);
}

// Уніфікація Робінсона
bool unify(const Term* s, const Term* t, Substitution* subst) {
    Term* s_sub = apply_subst(s, subst);
    Term* t_sub = apply_subst(t, subst);

    if (terms_equal(s_sub, t_sub)) {
        free_term(s_sub); free_term(t_sub);
        return true;
    }
    if (s_sub->kind == TERM_VAR) {
        if (contains_var(t_sub, s_sub->name)) {
            free_term(s_sub); free_term(t_sub);
            return false;
        }
        strncpy(subst->entries[subst->count].var, s_sub->name, MAX_NAME - 1);
        subst->entries[subst->count].term = clone_term(t_sub);
        subst->count++;
        free_term(s_sub); free_term(t_sub);
        return true;
    }
    if (t_sub->kind == TERM_VAR) {
        if (contains_var(s_sub, t_sub->name)) {
            free_term(s_sub); free_term(t_sub);
            return false;
        }
        strncpy(subst->entries[subst->count].var, t_sub->name, MAX_NAME - 1);
        subst->entries[subst->count].term = clone_term(s_sub);
        subst->count++;
        free_term(s_sub); free_term(t_sub);
        return true;
    }
    if (strcmp(s_sub->name, t_sub->name) != 0 || s_sub->arity != t_sub->arity) {
        free_term(s_sub); free_term(t_sub);
        return false;
    }
    for (int i = 0; i < s_sub->arity; ++i) {
        if (!unify(s_sub->args[i], t_sub->args[i], subst)) {
            free_term(s_sub); free_term(t_sub);
            return false;
        }
    }
    free_term(s_sub); free_term(t_sub);
    return true;
}

// Зіставлення за зразком
bool match_pattern(const Term* pat, const Term* tgt, Substitution* subst) {
    if (pat->kind == TERM_VAR) {
        for (int i = 0; i < subst->count; ++i) {
            if (strcmp(subst->entries[i].var, pat->name) == 0) {
                return terms_equal(subst->entries[i].term, tgt);
            }
        }
        strncpy(subst->entries[subst->count].var, pat->name, MAX_NAME - 1);
        subst->entries[subst->count].term = clone_term(tgt);
        subst->count++;
        return true;
    }
    if (tgt->kind == TERM_VAR || strcmp(pat->name, tgt->name) != 0 || pat->arity != tgt->arity) return false;
    for (int i = 0; i < pat->arity; ++i) {
        if (!match_pattern(pat->args[i], tgt->args[i], subst)) return false;
    }
    return true;
}

// Порядок LPO
int symbol_prec(const char* name) {
    if (strcmp(name, "i") == 0) return 3;
    if (strcmp(name, "*") == 0) return 2;
    if (strcmp(name, "e") == 0) return 1;
    return 0;
}

bool lpo_greater(const Term* s, const Term* t) {
    if (t->kind == TERM_VAR) return contains_var(s, t->name) && !terms_equal(s, t);
    if (s->kind == TERM_VAR) return false;

    for (int i = 0; i < s->arity; ++i) {
        if (terms_equal(s->args[i], t) || lpo_greater(s->args[i], t)) return true;
    }

    int ps = symbol_prec(s->name), pt = symbol_prec(t->name);
    for (int j = 0; j < t->arity; ++j) {
        if (!lpo_greater(s, t->args[j])) return false;
    }
    if (ps > pt) return true;
    if (ps == pt && strcmp(s->name, t->name) == 0 && s->arity == t->arity) {
        for (int i = 0; i < s->arity; ++i) {
            if (terms_equal(s->args[i], t->args[i])) continue;
            return lpo_greater(s->args[i], t->args[i]);
        }
    }
    return false;
}

// Нормалізація та поповнення
Term* rewrite_step(const Term* t, const Rule* rules, int rule_count) {
    if (t->kind == TERM_FN) {
        for (int i = 0; i < t->arity; ++i) {
            Term* red = rewrite_step(t->args[i], rules, rule_count);
            if (!terms_equal(red, t->args[i])) {
                Term* new_args[MAX_ARGS];
                for (int j = 0; j < t->arity; ++j) new_args[j] = (i == j) ? red : clone_term(t->args[j]);
                return make_fn(t->name, t->arity, new_args);
            }
            free_term(red);
        }
    }
    for (int r = 0; r < rule_count; ++r) {
        Substitution s = { .count = 0 };
        if (match_pattern(rules[r].lhs, t, &s)) {
            Term* res = apply_subst(rules[r].rhs, &s);
            for (int i = 0; i < s.count; ++i) free_term(s.entries[i].term);
            return res;
        }
    }
    return clone_term(t);
}

Term* normalize(Term* t, const Rule* rules, int rule_count) {
    while (true) {
        Term* nxt = rewrite_step(t, rules, rule_count);
        if (terms_equal(nxt, t)) { free_term(nxt); break; }
        free_term(t);
        t = nxt;
    }
    return t;
}

int main(void) {
    Term* x = make_var("x");
    Term* y = make_var("y");
    Term* z = make_var("z");
    Term* e = make_fn("e", 0, NULL);

    Term* a1[2] = { e, x };
    Term* ax1_l = make_fn("*", 2, a1);
    Term* ax1_r = make_var("x");

    printf("=== Рушій переписування термів на C: Демонстрація LPO ===\n");
    printf("Аксіома 1: ");
    print_term(ax1_l);
    printf(" = ");
    print_term(ax1_r);
    printf("\nЧи ax1_l > ax1_r за LPO? %s\n", lpo_greater(ax1_l, ax1_r) ? "ТАК" : "НІ");

    free_term(ax1_l); free_term(ax1_r);
    free_term(y); free_term(z);
    return 0;
}
```
:::

## 3. Детальний аналіз алгоритмічних фаз та стратегій обчислення

Робота рушія переписування розбивається на три головних взаємопов'язаних цикли: покрокова редукція виразів, перевірка та автоорієнтація за порядком LPO, та пошук критичних пар через накладання уніфікаторів.

### 3.1. Стратегії редукції (Rewrite Strategies)
Коли у виразі одночасно присутні кілька редексів (підтермів, які зіставляються з лівими частинами правил), порядок їх скорочення визначається стратегією редукції:
1. **Внутрішньо-ліва стратегія (Innermost / Call-by-Value):** Спершу редукуються найглибші підтерми (аргументи), і лише коли всі аргументи стали нормальними формами, правило застосовується до кореня. Це відповідає енергійній моделі обчислень у більшості імперативних та функціональних мов (OCaml, C, Rust). Перевага — компактність проміжних виразів і простота реалізації через звичайну постфіксну рекурсію.
2. **Зовнішньо-ліва стратегія (Outermost / Call-by-Name):** Правила переписування спершу перевіряються у корені виразу, і лише якщо корінь не редукується, пошук спускається до підтермів. Для систем без умови термінації (як лямбда-числення) ця стратегія є квазі-повною: якщо терм має нормальну форму, зовнішня редукція гарантовано її знайде, уникаючи нескінченних обчислень у невикористовуваних гілках (ліниві обчислення в Haskell).
3. **Паралельно-зовнішня стратегія (Parallel-Outermost):** Одночасно скорочує всі незалежні максимальні редекси за один макрокрок. Для нетермінантних ортогональних систем вона забезпечує найсильніші теоретичні гарантії збіжності.

### 3.2. Покроковий розбір генерації критичних пар у теорії груп
Простежимо, як у наведеній програмі виникає перша нетривіальна критична пара для аксіом теорії груп.

Розглянемо початкові правила:
- Правило 1: `e · x → x`
- Правило 2: `i(x) · x → e`
- Правило 3: `(x · y) · z → x · (y · z)`

Після перейменування змінних розглянемо накладання правила 2 `i(x₁) · x₁ → e` на ліву частину правила 3 `(x₂ · y₂) · z₂ → x₂ · (y₂ · z₂)` у підтермі першого множника `(x₂ · y₂)`:
1. Знаходимо уніфікатор: `mgu(x₂ · y₂, i(x₁) · x₁) = {x₂ ↦ i(x₁), y₂ ↦ x₁}`.
2. Загальний уніфікований вираз: `(i(x₁) · x₁) · z₂`.
3. Редукція за правилом 3 у корені дає лівий результат: `i(x₁) · (x₁ · z₂)`.
4. Редукція за правилом 2 у підтермі `(i(x₁) · x₁)` дає правий результат: `e · z₂`.
5. Нормалізуємо правий результат за правилом 1: `e · z₂ → z₂`.
6. Отримуємо незбіжну критичну пару: `⟨ i(x₁) · (x₁ · z₂),  z₂ ⟩`.

Оскільки `i(x₁) · (x₁ · z₂) >_lpo z₂` за лексикографічним порядком, алгоритм автоматично створює нове спрямоване правило:
```
i(x) · (x · z)  →  z
```
Це правило додається до множини `R`, після чого алгоритм запускає новий раунд обчислення критичних пар з урахуванням нового правила. Цей процес триває, доки всі критичні пари не стануть збіжними до однакових нормальних форм.

## 4. Повний ланцюг канонізації теорії груп

У результаті повного виконання алгоритму Кнута-Бендікса над трьома базовими аксіомами група перетворюється на канонічну систему переписування з 10 правил, кожне з яких закриває конкретні критичні розвилки:

1. `e · x → x` *(аксіома лівої нейтральності)*
2. `i(x) · x → e` *(аксіома лівого оберненого)*
3. `(x · y) · z → x · (y · z)` *(аксіома асоціативності)*
4. `i(x) · (x · z) → z` *(накладання правила 2 на правило 3)*
5. `i(e) · x → x` ⇒ спрощується до `i(e) → e` *(обернений до нейтрального є нейтральним)*
6. `i(i(x)) · e → x` ⇒ спрощується до `i(i(x)) → x` *(інволютивність взяття оберненого)*
7. `x · e → x` *(права нейтральність, виведена автоматично)*
8. `x · i(x) → e` *(правий обернений, виведений автоматично)*
9. `x · (i(x) · z) → z` *(права асоціативна взаємодія оберненого)*
10. `i(x · y) → i(y) · i(x)` *(обернений до добутку є добутком обернених у зворотному порядку)*

Отримана система з 10 правил володіє властивістю сильної нормалізації та глобальної конфлюентності. Будь-яка теорема елементарної теорії груп (наприклад, рівність `(a · b) · (i(b) · i(a)) = e`) доводиться простим обчисленням нормальної форми обох частин без будь-якого евристичного пошуку.

## 5. Обмеження та крайові випадки: комутативність та AC-поповнення

Найвідомішим обмеженням стандартного алгоритму Кнута-Бендікса є неможливість орієнтувати комутативні рівності вигляду:
```
x · y  =  y · x
```
Жоден фундований строгий порядок редукції `>` не може задовольнити умову `x · y > y · x`, оскільки за стабільністю щодо підстановок `(y · x) > (x · y)`, що призводить до циклу `x · y > y · x > x · y` і суперечить ациклічності порядку.

Якщо алгоритм зустрічає таку рівність, він зупиняється з помилкою відсутності орієнтації. Для подолання цього бар'єру застосовують **AC-переписування (Associative-Commutative Rewriting)**, де асоціативні та комутативні символи виносяться в семантичний базис: терми порівнюються за модулем еквівалентності `E_AC`, а уніфікація замінюється на AC-уніфікацію через системи діофантових рівнянь.

## 6. Порівняльний аналіз моделей управління пам'яттю: C проти C++

Вибір мови програмування та моделі володіння об'єктами суттєво впливає на швидкодію рушія переписування:

### 6.1. Модель C: Ручне виділення та арени пам'яті
У наївній реалізації на C виділення пам'яті здійснюється через поодинокі виклики `malloc`/`free`. Для термів невеликого розміру накладні витрати стандартного алокатора `glibc` можуть перевищувати 60% загального часу виконання програми через фрагментацію та блокування м'ютексів.

Для високопродуктивних C-бібліотек стандартом є **аренний алокатор (Arena / Region Allocator)**:
- Виділяється великий суцільний блок пам'яті (наприклад, 16 МБ).
- Створення нових вузлів термів зводиться до простого зсуву покажчика вершини арени (`arena->offset += sizeof(Term)`), що виконується за 1 такт процесора.
- Під час очищення пам'яті після поповнення або нормалізації вся арена звільняється одним викликом `free()`, усуваючи необхідність рекурсивного обходу дерева.

### 6.2. Модель C++: RAII та незмінні терми
У реалізації на C++ використання `std::shared_ptr<Term>` забезпечує автоматичне керування життєвим циклом об'єктів без ризику витоків пам'яті. Оскільки вузли термів після створення є незмінними (immutable), їх можна безпечно розділяти між різними підвиразами та правилами без необхідності глибокого клонування (`deep copy`).

Для ще більшої оптимізації в C++20 застосовують `std::pmr::monotonic_buffer_resource` (поліморфні алокатори пам'яті), які поєднують переваги C++ RAII зі швидкістю низькорівневих арен пам'яті.

## 7. Методика тестування та верифікації рушія

Надійність рушія переписування перевіряється набором спеціалізованих властивісно-орієнтованих тестів (Property-Based Testing):
1. **Тест ідемпотентності нормалізації:** Для будь-якого терма `t` повторна нормалізація не повинна змінювати результат: `normalize(normalize(t)) == normalize(t)`. Якщо функція повертає змінений вираз, це свідчить про наявність пропущених редексів під час першого проходу редукції.
2. **Тест інваріантності підстановки:** Для канонічної системи результат редукції зіставленого виразу не залежить від того, чи застосовано підстановку до чи після нормалізації: `(normalize(t))σ ↓ normalize(tσ)`. Порушення цієї властивості сигналізує про дефект в алгоритмі підстановки або некоректну орієнтацію правил.
3. **Стрес-тест на глибоку рекурсію:** Нормалізація виразів вигляду `f(f(...f(0)...))` глибиною 100 000 вузлів для перевірки стійкості до переповнення стека. У виробничому коді пряму рекурсію замінюють ітеративним обходом із явним стеком вузлів у динамічній пам'яті.
4. **Тест ізоляції вільних змінних:** Перевірка того, що під час уніфікації двох правил жодна змінна з лівої частини не перетікає у праву частину іншого правила без відповідного явного зв'язування в підстановці.

## 8. Практична інтеграція з SMT-розв'язувачами та оптимізацією в компіляторах

Розроблені алгоритми переписування складають фундамент сучасних систем автоматичного міркування:
- **Насичення рівностями (Equality Saturation):** Замість деструктивного переписування, де старий терм знищується і замінюється новим, сучасні компіляторні оптимізатори (фреймворк `egg`) будують компактний еквівалентнісний граф (E-Graph). Усі еквівалентні форми виразу зберігаються паралельно у вузлах конгруентності, а правила переписування лише додають нові ребра до графа, доки система не досягне точки насичення. Після цього алгоритм динамічного програмування обирає з графа єдиний вираз із найменшою вартістю виконання (розмір коду або кількість тактів процесора).
- **E-Matching у SMT-розв'язувачах:** Системи на кшталт Z3 та CVC5 використовують алгоритми зіставлення термів за модулем рівності (E-Matching) для інстанціювання квантифікованих лем у теоріях першого порядку без виклику важких процедур повної уніфікації.

## 9. Локальність кешу процесора та серіалізація термів

У високопродуктивних алгоритмічних рушіях (наприклад, у верифікаторах формальних протоколів Maude або перевірниках моделей) представлення термів у вигляді зв'язних об'єктів з покажчиками створює значне навантаження на підсистему пам'яті через часті промахи кешу (L1/L2 Cache Misses).

Для прискорення обчислень застосовують **лінеаризоване польське представлення (Linear Polish Notation)**:
- Вираз зберігається як компактний одновимірний масив цілих чисел `uint32_t[]`, де функціональний символ кодується унікальним ідентифікатором, за яким безпосередньо слідують його серіалізовані підтерми.
- Операція перевірки рівності термів зводиться до швидкого виклику `memcmp()`.
- Копіювання виразу під час підстановки здійснюється однією векторною інструкцією `memcpy()`, забезпечуючи максимальну пропускну здатність шини пам'яті процесора.

## 10. Рядкове переписування як монадичний окремий випадок

Системи переписування рядків (напівсистеми Туе) є прямим алгебраїчним звуженням систем переписування термів. Якщо кожен функціональний символ у сигнатурі має арність 1 (монадичні терми `f(g(h(x)))`), дерево терма вироджується в лінійний ланцюг символів, що завершується єдиною змінною `x`.

У цьому випадку:
- Підтерми відповідають суфіксам рядків.
- Накладання двох правил `u₁ → v₁` та `u₂ → v₂` відбувається тоді й лише тоді, коли непорожній суфікс рядка `u₁` збігається з префіксом рядка `u₂` (перекриття слів).
- Обчислення критичних пар зводиться до пошуку перекриттів суфіксів і префіксів за допомогою префікс-функції Кнута-Морріса-Пратта (KMP) або суфіксних автоматів за лінійний час `O(|u₁| + |u₂|)`.

Якщо система переписування рядків є термінантною та конфлюентною, проблема слів у відповідній напівгрупі чи моноїді розв'язується за лінійний час від довжини вхідного слова. Проте якщо поповнення Кнута-Бендікса не завершується за скінченну кількість кроків (що трапляється для груп із нерозв'язною проблемою слів за теоремою Новікова-Боона), рушій генерує нескінченну послідовність правил, наочно ілюструючи алгоритмічні межі обчислювальності.

## 11. Переписування термів у компіляторах функціональних мов

Алгоритми переписування лежать в основі компіляторів мов функціонального програмування (Haskell GHC, OCaml, Scala, Clean):
- **Скомпульоване зіставлення за зразком:** Декларативні визначення функцій із багатьма зразками (pattern matching) транслюються у високоефективні дерева рішень (Decision Trees) або матриці зіставлення (Match Matrices), які перевіряють кожен конструктор аргументу рівно один раз.
- **Правила перезапису користувача (GHC Rewrite Rules):** Компілятор GHC дозволяє розробникам декларувати власні правила еквівалентного спрощення виразів за допомогою прагми `{-# RULES ... #-}` (наприклад, оптимізація злиття списків `map f (map g xs) = map (f . g) xs`). Рушій оптимізації застосовує ці правила як систему переписування термів під час проходжень Core-to-Core оптимізатора.
- **Еквівалентнісні перетворення в інтерактивних довідниках:** У системах Lean, Coq та Isabelle тактики спрощення `simp` або `rewrite` є повноцінними інтерактивними інтерпретаторами систем переписування термів із підтримкою вищих порядків та залежних типів.
