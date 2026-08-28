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
